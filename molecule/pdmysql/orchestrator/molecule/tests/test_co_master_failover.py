# import os
# import pytest
# import time
#
# import testinfra.utils.ansible_runner
#
# testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
#     os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
#
#
# @pytest.fixture()
# def failover(host):
#     cmd = "mysqladmin -uci -pci -h 127.0.0.1 --port=10113 shutdown"
#     result = host.run(cmd)
#     assert result.rc == 0
#     time.sleep(20)
#
#
# @pytest.fixture()
# def cluster_master_path(host):
#     cluster_master_cmd = "orchestrator-client -c which-cluster-master -alias ci)"
#     cluster_master = host.run(cluster_master_cmd)
#     print(cluster_master.stdout)
#     assert cluster_master.rc == 0, cluster_master.stderr
#     return cluster_master.stdout.replace(":", "/")
#
#
# def test_make_co_master(host):
#     expected_output = "127.0.0.1:10113<127.0.0.1:10111"
#     cmd = "orchestrator-client -c make-co-master -i 127.0.0.1:10113"
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
#
#
# def test_relocate(host):
#     expected_output = "127.0.0.1:10114<127.0.0.1:10113"
#     cmd = "orchestrator-client -c relocate -i 127.0.0.1:10114 -d 127.0.0.1:10113"
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
#
#
# def test_failover(host):
#     cmd = "orchestrator-client -c which-cluster-master -alias ci"
#     expected_output = "127.0.0.1:10111"
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
#
#
# def test_read_only(host, cluster_master_path):
#     expected_output = "false"
#     cmd = f"orchestrator-client -c api -path instance/{cluster_master_path} | jq -r '.ReadOnly'"
#     result = host.run(cmd)
#     assert result.rc == 0
#     assert result.stdout == expected_output, result.stdout
#
#
# def test_count_replicas(host, cluster_master_path):
#     expected_output = "2"
#     cmd = f"orchestrator-client -c api -path instance/{cluster_master_path} | jq '.Replicas | length'"
#     result = host.run(cmd)
#     assert result.rc == 0
#     assert result.stdout == expected_output, result.stdout
#
#
# def test_downtimed(host):
#     expected_output = "10113"
#     cmd = """
#     orchestrator-client -c api -path downtimed | jq -r '.[] | select(.IsDowntimed==true and .DowntimeReason=="lost-in-recovery") | .Key.Port'
#     """
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
#
#
# def test_analysis(host):
#     expected_output = "DeadCoMaster"
#     cmd = "orchestrator-client -c replication-analysis | awk 'NF{ print $NF }'"
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
