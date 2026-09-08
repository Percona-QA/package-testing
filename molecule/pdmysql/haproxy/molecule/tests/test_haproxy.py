import os
import time

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")

VERSION = os.getenv("VERSION")
HAPROXY_VERSION = os.getenv("HAPROXY_VERSION")


def dump_mysql_debug(host):
    print("\n========== MYSQLADMIN PING ==========")
    ping = host.run("mysqladmin ping || true")
    print(ping.stdout)
    print(ping.stderr)

    print("\n========== WSREP STATUS ==========")
    wsrep = host.run(
        """mysql -Nse "
        SHOW STATUS LIKE 'wsrep_cluster_status';
        SHOW STATUS LIKE 'wsrep_local_state_comment';
        SHOW STATUS LIKE 'wsrep_ready';
        SHOW STATUS LIKE 'wsrep_connected';
        SHOW STATUS LIKE 'wsrep_cluster_size';
        SHOW STATUS LIKE 'wsrep_incoming_addresses';
        " || true"""
    )
    print(wsrep.stdout)


def dump_haproxy_debug(host):
    print("\n========== HAPROXY BACKEND ==========")
    stats = host.run(
        "echo 'show stat' | socat stdio /var/lib/haproxy/stats || true"
    )
    print(stats.stdout)
    print(stats.stderr)


def dump_haproxy_service_debug(host):
    print("\n========== HAPROXY CONFIG CHECK ==========")
    check = host.run("haproxy -c -f /etc/haproxy/haproxy.cfg")
    print(check.stdout)
    print(check.stderr)

    print("\n========== HAPROXY JOURNAL ==========")
    journal = host.run("journalctl -xeu haproxy.service --no-pager -n 50")
    print(journal.stdout)


@pytest.fixture
def prepare_test(host):
    with host.sudo("root"):

        cmd = (
            "mysql -e \""
            "CREATE USER IF NOT EXISTS 'clustercheckuser'@'%' IDENTIFIED BY 'clustercheckpassword!';"
            "GRANT PROCESS ON *.* TO 'clustercheckuser'@'%';"
            "CREATE USER IF NOT EXISTS 'haproxy_user'@'%' IDENTIFIED BY '$3Kr$t';"
            "\""
        )

        result = host.run(cmd)

        if result.rc != 0:
            dump_mysql_debug(host)

        assert result.rc == 0, result.stderr

        print("\n========== BEFORE RESTART ==========")
        dump_mysql_debug(host)

        for svc in [
            "xinetd",
            "haproxy",
        ]:
            result = host.run(f"systemctl restart {svc} || service {svc} restart")

            if result.rc != 0 and svc == "haproxy":
                dump_haproxy_service_debug(host)

            assert result.rc == 0, result.stderr

        time.sleep(2)

        print("\n========== AFTER RESTART ==========")
        dump_mysql_debug(host)
        dump_haproxy_debug(host)


def test_haproxy_package_version(host):
    pkg = host.package("percona-haproxy")
    assert pkg.is_installed
    assert HAPROXY_VERSION in pkg.version, pkg.version


def test_haproxy_config_valid(host):
    with host.sudo("root"):
        result = host.run("haproxy -c -f /etc/haproxy/haproxy.cfg")

        print("\n========== HAPROXY CONFIG CHECK ==========")
        print(result.stdout)
        print(result.stderr)

        assert result.rc == 0, result.stdout + result.stderr


def test_haproxy_service(host):
    with host.sudo("root"):
        if not host.service("haproxy").is_running:
            dump_haproxy_service_debug(host)

        assert host.service("haproxy").is_running


def test_haproxy_clustercheck(host, prepare_test):
    with host.sudo("root"):

        result = host.run("/usr/bin/clustercheck")

        print("\n========== CLUSTERCHECK ==========")
        print(result.stdout)
        print(result.stderr)

        if result.rc != 0:
            dump_mysql_debug(host)
            dump_haproxy_debug(host)

        assert result.rc == 0, result.stdout
        assert "Percona XtraDB Cluster Node is synced." in result.stdout


def test_haproxy_connect(host):
    with host.sudo("root"):

        cmd = (
            'mysql --port=9201 '
            '-h127.0.0.1 '
            '-uhaproxy_user '
            '-p$3Kr$t '
            '-e "SELECT VERSION();"'
        )

        timeout = 120

        for _ in range(timeout):
            result = host.run(cmd)

            if result.rc == 0:
                break

            time.sleep(1)

        print("\n========== MYSQL CLIENT ==========")
        print(result.stdout)
        print(result.stderr)

        if result.rc != 0:
            dump_mysql_debug(host)
            dump_haproxy_debug(host)

        assert result.rc == 0, result.stderr
        assert VERSION in result.stdout
