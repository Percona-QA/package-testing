#!/usr/bin/env python3
import pytest
import testinfra
import os
import testinfra.utils.ansible_runner

# Get test hosts from Ansible inventory
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

# Define base directory used in tests
BASE_DIR = '/package-testing/binary-tarball-tests/pxc/PRO/Percona-XtraDB-Cluster-Pro'

#  FIXTURE: Prepares environment and creates directories
@pytest.fixture(scope='module')
def test_load_env_vars_define_in_test(host):
    
    with host.sudo():
        vars={'BASE_DIR':BASE_DIR}
        for var, value in vars.items():
            cmd=f"echo {var}={value} >> /etc/environment"
            host.run(cmd)
    cmd="groups $USER| awk -F' ' '{print $1$2$3}'"
    user_group=host.run(cmd).stdout.replace(" ", "").replace("\n","")
    with host.sudo():
        for dir in (f'./package-testing',BASE_DIR, BASE_DIR+'-minimal'):
            cmd=f"chown -R {user_group} {dir}"
            host.check_output(cmd)
            cmd=f"ls -l {dir}"
            host.run(cmd)

def test_regular_tarball(host, test_load_env_vars_define_in_test):
    cmd = "cd package-testing/binary-tarball-tests/pxc/PRO && ./run.sh"
    result = host.run(cmd)
    print(result.stdout)
    print(result.stderr)
    assert result.rc == 0, result.stdout

def test_minimal_tarball(host, test_load_env_vars_define_in_test):
    with host.sudo():
        cmd = f"sed -i 's|^\(BASE_DIR=.*\)/$|\1/-minimal|' /etc/environment"
        result = host.run(cmd)
    cmd = "cd package-testing/binary-tarball-tests/pxc/PRO && ./run.sh"
    result = host.run(cmd)
    print(result.stdout)
    print(result.stderr)
    assert result.rc == 0, result.stdout
