# SPDX-License-Identifier: MIT
"""XML-TEI schema and guidelines for encoding witnesses of early medieval canon law texts. Developed and used
within the framework of SOLEMNE - The Social Life of Early Medieval Normative Texts project (ERC Consolidator
grant 101087979)"""

from solemne_tei.formats import FORMATS
from solemne_tei.schema_files import ClosedLists, closed_lists, schema_version
from solemne_tei.validate import Problem, Result, Validator, validate

__version__ = "0.8.0"

# The version of the ODD the package's schema was generated from.
SCHEMA_VERSION = schema_version()

__all__ = ["FORMATS", "SCHEMA_VERSION", "ClosedLists", "Problem", "Result", "Validator", "closed_lists", "validate"]
