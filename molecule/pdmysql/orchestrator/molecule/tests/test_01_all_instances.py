import os


import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_all_instances(host):
    cmd = "orchestrator-client -c all-instances | sort"
    result = host.run(cmd)
    assert result.rc == 0
    assert "127.0.0.1:10111" in result.stdout
    assert "127.0.0.1:10112" in result.stdout
    assert "127.0.0.1:10113" in result.stdout
    assert "127.0.0.1:10114" in result.stdout


def test_all_instances_replicas(host):
    cmd = "orchestrator-client -c api -path all-instances | jq '.[] | .Replicas | length'"
    result = host.run(cmd)
    assert result.rc == 0
    result_stdout = result.stdout.split("\n")
    assert 3 in result_stdout, result_stdout
    assert 0 in result_stdout, result_stdout
    zero_cts = 0
    for val in result_stdout:
        if val == zero_cts:
            zero_cts += 1
    assert zero_cts == 3, result_stdout
