<!-- SPDX-License-Identifier: MIT -->
# Changelog

Each release says what changed, and whether files that passed may now fail.

## Unreleased

A text taken from another project names that project as its source, in its header.

### What changes for existing files

The project's files that passed 0.5.0 still pass: on the 411 coded files, as received and as corrected, the counts
are 0.5.0's, rule by rule. Two new Schematron errors could fail another file: two sources in one `sourceDesc`
(`text-source-one`), or a source without its name (`source-named`). A source with a link and no date retrieved is
reported (`source-retrieved`, a warning).

### The schema

- **A text's source:** a `bibl` typed `source` in `sourceDesc`, after the edition's or the manuscript's
  description, in the form a record's source has: the source's name in `title`, a link to the text there in `ref`,
  the date it was taken in a `date` typed `retrieved`, the licence and the source's version where known, and a
  credit in the source's own words in a `note`. At most one per file (`text-source-one`); every source, a record's
  too, has its name (`source-named`); one with a link gives the date it was taken (`source-retrieved`).

### The guide

- **Part II, publication and source:** a text's source, with Abbo of Fleury's Canones (Patrologia Latina 139) as
  Corpus Corporum gives them; a text edited on a website names the site both as its edition and as its source; what
  the import reads, still to be settled with the application. Parts I and V point to it.
- **Part II, other projects' ids:** how Corpus Corporum numbers a paragraph: in its own text, not the file's, which
  may split its headings or number its divisions otherwise; a division inside another joined by a dot; page breaks
  not counted. An example from Isaac of Langres's Canones (Patrologia Latina 124).

## 0.5.0 (2026-11-06)

A note type for an edition's later collections, the later texts that took a passage over: `reception`.

### What changes for existing files

Nothing that passed 0.4.0 fails: the new type widens a closed list. The warning for codes left in a note's words
(`source-note-codes`) now checks reception notes and notes in the standOff too, reports older codes it missed
(`C.NIC_0325_11`, an underscore for the hyphen), and no longer takes Gratian's abbreviations (`D.5`, `C.16`) for
codes. On the project's 411 coded files, as received, this version reports 125,777 problems, against 0.4.0's 125,768:
the 9 more are such older codes in source notes' words, all warnings. On the files as corrected, the count is the
same as 0.4.0's.

### The schema

- **Reception notes:** a note typed `reception` gives the later texts that took the passage over, as an edition's
  tier of later collections lists them ("Burchard I, 135; Ivo, Decr. V, 234"): the editor's words, and the later
  texts' codes in `@source`. It stands inline, or in a stand-off annotation over its span, as source notes and
  parallels do: `text-note-type` and `annotation-body` take it. For this type, `@source` names the later texts, not
  the passage's sources.
- **Codes in a note's words:** `source-note-codes` checks source and reception notes, inline and in the standOff. A
  word starting `C.` or `D.` counts as a code when a letter follows the dot, then a hyphen, an underscore or a dot,
  and a digit.

### The guide

- **Part IV, notes:** reception notes, and how to tell them from parallels, by the edition's form and not the dates;
  an example from the Collectio Dionysio-Hadriana of 1525, whose margins give Gratian's chapters, and a stand-off one.
  The pointers' forms name a reception note's `@source`.
- **Parts I, VI and X, appendix D:** the reception note among the layers; how the import reads its codes, still to be
  settled with the application; the layer in stand-off bodies; older notes typed `corresp` that become reception
  notes.
- **Part VIII:** the project converts the Bodleian's descriptions with a converter outside this package; the guide
  said a tool of this package would.

## 0.4.0 (2026-11-05)

The guide finished and published: Parts IX and X, on editions and on exports, with the export template; appendices C
to F; the guide as HTML pages and as a PDF; the release workflow, which publishes the schema and the guide on GitHub
Pages. 1.0.0 follows once the project's corrected files pass.

### What changes for existing files

