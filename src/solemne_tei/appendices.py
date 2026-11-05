# SPDX-License-Identifier: MIT
"""The guide's generated appendices.

The ODD's back matter holds placeholders (`divGen`) for the appendices that are generated rather than written: A, the
elements and attributes, from the compiled ODD and the specifications; B, every rule, with its check, severity, tier
and part; C, the code tables and the vocabularies' seeds, from the package's tables and the ODD's lists; F, the
changes, from the changelog. The HTML and the PDF are made from the expanded ODD with these in place of the
placeholders, and with each counter-example labelled with the rule it breaks; the packaged ODD keeps the placeholders.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from pathlib import Path

from lxml import etree

from solemne_tei.codes import bible_books
from solemne_tei.examples import EXAMPLES
from solemne_tei.formats import BODLEIAN
from solemne_tei.rules import XML_ID, attribute_tiers, element_tiers, rules
from solemne_tei.schema_files import TEI, closed_lists_of

CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"
RNG = "http://relaxng.org/ns/structure/1.0"

# The vocabularies that grow, whose seeds appendix C lists: a title, the element and the attribute.
VOCABULARIES = (
    ("Object forms", "objectDesc", "form"),
    ("Materials", "supportDesc", "material"),
    ("Scripts", "handNote", "script"),
    ("Execution", "handNote", "execution"),
    ("Decoration", "decoNote", "type"),
    ("Relation types", "relation", "name"),
)
# The relation types taken from SAWS, the others being the model's.
SAWS_TYPES = ("isVerbatimOf", "isVariantOf", "isShorterVersionOf")
TESTAMENTS = {"ot": "Old Testament", "nt": "New Testament", "ap": "deuterocanonical"}


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


def _table(head: str, labels: Iterable[str], rows: Iterable[etree._Element], **attributes: str) -> etree._Element:
    table = _el("table", **attributes)
    if head:
        table.append(_el("head", head))
    table.append(_row(*labels, role="label"))
    table.extend(rows)
    return table


def _generated(divgen: etree._Element, intro: str, *content: etree._Element) -> etree._Element:
    """A division in place of a placeholder: its id, its heading, a paragraph, and what it holds."""
    div = _el("div", xml_id=divgen.get(XML_ID, ""))
    for head in divgen.iterfind(_t("head")):
        div.append(head)
    div.append(_el("p", intro))
    div.extend(content)
    return div


def _words(el: etree._Element) -> str:
    return " ".join("".join(el.itertext()).split())


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
    rows = (
        _row(_el("gi", element), modules[element], tiers[element][0], "; ".join(attributes.get(element, [])))
        for element in sorted(modules, key=str.lower)
    )
    table = _table("", ("Element", "Module", "Tier", "Attributes the guide defines or changes"), rows)
    table.set(XML_ID, "elements-table")
    intro = (
        "Every element the schema allows, with the TEI module it comes from and its tier, and the attributes the "
        "guide's specifications define or change, each with its tier and, for a closed list, its values. Generated "
        "from the specifications."
    )
    return _generated(divgen, intro, table)


def rules_appendix(odd: etree._Element, divgen: etree._Element) -> etree._Element:
    """Appendix B: every rule, its check, severity and tier, and the part that explains it."""
    heads = {
        div.get(XML_ID): _words(div.find(_t("head")))
        for div in odd.iter(_t("div"))
        if div.get(XML_ID) and div.find(_t("head")) is not None
    }
    rows = []
    for rule in rules(odd):
        part = _el("ref", heads.get(rule.part, rule.part), target=f"#{rule.part}")
        check = "RelaxNG" if rule.check == "relaxng" else "Schematron"
        # TEI's HTML doesn't give a row its id: an anchor in the first cell carries it.
        name = _el("ident", rule.id)
        name.insert(0, _el("anchor", xml_id=f"rule-{rule.id}"))
        name[0].tail, name.text = rule.id, None
        rows.append(_row(name, check, rule.severity, rule.tier, part, rule.description))
    table = _table("", ("Rule", "Check", "Severity", "Tier", "Part", "What it requires"), rows)
    table.set(XML_ID, "rules-table")
    intro = (
        "Every rule of the schema: the RelaxNG's restrictions, which the import refuses a file for breaking, and the "
        "Schematron's rules, whose errors and warnings it reports. Each has its tier and the part that explains it, "
        "where a counter-example shows it broken. Generated from the specifications."
    )
    return _generated(divgen, intro, table)


def categories(odd: etree._Element) -> list[tuple[str, str]]:
    """The categories and what each is, from the list in the part on the header."""
    listed = odd.find(f".//{_t('list')}[@{XML_ID}='category-list']")
    if listed is None:
        raise ValueError("the ODD has no list of categories (category-list)")
    found = []
    for item in listed.iterfind(_t("item")):
        code = _words(item.find(_t("val")))
        found.append((code, _words(item).removeprefix(code).lstrip(": ").rstrip(";.")))
    return found


def seeds(compiled: Path, element: str, attribute: str) -> list[tuple[str, str]]:
    """A vocabulary's seeds and what each is: its attribute's semi-open list in the compiled ODD."""
    tree = etree.parse(str(compiled))
    path = f".//{_t('elementSpec')}[@ident='{element}']//{_t('attDef')}[@ident='{attribute}']/{_t('valList')}"
    found = tree.find(path)
    if found is None or found.get("type") != "semi":
        raise ValueError(f"{element}/@{attribute} has no semi-open list in {compiled.name}")
    return [(item.get("ident"), _words(item.find(_t("desc")))) for item in found.iterfind(_t("valItem"))]


def bodleian_values(element: str, attribute: str, rng: Path = BODLEIAN.relaxng) -> set[str]:
    """The values the Bodleian's schema lists for an element's attribute: Oxford's terms, which ours are seeded
    with."""
    values: set[str] = set()
    for el in etree.parse(str(rng)).iter(f"{{{RNG}}}element"):
        if el.get("name") == element:
            for att in _own_attributes(el):
                if att.get("name") == attribute:
                    values.update(v.text for v in att.iter(f"{{{RNG}}}value"))
    return values


def _own_attributes(element: etree._Element) -> Iterator[etree._Element]:
    """The attributes a RelaxNG element pattern defines itself, not those of the elements inside it."""
    stack = list(element)
    while stack:
        node = stack.pop()
        if not isinstance(node.tag, str) or node.tag == f"{{{RNG}}}element":
            continue
        if node.tag == f"{{{RNG}}}attribute":
            yield node
        stack.extend(node)


def tables_appendix(odd: etree._Element, compiled: Path, divgen: etree._Element) -> etree._Element:
    """Appendix C: the categories, the Bible's books with their codes, and each vocabulary's seeds with where they
    come from and their equivalents."""
    category_rows = (_row(_el("val", code), what) for code, what in categories(odd))
    book_rows = (_row(_el("code", b.code), b.name, TESTAMENTS[b.testament]) for b in bible_books())
    vocabularies = []
    for title, element, attribute in VOCABULARIES:
        if element == "relation":
            rows = (
                _row(_el("val", term), what, "SAWS" if term in SAWS_TYPES else "the model")
                for term, what in seeds(compiled, element, attribute)
            )
            vocabularies.append(_table(f"{title}: {element}/@{attribute}", ("Term", "What it is", "From"), rows))
            continue
        oxford = bodleian_values(element, attribute)
        rows = (
            _row(
                _el("val", term),
                what,
                "the Bodleian's list" if term in oxford else "the old Solemne guide",
                _el("val", term) if term in oxford else "",
            )
            for term, what in seeds(compiled, element, attribute)
        )
        labels = ("Term", "What it is", "From", "Oxford")
        vocabularies.append(_table(f"{title}: {element}/@{attribute}", labels, rows))
    sections = (
        _section(
            "tables-categories",
            "The categories",
            "The categories a document's code begins with, as the formal title gives them.",
            _table("", ("Category", "What it is"), category_rows),
        ),
        _section(
            "tables-bible",
            "The books of the Bible",
            "The 73 books of the Bible, in the Vulgate's order, with the codes that pointers to a verse begin with "
            "(MAT_18_19).",
            _table("", ("Code", "Name", "Testament"), book_rows),
        ),
        _section(
            "tables-vocabularies",
            "The vocabularies' seeds",
            "The vocabularies that grow, each with the terms it starts with: the union of the Bodleian's lists and "
            "the old Solemne guide's, and, for relation types, the model's and SAWS's. A term outside the seeds is "
            "reported, not refused. The application's database holds each vocabulary, and the seeds are refreshed "
            "from its export at each release; their equivalents in Mirabile, Ligatus and the Getty AAT come with it. "
            "Oxford gives the Bodleian's term where the seed is one of them.",
            *vocabularies,
        ),
    )
    intro = (
        "The code tables encoders need beside the closed lists, and the seeds of the vocabularies that grow. "
        "Generated from the package's tables and the schema's lists; solemne-tei lists prints them too."
    )
    return _generated(divgen, intro, *sections)


def _section(ident: str, head: str, intro: str, *content: etree._Element) -> etree._Element:
    div = _el("div", xml_id=ident)
    div.append(_el("head", head))
    div.append(_el("p", intro))
    div.extend(content)
    return div


INLINE = re.compile(r"`([^`]+)`|\*\*(.+?)\*\*")


def _inline(parent: etree._Element, text: str) -> None:
    """Append Markdown's inline forms to an element: code spans as `code`, bold as `hi`."""
    position = 0
    for match in INLINE.finditer(text):
        _append_text(parent, text[position : match.start()])
        if match.group(1) is not None:
            parent.append(_el("code", match.group(1)))
        else:
            bold = _el("hi", rend="bold")
            _inline(bold, match.group(2))
            parent.append(bold)
        position = match.end()
    _append_text(parent, text[position:])


