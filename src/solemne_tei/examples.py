# SPDX-License-Identifier: MIT
"""The guide's examples, checked against the schema.

An example without `@valid` passes both checks: the RelaxNG, and the Schematron without an error (warnings don't
fail it). One with `@valid="false"` names in `@n` the rule it breaks, and fails on it: a Schematron rule among the
problems, with the RelaxNG passed; a RelaxNG rule at one of the elements it restricts.

Most examples are fragments. Each is placed in a minimal valid file by its root elements: a part of the header where
it stands in the header, a part of a manuscript's description in a minimal description's unit, a record in the
standOff, divisions, headings and paragraphs in the body, anything else in a paragraph. A fragment that dates by EDTF
without declaring it gets the declaration a file needs (`calendar xml:id="edtf"`), so that each date's example shows
only the date. An example that is a whole TEI file is checked as it is. An example saved under a file name of its
own, for the rule on file names, says so in a comment before its root: `<!-- file name: C.NIC-0325.xml -->`."""

from __future__ import annotations

import copy
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from solemne_tei.rules import Rule, part_of
from solemne_tei.schema_files import TEI
from solemne_tei.validate import Problem, Validator

EXAMPLES = "http://www.tei-c.org/ns/Examples"
FILE_NAME = re.compile(r"file name:\s*(\S+\.xml)")
DEFAULT_FILE_NAME = "example.xml"

# The minimal valid file a fragment is placed in.
HOST = f"""<TEI xmlns="{TEI}">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title type="formal">
          <idno>C.EXA-0600</idno>
          <idno type="category">C</idno>
          <idno type="type">edition</idno>
        </title>
      </titleStmt>
      <publicationStmt>
        <p>An example of the guide.</p>
      </publicationStmt>
      <sourceDesc>
        <p>An excerpt.</p>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body/>
  </text>
</TEI>"""

# The minimal description a part of a manuscript's description is placed in: the manuscript and its one unit.
DESCRIPTION = f"""<msDesc xmlns="{TEI}">
  <msIdentifier>
    <settlement>Nowhere</settlement>
    <repository>The Library</repository>
    <idno type="shelfmark">MS 1</idno>
  </msIdentifier>
  <msPart>
    <msIdentifier>
      <idno>A</idno>
    </msIdentifier>
  </msPart>
</msDesc>"""
DESCRIPTION_PATH = "teiHeader/fileDesc/sourceDesc/msDesc"
UNIT = f"{DESCRIPTION_PATH}/msPart"

# The declaration of EDTF, which a fragment's dates point to by `@datingMethod="#edtf"`.
EDTF = f"""<calendar xmlns="{TEI}" xml:id="edtf" target="https://www.loc.gov/standards/datetime/">
  <p>The Extended Date/Time Format (EDTF), ISO 8601-2.</p>
</calendar>"""

