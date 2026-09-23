import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')

def ip_hostnames(var):
    replaced_ip = os.environ.get(var, 'unused').replace('.', "-")
    return [
        "ip-" + replaced_ip,
        "ip-" + replaced_ip + ".us-west-2.compute.internal"
    ]

def assert_node_status(host, hostnames):
    topology_keys = ['"' + hostname + ':3306"' for hostname in hostnames]
    assert host.check_output(
        "mysqlsh root@localhost:6446 --password=Test1234# -- cluster status | "
        "jq -r '.defaultReplicaSet.topology[" + ', '.join(topology_keys) + "].status // empty'"
    ) == "ONLINE"

def test_mysqlsh_version(host):
    cmd = host.run("mysqlsh --version")
    assert os.environ['UPSTREAM_VERSION']+"-"+os.environ['PS_VERSION'] in cmd.stdout

def test_mysqlrouter_version(host):
    cmd = host.run("mysqlrouter --version")
    assert os.environ['UPSTREAM_VERSION']+"-"+os.environ['PS_VERSION'] in cmd.stdout
    assert os.environ['PS_REVISION'] in cmd.stdout

def test_mysqlrouter_ports(host):
    host.socket("tcp://6446").is_listening
    host.socket("tcp://6447").is_listening
    host.socket("tcp://64460").is_listening
    host.socket("tcp://64470").is_listening

def test_mysqlrouter_service(host):
    if host.system_info.distribution in ["redhat", "centos", 'rhel']:
        pytest.skip('Service not enabled on Centos.')
    else:
        assert host.service("mysqlrouter").is_running
#       assert host.service("mysqlrouter").is_enabled //disabled by upstream change

def test_mysqlrouter_config(host):
    assert host.file("/etc/mysqlrouter/mysqlrouter.conf").exists
    assert host.file("/etc/mysqlrouter/mysqlrouter.conf").user == "mysqlrouter"
    assert host.file("/etc/mysqlrouter/mysqlrouter.conf").group == "mysqlrouter"
    assert oct(host.file("/etc/mysqlrouter/mysqlrouter.conf").mode) == "0o600"

def test_packages(host):
    assert host.package("percona-mysql-router").is_installed
    assert os.environ['UPSTREAM_VERSION'] in host.package("percona-mysql-router").version
    assert host.package("percona-mysql-shell").is_installed
    assert os.environ['UPSTREAM_VERSION'] in host.package("percona-mysql-shell").version

#def test_database_checksums(host):
#    node1 = host.run("mysqlsh root@ps-node1:3306 --password=Test1234# --sql --database sbtest -e 'CHECKSUM TABLE sbtest1, sbtest2;'")
#    node2 = host.run("mysqlsh root@ps-node2:3306 --password=Test1234# --sql --database sbtest -e 'CHECKSUM TABLE sbtest1, sbtest2;'")
#    node3 = host.run("mysqlsh root@ps-node3:3306 --password=Test1234# --sql --database sbtest -e 'CHECKSUM TABLE sbtest1, sbtest2;'")
#    assert node1.stdout != ""
#    assert node1.stdout == node2.stdout
#    assert node1.stdout == node3.stdout

def test_cluster_status(host):
    assert host.check_output("mysqlsh root@localhost:6446 --password=Test1234# -- cluster status | jq -r '.defaultReplicaSet.status'") == "OK"

def test_node1_status(host):
    hostnames = ["ps-node1"] + ip_hostnames('PS_NODE1_IP')
    assert_node_status(host, hostnames)

def test_node2_status(host):
    hostnames = ["ps-node2"] + ip_hostnames('PS_NODE2_IP')
    assert_node_status(host, hostnames)

def test_node3_status(host):
    hostnames = ["ps-node3"] + ip_hostnames('PS_NODE3_IP')
    assert_node_status(host, hostnames)
