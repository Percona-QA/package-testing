#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
import shlex
from settings import *


class PxcNode:
    def __init__(self, node_name, bootstrap_node=False):
        self.node_name = node_name
        self.bootstrap_node = bootstrap_node
        if bootstrap_node:
            self.docker_id = subprocess.check_output(
                ['docker', 'run', '--name', node_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd, 
                 '-e', 'CLUSTER_NAME='+cluster_name, '-e', 'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport',
                 '--net='+docker_network, '-d', docker_image]).decode().strip()
            time.sleep(120)
            if pxc_version_major == "8.0":
                subprocess.check_call(['mkdir', '-p', test_pwd+'/cert'])
                subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/ca.pem', test_pwd+'/cert'])
                subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/server-cert.pem', test_pwd+'/cert'])
                subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/server-key.pem', test_pwd+'/cert'])
                subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/client-cert.pem', test_pwd+'/cert'])
                subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/client-key.pem', test_pwd+'/cert'])
                subprocess.check_call(['chmod','-R','a+r', test_pwd+'/cert'])
        else:
            if pxc_version_major == "8.0":
                self.docker_id = subprocess.check_output(
                ['docker', 'run', '--name', node_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd,
                '-e', 'CLUSTER_NAME='+cluster_name, '-e', 'CLUSTER_JOIN='+base_node_name+'1',
                '-e', 'PERCONA_TELEMETRY_DISABLE=1',
                '--net='+docker_network,'-v', test_pwd+'/config:/etc/percona-xtradb-cluster.conf.d',
                '-v', test_pwd+'/cert:/cert', '-d', docker_image]).decode().strip()
            else:
                self.docker_id = subprocess.check_output(
                ['docker', 'run', '--name', node_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd,
                '-e', 'CLUSTER_NAME='+cluster_name, '-e', 'CLUSTER_JOIN='+base_node_name+'1',
                '--net='+docker_network, '-d', docker_image]).decode().strip()
        self.ti_host = testinfra.get_host("docker://root@" + self.docker_id)

    def destroy(self):
        subprocess.check_call(['docker', 'rm', '-f', self.docker_id])
        if self.bootstrap_node:
            subprocess.check_call(['rm', '-rf', test_pwd+'/cert'])

    def run_query(self, query):
        cmd = self.ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e ' + shlex.quote(query))
        assert cmd.succeeded
        return cmd.stdout

@pytest.fixture(scope='module')
def cluster():
    cluster = []
    subprocess.check_call(['docker', 'network', 'create', docker_network])
    node1 = PxcNode(base_node_name+'1',True)
    cluster.append(node1)
    node2 = PxcNode(base_node_name+'2',False)
    cluster.append(node2)
    node3 = PxcNode(base_node_name+'3',False)
    cluster.append(node3)
    time.sleep(40)
    yield cluster
    for node in cluster:
        node.destroy()
    subprocess.check_call(['docker', 'network', 'rm', docker_network])
    
    def destroy(self):
        subprocess.check_call(['docker', 'rm', '-f', self.docker_id])


class TestCluster:
    @pytest.mark.parametrize("fname,soname,return_type", pxc_functions)
    def test_install_functions(self, cluster, fname, soname, return_type):
        cluster[0].run_query('CREATE FUNCTION '+fname+' RETURNS '+return_type+' SONAME "'+soname+'";')
        for node in cluster:
            output = node.run_query('SELECT name FROM mysql.func WHERE dl = "'+soname+'";')
            assert fname in output

    @pytest.mark.parametrize("pname,soname", pxc_plugins)
    def test_install_plugin(self, cluster, pname, soname):
        if pname == "group_replication":
            for node in cluster:
                node.run_query('set global pxc_strict_mode="PERMISSIVE";')
        cluster[0].run_query('INSTALL PLUGIN '+pname+' SONAME "'+soname+'";')
        for node in cluster:
            output = node.run_query('SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = "'+pname+'";')
            assert 'ACTIVE' in output

    def test_replication(self, cluster):
        cluster[0].run_query('create database test;')
        cluster[0].run_query('create table test.t1 (a int primary key);')
        cluster[0].run_query('insert into test.t1 values (1),(2),(3),(4);')
        for node in cluster:
            output = node.run_query('select count(*) from test.t1;')
            assert '4' in output

    def test_cluster_size(self, cluster):
        output = cluster[0].run_query('SHOW STATUS LIKE "wsrep_cluster_size";')
        assert output.split('\t')[1].strip() == "3"

    def test_telemetry_enabled(self, cluster):
        if pxc_version_major in ['5.7','5.6']:
            pytest.skip('telemetry was added in 8.0')
        else:
            assert cluster[0].ti_host.file('/usr/local/percona/telemetry_uuid').exists
            assert cluster[0].ti_host.file('/usr/local/percona/telemetry_uuid').contains('PRODUCT_FAMILY_PXC')
            assert cluster[0].ti_host.file('/usr/local/percona/telemetry_uuid').contains('instanceId:[0-9a-fA-F]\\{8\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{4\\}-[0-9a-fA-F]\\{12\\}$')

