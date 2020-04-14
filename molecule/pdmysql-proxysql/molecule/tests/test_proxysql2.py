import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_proxysql2_version(host):
    cmd = 'proxysql --version'
    if os.lower() in ["redhat", "centos", 'rhel']:
        cmd_pkg = host.run("repoquery -i proxysql2")
    else:
        cmd_pkg = host.run("apt-cache showpkg proxysql2")
    print(cmd_pkg.stdout, cmd_pkg.stderr)
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert '2.0.10' in result.stdout, result.stdout
