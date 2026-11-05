# SPDX-License-Identifier: MIT
"""The validator: problems with file, line and message; the same results whatever the number of workers; files that
aren't well formed reported, not raised; the command line."""

import json
import os
from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.cli import main
from solemne_tei.validate import Validator, _line, validate, xml_files

SAMPLES = Path(__file__).parent / "samples"
TEI_NS = "http://www.tei-c.org/ns/1.0"

HEAD = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title type="formal">
          <idno>C.SAM-0600</idno>
          <idno type="category">C</idno>
          <idno type="type">edition</idno>
        </title>
      </titleStmt>
      <publicationStmt>
        <p>A test.</p>
      </publicationStmt>
      <sourceDesc>
        <p>Made up.</p>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
"""
TAIL = """    </body>
  </text>
</TEI>
"""
HEAD_LINES = HEAD.count("\n")
LONE_UNIT = (
    '      <div type="chapter">\n        <div type="unit">\n          <p>Placuit.</p>\n        </div>\n      </div>\n'
)


def tei(tmp_path: Path, body: str, name: str = "test.xml") -> Path:
    path = tmp_path / name
    path.write_text(HEAD + body + TAIL, encoding="utf-8")
    return path


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def test_a_valid_file_has_no_problems(validator: Validator, tmp_path: Path) -> None:
    path = tei(tmp_path, '      <div type="chapter">\n        <p>Placuit.</p>\n      </div>\n')
    result = validator.check(path)
    assert result.problems == []
    assert result.passes_relaxng


def test_a_relaxng_problem_carries_file_line_and_message(validator: Validator, tmp_path: Path) -> None:
    path = tei(tmp_path, '      <div type="chpater">\n        <p>Placuit.</p>\n      </div>\n')
    result = validator.check(path)
    assert not result.passes_relaxng
    problem = next(p for p in result.problems if p.check == "relaxng")
    assert problem.file == str(path)
    assert problem.line == HEAD_LINES + 1
    assert "div" in problem.message


def test_a_relaxng_problem_is_reported_at_the_innermost_element(validator: Validator, tmp_path: Path) -> None:
    body = (
        '      <div type="chapter">\n'
        '        <div type="unit">\n          <p>Placuit.</p>\n        </div>\n'
        '        <div type="unit">\n'
        '          <p>Et <quote source="CNIC.325.2">placuit</quote>.</p>\n'
        "        </div>\n      </div>\n"
    )
    result = validator.check(tei(tmp_path, body))
    lines = {p.line for p in result.problems if p.check == "relaxng"}
    assert lines == {HEAD_LINES + 6}
    assert any("quote" in p.message for p in result.problems)


def test_a_schematron_problem_carries_its_rule_and_line(validator: Validator, tmp_path: Path) -> None:
    result = validator.check(tei(tmp_path, LONE_UNIT))
    assert result.passes_relaxng
    problem = next(p for p in result.problems if p.rule == "unit-alone")
    assert (problem.check, problem.severity, problem.line) == ("schematron", "error", HEAD_LINES + 2)
    assert problem.message


def test_a_file_that_is_not_well_formed_is_reported(validator: Validator, tmp_path: Path) -> None:
    path = tmp_path / "broken.xml"
    path.write_text("<TEI>\n  <text>\n</TEI>\n", encoding="utf-8")
    result = validator.check(path)
    assert not result.well_formed
    assert [(p.check, p.line) for p in result.problems] == [("well-formed", 3)]


def test_a_missing_file_is_reported(validator: Validator, tmp_path: Path) -> None:
    result = validator.check(tmp_path / "nowhere.xml")
    assert [p.rule for p in result.problems] == ["unreadable"]


def test_the_results_are_the_same_with_one_worker_and_with_all(tmp_path: Path) -> None:
    failing = [
        tei(tmp_path, LONE_UNIT, "unit.xml"),
        tei(tmp_path, '      <div type="chpater">\n        <p>Placuit.</p>\n      </div>\n', "type.xml"),
    ]
    paths = xml_files([SAMPLES]) + failing + [tmp_path / "missing.xml"]
    assert validate(paths, jobs=1) == validate(paths, jobs=max(2, os.cpu_count() or 2))


def test_folders_are_searched_for_xml_files(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    for name in ("a/one.xml", "two.xml", "three.txt"):
        (tmp_path / name).write_text("<x/>", encoding="utf-8")
    assert xml_files([tmp_path]) == [tmp_path / "a" / "one.xml", tmp_path / "two.xml"]


def test_a_schematron_location_gives_its_element_s_line() -> None:
    tree = etree.ElementTree(etree.fromstring(f'<TEI xmlns="{TEI_NS}">\n<text>\n<body/>\n<body/>\n</text>\n</TEI>'))
    q = f"Q{{{TEI_NS}}}"
    assert _line(tree, f"/{q}TEI[1]/{q}text[1]/{q}body[2]/@type") == 4
    assert _line(tree, f"/{q}TEI[1]/{q}text[1]") == 2
    assert _line(tree, "/") is None


def test_the_command_line_reports_and_sets_its_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = tei(tmp_path, '      <div type="chapter">\n        <p>Placuit.</p>\n      </div>\n', "good.xml")
    unit = tei(tmp_path, LONE_UNIT, "unit.xml")
    bad = tei(tmp_path, '      <div type="chpater">\n        <p>Placuit.</p>\n      </div>\n', "bad.xml")
    assert main(["validate", str(good), "--jobs", "1"]) == 0
    assert main(["validate", str(unit), "--jobs", "1"]) == 0
    assert main(["validate", str(unit), "--jobs", "1", "--strict"]) == 1
    capsys.readouterr()
    assert main(["validate", str(bad), str(good), "--jobs", "1", "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert [(Path(r["file"]).name, r["passes_relaxng"]) for r in payload] == [("bad.xml", False), ("good.xml", True)]
    assert main(["validate", str(bad), "--jobs", "1"]) == 1
    out = capsys.readouterr().out
    assert f"{bad}:{HEAD_LINES + 1}: relaxng error" in out
    assert "1 files: 1 well-formed, 0 pass the RelaxNG" in out


# libxml2 never finishes compiling some elements' patterns as a grammar's start; the narrowing skips them. These run
# in a process of their own, with a time limit, so that a new such element fails the test rather than hanging it.
EVERY_ELEMENT_ALONE = """
import sys
from lxml import etree
from solemne_tei.validate import NOT_ALONE, Validator
R = "{http://relaxng.org/ns/structure/1.0}"
for fmt in (None, "bodleian"):
    v = Validator(format=fmt)
    for d in v._grammar.iter(R + "define"):
        if d.find(R + "element") is not None and d.get("name") not in NOT_ALONE:
            print(fmt, d.get("name"), flush=True)
            v._schema_for(etree.Element("{http://www.tei-c.org/ns/1.0}" + d.get("name")))
