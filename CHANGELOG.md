<!-- SPDX-License-Identifier: MIT -->
# Changelog

Each release says what changed, and whether files that passed may now fail.

## Unreleased

### The guide

- The ODD is split into the guide's parts: `guide/solemne.odd` is the root, and includes by XInclude one file per
  part in `guide/chapters/`, each holding its prose and the specifications of the rules it explains, which the
  `schemaSpec` takes by `specGrpRef`. The rules are unchanged: every file passes and fails as before, with the same
  messages. Oxygen checks the root with its parts included.
- The build checks the ODD with its parts included, reports each error at its part's file and line, and writes the
  expanded ODD into the package as `solemne.expanded.odd`. The stamp in each generated file names the expanded ODD's
  SHA-256.

## 0.1.0 (2026-11-04)

The first release: SOLEMNE's TEI schema as a package.

### The package

- The schema's source is one ODD, `guide/solemne.odd`, under CC BY 4.0. The package holds what is generated from it:
  the RelaxNG, the Schematron and the Schematron compiled to XSLT, the compiled ODD, and `closed-lists.json`; each
  names the ODD's version and SHA-256.
- `solemne-tei validate <paths> [--jobs N] [--json] [--strict]` checks files against the RelaxNG and the Schematron,
  in parallel; each problem has its file, line, check, severity, rule and message.
- `solemne-tei build [--cache DIR]` regenerates the schema from the ODD in a clone, from pinned sources checked by
  their SHA-256; it says when nothing changed. It first checks the ODD against TEI's schema for ODD files, as
  Oxygen does, and stops if the ODD isn't valid.
- `solemne-tei lists [--json]` prints the closed lists, the categories and the codes of the Bible's 73 books.
- From Python: `Validator`, `validate(paths, jobs)`, `Problem`, `Result`, `closed_lists()` and `SCHEMA_VERSION`.
  `Validator` also takes another schema's RelaxNG and compiled Schematron.

### The forms

Files written for the draft of this schema need these changes to pass.

- **The formal title's identifiers:** the document's code in an `idno` without a type, its category in
  `idno type="category"` and its type in `idno type="type"`, once each; `collCode`, `collCat` and `collType` are no
  longer accepted. The code begins with its category's prefix (`COLL` for `SYSCOLL` and `CHRCOLL`); the categories
  gain `LR`, `CPT` and `CHA`, which take any prefix for now, as `UNK` does. A manuscript's code (`.ms-`) and the type
  `manuscript` go with the manuscript's description in the `sourceDesc`. An export adds there the permalinks of the
  levels the file belongs to, typed `work`, `version`, `witness` and `transcription`.
- **Pointers to records in the header:** `@ref`, in the same forms as in the text (a placeholder `#new_person_…`, an
  id in the file, or a permalink), on `title`, `author`, `editor`, `country`, `region`, `settlement`, `origPlace`,
  `repository`, `institution` and the names. `provenance`, `acquisition` and `origin` name their record inside them,
  by a name with `@ref`. A record's pointer in `@key` or `@corresp` is reported, as a warning.
- **External ids:** a node's ids in other projects go in `@sameAs`, each with a prefix declared in the header by
  `prefixDef` in `listPrefixDef` (`clavis:IS35.27`); an undeclared prefix is an error, and a prefix other than
  `scta`, `clavis`, `pseudoisidor` and `corpuscorporum` a warning. `idno/@type` is a closed list: the authorities
  (`wikidata`, `viaf`, `gnd`, `geonames`, `tgn`, `pleiades`, `mirabile`, `clavis`, `biblissima`, `schoenberg`,
  `hmml`, `bodleian`, `manusOnline`, the Bodleian's `ieArk`, `crArk` and `SCN`), the formal title's `category` and
  `type`, the levels' `work`, `version`, `witness` and `transcription`, and `shelfmark`, `ISBN`, `url` and
  `biblatex`.
- **Gaps:** `@reason` is optional (without one, the reason is unknown) and closed: `lacuna`, `damage`, `illegible`,
  `reproduction`, `deleted`, `sampling`, `editorial`; the files' `missing` is `lacuna`. The extent, where known, is
  `@quantity` with `@unit` (`leaves`, `lines`, `words`, `chars`), which go together, or `@extent`.
- **The text's elements** gain `rs` (a record of a kind no name element fits, its kind in `@type`, its record in
  `@ref` in the names' forms), `anchor` (a point a stand-off annotation refers to), `supplied`, and `choice` with
  `abbr` and `expan`, for the rare doubtful cases.
- **Curation:** `correction` in `editorialDecl`, its `@status` `high`, `medium`, `low` or `unknown`, with a paragraph
  saying how, as TEI requires; the whole text's is the default, and a division or paragraph that differs points to
  another by `@decls`. Of several corrections, one is the default. `@decls` points only to a `correction` or a
  `segmentation` in the header.
- **Inferred units:** `segmentation type="inferred-units"` states them for the whole file (`@default` true, or
  alone), or, with `@default` false and an id, for the divisions that point to it by `@decls`; a statement for
  divisions that none points to is a warning.
- **Manuscripts:** a description (`msDesc`) has at least one codicological unit (`msPart`), with its own identifier.
- **Fragments:** a span that crosses others or the structure, such as a quotation over several paragraphs, is split
  into fragments joined by `@next` and `@prev`; each points to the other within the file, on an element of the same
  kind.
