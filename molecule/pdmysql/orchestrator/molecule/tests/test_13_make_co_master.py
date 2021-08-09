import os
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_make_co_master(host):
    expect_output = "127.0.0.1:10113<127.0.0.1:10111"
    cmd = "orchestrator-client -c make-co-master -i 127.0.0.1:10113"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expect_output in result.stdout, result.stdout


def test_is_co_master(host):
    time.sleep(3)
    cmd = "orchestrator-client -c api -path all-instances | jq -r '.[] | select(.IsCoMaster == true) | .Key.Port'"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "10111" in result.stdout, result.stdout
    assert "10113" in result.stdout, result.stdout


def test_topology(host):
    cmd = "orchestrator-client -c topology-tabulated -alias ci | cut -d'|' -f 1,2,3"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "+ 127.0.0.1:10111  |0s|ok" in result.stdout, result.stdout
    assert "  + 127.0.0.1:10112|0s|ok" in result.stdout, result.stdout
    assert "  + 127.0.0.1:10114|0s|ok" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10113  |0s|ok" in result.stdout, result.stdout


def test_fail_make_co_master(host):
    expect_failuer = "instance 127.0.0.1:10113 is already co master of 127.0.0.1:10111"
    cmd = "orchestrator-client -c make-co-master -i 127.0.0.1:10113"
    result = host.run(cmd)
    assert result.rc == 1, result.stdout
    assert expect_failuer in result.stderr, result.stderr


def test_relocate(host):
    expect_output = "127.0.0.1:10114<127.0.0.1:10113"
    cmd = "orchestrator-client -c relocate -i 127.0.0.1:10114 -d 127.0.0.1:10113"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expect_output in result.stdout, result.stdout


def test_topology_2(host):
    cmd = "orchestrator-client -c topology-tabulated -alias ci | cut -d'|' -f 1,2,3"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "+ 127.0.0.1:10111  |0s|ok" in result.stdout, result.stdout
    assert "  + 127.0.0.1:10112|0s|ok" in result.stdout, result.stdout
    assert "+ 127.0.0.1:10113  |0s|ok" in result.stdout, result.stdout
    assert "  + 127.0.0.1:10114|0s|ok" in result.stdout, result.stdout