"""


def test_every_element_but_the_known_ones_compiles_on_its_own() -> None:
    import subprocess
    import sys

    try:
        subprocess.run([sys.executable, "-c", EVERY_ELEMENT_ALONE], check=True, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired as e:
        last = (e.stdout or b"").decode().strip().splitlines()[-1:]
        pytest.fail(f"compiling an element's pattern on its own doesn't finish: {last}; add it to NOT_ALONE")


def test_a_failure_beside_an_imprint_is_found_at_once(tmp_path: Path) -> None:
    import subprocess
    import sys

    body = """<biblStruct><monogr><title level="m">Concilia</title>
        <imprint><publisher>Hahn</publisher><date>1906</date></imprint>
        <biblScope unit="tome">2</biblScope></monogr></biblStruct>"""
    path = tmp_path / "unit.xml"
    path.write_text(HEAD.replace("<p>Made up.</p>", body) + "      <p>Placuit.</p>\n" + TAIL, "utf-8")
    done = subprocess.run(
        [sys.executable, "-m", "solemne_tei.cli", "validate", "--jobs", "1", "--json", str(path)],
        capture_output=True,
        timeout=60,
    )
    problems = json.loads(done.stdout)[0]["problems"]
    assert any("Invalid attribute unit for element biblScope" in p["message"] for p in problems), problems
