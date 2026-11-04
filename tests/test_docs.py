# SPDX-License-Identifier: MIT
"""The guide's HTML: appendix A lists every element, appendix B every rule, each counter-example names its rule,
and the HTML builds when the build's sources are cached."""

from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.build import CACHE_DIR, ODD_PATH, expand
from solemne_tei.cli import main
from solemne_tei.docs import with_appendices
from solemne_tei.examples import EXAMPLES
from solemne_tei.rules import XML_ID, rules
from solemne_tei.schema_files import COMPILED_ODD, SCHEMA_DIR, TEI

STYLESHEETS = CACHE_DIR / "tei-xsl-7.61.0"


@pytest.fixture(scope="module")
def guide() -> etree._Element:
    return etree.fromstring(with_appendices(expand(ODD_PATH).text, SCHEMA_DIR / COMPILED_ODD))


def table(guide: etree._Element, ident: str) -> list[etree._Element]:
    return list(guide.find(f".//{{{TEI}}}table[@{XML_ID}='{ident}']").iter(f"{{{TEI}}}row"))[1:]


def test_appendix_a_lists_every_element_the_schema_allows(guide: etree._Element) -> None:
    compiled = etree.parse(str(SCHEMA_DIR / COMPILED_ODD))
    elements = {e.get("ident") for e in compiled.find(f".//{{{TEI}}}schemaSpec").iter(f"{{{TEI}}}elementSpec")}
    assert {row[0].findtext(f"{{{TEI}}}gi") for row in table(guide, "elements-table")} == elements
    div = next(row for row in table(guide, "elements-table") if row[0].findtext(f"{{{TEI}}}gi") == "div")
    assert "@type (common): capitulum" in "".join(div[3].itertext())


def test_appendix_b_lists_every_rule(guide: etree._Element) -> None:
    listed = ["".join(row[0].itertext()) for row in table(guide, "rules-table")]
    assert listed == [r.id for r in rules(etree.fromstring(expand(ODD_PATH).text))]
    assert not list(guide.iter(f"{{{TEI}}}divGen"))


def test_every_counter_example_names_its_rule(guide: etree._Element) -> None:
    for eg in guide.iter(f"{{{EXAMPLES}}}egXML"):
        if eg.get("valid") == "false":
            label = eg.getprevious()
            assert label.find(f"{{{TEI}}}ref").get("target") == f"#rule-{eg.get('n')}"


@pytest.mark.skipif(not STYLESHEETS.exists(), reason="TEI's stylesheets aren't cached: run solemne-tei build first")
def test_the_html_builds(tmp_path: Path) -> None:
    assert main(["docs", "--html", "--out", str(tmp_path)]) == 0
    page = (tmp_path / "guide.html").read_text("utf-8")
    assert "The elements and attributes" in page
    assert 'id="rule-fragment-order"' in page
    assert 'id="marked-fragments"' in page
