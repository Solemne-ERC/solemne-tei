# SPDX-License-Identifier: MIT
"""A release's files and pages: the changelog's section as its notes; the schema, the HTML and the PDF gathered; the
site keeping every earlier version, filling in earlier releases' schemas, and pointing latest/ to the highest."""

import zipfile
from pathlib import Path

import pytest

from solemne_tei.release import CHANGELOG, ReleaseError, assemble, notes, site
from solemne_tei.schema_files import GENERATED, SCHEMA_DIR, schema_version

CHANGES = """# Changelog

Preface.

## Unreleased

- Coming.

## 1.0.0 (2027-01-01)

The first stable release.

### What changes

- **One:** a change.

## 0.3.0 (2026-11-05)

Older.
"""


def test_the_notes_are_the_versions_section() -> None:
    text = notes(CHANGES, "1.0.0")
    assert text.startswith("The first stable release.")
    assert "### What changes" in text and "Older." not in text and "1.0.0" not in text.splitlines()[0]
    assert notes(CHANGES, "0.3.0") == "Older.\n"


def test_a_version_without_a_section_has_no_notes() -> None:
    with pytest.raises(ReleaseError, match="no section for 2.0.0"):
        notes(CHANGES, "2.0.0")


def test_every_release_in_the_changelog_has_notes() -> None:
    import re

    for version in re.findall(r"^## (\d+\.\d+\.\d+) ", CHANGELOG.read_text("utf-8"), re.M):
        assert notes(CHANGELOG.read_text("utf-8"), version)


def made_guide(tmp_path: Path) -> tuple[Path, Path]:
    html = tmp_path / "html"
    (html / "fonts").mkdir(parents=True)
    (html / "index.html").write_text("<html/>", "utf-8")
    (html / "fonts" / "OFL.txt").write_text("licence", "utf-8")
    pdf = tmp_path / "guide.pdf"
    pdf.write_bytes(b"%PDF-1.7")
    return html, pdf


def test_assemble_gathers_the_schema_the_html_and_the_pdf(tmp_path: Path) -> None:
    html, pdf = made_guide(tmp_path)
    version = schema_version()
    out = tmp_path / "dist"
    assemble(out, version, html=html, pdf=pdf)
    files = sorted(p.name for p in (out / "files").iterdir())
    assert files == [
        f"solemne-tei-guide-{version}-html.zip",
        f"solemne-tei-guide-{version}.pdf",
        f"solemne-tei-schema-{version}.zip",
    ]
    with zipfile.ZipFile(out / "files" / f"solemne-tei-schema-{version}.zip") as z:
        assert sorted(n.split("/", 1)[1] for n in z.namelist()) == sorted(GENERATED)
    assert sorted(p.name for p in (out / "pages" / "schema" / version).iterdir()) == sorted(GENERATED)
    assert (out / "pages" / "guide" / version / "fonts" / "OFL.txt").exists()
    assert (out / "notes.md").read_text("utf-8").strip()
    assert (SCHEMA_DIR / "solemne.rng").read_bytes() == (
        out / "pages" / "schema" / version / "solemne.rng"
    ).read_bytes()


def test_assemble_needs_the_guide_made_first(tmp_path: Path) -> None:
    with pytest.raises(ReleaseError, match="solemne-tei docs"):
        assemble(tmp_path / "dist", "1.0.0", html=tmp_path / "none", pdf=tmp_path / "none.pdf")


def pages(tmp_path: Path, version: str) -> Path:
    folder = tmp_path / f"pages-{version}"
    for kind in ("schema", "guide"):
        (folder / kind / version).mkdir(parents=True)
        (folder / kind / version / "file.txt").write_text(version, "utf-8")
    return folder


def test_the_site_keeps_earlier_versions_and_points_latest_to_the_highest(tmp_path: Path) -> None:
    into = tmp_path / "gh-pages"
    earlier = tmp_path / "earlier"
    for version in ("0.1.0", "0.2.0", "1.0.0"):
        (earlier / version).mkdir(parents=True)
        (earlier / version / "file.txt").write_text(f"tag {version}", "utf-8")
    assert site(pages(tmp_path, "1.0.0"), into, earlier) == ["0.1.0", "0.2.0", "1.0.0"]
    # The release's own pages win over its tag's copy; earlier ones are filled in from their tags.
    assert (into / "schema" / "1.0.0" / "file.txt").read_text("utf-8") == "1.0.0"
    assert (into / "schema" / "0.1.0" / "file.txt").read_text("utf-8") == "tag 0.1.0"
    assert (into / "schema" / "latest" / "file.txt").read_text("utf-8") == "1.0.0"
    assert (into / "guide" / "latest" / "file.txt").read_text("utf-8") == "1.0.0"
    # A later release adds itself and moves latest; a patch of an older line doesn't.
    site(pages(tmp_path, "1.1.0"), into)
    site(pages(tmp_path, "1.0.1"), into)
    assert (into / "guide" / "latest" / "file.txt").read_text("utf-8") == "1.1.0"
    assert sorted(p.name for p in (into / "guide").iterdir()) == ["1.0.0", "1.0.1", "1.1.0", "latest"]
    assert "guide/latest/" in (into / "index.html").read_text("utf-8")
    assert (into / ".nojekyll").exists()
