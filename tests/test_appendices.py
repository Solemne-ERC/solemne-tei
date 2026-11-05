# SPDX-License-Identifier: MIT
"""The guide's appendices: A lists every element, B every rule, C every category, Bible book and seed term, D every
older form the decisions name, E every row of the import formats' tables, F every release in the changelog; each
counter-example names its rule."""

import re
from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.appendices import CHANGELOG, VOCABULARIES, changelog_divisions, seeds, with_appendices
from solemne_tei.build import ODD_PATH, expand
from solemne_tei.codes import CATEGORIES, bible_books
from solemne_tei.examples import EXAMPLES
from solemne_tei.rules import XML_ID, rules
from solemne_tei.schema_files import COMPILED_ODD, SCHEMA_DIR, TEI

MAPPINGS = Path(__file__).parents[1] / "guide" / "mappings"

# The older forms the decisions name, as appendix D gives them.
OLDER_FORMS = (
    "collCode",
    "collCat",
    "collType",
    "DP",
    "P.THB.0700",
    "key",
    "Clavis",
    "collection_1234",
    "atomicUnit",
    "opener",
    "chapterGroup",
    "part",
    "authStmt",
    "num",
    "inscriptio",
    "chpater",
    "missing",
    "corresp",
    "CNIC.325.2",
    "CanApost_N",
    "SEA_N",
    "DCEL.422.369",
    "links",
    "authorities",
    "Gregorian",
    "filiation",
    "msItem",
    "SAWS",
)


@pytest.fixture(scope="module")
def guide() -> etree._Element:
    return etree.fromstring(with_appendices(expand(ODD_PATH).text, SCHEMA_DIR / COMPILED_ODD))


def div(guide: etree._Element, ident: str) -> etree._Element:
    return guide.find(f".//{{{TEI}}}div[@{XML_ID}='{ident}']")


def table(guide: etree._Element, ident: str) -> list[etree._Element]:
    return list(guide.find(f".//{{{TEI}}}table[@{XML_ID}='{ident}']").iter(f"{{{TEI}}}row"))[1:]


def cells(el: etree._Element, column: int) -> list[str]:
    rows = [r for r in el.iter(f"{{{TEI}}}row") if r.get("role") != "label"]
    return [" ".join("".join(r[column].itertext()).split()) for r in rows if len(r) > column]


def test_the_placeholders_are_all_replaced(guide: etree._Element) -> None:
    assert not list(guide.iter(f"{{{TEI}}}divGen"))
    back = [d.get(XML_ID) for d in guide.find(f".//{{{TEI}}}back").iterfind(f"{{{TEI}}}div")]
    assert back == [
        "appendix-elements",
        "appendix-rules",
        "appendix-tables",
        "appendix-older-forms",
        "appendix-mappings",
        "appendix-changes",
        "example-sources",
    ]


def test_appendix_a_lists_every_element_the_schema_allows(guide: etree._Element) -> None:
    compiled = etree.parse(str(SCHEMA_DIR / COMPILED_ODD))
    elements = {e.get("ident") for e in compiled.find(f".//{{{TEI}}}schemaSpec").iter(f"{{{TEI}}}elementSpec")}
    assert {row[0].findtext(f"{{{TEI}}}gi") for row in table(guide, "elements-table")} == elements
    div_row = next(row for row in table(guide, "elements-table") if row[0].findtext(f"{{{TEI}}}gi") == "div")
    assert "@type (common): capitulum" in "".join(div_row[3].itertext())


def test_appendix_b_lists_every_rule(guide: etree._Element) -> None:
    listed = ["".join(row[0].itertext()) for row in table(guide, "rules-table")]
    assert listed == [r.id for r in rules(etree.fromstring(expand(ODD_PATH).text))]


def test_appendix_c_lists_every_category_bible_book_and_seed(guide: etree._Element) -> None:
    assert cells(div(guide, "tables-categories"), 0) == list(CATEGORIES)
    assert cells(div(guide, "tables-bible"), 0) == [b.code for b in bible_books()]
    listed = cells(div(guide, "tables-vocabularies"), 0)
    expected = [
        term
        for _, element, attribute in VOCABULARIES
        for term, _ in seeds(SCHEMA_DIR / COMPILED_ODD, element, attribute)
    ]
    assert listed == expected


def test_appendix_c_gives_oxford_terms_where_the_seed_is_the_bodleians(guide: etree._Element) -> None:
    rows = {r[0].findtext(f"{{{TEI}}}val"): r for r in div(guide, "tables-vocabularies").iter(f"{{{TEI}}}row")}
    assert "".join(rows["minusculeCaroline"][3].itertext()) == "minusculeCaroline"
    assert "".join(rows["quire"][2].itertext()) == "the old Solemne guide"
    assert "".join(rows["isVerbatimOf"][2].itertext()) == "SAWS"


def test_appendix_d_has_a_row_for_every_older_form(guide: etree._Element) -> None:
    older = " ".join(cells(div(guide, "appendix-older-forms"), 0))
    assert [form for form in OLDER_FORMS if not re.search(rf"(?<![\w.]){re.escape(form)}(?![\w])", older)] == []
    # Each row says where the guide explains the new form, and points somewhere.
    ids = {el.get(XML_ID) for el in guide.iter() if el.get(XML_ID)}
    for row in table(guide, "older-forms-table"):
        if row.get("role") != "label":
            targets = [p.get("target")[1:] for p in row[2].iter(f"{{{TEI}}}ptr")]
            assert targets and set(targets) <= ids


def test_appendix_e_holds_every_row_of_the_formats_tables(guide: etree._Element) -> None:
    appendix = div(guide, "appendix-mappings")
    for path in sorted(MAPPINGS.glob("*.xml")):
        mapping = etree.parse(str(path)).getroot()
        included = appendix.find(f".//{{{TEI}}}table[@{XML_ID}='{mapping.get(XML_ID)}']")
        assert included is not None, path.name
        assert len(included.findall(f"{{{TEI}}}row")) == len(mapping.findall(f"{{{TEI}}}row"))


def test_appendix_f_has_every_release_in_the_changelog(guide: etree._Element) -> None:
    releases = re.findall(r"^## (\S+)", CHANGELOG.read_text("utf-8"), re.M)
    heads = [d.findtext(f"{{{TEI}}}head").split()[0] for d in div(guide, "appendix-changes").iterfind(f"{{{TEI}}}div")]
    assert heads == releases


def test_the_changelogs_markdown_becomes_nested_lists_paragraphs_and_inline_forms() -> None:
    text = (
        "# Changelog\n\nPreface.\n\n## 1.0.0 (2027-01-01)\n\nA paragraph\nover two lines.\n\n### What changes\n\n"
        "- **Bold:** with `code`;\n  continued.\n  - nested\n\n  A paragraph in the item.\n- second\n"
    )
    (release,) = changelog_divisions(text)
    assert release.get(XML_ID) == "changes-1.0.0"
    assert release[1].text == "A paragraph over two lines."
    section = release[2]
    (listed,) = section.iterfind(f"{{{TEI}}}list")
    first, second = listed
    assert first[0].text == "Bold:" and first[1].text == "code"
    assert first[1].tail == "; continued."
    assert [etree.QName(c).localname for c in first] == ["hi", "code", "list", "p"]
    assert second.text == "second"


def test_every_counter_example_names_its_rule(guide: etree._Element) -> None:
    for eg in guide.iter(f"{{{EXAMPLES}}}egXML"):
        if eg.get("valid") == "false":
            label = eg.getprevious()
            assert label.find(f"{{{TEI}}}ref").get("target") == f"#rule-{eg.get('n')}"
