#!/usr/bin/env python3
import docker
import pytest
from settings import docker_image, ps_docker_image


@pytest.fixture(scope='session')
def docker_client():
    client = docker.from_env()
    client.images.pull(docker_image)
    client.images.pull(ps_docker_image)
    return client
