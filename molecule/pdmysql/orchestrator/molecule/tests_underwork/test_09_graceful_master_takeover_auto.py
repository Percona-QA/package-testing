import os
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_takeover(host):
    expected_output = "127.0.0.1:10112"
    cmd = "orchestrator-client -c graceful-master-takeover-auto -i 127.0.0.1:10111"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout


def test_is_replicating(host):
    expected_output = "127.0.0.1:10111"
    cmd = "orchestrator-client -c is-replicating -i 127.0.0.1:10111"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout


def test_topology(host):
    time.sleep(3)
    cmd = "orchestrator-client -c topology-tabulated -alias ci | cut -d'|' -f 1"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "127.0.0.1:10112" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10111" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10113" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10114" in result.stdout, result.stdout


def test_takeover_2(host):
    expected_output = "127.0.0.1:10113"
    cmd = "orchestrator-client -c graceful-master-takeover-auto --alias ci -d 127.0.0.1:10113"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout


def test_is_replicating_2(host):
    expected_output = "127.0.0.1:10111"
    cmd = "orchestrator-client -c is-replicating -i 127.0.0.1:10111"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout


def test_topology_2(host):
    time.sleep(3)
    cmd = "orchestrator-client -c topology-tabulated -alias ci | cut -d'|' -f 1"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "127.0.0.1:10112" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10111" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10113" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10114" in result.stdout, result.stdout


def test_takeover_3(host):
    host.run_expect([0], "orchestrator-client -c relocate -i 127.0.0.1:10112 -d 127.0.0.1:10111")
    expected_output = "127.0.0.1:10111"
    cmd = "orchestrator-client -c graceful-master-takeover-auto --alias ci"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout


def test_is_replicating_3(host):
    expected_output = "127.0.0.1:10112"
    cmd = "orchestrator-client -c is-replicating -i 127.0.0.1:10112"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout
