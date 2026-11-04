# SPDX-License-Identifier: MIT
"""The solemne-tei command line."""

import argparse

import solemne_tei


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="solemne-tei", description=solemne_tei.__doc__)
    p.add_argument("--version", action="version", version=solemne_tei.__version__)
    return p


def main(argv: list[str] | None = None) -> int:
    parser().parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
