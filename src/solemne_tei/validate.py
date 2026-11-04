# SPDX-License-Identifier: MIT
"""Check TEI files against the schema: the RelaxNG, with lxml, and the Schematron compiled to XSLT, with SaxonC-HE.
Each problem carries its file, line and message; a file that isn't well formed is reported, not raised.

Files are checked in parallel, on all cores by default; the results don't depend on the number of workers."""

from __future__ import annotations

import copy
import os
import re
from collections import Counter
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lxml import etree

from solemne_tei.schema_files import RELAXNG, SCHEMA_DIR, SCHEMATRON_XSLT

SVRL = "http://purl.oclc.org/dsdl/svrl"
RNG = "http://relaxng.org/ns/structure/1.0"
STEP = re.compile(r"/(?:Q\{([^}]*)\})?([^/\[{]+)(?:\[(\d+)\])?")
PATTERN = re.compile(r"^schematron-constraint-(.+?)(?:-\d+)?$")
ERROR_ROLES = {"error", "fatal"}


@dataclass(frozen=True)
class Problem:
    """One thing a file does wrong."""

    file: str
    line: int | None
    check: str  # well-formed, relaxng or schematron
    severity: str  # error, warning or info
    rule: str  # the Schematron rule, or the check's name
    message: str

    def __str__(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        return f"{where}: {self.check} {self.severity} [{self.rule}] {self.message}"


@dataclass
class Result:
    """What one file's checks found."""

    file: str
    problems: list[Problem] = field(default_factory=list)

    @property
    def well_formed(self) -> bool:
        return not any(p.check == "well-formed" for p in self.problems)

    @property
    def passes_relaxng(self) -> bool:
        return self.well_formed and not any(p.check == "relaxng" for p in self.problems)

    @property
    def schematron_errors(self) -> int:
        return sum(1 for p in self.problems if p.check == "schematron" and p.severity == "error")


class Validator:
    """The schema's two checks, compiled once."""

    def __init__(self, schema_dir: Path = SCHEMA_DIR) -> None:
        from saxonche import PySaxonProcessor

        self._grammar = etree.parse(str(schema_dir / RELAXNG))
        self.relaxng = etree.RelaxNG(self._grammar)
        self._defines = {d.get("name") for d in self._grammar.iter(f"{{{RNG}}}define")}
        self._alone: dict[str, Any] = {}
        self._saxon = PySaxonProcessor(license=False)
        xslt = self._saxon.new_xslt30_processor()
        self._schematron = xslt.compile_stylesheet(stylesheet_file=str(schema_dir / SCHEMATRON_XSLT))

    def check(self, path: str | os.PathLike[str]) -> Result:
        name = str(path)
        path = Path(path)
        result = Result(name)
        parser = etree.XMLParser(huge_tree=True, resolve_entities=False)
        try:
            tree = etree.parse(str(path), parser)
        except etree.XMLSyntaxError as e:
            result.problems.append(Problem(name, e.lineno, "well-formed", "error", "well-formed", e.msg))
            return result
        except OSError as e:
            result.problems.append(Problem(name, None, "well-formed", "error", "unreadable", str(e)))
            return result
        if not self.relaxng.validate(tree):
            result.problems.extend(self._relaxng_problems(name, tree))
        result.problems.extend(self._schematron_problems(name, path, tree))
        return result

    def _relaxng_problems(self, name: str, tree: Any) -> list[Problem]:
        """The RelaxNG's errors, each at the innermost element that fails on its own: libxml2 reports a failure
        inside a choice at the element holding it ("body has extra content")."""
        problems = []
        for el in self._failing(tree.getroot()):
            schema = self._schema_for(el)
            log = schema.error_log if schema is not None and not schema.validate(_alone(el)) else []
            for entry in log:
                problems.append(Problem(name, el.sourceline, "relaxng", "error", "relaxng", entry.message))
        if not problems:
            for entry in self.relaxng.error_log:
                problems.append(Problem(name, entry.line or None, "relaxng", "error", "relaxng", entry.message))
        return problems

    def _failing(self, el: Any) -> list[Any]:
        """The innermost elements under `el` that fail on their own; `el` if none of its children does."""
        failing = []
        for child in el:
            if not isinstance(child.tag, str):
                continue
            schema = self._schema_for(child)
            if schema is not None and not schema.validate(_alone(child)):
                failing.extend(self._failing(child))
        return failing or [el]

    def _schema_for(self, el: Any) -> Any:
        """The RelaxNG whose start is this element's pattern, or None when the grammar has none."""
        local = etree.QName(el).localname
        if local not in self._defines:
            return None
        if local not in self._alone:
            grammar = copy.deepcopy(self._grammar.getroot())
            for start in grammar.findall(f"{{{RNG}}}start"):
                grammar.remove(start)
            start = etree.SubElement(grammar, f"{{{RNG}}}start")
            etree.SubElement(start, f"{{{RNG}}}ref", name=local)
            self._alone[local] = etree.RelaxNG(grammar)
        return self._alone[local]

    def _schematron_problems(self, name: str, path: Path, tree: Any) -> Iterable[Problem]:
        svrl = self._schematron.transform_to_string(source_file=str(path.resolve()))
        if not svrl:
            yield Problem(name, None, "schematron", "error", "schematron", "the Schematron check gave no report")
            return
        report = etree.fromstring(svrl.encode("utf-8"))
        pattern = ""
        for el in report:
            tag = etree.QName(el).localname
            if tag == "active-pattern":
                pattern = el.get("id") or ""
            elif tag in ("failed-assert", "successful-report"):
                rule = el.get("id") or _rule_name(el.get("patternId") or pattern)
                role = (el.get("role") or "error").lower()
                severity = "error" if role in ERROR_ROLES else "info" if role == "info" else "warning"
                text = " ".join("".join(el.itertext()).split())
                yield Problem(name, _line(tree, el.get("location") or ""), "schematron", severity, rule, text)


def _alone(el: Any) -> Any:
    """A copy of an element without the text after it, to validate on its own."""
    alone = copy.deepcopy(el)
    alone.tail = None
    return etree.ElementTree(alone)


def _rule_name(pattern_id: str) -> str:
    m = PATTERN.match(pattern_id)
    return m.group(1) if m else pattern_id or "schematron"


def _line(tree: Any, location: str) -> int | None:
    """The line of the element an XPath 3 location (`/Q{ns}TEI[1]/Q{ns}text[1]`) points to."""
    el = tree.getroot()
    steps = list(STEP.finditer(location))
    if not steps:
        return None
    for i, m in enumerate(steps):
        ns, local, n = m.group(1), m.group(2), m.group(3)
        if n is None or local.startswith("@") or local.endswith(")"):
            break  # an attribute, a text node or a comment: its element is the place
        tag = f"{{{ns}}}{local}" if ns else local
        if i == 0:
            if el.tag != tag:
                return None
            continue
        matches = [ch for ch in el if ch.tag == tag]
        if len(matches) < int(n):
            break
        el = matches[int(n) - 1]
    line = el.sourceline
    return int(line) if line else None


_validator: Validator | None = None


def _init_worker(schema_dir: Path) -> None:
    global _validator
    _validator = Validator(schema_dir)


def _check_in_worker(path: str | os.PathLike[str]) -> Result:
    assert _validator is not None
    return _validator.check(path)


def xml_files(paths: Iterable[Path]) -> list[Path]:
    """The files named, and the `*.xml` under the folders named, sorted."""
    found: set[Path] = set()
    for p in paths:
        found.update(p.rglob("*.xml") if p.is_dir() else [p])
    return sorted(found)


def validate(
    paths: Sequence[str | os.PathLike[str]], jobs: int | None = None, schema_dir: Path = SCHEMA_DIR
) -> list[Result]:
    """Check files with `jobs` workers (all cores by default), in the order given. A path may be a string."""
    jobs = jobs or os.cpu_count() or 1
    if jobs <= 1 or len(paths) <= 1:
        validator = Validator(schema_dir)
        return [validator.check(p) for p in paths]
    workers = min(jobs, len(paths))
    with ProcessPoolExecutor(workers, initializer=_init_worker, initargs=(schema_dir,)) as pool:
        return list(pool.map(_check_in_worker, paths))


def summary(results: Sequence[Result]) -> str:
    """How many files pass, and the Schematron's findings by rule."""
    lines = [
        f"{len(results)} files: {sum(r.well_formed for r in results)} well-formed, "
        f"{sum(r.passes_relaxng for r in results)} pass the RelaxNG, "
        f"{sum(not r.schematron_errors for r in results if r.well_formed)} without a Schematron error"
    ]
    rules = Counter((p.severity, p.rule) for r in results for p in r.problems if p.check == "schematron")
    for (severity, rule), n in sorted(rules.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  schematron {severity} [{rule}]: {n}")
    return "\n".join(lines)
