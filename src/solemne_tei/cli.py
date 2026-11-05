# SPDX-License-Identifier: MIT
"""The solemne-tei command line."""

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

import solemne_tei
from solemne_tei import logs
from solemne_tei.formats import FORMATS


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="solemne-tei", description=solemne_tei.__doc__)
    p.add_argument("--version", action="version", version=solemne_tei.__version__)
    commands = p.add_subparsers(dest="command", required=True, metavar="command")

    v = commands.add_parser(
        "validate",
        help="check TEI files against the schema",
        description="Check TEI files against the schema: the RelaxNG and the Schematron. The exit code is 1 when a "
        "file isn't well formed or fails the RelaxNG, and, with --strict, when the Schematron finds an error.",
    )
    v.add_argument("paths", nargs="+", type=Path, help="files, or folders of *.xml")
    v.add_argument("--jobs", type=int, default=os.cpu_count() or 1, help="worker processes (default: all cores)")
    v.add_argument("--json", action="store_true", help="print the results as JSON")
    v.add_argument("--strict", action="store_true", help="fail on Schematron errors too, as exports must")
    v.add_argument(
        "--format",
        choices=sorted(FORMATS),
        help="check against an import format's own schema instead of the project's: bodleian, the Bodleian's "
        "manuscript descriptions",
    )

    b = commands.add_parser(
        "build",
        help="regenerate the schema from the ODD, in a clone of the repository",
        description="Regenerate the schema from guide/solemne.odd into the package. The first run fetches the "
        "pinned sources; later runs are offline.",
    )
    b.add_argument("--cache", type=Path, help="where the fetched sources are kept (default: build/tei)")

    d = commands.add_parser(
        "docs",
        help="the guide as HTML, in a clone of the repository",
        description="Write the guide as one HTML page, its appendices generated from the specifications, by TEI's "
        "odd2html. The first run fetches the build's pinned sources; later runs are offline.",
    )
    d.add_argument("--html", action="store_true", help="write the HTML (the default, and for now the only output)")
    d.add_argument("--out", type=Path, help="where to write guide.html (default: build/html)")
    d.add_argument("--cache", type=Path, help="where the fetched sources are kept (default: build/tei)")

    li = commands.add_parser(
        "lists",
        help="the closed lists, the categories and the Bible's codes",
        description="The schema's closed lists (by element and attribute, or attribute class), the categories a "
        "document's code begins with, and the codes of the Bible's 73 books.",
    )
    li.add_argument("--json", action="store_true", help="print them as JSON")
    return p


def validate_command(args: argparse.Namespace) -> int:
    from solemne_tei.validate import summary, validate, xml_files

    results = validate(xml_files(args.paths), args.jobs, format=args.format)
    if args.json:
        payload = [{**asdict(r), "well_formed": r.well_formed, "passes_relaxng": r.passes_relaxng} for r in results]
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        for r in results:
            for p in r.problems:
                print(p)
        print(summary(results))
    failed = any(not r.passes_relaxng for r in results)
    if args.strict:
        failed = failed or any(r.schematron_errors for r in results)
    return 1 if failed else 0


def build_command(args: argparse.Namespace) -> int:
    from solemne_tei.build import CACHE_DIR, BuildError, build

    logs.setup(verbose=True)
    try:
        written = build(cache=args.cache or CACHE_DIR)
    except BuildError as e:
        print(f"solemne-tei build: {e}", file=sys.stderr)
        return 1
    for path in written:
        print(f"wrote {path.name}")
    if not written:
        print("nothing changed: the generated files are up to date")
    return 0


def docs_command(args: argparse.Namespace) -> int:
    from solemne_tei.build import CACHE_DIR, BuildError
    from solemne_tei.docs import HTML_DIR, html

    logs.setup(verbose=True)
    try:
        path = html(out=args.out or HTML_DIR, cache=args.cache or CACHE_DIR)
    except BuildError as e:
        print(f"solemne-tei docs: {e}", file=sys.stderr)
        return 1
    print(f"wrote {path}")
    return 0


def lists_command(args: argparse.Namespace) -> int:
    from solemne_tei.codes import CATEGORIES, bible_books
    from solemne_tei.schema_files import closed_lists, schema_version

    lists = closed_lists()
    books = bible_books()
    if args.json:
        payload = {
            "version": schema_version(),
            "closed_lists": lists,
            "categories": list(CATEGORIES),
            "bible": [asdict(book) for book in books],
        }
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0
    print(f"The closed lists of the schema {schema_version()}, by element (or attribute class) and attribute:")
    for key, attributes in lists.items():
        for attribute, values in attributes.items():
            print(f"  {key}/@{attribute}: {' '.join(values)}")
    print("\nThe categories a document's code begins with:")
    print(f"  {' '.join(CATEGORIES)}")
    print("\nThe Bible's books, as source pointers name them (MAT_18_19):")
    for book in books:
        print(f"  {book.code}  {book.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    commands = {"validate": validate_command, "build": build_command, "docs": docs_command, "lists": lists_command}
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
