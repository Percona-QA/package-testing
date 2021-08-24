import os
import pytest
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture()
def redeploy(host):
    with host.sudo("root"):
        host.run_expect([0], "killall -9 mysqld_safe")
        host.run_expect([0], "killall -9 mysqld")
        host.run_expect([0], "killall -9 mysql")
        time.sleep(5)
        host.run_expect(
            [0],
            "mysqld_safe --defaults-file=/root/sandboxes/ci/master/my.sandbox.cnf &",
        )
        host.run_expect(
            [0],
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node1/my.sandbox.cnf &",
        )
        host.run_expect(
            [0],
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node2/my.sandbox.cnf &",
        )
        host.run_expect(
            [0],
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node3/my.sandbox.cnf &",
        )
        time.sleep(10)
