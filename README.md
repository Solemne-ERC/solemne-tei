# solemne-tei

XML-TEI schema and guidelines for encoding witnesses of early medieval canon law texts. Developed and used within the framework of SOLEMNE - The Social Life of Early Medieval Normative Texts project (ERC Consolidator grant 101087979)

The schema's one source is the ODD, `guide/solemne.odd`, which explains each rule: a root file with the guide's
parts in `guide/chapters/`, included by XInclude, each holding its prose and the specifications of the rules it
explains. The package `solemne-tei` holds what is generated from it, a RelaxNG and a Schematron, and checks TEI files
against them: files must pass the RelaxNG, and the Schematron's findings are reported.

## Install

With Python 3.12 or newer, from the repository at a release's tag:

```
pip install git+https://github.com/Solemne-ERC/solemne-tei@v0.8.0
```

For development, from a clone:

```
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## Checking files

```
solemne-tei validate one_file.xml a_folder/
```

Folders are searched for `*.xml`. Each problem is printed with its file, line, check (`well-formed`, `relaxng` or
`schematron`), severity, rule and message, then a summary with the Schematron's findings by rule. `--json` prints the
results as JSON; `--jobs N` sets the number of workers (all cores by default; the results don't depend on it);
`--strict` makes Schematron errors fail too. The exit code is 1 when a file isn't well formed or fails the RelaxNG.

`--format bodleian` checks files in an import format against that format's own schema instead: manuscript
descriptions in the form of the Bodleian Libraries' catalogues, which the project converts into its own. The
package holds the Bodleian's schema at a pinned commit: its RelaxNG as the Bodleian publishes it, and its Schematron
compiled to XSLT.

From Python:

```python
from solemne_tei import SCHEMA_VERSION, Validator, closed_lists, validate

