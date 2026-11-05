# SPDX-License-Identifier: MIT
"""The guide's HTML builds when the build's sources are cached."""

from pathlib import Path

import pytest

from solemne_tei.build import CACHE_DIR
from solemne_tei.cli import main

STYLESHEETS = CACHE_DIR / "tei-xsl-7.61.0"


@pytest.mark.skipif(not STYLESHEETS.exists(), reason="TEI's stylesheets aren't cached: run solemne-tei build first")
def test_the_html_builds(tmp_path: Path) -> None:
    assert main(["docs", "--html", "--out", str(tmp_path)]) == 0
    page = (tmp_path / "guide.html").read_text("utf-8")
    assert "The elements and attributes" in page
    assert 'id="rule-fragment-order"' in page
    assert 'id="marked-fragments"' in page
