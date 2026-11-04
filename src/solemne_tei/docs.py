# SPDX-License-Identifier: MIT
"""The guide as HTML.

The expanded ODD gets its generated appendices in place of the placeholders (`divGen`) its back matter holds: A, the
elements and attributes, from the compiled ODD and the specifications; B, every rule, with its check, severity, tier
and part. Each counter-example is labelled with the rule it breaks. The ODD is then compiled by TEI's `odd2odd`, as
the build does, and made into one page by TEI's `odd2html`, run by SaxonC-HE. The HTML is plain: TEI's own
stylesheet. It runs in a clone of the repository, offline once the build's sources are cached.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from lxml import etree

from solemne_tei.build import CACHE_DIR, ODD_PATH, REPOSITORY, Saxon, Tools, compile_odd, expand, stylesheet_params
from solemne_tei.examples import EXAMPLES
from solemne_tei.logs import logger
from solemne_tei.rules import XML_ID, attribute_tiers, element_tiers, rules
from solemne_tei.schema_files import TEI, closed_lists_of

HTML_DIR = REPOSITORY / "build" / "html"
GUIDE_HTML = "guide.html"


def _t(name: str) -> str:
    return f"{{{TEI}}}{name}"


def _el(name: str, text: str = "", **attributes: str) -> etree._Element:
    el = etree.Element(_t(name), {k.replace("xml_id", XML_ID): v for k, v in attributes.items()})
    el.text = text or None
    return el


def _row(*cells: etree._Element | str, **attributes: str) -> etree._Element:
    row = _el("row", **attributes)
    for content in cells:
        cell = etree.SubElement(row, _t("cell"))
        if isinstance(content, str):
            cell.text = content
        else:
            cell.append(content)
    return row


def _generated(divgen: etree._Element, intro: str, table: etree._Element) -> etree._Element:
    """A division in place of a placeholder: its id, its heading, a paragraph, and the table."""
    div = _el("div", xml_id=divgen.get(XML_ID, ""))
    for head in divgen.iterfind(_t("head")):
        div.append(head)
    div.append(_el("p", intro))
    div.append(table)
    return div


def elements_appendix(odd: etree._Element, compiled: Path, divgen: etree._Element) -> etree._Element:
    """Appendix A: every element the schema allows, its module and tier, and the attributes the specifications
    define or change, each with its tier and, for a closed list, its values."""
    tree = etree.parse(str(compiled))
    modules = {e.get("ident"): e.get("module", "") for e in tree.find(f".//{_t('schemaSpec')}").iter(_t("elementSpec"))}
    lists = closed_lists_of(compiled)
    tiers = element_tiers(odd)
    attributes: dict[str, list[str]] = {}
    for name, (tier,) in sorted(attribute_tiers(odd).items()):
        element, attribute = name.split("/@")
        values = lists.get(element, {}).get(attribute)
        attributes.setdefault(element, []).append(
            f"@{attribute} ({tier})" + (f": {', '.join(values)}" if values else "")
        )
    table = _el("table", xml_id="elements-table")
    table.append(_row("Element", "Module", "Tier", "Attributes the guide defines or changes", role="label"))
    for element in sorted(modules, key=str.lower):
        table.append(
            _row(_el("gi", element), modules[element], tiers[element][0], "; ".join(attributes.get(element, [])))
        )
    intro = (
        "Every element the schema allows, with the TEI module it comes from and its tier, and the attributes the "
        "guide's specifications define or change, each with its tier and, for a closed list, its values. Generated "
        "from the specifications."
    )
    return _generated(divgen, intro, table)


def rules_appendix(odd: etree._Element, divgen: etree._Element) -> etree._Element:
    """Appendix B: every rule, its check, severity and tier, and the part that explains it."""
    heads = {
        div.get(XML_ID): " ".join("".join(div.find(_t("head")).itertext()).split())
        for div in odd.iter(_t("div"))
        if div.get(XML_ID) and div.find(_t("head")) is not None
    }
    table = _el("table", xml_id="rules-table")
    table.append(_row("Rule", "Check", "Severity", "Tier", "Part", "What it requires", role="label"))
    for rule in rules(odd):
        part = _el("ref", heads.get(rule.part, rule.part), target=f"#{rule.part}")
        check = "RelaxNG" if rule.check == "relaxng" else "Schematron"
        # TEI's HTML doesn't give a row its id: an anchor in the first cell carries it.
        name = _el("ident", rule.id)
        name.insert(0, _el("anchor", xml_id=f"rule-{rule.id}"))
        name[0].tail, name.text = rule.id, None
        table.append(_row(name, check, rule.severity, rule.tier, part, rule.description))
    intro = (
        "Every rule of the schema: the RelaxNG's restrictions, which the import refuses a file for breaking, and the "
        "Schematron's rules, whose errors and warnings it reports. Each has its tier and the part that explains it, "
        "where a counter-example shows it broken. Generated from the specifications."
    )
    return _generated(divgen, intro, table)


def label_counter_examples(odd: etree._Element) -> None:
    """Name the rule each counter-example breaks, before it, with a link to the rule in appendix B."""
    for eg in list(odd.iter(f"{{{EXAMPLES}}}egXML")):
        if eg.get("valid") != "false" or etree.QName(eg.getparent()).localname != "div":
            continue
        label = _el("p", "Breaks ")
        label.append(_el("ref", eg.get("n", ""), target=f"#rule-{eg.get('n', '')}"))
        label[-1].tail = ":"
        eg.addprevious(label)


def with_appendices(expanded: bytes, compiled: Path) -> bytes:
    """The expanded ODD with its appendices generated and its counter-examples labelled."""
    odd = etree.fromstring(expanded)
    for divgen in list(odd.iter(_t("divGen"))):
        kind = divgen.get("type")
        if kind == "elements":
            generated = elements_appendix(odd, compiled, divgen)
        elif kind == "rules":
            generated = rules_appendix(odd, divgen)
        else:
            continue
        divgen.getparent().replace(divgen, generated)
    label_counter_examples(odd)
    return etree.tostring(odd, xml_declaration=True, encoding="UTF-8")


def html(out: Path = HTML_DIR, cache: Path = CACHE_DIR, odd: Path = ODD_PATH) -> Path:
    """Write the guide as one HTML page into `out`, and return its path."""
    tools = Tools.prepare(cache)
    saxon = Saxon()
    work = cache / "docs"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    expanded = expand(odd)
    source = work / "guide.odd"
    source.write_bytes(expanded.text)
    compiled = work / "guide.compiled.odd"
    compile_odd(saxon, tools, source, compiled)
    logger.info("Generating the appendices")
    source.write_bytes(with_appendices(expanded.text, compiled))
    compile_odd(saxon, tools, source, compiled)
    logger.info("Writing the HTML")
    page = saxon.run(tools.stylesheets / "odds" / "odd2html.xsl", compiled, **stylesheet_params(tools))
    out.mkdir(parents=True, exist_ok=True)
    path = out / GUIDE_HTML
    path.write_text(page, "utf-8")
    return path
