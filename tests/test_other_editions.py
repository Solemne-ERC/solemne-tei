# SPDX-License-Identifier: MIT
"""Another edition's pages and numbering: page breaks and milestones that name a witness listed in the file."""

from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.examples import EXAMPLES, Example, placed
from solemne_tei.validate import Problem, Validator

WITNESS = '<listWit><witness xml:id="wit-h"><bibl><ptr target="#new_bibl_hinschius_1863"/></bibl></witness></listWit>'
MILESTONE = '<milestone unit="chapter" n="5" edRef="#wit-h"/>'


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def problems(validator: Validator, tmp_path: Path, xml: str) -> list[Problem]:
    """The problems of fragments, placed in a minimal file as the guide's examples are."""
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    path = tmp_path / "fragment.xml"
    placed(Example(eg, True, "", "", 1, "fragment.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    return validator.check(path).problems


@pytest.mark.parametrize(
    "text",
    [
        f"<p>Exemplum {MILESTONE}verborum.</p>",
        f'<div type="chapter" n="4"><head type="rubric">De {MILESTONE}exemplo.</head><p>Exemplum.</p></div>',
        f'<div type="section" n="1"><div type="chapter" n="4"><p>Unum.</p></div>{MILESTONE}'
        '<div type="chapter" n="5"><p>Aliud.</p></div></div>',
    ],
)
def test_a_milestone_stands_where_its_unit_begins(validator: Validator, tmp_path: Path, text: str) -> None:
    assert problems(validator, tmp_path, WITNESS + text) == []


@pytest.mark.parametrize("attribute", ['n="5"', 'edRef="#wit-h"'])
def test_a_milestone_without_its_number_or_edition_fails(validator: Validator, tmp_path: Path, attribute: str) -> None:
    milestone = MILESTONE.replace(f" {attribute}", "")
    found = problems(validator, tmp_path, f"{WITNESS}<p>Exemplum {milestone}verborum.</p>")
    assert "relaxng" in {p.check for p in found}


@pytest.mark.parametrize("unit", ["book", "chapter", "canon", "letter", "section"])
def test_the_seed_units_pass(validator: Validator, tmp_path: Path, unit: str) -> None:
    milestone = MILESTONE.replace('"chapter"', f'"{unit}"')
    assert problems(validator, tmp_path, f"{WITNESS}<p>Exemplum {milestone}verborum.</p>") == []


@pytest.mark.parametrize("unit", ["folio", "page"])
def test_a_unit_outside_the_seeds_is_reported(validator: Validator, tmp_path: Path, unit: str) -> None:
    milestone = MILESTONE.replace('"chapter"', f'"{unit}"')
    found = problems(validator, tmp_path, f"{WITNESS}<p>Exemplum {milestone}verborum.</p>")
    assert [(p.rule, p.severity) for p in found] == [("milestone-term", "warning")]


@pytest.mark.parametrize("mark", ['<pb n="131" edRef="{ref}"/>', '<milestone unit="chapter" n="5" edRef="{ref}"/>'])
def test_the_edition_named_is_a_witness_of_the_file(validator: Validator, tmp_path: Path, mark: str) -> None:
    listed = problems(validator, tmp_path, f"{WITNESS}<p>Exemplum {mark.format(ref='#wit-h')}verborum.</p>")
    assert listed == []
    for ref in ("#wit-k", "wit-h", "#new_bibl_hinschius_1863"):
        found = problems(validator, tmp_path, f"{WITNESS}<p>Exemplum {mark.format(ref=ref)}verborum.</p>")
        assert "edref-witness" in {p.rule for p in found}, ref


def test_a_milestone_stands_off_as_a_note_holding_it(validator: Validator, tmp_path: Path) -> None:
    text = f"""{WITNESS}<p xml:id="p1">Exemplum verborum.</p>
      <listAnnotation><annotation xml:id="annotation-numbering" target="#string-range(p1,8,0)">
        <note>{MILESTONE}</note></annotation></listAnnotation>"""
    assert problems(validator, tmp_path, text) == []
