import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_non_existing(host):
    expected_failure = "127.0.0.1:10999 must be directly replicating from the master"
    cmd = "orchestrator-client -c graceful-master-takeover -i 127.0.0.1:10111 -d 127.0.0.1:10999"
    result = host.run(cmd)
    assert result.rc == 1, result.stderr
    assert expected_failure in result.stderr, result.stderr


def test_non_direct(host):
    for i in range(10):
        host.run_expect(
            [0], "orchestrator-client -c relocate -i 127.0.0.1:10112 -d 127.0.0.1:10113"
        )
    expected_failure = "127.0.0.1:10112 must be directly replicating from the master"
    cmd = "orchestrator-client -c graceful-master-takeover -i 127.0.0.1:10111 -d 127.0.0.1:10112w"
    result = host.run(cmd)
    assert result.rc == 1, result.stderr
    assert expected_failure in result.stderr, result.stderr
    for i in range(10):
        host.run([0], "orchestrator-client -c relocate -i 127.0.0.1:10112 -d 127.0.0.1:10111")
