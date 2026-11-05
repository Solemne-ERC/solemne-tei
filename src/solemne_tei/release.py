# SPDX-License-Identifier: MIT
"""A release's files and its pages, for the release workflow; it runs in a clone of the repository.

- `notes`: the changelog's section for a version, the GitHub release's notes;
- `assemble`: the files a GitHub release carries (the schema's files, the guide's HTML as a zip, its PDF), and the
  version's pages (`schema/X.Y.Z/`, `guide/X.Y.Z/`);
- `site`: those pages merged into the published site, a checkout of its branch, keeping every earlier version.
  `schema/latest/` and `guide/latest/` follow the highest version. Earlier releases' schemas, taken from their tags,
  fill in versions the site lacks, so that the templates of every release find their schema.

    python -m solemne_tei.release assemble --out dist
    python -m solemne_tei.release site --pages dist/pages --into gh-pages --earlier earlier
"""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

from solemne_tei.build import REPOSITORY
from solemne_tei.docs import HTML_DIR, PDF, PDF_DIR
from solemne_tei.schema_files import GENERATED, SCHEMA_DIR, schema_version

CHANGELOG = REPOSITORY / "CHANGELOG.md"
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
# The site's first page leads to the latest guide.
REDIRECT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=guide/latest/">
<link rel="canonical" href="guide/latest/">
<title>Encoding Early Medieval Canon Law: The SOLEMNE Guidelines for TEI</title>
</head>
<body><p><a href="guide/latest/">The guide</a>; its schemas are in <a href="schema/">schema/</a>.</p></body>
</html>
"""


class ReleaseError(RuntimeError):
    pass


def notes(changelog: str, version: str) -> str:
    """The changelog's section for a version, without its heading."""
    found = re.search(rf"^## {re.escape(version)}\b[^\n]*\n(.*?)(?=^## |\Z)", changelog, re.M | re.S)
    if not found or not found.group(1).strip():
        raise ReleaseError(f"the changelog has no section for {version}")
    return found.group(1).strip() + "\n"


def _zip(folder: Path, archive: Path, prefix: str) -> None:
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                z.write(path, f"{prefix}/{path.relative_to(folder)}")


def assemble(
    out: Path, version: str, html: Path = HTML_DIR, pdf: Path = PDF_DIR / PDF, schema: Path = SCHEMA_DIR
) -> None:
    """The release's files into `out/files`, its notes into `out/notes.md`, and its pages into `out/pages`."""
    if not html.joinpath("index.html").exists() or not pdf.exists():
        raise ReleaseError("make the guide's HTML and PDF first: solemne-tei docs --html --pdf")
    shutil.rmtree(out, ignore_errors=True)
    files = out / "files"
    files.mkdir(parents=True)
    (out / "notes.md").write_text(notes(CHANGELOG.read_text("utf-8"), version), "utf-8")
    schema_pages = out / "pages" / "schema" / version
    schema_pages.mkdir(parents=True)
    for name in GENERATED:
        shutil.copy2(schema / name, schema_pages / name)
    _zip(schema_pages, files / f"solemne-tei-schema-{version}.zip", f"solemne-tei-schema-{version}")
    shutil.copytree(html, out / "pages" / "guide" / version)
    _zip(html, files / f"solemne-tei-guide-{version}-html.zip", f"solemne-tei-guide-{version}")
    shutil.copy2(pdf, files / f"solemne-tei-guide-{version}.pdf")


def _key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _replace(source: Path, target: Path) -> None:
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(source, target)


def site(pages: Path, into: Path, earlier: Path | None = None) -> list[str]:
    """Merge a version's pages into the site checked out at `into`, add the earlier releases' schemas it lacks (one
    folder per version in `earlier`), point `latest/` to the highest version, and return the versions it holds."""
    for kind in ("schema", "guide"):
        for folder in sorted((pages / kind).iterdir()):
            _replace(folder, into / kind / folder.name)
    if earlier and earlier.exists():
        for folder in sorted(earlier.iterdir()):
            target = into / "schema" / folder.name
            if VERSION.match(folder.name) and not target.exists():
                shutil.copytree(folder, target)
    for kind in ("schema", "guide"):
        versions = sorted((p.name for p in (into / kind).iterdir() if VERSION.match(p.name)), key=_key)
        if versions:
            _replace(into / kind / versions[-1], into / kind / "latest")
    (into / "index.html").write_text(REDIRECT, "utf-8")
    (into / ".nojekyll").write_text("", "utf-8")
    return sorted((p.name for p in (into / "schema").iterdir() if VERSION.match(p.name)), key=_key)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m solemne_tei.release", description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    a = commands.add_parser("assemble", help="the release's files, notes and pages, after solemne-tei docs")
    a.add_argument("--out", type=Path, required=True)
    s = commands.add_parser("site", help="a release's pages merged into the published site")
    s.add_argument("--pages", type=Path, required=True)
    s.add_argument("--into", type=Path, required=True)
    s.add_argument("--earlier", type=Path, help="earlier releases' schemas, a folder per version")
    args = parser.parse_args(argv)
    if args.command == "assemble":
        assemble(args.out, schema_version())
        print(f"assembled {schema_version()} in {args.out}")
    else:
        print("the site holds the schemas of " + ", ".join(site(args.pages, args.into, args.earlier)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
