#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
from settings import *


container_name = 'proxy-docker-test-inspect'

@pytest.fixture(scope='module')
def inspect_data():
    docker_id = subprocess.check_output(
        ['docker', 'run', '-p', '16034:6032', '-p', '16035:6033', '-p', '16072:6070', '--name', container_name, '-d', docker_image]).decode().strip()
    inspect_data = json.loads(subprocess.check_output(['docker','inspect',container_name]))
    yield inspect_data[0]
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestContainerAttributes:
    def test_args(self, inspect_data):
        assert len(inspect_data['Args']) == 5
        assert inspect_data['Args'][0] == '/usr/bin/proxysql'
        assert inspect_data['Args'][1] == '-f'
        assert inspect_data['Args'][2] == '-c'
        assert inspect_data['Args'][3] == '/etc/proxysql/proxysql.cnf'
        assert inspect_data['Args'][4] == '--reload'


    def test_status(self, inspect_data):
        assert inspect_data['State']['Status'] == 'running'
        assert inspect_data['State']['Running'] == True

    def test_config(self, inspect_data):
        assert len(inspect_data['Config']['Cmd']) == 5
        assert inspect_data['Config']['Cmd'][0] == '/usr/bin/proxysql'
        assert inspect_data['Config']['Cmd'][1] == '-f'
        assert inspect_data['Config']['Cmd'][2] == '-c'
        assert inspect_data['Config']['Cmd'][3] == '/etc/proxysql/proxysql.cnf'
        assert inspect_data['Config']['Cmd'][4] == '--reload'

    def test_image_name(self, inspect_data):
        assert inspect_data['Config']['Image'] == docker_image

    def test_volumes(self, inspect_data):
        assert len(inspect_data['Config']['Volumes']) == 1
        assert '/var/lib/proxysql' in inspect_data['Config']['Volumes']

    def test_entrypoint(self, inspect_data):
        assert len(inspect_data['Config']['Entrypoint']) == 1
        assert inspect_data['Config']['Entrypoint'][0] == '/docker-entrypoint.sh'

    def test_exposed_ports(self, inspect_data):
        exposed_ports = inspect_data['Config']['ExposedPorts']
        expected_ports = ['3306/tcp', '6032/tcp', '6033/tcp', '6070/tcp']
        assert len(exposed_ports) == len(expected_ports)
        for port in expected_ports:
            assert port in exposed_ports

