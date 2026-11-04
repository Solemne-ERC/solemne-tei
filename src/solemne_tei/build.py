# SPDX-License-Identifier: MIT
"""Generate the schema from the ODD.

Fetches TEI P5's `p5subset.xml`, TEI's schema for ODD files, TEI's stylesheets, the Bodleian's consolidated msDesc
ODD with its licence, and SchXslt2 at pinned versions, checked by SHA-256, into the cache. First it expands our ODD,
`guide/solemne.odd` with its parts in `guide/chapters/` included by XInclude, and checks the expanded ODD against
TEI's schema for ODD files, its RelaxNG and the Schematron rules embedded in it, as Oxygen does; it stops if the ODD
isn't valid, naming each error's part and line. Then, with SaxonC-HE: compiles the Bodleian's ODD and ours with TEI's
`odd2odd` (ours takes its `msdescription` module from the Bodleian's), writes the RelaxNG with `odd2relax`, extracts
the Schematron with `extract-isosch`, and compiles it to XSLT with SchXslt2. It keeps the expanded and the compiled
ODD, and writes the closed lists as `closed-lists.json`. Each generated file names the ODD it came from by its version
and the expanded ODD's SHA-256, and carries the notices of the material it contains.

The build runs in a clone of the repository: it reads `guide/` and writes into the package's `schema/`.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import shutil
import tempfile
import textwrap
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from solemne_tei.logs import logger
from solemne_tei.schema_files import (
    CLOSED_LISTS,
    COMPILED_ODD,
    EXPANDED_ODD,
    GENERATED,
    ODD,
    RELAXNG,
    SCHEMA_DIR,
    SCHEMATRON,
    SCHEMATRON_XSLT,
    TEI,
    closed_lists_of,
    odd_version,
    sha256,
    stamp,
    stamp_text,
)
from solemne_tei.validate import Validator

REPOSITORY = Path(__file__).resolve().parents[2]
ODD_PATH = REPOSITORY / "guide" / ODD
CACHE_DIR = REPOSITORY / "build" / "tei"

# The name the ODD gives the Bodleian's compiled ODD, in `moduleRef/@source`; the build puts it next to our ODD.
MSDESC_COMPILED = "msdesc.compiled.odd"

SPDX = "<!-- SPDX-License-Identifier: MIT -->"
SPDX_GUIDE = "<!-- SPDX-License-Identifier: CC-BY-4.0 -->"
SCH = "http://purl.oclc.org/dsdl/schematron"
XML_BASE = "{http://www.w3.org/XML/1998/namespace}base"


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
# TEI's schema for ODD files, which Oxygen checks an ODD against.
TEI_ODDS = Source(
    "tei_odds.rng",
    "4.12.0",
    "https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_odds.rng",
    "655113c0d40b798847d6f41b15c95a75055c0ee3e8ad6fb923c49ad7ebc87df1",
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
MSDESC_LICENCE = Source(
    "msdesc-LICENSE",
    "7e8b89c",
    "https://raw.githubusercontent.com/msDesc/consolidated-tei-schema/7e8b89c17e8dfff086dd2ef6e2322f580baf7a64/LICENSE",
    "bdc76293925bdd0be036cfded22dcaa863713fb25b7b3f16be76f3735f9f394d",
    "BSD 2-Clause",
)
SOURCES = (P5SUBSET, TEI_ODDS, STYLESHEETS, MSDESC, MSDESC_LICENCE, SCHXSLT)


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
    tei_odds: Path
    stylesheets: Path
    msdesc: Path
    transpiler: Path
    tei_licence: str
    msdesc_licence: str
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
        return cls(
            p5subset=paths[P5SUBSET.name],
            tei_odds=paths[TEI_ODDS.name],
            stylesheets=stylesheets,
            msdesc=paths[MSDESC.name],
            transpiler=transpilers[0],
            tei_licence=tei_bsd_licence(paths[P5SUBSET.name]),
            msdesc_licence=paths[MSDESC_LICENCE.name].read_text("utf-8"),
            schxslt_licence=licences[0].read_text("utf-8"),
        )


def tei_bsd_licence(p5subset: Path) -> str:
    """TEI P5's BSD 2-Clause licence, as its header gives it, in plain text."""
    for _, el in etree.iterparse(str(p5subset), tag=f"{{{TEI}}}licence"):
        if "BSD" not in (el.get("target") or ""):
            continue
        parts = []
        for child in el:
            if etree.QName(child).localname == "list":
                parts.extend(textwrap.fill("* " + _words(item), 100, subsequent_indent="  ") for item in child)
            else:
                parts.append(textwrap.fill(_words(child), 100))
        return "\n\n".join(parts)
    raise BuildError(f"no BSD 2-Clause licence in the header of {p5subset.name}")


