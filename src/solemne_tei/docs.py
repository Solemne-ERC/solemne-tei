# SPDX-License-Identifier: MIT
"""The guide as HTML.

The expanded ODD gets its generated appendices (`solemne_tei.appendices`), is compiled by TEI's `odd2odd` as the
build does, and is made into HTML by TEI's `odd2html`, run by SaxonC-HE. It runs in a clone of the repository,
offline once the build's sources are cached.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from solemne_tei.appendices import with_appendices
from solemne_tei.build import CACHE_DIR, ODD_PATH, REPOSITORY, Saxon, Tools, compile_odd, expand, stylesheet_params
from solemne_tei.logs import logger

HTML_DIR = REPOSITORY / "build" / "html"
GUIDE_HTML = "guide.html"


def html(out: Path = HTML_DIR, cache: Path = CACHE_DIR, odd: Path = ODD_PATH) -> Path:
    """Write the guide as one HTML page into `out`, and return its path."""
    tools = Tools.prepare(cache)
    saxon = Saxon()
    work = cache / "docs"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    expanded = expand(odd)
    source = work / "guide.odd"
    source.write_bytes(expanded.text)
    compiled = work / "guide.compiled.odd"
    compile_odd(saxon, tools, source, compiled)
    logger.info("Generating the appendices")
    source.write_bytes(with_appendices(expanded.text, compiled))
    compile_odd(saxon, tools, source, compiled)
    logger.info("Writing the HTML")
    page = saxon.run(tools.stylesheets / "odds" / "odd2html.xsl", compiled, **stylesheet_params(tools))
    out.mkdir(parents=True, exist_ok=True)
    path = out / GUIDE_HTML
    path.write_text(page, "utf-8")
    return path
