#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
import time
from settings import *
import os
import requests
import docker

ps_docker_product = 'percona-server'
ps_docker_tag = os.getenv('PS_VERSION')
ps_docker_image = docker_acc + "/" + ps_docker_product + ":" + ps_docker_tag

orch_container = 'orchestartor-test-docker'
source_ps_container = 'source-ps-docker'
replica_ps_container = 'replica-ps-docker'
network_name = 'orchestrator'

ps_password ='secret'

source_attr_reference = ({"key_path": ["Key", "Hostname"], "expected_value": source_ps_container},
                         {"key_path": ["Version"], "expected_value": ps_docker_tag},
                         {"key_path": ["SlaveHosts", "Hostname"], "expected_value": replica_ps_container},
                         {"key_path": ["IsLastCheckValid"], "expected_value": True},
                         {"key_path": ["IsUpToDate"], "expected_value": True},)

replica_attr_reference = ({"key_path": ["Key", "Hostname"], "expected_value": replica_ps_container},
                          {"key_path": ["Version"], "expected_value": ps_docker_tag},
                          {"key_path": ["MasterKey", "Hostname"], "expected_value": source_ps_container},
                          {"key_path": ["ReplicationSQLThreadRuning"], "expected_value": True},
                          {"key_path": ["ReplicationIOThreadRuning"], "expected_value": True},
                          {"key_path": ["IsLastCheckValid"], "expected_value": True},
                          {"key_path": ["IsUpToDate"], "expected_value": True},)

replica_stopped_attr_reference = ({"key_path": ["Key", "Hostname"], "expected_value": replica_ps_container},
                                  {"key_path": ["MasterKey", "Hostname"], "expected_value": source_ps_container},
                                  {"key_path": ["ReplicationSQLThreadRuning"], "expected_value": False},
                                  {"key_path": ["ReplicationIOThreadRuning"], "expected_value": False},
                                  {"key_path": ["IsLastCheckValid"], "expected_value": True},
                                  {"key_path": ["IsUpToDate"], "expected_value": True},)

@pytest.fixture(scope='module')
def orchestrator_ip():
    docker_client = docker.from_env()
    docker_client.networks.create(network_name)
    docker_client.containers.run(docker_image, name=orch_container, network=network_name, detach=True)
    source_container = docker_client.containers.run(ps_docker_image, '--log-error-verbosity=3 --report_host='+source_ps_container+' --max-allowed-packet=134217728',
                        name=source_ps_container, environment=["MYSQL_ROOT_PASSWORD="+ps_password, "PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport"], network=network_name, detach=True)
    replica_container = docker_client.containers.run(ps_docker_image, '--log-error-verbosity=3 --report_host='+replica_ps_container+' --max-allowed-packet=134217728 --server-id=2',
                        name=replica_ps_container, environment=["MYSQL_ROOT_PASSWORD="+ps_password, "PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport"], network=network_name, detach=True)
    #wait till replica mysql is up and listening on port
    time.sleep(15)
    #setup replication
    source_container.exec_run('mysql -uroot -p'+ps_password+' -e "CREATE USER \'repl\'@\'%\' IDENTIFIED BY \'replicapass\'; \
                            GRANT REPLICATION SLAVE ON *.* TO \'repl\'@\'%\';"')
    replica_container.exec_run('mysql -uroot -p'+ps_password+' -e "CHANGE REPLICATION SOURCE to SOURCE_HOST=\''+source_ps_container+'\', \
                            SOURCE_USER=\'repl\',SOURCE_PASSWORD=\'replicapass\',SOURCE_SSL=1,SOURCE_LOG_FILE=\'binlog.000002\';START REPLICA;"')
    #Add orchestrator user to PS
    source_container.exec_run('mysql -uroot -p'+ps_password+' -e "CREATE USER \'orchestrator\'@\'%\' IDENTIFIED BY \'\'; \
                            GRANT SUPER, PROCESS, REPLICATION SLAVE, RELOAD ON *.* TO \'orchestrator\'@\'%\'; \
                            GRANT SELECT ON mysql.slave_master_info TO \'orchestrator\'@\'%\';"')
    #Add sysbench user to PS
    source_container.exec_run('mysql -uroot -p'+ps_password+' -e \
                                "CREATE USER \'sysbench\'@\'%\' IDENTIFIED BY \'Test1234#\'; \
                                GRANT ALL PRIVILEGES on *.* to \'sysbench\'@\'%\'; \
                                CREATE DATABASE sbtest;"')
    #get orchestrator IP
    orchestrator = docker_client.containers.get(orch_container).attrs['NetworkSettings']['Networks'][network_name]['IPAddress']
    yield orchestrator
    containers_list=docker_client.containers.list()
    for container in containers_list:
        container.remove(v=True, force=True)
    docker_client.networks.get(network_name).remove()