def _words(el: etree._Element) -> str:
    return " ".join("".join(el.itertext()).split())


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


def embedded_schematron(rng: Path) -> bytes:
    """The Schematron rules embedded in a RelaxNG grammar that TEI's stylesheets made, as one Schematron schema: the
    namespaces first, then the patterns."""
    grammar = etree.parse(str(rng))
    embedded = [el for el in grammar.iter(f"{{{SCH}}}*") if etree.QName(el.getparent()).namespace != SCH]
    schema = etree.Element(f"{{{SCH}}}schema", queryBinding="xslt2", nsmap={"sch": SCH})
    for kind in ("ns", "pattern"):
        schema.extend(copy.deepcopy(el) for el in embedded if etree.QName(el).localname == kind)
    return etree.tostring(schema, xml_declaration=True, encoding="UTF-8")


def odd_validator(tools: Tools, cache: Path) -> Validator:
    """TEI's schema for ODD files, as Oxygen applies it: its RelaxNG and its embedded Schematron, compiled to XSLT
    once into the cache. It's compiled by a Saxon of its own: Saxon numbers the documents it reads, and the
    compiled Schematron of our ODD carries those numbers in its names."""
    xslt = cache / f"tei_odds-{TEI_ODDS.version}-schxslt-{SCHXSLT.version}.xsl"
    if not xslt.exists():
        sch = xslt.with_suffix(".sch")
        sch.write_bytes(embedded_schematron(tools.tei_odds))
        tmp = xslt.with_suffix(".tmp")
        tmp.write_text(Saxon().run(tools.transpiler, sch), "utf-8")
        tmp.replace(xslt)
    return Validator(relaxng=tools.tei_odds, schematron_xslt=xslt)


Places = dict[int, tuple[str, int]]


@dataclass(frozen=True)
class Expanded:
    """The ODD with its parts included: its text, and for each line of it where an element starts, the file (relative
    to the ODD's folder) and the line that element was written on."""

    text: bytes
    places: Places

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text).hexdigest()


def expand(odd: Path) -> Expanded:
    """The ODD with the parts it includes by XInclude, without the `xml:base` the inclusion adds and without the SPDX
    lines: each generated file carries its own."""
    tree = etree.parse(str(odd))
    tree.xinclude()
    root = tree.getroot()
    origins = []
    for el in root.iter(tag=etree.Element):
        base = el.get(XML_BASE) or next((a.get(XML_BASE) for a in el.iterancestors() if a.get(XML_BASE)), odd.name)
        origins.append((base, el.sourceline))
    for el in root.iter(tag=etree.Element):
        el.attrib.pop(XML_BASE, None)
    for spdx in [c for c in root.iter(tag=etree.Comment) if "SPDX-License-Identifier" in (c.text or "")]:
        _remove(spdx)
    # XInclude's namespace, which nothing uses once the parts are included.
    etree.cleanup_namespaces(root, keep_ns_prefixes=[p for p in root.nsmap if p and p != "xi"])
    text = etree.tostring(root, xml_declaration=True, encoding="UTF-8") + b"\n"
    places: Places = {}
    for el, origin in zip(etree.fromstring(text).iter(tag=etree.Element), origins, strict=True):
        places.setdefault(el.sourceline, origin)
    return Expanded(text, places)


