import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pgaudit_package(host):
    if os == "RedHat":
        pkg = host.package("percona-pgaudit")
    elif os == "debian":
        pkg = "percona-postgresql-11-pgaudit"
    assert pkg.is_installed


def test_pgrepack_package(host):
    if os == "RedHat":
        pkg = host.package("percona-pg_repack11")
        assert pkg.is_installed
    elif os == "debian":
        pkg = host.package("percona-postgresql-11-repack")
        assert pkg.is_installed
        pkg_dbgsym = host.package("percona-postgresql-11-repack-dbgsym")
        assert pkg_dbgsym


def test_pgbackrest_package(host):
    if os == "RedHat":
        pkg = host.package("percona-pgbackrest")
        assert pkg.is_installed
    elif os == "debian":
        pkg = host.package("percona-postgresql-11-pgbackrest")
    assert pkg.is_installed
