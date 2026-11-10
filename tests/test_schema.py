# SPDX-License-Identifier: MIT
"""The schema: the valid samples pass; the generated files come from the ODD as it is now; the build's downloads are
checked against their pins, and the build stops on an ODD that isn't valid. The guide's examples, counter-examples
of every rule among them, are checked in test_guide."""

import hashlib
import io
import re
import tomllib
import urllib.error
from pathlib import Path

import pytest
from lxml import etree

import solemne_tei
from solemne_tei.build import (
    ODD_PATH,
    XHTML,
    BuildError,
    Source,
    check_odd,
    embedded_schematron,
    expand,
    fetch,
    plain_documentation,
    stamped,
)
from solemne_tei.codes import CATEGORIES, code_prefix
from solemne_tei.schema_files import (
    COMPILED_ODD,
    GENERATED,
    ODD,
    RELAXNG,
    SCHEMA_DIR,
    closed_lists,
    closed_lists_of,
    odd_version,
    read_stamp,
    schema_version,
    stamp,
)
from solemne_tei.validate import Result, Validator

SAMPLES = Path(__file__).parent / "samples"
VALID = sorted((SAMPLES / "valid").glob("*.xml"))
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


def test_generated_files_come_from_the_odd_as_it_is() -> None:
    odd = (odd_version(ODD_PATH), expand(ODD_PATH).sha256)
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


def test_the_relaxng_holds_no_xhtml() -> None:
    """A browser shows an XML file holding XHTML as an unstyled web page, its tags hidden."""
    assert XHTML not in (SCHEMA_DIR / RELAXNG).read_text("utf-8")


DOCUMENTATION = 'xmlns:a="http://relaxng.org/ns/compatibility/annotations/1.0"'


def test_plain_documentation_keeps_the_words_and_the_rest_of_the_text() -> None:
    text = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<grammar xmlns="http://relaxng.org/ns/structure/1.0"',
            '         ns="http://www.tei-c.org/ns/1.0">',
            f'  <a:documentation {DOCUMENTATION}>the <code xmlns="{XHTML}"',
            '      xmlns:rng="http://relaxng.org/ns/structure/1.0">@unit</code> attribute, by'
            f' <a xmlns="{XHTML}" href="https://example.org/">BCP 47</a>.</a:documentation>',
            "  <start><empty/></start>",
            "</grammar>",
        ]
    )
    plain = plain_documentation(text).splitlines()
    original = text.splitlines()
    assert plain[3] == f"  <a:documentation {DOCUMENTATION}>the @unit attribute, by BCP 47.</a:documentation>"
    assert plain[:3] + plain[4:] == original[:3] + original[5:]


def test_plain_documentation_stops_on_xhtml_that_isn_t_only_text() -> None:
    text = f'<a:documentation {DOCUMENTATION}><code xmlns="{XHTML}"><b>x</b></code></a:documentation>'
    with pytest.raises(BuildError, match="isn't only text"):
        plain_documentation(text)


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


class FlakyServer:
    """Stands in for urlopen: fails with each of `errors` in turn, then serves `content`."""

    def __init__(self, errors: list[Exception], content: bytes = b"<TEI/>") -> None:
        self.errors, self.content, self.calls = list(errors), content, 0

    def __call__(self, url: str, timeout: float) -> io.BytesIO:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return io.BytesIO(self.content)


def http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://example.org/tei.zip", code, "error", hdrs=None, fp=None)  # type: ignore[arg-type]


@pytest.fixture
def waits(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """The pauses fetch takes, recorded instead of slept."""
    taken: list[float] = []
    monkeypatch.setattr("solemne_tei.build.time.sleep", taken.append)
    return taken


def test_fetch_tries_again_after_a_timeout_and_a_server_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, waits: list[float]
) -> None:
    server = FlakyServer([TimeoutError("The read operation timed out"), http_error(504)])
    monkeypatch.setattr("solemne_tei.build.urllib.request.urlopen", server)
    source = pinned(tmp_path, b"", hashlib.sha256(b"<TEI/>").hexdigest())
    assert fetch(source, tmp_path / "downloads", wait=1).read_bytes() == b"<TEI/>"
    assert (server.calls, waits) == (3, [1, 2])
    assert [p.name for p in (tmp_path / "downloads").iterdir()] == ["p5subset.xml"]


def test_fetch_gives_up_after_its_attempts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    server = FlakyServer([http_error(504)] * 3)
    monkeypatch.setattr("solemne_tei.build.urllib.request.urlopen", server)
    with pytest.raises(BuildError, match="could not be fetched"):
        fetch(pinned(tmp_path, b"", "0" * 64), tmp_path / "downloads", attempts=3, wait=1)
    assert (server.calls, waits) == (3, [1, 2])
    assert list((tmp_path / "downloads").iterdir()) == []


