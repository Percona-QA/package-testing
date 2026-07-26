import os
import time

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

VERSION = os.getenv("VERSION")


@pytest.fixture
def prepare_test(host):
    with host.sudo("root"):
        if VERSION.startswith("8.4."):
            cmd = (
                "mysql -e \"CREATE USER 'clustercheckuser'@'%' IDENTIFIED by 'clustercheckpassword!';"
                "GRANT PROCESS ON *.* TO 'clustercheckuser'@'%';"
                "CREATE USER 'haproxy_user'@'%' IDENTIFIED by '$3Kr$t';\""
            )
        else:
            cmd = (
                "mysql -e \"CREATE USER 'clustercheckuser'@'%' IDENTIFIED WITH mysql_native_password by 'clustercheckpassword!';"
                "GRANT ALL PRIVILEGES ON *.* TO 'clustercheckuser'@'%';"
                "CREATE USER 'haproxy_user'@'%' IDENTIFIED WITH mysql_native_password by '$3Kr$t';\""
            )

        result = host.run(cmd)
        assert result.rc == 0, result.stdout

        for restart_cmd in [
            "service xinetd restart",
            "service haproxy restart"
        ]:
            result = host.run(restart_cmd)
            assert result.rc == 0, result.stdout

        time.sleep(2)


def test_haproxy_service(host):
    assert host.service("haproxy").is_running


def test_haproxy_clustercheck(host, prepare_test):
    with host.sudo("root"):

        print("\n================ WSREP STATUS ================\n")
        wsrep = host.run(
            """mysql -Nse "
            SHOW STATUS LIKE 'wsrep_cluster_status';
            SHOW STATUS LIKE 'wsrep_local_state_comment';
            SHOW STATUS LIKE 'wsrep_ready';
            SHOW STATUS LIKE 'wsrep_connected';
            SHOW STATUS LIKE 'wsrep_cluster_size';
            SHOW STATUS LIKE 'wsrep_incoming_addresses';
            " """
        )
        print(wsrep.stdout)

        result = host.run("/usr/bin/clustercheck")

        print("\n================ CLUSTERCHECK ================\n")
        print(result.stdout)
        print(result.stderr)

        if result.rc != 0:

            print("\n================ MYSQL SERVICE ================\n")
            print(host.run("systemctl status mysql --no-pager -l").stdout)

            print("\n================ MYSQL ERROR LOG ================\n")
            print(host.run("tail -200 /var/log/mysql/error.log").stdout)

            print("\n================ HAPROXY STATUS ================\n")
            print(host.run("systemctl status haproxy --no-pager -l").stdout)

            print("\n================ HAPROXY BACKENDS ================\n")

            stats = host.run(
                "echo 'show stat' | socat stdio /var/lib/haproxy/stats"
            )

            if stats.rc == 0:
                print(stats.stdout)
            else:
                print("HAProxy stats socket unavailable")

        assert result.rc == 0, result.stdout
        assert "Percona XtraDB Cluster Node is synced." in result.stdout


def test_haproxy_connect(host):
    with host.sudo("root"):

        wait = 0
        timeout = 120

        cmd = (
            'mysql --port=9201 -h127.0.0.1 '
            '-uhaproxy_user -p$3Kr$t '
            '-e "SELECT VERSION();"'
        )

        while wait < timeout:
            result = host.run(cmd)

            if "Lost connection to MySQL server" not in result.stderr:
                break

            time.sleep(1)
            wait += 1

        result = host.run(cmd)

        if result.rc != 0:

            print("\n================ MYSQL CLIENT OUTPUT ================\n")
            print(result.stdout)
            print(result.stderr)

            print("\n================ WSREP STATUS ================\n")
            print(host.run(
                """mysql -Nse "
                SHOW STATUS LIKE 'wsrep_cluster_status';
                SHOW STATUS LIKE 'wsrep_local_state_comment';
                SHOW STATUS LIKE 'wsrep_ready';
                SHOW STATUS LIKE 'wsrep_connected';
                " """
            ).stdout)

            print("\n================ CLUSTERCHECK ================\n")
            print(host.run("/usr/bin/clustercheck").stdout)

            print("\n================ HAPROXY STATUS ================\n")
            print(host.run("systemctl status haproxy --no-pager -l").stdout)

            print("\n================ MYSQL ERROR LOG ================\n")
            print(host.run("tail -100 /var/log/mysql/error.log").stdout)

        assert result.rc == 0, result.stderr
        assert VERSION in result.stdout, result.stdout
