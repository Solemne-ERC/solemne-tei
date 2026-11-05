# SPDX-License-Identifier: MIT
"""Import formats: other projects' TEI, which the application converts into the project's encoding. A file in such a
format is checked against that format's own schema before it's converted. The build compiles each format's schema
from its source, pinned by commit and SHA-256, and the package keeps it here, with the notices of its material."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

FORMATS_DIR = Path(str(resources.files("solemne_tei").joinpath("formats")))


@dataclass(frozen=True)
class Format:
    """An import format: its name, what it is, and its schema's two files in the package, the RelaxNG and the
    Schematron compiled to XSLT."""

    name: str
    title: str

    @property
    def folder(self) -> Path:
        return FORMATS_DIR / self.name

    @property
    def relaxng(self) -> Path:
        return self.folder / f"{self.name}.rng"

    @property
    def schematron_xslt(self) -> Path:
        return self.folder / f"{self.name}-schematron.xsl"


BODLEIAN = Format("bodleian", "the Bodleian Libraries' consolidated TEI schema for manuscript descriptions")
FORMATS = {f.name: f for f in (BODLEIAN,)}


def import_format(name: str) -> Format:
    """The import format of that name."""
    try:
        return FORMATS[name]
    except KeyError:
        raise ValueError(f"no import format {name!r}: the formats are {', '.join(FORMATS)}") from None
