import os
import pytest
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


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
