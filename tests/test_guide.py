# SPDX-License-Identifier: MIT
"""The guide: its parts included, each specification group referenced by the schema, its ids unique; the build
reports an error in a part at that part's file and line."""

from pathlib import Path

import pytest
from lxml import etree

from solemne_tei.build import ODD_PATH, BuildError, check_odd, expand
from solemne_tei.validate import Validator

TEI = "http://www.tei-c.org/ns/1.0"
XI = "http://www.w3.org/2001/XInclude"
GUIDE = ODD_PATH.parent


@pytest.fixture(scope="module")
def odd() -> etree._Element:
    # lxml refuses a document whose xml:ids repeat, so parsing it is the check that they don't.
    return etree.fromstring(expand(ODD_PATH).text)


def test_every_part_is_included(odd: etree._Element) -> None:
    root = etree.parse(str(ODD_PATH)).getroot()
    hrefs = [el.get("href") for el in root.iter(f"{{{XI}}}include")]
    assert hrefs
    assert sorted(hrefs) == sorted(f"chapters/{p.name}" for p in (GUIDE / "chapters").glob("*.xml"))
    assert not list(odd.iter(f"{{{XI}}}*"))
    assert "xi" not in odd.nsmap


def test_every_specification_group_is_referenced_once(odd: etree._Element) -> None:
    groups = [g.get("{http://www.w3.org/XML/1998/namespace}id") for g in odd.iter(f"{{{TEI}}}specGrp")]
    refs = [r.get("target") for r in odd.iter(f"{{{TEI}}}specGrpRef")]
    assert groups
    assert sorted(refs) == sorted(f"#{g}" for g in groups)


def test_every_part_carries_the_guide_s_licence() -> None:
    for path in [ODD_PATH, *(GUIDE / "chapters").glob("*.xml")]:
        assert "<!-- SPDX-License-Identifier: CC-BY-4.0 -->" in path.read_text("utf-8").splitlines()[1], path.name


ROOT = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<TEI xmlns="http://www.tei-c.org/ns/1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title type="formal">
          <idno>C.SAM-0600</idno>
          <idno type="category">C</idno>
          <idno type="type">edition</idno>
        </title>
      </titleStmt>
      <publicationStmt>
        <p>A test.</p>
      </publicationStmt>
      <sourceDesc>
        <p>Made up.</p>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
      <xi:include href="chapters/part.xml"/>
    </body>
  </text>
</TEI>
"""
PART = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<div xmlns="http://www.tei-c.org/ns/1.0" type="chapter">
  <p>Placuit.</p>
  <div type="chpater">
    <p>Placuit.</p>
  </div>
</div>
"""


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters" / "part.xml").write_text(PART, encoding="utf-8")
    path = tmp_path / "root.xml"
    path.write_text(ROOT, encoding="utf-8")
    return path


def test_expansion_places_each_element_at_its_file_and_line(root: Path) -> None:
    expanded = expand(root)
    text = expanded.text.decode("utf-8")
    assert "SPDX" not in text
    assert "xml:base" not in text
    assert "XInclude" not in text
    lines = text.splitlines()
    division = next(i for i, line in enumerate(lines, 1) if 'type="chpater"' in line)
    assert expanded.places[division] == ("chapters/part.xml", 5)
    body = next(i for i, line in enumerate(lines, 1) if "<body>" in line)
    assert expanded.places[body] == ("root.xml", 22)


def test_the_odd_check_names_the_part_and_its_line(root: Path, tmp_path: Path) -> None:
    # The package's own schema stands in for TEI's schema for ODD files, which needs a download.
    expanded = expand(root)
    path = tmp_path / "expanded.xml"
    path.write_bytes(expanded.text)
    with pytest.raises(BuildError, match=r"chapters/part\.xml:5: relaxng error"):
        check_odd(path, Validator(), expanded.places)
