# SPDX-License-Identifier: MIT
"""The code tables encoders need beside the closed lists: the documents' categories, and the Bible's books with the
codes that source pointers use for them."""

import csv
from dataclasses import dataclass
from importlib import resources

# The categories a document's code begins with, as the schema checks them on the formal title's category.
CATEGORIES = ("SYSCOLL", "CHRCOLL", "C", "D", "P", "H", "EX", "EP", "LR", "CPT", "CHA", "BIB", "UNK")


def code_prefix(category: str) -> str:
    """The prefix a code of this category begins with: COLL for both kinds of collection, the category itself for the
    others. A code of category UNK may take any prefix."""
    return "COLL" if category in ("SYSCOLL", "CHRCOLL") else category


@dataclass(frozen=True)
class Book:
    """A book of the Bible: its code in source pointers (`MAT_18_19`), its Vulgate name, and its testament (`ot`,
    `nt`, or `ap` for the deuterocanonical books)."""

    code: str
    name: str
    testament: str


def bible_books() -> list[Book]:
    """The 73 books, in the Vulgate's order."""
    text = resources.files("solemne_tei").joinpath("tables", "bible-books.tsv").read_text("utf-8")
    rows = csv.DictReader((line for line in text.splitlines() if not line.startswith("#")), delimiter="\t")
    return [Book(row["code"], row["name"], row["testament"]) for row in rows]
