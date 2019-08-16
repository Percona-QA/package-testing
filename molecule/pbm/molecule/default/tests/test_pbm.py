import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_version(host):
    pass


def test_service(host):
    pass


def test_storages(host):
    pass


def test_nodes(host):
    pass


def test_users(host):
    pass


def test_backup(host):
    pass


def test_restore(host):
    pass


def test_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_package_deletion():
    pass