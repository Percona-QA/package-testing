"""Per-product definitions.

Everything that differs between the products whose SBOM files these checks
validate lives here, so the discovery, parsing and audit code stays generic and
a second product is a new entry rather than a new copy of the checks.

Imports nothing from this package: config.py imports this module to resolve the
selected product, so an import in the other direction would be a cycle.

The default product is PXB, and nothing in the pipelines selects one -- so every
existing job keeps resolving to exactly the values these checks had before they
were made per-product.
"""

import re


class Product(object):
    """What the checks need to know about one product.

    A plain class rather than a dataclass: the library must import unchanged on
    RHEL-8 targets, which run python 3.6, and dataclasses arrived in 3.7.
    """

    def __init__(self, key, display_name, package_glob, main_package_re,
                 search_dirs, cdx_property_prefixes):
        self.key = key
        self.display_name = display_name
        # rpm/dpkg query pattern for the installed packages. Quoted literally
        # when passed to the shell (see discovery.installed_packages), so it
        # must stay a registry constant, never external input.
        self.package_glob = package_glob
        # Which installed package owns the SBOM, as opposed to -test, -dbg,
        # -debuginfo or client/shared subpackages.
        self.main_package_re = re.compile(main_package_re)
        # find(1) fallback when the package does not declare the files. Globs,
        # expanded by the shell, so the same registry-constant rule applies.
        self.search_dirs = tuple(search_dirs)
        # Prefixes of the CycloneDX component properties that carry linkage and
        # origin, e.g. "pxb:" -> "pxb:linkage".
        self.cdx_property_prefixes = tuple(cdx_property_prefixes)

    def __repr__(self):
        return "Product(%r)" % self.key


PXB = Product(
    key="pxb",
    display_name="Percona XtraBackup",
    package_glob="percona-xtrabackup*",
    main_package_re=r"^percona-xtrabackup(-pro)?(-\d+)?$",
    # Both rpm and deb install the files under the package's own directory,
    # e.g. /usr/share/percona-xtrabackup-97/sbom/.
    search_dirs=("/usr/share/percona-xtrabackup*",),
    cdx_property_prefixes=("pxb:",),
)

PS = Product(
    key="ps",
    display_name="Percona Server for MySQL",
    package_glob="percona-server*",
    # UNCONFIRMED -- no PS pipeline runs these checks yet, and the self-test
    # works in directory mode, so neither of the next two values is exercised.
    # PS ships percona-server-server / -client / -shared while the SBOM root is
    # named "percona-server"; which package owns the files, and where they are
    # installed, still needs confirming against a real PS package.
    main_package_re=r"^percona-server-server(-pro)?$",
    search_dirs=("/usr/share/percona-server*",),
    cdx_property_prefixes=("percona:",),
)

PRODUCTS = {p.key: p for p in (PXB, PS)}
DEFAULT = PXB.key


def get(key):
    """The product registered under key. An unknown key is a setup error, not
    something to fall back from: checking the wrong product's files would
    report findings that mean nothing."""
    try:
        return PRODUCTS[key]
    except KeyError:
        raise ValueError("unknown SBOM product %r; known: %s"
                         % (key, ", ".join(sorted(PRODUCTS))))


def all_cdx_property_prefixes():
    """Every registered property prefix, in registry order.

    The parser accepts any of these rather than only the selected product's:
    a component's linkage is its linkage whatever vendor prefix the generator
    used, and the PXB files are expected to move from "pxb:" to "percona:".
    """
    seen = []
    for product in (PXB, PS):
        for prefix in product.cdx_property_prefixes:
            if prefix not in seen:
                seen.append(prefix)
    return tuple(seen)
