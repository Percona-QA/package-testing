#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
from settings import *

container_name = 'router-docker-test-inspect'

@pytest.fixture(scope='module')
def inspect_data():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-d', docker_image], stderr=subprocess.STDOUT ).decode().strip()
    inspect_data = json.loads(subprocess.check_output(['docker','inspect',container_name]))
    yield inspect_data[0]
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestContainerAttributes:
    def test_status(self, inspect_data):
        assert inspect_data['State']['Status'] == 'running'
        assert inspect_data['State']['Running'] == True

    def test_config(self, inspect_data):
        assert len(inspect_data['Config']['Cmd']) == 1
        assert inspect_data['Config']['Cmd'][0] == 'mysqlrouter'

    def test_image_name(self, inspect_data):
        assert inspect_data['Config']['Image'] == docker_image

    def test_volumes(self, inspect_data):
        assert len(inspect_data['Config']['Volumes']) == 1
        assert '/var/lib/mysqlrouter' in inspect_data['Config']['Volumes']

    def test_entrypoint(self, inspect_data):
        assert len(inspect_data['Config']['Entrypoint']) == 1
        assert inspect_data['Config']['Entrypoint'][0] == '/entrypoint.sh'

