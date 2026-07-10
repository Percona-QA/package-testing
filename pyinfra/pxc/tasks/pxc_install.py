"""PXC package installation matrix (non-pro), ported from the install task
blocks of pxc{80,84}-{bootstrap,common}-install/tasks/main.yml.

Phases:
  initial          first install on the node (bootstrap and common)
  post_cluster     the re-install matrix the common nodes run after the
                   cluster-size check (pxc80 arm RPM gains xtrabackup here,
                   pxc84 deb drops percona-toolkit - kept as in molecule)
  telemetry_blocked  re-install with the telemetry server blocked
                   (percona-xtradb-cluster-full only)
"""

from pyinfra.operations import apt, dnf

from tasks import system

TELEMETRY_ENV = {
    "PERCONA_TELEMETRY_URL": "https://check-dev.percona.com/v1/telemetry/GenericReport"
}

XTRABACKUP = {"pxc80": "percona-xtrabackup-80", "pxc84": "percona-xtrabackup-84"}
FULL = "percona-xtradb-cluster-full"
TOOLKIT = "percona-toolkit"


def _packages(product, phase):
    if phase == "telemetry_blocked":
        return [FULL]

    xtrabackup = XTRABACKUP[product]
    debian = system.os_family() == "debian"

    if product == "pxc80":
        if debian:
            return [FULL, xtrabackup, TOOLKIT]
        if system.is_amazon():
            return [FULL]
        if system.is_arm():
            # arm RPM installs xtrabackup only in the post-cluster matrix
            return [FULL, xtrabackup] if phase == "post_cluster" else [FULL]
        return [FULL, TOOLKIT, xtrabackup]

    # pxc84
    if debian:
        return [FULL, xtrabackup] if phase == "post_cluster" else [FULL, xtrabackup, TOOLKIT]
    return [FULL, xtrabackup]


def install_pxc(product, phase="initial"):
    packages = _packages(product, phase)
    if system.os_family() == "debian":
        apt.packages(
            name="Install PXC deb packages ({})".format(phase),
            packages=packages,
            update=True,
            _env=TELEMETRY_ENV,
        )
    else:
        dnf.packages(
            name="Install PXC rpm packages ({})".format(phase),
            packages=packages,
            latest=True,
            _env=TELEMETRY_ENV,
        )
