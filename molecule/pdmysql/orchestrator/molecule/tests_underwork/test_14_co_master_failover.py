import os
import time

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# def test_make_co_master(host):
#     pass
#
#
# def test_relocate(host):
#     pass
#
#
# def test_failover(host):
#     pass
#
#
# def test_read_only(host):
#     pass
#
#
# def test_count_replicas(host):
#     pass
#
#
# def test_downtimed():
#     pass
#
#
# def test_analysis(host):
#     pass