def _append_text(parent: etree._Element, text: str) -> None:
    if not text:
        return
    if len(parent):
        parent[-1].tail = (parent[-1].tail or "") + text
    else:
        parent.text = (parent.text or "") + text


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _blocks(lines: list[str], indent: int) -> list[etree._Element]:
    """Markdown's paragraphs and bulleted lists, nested by indentation, as TEI's `p` and `list`."""
    found: list[etree._Element] = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        if lines[i][indent:].startswith("- "):
            listed = found[-1] if found and etree.QName(found[-1]).localname == "list" else None
            if listed is None:
                listed = _el("list", rend="bulleted")
                found.append(listed)
            item_lines = [" " * (indent + 2) + lines[i][indent + 2 :]]
            i += 1
            while i < len(lines):
                if lines[i].strip() and _indent(lines[i]) < indent + 2:
                    break
                if not lines[i].strip():
                    rest = next((line for line in lines[i:] if line.strip()), "")
                    if not rest or _indent(rest) < indent + 2:
                        break
                item_lines.append(lines[i])
                i += 1
            item = _el("item")
            for n, block in enumerate(_blocks(item_lines, indent + 2)):
                if n == 0 and etree.QName(block).localname == "p":
                    item.text, children = block.text, list(block)
                    item.extend(children)
                else:
                    item.append(block)
            listed.append(item)
            continue
        words = []
        while i < len(lines) and lines[i].strip() and not lines[i][indent:].startswith("- "):
            words.append(lines[i].strip())
            i += 1
        p = _el("p")
        _inline(p, " ".join(words))
        found.append(p)
    return found


