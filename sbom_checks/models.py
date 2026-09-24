"""Data types shared by the SBOM parsers and checks.

Plain classes rather than dataclasses/NamedTuple defaults: RHEL-8 targets ship
python 3.6 and this package must import there unchanged.
"""


class Component(object):
    """One third-party component as described by an SBOM."""

    def __init__(self, name, version, license="", linkage="", origin=""):
        self.name = name
        self.version = version
        self.license = license
        self.linkage = linkage
        self.origin = origin

    def key(self):
        """Identity used when comparing formats: name is case-folded, version is not."""
        return (self.name.strip().lower(), self.version.strip())

    def __repr__(self):
        return "Component(%r, %r, %r)" % (self.name, self.version, self.license)

    def __eq__(self, other):
        return isinstance(other, Component) and self.key() == other.key()

    def __hash__(self):
        return hash(self.key())


class SbomSet(object):
    """The four files that make up one product SBOM, keyed by format.

    Any of the four may be None when the artifact ships an incomplete set --
    that is itself a finding, not a crash.
    """

    FORMATS = ("cdx", "spdx", "table", "licenses")

    def __init__(self, stem, paths=None, directory=None):
        self.stem = stem
        # Sets are identified by (directory, stem), never stem alone: two
        # directories under the package dir can hold files with identical names
        # (a leftover or a backup copy), and merging them would validate
        # CycloneDX from one and SPDX from the other.
        self.directory = directory
        self.paths = dict((f, None) for f in self.FORMATS)
        if paths:
            self.paths.update(paths)

    def label(self):
        if self.directory:
            return "%s in %s" % (self.stem, self.directory)
        return self.stem

    def present(self):
        return [f for f in self.FORMATS if self.paths.get(f)]

    def missing(self):
        return [f for f in self.FORMATS if not self.paths.get(f)]

    def is_empty(self):
        return not self.present()

    def __repr__(self):
        return "SbomSet(%r, present=%r)" % (self.label(), self.present())


class Finding(object):
    """A single problem. Checks return lists of these instead of raising, so one
    run reports every problem rather than stopping at the first."""

    def __init__(self, where, message):
        self.where = where
        self.message = message

    def __str__(self):
        return "[%s] %s" % (self.where, self.message)

    __repr__ = __str__


def render(findings):
    """Format findings for a pytest assertion message."""
    if not findings:
        return ""
    return "\n".join("  - %s" % f for f in findings)
