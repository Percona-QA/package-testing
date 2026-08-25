#!/usr/bin/env python3
import json
import os
import time

import pytest

from pbs_helpers import run_pbs
from settings import (network_name, ps_docker_image, ps_pwd, pull_source_container,
                       repl_pwd, repl_user, test_pwd)

CONFIG_DIR = os.path.join(test_pwd, 'conf-pull')
DATA_DIR = os.path.join(test_pwd, 'data-pull')
CONFIG_FILE_HOST = os.path.join(CONFIG_DIR, 'config.json')
CONFIG_FILE_CONTAINER = '/etc/binlog-server/config.json'
DATA_DIR_CONTAINER = '/var/lib/binlog-server/data'


def _dir_size(path):
    return sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path))


@pytest.fixture(scope='module')
def source(docker_client):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True, mode=0o777)
    os.chmod(DATA_DIR, 0o777)

    docker_client.networks.create(network_name)
    container = docker_client.containers.run(
        ps_docker_image, name=pull_source_container, network=network_name,
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
        '"CREATE DATABASE test; CREATE TABLE test.t1 (a INT PRIMARY KEY); '
        'INSERT INTO test.t1 VALUES (1);"')

    # short checkpoint interval so a running "pull" streams new data to
    # the storage directory quickly enough for the test to observe it,
    # instead of sitting buffered for however long the (much larger)
    # default checkpoint interval would hold it.
    config = {
        "logger": {"level": "info", "file": "/var/log/binlog-server/binsrv.log"},
        "connection": {
            "host": pull_source_container,
            "port": 3306,
            "user": repl_user,
            "password": repl_pwd,
            "connect_timeout": 20,
            "read_timeout": 60,
            "write_timeout": 60,
        },
        "replication": {
            "server_id": 44,
            "idle_time": 2,
            "verify_checksum": True,
            "mode": "position",
        },
        "storage": {
            "backend": "file",
            "uri": "file://" + DATA_DIR_CONTAINER,
            "checkpoint_interval": "2s",
        },
    }
    with open(CONFIG_FILE_HOST, 'w') as f:
        json.dump(config, f)

    yield container

    container.remove(v=True, force=True)
    docker_client.networks.get(network_name).remove()


@pytest.fixture
def pull_process(docker_client, source):
    container = run_pbs(
        docker_client, network_name, CONFIG_DIR, DATA_DIR, DATA_DIR_CONTAINER,
        ['binlog_server', 'pull', CONFIG_FILE_CONTAINER], detach=True)
    # give it time to connect and take its initial snapshot before the
    # test starts generating the traffic it's supposed to pick up live.
    time.sleep(15)
    yield container
    container.stop()
    container.remove()


class TestBinlogServerPull:
    def test_pull_streams_new_binlogs_without_restart(self, source, pull_process):
        before = _dir_size(DATA_DIR)

        source.exec_run(
            'mysql -uroot -p' + ps_pwd + ' -e '
            '"INSERT INTO test.t1 VALUES (2),(3),(4); FLUSH BINARY LOGS;"')

        deadline = time.time() + 20
        after = _dir_size(DATA_DIR)
        while after <= before and time.time() < deadline:
            time.sleep(0.5)
            after = _dir_size(DATA_DIR)
        assert after > before, (
            "storage directory did not grow while pull mode was running "
            "(before=%d bytes, after=%d bytes); pull-mode logs:\n%s"
            % (before, after, pull_process.logs().decode()))
