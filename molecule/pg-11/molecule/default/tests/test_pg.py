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
def postgres_unit_file(host):
    cmd = "systemctl list-units| grep postgresql"
    return host.check_output(cmd)


@pytest.fixture()
def start_stop_postgresql(host):
    cmd = "sudo systemctl stop postgresql"
    result = host.run(cmd)
    assert result.rc == 0
    cmd = "sudo systemctl start postgresql"
    result = host.run(cmd)
    assert result.rc == 0
    cmd = "sudo systemctl status postgresql"
    return host.run(cmd)


@pytest.fixture()
def restart_postgresql(host):
    cmd = "sudo systemctl restart postgresql"
    result = host.run(cmd)
    assert result.rc == 0
    cmd = "sudo systemctl status postgresql"
    return host.run(cmd)


@pytest.mark.parametrize("package", DEB_PACKAGES)
def test_deb_package_is_installed(host, package):
    os = host.system_info.distribution
    print(os)
    if os == "RedHat":
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed


@pytest.mark.parametrize("package", RPM_PACKAGES)
def test_rpm_package_is_installed(host, package):
    os = host.system_info.distribution
    print(os)
    if os == "Debian":
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package(package)
    assert pkg.is_installed


def test_postgresql_client_version(host):
    pkg = "percona-platform-postgresql-11"
    if os == "RedHat":
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(pkg)
    assert "11" in pkg.version


def test_postgresql_version(host):
    pkg = "percona-platform-postgresql-client-11"
    if os == "RedHat":
        pkg = "percona-platform-postgresql11"
    pkg = host.package(pkg)
    assert "11" in pkg.version


def test_postgresql_is_running_and_enabled(host):
    if os == "RedHat":
        pytest.skip("This test only for Debian based platforms")
    postgresql = host.service("postgresql")
    assert postgresql.is_running
    assert postgresql.is_enabled


def test_postgres_unit_file(postgres_unit_file):
    assert "postgresql" in postgres_unit_file


def test_postgres_binary(host):
    pass


def test_postgres_server_version(host):
    cmd = "pg_config --version"
    result = host.check_output(cmd)
    assert "11" in result


def test_postgres_client_version(host):
    cmd = "psql --version"
    result = host.check_output(cmd)
    assert "11" in result


def test_start_stop_postgresql(start_stop_postgresql):
    assert start_stop_postgresql.rc == 0
    assert "active" in start_stop_postgresql.stdout
    assert not start_stop_postgresql.stderr


def test_restart_postgresql(restart_postgresql):
    assert restart_postgresql.rc == 0
    assert "active" in restart_postgresql.stdout
    assert not restart_postgresql.stderr

