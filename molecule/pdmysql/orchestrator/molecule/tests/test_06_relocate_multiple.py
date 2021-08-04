import os


import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_relocate_1(host):
    pass


def test_relocate_2(host):
    pass


def test_relocate_3(host):
    pass


def test_topology(host):
    pass