# Where a fragment's root goes: the path of its parent in the host, made where it's missing, from the root's
# children down. Each step names an element and the elements that come before it, so that it's made in TEI's order.
PARENT = {
    "teiHeader": "",
    "text": "",
    "standOff": "",
    "fileDesc": "teiHeader",
    "encodingDesc": "teiHeader",
    "profileDesc": "teiHeader",
    "revisionDesc": "teiHeader",
    "titleStmt": "teiHeader/fileDesc",
    "editionStmt": "teiHeader/fileDesc",
    "extent": "teiHeader/fileDesc",
    "publicationStmt": "teiHeader/fileDesc",
    "seriesStmt": "teiHeader/fileDesc",
    "notesStmt": "teiHeader/fileDesc",
    "sourceDesc": "teiHeader/fileDesc",
    "author": "teiHeader/fileDesc/titleStmt",
    "editor": "teiHeader/fileDesc/titleStmt",
    "respStmt": "teiHeader/fileDesc/titleStmt",
    "funder": "teiHeader/fileDesc/titleStmt",
    "sponsor": "teiHeader/fileDesc/titleStmt",
    "principal": "teiHeader/fileDesc/titleStmt",
    "publisher": "teiHeader/fileDesc/publicationStmt",
    "distributor": "teiHeader/fileDesc/publicationStmt",
    "availability": "teiHeader/fileDesc/publicationStmt",
    "msDesc": "teiHeader/fileDesc/sourceDesc",
    "biblStruct": "teiHeader/fileDesc/sourceDesc",
    "listWit": "teiHeader/fileDesc/sourceDesc",
    "projectDesc": "teiHeader/encodingDesc",
    "samplingDecl": "teiHeader/encodingDesc",
    "editorialDecl": "teiHeader/encodingDesc",
    "refsDecl": "teiHeader/encodingDesc",
    "classDecl": "teiHeader/encodingDesc",
    "listPrefixDef": "teiHeader/encodingDesc",
    "correction": "teiHeader/encodingDesc/editorialDecl",
    "normalization": "teiHeader/encodingDesc/editorialDecl",
    "segmentation": "teiHeader/encodingDesc/editorialDecl",
    "punctuation": "teiHeader/encodingDesc/editorialDecl",
    "quotation": "teiHeader/encodingDesc/editorialDecl",
    "interpretation": "teiHeader/encodingDesc/editorialDecl",
    "stdVals": "teiHeader/encodingDesc/editorialDecl",
    "prefixDef": "teiHeader/encodingDesc/listPrefixDef",
    "taxonomy": "teiHeader/encodingDesc/classDecl",
    "abstract": "teiHeader/profileDesc",
    "calendarDesc": "teiHeader/profileDesc",
    "calendar": "teiHeader/profileDesc/calendarDesc",
    "creation": "teiHeader/profileDesc",
    "langUsage": "teiHeader/profileDesc",
    "textClass": "teiHeader/profileDesc",
    "change": "teiHeader/revisionDesc",
    "listPerson": "standOff",
    "listPlace": "standOff",
    "listOrg": "standOff",
    "listEvent": "standOff",
    "listRelation": "standOff",
    "listAnnotation": "standOff",
    "listBibl": "standOff",
    "person": "standOff/listPerson",
    "place": "standOff/listPlace",
    "org": "standOff/listOrg",
    "event": "standOff/listEvent",
    "relation": "standOff/listRelation",
    "annotation": "standOff/listAnnotation",
    "div": "text/body",
    "head": "text/body",
    "p": "text/body",
    "history": UNIT,
    "origin": f"{UNIT}/history",
    "origDate": f"{UNIT}/history/origin",
    "origPlace": f"{UNIT}/history/origin",
}
# TEI's order of the children that the host makes, so that a part made later stands where TEI puts it.
ORDER = {
    "TEI": ("teiHeader", "text", "standOff"),
    "teiHeader": ("fileDesc", "encodingDesc", "profileDesc", "revisionDesc"),
    "fileDesc": (
        "titleStmt",
        "editionStmt",
        "extent",
        "publicationStmt",
        "seriesStmt",
        "notesStmt",
        "sourceDesc",
    ),
    "encodingDesc": ("projectDesc", "samplingDecl", "editorialDecl", "refsDecl", "classDecl", "listPrefixDef"),
    "titleStmt": ("title", "author", "editor", "respStmt", "funder", "sponsor", "principal"),
    "msPart": ("msIdentifier", "msContents", "physDesc", "history", "additional"),
}
# Fragments that replace the host's own element rather than join it.
REPLACES = {"teiHeader", "text", "fileDesc", "titleStmt", "publicationStmt", "sourceDesc", "body"}


@dataclass(frozen=True)
class Example:
    """An example of the guide: the `egXML`, whether it should pass, the rule it breaks if not, the part it stands in,
    and the file name it's checked under."""

    element: etree._Element
    valid: bool
    rule: str
    part: str
    line: int
    file_name: str


@dataclass(frozen=True)
class Outcome:
    """How an example fared: whether it passed or failed as it says, and why not."""

    example: Example
    ok: bool
    why: str
    problems: tuple[Problem, ...]


def examples(odd: etree._Element) -> list[Example]:
    """Every example of the expanded ODD, in the guide's order."""
    found = []
    for eg in odd.iter(f"{{{EXAMPLES}}}egXML"):
        comments = [c.text or "" for c in eg if isinstance(c, etree._Comment)]
        named = next((m.group(1) for c in comments if (m := FILE_NAME.search(c))), DEFAULT_FILE_NAME)
        valid = eg.get("valid", "true") != "false"
        found.append(Example(eg, valid, eg.get("n", ""), part_of(eg), eg.sourceline or 0, named))
    return found


def _in_tei(el: etree._Element) -> etree._Element:
    """A copy of an example's element in TEI's namespace."""
    el = copy.deepcopy(el)
    for node in el.iter(tag=etree.Element):
        q = etree.QName(node)
        if q.namespace == EXAMPLES:
            node.tag = f"{{{TEI}}}{q.localname}"
    etree.cleanup_namespaces(el, top_nsmap={None: TEI})
    return el


def _child(parent: etree._Element, local: str) -> etree._Element:
    """The parent's child of that name, made in TEI's order if it's missing."""
    found = parent.find(f"{{{TEI}}}{local}")
    if found is not None:
        return found
    made = etree.Element(f"{{{TEI}}}{local}")
    order = ORDER.get(etree.QName(parent).localname, ())
    after = order[order.index(local) + 1 :] if local in order else ()
    following = next((c for c in parent if isinstance(c.tag, str) and etree.QName(c).localname in after), None)
    if following is not None:
        following.addprevious(made)
    else:
        parent.append(made)
    return made


