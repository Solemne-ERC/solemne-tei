# SPDX-License-Identifier: MIT
"""The guide: its parts included, each specification group referenced by the schema, its ids unique; every
element, attribute and rule with one tier; every example passing or failing as it says, and every rule with a
counter-example; the build reports an error in a part at that part's file and line."""

import re
from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.build import ODD_PATH, BuildError, check_odd, check_specification_groups, expand
from solemne_tei.examples import EXAMPLES, Example, Outcome, check, examples, placed
from solemne_tei.rules import attribute_tiers, element_tiers, rules, tiers
from solemne_tei.schema_files import COMPILED_ODD, SCHEMA_DIR, odd_version
from solemne_tei.validate import Validator

TEI = "http://www.tei-c.org/ns/1.0"
XI = "http://www.w3.org/2001/XInclude"
SCH_NS = "http://purl.oclc.org/dsdl/schematron"
GUIDE = ODD_PATH.parent
TIERS = ("required", "common", "full", "export only")
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


@pytest.fixture(scope="module")
def odd() -> etree._Element:
    # lxml refuses a document whose xml:ids repeat, so parsing it is the check that they don't.
    return etree.fromstring(expand(ODD_PATH).text)


def test_every_part_is_included(odd: etree._Element) -> None:
    root = etree.parse(str(ODD_PATH)).getroot()
    hrefs = [el.get("href") for el in root.iter(f"{{{XI}}}include")]
    assert hrefs
    included = [f"{folder}/{p.name}" for folder in ("chapters", "mappings") for p in (GUIDE / folder).glob("*.xml")]
    assert sorted(hrefs) == sorted(included)
    assert not list(odd.iter(f"{{{XI}}}*"))
    assert "xi" not in odd.nsmap


def test_every_specification_group_is_referenced_once(odd: etree._Element) -> None:
    groups = [g.get("{http://www.w3.org/XML/1998/namespace}id") for g in odd.iter(f"{{{TEI}}}specGrp")]
    refs = [r.get("target") for r in odd.iter(f"{{{TEI}}}specGrpRef")]
    assert groups
    assert sorted(refs) == sorted(f"#{g}" for g in groups)


def test_every_part_carries_the_guide_s_licence() -> None:
    for path in [ODD_PATH, *(GUIDE / "chapters").glob("*.xml")]:
        assert "<!-- SPDX-License-Identifier: CC-BY-4.0 -->" in path.read_text("utf-8").splitlines()[1], path.name


ROOT = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<TEI xmlns="http://www.tei-c.org/ns/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title type="formal">
          <idno>C.SAM-0600</idno>
          <idno type="category">C</idno>
          <idno type="type">edition</idno>
        </title>
      </titleStmt>
      <publicationStmt>
        <p>A test.</p>
      </publicationStmt>
      <sourceDesc>
        <p>Made up.</p>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
      <xi:include href="chapters/part.xml"/>
    </body>
  </text>
</TEI>
"""
PART = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<div xmlns="http://www.tei-c.org/ns/1.0" type="chapter">
  <p>Placuit.</p>
  <div type="chpater">
    <p>Placuit.</p>
  </div>
</div>
"""


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters" / "part.xml").write_text(PART, encoding="utf-8")
    path = tmp_path / "root.xml"
    path.write_text(ROOT, encoding="utf-8")
    return path


def test_expansion_places_each_element_at_its_file_and_line(root: Path) -> None:
    expanded = expand(root)
    text = expanded.text.decode("utf-8")
    assert "SPDX" not in text
    assert "xml:base" not in text
    assert "XInclude" not in text
    lines = text.splitlines()
    division = next(i for i, line in enumerate(lines, 1) if 'type="chpater"' in line)
    assert expanded.places[division] == ("chapters/part.xml", 5)
    body = next(i for i, line in enumerate(lines, 1) if "<body>" in line)
    assert expanded.places[body] == ("root.xml", 22)


def test_the_odd_check_names_the_part_and_its_line(root: Path, tmp_path: Path) -> None:
    # The package's own schema stands in for TEI's schema for ODD files, which needs a download.
    expanded = expand(root)
    path = tmp_path / "expanded.xml"
    path.write_bytes(expanded.text)
    with pytest.raises(BuildError, match=r"chapters/part\.xml:5: relaxng error"):
        check_odd(path, Validator(), expanded.places)


def schema_elements() -> set[str]:
    compiled = etree.parse(str(SCHEMA_DIR / COMPILED_ODD))
    return {e.get("ident") for e in compiled.find(f".//{{{TEI}}}schemaSpec").iter(f"{{{TEI}}}elementSpec")}


def test_the_tiers_are_the_four_of_the_header(odd: etree._Element) -> None:
    assert sorted(tiers(odd).values()) == sorted(TIERS)


def test_every_element_the_schema_allows_has_one_tier(odd: etree._Element) -> None:
    found = element_tiers(odd)
    assert set(found) == schema_elements()
    wrong = {element: named for element, named in found.items() if len(named) != 1 or named[0] not in TIERS}
    assert not wrong