Files that passed 0.3.0 may now fail where a publication's volume or pages are in a unit outside the five, or a
code joins its date by a dot. On the project's 411 coded files, as received, this version reports 125,768 problems,
against 0.3.0's 125,685: the 83 more are the units of `biblScope` and `citedRange` in 61 files, all RelaxNG errors
until the corrections rewrite them. The dotted codes of four penitentials (`P.THB.0700` and three others) fail once
the corrections move them to the formal title's code, unless the hyphen goes in with them.

- **A date in a code is joined by a hyphen:** `code-format` refuses a date joined by a dot, as the coding rules have
  it (`P.THB.0700` is `P.THB-0700`). A part of a code after a second dot is a source part, beginning with a letter
  (`.ms-`, `.ed-`).
- **Publications:** the units of `biblScope` and `citedRange` are a closed list, `volume`, `part`, `issue`, `page` and
  `column` (`scope-unit`, `cited-range-unit`), so that each is a field of biblatex: a `tome`, `vol`, `band`,
  `fascicle` or `heft` now fails the RelaxNG. A title in a `biblStruct` has the level of its part, `a` in `analytic`,
  `m` or `j` in `monogr`, `s` in `series` (`title-level`, an error). A `biblStruct`'s `@type` is biblatex's entry
  type, a warning outside biblatex's types (`entry-type`); `@subtype` goes.
- **Stand-off annotations:** a target is an id in the file, a range, a span by `string-range()` or a permalink
  (`annotation-target`), and the body is one `note`, holding the layer's element alone or typed by a note's layer
  (`annotation-body`); both errors. `annotation/@motivation` goes: the body says the layer.
- **Exports' elements:** a `linkGrp` is typed `reuse` or not at all (`link-group-type`), and a hit of text reuse
  has two targets (`reuse-link`); a `change` is typed `release` or not at all (`change-type`), and a release has
  `@n` and `@when` (`release-named`).

### The guide

- **Part IX, editions and literature:** a publication's parts and their titles' levels, the MGH case and texts
  with editors of their own, the two kinds of pages, the units, biblatex's entry types and the table of its
  fields, publications as records, and reconstructions.
- **Part X, exports:** the nodes' ids, permalinks and the records listed; the citation structure; annotations in the
  standOff, each with its layer's element; text reuse; releases and change sets; the vocabularies' terms with their
  permalinks; both checks. The template `export.xml` is a short export of the Council of Soissons of 744.
- **Appendices C to F:** C, the code tables and the vocabularies' seeds, each seed with where it comes from and its
  Oxford term; D, older encodings and what they became; E, the import formats' tables, the Bodleian's moved there
  from Part VIII; F, the changes, from this changelog. C and F are generated, as A and B are, into the HTML; the
  examples' sources follow them.
- **The guide's title:** "The SOLEMNE Encoding Guidelines", on a title page with its
  authors, version, date and licences, in the HTML and the PDF.
- **The HTML, a page per part:** `solemne-tei docs --html` writes a folder of pages, the title page and contents in
  `index.html`, a page for the front matter, each part and each appendix, and one per specification of TEI's
  reference, so that no page is large. The parts are numbered I to X; no page shows the build's date. The guide's
  stylesheets are in `guide/style/`, and the text is set in Junicode, served with the pages.
- **The PDF:** `solemne-tei docs --pdf` makes the guide TEI Lite, then LaTeX, by TEI's stylesheets, and sets it with
  LuaLaTeX in Junicode, into `build/pdf/solemne-guide.pdf`. It leaves out TEI's reference for each element, which the
  HTML holds. Junicode is fetched once at a pinned release, checked by its SHA-256.

### The package

- **The validator no longer hangs** on a file whose publication fails beside its `imprint`, such as a volume in an
  older unit: libxml2 never finishes compiling `imprint`'s pattern on its own, so the narrowing of a RelaxNG error to
  its element doesn't try it, and a failure inside an `imprint` is reported at its parent.