def receive_current_value(key_path, server_state):
    if len(key_path) == 2:
        if key_path[0] == 'SlaveHosts':
            current_value = server_state[key_path[0]][0][key_path[1]]
            return current_value
        else:
            current_value = server_state[key_path[0]][key_path[1]]
            return current_value
    else:
        current_value = server_state[key_path[0]]
        return current_value

def test_discovery(orchestrator_ip):
    print(orchestrator_ip)
    r=requests.get('http://{}:3000/api/{}/{}/3306'.format(orchestrator_ip, 'discover', source_ps_container))
    discover_state = json.loads(r.text)
    assert r.status_code == 200
    assert discover_state['Message'] == 'Instance discovered: '+source_ps_container+':3306', (discover_state['Message'])

def test_source(orchestrator_ip):
    r=requests.get('http://{}:3000/api/{}/{}/3306'.format(orchestrator_ip, 'instance', source_ps_container))
    source_state = json.loads(r.text)
    assert r.status_code == 200
    for attibute in source_attr_reference:
        current_attr_value = receive_current_value(attibute['key_path'], source_state)
        assert current_attr_value == attibute['expected_value'], attibute

def test_replica(orchestrator_ip):
    time.sleep(10)
    r=requests.get('http://{}:3000/api/{}/{}/3306'.format(orchestrator_ip, 'instance', replica_ps_container))
    replica_state = json.loads(r.text)
    assert r.status_code == 200
    for attibute in replica_attr_reference:
        current_attr_value = receive_current_value(attibute['key_path'], replica_state)
        assert current_attr_value == attibute['expected_value'], attibute

def test_load(host,orchestrator_ip):
    docker_client = docker.from_env()
    cmd='sysbench --tables=20 --table-size=10000 --threads=4 --rand-type=pareto --db-driver=mysql \
        --mysql-user=sysbench --mysql-password=Test1234# --mysql-host={} --mysql-port=3306 --mysql-db=sbtest --mysql-storage-engine=innodb \
        /usr/share/sysbench/oltp_read_write.lua prepare'.format(docker_client.containers.get(source_ps_container).attrs['NetworkSettings']['Networks'][network_name]['IPAddress'])
    host.run(cmd)
    time.sleep(15)
    r=requests.get('http://{}:3000/api/{}/{}/3306'.format(orchestrator_ip, 'instance', replica_ps_container))
    replica_state = json.loads(r.text)
    assert r.status_code == 200
    for attibute in replica_attr_reference:
        current_attr_value = receive_current_value(attibute['key_path'], replica_state)
        assert current_attr_value == attibute['expected_value'], attibute

def test_replica_stopped(orchestrator_ip):
    time.sleep(2)
    subprocess.check_call(['docker', 'exec', replica_ps_container, 'mysql', '-uroot', '-psecret', '-e', 'STOP REPLICA;'])
    time.sleep(10)
    r=requests.get('http://{}:3000/api/{}/{}/3306'.format(orchestrator_ip, 'instance', replica_ps_container))
    replica_state = json.loads(r.text)
    assert r.status_code == 200
    for attibute in replica_stopped_attr_reference:
        current_attr_value = receive_current_value(attibute['key_path'], replica_state)
        assert current_attr_value == attibute['expected_value'], attibute

