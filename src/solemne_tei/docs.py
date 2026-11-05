# SPDX-License-Identifier: MIT
"""The guide as HTML and as a PDF.

The expanded ODD gets its generated appendices (`solemne_tei.appendices`) and is compiled by TEI's `odd2odd`, as the
build compiles it. Then, with SaxonC-HE and the guide's stylesheets in `guide/style/`:
- **HTML:** TEI's `odd2html` makes a folder of pages: the title page and contents (`index.html`), a page for the
  front matter, one per part and one per appendix, and one per specification of the reference; the guide's CSS and
  Junicode's web fonts, with their licence, go with them;
- **PDF:** TEI's `odd2lite` makes the guide TEI Lite, TEI's LaTeX stylesheet makes that LaTeX, and LuaLaTeX sets it in
  Junicode, without TEI's reference for each element, which the HTML holds.

Junicode is fetched at its pinned release into the build's cache. It runs in a clone of the repository, offline once
the cache holds the build's sources and Junicode.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

from solemne_tei.appendices import with_appendices
from solemne_tei.build import (
    CACHE_DIR,
    JUNICODE,
    ODD_PATH,
    REPOSITORY,
    BuildError,
    Saxon,
    Source,
    Tools,
    compile_odd,
    expand,
    fetch,
    stylesheet_params,
)
from solemne_tei.logs import logger

HTML_DIR = REPOSITORY / "build" / "html"
PDF_DIR = REPOSITORY / "build" / "pdf"
STYLE_DIR = REPOSITORY / "guide" / "style"
INDEX = "index.html"
PDF = "solemne-guide.pdf"
# Junicode's files the guide uses: its four styles for LuaLaTeX, its two web fonts for the HTML, and its licence.
JUNICODE_OTF = ("Regular", "Bold", "Italic", "BoldItalic")
JUNICODE_WOFF2 = ("JunicodeVF-Roman.woff2", "JunicodeVF-Italic.woff2")
LUALATEX_RUNS = 4


def compiled_guide(tools: Tools, saxon: Saxon, work: Path, odd: Path = ODD_PATH) -> Path:
    """The ODD with its appendices generated, compiled by TEI's `odd2odd` into `work`."""
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
    return compiled


def guide_stylesheet(tools: Tools, name: str, work: Path) -> Path:
    """One of the guide's stylesheets, importing TEI's from the cache: the guide's are copied into `work` together,
    since they include each other."""
    for source in STYLE_DIR.glob("*.xsl"):
        text = source.read_text("utf-8").replace("TEI-STYLESHEETS", tools.stylesheets.as_uri())
        (work / source.name).write_text(text, "utf-8")
    return work / name


def junicode(cache: Path = CACHE_DIR, source: Source = JUNICODE) -> Path:
    """The folder of Junicode's files the guide uses, unpacked once from its pinned release into the cache."""
    folder = cache / f"junicode-{source.version}"
    if not (folder / "OFL.txt").exists():
        archive = fetch(source, cache / "downloads")
        tmp = folder.with_name(folder.name + ".tmp")
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        wanted = {f"Junicode-{style}.otf" for style in JUNICODE_OTF} | set(JUNICODE_WOFF2) | {"OFL.txt"}
        with zipfile.ZipFile(archive) as z:
            for member in z.namelist():
                name = member.rsplit("/", 1)[-1]
                if name in wanted:
                    (tmp / name).write_bytes(z.read(member))
        missing = wanted - {p.name for p in tmp.iterdir()}
        if missing:
            raise BuildError(f"{source.name} lacks {', '.join(sorted(missing))}")
        shutil.rmtree(folder, ignore_errors=True)
        tmp.replace(folder)
    return folder


def html(out: Path = HTML_DIR, cache: Path = CACHE_DIR, odd: Path = ODD_PATH) -> Path:
    """Write the guide as HTML pages into `out`, emptied first, and return the path of its first page."""
    tools = Tools.prepare(cache)
    fonts = junicode(cache)
    saxon = Saxon()
    work = cache / "docs"
    compiled = compiled_guide(tools, saxon, work, odd)
    logger.info("Writing the HTML")
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    index = out / INDEX
    params = stylesheet_params(tools) | {"outputDir": str(out)}
    saxon.write(guide_stylesheet(tools, "html.xsl", work), compiled, index, **params)
    shutil.copy2(STYLE_DIR / "guide.css", out / "guide.css")
    (out / "fonts").mkdir()
    for name in (*JUNICODE_WOFF2, "OFL.txt"):
        shutil.copy2(fonts / name, out / "fonts" / name)
    return index


def lualatex() -> str:
    """LuaLaTeX's command: on the path, or where TeX Live puts it on a Mac."""
    found = shutil.which("lualatex") or shutil.which("lualatex", path="/Library/TeX/texbin")
    if not found:
        raise BuildError("LuaLaTeX isn't installed: the PDF needs TeX Live")
    return found


def pdf(out: Path = PDF_DIR, cache: Path = CACHE_DIR, odd: Path = ODD_PATH) -> Path:
    """Write the guide as a PDF into `out`, and return its path."""
    command = lualatex()
    tools = Tools.prepare(cache)
    fonts = junicode(cache)
    saxon = Saxon()
    work = cache / "docs-pdf"
    compiled = compiled_guide(tools, saxon, work, odd)
    logger.info("Writing the LaTeX")
    lite = work / "guide.lite.xml"
    params = stylesheet_params(tools)
    lite.write_text(saxon.run(tools.stylesheets / "odds" / "odd2lite.xsl", compiled, **params), "utf-8")
    latex = saxon.run(guide_stylesheet(tools, "latex.xsl", work), lite, **params, fontPath=str(fonts))
    tex = work / "guide.tex"
    tex.write_text(latex, "utf-8")
    env = dict(os.environ, TEXINPUTS=f"{STYLE_DIR}{os.sep}{os.sep}{os.pathsep}")
    for run in range(1, LUALATEX_RUNS + 1):
        logger.info("Typesetting with LuaLaTeX, pass %d", run)
        done = subprocess.run(
            [command, "-interaction=nonstopmode", "-halt-on-error", tex.name],
            cwd=work,
            env=env,
            capture_output=True,
            text=True,
        )
        log = (work / "guide.log").read_text("utf-8", errors="replace")
        if done.returncode != 0:
            errors = [line for line in log.splitlines() if line.startswith("!")]
            raise BuildError(f"LuaLaTeX failed on {tex}: {'; '.join(errors) or done.stdout[-500:]}")
        if "Rerun to get" not in log and "Label(s) may have changed" not in log:
            break
    out.mkdir(parents=True, exist_ok=True)
    path = out / PDF
    shutil.copy2(work / "guide.pdf", path)
    return path
