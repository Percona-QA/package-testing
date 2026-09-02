#!/usr/bin/env python3
import json
import os
import time

import pytest

from pbs_helpers import run_pbs
from settings import (inspect_source_container, network_name, ps_docker_image,
                       ps_pwd, repl_pwd, repl_user, test_pwd)

CONFIG_DIR = os.path.join(test_pwd, 'conf-inspect')
DATA_DIR = os.path.join(test_pwd, 'data-inspect')
CONFIG_FILE_HOST = os.path.join(CONFIG_DIR, 'config.json')
CONFIG_FILE_CONTAINER = '/etc/binlog-server/config.json'
DATA_DIR_CONTAINER = '/var/lib/binlog-server/data'


@pytest.fixture(scope='module')
def fetched_storage(docker_client):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True, mode=0o777)
    os.chmod(DATA_DIR, 0o777)

    docker_client.networks.create(network_name)
    source = docker_client.containers.run(
        ps_docker_image, name=inspect_source_container, network=network_name,
        environment=[
            "MYSQL_ROOT_PASSWORD=" + ps_pwd,
            "PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport",
        ], detach=True)
    time.sleep(30)

    source.exec_run(
        'mysql -uroot -p' + ps_pwd + ' -e '
        '"CREATE USER \'' + repl_user + '\'@\'%\' IDENTIFIED BY \'' + repl_pwd + '\'; '
        'GRANT REPLICATION SLAVE ON *.* TO \'' + repl_user + '\'@\'%\';"')
    source.exec_run(
        'mysql -uroot -p' + ps_pwd + ' -e '
        '"CREATE DATABASE test; CREATE TABLE test.t1 (a INT PRIMARY KEY);"')
    # rotate a few times so there's more than one fetched binlog file -
    # purge_binlogs can't remove the current tail file, so a single-file
    # storage directory would make that test meaningless.
    for i in range(3):
        source.exec_run(
            'mysql -uroot -p' + ps_pwd + ' -e '
            '"INSERT INTO test.t1 VALUES (' + str(i) + '); FLUSH BINARY LOGS;"')

    config = {
        "logger": {"level": "info", "file": "/var/log/binlog-server/binsrv.log"},
        "connection": {
            "host": inspect_source_container,
            "port": 3306,
            "user": repl_user,
            "password": repl_pwd,
            "connect_timeout": 20,
            "read_timeout": 60,
            "write_timeout": 60,
        },
        "replication": {
            "server_id": 45,
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

    exit_code, output = run_pbs(
        docker_client, network_name, CONFIG_DIR, DATA_DIR, DATA_DIR_CONTAINER,
        ['binlog_server', 'fetch', CONFIG_FILE_CONTAINER])
    assert exit_code == 0, "initial fetch failed: " + output
    files_before = sorted(os.listdir(DATA_DIR))
    assert len(files_before) > 1, (
        "need more than one fetched binlog file to test purge_binlogs, got: "
        + str(files_before))

    yield files_before

    source.remove(v=True, force=True)
    docker_client.networks.get(network_name).remove()


class TestBinlogServerInspect:
    def test_search_by_timestamp(self, docker_client, fetched_storage):
        now = time.strftime('%Y-%m-%dT%H:%M:%S')
        exit_code, output = run_pbs(
            docker_client, network_name, CONFIG_DIR, DATA_DIR, DATA_DIR_CONTAINER,
            ['binlog_server', 'search_by_timestamp', CONFIG_FILE_CONTAINER, now])
        assert exit_code == 0, output
        assert 'binlog' in output.lower(), output

    def test_purge_binlogs(self, docker_client, fetched_storage):
        oldest = fetched_storage[0]
        exit_code, output = run_pbs(
            docker_client, network_name, CONFIG_DIR, DATA_DIR, DATA_DIR_CONTAINER,
            ['binlog_server', 'purge_binlogs', CONFIG_FILE_CONTAINER, oldest])
        assert exit_code == 0, output
        files_after = sorted(os.listdir(DATA_DIR))
        assert oldest not in files_after, (
            "expected %s to be purged, still present: %s" % (oldest, files_after))
        assert files_after, "purge_binlogs must not remove the current tail file"
