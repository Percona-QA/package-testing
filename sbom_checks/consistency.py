"""Cross-format consistency.

A product's four SBOM files come from one generator in one run, so they must agree.
This is what catches a generator that updates one output and forgets another.

Verified against the real prototype set: all four formats yield identical
18-element (name, version, licence) data once whitespace is stripped. So strict
set equality on component identity is the correct, non-flaky assertion.

Three tiers, reported separately so a licence-vocabulary difference can never
masquerade as a missing component:

  A  component identity     strict set equality, always enforced
  B  licence presence       every component names a licence, always enforced
  C  licence equivalence    normalised comparison, overlap by default
"""

from .models import Finding
from . import licenses as lic

FORMAT_LABELS = {
    "cdx": ".cdx.json",
    "spdx": ".spdx.json",
    "table": ".sbom.txt",
    "licenses": ".licenses.txt",
}


def _label(fmt):
    return FORMAT_LABELS.get(fmt, fmt)


def check_identity(by_format):
    """Tier A: every format must describe exactly the same (name, version) set."""
    findings = []
    formats = sorted(by_format)
    if len(formats) < 2:
        return findings

    keysets = dict((f, set(c.key() for c in by_format[f])) for f in formats)

    counts = dict((f, len(by_format[f])) for f in formats)
    if len(set(counts.values())) > 1:
        findings.append(Finding("consistency", "component counts differ: %s" % ", ".join(
            "%s=%d" % (_label(f), counts[f]) for f in formats)))

    reference = formats[0]
    for fmt in formats[1:]:
        only_ref = keysets[reference] - keysets[fmt]
        only_other = keysets[fmt] - keysets[reference]
        for name, version in sorted(only_ref):
            findings.append(Finding("consistency", "%s %s is in %s but missing from %s"
                                    % (name, version, _label(reference), _label(fmt))))
        for name, version in sorted(only_other):
            findings.append(Finding("consistency", "%s %s is in %s but missing from %s"
                                    % (name, version, _label(fmt), _label(reference))))
    return findings


def check_license_presence(by_format):
    """Tier B: no component may be shipped without a stated licence."""
    findings = []
    for fmt in sorted(by_format):
        for component in by_format[fmt]:
            if lic.is_null(component.license):
                findings.append(Finding(
                    "consistency",
                    "%s states no licence for %s %s (%r)"
                    % (_label(fmt), component.name, component.version, component.license)))
    return findings


def check_license_equivalence(by_format, strict=False):
    """Tier C: the same component must carry an equivalent licence everywhere."""
    findings = []
    formats = sorted(by_format)
    if len(formats) < 2:
        return findings

    indexed = {}
    for fmt in formats:
        indexed[fmt] = dict((c.key(), c) for c in by_format[fmt])

    shared = set(indexed[formats[0]])
    for fmt in formats[1:]:
        shared &= set(indexed[fmt])

    for key in sorted(shared):
        values = {}
        for fmt in formats:
            values[fmt] = indexed[fmt][key].license
        reference_fmt = formats[0]
        for fmt in formats[1:]:
            if not lic.equivalent(values[reference_fmt], values[fmt], strict=strict):
                findings.append(Finding(
                    "consistency",
                    "%s %s licence disagrees: %s says %r, %s says %r"
                    % (key[0], key[1], _label(reference_fmt), values[reference_fmt],
                       _label(fmt), values[fmt])))
                break
    return findings


def check_all(by_format, strict_licenses=False):
    findings = []
    findings.extend(check_identity(by_format))
    findings.extend(check_license_presence(by_format))
    findings.extend(check_license_equivalence(by_format, strict=strict_licenses))
    return findings


def summary(by_format):
    """One-line description of what was compared, for the test output."""
    return ", ".join("%s=%d" % (_label(f), len(by_format[f])) for f in sorted(by_format))
