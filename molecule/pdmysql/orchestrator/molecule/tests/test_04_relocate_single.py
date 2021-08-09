import os


import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_relocate_single(host):
    expected_output = "127.0.0.1:10113<127.0.0.1:10112"
    cmd = "orchestrator-client -c relocate -i 127.0.0.1:10113 -d 127.0.0.1:10112"
    result = host.run(cmd)
    assert expected_output in result.stdout, result.stdout
    host.run_test("orchestrator-client -c relocate -i 127.0.0.1:10113 -d 127.0.0.1:10111")
