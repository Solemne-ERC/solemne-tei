<!-- SPDX-License-Identifier: MIT -->
# Changelog

Each release says what changed, and whether files that passed may now fail.

## Unreleased

The first release: SOLEMNE's TEI schema as a package.

### The package

- The schema's source is one ODD, `guide/solemne.odd`, under CC BY 4.0. The package holds what is generated from it:
  the RelaxNG, the Schematron and the Schematron compiled to XSLT, the compiled ODD, and `closed-lists.json`; each
  names the ODD's version and SHA-256.
- `solemne-tei validate <paths> [--jobs N] [--json] [--strict]` checks files against the RelaxNG and the Schematron,
  in parallel; each problem has its file, line, check, severity, rule and message.
- `solemne-tei build [--cache DIR]` regenerates the schema from the ODD in a clone, from pinned sources checked by
  their SHA-256; it says when nothing changed.
- `solemne-tei lists [--json]` prints the closed lists, the categories and the codes of the Bible's 73 books.
- From Python: `Validator`, `validate(paths, jobs)`, `Problem`, `Result`, `closed_lists()` and `SCHEMA_VERSION`.
