# SPDX-License-Identifier: MIT
"""The schema's files: where the package keeps them, and the stamp that names the ODD they came from."""

import hashlib
import re
from importlib import resources
from pathlib import Path

SCHEMA_DIR = Path(str(resources.files("solemne_tei").joinpath("schema")))

ODD = "solemne.odd"
RELAXNG = "solemne.rng"
SCHEMATRON = "solemne.sch"
SCHEMATRON_XSLT = "solemne-schematron.xsl"
GENERATED = (RELAXNG, SCHEMATRON, SCHEMATRON_XSLT)

STAMP = re.compile(r"<!-- Generated from solemne\.odd \(SHA-256 ([0-9a-f]{64})\)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(odd_sha256: str) -> str:
    """The comment each generated file carries, naming the ODD it came from."""
    return (
        f"<!-- Generated from solemne.odd (SHA-256 {odd_sha256}) by solemne-tei build. Edit the ODD, not this file. -->"
    )


def stamped_sha256(path: Path) -> str | None:
    """The SHA-256 of the ODD a generated file records, or None."""
    with path.open(encoding="utf-8") as f:
        head = f.read(4000)
    m = STAMP.search(head)
    return m.group(1) if m else None
