import os
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_no_errant(host):
    cmd = """
    orchestrator-client -c all-instances | while read i ; do
    orchestrator-client -c which-gtid-errant -i $i
    done | grep . || :
    """
    result = host.run(cmd)
    assert result.rc == 0
    time.sleep(3)


def test_inject_errant(host):
    setup_cmd = """
mysql -uci -pci -h 127.0.0.1 --port=10112 -e "update test.heartbeat set hint='gtid-errant'"
    """
    host.run_test(setup_cmd)
    time.sleep(3)
    expected_output = "10112"
    cmd = "orchestrator-client -c api -path all-instances | jq -r \'.[] | select(.GtidErrant != \"\") | .Key.Port\'"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout


def test_reset_master(host):
    expected_result = "127.0.0.1:10112"
    cmd = "orchestrator-client -c gtid-errant-reset-master -i 127.0.0.1:10112"
    result = host.run(cmd)
    assert expected_result in result.stdout, result.stdout


def test_no_errant_2(host):
    cmd = """
    orchestrator-client -c all-instances | while read i ; do
    orchestrator-client -c which-gtid-errant -i $i
    done | grep . || :
    """
    result = host.run(cmd)
    assert result.rc == 0
    time.sleep(3)


def test_inject_errant_2(host):
    expected_result = "10113"
    cmd = "orchestrator-client -c api -path all-instances | jq -r \'.[] | select(.GtidErrant != \"\") | .Key.Port\'"
    setup_1 = "orchestrator-client -c relocate -i 127.0.0.1:10114 -d 127.0.0.1:10113"
    setup_2 = """
    mysql -uci -pci -h 127.0.0.1 --port=10113 -e "update test.heartbeat set hint='gtid-errant'"
    """
    host.run_test(setup_1)
    host.run_test(setup_2)
    time.sleep(4)
    result = host.run(cmd)
    assert expected_result in result.stdout, result.stdout


def test_relocate_nested_replica(host):
    cmd = "orchestrator-client -c api -path all-instances | jq -r \'.[] | select(.GtidErrant != \"\") | .Key.Port\'"
    setup_cmd = "orchestrator-client -c relocate -i 127.0.0.1:10114 -d 127.0.0.1:10111"
    host.run_test(setup_cmd)
    time.sleep(3)
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert "10113" in result.stdout, result.stdout
    assert "10114" in result.stdout, result.stdout


def test_inject_empty(host):
    expected_output = "127.0.0.1:10113"
    cmd = "orchestrator-client -c gtid-errant-inject-empty -i 127.0.0.1:10113"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert expected_output in result.stdout, result.stdout
    time.sleep(3)


def test_no_errant_3(host):
    cmd = """
    orchestrator-client -c all-instances | while read i ; do
    orchestrator-client -c which-gtid-errant -i $i
    done | grep . || :
    """
    result = host.run(cmd)
    assert result.rc == 0
    time.sleep(3)
