#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *


class PxcNode:
    def __init__(self, node_name, bootstrap_node=False):
        self.node_name = node_name
        self.bootstrap_node = bootstrap_node
        if bootstrap_node:
            self.docker_id = subprocess.check_output(
                ['docker', 'run', '--name', node_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd, 
                 '-e', 'CLUSTER_NAME='+cluster_name, '--net='+docker_network,'-d', docker_image]).decode().strip()
            time.sleep(30)
            subprocess.check_call(['mkdir', '-p', test_pwd+'/cert'])
            subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/ca.pem', test_pwd+'/cert'])
            subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/server-cert.pem', test_pwd+'/cert'])
            subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/server-key.pem', test_pwd+'/cert'])
            subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/client-cert.pem', test_pwd+'/cert'])
            subprocess.check_call(['docker', 'cp', node_name+':/var/lib/mysql/client-key.pem', test_pwd+'/cert'])
            subprocess.check_call(['chmod','a+r','-R', test_pwd+'/cert'])
        else:
            self.docker_id = subprocess.check_output(
            ['docker', 'run', '--name', node_name, '-e', 'MYSQL_ROOT_PASSWORD='+pxc_pwd, 
             '-e', 'CLUSTER_NAME='+cluster_name, '-e', 'CLUSTER_JOIN='+base_node_name+'1', 
             '--net='+docker_network,'-v', test_pwd+'/config:/etc/percona-xtradb-cluster.conf.d', 
             '-v', test_pwd+'/cert:/cert', '-d', docker_image]).decode().strip()
            time.sleep(30)
        self.ti_host = testinfra.get_host("docker://root@" + self.docker_id)

    def destroy(self):
        subprocess.check_call(['docker', 'rm', '-f', self.docker_id])
        if self.bootstrap_node:
            subprocess.check_call(['rm', '-rf', test_pwd+'/cert'])


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
    yield cluster
    for node in cluster:
        node.destroy()
    subprocess.check_call(['docker', 'network', 'rm', docker_network])


class TestCluster:
    @pytest.mark.parametrize("fname,soname,return_type", pxc_functions)
    def test_install_functions(self, cluster, fname, soname, return_type):
        cmd = cluster[0].ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "CREATE FUNCTION '+fname+' RETURNS '+return_type+' SONAME \''+soname+'\';"')
        assert cmd.succeeded
        for node in cluster:
            cmd = node.ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "SELECT name FROM mysql.func WHERE dl = \''+soname+'\';"')
            assert cmd.succeeded
            assert fname in cmd.stdout

    @pytest.mark.parametrize("pname,soname", pxc_plugins)
    def test_install_plugin(self, cluster, pname, soname):
        cmd = cluster[0].ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "INSTALL PLUGIN '+pname+' SONAME \''+soname+'\';"')
        assert cmd.succeeded
        for node in cluster:
            cmd = node.ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = \''+pname+'\';"')
            assert cmd.succeeded
            assert 'ACTIVE' in cmd.stdout

    def test_replication(self, cluster):
        cmd = cluster[0].ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "create database test;"')
        assert cmd.succeeded
        cmd = cluster[0].ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "create table t1 (a int primary key);" test')
        assert cmd.succeeded
        cmd = cluster[0].ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "insert into t1 values (1),(2),(3),(4);" test')
        assert cmd.succeeded
        for node in cluster:
            cmd = node.ti_host.run('mysql --user=root --password='+pxc_pwd+' -S/tmp/mysql.sock -s -N -e "select count(*) from test.t1;"')
            assert cmd.succeeded
            assert '4' in cmd.stdout
