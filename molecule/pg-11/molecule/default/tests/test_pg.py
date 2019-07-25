import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEB_PACKAGES = ["percona-platform-postgresql-11", "percona-platform-postgresql-client", "percona-platform-postgresql",
                "percona-platform-postgresql-client-11", "percona-platform-postgresql-client-common",
                "percona-platform-postgresql-contrib", "percona-platform-postgresql-doc",
                "percona-platform-postgresql-doc-11", "percona-platform-postgresql-plperl-11",
                "percona-platform-postgresql-plpython-11", "percona-platform-postgresql-plpython3-11",
                "percona-platform-postgresql-pltcl-11", "percona-platform-postgresql-all"]

RPM_PACKAGES = ["percona-platform-postgresql11", "percona-platform-postgresql11-contrib",
                "percona-platform-postgresql11-debuginfo", "percona-platform-postgresql11-devel",
                "percona-platform-postgresql11-docs", "percona-platform-postgresql11-libs",
                "percona-platform-postgresql11-plperl", "percona-platform-postgresql11-plpython",
                "percona-platform-postgresql11-pltcl", "percona-platform-postgresql11-server",
                "percona-platform-postgresql11-test"]


@pytest.fixture()
def start_postgresql(host):
    pass


@pytest.fixture()
def stop_postgresql(host):
    pass


@pytest.fixture()
def restart_postgresql():
    pass


@pytest.mark.parametrize("package", DEB_PACKAGES)
def test_deb_package_is_installed(host, package):
    os = host.system_info.distribution
    if os == "RedHat":
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed


@pytest.mark.parametrize("package", RPM_PACKAGES)
def test_deb_package_is_installed(host, package):
    os = host.system_info.distribution
    if os == "RedHat":
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed


def test_postgresql_is_running_and_enabled(host):
    if os == "RedHat":
        pytest.skip("This test only for Debian based platforms")
    postgresql = host.service("postgresql")
    assert postgresql.is_running
    assert postgresql.is_enabled


def test_postgres_binary(host):
    pass


def test_postgres_server_version(host):
    pass


def test_postgres_client_version(host):
    pass


def test_start_postgresql(host, start_postgresql):
    pass


def test_stop_postgresql(host, stop_postgresql):
    pass


def test_restart_service(host, restart_postgresql):
    pass