def _remove(node: etree._Element) -> None:
    """Remove a node, keeping the text after it."""
    parent = node.getparent()
    previous = node.getprevious()
    if previous is not None:
        previous.tail = (previous.tail or "") + (node.tail or "")
    else:
        parent.text = (parent.text or "") + (node.tail or "")
    parent.remove(node)


def check_specification_groups(expanded: Expanded) -> None:
    """Stops the build when a `specGrpRef` leads to no `specGrp`, or a `specGrp` isn't referred to: TEI's
    stylesheets would leave its specifications out of the schema without a word."""
    root = etree.fromstring(expanded.text)
    xml_id = "{http://www.w3.org/XML/1998/namespace}id"
    groups = {g.get(xml_id): g for g in root.iter(f"{{{TEI}}}specGrp")}
    refs = {r.get("target", "")[1:]: r for r in root.iter(f"{{{TEI}}}specGrpRef")}

    def place(el: etree._Element) -> str:
        file, line = expanded.places.get(el.sourceline or 0, (ODD, el.sourceline))
        return f"{file}:{line}"

    problems = [f"  {place(r)}: a specGrpRef to #{t}, which no specGrp has" for t, r in refs.items() if t not in groups]
    unnamed = [(i, g) for i, g in groups.items() if i not in refs]
    problems += [f"  {place(g)}: the specGrp {i}, which no specGrpRef names" for i, g in unnamed]
    if problems:
        raise BuildError("the schema's specification groups don't match:\n" + "\n".join(problems))


def check_odd(odd: Path, validator: Validator, places: Places | None = None) -> None:
    """Stops the build when the ODD isn't valid against the validator's schema; its warnings are logged. With the
    places of an expanded ODD, each problem is reported at the file and line it was written on."""
    problems = []
    for problem in validator.check(odd).problems:
        file, line = (places or {}).get(problem.line or 0, (odd.name, problem.line))
        problems.append(dataclasses.replace(problem, file=file, line=line))
    for problem in problems:
        if problem.severity != "error":
            logger.warning("%s", problem)
    errors = [p for p in problems if p.severity == "error"]
    if errors:
        listed = "\n".join(f"  {p}" for p in errors)
        raise BuildError(f"{odd.name} isn't valid against TEI's schema for ODD files:\n{listed}")


def comment(text: str) -> str:
    """Text as an XML comment: a double hyphen isn't allowed inside one."""
    while "--" in text:
        text = text.replace("--", "- -")
    return f"<!--\n{text.strip()}\n-->"


def credits_notice(tools: Tools) -> str:
    """TEI P5's and the Bodleian's copyright lines and licences, for the top of every generated file."""
    return comment(
        f"This schema is made from TEI P5 {P5SUBSET.version} by the TEI Consortium (https://tei-c.org/), which"
        " distributes it under the Creative Commons Attribution 3.0 Unported licence"
        " (https://creativecommons.org/licenses/by/3.0/) and under the BSD 2-Clause licence:\n\n"
        f"{tools.tei_licence}\n\n"
        "Its manuscript description module comes from the Bodleian Libraries' consolidated TEI schema"
        f" (https://github.com/msDesc/consolidated-tei-schema, commit {MSDESC.version}), under its licence:\n\n"
        f"{tools.msdesc_licence}"
    )


def schxslt_notice(tools: Tools) -> str:
    """SchXslt2's copyright line and permission notice, for the top of the compiled Schematron."""
    return comment(
        f"The code of this file comes from SchXslt2 {SCHXSLT.version} (https://codeberg.org/SchXslt/schxslt2),"
        f" under its licence:\n\n{tools.schxslt_licence}"
    )


def stamped(text: str, version: str, odd_sha256: str, notice: str = "", spdx: str = SPDX) -> str:
    """The generated text with the SPDX line, the stamp and a notice after its XML declaration."""
    head, sep, rest = text.partition("?>") if text.startswith("<?xml") else ("", "", text)
    lines = [f"{head}{sep}".strip(), spdx, stamp(version, odd_sha256), notice, rest.lstrip()]
    text = "\n".join(line for line in lines if line)
    return text if text.endswith("\n") else text + "\n"


