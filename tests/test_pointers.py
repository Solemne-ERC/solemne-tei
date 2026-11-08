# SPDX-License-Identifier: MIT
"""Pointers to sources: a code of any category may be pointed to, and the pointers' prefixes are the categories'."""

import re
from collections.abc import Callable
from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.build import ODD_PATH, expand
from solemne_tei.codes import CATEGORIES, code_prefix
from solemne_tei.examples import EXAMPLES, Example, placed
from solemne_tei.validate import Problem, Validator

TEI = "http://www.tei-c.org/ns/1.0"
SCH = "http://purl.oclc.org/dsdl/schematron"

# W isn't a category's prefix: the pattern keeps it, though no file uses it yet.
EXTRA_PREFIXES = {"W"}


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


@pytest.fixture(scope="module")
def odd() -> etree._Element:
    return etree.fromstring(expand(ODD_PATH).text)


def problems(validator: Validator, tmp_path: Path, xml: str) -> list[Problem]:
    """The problems of a fragment of the text, placed in a minimal file."""
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    path = tmp_path / "pointer.xml"
    placed(Example(eg, True, "", "", 1, "pointer.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    return validator.check(path).problems


def note(pointer: str, words: str = "Cod. Theod. 16, 2, 47") -> str:
    return f'<p>Placuit ut episcopi maneant.<note type="source" source="{pointer}">{words}</note></p>'


def quote(pointer: str) -> str:
    return f'<p><cit><ref>Lex ait:</ref> <quote source="{pointer}">Clericos etiam</quote></cit></p>'


def prefixes(pattern: str) -> set[str]:
    """The prefixes of the pattern's group of codes: the alternatives before an escaped dot."""
    groups = re.findall(r"\(((?:[A-Z]+\|)+[A-Z]+)\)\\\.", pattern)
    assert groups
    return {prefix for group in groups for prefix in group.split("|")}


def category_prefixes() -> set[str]:
    return {code_prefix(category) for category in CATEGORIES if category != "UNK"}


def test_the_pointer_pattern_takes_the_categories_prefixes(odd: etree._Element) -> None:
    pattern = odd.find(f".//{{{TEI}}}dataSpec[@ident='solemne.pointer']//{{{TEI}}}dataRef").get("restriction")
    assert prefixes(pattern) == category_prefixes() | EXTRA_PREFIXES


def test_the_note_words_warning_takes_the_categories_prefixes(odd: etree._Element) -> None:
    rule = odd.find(f".//{{{SCH}}}report[@id='source-note-codes']").get("test")
    assert prefixes(rule) == category_prefixes() | EXTRA_PREFIXES


@pytest.mark.parametrize(
    "pointer",
    [
        "LR.CTh-0438",
        "LR.CTh-0438_16.2.47",
        "cf_LR.CTh-0438_16.2.47.1",
        "CPT.Exemplum-0802_5",
        "CHA.Exemplum-0900",
        "W.Exemplum_3",
    ],
)
@pytest.mark.parametrize("form", [note, quote])
def test_a_pointer_to_any_category_passes(
    validator: Validator, tmp_path: Path, form: Callable[[str], str], pointer: str
) -> None:
    assert problems(validator, tmp_path, form(pointer)) == []


@pytest.mark.parametrize("pointer", ["CAN.SAM-0600_3", "LRX.CTh-0438"])
def test_a_prefix_no_category_makes_fails(validator: Validator, tmp_path: Path, pointer: str) -> None:
    assert {p.check for p in problems(validator, tmp_path, note(pointer))} == {"relaxng"}


@pytest.mark.parametrize("code", ["LR.CTh-0438_16.2.47", "CPT.Exemplum-0802_5", "CHA.Exemplum-0900"])
def test_a_code_of_the_new_categories_in_a_note_s_words_is_reported(
    validator: Validator, tmp_path: Path, code: str
) -> None:
    found = problems(validator, tmp_path, note("C.NIC-0325_3", f"{code}; Cod. Theod. 16, 2, 47."))
    assert [(p.rule, p.severity) for p in found] == [("source-note-codes", "warning")]