def test_fetch_does_not_try_again_a_file_that_isnt_there(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, waits: list[float]
) -> None:
    server = FlakyServer([http_error(404)])
    monkeypatch.setattr("solemne_tei.build.urllib.request.urlopen", server)
    with pytest.raises(BuildError, match="404"):
        fetch(pinned(tmp_path, b"", "0" * 64), tmp_path / "downloads")
    assert (server.calls, waits) == (1, [])


# The ODD check takes any validator: these tests give it the package's own schema, which needs no download.
def test_the_odd_check_passes_a_valid_file(validator: Validator) -> None:
    check_odd(VALID[0], validator)


def test_the_odd_check_stops_the_build_on_an_error(validator: Validator, tmp_path: Path) -> None:
    sample = tmp_path / "invalid.xml"
    text = VALID[0].read_text(encoding="utf-8").replace('<div type="chapter"', '<div type="chpater"', 1)
    assert 'type="chpater"' in text
    sample.write_text(text, encoding="utf-8")
    with pytest.raises(BuildError, match="invalid.xml isn't valid"):
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


def with_code(tmp_path: Path, code: str, category: str, name: str = "file.xml") -> Path:
    """A valid sample whose formal title gives this code and category, saved under this name."""
    text = (SAMPLES / "valid" / "council-edition.xml").read_text(encoding="utf-8")
    text = re.sub(r"<idno>[^<]*</idno>", f"<idno>{code}</idno>", text, count=1)
    text = re.sub(r'<idno type="category">[^<]*</idno>', f'<idno type="category">{category}</idno>', text, count=1)
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def schematron_rules(validator: Validator, path: Path) -> set[str]:
    return {p.rule for p in validator.check(path).problems if p.check == "schematron"}


@pytest.mark.parametrize("category", ["LR", "CPT", "CHA"])
def test_a_code_begins_with_its_category_s_own_prefix(validator: Validator, tmp_path: Path, category: str) -> None:
    own = with_code(tmp_path, f"{category}.Exemplum-0800", category)
    assert "code-category" not in schematron_rules(validator, own)
    assert "code-category" in schematron_rules(validator, with_code(tmp_path, "C.Exemplum-0800", category))


def test_a_code_of_an_unknown_category_takes_any_prefix(validator: Validator, tmp_path: Path) -> None:
    assert "code-category" not in schematron_rules(validator, with_code(tmp_path, "C.Exemplum-0800", "UNK"))


@pytest.mark.parametrize("category", [category for category in CATEGORIES if category != "UNK"])
def test_the_schema_s_prefix_for_a_category_is_the_package_s(
    validator: Validator, tmp_path: Path, category: str
) -> None:
    code = with_code(tmp_path, f"{code_prefix(category)}.Exemplum-0800", category)
    assert "code-category" not in schematron_rules(validator, code)


def test_a_collection_in_no_order_takes_the_collections_prefix(validator: Validator, tmp_path: Path) -> None:
    assert "code-category" not in schematron_rules(validator, with_code(tmp_path, "COLL.Exemplum", "FARCOLL"))
    assert "code-category" in schematron_rules(validator, with_code(tmp_path, "FARCOLL.Exemplum", "FARCOLL"))


def test_a_work_known_by_its_siglum_is_coded_from_it(validator: Validator, tmp_path: Path) -> None:
    found = schematron_rules(validator, with_code(tmp_path, "W.IS-ety", "W", "W.IS-ety.xml"))
    assert not found & {"code-format", "code-category", "category-value", "code-matches-file-name"}


@pytest.mark.parametrize(
    ("code", "category"),
    [
        ("D.LEO-0449-423.ed-Schon-222", "D"),
        ("D.DAM-0378-235.ed-Schon-142", "D"),
        ("C.BRA-0561.ed-Schon-109", "C"),
        ("C.NIC-0325.ed-Exemplum-12", "C"),
    ],
)
def test_a_second_text_of_one_work_in_one_edition_takes_its_item_s_number(
    validator: Validator, tmp_path: Path, code: str, category: str
) -> None:
    found = schematron_rules(validator, with_code(tmp_path, code, category, f"{code}.xml"))
    assert not found & {"code-format", "code-category", "category-value", "code-matches-file-name"}


@pytest.mark.parametrize("category", ["C", "LR", "CPT", "CHA", "SYSCOLL"])
def test_a_file_named_by_a_code_is_named_by_its_own(validator: Validator, tmp_path: Path, category: str) -> None:
    prefix = code_prefix(category)
    code = f"{prefix}.Exemplum-0800"
    right = with_code(tmp_path, code, category, f"{code}.xml")
    assert "code-matches-file-name" not in schematron_rules(validator, right)
    wrong = with_code(tmp_path, code, category, f"{prefix}.Aliud-0801.xml")
    assert "code-matches-file-name" in schematron_rules(validator, wrong)
