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
# def test_takeover(host):
#     expected_output = "127.0.0.1:10112"
#     cmd = "orchestrator-client -c graceful-master-takeover-auto -i 127.0.0.1:10111"
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
#
#
# def test_is_replicating(host):
#     expected_output = "127.0.0.1:10111"
#     cmd = "orchestrator-client -c is-replicating -i 127.0.0.1:10111"
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
#
#
# def test_topology(host):
#     expected_output = """
# 127.0.0.1:10112
# + 127.0.0.1:10111
# + 127.0.0.1:10113
# + 127.0.0.1:10114
# """
#     time.sleep(3)
#     cmd = "orchestrator-client -c topology-tabulated -alias ci | cut -d'|' -f 1"
#     result = host.run(cmd)
#     assert expected_output in result.stdout, (result.stdout, result.stderr)
#
#
# def test_takeover_again(host):
#     pass
