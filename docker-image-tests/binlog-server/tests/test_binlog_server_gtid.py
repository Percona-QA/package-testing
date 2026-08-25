#!/usr/bin/env python3
import json
import os
import time

import pytest

from pbs_helpers import run_pbs
from settings import (gtid_source_container, network_name, ps_docker_image,
                       ps_pwd, repl_pwd, repl_user, test_pwd)

CONFIG_DIR = os.path.join(test_pwd, 'conf-gtid')
DATA_DIR = os.path.join(test_pwd, 'data-gtid')
CONFIG_FILE_HOST = os.path.join(CONFIG_DIR, 'config.json')
CONFIG_FILE_CONTAINER = '/etc/binlog-server/config.json'
DATA_DIR_CONTAINER = '/var/lib/binlog-server/data'


@pytest.fixture(scope='module')
def gtid_source(docker_client):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True, mode=0o777)
    os.chmod(DATA_DIR, 0o777)

    docker_client.networks.create(network_name)
    container = docker_client.containers.run(
        ps_docker_image, '--gtid-mode=ON --enforce-gtid-consistency=ON',
        name=gtid_source_container, network=network_name,
        environment=[
            "MYSQL_ROOT_PASSWORD=" + ps_pwd,
            "PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport",
        ], detach=True)
    time.sleep(30)

    container.exec_run(
        'mysql -uroot -p' + ps_pwd + ' -e '
        '"CREATE USER \'' + repl_user + '\'@\'%\' IDENTIFIED BY \'' + repl_pwd + '\'; '
        'GRANT REPLICATION SLAVE ON *.* TO \'' + repl_user + '\'@\'%\';"')
    container.exec_run(
        'mysql -uroot -p' + ps_pwd + ' -e '
        '"CREATE DATABASE test; '
        'CREATE TABLE test.t1 (a INT PRIMARY KEY); '
        'INSERT INTO test.t1 VALUES (1),(2),(3); '
        'FLUSH BINARY LOGS;"')

    config = {
        "logger": {"level": "info", "file": "/var/log/binlog-server/binsrv.log"},
        "connection": {
            "host": gtid_source_container,
            "port": 3306,
            "user": repl_user,
            "password": repl_pwd,
            "connect_timeout": 20,
            "read_timeout": 60,
            "write_timeout": 60,
        },
        "replication": {
            "server_id": 43,
            "idle_time": 10,
            "verify_checksum": True,
            "mode": "gtid",
        },
        "storage": {
            "backend": "file",
            "uri": "file://" + DATA_DIR_CONTAINER,
        },
    }
    with open(CONFIG_FILE_HOST, 'w') as f:
        json.dump(config, f)

    yield container

    container.remove(v=True, force=True)
    docker_client.networks.get(network_name).remove()


class TestBinlogServerGtid:
    def test_fetch_streams_binlogs_in_gtid_mode(self, docker_client, gtid_source):
        exit_code, output = run_pbs(
            docker_client, network_name, CONFIG_DIR, DATA_DIR, DATA_DIR_CONTAINER,
            ['binlog_server', 'fetch', CONFIG_FILE_CONTAINER])
        assert exit_code == 0, output
        files = os.listdir(DATA_DIR)
        assert files, "no files written to storage directory: " + output

    def test_search_by_gtid_set(self, docker_client, gtid_source):
        result = gtid_source.exec_run(
            'mysql -uroot -N -s -e "SELECT @@GLOBAL.gtid_executed;"',
            environment=["MYSQL_PWD=" + ps_pwd])
        gtid_set = result.output.decode().strip()
        assert gtid_set, "source reported an empty gtid_executed value"

        exit_code, output = run_pbs(
            docker_client, network_name, CONFIG_DIR, DATA_DIR, DATA_DIR_CONTAINER,
            ['binlog_server', 'search_by_gtid_set', CONFIG_FILE_CONTAINER, gtid_set])
        assert exit_code == 0, output
        assert 'binlog' in output.lower(), output
