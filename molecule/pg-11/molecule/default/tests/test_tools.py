import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture()
def pgaudit(host):
    pass


@pytest.fixture()
def pgbackrest(host):
    pass


@pytest.fixture()
def ptrack(host):
    pass


@pytest.fixture()
def patroni(host):
    pass


def test_pgaudit_package(host):
    pkgn = ""
    if os == "RedHat":
        pkgn = "percona-pgaudit"
    elif os == "debian":
        pkgn = "percona-postgresql-11-pgaudit"
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed


def test_pgrepack_package(host):
    pkgn = ""
    if os == "RedHat":
        pkgn = "percona-pg_repack11"
    elif os == "debian":
        pkgn = "percona-postgresql-11-repack"
        pkg_dbgsym = host.package("percona-postgresql-11-repack-dbgsym")
        assert pkg_dbgsym.is_installed
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed


def test_pgbackrest_package(host):
    pkgn = ""
    if os == "RedHat":
        pkgn = "percona-pgbackrest"
    elif os == "debian":
        pkgn = "percona-postgresql-11-pgbackrest"
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