- **The release workflow:** on a tag `vX.Y.Z`, it rebuilds the schema from an empty cache and checks it against the
  committed files, runs the tests, makes the HTML and the PDF, and publishes: a GitHub release with the schema's
  files, the HTML and the PDF, its notes this changelog's section; the pages, `schema/X.Y.Z/`, `guide/X.Y.Z/` and
  `latest/`, keeping every earlier version, earlier releases' schemas included; from 1.0.0 on, the package on PyPI.
  On a pull request, or started by hand, it builds the same and publishes nothing.

## 0.3.0 (2026-11-05)

The guide for records, relations, dates and manuscripts: Parts V to VIII, with the schema's own manuscript
description in place of the Bodleian's module, the Bodleian's descriptions as an import format, and two templates.

### What changes for existing files

Files that passed 0.2.0 may now fail where they describe a manuscript, date by EDTF or name a calendar, or point to
an authority's record from a note of links. On the project's 411 coded files, this version reports 125,685 problems,
against 0.2.0's 125,126; the differences, by rule, are below.

- **Manuscript descriptions, our own:** the schema takes TEI P5's manuscript description module, restricted to the
  guide's profile, in place of the Bodleian Libraries' consolidated schema. Descriptions that passed may now fail:
  - 21 of the module's elements, and the header's `scriptNote`, are left out, each said another way: `accMat`,
    `catchwords`, `custEvent`, `custodialHist`, `dim`, `filiation`, `heraldry`, `material`, `msFrag`, `msItemStruct`,
    `musicNotation`, `objectType`, `scriptDesc`, `seal`, `sealDesc`, `secFol`, `signatures`, `stamp`, `typeDesc`,
    `typeNote`, `watermark`; so are `msItem/@class`, `handDesc/@hands`, `handNote`'s `@scribe`, `@scribeRef`,
    `@scriptRef` and `@medium`, and the Bodleian's additions (`collation/@mainStructures`, `layout/@topLine`,
    `layout/@rulingMedium`);
  - `altIdentifier` is typed `former`, `siglum` or `code` (`alt-identifier-type`); `origDate/@type` is `undated`
    or nothing (`orig-date-type`); `binding/@contemporary` is `true`, `false` or `unknown` (`binding-contemporary`);
  - new errors: inside a description, only the profile's elements, in their places, and the prose's `locus`, names,
    `title`, `date`, `foreign`, `hi` and `ref` (`description-elements`): contents and the physical description go on
    a unit, the manuscript's own physical description holds the binding alone, and `num` is left out; every unit
    is dated, or said undated by `origDate type="undated"` (`unit-dated`); dimensions give their unit
    (`dimensions-unit`); a binding is dated or says whether it's contemporary (`binding-dated`); a `@hand` pointing
    into the file points to a `handNote` (`hand-declared`);
  - new warnings: an item without its folios (`item-locus`); an object's form, a support's material, a hand's script
    and execution, and a decoration's type outside their vocabularies' seeds (`form-term`, `material-term`,
    `script-term`, `execution-term`, `decoration-term`);
  - the Bodleian's own rules go, among them its warnings on an item's language;
  - `hi` joins the schema, for italics and the like in a description's prose; `handNote` gains `@execution`;
    `ref/@type` gains `iiif`, for a manuscript's IIIF manifests in `surrogates`.

  On the corpus's 38 descriptions: 110 new errors of `description-elements` (60 `num`, 37 physical descriptions of
  the whole manuscript, 9 contents on the manuscript, 3 `filiation`, a unit's binding), 56 items without folios, 86
  new RelaxNG errors (73 `altIdentifier`s, 7 `msItem/@class`, `filiation`), and the Bodleian's 35 warnings gone.
