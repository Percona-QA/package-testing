import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_proxysql2_version(host):
    cmd = 'proxysql --version'
    result = host.run(cmd)
    print(result.stdout)
    assert result.rc == 0, result.stderr
    assert '8.0.18' in result.stdout, result.stdout
