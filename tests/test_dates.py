# SPDX-License-Identifier: MIT
"""Dates: the bounds agree with the EDTF by years, the EDTF has its form, no bound comes after its pair, and a date's
calendars are declared. Each case is a fragment placed in a minimal valid file, as the guide's examples are."""

from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.examples import EXAMPLES, Example, placed
from solemne_tei.validate import Validator


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def schematron_rules(validator: Validator, tmp_path: Path, xml: str) -> set[str]:
    """The Schematron rules a fragment breaks; it passes the RelaxNG."""
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    path = tmp_path / "date.xml"
    placed(Example(eg, True, "", "", 1, "date.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    problems = validator.check(path).problems
    assert [p for p in problems if p.check != "schematron"] == []
    return {p.rule for p in problems}


def edtf(attributes: str) -> str:
    return f'<p>Datum <date {attributes} datingMethod="#edtf">anno</date>.</p>'


AGREE = [
    'notBefore="0801" notAfter="0900" when-custom="08XX"',
    'notBefore="0800" notAfter="0899" when-custom="08XX"',
    'notBefore="0810" notAfter="0819" when-custom="081X"',
    'notBefore="0776" notAfter="0825" when-custom="0800~"',
    'notBefore="0755" notAfter="0760" when-custom="0756?"',
    'when="0813-06-13" when-custom="0813-06-13"',
    'when="0813-06-13" when-custom="0813"',
    'notBefore="0867" notAfter="0900" when-custom="[0867..0900]"',
    'notBefore="0755" notAfter="0756" when-custom="[0755,0756]"',
    'from="0745" to="0760" from-custom="0750~" to-custom="0760"',
    'from="0750" to="0769" from-custom="075X" to-custom="076X"',
]
DISAGREE = [
    'notBefore="0901" notAfter="1000" when-custom="08XX"',
    'notBefore="0801" notAfter="0825" when-custom="0800~"',
    'when="0831" when-custom="0813"',
    'notBefore="0755" notAfter="0760" when-custom="[0755,0756]"',
    'from="0751" to="0760" from-custom="0750~" to-custom="0760"',
    'from="0745" to="0761" from-custom="0750~" to-custom="0760"',
]


@pytest.mark.parametrize("attributes", AGREE)
def test_bounds_that_agree_with_the_edtf_pass(validator: Validator, tmp_path: Path, attributes: str) -> None:
    assert "date-edtf-bounds" not in schematron_rules(validator, tmp_path, edtf(attributes))


@pytest.mark.parametrize("attributes", DISAGREE)
def test_bounds_that_disagree_with_the_edtf_are_reported(validator: Validator, tmp_path: Path, attributes: str) -> None:
    assert "date-edtf-bounds" in schematron_rules(validator, tmp_path, edtf(attributes))


@pytest.mark.parametrize(
    "value", ["0813", "0816-08", "0813-06-13%", "08XX", "081X", "0800~", "0756?", "[0867..0900]", "[0755,0756]"]
)
def test_edtf_in_its_form_passes(validator: Validator, tmp_path: Path, value: str) -> None:
    rules = schematron_rules(validator, tmp_path, edtf(f'notBefore="0700" notAfter="0999" when-custom="{value}"'))
    assert "date-edtf-form" not in rules


@pytest.mark.parametrize("value", ["sec. IX", "813", "0813/0816", "ca. 0800", "0800~~"])
def test_edtf_out_of_its_form_fails(validator: Validator, tmp_path: Path, value: str) -> None:
    rules = schematron_rules(validator, tmp_path, edtf(f'notBefore="0700" notAfter="0999" when-custom="{value}"'))
    assert "date-edtf-form" in rules


def test_edtf_without_its_dating_method_fails(validator: Validator, tmp_path: Path) -> None:
    rules = schematron_rules(validator, tmp_path, '<p><date when="0813" when-custom="0813">anno</date></p>')
    assert "date-edtf-form" in rules


@pytest.mark.parametrize(
    ("attributes", "in_order"),
    [
        ('notBefore="0800" notAfter="0900"', True),
        ('notBefore="0813-06" notAfter="0813"', True),
        ('notBefore="0813" notAfter="0813-06-13"', True),
        ('notBefore="0900" notAfter="0800"', False),
        ('notBefore="0813-07" notAfter="0813-06"', False),
        ('from="0750" to="0760"', True),
        ('from="0760" to="0750"', False),
    ],
)
def test_no_bound_comes_after_its_pair(validator: Validator, tmp_path: Path, attributes: str, in_order: bool) -> None:
    rules = schematron_rules(validator, tmp_path, f"<p><date {attributes}>anno</date></p>")
    assert ("date-bounds-order" not in rules) == in_order


def test_a_calendar_must_be_declared(validator: Validator, tmp_path: Path) -> None:
    declared = (
        '<calendarDesc><calendar xml:id="julian"><p>The Julian calendar.</p></calendar></calendarDesc>'
        '<p><date when="0813-06-13" calendar="#julian">V Idus Iunias</date></p>'
    )
    assert "calendar-declared" not in schematron_rules(validator, tmp_path, declared)
    undeclared = '<p><date when="0813-06-13" calendar="#julian">V Idus Iunias</date></p>'
    assert "calendar-declared" in schematron_rules(validator, tmp_path, undeclared)
