#!/usr/bin/env python3
import pytest
import testinfra
import os
import testinfra.utils.ansible_runner

# Get test hosts from Ansible inventory
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

#  FIXTURE: Prepares environment and creates directories



@pytest.fixture(scope='module')
def base_dir(host):
    result = host.run("source /etc/environment && echo $BASE_DIR")
    base_dir_value = result.stdout.strip()
    if not base_dir_value or base_dir_value.lower() == "none":
        raise ValueError(f"BASE_DIR is not set correctly on remote. Got: {base_dir_value}")
    return base_dir_value

@pytest.fixture(scope='module')
def test_load_env_vars_define_in_test(host, base_dir):
    with host.sudo():
        # Clean up any old BASE_DIR lines just in case
        host.run("sed -i '/^BASE_DIR=/d' /etc/environment")
        host.run(f"echo BASE_DIR={base_dir} >> /etc/environment")

    # Get current user group
    cmd = "groups $USER | awk -F' ' '{print $1$2$3}'"
    user_group = host.run(cmd).stdout.replace(" ", "").replace("\n", "")

    with host.sudo():
        for dir in ("./package-testing", base_dir):
            if host.file(dir).exists:
                host.check_output(f"chown -R {user_group} {dir}")
                host.run(f"ls -l {dir}")


# ✅ Final test: runs the tarball test script
def test_proxysql_tarball(host, test_load_env_vars_define_in_test):
    cmd = "cd package-testing/binary-tarball-tests/proxysql && chmod +x run.sh && ./run.sh"
    result = host.run(cmd)
    print(result.stdout)
    print(result.stderr)
    assert result.rc == 0, result.stdout
