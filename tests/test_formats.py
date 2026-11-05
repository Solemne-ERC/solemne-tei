# SPDX-License-Identifier: MIT
"""The import formats: a file in the Bodleian's form is checked against the Bodleian's own schema, from the command
line and from Python; the format's files name their pinned source and carry its licence."""

import re
from pathlib import Path

import pytest

from solemne_tei.cli import main
from solemne_tei.formats import BODLEIAN, import_format
from solemne_tei.validate import Validator, validate

SAMPLE = Path(__file__).parent / "samples" / "bodleian" / "valid.xml"
TITLE = "<title>Collectio exempli</title>"
# An element no TEI module has, which the old drafts of the project's encoding used.
OUTSIDE = f"{TITLE}<collCode>C</collCode>"


@pytest.fixture(scope="module")
def bodleian() -> Validator:
    return Validator(format="bodleian")


def broken(tmp_path: Path, old: str, new: str) -> Path:
    """The sample with one change."""
    text = SAMPLE.read_text("utf-8")
    assert old in text
    path = tmp_path / "broken.xml"
    path.write_text(text.replace(old, new), "utf-8")
    return path


def test_a_file_in_the_bodleians_form_passes_its_schema(bodleian: Validator) -> None:
    assert bodleian.check(SAMPLE).problems == []


def test_the_same_file_fails_the_projects_schema() -> None:
    rules = {p.rule for p in Validator().check(SAMPLE).problems}
    assert {"manuscript-unit", "description-elements"} <= rules


def test_a_date_without_its_calendar_breaks_the_bodleians_rule(bodleian: Validator, tmp_path: Path) -> None:
    path = broken(tmp_path, '<origDate calendar="#Gregorian" ', "<origDate ")
    problems = bodleian.check(path).problems
    assert [(p.check, p.rule) for p in problems] == [("schematron", "origDate.check")]


def test_an_element_outside_its_schema_fails_the_relaxng(bodleian: Validator, tmp_path: Path) -> None:
    path = broken(tmp_path, TITLE, OUTSIDE)
    result = bodleian.check(path)
    assert not result.passes_relaxng


def test_validate_takes_the_format_in_parallel_too(tmp_path: Path) -> None:
    path = broken(tmp_path, '<origDate calendar="#Gregorian" ', "<origDate ")
    results = validate([SAMPLE, path], jobs=2, format="bodleian")
    assert [r.schematron_errors for r in results] == [0, 1]


def test_an_unknown_format_is_refused() -> None:
    with pytest.raises(ValueError, match="no import format"):
        validate([SAMPLE], format="oxford")


def test_the_command_line_checks_against_the_format(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    assert main(["validate", "--format", "bodleian", str(SAMPLE)]) == 0
    path = broken(tmp_path, TITLE, OUTSIDE)
    assert main(["validate", "--format", "bodleian", str(path)]) == 1
    assert "relaxng" in capsys.readouterr().out


@pytest.mark.parametrize("path", [BODLEIAN.relaxng, BODLEIAN.schematron_xslt], ids=lambda p: p.name)
def test_the_formats_files_name_their_source_and_carry_its_licence(path: Path) -> None:
    head = path.read_text("utf-8")[:6000]
    assert re.search(r"Generated from msdesc\.rng at commit 7e8b89c \(SHA-256 [0-9a-f]{64}\)", head)
    assert "Copyright (c) 2017, James Cummings" in head
    assert "SPDX-License-Identifier: BSD-2-Clause" in head


def test_import_format_finds_the_bodleians() -> None:
    assert import_format("bodleian") is BODLEIAN


# Every element and attribute the project's 38 descriptions in the Bodleian's form use, counted once from its coded
# files: the mapping table has a row for each.
DESCRIPTIONS_USE = (
    "additional",
    "additions",
    "adminInfo",
    "altIdentifier",
    "author",
    "bibl",
    "biblScope",
    "binding",
    "bindingDesc",
    "collation",
    "colophon",
    "condition",
    "country",
    "date",
    "decoDesc",
    "decoNote",
    "dimensions",
    "explicit",
    "extent",
    "filiation",
    "finalRubric",
    "foliation",
    "height",
    "history",
    "idno",
    "incipit",
    "institution",
    "layout",
    "layoutDesc",
    "listBibl",
    "locus",
    "msContents",
    "msDesc",
    "msIdentifier",
    "msItem",
    "msName",
    "msPart",
    "note",
    "num",
    "objectDesc",
    "orgName",
    "origDate",
    "origPlace",
    "origin",
    "p",
    "physDesc",
    "placeName",
    "provenance",
    "pubPlace",
    "recordHist",
    "region",
    "repository",
    "rubric",
    "settlement",
    "source",
    "summary",
    "support",
    "supportDesc",
    "title",
    "width",
)
DESCRIPTIONS_USE_ATTRIBUTES = (
    "altIdentifier/@type",
    "author/@key",
    "bibl/@facs",
    "bibl/@type",
    "biblScope/@unit",
    "binding/@notAfter",
    "binding/@notBefore",
    "country/@key",
    "dimensions/@type",
    "dimensions/@unit",
    "idno/@type",
    "layout/@columns",
    "layout/@writtenLines",
    "msDesc/@xml:lang",
    "msItem/@class",
    "msItem/@n",
    "msPart/@n",
    "note/@type",
    "objectDesc/@form",
    "origDate/@calendar",
    "origDate/@notAfter",
    "origDate/@notBefore",
    "origPlace/@key",
    "provenance/@corresp",
    "provenance/@notAfter",
    "provenance/@notBefore",
    "region/@type",
    "supportDesc/@material",
    "title/@key",
    "title/@level",
)
MAPPING = Path(__file__).parents[1] / "guide" / "mappings" / "bodleian.xml"


def mapped() -> tuple[set[str], set[str]]:
    """The elements and the attributes (`msItem/@class`, or `*/@xml:id` for any element's) the mapping table's rows
    name in their first cell."""
    from lxml import etree

    tei = "{http://www.tei-c.org/ns/1.0}"
    elements: set[str] = set()
    attributes: set[str] = set()
    for row in etree.parse(str(MAPPING)).iter(f"{tei}row"):
        if row.get("role") == "label":
            continue
        first = row.find(f"{tei}cell")
        gis = {gi.text for gi in first.iter(f"{tei}gi")}
        elements |= gis
        for att in first.iter(f"{tei}att"):
            attributes |= {f"{gi}/@{att.text}" for gi in gis} or {f"*/@{att.text}"}
    return elements, attributes


def test_the_mapping_table_has_a_row_for_every_element_the_descriptions_use() -> None:
    elements, _ = mapped()
    assert [e for e in DESCRIPTIONS_USE if e not in elements] == []


def test_the_mapping_table_has_a_row_for_every_attribute_the_descriptions_use() -> None:
    _, attributes = mapped()
    missing = [
        a for a in DESCRIPTIONS_USE_ATTRIBUTES if a not in attributes and f"*/@{a.split('/@')[1]}" not in attributes
    ]
    assert missing == []
