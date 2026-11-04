# SPDX-License-Identifier: MIT
"""The schema's files: where the package keeps them, and the stamp that names the ODD and the version they came
from."""

import hashlib
import json
import re
from importlib import resources
from pathlib import Path

from lxml import etree

SCHEMA_DIR = Path(str(resources.files("solemne_tei").joinpath("schema")))

ODD = "solemne.odd"
RELAXNG = "solemne.rng"
SCHEMATRON = "solemne.sch"
SCHEMATRON_XSLT = "solemne-schematron.xsl"
COMPILED_ODD = "solemne.compiled.odd"
CLOSED_LISTS = "closed-lists.json"
GENERATED = (RELAXNG, SCHEMATRON, SCHEMATRON_XSLT, COMPILED_ODD, CLOSED_LISTS)

TEI = "http://www.tei-c.org/ns/1.0"
STAMP = re.compile(r"Generated from solemne\.odd (\S+) \(SHA-256 ([0-9a-f]{64})\)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def odd_version(odd: Path) -> str:
    """The ODD's version: its header's `editionStmt/edition/@n`."""
    edition = etree.parse(str(odd)).find(f"{{{TEI}}}teiHeader/{{{TEI}}}fileDesc/{{{TEI}}}editionStmt/{{{TEI}}}edition")
    version = edition.get("n") if edition is not None else None
    if not version:
        raise ValueError(f"{odd} gives no version in editionStmt/edition/@n")
    return version


def stamp_text(version: str, odd_sha256: str) -> str:
    """What each generated file says about where it came from."""
    return (
        f"Generated from solemne.odd {version} (SHA-256 {odd_sha256}) by solemne-tei build."
        " Edit the ODD, not this file."
    )


def stamp(version: str, odd_sha256: str) -> str:
    """The stamp as the comment an XML file carries."""
    return f"<!-- {stamp_text(version, odd_sha256)} -->"


def read_stamp(path: Path) -> tuple[str, str] | None:
    """The version and the SHA-256 of the ODD a generated file records, or None."""
    with path.open(encoding="utf-8") as f:
        head = f.read(4000)
    m = STAMP.search(head)
    return (m.group(1), m.group(2)) if m else None


def schema_version() -> str:
    """The version of the ODD the package's schema was generated from."""
    stamped = read_stamp(SCHEMA_DIR / RELAXNG)
    if stamped is None:
        raise ValueError(f"{SCHEMA_DIR / RELAXNG} has no stamp")
    return stamped[0]


ClosedLists = dict[str, dict[str, list[str]]]


def closed_lists_of(compiled_odd: Path) -> ClosedLists:
    """Every closed list of a compiled ODD: by element and attribute, and by class and attribute for the lists an
    attribute class defines (`att.global`), all sorted."""
    lists: ClosedLists = {}
    tree = etree.parse(str(compiled_odd))
    for spec in tree.iter(f"{{{TEI}}}elementSpec", f"{{{TEI}}}classSpec"):
        for att in spec.iter(f"{{{TEI}}}attDef"):
            for val_list in att.iterfind(f"{{{TEI}}}valList[@type='closed']"):
                values = sorted(item.get("ident") for item in val_list.iterfind(f"{{{TEI}}}valItem"))
                lists.setdefault(spec.get("ident"), {})[att.get("ident")] = values
    return {key: dict(sorted(atts.items())) for key, atts in sorted(lists.items())}


def closed_lists() -> ClosedLists:
    """The schema's closed lists, as the package holds them: `{"div": {"type": ["capitulum", …]}, …}`."""
    with (SCHEMA_DIR / CLOSED_LISTS).open(encoding="utf-8") as f:
        return json.load(f)["lists"]
