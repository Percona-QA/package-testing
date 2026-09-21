"""Hand-rolled structural validation for CycloneDX and SPDX documents.

Deliberately not jsonschema: the docker side is pinned to pytest 5.2.1 and the
molecule targets install pip through a fragile fallback chain across 24 OSes, so
a third-party dependency is a new failure mode on every platform. The schemas
would have to be vendored anyway, and hand-rolled checks give far better failure
messages than a schema validator's path expressions.

Every function returns a list of Finding rather than raising, so one run reports
every problem instead of stopping at the first.
"""

import re

from .models import Finding
from .parsers import SPDX_ROOT_SPDXID, _mapping, _sequence
from . import licenses as lic

CDX_SPEC_VERSIONS = ("1.2", "1.3", "1.4", "1.5", "1.6")
SPDX_ID_RE = re.compile(r"^SPDXRef-[A-Za-z0-9.\-]+$")


def _matches(actual, expected):
    """Version comparison tolerant of a package release suffix.

    An SBOM may say 9.7.1-rc1 while rpm reports 9.7.1-rc1-1.el9; accept either
    as a prefix of the other rather than demanding an exact string match.
    """
    a = (actual or "").strip()
    e = (expected or "").strip()
    if not a or not e:
        return False
    return a == e or a.startswith(e) or e.startswith(a)


def check_cyclonedx(doc, root, components, expect_name=None, expect_version=None):
    findings = []
    add = lambda msg: findings.append(Finding("cdx", msg))
    # Root identity is reported separately from document structure: "this SBOM
    # describes the wrong version" is a different problem from "this SBOM is
    # malformed", and each gets its own named test.
    add_root = lambda msg: findings.append(Finding("root", msg))

    if doc.get("bomFormat") != "CycloneDX":
        add("bomFormat is %r, expected 'CycloneDX'" % doc.get("bomFormat"))

    spec = doc.get("specVersion")
    if not spec:
        add("specVersion is missing")
    elif spec not in CDX_SPEC_VERSIONS:
        add("specVersion %r is not a version this check recognises (%s)"
            % (spec, ", ".join(CDX_SPEC_VERSIONS)))

    if not doc.get("serialNumber"):
        add("serialNumber is missing")

    if "metadata" in doc and not isinstance(doc.get("metadata"), dict):
        add("metadata is %s, expected an object"
            % type(doc.get("metadata")).__name__)
    elif "component" in _mapping(doc.get("metadata")) \
            and not isinstance(_mapping(doc.get("metadata")).get("component"), dict):
        add("metadata.component is %s, expected an object"
            % type(_mapping(doc.get("metadata")).get("component")).__name__)

    if "components" in doc and not isinstance(doc.get("components"), list):
        add("components is %s, expected an array" % type(doc.get("components")).__name__)

    if root is None:
        add("metadata.component is missing -- the document does not say what it describes")
    else:
        if expect_name and not _matches(root.name, expect_name):
            add_root("metadata.component.name is %r, expected %r" % (root.name, expect_name))
        if expect_version and not _matches(root.version, expect_version):
            add_root("metadata.component.version is %r, expected %r"
                     % (root.version, expect_version))

    if not components:
        add("components[] is empty")
        return findings

    seen_refs = {}
    for index, entry in enumerate(_sequence(doc.get("components"))):
        if not isinstance(entry, dict):
            # The parsers filter these out; the validation loop must too, or a
            # mixed array parses cleanly and then crashes one function later.
            add("components[%d] is %s, expected an object"
                % (index, type(entry).__name__))
            continue
        where = entry.get("name") or "components[%d]" % index
        if not entry.get("name"):
            add("%s has no name" % where)
        if not entry.get("version"):
            add("%s has no version" % where)
        if not entry.get("purl"):
            add("%s has no purl" % where)
        if not entry.get("licenses"):
            add("%s has no licenses[]" % where)
        ref = entry.get("bom-ref")
        if not ref:
            add("%s has no bom-ref" % where)
        elif ref in seen_refs:
            add("bom-ref %r is used by both %r and %r" % (ref, seen_refs[ref], where))
        else:
            seen_refs[ref] = where

    for component in components:
        if lic.is_null(component.license):
            add("%s has no usable licence (%r)" % (component.name, component.license))

    return findings