def _without_paths(text: str, work: Path, p5subset: Path) -> str:
    """Generated text without the paths of the machine it was made on: the folder it was made in goes, and TEI P5's
    cached copy becomes its pinned address."""
    text = text.replace(p5subset.as_uri(), P5SUBSET.url)
    for path in (f"{work.as_uri()}/", f"file:{work}/", work.as_uri(), f"file:{work}", str(work)):
        text = text.replace(path, "")
    return text


def closed_lists_json(compiled_odd: Path, version: str, odd_sha256: str) -> str:
    """`closed-lists.json`: the compiled ODD's closed lists, with the licence and the stamp as keys of their own."""
    payload = {
        "SPDX-License-Identifier": "MIT",
        "generated": stamp_text(version, odd_sha256),
        "lists": closed_lists_of(compiled_odd),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def build(odd: Path = ODD_PATH, out: Path = SCHEMA_DIR, cache: Path = CACHE_DIR) -> list[Path]:
    """Generate the schema's files from the ODD into `out`; returns those it wrote, which are those that changed."""
    if not odd.exists():
        raise BuildError(f"no ODD at {odd}: the build runs in a clone of the repository")
    tools = Tools.prepare(cache)
    saxon = Saxon()
    work = cache / "work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    expanded = expand(odd)
    check_specification_groups(expanded)
    (work / ODD).write_bytes(expanded.text)
    logger.info("Checking %s, its parts included, against TEI's schema for ODD files", ODD)
    check_odd(work / ODD, odd_validator(tools, cache), expanded.places)
    common = {"defaultSource": tools.p5subset.as_uri(), "useFixedDate": "true", "verbose": "false"}
    odds = tools.stylesheets / "odds"

    logger.info("Compiling the Bodleian's ODD")
    shutil.copy(tools.msdesc, work / "msdesc.odd")
    (work / MSDESC_COMPILED).write_text(saxon.run(odds / "odd2odd.xsl", work / "msdesc.odd", **common), "utf-8")

    logger.info("Compiling %s", ODD)
    odd_sha256 = expanded.sha256
    version = odd_version(odd)
    compiled = work / COMPILED_ODD
    compiled.write_text(saxon.run(odds / "odd2odd.xsl", work / ODD, **common), "utf-8")

    logger.info("Writing the RelaxNG, the Schematron and its XSLT, and the closed lists")
    outputs = {RELAXNG: saxon.run(odds / "odd2relax.xsl", compiled, **common)}
    outputs[SCHEMATRON] = saxon.run(odds / "extract-isosch.xsl", compiled, **common)
    (work / SCHEMATRON).write_text(outputs[SCHEMATRON], "utf-8")
    outputs[SCHEMATRON_XSLT] = saxon.run(tools.transpiler, work / SCHEMATRON)
    outputs[EXPANDED_ODD] = expanded.text.decode("utf-8")
    outputs[COMPILED_ODD] = compiled.read_text("utf-8")
    credits = credits_notice(tools)
    # The expanded ODD holds only the guide's own text.
    notices = {SCHEMATRON_XSLT: f"{credits}\n{schxslt_notice(tools)}", EXPANDED_ODD: ""}
    # The expanded and the compiled ODD are the guide's, so under its licence.
    spdx = {EXPANDED_ODD: SPDX_GUIDE, COMPILED_ODD: SPDX_GUIDE}
    files = {
        name: stamped(
            _without_paths(text, work, tools.p5subset),
            version,
            odd_sha256,
            notices.get(name, credits),
            spdx.get(name, SPDX),
        )
        for name, text in outputs.items()
    }
    files[CLOSED_LISTS] = closed_lists_json(compiled, version, odd_sha256)

    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name in GENERATED:
        text = files[name]
        path = out / name
        if not path.exists() or path.read_text("utf-8") != text:
            path.write_text(text, "utf-8")
            written.append(path)
    return written