- **Dates, in one form:** a date's bounds in TEI's W3C attributes, its EDTF in `@when-custom`, `@from-custom` and
  `@to-custom` with `@datingMethod="#edtf"`. TEI's other forms of the same date are left out: the ISO attributes
  (`@when-iso`, …), `@period`, `@datingPoint`, `@notBefore-custom` and `@notAfter-custom`. No file of the corpus uses
  them.
- **Calendars declared:** `calendarDesc` and `calendar` join the schema, and every `@calendar` and `@datingMethod`
  points to a declared calendar (`calendar-declared`, an error). Files that give `calendar="Gregorian"` without
  declaring it now fail: 46 dates in the corpus's 38 manuscript descriptions, which become `calendar="#gregorian"`
  with its declaration.
- **Calendars named:** a manuscript's date (`origDate`) and a date in the text name the calendar of their words
  (`date-calendar`, an error): `#gregorian` for a modern statement such as "sec. IX", the source's own otherwise (a
  Julian day, an era). A unit said undated, and the dates of publications, records and the header, name none. The
  corpus's `origDate`s all have one; no transcription marks a date yet.
- **Dates checked:** no bound comes after its pair (`date-bounds-order`, an error; two dates in the corpus); an EDTF
  value has EDTF's form (`date-edtf-form`, an error); the bounds agree with the EDTF by years
  (`date-edtf-bounds`, a warning).
- **Relations:** `@cert` on a relation is `high`, `medium` or `low` (`relation-certainty`, closed); a relation's
  `@name` outside the guide's types is a warning (`relation-term`). No file of the corpus has relations.
- **Pointers typed:** `ptr/@type` is `canonical` or `stand-in` (a work's choices of versions) or `via` (what a text
  came through, in a relation), closed (`pointer-type`). No file of the corpus types a `ptr`.
- **A work's choices of versions:** a work names at most one canonical version and one version that stands in for
  it (`version-choices`, an error).
- **Ids, not links, for an authority's records:** a link into an authority's records (Mirabile's authors, titles and
  manuscripts, VIAF, GND, Wikidata, GeoNames, …) in a note of links is a warning (`link-authority`): its id goes in
  an `idno` typed by the authority. Notes of links keep the links to other pages. The corpus's 294 Mirabile links
  in notes of links are reported.
- **Extra fields:** `fs` and `f` join the schema, for a record's fields that no element holds.

### The package

- **Import formats:** `solemne-tei validate --format bodleian`, and `validate(paths, format="bodleian")` and
  `Validator(format="bodleian")` from Python, check manuscript descriptions in the Bodleian's form against the
  Bodleian's own schema, which the project converts into its own. The package holds that schema at a pinned commit
  (`7e8b89c`): its RelaxNG as the Bodleian publishes it, and its Schematron compiled to XSLT, with its notice. Its
  rules are named as the Bodleian names them (`origDate.check`). `FORMATS` lists the formats.
- The build no longer compiles the Bodleian's ODD for the schema, and the schema's generated files no longer carry
  its notice: they hold none of its material. It fetches the Bodleian's RelaxNG in place of its ODD.

### The guide

- Part V, records: placeholders, ids and permalinks; persons, places, institutions, events, works and versions,
  witnesses, work groups, rare kinds and their extra fields; ids elsewhere, with Mirabile's indices by the kind of
  record; sources. A work names its canonical version, and the version that stands in for it.
- Part VI, relations: their form, the types to start with and their reverses, the levels' relations.
- Part VII, dates: the one form, with the corpus's own wordings; calendars and eras, with the Julian day converted to
  the Gregorian in the bounds; what the checks require.
- Part VIII, manuscripts: the description and the manuscript's identifier; units; contents, items inside items and
  an item's transcription; the physical description; hands, decoration, the binding; history; images, literature
  and sources; the Bodleian's descriptions as an import format, with the table of what the conversion does with each
  of their elements and attributes, in `guide/mappings/`. It is modelled on the Bodleian Libraries' guidelines for
  manuscript description, credited once in the front matter, and quotes them where their words fit.
