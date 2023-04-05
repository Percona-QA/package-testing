#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
from settings import *

container_name = 'orch-docker-test-inspect'

@pytest.fixture(scope='module')
def inspect_data():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-d', docker_image]).decode().strip()
    inspect_data = json.loads(subprocess.check_output(['docker','inspect',container_name]))
    yield inspect_data[0]
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestContainerAttributes:
    def test_args(self, inspect_data):
        assert len(inspect_data['Args']) == 4
        assert inspect_data['Args'][0] == '/usr/local/orchestrator/orchestrator'
        assert inspect_data['Args'][1] == '-config'
        assert inspect_data['Args'][2] == '/etc/orchestrator/orchestrator.conf.json'
        assert inspect_data['Args'][3] == 'http'

    def test_status(self, inspect_data):
        assert inspect_data['State']['Status'] == 'running'
        assert inspect_data['State']['Running'] == True

    def test_config(self, inspect_data):
        assert len(inspect_data['Config']['Cmd']) == 4
        assert inspect_data['Config']['Cmd'][0] == '/usr/local/orchestrator/orchestrator'
        assert inspect_data['Config']['Cmd'][1] == '-config'
        assert inspect_data['Config']['Cmd'][2] == '/etc/orchestrator/orchestrator.conf.json'
        assert inspect_data['Config']['Cmd'][3] == 'http'

    def test_image_name(self, inspect_data):
        assert inspect_data['Config']['Image'] == docker_image

    def test_volumes(self, inspect_data):
        assert len(inspect_data['Config']['Volumes']) == 1
        assert '/var/lib/orchestrator' in inspect_data['Config']['Volumes']

    def test_entrypoint(self, inspect_data):
        assert len(inspect_data['Config']['Entrypoint']) == 1
        assert inspect_data['Config']['Entrypoint'][0] == '/entrypoint.sh'

    def test_exposed_ports(self, inspect_data):
        assert len(inspect_data['Config']['ExposedPorts']) == 2
        assert '10008/tcp' in inspect_data['Config']['ExposedPorts']
        assert '3000/tcp' in inspect_data['Config']['ExposedPorts']
