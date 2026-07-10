"""Percona repository setup: port of package-testing/tasks/
enable_pxc{80,84}_{testing,main,experimental}_repo.yml (non-pro).
"""

from pyinfra.operations import apt, dnf, files, server

from tasks import system

PERCONA_RELEASE_DEB = (
    "https://repo.percona.com/apt/percona-release_latest.generic_all.deb"
)
PERCONA_RELEASE_RPM = (
    "https://repo.percona.com/yum/percona-release-latest.noarch.rpm"
)
# pxc84 repo tasks install this dedicated percona-release build on Amazon Linux
PERCONA_RELEASE_RPM_AMAZON = (
    "https://repo.percona.com/prel/yum/testing/2023/RPMS/noarch/"
    "percona-release-1.0-31.noarch.rpm"
)

YUM_REPO_LEFTOVERS = [
    "/etc/yum.repos.d/percona-release.repo",
    "/etc/yum.repos.d/percona-release.repo.rpmsave",
    "/etc/yum.repos.d/percona-original-release.repo",
    "/etc/yum.repos.d/percona-original-release.repo.rpmsave",
    "/etc/yum.repos.d/percona-original-testing.repo",
    "/etc/yum.repos.d/percona-original-testing.repo.rpmsave",
]

# percona-release commands per (product, repo), matching the ansible task
# files 1:1. Note: upstream enable_pxc84_experimental_repo.yml does not
# enable-only the pxc-84-lts experimental repo itself - kept as-is for parity.
ENABLE_COMMANDS = {
    ("pxc80", "testing"): [
        "percona-release enable-only pxc-80 testing",
        "percona-release enable tools release",
        "percona-release enable pxb-80 release",
        "percona-release enable pt release",
    ],
    ("pxc80", "main"): [
        "percona-release enable-only pxc-80 release",
        "percona-release enable pxb-80 release",
        "percona-release enable tools release",
        "percona-release enable pt release",
    ],
    ("pxc80", "experimental"): [
        "percona-release enable-only pxc-80 experimental",
        "percona-release enable tools experimental",
    ],
    ("pxc84", "testing"): [
        "percona-release enable-only pxc-84-lts testing",
        "percona-release enable pxb-84-lts testing",
    ],
    ("pxc84", "main"): [
        "percona-release enable-only pxc-84-lts release",
        "percona-release enable pxb-84-lts release",
    ],
    ("pxc84", "experimental"): [
        "percona-release enable tools experimental",
        "percona-release enable pxb-84-lts experimental",
    ],
}


def _remove_percona_repository():
    if system.os_family() == "debian":
        apt.packages(
            name="Remove the Percona apt main repository",
            packages=["percona-release"],
            present=False,
        )
    else:
        dnf.packages(
            name="Remove the Percona yum repositories",
            packages=["percona-release"],
            present=False,
        )
        for repo_file in YUM_REPO_LEFTOVERS:
            files.file(
                name="Remove {}".format(repo_file),
                path=repo_file,
                present=False,
            )


def _install_percona_release(product, install_repo):
    # the install method differs per repo task file:
    #   pxc80 testing/main: yum with disable_gpg_check
    #   pxc84 testing/main: rpm -ivh, with a dedicated prel build on Amazon
    #   experimental (both products): plain yum install, GPG check on
    if system.os_family() == "debian":
        apt.deb(
            name="Install percona repository package",
            src=PERCONA_RELEASE_DEB,
        )
    elif install_repo == "experimental":
        server.shell(
            name="Add the Percona yum repos",
            commands=["dnf install -y " + PERCONA_RELEASE_RPM],
        )
    elif product == "pxc84":
        if system.is_amazon():
            server.shell(
                name="Install percona release Amazon",
                commands=[
                    "rpm -ivh --nodigest --nofiledigest "
                    + PERCONA_RELEASE_RPM_AMAZON
                ],
            )
        else:
            server.shell(
                name="Install percona release RHEL",
                commands=[
                    "rpm -ivh --nodigest --nofiledigest " + PERCONA_RELEASE_RPM
                ],
            )
    else:
        server.shell(
            name="Add the Percona Release yum repo without GPG check",
            commands=["dnf install -y --nogpgcheck " + PERCONA_RELEASE_RPM],
        )


def enable_repo(product, install_repo):
    key = (product, install_repo)
    if key not in ENABLE_COMMANDS:
        raise ValueError("Unsupported product/repo combination: {}".format(key))

    _remove_percona_repository()

    if system.os_family() == "redhat" and system.major_version() == 8:
        server.shell(
            name="Disable the mysql module on RHEL 8",
            commands=["/usr/bin/dnf module disable mysql -y"],
        )

    _install_percona_release(product, install_repo)

    server.shell(
        name="Enable {} {} repos".format(product, install_repo),
        commands=ENABLE_COMMANDS[key],
    )

    if system.os_family() == "redhat":
        server.shell(
            name="Clean and update package cache",
            commands=["dnf clean all", "dnf makecache"],
        )
