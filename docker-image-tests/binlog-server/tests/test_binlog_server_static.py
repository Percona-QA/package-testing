#!/usr/bin/env python3
from settings import docker_image, pbs_version


def _run(docker_client, cmd):
    container = docker_client.containers.run(docker_image, cmd, detach=True)
    exit_code = container.wait()['StatusCode']
    output = container.logs().decode()
    container.remove()
    return exit_code, output


class TestBinlogServerStatic:
    def test_version(self, docker_client):
        exit_code, output = _run(docker_client, ['binlog_server', 'version'])
        assert exit_code == 0, output
        assert pbs_version.split('-')[0] in output, output

    def test_usage(self, docker_client):
        # invoked with no mode: should print usage rather than crash the
        # container, listing the known modes.
        exit_code, output = _run(docker_client, ['binlog_server'])
        for mode in ('fetch', 'pull', 'list', 'search_by_timestamp',
                     'search_by_gtid_set', 'purge_binlogs'):
            assert mode in output, output

    def test_runs_as_unprivileged_user(self, docker_client):
        exit_code, output = _run(docker_client, ['id', '-u'])
        assert exit_code == 0, output
        assert output.strip() == '1001', output
