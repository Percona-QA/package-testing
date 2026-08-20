#!/usr/bin/env python3
"""
Assertions for the InnoDB cluster + router + sysbench + fault-tolerance
flow run by router-docker_test.sh (see /router-docker_test.sh at the
repo root). This file does no setup of its own: it expects that script
to have already built the mysql1-4 cluster, bootstrapped mysql-router,
loaded sbtest data via sysbench, and stopped mysql1 to exercise fault
tolerance. Run explicitly (not picked up by the router_docker job's
./run.sh with no args), e.g.:

    ./run.sh tests/test_router_cluster_ha.py
"""
import json
import subprocess

import pytest

EXPECTED_ROWS = 10000


def docker_exec(container, *args, timeout=30):
    return subprocess.run(
        ["sudo", "docker", "exec", container, *args],
        check=True, capture_output=True, text=True, timeout=timeout,
    ).stdout


def mysql_query(container, query, host_port_args=None, timeout=30):
    args = ["mysql", "-uinno", "-pinno"]
    if host_port_args:
        args += host_port_args
    args += ["-N", "-e", query]
    return docker_exec(container, *args, timeout=timeout).strip()


class TestSbtestDataViaRouter:
    def test_sbtest_schema_exists(self):
        out = mysql_query(
            "mysql-client",
            "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='sbtest'",
            host_port_args=["-h", "mysql-router", "-P", "6447"],
        )
        assert out == "1"

    def test_sbtest_row_count(self):
        out = mysql_query(
            "mysql-client",
            "SELECT COUNT(*) FROM sbtest.sbtest1",
            host_port_args=["-h", "mysql-router", "-P", "6447"],
        )
        assert int(out) == EXPECTED_ROWS


class TestReplicationSurvivors:
    """mysql1 is stopped by Fault_tolerance() before this suite runs, so
    only the surviving nodes are checked here."""

    @pytest.mark.parametrize("node", ["mysql2", "mysql3", "mysql4"])
    def test_row_count_replicated(self, node):
        out = mysql_query(node, "SELECT COUNT(*) FROM sbtest.sbtest1")
        assert int(out) == EXPECTED_ROWS


class TestFaultTolerance:
    def test_cluster_status_ok_partial(self):
        raw = docker_exec(
            "mysql-client", "mysqlsh", "-h", "mysql-router", "-P", "6446",
            "-uinno", "-pinno", "--", "cluster", "status",
            timeout=60,
        )
        # mysqlsh prints a banner line before the JSON payload
        payload = "\n".join(raw.splitlines()[1:])
        status = json.loads(payload)["defaultReplicaSet"]["status"]
        assert status == "OK_PARTIAL"
