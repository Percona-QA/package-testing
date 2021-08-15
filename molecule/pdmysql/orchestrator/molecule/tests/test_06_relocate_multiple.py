import os
import pytest
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture(scope="module")
def teardown(host):
    yield
    host.run_expect([0], "orchestrator-client -c relocate -i 127.0.0.1:10113 -d 127.0.0.1:10111")
    host.run_expect([0], "orchestrator-client -c relocate -i 127.0.0.1:10114 -d 127.0.0.1:10111")
    time.sleep(10)


def test_relocate_1(host):
    expected_result = "127.0.0.1:10113<127.0.0.1:10112"
    cmd = "orchestrator-client -c relocate -i 127.0.0.1:10113 -d 127.0.0.1:10112"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_result in result.stdout, result.stdout


def test_relocate_2(host):
    expected_result = "127.0.0.1:10114<127.0.0.1:10112"
    cmd = "orchestrator-client -c relocate -i 127.0.0.1:10114 -d 127.0.0.1:10112"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_result in result.stdout, result.stdout


def test_relocate_3(host):
    expected_result = "127.0.0.1:10114<127.0.0.1:10113"
    cmd = "orchestrator-client -c relocate -i 127.0.0.1:10114 -d 127.0.0.1:10113"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_result in result.stdout, result.stdout


def test_topology(host, teardown):
    _ = teardown
    cmd = "orchestrator-client -c topology-tabulated -alias ci | cut -d'|' -f 1,2,3"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "127.0.0.1:10111      |0s|ok" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10112    |0s|ok" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10113  |0s|ok" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10114|0s|ok" in result.stdout, result.stdout
