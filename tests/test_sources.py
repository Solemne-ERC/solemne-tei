# SPDX-License-Identifier: MIT
"""Sources: a text names the one it was taken from in its sourceDesc, beside the witness's description; every
source, a record's too, has its name; one with a link gives the date it was taken. Each case is a fragment placed in
a minimal valid file, as the guide's examples are."""

from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.examples import EXAMPLES, Example, placed
from solemne_tei.validate import Problem, Validator

EDITION = (
    "<biblStruct><monogr><title level='m'>Canones</title><imprint><date>1853</date></imprint></monogr></biblStruct>"
)
LINK = '<ref target="https://mlat.uzh.ch/browser/cps_2.AbFlHuF.Canone5">mlat.uzh.ch</ref>'
RETRIEVED = '<date type="retrieved" when="2026-11-06">6 November 2026</date>'
NAME = "<title>Corpus Corporum</title>"


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def problems(validator: Validator, tmp_path: Path, xml: str) -> list[Problem]:
    """The problems of a fragment, which passes the RelaxNG."""
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    path = tmp_path / "source.xml"
    placed(Example(eg, True, "", "", 1, "source.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    found = validator.check(path).problems
    assert [p for p in found if p.check != "schematron"] == []
    return found


def rules(found: list[Problem]) -> list[str]:
    return [p.rule for p in found]


def text_source(*parts: str) -> str:
    return f'<sourceDesc>{EDITION}<bibl type="source">{"".join(parts)}</bibl></sourceDesc>'


def test_a_text_s_source_in_the_requested_form_passes(validator: Validator, tmp_path: Path) -> None:
    note = "<note>this file was encoded in TEI xml for Corpus Corporum by Ph. Roelli in 2019</note>"
    assert problems(validator, tmp_path, text_source(NAME, LINK, RETRIEVED, note)) == []


def test_a_text_s_source_with_its_version_and_licence_passes(validator: Validator, tmp_path: Path) -> None:
    licence = (
        '<availability><licence target="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</licence>'
        "</availability>"
    )
    xml = text_source(NAME, LINK, RETRIEVED, "<edition>2019</edition>", licence)
    assert problems(validator, tmp_path, xml) == []


def test_two_sources_of_a_text_fail(validator: Validator, tmp_path: Path) -> None:
    second = f'<bibl type="source"><title>The Latin Library</title>{RETRIEVED}</bibl>'
    xml = text_source(NAME, LINK, RETRIEVED).replace("</sourceDesc>", f"{second}</sourceDesc>")
    found = problems(validator, tmp_path, xml)
    assert rules(found) == ["text-source-one"]
    assert found[0].severity == "error"


def test_a_description_may_name_several_sources_of_its_own(validator: Validator, tmp_path: Path) -> None:
    sources = "".join(f'<bibl type="source"><title>{name}</title>{RETRIEVED}</bibl>' for name in ("Mirabile", "HMML"))
    xml = f"<additional><adminInfo><recordHist><source>{sources}</source></recordHist></adminInfo></additional>"
    assert problems(validator, tmp_path, xml) == []


@pytest.mark.parametrize(
    "xml",
    [
        text_source(LINK, RETRIEVED),
        text_source("<title> </title>", RETRIEVED),
        f'<place xml:id="new_place_exemplum"><placeName>Exemplum</placeName><bibl type="source">{RETRIEVED}</bibl>'
        "</place>",
    ],
    ids=["a text's", "a blank name", "a record's"],
)
def test_a_source_without_its_name_fails(validator: Validator, tmp_path: Path, xml: str) -> None:
    found = problems(validator, tmp_path, xml)
    assert rules(found) == ["source-named"]
    assert found[0].severity == "error"


def test_a_source_with_a_link_and_no_date_retrieved_is_reported(validator: Validator, tmp_path: Path) -> None:
    found = problems(validator, tmp_path, text_source(NAME, LINK))
    assert rules(found) == ["source-retrieved"]
    assert found[0].severity == "warning"


def test_a_source_without_a_link_needs_no_date(validator: Validator, tmp_path: Path) -> None:
    assert problems(validator, tmp_path, text_source(NAME)) == []