def _place(host: etree._Element, el: etree._Element) -> None:
    local = etree.QName(el).localname
    if local == "title" and el.get("type") == "formal":
        formal = host.find(f".//{{{TEI}}}titleStmt/{{{TEI}}}title[@type='formal']")
        formal.addnext(el)
        formal.getparent().remove(formal)
        return
    path = PARENT.get(local, "text/body/p")
    if local == "title":
        path = "teiHeader/fileDesc/titleStmt"
    if path.startswith(DESCRIPTION_PATH):
        _describe(host)
    parent = host
    for step in filter(None, path.split("/")):
        parent = _child(parent, step)
    if local in REPLACES:
        old = parent.find(f"{{{TEI}}}{local}")
        if old is not None:
            old.addnext(el)
            parent.remove(old)
            return
    # The host's own paragraph stands in for what a publication statement or a source description holds.
    if etree.QName(parent).localname in ("publicationStmt", "sourceDesc") and local != "p":
        for placeholder in parent.findall(f"{{{TEI}}}p"):
            parent.remove(placeholder)
    if local in ORDER.get(etree.QName(parent).localname, ()):
        order = ORDER[etree.QName(parent).localname]
        after = order[order.index(local) + 1 :]
        following = next((c for c in parent if isinstance(c.tag, str) and etree.QName(c).localname in after), None)
        if following is not None:
            following.addprevious(el)
            return
    parent.append(el)


def _describe(host: etree._Element) -> None:
    """Put the minimal description in the host's source description, in place of its paragraph, unless one is
    there."""
    source = host.find(f"{{{TEI}}}teiHeader/{{{TEI}}}fileDesc/{{{TEI}}}sourceDesc")
    if source.find(f"{{{TEI}}}msDesc") is not None:
        return
    for placeholder in source.findall(f"{{{TEI}}}p"):
        source.remove(placeholder)
    source.append(etree.fromstring(DESCRIPTION))


def _declare_edtf(host: etree._Element) -> None:
    """Declare EDTF where the file's dates point to it and nothing declares it."""
    pointers = {p for el in host.iter(tag=etree.Element) for p in (el.get("datingMethod") or "").split()}
    if "#edtf" not in pointers or host.xpath("//*[@xml:id = 'edtf']"):
        return
    header = _child(host, "teiHeader")
    _child(_child(header, "profileDesc"), "calendarDesc").append(etree.fromstring(EDTF))


def placed(example: Example) -> etree._ElementTree:
    """The file an example is checked as: itself if it's a whole TEI file, else the minimal file holding it."""
    roots = [_in_tei(el) for el in example.element if isinstance(el.tag, str)]
    if len(roots) == 1 and etree.QName(roots[0]).localname == "TEI":
        return etree.ElementTree(roots[0])
    host = etree.fromstring(HOST)
    for el in roots:
        _place(host, el)
    _declare_edtf(host)
    return etree.ElementTree(host)


def _elements_at(path: Path) -> dict[int, set[str]]:
    lines: dict[int, set[str]] = {}
    for el in etree.parse(str(path)).iter(tag=etree.Element):
        lines.setdefault(el.sourceline, set()).add(etree.QName(el).localname)
    return lines


def judge(example: Example, problems: list[Problem], path: Path, rules: dict[str, Rule]) -> tuple[bool, str]:
    """Whether an example passed or failed as it says, and why not."""
    relaxng = [p for p in problems if p.check in ("relaxng", "well-formed")]
    errors = [p for p in problems if p.check == "schematron" and p.severity == "error"]
    if example.valid:
        if relaxng or errors:
            return False, "it should pass, and fails"
        return True, ""
    rule = rules.get(example.rule)
    if rule is None:
        return False, f"it names no rule of the schema in @n ({example.rule!r})"
    if rule.check == "schematron":
        if relaxng:
            return False, "it should fail only the Schematron, and fails the RelaxNG"
        if not any(p.check == "schematron" and p.rule == rule.id for p in problems):
            return False, f"it doesn't fail on {rule.id}"
        return True, ""
    if not relaxng:
        return False, f"it should fail the RelaxNG on {rule.id}, and passes it"
    if rule.elements:
        at = _elements_at(path)
        if not any(at.get(p.line or 0, set()) & set(rule.elements) for p in relaxng):
            return False, f"it fails the RelaxNG, but not at {', '.join(rule.elements)}, as {rule.id} would"
    return True, ""


def check(found: list[Example], rules: list[Rule], validator: Validator | None = None) -> list[Outcome]:
    """Check every example, each in a file of its own."""
    validator = validator or Validator()
    by_id = {r.id: r for r in rules}
    outcomes = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, example in enumerate(found):
            folder = Path(tmp) / str(i)
            folder.mkdir()
            path = folder / example.file_name
            placed(example).write(str(path), xml_declaration=True, encoding="UTF-8", pretty_print=True)
            problems = validator.check(path).problems
            ok, why = judge(example, problems, path, by_id)
            outcomes.append(Outcome(example, ok, why, tuple(problems)))
    return outcomes
