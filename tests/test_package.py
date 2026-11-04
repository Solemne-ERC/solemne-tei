# SPDX-License-Identifier: MIT
"""The package as others use it: its Python interface, and its data found the way an installed copy finds it."""

import shutil
import subprocess
import sys
import tomllib
from fnmatch import fnmatch
from pathlib import Path

import solemne_tei
from solemne_tei import SCHEMA_VERSION, Problem, Result, Validator, closed_lists, validate

PACKAGE = Path(solemne_tei.__file__).parent
REPOSITORY = Path(__file__).parents[1]
SAMPLE = Path(__file__).parent / "samples" / "valid" / "council-edition.xml"


def test_the_interface_checks_files() -> None:
    results = validate([SAMPLE], jobs=1)
    assert isinstance(results[0], Result)
    assert results[0].problems == []
    assert Validator().check(SAMPLE).passes_relaxng
    assert Problem("f.xml", 3, "relaxng", "error", "relaxng", "m").line == 3


def test_the_interface_gives_the_version_and_the_lists() -> None:
    assert solemne_tei.__version__ == SCHEMA_VERSION
    assert "type" in closed_lists()["div"]


def test_the_package_data_covers_every_data_file() -> None:
    with (REPOSITORY / "pyproject.toml").open("rb") as f:
        globs = tomllib.load(f)["tool"]["setuptools"]["package-data"]["solemne_tei"]
    data = [
        path.relative_to(PACKAGE).as_posix()
        for path in PACKAGE.rglob("*")
        if path.is_file() and path.suffix not in (".py", ".pyc")
    ]
    assert data
    assert [name for name in data if not any(fnmatch(name, glob) for glob in globs)] == []


def test_an_installed_copy_validates_outside_the_repository(tmp_path: Path) -> None:
    sample = tmp_path / SAMPLE.name
    shutil.copy(SAMPLE, sample)
    script = "import sys, solemne_tei; r = solemne_tei.validate([sys.argv[1]], jobs=1)[0]; print(r.problems == [])"
    run = subprocess.run(
        [sys.executable, "-I", "-c", script, str(sample)], cwd=tmp_path, capture_output=True, text=True, check=True
    )
    assert run.stdout.strip() == "True"
