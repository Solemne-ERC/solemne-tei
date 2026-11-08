# SPDX-License-Identifier: MIT
"""A number heading asks for @n only on the divisions cited by their number."""

from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.examples import EXAMPLES, Example, placed
from solemne_tei.validate import Validator


@pytest.fixture(scope="module")
def validator() -> Validator:
    return Validator()


def rules(validator: Validator, tmp_path: Path, xml: str) -> list[str]:
    """The rules a fragment of the text breaks, placed in a minimal file."""
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    path = tmp_path / "numbers.xml"
    placed(Example(eg, True, "", "", 1, "numbers.xml")).write(str(path), xml_declaration=True, encoding="UTF-8")
    return [p.rule for p in validator.check(path).problems]


def numbered(division: str, heading: str = "CTh.16.2.47pr.") -> str:
    return f'<div type="{division}"><head type="number">{heading}</head><p>Idem a. et caes.</p></div>'


@pytest.mark.parametrize("division", ["preface", "closer", "subscriptions"])
def test_a_division_cited_by_its_prefix_needs_no_n(validator: Validator, tmp_path: Path, division: str) -> None:
    assert rules(validator, tmp_path, numbered(division)) == []


def test_a_register_with_a_number_heading_needs_no_n(validator: Validator, tmp_path: Path) -> None:
    register = (
        '<div type="register"><head type="number">Capitula</head>'
        '<div type="registerItem" n="1"><head type="number">I</head><head type="rubric">De fide</head></div></div>'
    )
    assert rules(validator, tmp_path, register) == []


@pytest.mark.parametrize("division", ["chapter", "section"])
def test_a_division_cited_by_its_number_still_needs_n(validator: Validator, tmp_path: Path, division: str) -> None:
    assert rules(validator, tmp_path, numbered(division, "Cap. I.")) == ["number-heading-n"]


def test_a_register_item_still_needs_n(validator: Validator, tmp_path: Path) -> None:
    register = (
        '<div type="register">'
        '<div type="registerItem"><head type="number">I</head><head type="rubric">De fide</head></div></div>'
    )
    assert rules(validator, tmp_path, register) == ["number-heading-n"]


def test_a_principium_with_its_id_line_passes(validator: Validator, tmp_path: Path) -> None:
    law = (
        '<div type="chapter" n="47">'
        f"{numbered('preface')}"
        '<div type="chapter" n="1"><head type="number">CTh.16.2.47.1</head><p>Clericos etiam.</p></div>'
        "</div>"
    )
    assert rules(validator, tmp_path, law) == []
