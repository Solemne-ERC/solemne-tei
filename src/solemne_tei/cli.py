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

    b = commands.add_parser(
        "build",
        help="regenerate the schema from the ODD, in a clone of the repository",
        description="Regenerate the schema from guide/solemne.odd into the package. The first run fetches the "
        "pinned sources; later runs are offline.",
    )
    b.add_argument("--cache", type=Path, help="where the fetched sources are kept (default: build/tei)")
    return p


def validate_command(args: argparse.Namespace) -> int:
    from solemne_tei.validate import summary, validate, xml_files

    results = validate(xml_files(args.paths), args.jobs)
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


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "validate":
        return validate_command(args)
    return build_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
