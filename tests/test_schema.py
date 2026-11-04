# SPDX-License-Identifier: MIT
"""The schema: the samples that must pass and those that must fail, each on its rule; every rule has its sample; the
generated files come from the ODD as it is now; the build's downloads are checked against their pins."""

import hashlib
import re
import shutil
from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.build import ODD_PATH, BuildError, Source, fetch, stamped
from solemne_tei.schema_files import GENERATED, ODD, SCHEMA_DIR, sha256, stamp, stamped_sha256
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
    odd = sha256(ODD_PATH)
    for name in GENERATED:
        assert stamped_sha256(SCHEMA_DIR / name) == odd, (
            f"{name} was generated from another version of {ODD}: run solemne-tei build"
        )


def test_stamp_follows_the_xml_declaration(tmp_path: Path) -> None:
    text = stamped('<?xml version="1.0" encoding="UTF-8"?><grammar/>', "ab" * 32)
    assert text.splitlines() == [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- SPDX-License-Identifier: MIT -->",
        stamp("ab" * 32),
        "<grammar/>",
    ]
    path = tmp_path / "solemne.rng"
    path.write_text(text, encoding="utf-8")
    assert stamped_sha256(path) == "ab" * 32


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
