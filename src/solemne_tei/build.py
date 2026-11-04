# SPDX-License-Identifier: MIT
"""Generate the schema from the ODD.

Fetches TEI P5's `p5subset.xml`, TEI's stylesheets, the Bodleian's consolidated msDesc ODD and SchXslt2 at pinned
versions, checked by SHA-256, into the cache. Then, with SaxonC-HE: compiles the Bodleian's ODD and ours with TEI's
`odd2odd` (ours takes its `msdescription` module from the Bodleian's), writes the RelaxNG with `odd2relax`, extracts
the Schematron with `extract-isosch`, and compiles it to XSLT with SchXslt2. Each generated file names the ODD it came
from by its SHA-256, and the compiled Schematron carries SchXslt2's licence.

The build runs in a clone of the repository: it reads `guide/solemne.odd` and writes into the package's `schema/`.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

from solemne_tei.logs import logger
from solemne_tei.schema_files import GENERATED, ODD, RELAXNG, SCHEMA_DIR, SCHEMATRON, SCHEMATRON_XSLT, sha256, stamp

REPOSITORY = Path(__file__).resolve().parents[2]
ODD_PATH = REPOSITORY / "guide" / ODD
CACHE_DIR = REPOSITORY / "build" / "tei"

# The name the ODD gives the Bodleian's compiled ODD, in `moduleRef/@source`; the build puts it next to our ODD.
MSDESC_COMPILED = "msdesc.compiled.odd"

SPDX = "<!-- SPDX-License-Identifier: MIT -->"


@dataclass(frozen=True)
class Source:
    """A file fetched for the build, at a pinned version."""

    name: str
    version: str
    url: str
    sha256: str
    licence: str


P5SUBSET = Source(
    "p5subset.xml",
    "4.12.0",
    "https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/odd/p5subset.xml",
    "5b89720edc6f3821ab3d0aa242aa5dc922bfbafabfb103d2de9d211001c33e26",
    "TEI P5: BSD 2-Clause, or CC BY 3.0",
)
STYLESHEETS = Source(
    "tei-xsl-7.61.0.zip",
    "7.61.0",
    "https://github.com/TEIC/Stylesheets/releases/download/v7.61.0/tei-xsl-7.61.0.zip",
    "1a6cd1043af5adb3c5a8c1b2ec0b6abb7d0f241cd8725e233d691b3ca2f312bf",
    "TEI Stylesheets: BSD 2-Clause, or CC BY-SA 3.0",
)
MSDESC = Source(
    "msdesc.odd",
    "7e8b89c",
    "https://raw.githubusercontent.com/msDesc/consolidated-tei-schema/7e8b89c17e8dfff086dd2ef6e2322f580baf7a64/msdesc.odd",
    "93e87cfd1d9a3f4dc8376bb0c25cab22671053edffca9002f54e9c3298b1e9c9",
    "BSD 2-Clause",
)
SCHXSLT = Source(
    "schxslt2-1.11.3.zip",
    "1.11.3",
    "https://codeberg.org/SchXslt/schxslt2/releases/download/v1.11.3/schxslt2-1.11.3.zip",
    "8afe545678c2360c56dea24a5b3471e7417e136bc756516ceeec4151557c070a",
    "MIT",
)
SOURCES = (P5SUBSET, STYLESHEETS, MSDESC, SCHXSLT)


class BuildError(RuntimeError):
    pass


def fetch(source: Source, downloads: Path) -> Path:
    """The source's file in `downloads`, fetched if it's missing, refused if its SHA-256 differs from the pin."""
    downloads.mkdir(parents=True, exist_ok=True)
    path = downloads / source.name
    if path.exists() and sha256(path) == source.sha256:
        return path
    logger.info("Fetching %s %s", source.name, source.version)
    with (
        tempfile.NamedTemporaryFile(dir=downloads, delete=False) as tmp,
        urllib.request.urlopen(source.url, timeout=120) as response,
    ):
        shutil.copyfileobj(response, tmp)
    got = hashlib.sha256(Path(tmp.name).read_bytes()).hexdigest()
    if got != source.sha256:
        Path(tmp.name).unlink()
        raise BuildError(f"{source.name}: SHA-256 {got}, expected {source.sha256}")
    Path(tmp.name).replace(path)
    return path


def unpack(archive: Path, into: Path) -> Path:
    """Unzip an archive once, into a folder named after it."""
    target = into / archive.stem
    if not target.exists():
        tmp = Path(tempfile.mkdtemp(dir=into))
        with zipfile.ZipFile(archive) as z:
            z.extractall(tmp)
        tmp.replace(target)
    return target


@dataclass
class Tools:
    """The unpacked sources a build needs."""

    p5subset: Path
    stylesheets: Path
    msdesc: Path
    transpiler: Path
    schxslt_licence: str

    @classmethod
    def prepare(cls, cache: Path) -> Tools:
        downloads = cache / "downloads"
        paths = {s.name: fetch(s, downloads) for s in SOURCES}
        stylesheets = unpack(paths[STYLESHEETS.name], cache) / "xml" / "tei" / "stylesheet"
        schxslt = unpack(paths[SCHXSLT.name], cache)
        transpilers = sorted(schxslt.glob("*/transpile.xsl"))
        licences = sorted(schxslt.glob("*/LICENSE*"))
        if not transpilers or not licences:
            raise BuildError(f"no transpile.xsl or LICENSE in {schxslt}")
        licence = licences[0].read_text("utf-8")
        return cls(paths[P5SUBSET.name], stylesheets, paths[MSDESC.name], transpilers[0], licence)


class Saxon:
    """TEI's stylesheets and SchXslt2, run by SaxonC-HE."""

    def __init__(self) -> None:
        from saxonche import PySaxonProcessor

        self.processor = PySaxonProcessor(license=False)
        self.xslt = self.processor.new_xslt30_processor()

    def run(self, stylesheet: Path, source: Path, **params: str) -> str:
        executable = self.xslt.compile_stylesheet(stylesheet_file=str(stylesheet))
        executable.set_save_xsl_message(True, None)
        for name, value in params.items():
            executable.set_parameter(name, self.processor.make_string_value(value))
        result = executable.transform_to_string(source_file=str(source))
        if result is None:
            raise BuildError(f"{stylesheet.name} on {source.name} gave no output")
        return str(result)


