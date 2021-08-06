import os
import pytest
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture
def semi_sync_master(host):
    host.run_expect([0], "orchestrator-client -c enable-semi-sync-master -i 127.0.0.1:10111")
    time.sleep(2)
    host.run_expect([0], "orchestrator-client -c enable-semi-sync-replica -i 127.0.0.1:10112")
    time.sleep(2)
    host.run_expect([0], "orchestrator-client -c disable-semi-sync-replica -i 127.0.0.1:10112")
    time.sleep(5)
    yield
    all_instances = host.run("orchestrator-client -c all-instances")
    all_instances_stdout = all_instances.stdout.split("\n")
    print(all_instances_stdout)
    for instance in all_instances_stdout[0: -1]:
        host.run_expect([0], f"orchestrator-client -c disable-semi-sync-master -i {instance}")
        host.run_expect([0], f"orchestrator-client -c disable-semi-sync-replica -i {instance}")


@pytest.fixture
def semi_sync_analysis_locked(semi_sync_master):
    time.sleep(15)


def test_analysis_locked_hypothesis(host, semi_sync_master):
    _ = semi_sync_master
    cmd = "orchestrator-client -c replication-analysis"
    result = host.run(cmd)
    expected_output = "127.0.0.1:10111 (cluster 127.0.0.1:10111): LockedSemiSyncMasterHypothesis"
    assert expected_output in result.stdout, result.stdout


def test_analysis_locked(host, semi_sync_analysis_locked):
    _ = semi_sync_analysis_locked
    expected_output = "127.0.0.1:10111 (cluster 127.0.0.1:10111): LockedSemiSyncMaster"
    cmd = "orchestrator-client -c replication-analysis"
    result = host.run(cmd)
    assert expected_output in result.stdout, result.stdout