def check_spdx(doc, root, components, expect_name=None, expect_version=None):
    findings = []
    add = lambda msg: findings.append(Finding("spdx", msg))
    add_root = lambda msg: findings.append(Finding("root", msg))

    version = doc.get("spdxVersion", "")
    if not version.startswith("SPDX-"):
        add("spdxVersion is %r, expected something like 'SPDX-2.3'" % version)
    if doc.get("SPDXID") != "SPDXRef-DOCUMENT":
        add("SPDXID is %r, expected 'SPDXRef-DOCUMENT'" % doc.get("SPDXID"))
    if not doc.get("dataLicense"):
        add("dataLicense is missing")
    if not doc.get("name"):
        add("document name is missing")
    if not doc.get("documentNamespace"):
        add("documentNamespace is missing")

    if "packages" in doc and not isinstance(doc.get("packages"), list):
        add("packages is %s, expected an array" % type(doc.get("packages")).__name__)
    if "relationships" in doc and not isinstance(doc.get("relationships"), list):
        add("relationships is %s, expected an array"
            % type(doc.get("relationships")).__name__)

    packages = _sequence(doc.get("packages"))
    if not packages:
        add("packages[] is empty")
        return findings

    seen_ids = {}
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            add("packages[%d] is %s, expected an object"
                % (index, type(package).__name__))
            continue
        name = package.get("name") or "packages[%d]" % index
        spdx_id = package.get("SPDXID")
        if not spdx_id:
            add("%s has no SPDXID" % name)
        else:
            if not SPDX_ID_RE.match(spdx_id):
                add("SPDXID %r for %s contains characters outside [A-Za-z0-9.-]"
                    % (spdx_id, name))
            if spdx_id in seen_ids:
                add("SPDXID %r is used by both %r and %r" % (spdx_id, seen_ids[spdx_id], name))
            else:
                seen_ids[spdx_id] = name
        if not package.get("versionInfo"):
            add("%s has no versionInfo" % name)
        if not package.get("licenseConcluded") and not package.get("licenseDeclared"):
            add("%s has neither licenseConcluded nor licenseDeclared" % name)

    relationships = []
    for index, rel in enumerate(_sequence(doc.get("relationships"))):
        if not isinstance(rel, dict):
            # Report, not just filter: a dropped relationship silently changes
            # which packages look contained, so it must not pass unremarked.
            add("relationships[%d] is %s, expected an object"
                % (index, type(rel).__name__))
            continue
        relationships.append(rel)
    describes = [r for r in relationships if r.get("relationshipType") == "DESCRIBES"]

    # _sequence before indexing: an object here would raise KeyError on [0] and
    # a string would yield a single character. parsers._spdx_root_id guards the
    # same lookup; this is the second copy of that logic.
    described_ids = _sequence(doc.get("documentDescribes"))
    if "documentDescribes" in doc and not isinstance(doc.get("documentDescribes"), list):
        add("documentDescribes is %s, expected an array"
            % type(doc.get("documentDescribes")).__name__)

    if not describes and not described_ids:
        add("no DESCRIBES relationship and no documentDescribes -- "
            "the document does not say which package is the product")

    root_id = None
    if describes:
        root_id = describes[0].get("relatedSpdxElement")
    elif described_ids:
        root_id = described_ids[0]
    else:
        root_id = SPDX_ROOT_SPDXID

    contained = set()
    for rel in relationships:
        if rel.get("relationshipType") == "CONTAINS" and rel.get("spdxElementId") == root_id:
            contained.add(rel.get("relatedSpdxElement"))
    for package in packages:
        if not isinstance(package, dict):
            continue
        spdx_id = package.get("SPDXID")
        if spdx_id and spdx_id != root_id and spdx_id not in contained:
            add("%s (%s) has no CONTAINS relationship from the root package"
                % (package.get("name", "?"), spdx_id))

    if root is None:
        add("the described root package %r is not present in packages[]" % root_id)
    else:
        if expect_name and not _matches(root.name, expect_name):
            add_root("root package name is %r, expected %r" % (root.name, expect_name))
        if expect_version and not _matches(root.version, expect_version):
            add_root("root package versionInfo is %r, expected %r"
                     % (root.version, expect_version))

    for component in components:
        if lic.is_null(component.license):
            add("%s has no usable licence (%r)" % (component.name, component.license))

    return findings


def check_component_list(components, where):
    """Shared checks for the two plain-text formats."""
    findings = []
    if not components:
        return [Finding(where, "no components parsed")]
    seen = {}
    for component in components:
        if not component.name:
            findings.append(Finding(where, "a row has an empty name"))
        if not component.version:
            findings.append(Finding(where, "%s has an empty version" % component.name))
        if lic.is_null(component.license):
            findings.append(Finding(
                where, "%s has no usable licence (%r)" % (component.name, component.license)))
        key = component.key()
        if key in seen:
            findings.append(Finding(where, "duplicate row for %s %s" % key))
        seen[key] = True
    return findings
