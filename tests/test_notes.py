# SPDX-License-Identifier: MIT
"""Notes in the text: a reception note stands inline or in the standOff, as the other notes' layers do; codes left in
a source or reception note's words are reported, inline or stand-off, but Gratian's abbreviations aren't taken for
codes; an attribution names the sources no words name, in an inscription or a division. Each case is a fragment placed
in a minimal valid file, as the guide's examples are."""

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
@pytest.mark.parametrize("code", ["C.NIC-0325_15", "D.LEO-0447-414_11", "C.MEA_0845", "C.NIC.325_17", "MAT_18_19"])
def test_a_code_in_a_note_s_words_is_reported(
    validator: Validator, tmp_path: Path, form: Form, note_type: str, code: str
) -> None:
    found = problems(validator, tmp_path, form(note_type, f"{code}; Burchard I, 135."))
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


def attribution_in_inscription(source: str, words: str = "Clavis canonum's author group.") -> str:
    return (
        f'<div type="chapter" n="1"><head type="inscription">ITEM <note type="attribution" source="{source}">'
        f"{words}</note></head><p>Placuit ut episcopi maneant.</p></div>"
    )


def attribution_in_division(source: str) -> str:
    return (
        f'<div type="chapter" n="1"><note type="attribution" source="{source}">Clavis canonum\'s author groups.</note>'
        '<head type="rubric">De episcopis.</head><p>Placuit ut episcopi maneant.</p></div>'
    )


def attribution_stand_off(source: str) -> str:
    return (
        '<div type="chapter" n="1"><head type="inscription" xml:id="inscription-1">ITEM</head>'
        "<p>Placuit ut episcopi maneant.</p></div>"
        '<listAnnotation><annotation xml:id="attribution-1" target="#inscription-1">'
        f'<note type="attribution" source="{source}"/></annotation></listAnnotation>'
    )


def test_attribution_is_among_the_note_types() -> None:
    assert "attribution" in closed_lists()["note"]["type"]


@pytest.mark.parametrize("form", [attribution_in_inscription, attribution_in_division, attribution_stand_off])
@pytest.mark.parametrize(
    "source", ["#PERS.12", "#EVENT.4", "#new_person_exemplus", "#new_work_exemplum", "C.NIC-0325", "#PERS.40 #EVENT.9"]
)
def test_an_attribution_passes_in_an_inscription_a_division_or_the_standoff(
    validator: Validator, tmp_path: Path, form: Callable[[str], str], source: str
) -> None:
    assert problems(validator, tmp_path, form(source)) == []


@pytest.mark.parametrize("source", ["#leo", "#PLACE.3", "#new_place_exemplum", "#PERS.12 #leo"])
def test_an_attribution_points_to_persons_events_and_works(validator: Validator, tmp_path: Path, source: str) -> None:
    found = problems(validator, tmp_path, attribution_in_inscription(source))
    assert {p.rule for p in found} == {"attribution-source"}


def test_an_attribution_names_its_sources(validator: Validator, tmp_path: Path) -> None:
    xml = (
        '<div type="chapter" n="1"><head type="inscription">ITEM <note type="attribution">Leo.</note></head>'
        "<p>P.</p></div>"
    )
    assert {p.rule for p in problems(validator, tmp_path, xml)} == {"attribution-source"}


@pytest.mark.parametrize(
    "xml",
    [
        '<p>Placuit ut episcopi maneant.<note type="attribution" source="#PERS.12"/></p>',
        '<div type="chapter" n="1"><head type="rubric">De episcopis <note type="attribution" source="#PERS.12"/>'
        "</head><p>P.</p></div>",
    ],
)
def test_an_attribution_stands_in_an_inscription_or_a_division(validator: Validator, tmp_path: Path, xml: str) -> None:
    assert {p.rule for p in problems(validator, tmp_path, xml)} == {"attribution-place"}


@pytest.mark.parametrize("note_type", ["source", "reception", "parallel"])
def test_only_an_attribution_points_to_records(validator: Validator, tmp_path: Path, note_type: str) -> None:
    xml = f'<p>Placuit ut episcopi maneant.<note type="{note_type}" source="#PERS.12"/></p>'
    assert {p.rule for p in problems(validator, tmp_path, xml)} == {"note-source-records"}


def test_an_attribution_s_source_is_a_pointer_not_a_name(validator: Validator, tmp_path: Path) -> None:
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{attribution_in_inscription("Leo")}</egXML>')
    path = tmp_path / "note.xml"
    placed(Example(eg, True, "", "", 1, "note.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    assert not validator.check(path).passes_relaxng


def test_a_code_in_an_attribution_s_words_is_reported(validator: Validator, tmp_path: Path) -> None:
    found = problems(validator, tmp_path, attribution_in_inscription("#EVENT.4", "Clavis: C.NIC-0325."))
    assert [(p.rule, p.severity) for p in found] == [("source-note-codes", "warning")]
