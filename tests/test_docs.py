# SPDX-License-Identifier: MIT
"""The guide's HTML and PDF: a page per part and appendix, the parts numbered I to X, a title page with the version,
no page with the build's fixed date, nothing fetched from elsewhere; Junicode kept only at its pinned checksum; the
PDF built by LuaLaTeX (slow, skipped without it). The HTML and PDF tests need the build's cache."""

import hashlib
import re
import zipfile
from pathlib import Path

import pytest
from lxml import etree, html

from solemne_tei.build import CACHE_DIR, JUNICODE, ODD_PATH, BuildError, Source, expand
from solemne_tei.cli import main
from solemne_tei.docs import JUNICODE_OTF, JUNICODE_WOFF2, junicode, lualatex
from solemne_tei.rules import XML_ID
from solemne_tei.schema_files import TEI, odd_version

cached = pytest.mark.skipif(
    not (CACHE_DIR / "tei-xsl-7.61.0").exists(), reason="TEI's stylesheets aren't cached: run solemne-tei build first"
)
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def has_lualatex() -> bool:
    try:
        lualatex()
    except BuildError:
        return False
    return True


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("html")
    assert main(["docs", "--html", "--out", str(out)]) == 0
    return out


def divisions() -> dict[str, list[str]]:
    """The ids of the ODD's divisions, by front, body and back."""
    text = etree.fromstring(expand(ODD_PATH).text).find(f"{{{TEI}}}text")
    return {
        part: [d.get(XML_ID) for d in text.find(f"{{{TEI}}}{part}").iterfind(f"{{{TEI}}}div")]
        for part in ("front", "body", "back")
    }


@cached
def test_the_html_has_a_page_per_part_and_appendix(site: Path) -> None:
    found = divisions()
    pages = {p.stem for p in site.glob("*.html")}
    assert set(found["front"] + found["body"]) <= pages
    for ident in ("appendix-elements", "appendix-rules", "appendix-tables", "appendix-older-forms"):
        assert ident in pages
    assert {"appendix-mappings", "appendix-changes", "example-sources", "index"} <= pages
    # The reference is split, a page per specification, so that no page is large.
    assert "ref-persName" in pages
    assert max(p.stat().st_size for p in site.glob("*.html")) < 500_000


@cached
def test_the_parts_are_numbered_i_to_x(site: Path) -> None:
    index = (site / "index.html").read_text("utf-8")
    numbers = re.findall(r'<span class="headingNumber">([IVX]+) </span><a class="toc toc_0"', index)
    assert numbers == ROMAN
    assert re.search(
        r'<span class="headingNumber">V </span><span class="head">Records</span>',
        (site / "records.html").read_text("utf-8"),
    )


@cached
def test_no_page_holds_the_builds_fixed_date(site: Path) -> None:
    """The pages' words, not the ids the stylesheets number, which may hold any digits."""
    pages = {p.name: html.fromstring(p.read_text("utf-8")).text_content() for p in site.glob("*.html")}
    assert [name for name, words in pages.items() if "1970" in words] == []


@cached
def test_the_title_page_gives_the_title_authors_version_and_licence(site: Path) -> None:
    index = (site / "index.html").read_text("utf-8")
    title = " ".join(html.fromstring(index).find_class("titlePage")[0].text_content().split())
    for words in ("The SOLEMNE Encoding Guidelines", "Gleb Schmidt", "Friederike Voit", "Sven Meeder"):
        assert words in title
    assert f"Version {odd_version(ODD_PATH)}" in title
    assert "Creative Commons Attribution 4.0" in title


@cached
def test_the_pages_use_only_what_comes_with_them(site: Path) -> None:
    for page in site.glob("*.html"):
        text = page.read_text("utf-8")
        assert not re.search(r'<(link|script)[^>]+(href|src)="https?:', text), page.name
    assert (site / "guide.css").exists()
    assert {p.name for p in (site / "fonts").iterdir()} == {*JUNICODE_WOFF2, "OFL.txt"}


def test_the_title_page_carries_the_odds_version_and_its_release_date() -> None:
    front = etree.parse(str(ODD_PATH)).find(f".//{{{TEI}}}titlePage")
    version = odd_version(ODD_PATH)
    assert front.findtext(f"{{{TEI}}}docEdition") == f"Version {version}"
    changelog = (ODD_PATH.parents[1] / "CHANGELOG.md").read_text("utf-8")
    released = re.search(rf"^## {re.escape(version)} \((\d{{4}}-\d{{2}}-\d{{2}})\)", changelog, re.M)
    assert released, f"the changelog has no section for {version}"
    assert front.find(f"{{{TEI}}}docDate").get("when") == released.group(1)


def fake_junicode(tmp_path: Path, checksum: str | None = None) -> Source:
    archive = tmp_path / "Junicode_0.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for name in (*(f"OTF/Junicode-{s}.otf" for s in JUNICODE_OTF), *(f"WOFF2/{n}" for n in JUNICODE_WOFF2)):
            z.writestr(f"Junicode/{name}", b"font")
        z.writestr("Junicode/OFL.txt", b"licence")
        z.writestr("Junicode/TTF/Junicode-Light.ttf", b"not used")
    digest = checksum or hashlib.sha256(archive.read_bytes()).hexdigest()
    return Source("Junicode_0.zip", "0", archive.as_uri(), digest, "")


def test_junicode_is_unpacked_from_its_pinned_release(tmp_path: Path) -> None:
    folder = junicode(tmp_path / "cache", fake_junicode(tmp_path))
    assert {p.name for p in folder.iterdir()} == {
        *(f"Junicode-{s}.otf" for s in JUNICODE_OTF),
        *JUNICODE_WOFF2,
        "OFL.txt",
    }


def test_junicode_is_refused_without_its_checksum(tmp_path: Path) -> None:
    with pytest.raises(BuildError, match="SHA-256"):
        junicode(tmp_path / "cache", fake_junicode(tmp_path, "0" * 64))
    assert not (tmp_path / "cache" / "junicode-0").exists()


def test_junicodes_pin_names_its_release() -> None:
    assert JUNICODE.version in JUNICODE.url and JUNICODE.name in JUNICODE.url
    assert re.fullmatch(r"[0-9a-f]{64}", JUNICODE.sha256)


@pytest.mark.slow
@cached
@pytest.mark.skipif(not has_lualatex(), reason="LuaLaTeX isn't installed")
def test_the_pdf_builds(tmp_path: Path) -> None:
    assert main(["docs", "--pdf", "--out", str(tmp_path)]) == 0
    pdf = tmp_path / "solemne-guide.pdf"
    assert pdf.read_bytes().startswith(b"%PDF")
    log = (CACHE_DIR / "docs-pdf" / "guide.log").read_text("utf-8", errors="replace")
    pages = int(re.search(r"Output written on guide\.pdf \((\d+) pages", log).group(1))
    assert 50 < pages < 300
    assert "Missing character" not in log
