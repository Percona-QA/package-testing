#!/usr/bin/env python3
import json
import os
import time

import pytest

from settings import (docker_image, network_name, ps_docker_image, ps_pwd,
                       repl_pwd, repl_user, source_container, test_pwd)

CONFIG_DIR = os.path.join(test_pwd, 'conf')
DATA_DIR = os.path.join(test_pwd, 'data')
CONFIG_FILE_HOST = os.path.join(CONFIG_DIR, 'config.json')
CONFIG_FILE_CONTAINER = '/etc/binlog-server/config.json'
DATA_DIR_CONTAINER = '/var/lib/binlog-server/data'


def _run_pbs(docker_client, cmd):
    container = docker_client.containers.run(
        docker_image, cmd, network=network_name, detach=True,
        volumes={
            CONFIG_DIR: {'bind': '/etc/binlog-server', 'mode': 'ro'},
            DATA_DIR: {'bind': DATA_DIR_CONTAINER, 'mode': 'rw'},
        })
    exit_code = container.wait()['StatusCode']
    output = container.logs().decode()
    container.remove()
    return exit_code, output


@pytest.fixture(scope='module')
def source(docker_client):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    # world-writable: the binlog-server container writes here as its
    # unprivileged image user (uid 1001), which won't match whatever
    # owns this bind-mounted host directory.
    os.makedirs(DATA_DIR, exist_ok=True, mode=0o777)
    os.chmod(DATA_DIR, 0o777)

    docker_client.networks.create(network_name)
    container = docker_client.containers.run(
        ps_docker_image, name=source_container, network=network_name,
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
        "logger": {"level": "info", "file": "binsrv.log"},
        "connection": {
            "host": source_container,
            "port": 3306,
            "user": repl_user,
            "password": repl_pwd,
            "connect_timeout": 20,
            "read_timeout": 60,
            "write_timeout": 60,
        },
        "replication": {
            "server_id": 42,
            "idle_time": 10,
            "verify_checksum": True,
            "mode": "position",
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


class TestBinlogServerFetch:
    def test_fetch_streams_binlogs(self, docker_client, source):
        exit_code, output = _run_pbs(
            docker_client, ['binlog_server', 'fetch', CONFIG_FILE_CONTAINER])
        assert exit_code == 0, output
        files = os.listdir(DATA_DIR)
        assert files, "no files written to storage directory: " + output

    def test_list_shows_fetched_binlogs(self, docker_client, source):
        exit_code, output = _run_pbs(
            docker_client, ['binlog_server', 'list', CONFIG_FILE_CONTAINER])
        assert exit_code == 0, output
        assert 'binlog' in output.lower(), output