def test_every_attribute_the_odd_defines_has_one_tier(odd: etree._Element) -> None:
    found = attribute_tiers(odd)
    assert "div/@type" in found
    wrong = {attribute: named for attribute, named in found.items() if len(named) != 1 or named[0] not in TIERS}
    assert not wrong


def test_every_rule_has_one_tier_and_a_part(odd: etree._Element) -> None:
    found = rules(odd)
    assert {r.check for r in found} == {"relaxng", "schematron"}
    assert [r.id for r in found if r.tier not in TIERS or not r.part or not r.description] == []
    ids = [r.id for r in found]
    assert len(ids) == len(set(ids))


def test_an_attribute_s_tier_is_not_below_its_element_s(odd: etree._Element) -> None:
    order = {tier: i for i, tier in enumerate(TIERS)}
    elements = element_tiers(odd)
    lower = [
        attribute
        for attribute, (tier,) in attribute_tiers(odd).items()
        if order[tier] < order[elements[attribute.split("/@")[0]][0]]
    ]
    assert lower == []


@pytest.fixture(scope="module")
def outcomes(odd: etree._Element) -> list[Outcome]:
    return check(examples(odd), rules(odd))


def where(example: Example) -> str:
    file, line = expand(ODD_PATH).places.get(example.line, ("solemne.odd", example.line))
    return f"{file}:{line}"


def test_every_example_passes_or_fails_as_it_says(outcomes: list[Outcome]) -> None:
    assert outcomes
    wrong = [
        f"{where(o.example)} [{o.example.rule}]: {o.why}" + "".join(f"\n    {p}" for p in o.problems)
        for o in outcomes
        if not o.ok
    ]
    assert not wrong, "\n".join(wrong)


def test_every_rule_has_a_counter_example(odd: etree._Element, outcomes: list[Outcome]) -> None:
    shown = {o.example.rule for o in outcomes if not o.example.valid and o.ok}
    assert [r.id for r in rules(odd) if r.id not in shown] == []


def example(xml: str) -> Example:
    eg = etree.fromstring(f'<egXML xmlns="{EXAMPLES}">{xml}</egXML>')
    return Example(eg, True, "", "", 1, "example.xml")


def test_a_header_part_is_placed_in_the_header() -> None:
    tree = placed(example('<editorialDecl><correction status="high"><p>Checked.</p></correction></editorialDecl>'))
    header = tree.getroot()[0]
    assert [etree.QName(c).localname for c in header] == ["fileDesc", "encodingDesc"]
    assert header.find(f"{{{TEI}}}encodingDesc/{{{TEI}}}editorialDecl/{{{TEI}}}correction") is not None


def test_a_phrase_is_placed_in_a_paragraph_and_a_division_in_the_body() -> None:
    body = placed(example("<persName>Paulus</persName>")).find(f".//{{{TEI}}}body")
    assert body.find(f"{{{TEI}}}p/{{{TEI}}}persName") is not None
    body = placed(example('<div type="chapter"><p>Placuit.</p></div>')).find(f".//{{{TEI}}}body")
    assert [etree.QName(c).localname for c in body] == ["div"]


def test_a_formal_title_replaces_the_host_s_and_a_description_its_paragraph() -> None:
    tree = placed(example('<title type="formal"><idno>C.NIC-0325</idno></title><msDesc/>'))
    titles = tree.findall(f".//{{{TEI}}}titleStmt/{{{TEI}}}title")
    assert len(titles) == 1 and titles[0].findtext(f"{{{TEI}}}idno") == "C.NIC-0325"
    source = tree.find(f".//{{{TEI}}}sourceDesc")
    assert [etree.QName(c).localname for c in source] == ["msDesc"]


# The vocabularies a Schematron rule warns outside of: the rule, and the element and attribute whose semi-open list
# holds the same terms.
VOCABULARIES = {
    "relation-term": ("relation", "name"),
    "form-term": ("objectDesc", "form"),
    "material-term": ("supportDesc", "material"),
    "script-term": ("handNote", "script"),
    "execution-term": ("handNote", "execution"),
    "decoration-term": ("decoNote", "type"),
    "entry-type": ("biblStruct", "type"),
}


@pytest.mark.parametrize("rule", sorted(VOCABULARIES))
def test_a_vocabulary_s_rule_holds_the_terms_of_its_list(odd: etree._Element, rule: str) -> None:
    element, attribute = VOCABULARIES[rule]
    listed = odd.xpath(
        f"//tei:elementSpec[@ident='{element}']//tei:attDef[@ident='{attribute}']/tei:valList[@type='semi']"
        "/tei:valItem/@ident",
        namespaces={"tei": TEI},
    )
    terms = odd.xpath(f"//sch:assert[@id='{rule}']/../sch:let[@name='terms']/@value", namespaces={"sch": SCH_NS})
    assert listed and len(terms) == 1
    assert sorted(re.findall(r"'([^']+)'", terms[0])) == sorted(listed)


