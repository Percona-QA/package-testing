#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json

from settings import *

container_name = 'ps-docker-test-inspect'

@pytest.fixture(scope='class')
def inspect_data():
    # run a container
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'MYSQL_ROOT_PASSWORD='+ps_pwd, '-d', docker_image]).decode().strip()
    # return json data with info about container
    inspect_data = json.loads(subprocess.check_output(['docker','inspect',container_name]))
    yield inspect_data
    # at the end of the test suite, destroy the container
    subprocess.check_call(['docker', 'rm', '-f', docker_id])

def test_args(inspect_data):
    assert len(inspect_data[0]['Args']) == 1
    assert inspect_data[0]['Args'][0] == 'mysqld'

def test_status(inspect_data):
    assert inspect_data[0]['State']['Status'] == 'running'
    assert inspect_data[0]['State']['Running'] == True

def test_config(inspect_data):
    assert len(inspect_data[0]['Config']['Cmd']) == 1
    assert inspect_data[0]['Config']['Cmd'][0] == 'mysqld'

def test_image_name(inspect_data):
    assert inspect_data[0]['Config']['Image'] == docker_image

def test_volumes(inspect_data):
    assert len(inspect_data[0]['Config']['Volumes']) == 2
    assert '/var/lib/mysql' in inspect_data[0]['Config']['Volumes']
    assert '/var/log/mysql' in inspect_data[0]['Config']['Volumes']

def test_entrypoint(inspect_data):
    assert len(inspect_data[0]['Config']['Entrypoint']) == 1
    assert inspect_data[0]['Config']['Entrypoint'][0] == '/docker-entrypoint.sh'

def test_exposed_ports(inspect_data):
    if ps_version_major in ['5.7','5.6']:
        assert len(inspect_data[0]['Config']['ExposedPorts']) == 1
        assert '3306/tcp' in inspect_data[0]['Config']['ExposedPorts']
    else:
        assert len(inspect_data[0]['Config']['ExposedPorts']) == 2
        assert '3306/tcp' in inspect_data[0]['Config']['ExposedPorts']
        assert '33060/tcp' in inspect_data[0]['Config']['ExposedPorts']
