import os
import pytest
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture()
def redeploy(host):
    with host.sudo("root"):
        host.run("killall -9 mysqld_safe")
        host.run("killall -9 mysqld")
        time.sleep(5)
        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/master/my.sandbox.cnf",
            background=True,
        )
        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node1/my.sandbox.cnf",
            background=True,
        )
        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node2/my.sandbox.cnf",
            background=True,
        )
        host.run(
            "mysqld_safe --defaults-file=/root/sandboxes/ci/node3/my.sandbox.cnf",
            background=True,
        )
        time.sleep(10)
        print(host.run("ps aux | grep mysql").stdout)

@pytest.fixture(scope="module")
def teardown(host):
    with host.sudo("root"):
        host.run_expect([0], "service orchestrator restart")
    time.sleep(5)
    yield
    cmd = "orchestrator-client -c relocate-replicas -i 127.0.0.1:10112 -d 127.0.0.1:10111"
    host.run_expect([0], cmd)
    with host.sudo("root"):
        host.run_expect([0], "service orchestrator restart")
    time.sleep(5)


def test_relocate_replicas(host, redeploy, teardown):
    cmd = "orchestrator-client -c relocate-replicas -i 127.0.0.1:10111 -d 127.0.0.1:10112 | sort"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "127.0.0.1:10113" in result.stdout, result.stdout
    assert "127.0.0.1:10114" in result.stdout, result.stdout