def test_a_part_of_a_description_is_placed_in_a_unit_and_its_calendars_are_declared() -> None:
    xml = '<origDate when="0813" when-custom="0813~" datingMethod="#edtf" calendar="#gregorian">813</origDate>'
    tree = placed(example(xml))
    unit = tree.find(f".//{{{TEI}}}sourceDesc/{{{TEI}}}msDesc/{{{TEI}}}msPart")
    assert unit.find(f"{{{TEI}}}history/{{{TEI}}}origin/{{{TEI}}}origDate") is not None
    assert tree.find(f".//{{{TEI}}}sourceDesc/{{{TEI}}}p") is None
    calendars = tree.findall(f".//{{{TEI}}}profileDesc/{{{TEI}}}calendarDesc/{{{TEI}}}calendar")
    assert [c.get(XML_ID) for c in calendars] == ["edtf", "gregorian"]


def test_a_fragment_that_declares_edtf_keeps_its_own_declaration() -> None:
    xml = (
        '<calendarDesc><calendar xml:id="edtf"><p>EDTF.</p></calendar></calendarDesc>'
        '<p><date when="0813" when-custom="0813~" datingMethod="#edtf">813</date></p>'
    )
    calendars = placed(example(xml)).findall(f".//{{{TEI}}}calendar")
    assert [c.findtext(f"{{{TEI}}}p") for c in calendars] == ["EDTF."]


def test_a_whole_file_is_checked_as_it_is() -> None:
    tree = placed(example("<TEI><teiHeader/><text><body/></text></TEI>"))
    assert tree.getroot().tag == f"{{{TEI}}}TEI"
    assert tree.find(f".//{{{TEI}}}fileDesc") is None


def test_every_pointer_of_the_guide_leads_somewhere(odd: etree._Element) -> None:
    ids = {el.get(XML_ID) for el in odd.iter() if isinstance(el.tag, str) and el.get(XML_ID)}
    pointers = [
        (etree.QName(el).localname, target)
        for el in odd.iter(f"{{{TEI}}}ptr", f"{{{TEI}}}ref", f"{{{EXAMPLES}}}egXML")
        for target in (el.get("target") or el.get("source") or "").split()
        if target.startswith("#")
    ]
    assert pointers
    assert [(name, target) for name, target in pointers if target[1:] not in ids] == []


def test_every_source_of_an_example_is_used(odd: etree._Element) -> None:
    sources = odd.find(f".//{{{TEI}}}div[@{XML_ID}='example-sources']")
    listed = {b.get(XML_ID) for b in sources.iter(f"{{{TEI}}}bibl")}
    used = {eg.get("source")[1:] for eg in odd.iter(f"{{{EXAMPLES}}}egXML") if eg.get("source")}
    assert listed == used


def test_the_build_stops_on_a_specification_group_that_isn_t_referred_to(root: Path) -> None:
    part = root.parent / "chapters" / "part.xml"
    part.write_text(PART.replace("</div>\n", '<specGrp xml:id="lost"/>\n</div>\n', 1), encoding="utf-8")
    with pytest.raises(BuildError, match=r"chapters/part\.xml:\d+: the specGrp lost, which no specGrpRef names"):
        check_specification_groups(expand(root))


TEMPLATES = sorted((GUIDE / "templates").glob("*.xml"))


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.stem)
def test_a_template_passes_both_checks(template: Path) -> None:
    result = Validator().check(template)
    assert result.problems == [], "\n".join(str(p) for p in result.problems)


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.stem)
def test_a_template_declares_the_schema_of_its_version(template: Path) -> None:
    version = odd_version(ODD_PATH)
    tree = etree.parse(str(template))
    models = [pi for pi in tree.getroot().itersiblings(preceding=True) if isinstance(pi, etree._ProcessingInstruction)]
    hrefs = sorted(pi.get("href") for pi in models if pi.target == "xml-model")
    base = f"https://solemne-erc.github.io/solemne-tei/schema/{version}/"
    assert hrefs == [f"{base}solemne.rng", f"{base}solemne.sch"]
    assert "<!-- SPDX-License-Identifier: CC-BY-4.0 -->" in template.read_text("utf-8").splitlines()[1]


def test_the_templates_are_those_the_front_matter_names(odd: etree._Element) -> None:
    section = odd.find(f".//{{{TEI}}}div[@{XML_ID}='intro-templates']")
    named = sorted("".join(code.itertext()) for code in section.iter(f"{{{TEI}}}code") if code.text.endswith(".xml"))
    assert named == [p.name for p in TEMPLATES]


def template_elements(name: str) -> set[str]:
    return {etree.QName(el).localname for el in etree.parse(str(GUIDE / "templates" / name)).iter(tag=etree.Element)}


def test_the_minimal_template_holds_only_the_required_tier(odd: etree._Element) -> None:
    tiers = {element: named[0] for element, named in element_tiers(odd).items()}
    # TEI requires a paragraph in the publication statement and the source description, and it holds the text.
    assert {e for e in template_elements("minimal.xml") if tiers[e] != "required"} == {"p"}


def test_the_rich_template_holds_every_common_element(odd: etree._Element) -> None:
    common = {element for element, named in element_tiers(odd).items() if named[0] == "common"}
    # The project's files give a person's address for contact, which a public template leaves out.
    assert common - template_elements("rich.xml") == {"distributor", "email"}
