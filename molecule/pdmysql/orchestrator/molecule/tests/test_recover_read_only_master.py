# import os
#
#
# import testinfra.utils.ansible_runner
#
# testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
#     os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
#
#
# def test_recover(host):
#     """
#     real_config_path="$(realpath $test_path/config.json)"
#         orchestrator-client -c api -path "reload-configuration?config=$real_config_path" | jq -r '.Code'
#
#     """
#     new_config = {
#       "RecoverNonWriteableMaster": True
#     }
#     set_new_config
#
#
# def test_all_instances_replicas(host):
#     cmd = "orchestrator-client -c api -path all-instances | jq '.[] | .Replicas | length'"
#     result = host.run(cmd)
#     assert result.rc == 0
#     result_stdout = result.stdout.split("\n")
#     assert 3 in result_stdout, result_stdout
#     assert 0 in result_stdout, result_stdout
#     zero_cts = 0
#     for val in result_stdout:
#         if val == zero_cts:
#             zero_cts += 1
#     assert zero_cts == 3, result_stdout
