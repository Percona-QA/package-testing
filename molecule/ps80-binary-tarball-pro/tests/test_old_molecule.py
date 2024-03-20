#!/usr/bin/env python3
import pytest
import testinfra
import os

import testinfra.utils.ansible_runner
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

BASE_DIR='/usr/percona-server'

@pytest.fixture(scope='module')
def test_load_env_vars_define_in_test(host):
    with host.sudo():
        vars={'BASE_DIR':BASE_DIR,'PS_VERSION':os.getenv('PS_VERSION'),'PS_REVISION':os.getenv('PS_REVISION'),'PRO':os.getenv('PRO'),'FIPS_SUPPORTED':os.getenv('FIPS_SUPPORTED')}
        for var, value in vars.items():
            cmd=f"echo {var}={value} >> /etc/environment"
            host.run(cmd)
    cmd="groups $USER| awk -F' ' '{print $1$2$3}'"
    user_group=host.run(cmd).stdout.replace(" ", "").replace("\n","")
    with host.sudo():
        for dir in (f'./package-testing',BASE_DIR, BASE_DIR+'-minimal', BASE_DIR+'-debug'):
            cmd=f"chown -R {user_group} {dir}"
            host.check_output(cmd)
            cmd=f"ls -l {dir}"
            host.run(cmd)

def test_regular_tarball(host, test_load_env_vars_define_in_test):
    cmd = "cd ~/package-testing/binary-tarball-tests/ps/ && ./run.sh"
    result = host.run(cmd)
    print(result.stdout)
    print(result.stderr)
    assert result.rc == 0, result.stdout

def test_minimal_tarball(host, test_load_env_vars_define_in_test):
    with host.sudo():
        cmd = f"sed -i 's/\\(BASE_DIR.*\\)/\\1-minimal/g' /etc/environment"
        result = host.run(cmd)
    cmd = "cd ~/package-testing/binary-tarball-tests/ps/ && ./run.sh"
    result = host.run(cmd)
    print(result.stdout)
    print(result.stderr)
    assert result.rc == 0, result.stdout

def test_debug_tarball(host, test_load_env_vars_define_in_test):
    with host.sudo():
        cmd = f"sed -i 's/\\(BASE_DIR.*\\)-minimal/\\1-debug/g' /etc/environment"
        result = host.run(cmd)
        cmd=f"echo DEBUG='yes' >> /etc/environment"
        result = host.run(cmd)
    cmd = "cd ~/package-testing/binary-tarball-tests/ps/ && ./run.sh"
    result = host.run(cmd)
    print(result.stdout)
    print(result.stderr)
    assert result.rc == 0, result.stdout