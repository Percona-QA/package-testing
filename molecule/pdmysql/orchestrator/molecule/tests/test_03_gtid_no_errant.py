import os


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


def test_reset_master(host):
    expect_failure = "gtid-errant-reset-master will not operate on 127.0.0.1:10112"
    cmd = "orchestrator-client -c gtid-errant-reset-master -i 127.0.0.1:10112"
    result = host.run(cmd)
    assert expect_failure in result.stdout, result.stdout


def test_inject_empty(host):
    cmd = "orchestrator-client -c gtid-errant-inject-empty -i 127.0.0.1:10113"
    expect_failure = "gtid-errant-inject-empty will not operate on 127.0.0.1:10113"
    result = host.run(cmd)
    assert expect_failure in result.stdout, result.stdout
