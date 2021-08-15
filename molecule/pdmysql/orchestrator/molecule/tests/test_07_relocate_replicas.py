import os
import pytest
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture(scope="module")
def teardown(host):
    yield
    cmd = "orchestrator-client -c relocate-replicas -i 127.0.0.1:10112 -d 127.0.0.1:10111"
    host.run_expect([0], cmd)
    time.sleep(10)



def test_relocate_replicas(host):
    cmd = "orchestrator-client -c relocate-replicas -i 127.0.0.1:10111 -d 127.0.0.1:10112 | sort"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "127.0.0.1:10113" in result.stdout, result.stdout
    assert "127.0.0.1:10114" in result.stdout, result.stdout
