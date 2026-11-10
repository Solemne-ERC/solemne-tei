# SPDX-License-Identifier: MIT
"""The guide's rules and tiers, read from the expanded ODD.

A rule is a Schematron assertion or report, named by its `id`, or a restriction the specifications put on TEI and
the RelaxNG checks (a closed list, a required attribute, a pattern, a content model, the elements the schema takes),
named by the `xml:id` of the specification that makes it. Every element, attribute and rule names its tier by
`@corresp`, pointing to a category of the header's taxonomy; an element taken from TEI unchanged takes its tier from
the table of elements beside the specification."""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from solemne_tei.schema_files import TEI

SCH = "http://purl.oclc.org/dsdl/schematron"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
TIER_TABLE = "element-tiers"
# The specifications whose xml:id names a restriction the RelaxNG checks.
RELAXNG_RULES = ("schemaSpec", "macroSpec", "dataSpec", "attDef", "valList", "datatype")


@dataclass(frozen=True)
class Rule:
    """A rule of the schema: its id, its check (`relaxng` or `schematron`), its severity (`error` or `warning`), its
    tier, the part of the guide that explains it (its `xml:id`), and what it requires. A RelaxNG rule names the
    elements it restricts, where it restricts some and not all."""

    id: str
    check: str
    severity: str
    tier: str
    part: str
    description: str
    elements: tuple[str, ...] = ()


def _t(name: str) -> str:
    return f"{{{TEI}}}{name}"


def _words(el: etree._Element | None) -> str:
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def tiers(odd: etree._Element) -> dict[str, str]:
    """The tiers, from the header's taxonomy: each category's pointer (`#tier-common`) and its name (`common`)."""
    taxonomy = odd.find(f".//{_t('taxonomy')}[@{XML_ID}='tiers']")
    if taxonomy is None:
        return {}
    return {f"#{c.get(XML_ID)}": _words(c.find(f"{_t('catDesc')}/{_t('term')}")) for c in taxonomy.iter(_t("category"))}


def _tier(el: etree._Element, names: dict[str, str]) -> str:
    return names.get(el.get("corresp", ""), "")


def part_of(el: etree._Element) -> str:
    """The `xml:id` of the part of the guide an element stands in: the division under the front, body or back."""
    for ancestor in el.iterancestors(_t("div")):
        parent = ancestor.getparent()
        if parent is not None and parent.tag in (_t("front"), _t("body"), _t("back")):
            return ancestor.get(XML_ID, "")
    return ""


def _owner(el: etree._Element) -> tuple[str, str]:
    """The element and the attribute a specification inside an attDef belongs to."""
    att = el if el.tag == _t("attDef") else next(el.iterancestors(_t("attDef")), None)
    spec = next(el.iterancestors(_t("elementSpec")), None)
    return (spec.get("ident", "") if spec is not None else "", att.get("ident", "") if att is not None else "")


def _relaxng_description(el: etree._Element) -> str:
    local = etree.QName(el).localname
    element, attribute = _owner(el)
    if local == "schemaSpec":
        return "Only the elements the schema takes from TEI's modules."
    if local in ("macroSpec", "dataSpec"):
        return _words(el.find(_t("desc")))
    if local == "valList":
        values = ", ".join(item.get("ident", "") for item in el.iter(_t("valItem")))
        return f"<{element}>'s @{attribute} is one of: {values}."
    if local == "datatype":
        return f"<{element}>'s @{attribute}: {_words(el.getparent().find(_t('desc'))) or 'its form'}."
    if el.get("mode") == "delete":
        return f"<{element}> has no @{attribute}."
    if el.get("usage") == "req":
        return f"<{element}> has @{attribute}."
    return _words(el.find(_t("desc")))


def _restricted(el: etree._Element, odd: etree._Element) -> tuple[str, ...]:
    """The elements a RelaxNG rule restricts: its element's, or those whose content or attributes use its macro or
    datatype; none for the schema as a whole."""
    local = etree.QName(el).localname
    if local in ("attDef", "valList", "datatype"):
        return (_owner(el)[0],)
    ref = {"macroSpec": "macroRef", "dataSpec": "dataRef"}.get(local)
    if ref is None:
        return ()
    # A datatype may be used through another that holds it (a note's pointer holds a source's).
    keys = {el.get("ident", "")}
    while True:
        holders = {
            spec.get("ident", "")
            for spec in odd.iter(_t(local))
            if any(r.get("key") in keys for r in spec.iter(_t(ref)))
        }
        if holders <= keys:
            break
        keys |= holders
    users = {
        spec.get("ident", "")
        for spec in odd.iter(_t("elementSpec"))
        if any(r.get("key") in keys for r in spec.iter(_t(ref)))
    }
    return tuple(sorted(users))


def rules(odd: etree._Element) -> list[Rule]:
    """Every rule of the expanded ODD, in the order the guide gives them."""
    names = tiers(odd)
    found = []
    for el in odd.iter(f"{{{SCH}}}assert", f"{{{SCH}}}report", *(_t(name) for name in RELAXNG_RULES)):
        if etree.QName(el).namespace == SCH:
            if el.get("id") is None:
                continue
            spec = next(el.iterancestors(_t("constraintSpec")), None)
            severity = "warning" if (el.get("role") or "error").lower() in ("warning", "warn", "info") else "error"
            tier = _tier(spec, names) if spec is not None else ""
            description = _words(spec.find(_t("desc"))) if spec is not None else ""
            found.append(Rule(el.get("id"), "schematron", severity, tier, part_of(el), description))
        elif el.get(XML_ID) is not None:
            rule = Rule(
                el.get(XML_ID),
                "relaxng",
                "error",
                _tier(el, names),
                part_of(el),
                _relaxng_description(el),
                _restricted(el, odd),
            )
            found.append(rule)
    return found


def element_tiers(odd: etree._Element) -> dict[str, list[str]]:
    """Each element's tiers: from its specification, and from the table of elements taken from TEI unchanged. An
    element has exactly one."""
    names = tiers(odd)
    found: dict[str, list[str]] = {}
    for spec in odd.iter(_t("elementSpec")):
        found.setdefault(spec.get("ident", ""), []).append(_tier(spec, names))
    table = odd.find(f".//{_t('table')}[@{XML_ID}='{TIER_TABLE}']")
    for row in table.iter(_t("row")) if table is not None else ():
        if row.get("corresp"):
            for gi in row.iter(_t("gi")):
                found.setdefault(_words(gi), []).append(_tier(row, names))
    return found


def attribute_tiers(odd: etree._Element) -> dict[str, list[str]]:
    """The tiers of each attribute the specifications define or change (`div/@type`); a deleted one has none."""
    names = tiers(odd)
    found: dict[str, list[str]] = {}
    for att in odd.iter(_t("attDef")):
        if att.get("mode") == "delete":
            continue
        element, attribute = _owner(att)
        found.setdefault(f"{element}/@{attribute}", []).append(_tier(att, names))
    return found