- A template for a collection in one manuscript, `manuscript-collection.xml`: the Collectio 400 capitulorum in
  Munich, Clm 4592, with the manuscript's description in the guide's form.
- A template for a reconstruction, `reconstruction.xml`: the collection of Benedictus Levita, with the two editions
  it was put together from as its witnesses.

## 0.2.0 (2026-11-04)

The guide for texts: the front matter and Parts I to IV, the templates, and the guide as HTML. Encoders can use this
version for texts; manuscripts, records, relations and dates come in the next.

### What changes for existing files

Files that passed 0.1.0 may now fail where they have fragments, codes of the categories `LR`, `CPT` and `CHA`, or
segments with terms. No file of the project's corpus has any of these yet: on its 411 coded files, this version
reports the same problems as 0.1.0.

- **Fragments, two new errors:** `fragment-attributes`: a later fragment (one with `@prev`) carries only its
  `xml:id`, `@prev` and `@next`, and the span's other attributes go on its first fragment; a segment's later
  fragments repeat its `@type`, which the RelaxNG requires, with the same value. `fragment-order`: `@next` points to
  an element later in the file, so that the fragments follow the text's order.
- **Codes:** a code of the categories `LR`, `CPT` and `CHA` begins with `LR.`, `CPT.` and `CHA.` (`code-category`),
  as the old guide's coding rules have it; it took any prefix before. `UNK` still takes any.
- **File names:** `code-matches-file-name` reads any category's prefix in a file's name, not only `C`, `D`, `COLL`,
  `P`, `EP`, `H` and `EX`.
- **A segment's term:** `seg` takes `@ana`, pointing to a category of a taxonomy in the header's `classDecl`; a term
  that isn't declared there is an error (`seg-term-declared`).

### The guide

- The ODD is split into the guide's parts: `guide/solemne.odd` is the root, and includes by XInclude one file per
  part in `guide/chapters/`, each holding its prose and the specifications of the rules it explains, which the
  `schemaSpec` takes by `specGrpRef`. Oxygen checks the root with its parts included.
- The front matter and Parts I to IV are written: what a file describes; the file and its header, the coding rules
  among them; the text and its transcription; what is marked in the text. Each section has examples from the corpus,
  credited in a list of the examples' sources, and the counter-examples of its rules. Parts V to X hold their rules
  and counter-examples; their prose comes later.
- Every element, attribute and rule names its tier, `required`, `common`, `full` or `export only`, by `@corresp`
  pointing to the tiers' taxonomy in the ODD's header; the elements taken from TEI unchanged take theirs from a table
  beside the specification. Each Schematron rule has a `constraintSpec` of its own, and each restriction the RelaxNG
  checks (a closed list, a required attribute, a pattern) an `xml:id` on the specification that makes it.
- The guide's examples are tests: an example passes both checks, a counter-example (`valid="false"`) fails on the
  rule its `@n` names, and every rule has one. Fragments are checked in a minimal file. The invalid samples that
  tested each rule are now counter-examples in the parts that explain their rules.
- The templates, in `guide/templates/`, are whole files to start from, each a short text of the corpus: a minimal
  file, a rich one, a council and a collection from editions, a decretal and a penitential. Each declares the schema
  by two `<?xml-model?>` lines, at its version's address on GitHub Pages, and passes both checks.

### The package

- `solemne-tei docs --html [--out DIR]` writes the guide as one HTML page, by TEI's `odd2html`, with appendix A (the
  elements and attributes) and appendix B (every rule, with its check, severity, tier and part) generated from the
  specifications, and each counter-example labelled with the rule it breaks.
- The build checks the ODD with its parts included, reports each error at its part's file and line, and writes the
  expanded ODD into the package as `solemne.expanded.odd`. The stamp in each generated file names the expanded ODD's
  SHA-256. It stops when a `specGrpRef` leads nowhere or a `specGrp` isn't referred to, which TEI's stylesheets would
  pass over without a word.

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
