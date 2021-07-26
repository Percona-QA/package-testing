import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_all_instances(host):
    cmd = "orchestrator-client -c all-instances | sort"
    expected_output = """
    127.0.0.1:10111
127.0.0.1:10112
127.0.0.1:10113
127.0.0.1:10114"""
    pass

def test_all_instances_replicas(host):
    """3
0
0
0"""
    cmd = "orchestrator-client -c api -path all-instances | jq '.[] | .Replicas | length'"

def test_analysis_locked_semi_sync_master(host):
    pass

def test_co_master_failover(host):
    pass

def test_graceful_master_takeover_auto(host):
    pass


def test_graceful_master_takeover_fail_cross_region(host):
    pass


def test_graceful_master_takeover_fail_no_target(host):
    pass


def test_graceful_master_takeover_fail_non_direct_replica(host):
    pass


def test_graceful_master_takeover(host):
    pass


def test_gtid_errant(host):
    pass


def test_gtid_no_errant(host):
    pass

def test_intermediate_master_failover(host):
    pass


def test_make_co_master(host):
    pass


def test_master_failover_candidate_lag_cross_datacenter(host):
    pass


def test_master_failover_candidate_lag_cross_region(host):
    pass


def test_master_failover_candidate_lag(host):
    pass


def test_master_failover_candidate(host):
    pass


def test_master_failover_fail_promotion_lag_minutes_failure(host):
    pass


def test_master_failover_fail_promotion_lag_minutes_success(host):
    pass


def test_master_failover_lost_replicas(host):
    pass


def test_master_failover(host):
    pass


def test_recover_read_only_master(host):
    pass


def test_relocate_multiple(host):
    pass


def test_relocate_replicas(host):
    pass


def test_relocate_single(host):
    pass



