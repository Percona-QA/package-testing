"""SPDX licence expression normalisation.

The four PXB SBOM files express the same licence in four vocabularies:

  .cdx.json       licenses[].license.id  or  licenses[].expression
  .spdx.json      licenseConcluded (falling back to licenseDeclared)
  .sbom.txt       the LICENSE column
  .licenses.txt   everything after "<name> <version> "

Comparing those raw would flag cosmetic differences as failures, so each is
reduced to a set of canonical operands before comparison.
"""

import re

# Values that mean "no licence stated" rather than naming one.
NULL_LICENSES = frozenset(["", "NOASSERTION", "NONE", "UNKNOWN", "-", "N/A"])

# Deprecated or informal spellings -> current SPDX identifier.
ALIASES = {
    "GPL-2.0": "GPL-2.0-ONLY",
    "GPL-2.0+": "GPL-2.0-OR-LATER",
    "GPL-3.0": "GPL-3.0-ONLY",
    "GPL-3.0+": "GPL-3.0-OR-LATER",
    "LGPL-2.1": "LGPL-2.1-ONLY",
    "LGPL-2.1+": "LGPL-2.1-OR-LATER",
    "APACHE2": "APACHE-2.0",
    "APACHE 2.0": "APACHE-2.0",
    "APACHE-2": "APACHE-2.0",
    "BSD-2": "BSD-2-CLAUSE",
    "BSD-3": "BSD-3-CLAUSE",
    "BSD": "BSD-3-CLAUSE",
    "BOOST-1.0": "BSL-1.0",
    "ZLIB LICENSE": "ZLIB",
    "MIT LICENSE": "MIT",
}

_OPERATORS = re.compile(r"\s+(?:AND|OR|WITH)\s+", re.IGNORECASE)
_WS = re.compile(r"\s+")


def is_null(value):
    return canonical_text(value) in NULL_LICENSES


def canonical_text(value):
    """Uppercase, collapse whitespace, strip parens and the LicenseRef- prefix."""
    if value is None:
        return ""
    text = _WS.sub(" ", str(value)).strip().strip("()").strip()
    text = text.upper()
    if text.startswith("LICENSEREF-"):
        text = text[len("LICENSEREF-"):]
    return text


def operands(expression):
    """Reduce a licence expression to a frozenset of canonical operands.

    'Apache-2.0 OR BSD-3-Clause' -> {'APACHE-2.0', 'BSD-3-CLAUSE'}

    Operator semantics (AND vs OR) are deliberately discarded: the goal is to
    detect a generator that dropped or renamed a licence between formats, not to
    reason about licence compatibility.
    """
    text = canonical_text(expression)
    if text in NULL_LICENSES:
        return frozenset()
    parts = []
    for raw in _OPERATORS.split(text):
        part = raw.strip().strip("()").strip()
        if not part:
            continue
        parts.append(ALIASES.get(part, part))
    return frozenset(parts)


def equivalent(a, b, strict=False):
    """Compare two licence expressions.

    Default is non-empty intersection, which tolerates one format carrying a
    fuller expression than another. strict=True demands identical operand sets.
    """
    sa, sb = operands(a), operands(b)
    if not sa and not sb:
        return True
    if not sa or not sb:
        return False
    return sa == sb if strict else bool(sa & sb)
