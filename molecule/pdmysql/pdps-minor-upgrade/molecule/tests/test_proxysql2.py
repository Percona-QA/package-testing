import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_package_is_installed(host):
    pkg = host.package('proxysql2')
    assert pkg.is_installed


def test_proxysql2_version(host):
    cmd = 'proxysql --version'
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert '2.0.14' in result.stdout, result.stdout