results = validate(["one_file.xml"], jobs=4)  # a Result per file, with its Problems
validator = Validator()  # compiled once, to check files one by one
result = validator.check("one_file.xml")
bodleian = validate(["description.xml"], format="bodleian")  # against an import format's own schema
lists = closed_lists()  # {"div": {"type": ["capitulum", ...]}, ...}
```

## The lists encoders need

```
solemne-tei lists
```

It prints the schema's closed lists (the types of divisions, headings, notes and the rest, by element and attribute),
the categories a document's code begins with, and the codes of the Bible's 73 books with their Vulgate names; `--json`
gives the same as data.

## The guide

The guide is the ODD itself: `guide/solemne.odd` holds the header, the front matter and the parts by XInclude, from
`guide/chapters/`, and the specification. Each part explains its forms with examples from the project's corpus, and
holds the specifications of the rules it explains, with a counter-example of each. `guide/templates/` holds whole
files to start from. To read it, as HTML pages or as a PDF:

```
solemne-tei docs --html
solemne-tei docs --pdf
```

The HTML goes into `build/html/`: `index.html` holds the title page and the contents, and each part, appendix and
specification has a page of its own, made by TEI's `odd2html` with the guide's stylesheets in `guide/style/`. The PDF,
`build/pdf/solemne-guide.pdf`, is made by TEI's LaTeX stylesheets and set by LuaLaTeX, which TeX Live provides; it
leaves out TEI's reference for each element, which the HTML has. Both are set in Junicode. The appendices that can be
generated are: A, the elements and attributes; B, every rule with its check, severity and tier; C, the code tables
and the vocabularies' seeds; F, the changes, from the changelog. Neither the HTML nor the PDF is committed. In a
clone, the command runs offline once the sources and Junicode are cached.

## Regenerating the schema

After changing the ODD or one of its parts, in a clone:

```
solemne-tei build
```

It first expands the ODD, its parts included, and checks it against TEI's schema for ODD files, its RelaxNG and the
Schematron rules embedded in it, as Oxygen does; it stops with the problems listed, each at its part's file and line,
if the ODD isn't valid. Then it writes the RelaxNG (`solemne.rng`), the Schematron (`solemne.sch`), the Schematron
compiled to XSLT (`solemne-schematron.xsl`), the expanded ODD (`solemne.expanded.odd`), the compiled ODD
(`solemne.compiled.odd`) and its closed lists (`closed-lists.json`) into `src/solemne_tei/schema/`. Each names the
version and the SHA-256 of the expanded ODD it came from; a test fails when the ODD or a part has changed since. The version is the ODD's `editionStmt/edition/@n`, kept equal to the package's. Running the build
again on the same ODD writes nothing, and says so.

The first run fetches what the build needs into `build/tei/` (ignored by git), at pinned versions checked by their
SHA-256:

| What | Version | From |
|---|---|---|
| TEI P5, `p5subset.xml` | 4.12.0 | <https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/odd/p5subset.xml> |
| TEI P5's schema for ODD files, `tei_odds.rng` | 4.12.0 | <https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/custom/schema/relaxng/tei_odds.rng> |
| TEI's stylesheets | 7.61.0 | <https://github.com/TEIC/Stylesheets/releases/tag/v7.61.0> |
| The Bodleian's consolidated TEI schema, `msdesc.rng`, and its licence | commit `7e8b89c` | <https://github.com/msDesc/consolidated-tei-schema> |
| SchXslt2 | 1.11.3 | <https://codeberg.org/SchXslt/schxslt2> |
| Junicode, for the guide's HTML and PDF only | 2.226 | <https://github.com/psb1558/Junicode-font/releases/tag/v2.226> |

The build runs with SaxonC-HE: TEI's `odd2odd` compiles the ODD; `odd2relax` writes the RelaxNG; `extract-isosch` extracts the Schematron;
SchXslt2 compiles it to XSLT. It also compiles the Schematron embedded in the Bodleian's RelaxNG, once into the
cache, and writes the import format's two files into `src/solemne_tei/formats/bodleian/`, with the Bodleian's notice.
The development install pins SaxonC-HE's version, since the compiled Schematron
differs between versions; the package itself works with a range of them.

A new rule goes into the part of the guide that explains it, in that part's `specGrp`: a Schematron assertion with
an `id`, in a `constraintSpec` of its own, or a restriction the RelaxNG checks, named by the `xml:id` of the
specification that makes it (a `valList`, an `attDef`, a `datatype`). It names its tier by `@corresp`, and comes
with a counter-example: an `egXML` with `valid="false"` and the rule's name in `@n`. The tests check every example of
the guide: one without `@valid` passes both checks, placed in a minimal file when it's a fragment; a counter-example
fails on its rule; and every rule has one.

## Tests

```
.venv/bin/pytest
```

The PDF's test is marked `slow`, and skipped without LuaLaTeX; `pytest -m "not slow"` leaves it out.

## Releases

A release is a tag `vX.Y.Z` on `main`, whose version the ODD, `pyproject.toml` and the package give, and whose section
the changelog holds. The release workflow (`.github/workflows/release.yml`) then rebuilds the schema from an empty
cache and checks it against the committed files, runs the tests, makes the guide's HTML and PDF, and publishes:

- a GitHub release, with the schema's files, the HTML as a zip and the PDF, and the changelog's section as its notes;
- the pages, from the `gh-pages` branch: `schema/X.Y.Z/` and `guide/X.Y.Z/`, with `schema/latest/` and
  `guide/latest/` for the highest version, keeping every earlier one;
- from 1.0.0 on, the package on PyPI, by trusted publishing.

On a pull request, or started by hand, the workflow builds the same files and keeps them as the run's artifacts,
publishing nothing.

## Licence

The code and the schema are under the MIT licence ([LICENSE](LICENSE)); the guidelines in `guide/` are under CC BY 4.0
([guide/LICENSE](guide/LICENSE)).

## Credits

- **TEI P5**, by the TEI Consortium, distributed under CC BY 3.0 and the BSD 2-Clause licence: the schema is made
  from it, and the build checks the ODD against TEI P5's schema for ODD files, which it fetches and doesn't
  distribute.
- **SchXslt2**, by David Maus, under the MIT licence: its code is in the compiled Schematron,
  `solemne-schematron.xsl`, which carries its copyright line and licence.
- **The Bodleian Libraries' consolidated TEI schema**, by James Cummings and the Bodleian Libraries, University of
  Oxford, under the BSD 2-Clause licence: the schema's manuscript description is modelled on it, and the import
  format's files in `src/solemne_tei/formats/bodleian/` are its schema, which carry its copyright line and licence.
- **The Bodleian Libraries' TEI P5 Customization and Encoding Guidelines for Manuscript Description**, by James
  Freeman and Matthew Holford, Bodleian Library, Oxford, under CC BY 4.0: the guide's part on manuscripts is modelled
  on them, and quotes them where their words fit, each quotation introduced as "Oxford encoding guide:".
- **TEI's stylesheets**, by the TEI Consortium, distributed under CC BY-SA 3.0 and the BSD 2-Clause licence: they
  generate the schema. They're fetched by the build, not distributed with this package.
- **Junicode**, by Peter S. Baker, under the SIL Open Font License 1.1: the guide's HTML and PDF are set in it. It's
  fetched by `solemne-tei docs`, not distributed with this package; the HTML serves its web fonts with the licence.
