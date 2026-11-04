# SPDX-License-Identifier: MIT
"""The code tables and the lists command: the Bible's codes and the categories are those the ODD checks."""

import json
import re

import pytest
from lxml import etree

from solemne_tei.build import ODD_PATH
from solemne_tei.cli import main
from solemne_tei.codes import CATEGORIES, bible_books
from solemne_tei.schema_files import closed_lists

TEI = "http://www.tei-c.org/ns/1.0"
SCH = "http://purl.oclc.org/dsdl/schematron"


def odd() -> etree._ElementTree:
    return etree.parse(str(ODD_PATH))


def test_the_bible_codes_are_those_of_the_odd_s_pointer_pattern() -> None:
    pattern = odd().find(f".//{{{TEI}}}dataSpec[@ident='solemne.pointer']//{{{TEI}}}dataRef").get("restriction")
    books = re.search(r"\((GEN\|[0-9A-Z|]+)\)", pattern)
    assert books
    assert [book.code for book in bible_books()] == books.group(1).split("|")


def test_the_bible_table_names_73_books_by_testament() -> None:
    books = bible_books()
    assert len(books) == len({book.code for book in books}) == 73
    assert {book.testament for book in books} == {"ot", "nt", "ap"}
    assert all(book.name for book in books)


def test_the_categories_are_those_the_odd_checks() -> None:
    rule = odd().find(f".//{{{SCH}}}assert[@id='category-value']")
    assert set(CATEGORIES) == set(re.findall(r"'([A-Z]+)'", rule.get("test")))


def test_the_lists_command_prints_the_lists(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lists"]) == 0
    out = capsys.readouterr().out
    assert "div/@type: " in out
    assert "  MAT  Matthaeus" in out
    assert " ".join(CATEGORIES) in out


def test_the_lists_command_prints_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lists", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["closed_lists"] == closed_lists()
    assert payload["categories"] == list(CATEGORIES)
    assert payload["bible"][0] == {"code": "GEN", "name": "Genesis", "testament": "ot"}
