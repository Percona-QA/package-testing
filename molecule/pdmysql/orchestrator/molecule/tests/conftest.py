import os
import pytest
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def clean_data_dir(host):
    pass


def init_data_dir(host):
    pass


def create_ci_user(host):
    pass


def create_hearbeat_user(host):
    pass


def set_global_master_ro(host):
    pass


def create_test_db(host):
    pass


def configure_slaves(host):
    pass


def start_slaves(host):
    pass





@pytest.fixture()
def redeploy(host):
    with host.sudo("root"):
        print("Killing mysql")
        host.run("killall -9 mysqld_safe")
        time.sleep(5)
        print("Starting master")
        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/master/my.sandbox.cnf &",
        )
        print("Starting node1")
        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node1/my.sandbox.cnf &",
        )
        print("Starting node2")

        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node2/my.sandbox.cnf &",
        )
        print("Starting node3")
        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node3/my.sandbox.cnf &",
        )
        time.sleep(10)
        print(host.run("ps aux | grep mysql").stdout)