def changelog_divisions(text: str) -> list[etree._Element]:
    """The changelog's releases, each a division with its sections: its `## ` and `### ` headings, its paragraphs
    and its lists. What comes before the first release is the changelog's own preface, and is left out."""
    releases: list[etree._Element] = []
    current: etree._Element | None = None
    lines: list[str] = []

    def flush() -> None:
        if current is not None:
            current.extend(_blocks(lines, 0))
        lines.clear()

    for line in text.splitlines():
        if line.startswith("<!--"):
            continue
        if line.startswith("## "):
            flush()
            head = line[3:].strip()
            version = head.split()[0].lower()
            current = _el("div", xml_id=f"changes-{version}")
            current.append(_el("head", head))
            releases.append(current)
        elif line.startswith("### ") and releases:
            flush()
            current = _el("div")
            current.append(_el("head", line[4:].strip()))
            releases[-1].append(current)
        elif current is not None:
            lines.append(line)
    flush()
    return releases


def changes_appendix(divgen: etree._Element, changelog: Path = CHANGELOG) -> etree._Element:
    """Appendix F: the changes, release by release, from the changelog."""
    intro = (
        "What each release changed, and what may now fail in files that passed the release before it, as the "
        "changelog gives it. Generated from the changelog."
    )
    return _generated(divgen, intro, *changelog_divisions(changelog.read_text("utf-8")))


def label_counter_examples(odd: etree._Element) -> None:
    """Name the rule each counter-example breaks, before it, with a link to the rule in appendix B."""
    for eg in list(odd.iter(f"{{{EXAMPLES}}}egXML")):
        if eg.get("valid") != "false" or etree.QName(eg.getparent()).localname != "div":
            continue
        label = _el("p", "Breaks ")
        label.append(_el("ref", eg.get("n", ""), target=f"#rule-{eg.get('n', '')}"))
        label[-1].tail = ":"
        eg.addprevious(label)


def with_appendices(expanded: bytes, compiled: Path, changelog: Path = CHANGELOG) -> bytes:
    """The expanded ODD with its appendices generated and its counter-examples labelled."""
    odd = etree.fromstring(expanded)
    for divgen in list(odd.iter(_t("divGen"))):
        kind = divgen.get("type")
        if kind == "elements":
            generated = elements_appendix(odd, compiled, divgen)
        elif kind == "rules":
            generated = rules_appendix(odd, divgen)
        elif kind == "tables":
            generated = tables_appendix(odd, compiled, divgen)
        elif kind == "changes":
            generated = changes_appendix(divgen, changelog)
        else:
            continue
        divgen.getparent().replace(divgen, generated)
    label_counter_examples(odd)
    return etree.tostring(odd, xml_declaration=True, encoding="UTF-8")
