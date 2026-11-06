# SPDX-License-Identifier: MIT
"""Notes in the text: a reception note stands inline or in the standOff, as the other notes' layers do; codes left in
a source or reception note's words are reported, inline or stand-off, but Gratian's abbreviations aren't taken for
codes. Each case is a fragment placed in a minimal valid file, as the guide's examples are."""

from collections.abc import Callable
from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.examples import EXAMPLES, Example, placed
from solemne_tei.schema_files import closed_lists
from solemne_tei.validate import Problem, Validator

Form = Callable[[str, str], str]


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def problems(validator: Validator, tmp_path: Path, xml: str) -> list[Problem]:
    """The problems of a fragment, which passes the RelaxNG."""
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    path = tmp_path / "note.xml"
    placed(Example(eg, True, "", "", 1, "note.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    found = validator.check(path).problems
    assert [p for p in found if p.check != "schematron"] == []
    return found


def inline(note_type: str, words: str) -> str:
    return f'<p>Placuit ut episcopi maneant.<note type="{note_type}">{words}</note></p>'


def stand_off(note_type: str, words: str) -> str:
    return (
        '<p><anchor xml:id="start"/>Placuit ut episcopi maneant.<anchor xml:id="end"/></p>'
        '<listAnnotation><annotation xml:id="later" target="#range(start,end)">'
        f'<note type="{note_type}">{words}</note></annotation></listAnnotation>'
    )


def test_reception_is_among_the_note_types() -> None:
    assert "reception" in closed_lists()["note"]["type"]


@pytest.mark.parametrize("form", [inline, stand_off])
def test_a_reception_note_passes_inline_and_stand_off(validator: Validator, tmp_path: Path, form: Form) -> None:
    assert problems(validator, tmp_path, form("reception", "Burchard I, 135; Ivo, Decr. V, 234.")) == []


@pytest.mark.parametrize("form", [inline, stand_off])
@pytest.mark.parametrize("note_type", ["source", "reception"])
def test_a_code_in_a_note_s_words_is_reported(validator: Validator, tmp_path: Path, form: Form, note_type: str) -> None:
    found = problems(validator, tmp_path, form(note_type, "Burchard I, 135; C.NIC-0325_15."))
    assert [(p.rule, p.severity) for p in found] == [("source-note-codes", "warning")]


@pytest.mark.parametrize(
    "words",
    [
        "Cf.concil.Mogunt.847 c.7; l.l.p.178, v. etiam c.34 D.5 de consecr.",
        "Ivo, Decr. VI, 12; c. 2 C.16 qu. 2.",
        "Gratian D.LXXVI, c. 1.",
    ],
)
@pytest.mark.parametrize("note_type", ["source", "reception"])
def test_gratian_s_abbreviations_are_not_taken_for_codes(
    validator: Validator, tmp_path: Path, note_type: str, words: str
) -> None:
    assert problems(validator, tmp_path, inline(note_type, words)) == []


def test_a_parallel_s_words_are_not_checked_for_codes(validator: Validator, tmp_path: Path) -> None:
    assert problems(validator, tmp_path, inline("parallel", "Cf. C.NIC-0325_15.")) == []
