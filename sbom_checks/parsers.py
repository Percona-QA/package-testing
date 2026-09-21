"""Parsers for the four PXB SBOM formats.

Two traps here, both verified against the real prototype files:

  * .sbom.txt is a FIXED-WIDTH table. The LICENSE column contains spaces
    ("Apache-2.0 OR BSD-3-Clause" for libkmip), so line.split() shreds it.
    Column offsets are derived from the header row instead.
  * .licenses.txt is "<name> <version> <licence...>" where the licence is the
    rest of the line -- split(None, 2), never split().
"""

import json
import re

from .models import Component

TABLE_COLUMNS = ("NAME", "VERSION", "LICENSE", "LINKAGE", "ORIGIN")

SPDX_ROOT_SPDXID = "SPDXRef-Package-ROOT"


class ParseError(Exception):
    pass


def _mapping(value):
    """The value if it is a JSON object, else an empty one.

    These documents come from a generator we do not control, and "valid JSON of
    the wrong shape" must be reported as a malformed SBOM, never crash the run.
    """
    return value if isinstance(value, dict) else {}


def _sequence(value):
    """The value if it is a JSON array, else an empty one.

    Not just a falsy check: a bare string is truthy and iterates per character,
    which silently produces nonsense instead of an error.
    """
    return value if isinstance(value, list) else []


def _text(raw):
    if isinstance(raw, bytes):
        return raw.decode("utf-8", "replace")
    return raw


def _cdx_license(component):
    """CycloneDX carries a licence either as an SPDX id or as an expression.
    libkmip in the PXB set uses the expression form, so both must be handled."""
    entries = _sequence(component.get("licenses"))
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("expression"):
            return entry["expression"]
        node = entry.get("license") or {}
        if node.get("id"):
            return node["id"]
        if node.get("name"):
            return node["name"]
    return ""


def load_cyclonedx(raw):
    """-> (document, root Component or None, [Component])"""
    try:
        doc = json.loads(_text(raw))
    except ValueError as exc:
        raise ParseError("not valid JSON: %s" % exc)
    if not isinstance(doc, dict):
        raise ParseError("top level is %s, expected an object" % type(doc).__name__)

    meta = _mapping(_mapping(doc.get("metadata")).get("component"))
    root = None
    if meta.get("name"):
        root = Component(meta.get("name", ""), meta.get("version", ""), _cdx_license(meta))

    components = []
    for entry in _sequence(doc.get("components")):
        if not isinstance(entry, dict):
            continue
        props = {}
        for prop in _sequence(entry.get("properties")):
            if isinstance(prop, dict) and prop.get("name"):
                props[prop["name"]] = prop.get("value", "")
        components.append(Component(
            entry.get("name", ""),
            entry.get("version", ""),
            _cdx_license(entry),
            props.get("pxb:linkage", ""),
            props.get("pxb:origin", ""),
        ))
    return doc, root, components


def _spdx_license(package):
    concluded = package.get("licenseConcluded", "")
    if concluded and concluded.upper() != "NOASSERTION":
        return concluded
    return package.get("licenseDeclared", "") or concluded


def _spdx_root_id(doc):
    """The root package is whichever SPDXRef the document DESCRIBES."""
    for rel in _sequence(doc.get("relationships")):
        if isinstance(rel, dict) and rel.get("relationshipType") == "DESCRIBES":
            return rel.get("relatedSpdxElement")
    # _sequence, then index: a documentDescribes that is an object would raise
    # KeyError on [0], and one that is a string would yield a single character.
    described = _sequence(doc.get("documentDescribes"))
    if described:
        return described[0]
    return SPDX_ROOT_SPDXID


def load_spdx(raw):
    """-> (document, root Component or None, [Component])

    Packages are matched on the `name` field, never on SPDXID: SPDXIDs are
    mangled (unordered_dense -> SPDXRef-Package-unordered-dense) because
    underscores are not legal in an SPDXID.
    """
    try:
        doc = json.loads(_text(raw))
    except ValueError as exc:
        raise ParseError("not valid JSON: %s" % exc)
    if not isinstance(doc, dict):
        raise ParseError("top level is %s, expected an object" % type(doc).__name__)

    root_id = _spdx_root_id(doc)
    root = None
    components = []
    for package in _sequence(doc.get("packages")):
        if not isinstance(package, dict):
            continue
        component = Component(
            package.get("name", ""),
            package.get("versionInfo", ""),
            _spdx_license(package),
        )
        if package.get("SPDXID") == root_id:
            root = component
        else:
            components.append(component)
    return doc, root, components


def _column_offsets(header):
    """Start offset of every column in a fixed-width header row."""
    offsets = []
    for name in TABLE_COLUMNS:
        match = re.search(r"\b%s\b" % re.escape(name), header)
        if match is None:
            raise ParseError(
                "table header is missing the %s column (header was: %r); "
                "the .sbom.txt table format has changed" % (name, header)
            )
        offsets.append(match.start())
    if offsets != sorted(offsets):
        raise ParseError("table columns are out of order: %r" % (offsets,))
    return offsets


def load_table(raw):
    """Parse the fixed-width .sbom.txt table -> [Component]."""
    lines = [line for line in _text(raw).splitlines() if line.strip()]
    if not lines:
        raise ParseError("file is empty")
    offsets = _column_offsets(lines[0]) + [None]

    components = []
    for line in lines[1:]:
        fields = []
        for index in range(len(TABLE_COLUMNS)):
            start = offsets[index]
            end = offsets[index + 1]
            fields.append(line[start:end].strip() if end else line[start:].strip())
        name, version, license_, linkage, origin = fields
        if not name:
            raise ParseError("row has no NAME value: %r" % line)
        components.append(Component(name, version, license_, linkage, origin))
    if not components:
        raise ParseError("table has a header but no rows")
    return components


def load_licenses(raw):
    """Parse .licenses.txt ('<name> <version> <licence...>') -> [Component]."""
    components = []
    for line in _text(raw).splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 2)
        if len(parts) < 2:
            raise ParseError("row has fewer than 2 fields: %r" % line)
        name = parts[0]
        version = parts[1]
        license_ = parts[2].strip() if len(parts) > 2 else ""
        components.append(Component(name, version, license_))
    if not components:
        raise ParseError("file has no rows")
    return components


LOADERS = {
    "cdx": load_cyclonedx,
    "spdx": load_spdx,
    "table": load_table,
    "licenses": load_licenses,
}
