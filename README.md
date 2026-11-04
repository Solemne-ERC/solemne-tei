# solemne-tei

XML-TEI schema and guidelines for encoding witnesses of early medieval canon law texts. Developed and used within the framework of SOLEMNE - The Social Life of Early Medieval Normative Texts project (ERC Consolidator grant 101087979)

The schema's one source is the ODD, `guide/solemne.odd`, which explains each rule. The package `solemne-tei` holds
what is generated from it, a RelaxNG and a Schematron, and checks TEI files against them: files must pass the
RelaxNG, and the Schematron's findings are reported.

## Install

With Python 3.12 or newer, from the repository at a release's tag:

```
pip install git+https://github.com/Solemne-ERC/solemne-tei@v0.1.0
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

From Python:

```python
from solemne_tei import SCHEMA_VERSION, Validator, closed_lists, validate

results = validate(["one_file.xml"], jobs=4)  # a Result per file, with its Problems
validator = Validator()  # compiled once, to check files one by one
result = validator.check("one_file.xml")
lists = closed_lists()  # {"div": {"type": ["capitulum", ...]}, ...}
```

## The lists encoders need

```
solemne-tei lists
```

It prints the schema's closed lists (the types of divisions, headings, notes and the rest, by element and attribute),
the categories a document's code begins with, and the codes of the Bible's 73 books with their Vulgate names; `--json`
gives the same as data.

## Regenerating the schema

After changing the ODD, in a clone:

```
solemne-tei build
```

It writes the RelaxNG (`solemne.rng`), the Schematron (`solemne.sch`), the Schematron compiled to XSLT
(`solemne-schematron.xsl`), the compiled ODD (`solemne.compiled.odd`) and its closed lists (`closed-lists.json`) into
`src/solemne_tei/schema/`. Each names the version and the SHA-256 of the ODD it came from; a test fails when the ODD
has changed since. The version is the ODD's `editionStmt/edition/@n`, kept equal to the package's. Running the build
again on the same ODD writes nothing, and says so.

The first run fetches what the build needs into `build/tei/` (ignored by git), at pinned versions checked by their
SHA-256:

| What | Version | From |
|---|---|---|
| TEI P5, `p5subset.xml` | 4.12.0 | <https://www.tei-c.org/Vault/P5/4.12.0/xml/tei/odd/p5subset.xml> |
| TEI's stylesheets | 7.61.0 | <https://github.com/TEIC/Stylesheets/releases/tag/v7.61.0> |
| The Bodleian's consolidated TEI schema, `msdesc.odd` | commit `7e8b89c` | <https://github.com/msDesc/consolidated-tei-schema> |
| SchXslt2 | 1.11.3 | <https://codeberg.org/SchXslt/schxslt2> |

The build runs with SaxonC-HE: TEI's `odd2odd` compiles the Bodleian's ODD, then ours, which takes its manuscript
description module from the Bodleian's; `odd2relax` writes the RelaxNG; `extract-isosch` extracts the Schematron;
SchXslt2 compiles it to XSLT. The development install pins SaxonC-HE's version, since the compiled Schematron
differs between versions; the package itself works with a range of them.

A new rule goes into the ODD as a Schematron assertion with an `id`, or as a RelaxNG constraint, with an invalid
sample in `tests/samples/invalid/` named by the rule; the tests check that every assertion of the ODD has its sample.

## Tests

```
.venv/bin/pytest
```

## Licence

The code and the schema are under the MIT licence ([LICENSE](LICENSE)); the guidelines in `guide/` are under CC BY 4.0
([guide/LICENSE](guide/LICENSE)).

## Credits

- **TEI P5**, by the TEI Consortium, distributed under CC BY 3.0 and the BSD 2-Clause licence: the schema is made
  from it.
- **SchXslt2**, by David Maus, under the MIT licence: its code is in the compiled Schematron,
  `solemne-schematron.xsl`, which carries its copyright line and licence.
- **The Bodleian Libraries' consolidated TEI schema**, by James Cummings and the Bodleian Libraries, University of
  Oxford, under the BSD 2-Clause licence: the schema takes its manuscript description module.
- **TEI's stylesheets**, by the TEI Consortium, distributed under CC BY-SA 3.0 and the BSD 2-Clause licence: they
  generate the schema. They're fetched by the build, not distributed with this package.
