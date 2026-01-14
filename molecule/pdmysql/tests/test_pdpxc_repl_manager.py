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

def test_script_run(host):
    cmd = "/usr/bin/replication_manager.sh"
    result = host.run(cmd)

    expected_errors = [
        "Access denied for user",
        "Plugin 'mysql_native_password' is not loaded",
    ]

    assert any(err in result.stdout for err in expected_errors), result.stdout