def comment(text: str) -> str:
    """Text as an XML comment: a double hyphen isn't allowed inside one."""
    while "--" in text:
        text = text.replace("--", "- -")
    return f"<!--\n{text.strip()}\n-->"


def schxslt_notice(licence: str) -> str:
    """SchXslt2's copyright line and permission notice, for the top of the compiled Schematron."""
    return comment(
        f"The code of this file comes from SchXslt2 {SCHXSLT.version} (https://codeberg.org/SchXslt/schxslt2).\n\n{licence}"
    )


def stamped(text: str, odd_sha256: str, notice: str = "") -> str:
    """The generated text with the SPDX line, the stamp and a notice after its XML declaration."""
    head, sep, rest = text.partition("?>") if text.startswith("<?xml") else ("", "", text)
    lines = [f"{head}{sep}".strip(), SPDX, stamp(odd_sha256), notice, rest.lstrip()]
    text = "\n".join(line for line in lines if line)
    return text if text.endswith("\n") else text + "\n"


def build(odd: Path = ODD_PATH, out: Path = SCHEMA_DIR, cache: Path = CACHE_DIR) -> list[Path]:
    """Generate the schema's files from the ODD into `out`; returns those it wrote, which are those that changed."""
    if not odd.exists():
        raise BuildError(f"no ODD at {odd}: the build runs in a clone of the repository")
    tools = Tools.prepare(cache)
    saxon = Saxon()
    work = cache / "work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    common = {"defaultSource": tools.p5subset.as_uri(), "useFixedDate": "true", "verbose": "false"}
    odds = tools.stylesheets / "odds"

    logger.info("Compiling the Bodleian's ODD")
    shutil.copy(tools.msdesc, work / "msdesc.odd")
    (work / MSDESC_COMPILED).write_text(saxon.run(odds / "odd2odd.xsl", work / "msdesc.odd", **common), "utf-8")

    logger.info("Compiling %s", ODD)
    odd_sha256 = sha256(odd)
    shutil.copy(odd, work / ODD)
    compiled = work / "solemne.compiled.odd"
    compiled.write_text(saxon.run(odds / "odd2odd.xsl", work / ODD, **common), "utf-8")

    logger.info("Writing the RelaxNG, the Schematron and its XSLT")
    outputs = {RELAXNG: saxon.run(odds / "odd2relax.xsl", compiled, **common)}
    outputs[SCHEMATRON] = saxon.run(odds / "extract-isosch.xsl", compiled, **common)
    (work / SCHEMATRON).write_text(outputs[SCHEMATRON], "utf-8")
    outputs[SCHEMATRON_XSLT] = saxon.run(tools.transpiler, work / SCHEMATRON)
    notices = {SCHEMATRON_XSLT: schxslt_notice(tools.schxslt_licence)}

    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name in GENERATED:
        text = outputs[name].replace(work.as_uri(), "").replace(str(work), "")
        text = stamped(text, odd_sha256, notices.get(name, ""))
        path = out / name
        if not path.exists() or path.read_text("utf-8") != text:
            path.write_text(text, "utf-8")
            written.append(path)
    return written
