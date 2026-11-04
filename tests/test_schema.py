# SPDX-License-Identifier: MIT
"""The schema: the samples that must pass and those that must fail, each on its rule; every rule has its sample; the
generated files come from the ODD as it is now; the build's downloads are checked against their pins, and the
build stops on an ODD that isn't valid."""

import hashlib
import re
import shutil
import tomllib
from pathlib import Path

import pytest
from lxml import etree

import solemne_tei
from solemne_tei.build import ODD_PATH, BuildError, Source, check_odd, embedded_schematron, fetch, stamped
from solemne_tei.schema_files import (
    COMPILED_ODD,
    GENERATED,
    ODD,
    SCHEMA_DIR,
    closed_lists,
    closed_lists_of,
    odd_version,
    read_stamp,
    schema_version,
    sha256,
    stamp,
)
from solemne_tei.validate import Result, Validator

SAMPLES = Path(__file__).parent / "samples"
VALID = sorted((SAMPLES / "valid").glob("*.xml"))
INVALID = sorted((SAMPLES / "invalid").glob("*.xml"))
SCH = "http://purl.oclc.org/dsdl/schematron"


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def describe(result: Result) -> str:
    return "\n".join(str(p) for p in result.problems)


def test_there_is_a_valid_sample_per_kind_of_file() -> None:
    assert {p.stem for p in VALID} >= {"council-edition", "manuscript-collection", "export"}


@pytest.mark.parametrize("sample", VALID, ids=lambda p: p.stem)
def test_valid_sample_passes_both_checks(validator: Validator, sample: Path) -> None:
    result = validator.check(sample)
    assert result.problems == [], describe(result)


@pytest.mark.parametrize("sample", INVALID, ids=lambda p: p.stem)
def test_invalid_sample_fails_on_its_rule(validator: Validator, sample: Path, tmp_path: Path) -> None:
    text = sample.read_text(encoding="utf-8")
    statement = re.search(r"<!-- Breaks one rule: (\S+) \(.*?\), checked by the (RelaxNG|Schematron)", text)
    assert statement, "the sample says which rule it breaks"
    rule, check = statement.groups()
    assert rule == sample.stem
    renamed = re.search(r"under the file name (\S+\.xml)", text)
    path = sample
    if renamed:
        path = tmp_path / renamed.group(1)
        shutil.copy(sample, path)
    result = validator.check(path)
    if check == "RelaxNG":
        marked = {i for i, line in enumerate(text.splitlines(), 1) if "<!-- breaks the rule -->" in line and i > 3}
        assert marked, "the sample marks the line of its error"
        lines = {p.line for p in result.problems if p.check == "relaxng"}
        assert lines & marked, describe(result)
    else:
        assert result.passes_relaxng, describe(result)
        assert rule in {p.rule for p in result.problems if p.check == "schematron"}, describe(result)


def odd_rules() -> set[str]:
    odd = etree.parse(str(ODD_PATH))
    return {el.get("id") for el in odd.iter(f"{{{SCH}}}assert", f"{{{SCH}}}report") if el.get("id") is not None}


def test_every_rule_of_the_odd_has_an_invalid_sample() -> None:
    missing = odd_rules() - {p.stem for p in INVALID}
    assert not missing


def test_generated_files_come_from_the_odd_as_it_is() -> None:
    odd = (odd_version(ODD_PATH), sha256(ODD_PATH))
    for name in GENERATED:
        assert read_stamp(SCHEMA_DIR / name) == odd, (
            f"{name} was generated from another version of {ODD}: run solemne-tei build"
        )


def test_generated_files_hold_no_paths_of_the_machine_they_were_made_on() -> None:
    for name in GENERATED:
        assert "file:/" not in (SCHEMA_DIR / name).read_text("utf-8"), name


def test_the_versions_agree() -> None:
    with (ODD_PATH.parents[1] / "pyproject.toml").open("rb") as f:
        project = tomllib.load(f)["project"]["version"]
    assert odd_version(ODD_PATH) == project == solemne_tei.__version__ == schema_version()


def test_the_closed_lists_are_those_of_the_compiled_odd() -> None:
    lists = closed_lists()
    assert lists == closed_lists_of(SCHEMA_DIR / COMPILED_ODD)
    assert lists["div"]["type"] == sorted(lists["div"]["type"])
    assert {"section", "chapter", "unit"} <= set(lists["div"]["type"])


def test_stamp_follows_the_xml_declaration(tmp_path: Path) -> None:
    text = stamped('<?xml version="1.0" encoding="UTF-8"?><grammar/>', "1.2.3", "ab" * 32)
    assert text.splitlines() == [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- SPDX-License-Identifier: MIT -->",
        stamp("1.2.3", "ab" * 32),
        "<grammar/>",
    ]
    path = tmp_path / "solemne.rng"
    path.write_text(text, encoding="utf-8")
    assert read_stamp(path) == ("1.2.3", "ab" * 32)


def pinned(tmp_path: Path, content: bytes, checksum: str) -> Source:
    original = tmp_path / "original.xml"
    original.write_bytes(content)
    return Source("p5subset.xml", "0", original.as_uri(), checksum, "")


def test_fetch_keeps_a_file_with_its_pinned_checksum(tmp_path: Path) -> None:
    content = b"<TEI/>"
    path = fetch(pinned(tmp_path, content, hashlib.sha256(content).hexdigest()), tmp_path / "downloads")
    assert path.read_bytes() == content


def test_fetch_refuses_a_file_whose_checksum_differs(tmp_path: Path) -> None:
    with pytest.raises(BuildError, match="SHA-256"):
        fetch(pinned(tmp_path, b"<TEI/>", "0" * 64), tmp_path / "downloads")
    assert not (tmp_path / "downloads" / "p5subset.xml").exists()


# The ODD check takes any validator: these tests give it the package's own schema, which needs no download.
def test_the_odd_check_passes_a_valid_file(validator: Validator) -> None:
    check_odd(VALID[0], validator)


def test_the_odd_check_stops_the_build_on_an_error(validator: Validator) -> None:
    sample = next(p for p in INVALID if "checked by the RelaxNG" in p.read_text(encoding="utf-8"))
    with pytest.raises(BuildError, match=f"{sample.name} isn't valid"):
        check_odd(sample, validator)


def test_the_schematron_embedded_in_a_grammar_is_gathered_namespaces_first(tmp_path: Path) -> None:
    rng = tmp_path / "grammar.rng"
    rng.write_text(
        f"""<grammar xmlns="http://relaxng.org/ns/structure/1.0" xmlns:sch="{SCH}">
          <sch:pattern id="p">
            <sch:rule context="tei:p"><sch:assert test="text()">text</sch:assert></sch:rule>
          </sch:pattern>
          <sch:ns prefix="tei" uri="http://www.tei-c.org/ns/1.0"/>
          <start><element name="p"><text/></element></start>
        </grammar>""",
        encoding="utf-8",
    )
    schema = etree.fromstring(embedded_schematron(rng))
    assert schema.get("queryBinding") == "xslt2"
    assert [etree.QName(el).localname for el in schema] == ["ns", "pattern"]
    assert schema.find(f"{{{SCH}}}pattern/{{{SCH}}}rule").get("context") == "tei:p"
