#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *
import json
import os
import requests
import docker

container_name = 'mysql-router-test'
container_name_mysql_router = 'mysql-router'
network_name = 'innodbnet1'
docker_tag = os.getenv('ROUTER_VERSION')
docker_acc = os.getenv('DOCKER_ACC')
ps_version = os.getenv('PS_VERSION')
router_docker_image = docker_acc + "/" + "percona-mysql-router" + ":" + docker_tag
percona_docker_image = docker_acc + "/" + "percona-server" + ":" + ps_version

def create_network():
    subprocess.run(['docker', 'network', 'create', 'innodbnet'])

def create_mysql_config():
    for N in range(1, 5):
        with open(f'my{N}.cnf', 'w') as file:
            file.write(
                f"[mysqld]\n"
                f"plugin_load_add='group_replication.so'\n"
                f"server_id={(hash(str(time.time()) + str(N))) % 40 + 10}\n"
                f"binlog_checksum=NONE\n"
                f"enforce_gtid_consistency=ON\n"
                f"gtid_mode=ON\n"
                f"relay_log=mysql{N}-relay-bin\n"
                f"innodb_dedicated_server=ON\n"
                f"binlog_transaction_dependency_tracking=WRITESET\n"
                f"slave_preserve_commit_order=ON\n"
                f"slave_parallel_type=LOGICAL_CLOCK\n"
                f"transaction_write_set_extraction=XXHASH64\n"
            )

def start_mysql_containers():
    for N in range(1, 5):
        subprocess.run([
            'docker', 'run', '-d',
            f'--name=mysql{N}',
            f'--hostname=mysql{N}',
            '--net=innodbnet',
            '-v', f'my{N}.cnf:/etc/my.cnf',
            '-e', 'MYSQL_ROOT_PASSWORD=root', percona_docker_image
        ])
    time.sleep(60)

def create_new_user():
    for N in range(1, 5):
        subprocess.run([
            'docker', 'exec', f'mysql{N}',
            'mysql', '-uroot', '-proot',
            '-e', "CREATE USER 'inno'@'%' IDENTIFIED BY 'inno'; GRANT ALL privileges ON *.* TO 'inno'@'%' with grant option; FLUSH PRIVILEGES;"
        ])

def verify_new_user():
    for N in range(1, 5):
        subprocess.run([
            'docker', 'exec', f'mysql{N}',
            'mysql', '-uinno', '-pinno',
            '-e', "SHOW VARIABLES WHERE Variable_name = 'hostname';"
            '-e', "SELECT user FROM mysql.user where user = 'inno';"
        ])
    time.sleep(30)

def docker_restart():
    subprocess.run(['docker', 'restart', 'mysql1', 'mysql2', 'mysql3', 'mysql4'])
    time.sleep(10)

def create_cluster():
    subprocess.run([
        'docker', 'exec', 'mysql1',
        'mysqlsh', '-uinno', '-pinno', '--', 'dba', 'create-cluster', 'testCluster'
    ])

def add_slave():
    subprocess.run([
        'docker', 'exec', 'mysql1',
        'mysqlsh', '-uinno', '-pinno', '--',
        'cluster', 'add-instance', '--uri=inno@mysql3', '--recoveryMethod=incremental'
    ])
    time.sleep(10)
    subprocess.run([
        'docker', 'exec', 'mysql1',
        'mysqlsh', '-uinno', '-pinno', '--',
        'cluster', 'add-instance', '--uri=inno@mysql4', '--recoveryMethod=incremental'
    ])

@pytest.fixture(scope='module')
def inspect_data():
    dockerid = subprocess.check_output([
        'docker', 'run', '-d',
        '--name', 'mysql-router',
        '--net=innodbnet',
        '-e', 'MYSQL_HOST=mysql1',
        '-e', 'MYSQL_PORT=3306',
        '-e', 'MYSQL_USER=inno',
        '-e', 'MYSQL_PASSWORD=inno',
        '-e', 'MYSQL_INNODB_CLUSTER_MEMBERS=4',
        router_docker_image
    ]).decode().strip()
    inspect_data = json.loads(subprocess.check_output(['docker','inspect','mysql-router']))
    yield inspect_data[0]
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


create_network()
create_mysql_config()
start_mysql_containers()
create_new_user()
verify_new_user()
docker_restart()
create_cluster()
add_slave()
inspect_data()

class TestRouterEnvironment:
    def test_mysqlrouter_version(self, host):
        command = "mysqlrouter --version"
        output = host.check_output(command)
        assert ROUTER_VERSION in output

    def test_mysqlsh_version(self, host):
        command = "mysqlsh --version"
        output = host.check_output(command)
        assert PS_VERSION in output

    def test_mysqlrouter_directory_permissions(self, host):
        assert host.file('/var/lib/mysqlrouter').user == 'mysql'
        assert host.file('/var/lib/mysqlrouter').group == 'mysql'
        assert oct(host.file('/var/lib/mysqlrouter').mode) == '0o755'

    def test_mysql_user(self, host):
        assert host.user('mysql').exists
        assert host.user('mysql').uid == 1001
        assert host.user('mysql').gid == 1001
        assert 'mysql' in host.user('mysql').groups
 
    def test_mysql_user(self, host):
        mysql_user = host.user('mysql')
        print(f"Username: {mysql_user.name}, UID: {mysql_user.uid}")
        assert mysql_user.exists
        assert mysql_user.uid == 1001

    def test_mysqlrouter_ports(self, host):
        host.socket("tcp://6446").is_listening
        host.socket("tcp://6447").is_listening
        host.socket("tcp://64460").is_listening
        host.socket("tcp://64470").is_listening

    def test_mysqlrouter_config(self, host):
        assert host.file("/etc/mysqlrouter/mysqlrouter.conf").exists
        assert host.file("/etc/mysqlrouter/mysqlrouter.conf").user == "root"
        assert host.file("/etc/mysqlrouter/mysqlrouter.conf").group == "root"
        assert oct(host.file("/etc/mysqlrouter/mysqlrouter.conf").mode) == "0o644"    
