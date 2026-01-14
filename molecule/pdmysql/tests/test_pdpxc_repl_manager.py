import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

PACKAGES = ['percona-replication-manager']

REPL_MANAGER_VERSION = os.environ.get("REPL_MANAGER_VERSION")

@pytest.mark.parametrize("package", PACKAGES)
def test_check_package(host, package):
    pkg = host.package(package)
    assert pkg.is_installed
    assert REPL_MANAGER_VERSION in pkg.version, pkg.version

def test_prepare_mysql_auth(host):
    host.run(
        "mysql -e \"ALTER USER 'root'@'localhost' "
        "IDENTIFIED WITH caching_sha2_password;\""
    )

def test_script_run(host):
    result = host.run("/usr/bin/replication_manager.sh")
    assert result.rc == 0, result.stdout
