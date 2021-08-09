import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_graceful_master_takeover_fail_no_target(host):
    expected_failure = "GracefulMasterTakeover: target instance not indicated"
    cmd = "orchestrator-client -c graceful-master-takeover -i 127.0.0.1:10111"
    result = host.run(cmd)
    assert result.rc == 1, result.stderr
    assert expected_failure in result.stderr, result.stderr
