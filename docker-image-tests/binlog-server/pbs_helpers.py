#!/usr/bin/env python3
from settings import docker_image


def run_pbs(docker_client, network, config_dir, data_dir, data_dir_container,
            cmd, detach=False):
    """Run a binlog_server container against a mounted config/data dir.

    With detach=False (the default) this waits for the container to
    exit and returns (exit_code, combined stdout+stderr); the container
    is removed either way. With detach=True it returns the running
    Container object instead - the caller owns stopping/removing it -
    which is what the long-running "pull" mode needs.
    """
    volumes = {
        config_dir: {'bind': '/etc/binlog-server', 'mode': 'ro'},
        data_dir: {'bind': data_dir_container, 'mode': 'rw'},
    }
    container = docker_client.containers.run(
        docker_image, cmd, network=network, detach=True, volumes=volumes)
    if detach:
        return container
    exit_code = container.wait()['StatusCode']
    output = container.logs().decode()
    container.remove()
    return exit_code, output
