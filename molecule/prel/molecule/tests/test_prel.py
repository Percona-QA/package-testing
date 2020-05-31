import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

COMMANDS = ['enable', 'enable-only']
PRODUCTS = ["ps56", "ps57", "ps80", "psmdb34", "psmdb36", "psmdb40", "psmdb42",
            "pxb80", "pxc56", "pxc57", "pxc80", "ppg11", "ppg11.5", "ppg11.6",
            "ppg11.7", "ppg12", "ppg12.2", "pdmdb4.2", "pdmdb4.2.6", "pdmysql8.0.18", "pdmysql8.0"]
REPOSITORIES = ["original", "ps-80", "pxc-80", "psmdb-40", "psmdb-42",
                "tools", "ppg-11", "ppg-11.5", "ppg-11.6", "ppg-11.7",
                "ppg-12", "ppg-12.2", "pdmdb-4.2", "pdmdb-4.2.6", "pdmysql-8.0",
                "pdmysql-8.0.18"]
COMPONENTS = ['testing', 'release', 'experimental']
TEST_REPOSITORIES_DATA = [(repo, component) for repo in REPOSITORIES for component in PRODUCTS]


"""
-> Available commands:       enable enable-only setup disable
-> Available setup products: ps56 ps57 ps80 psmdb34 psmdb36 psmdb40 psmdb42 pxb80 pxc56 pxc57 pxc80 ppg11 ppg11.5 ppg11.6 ppg11.7 ppg12 ppg12.2 pdmdb4.2 pdmdb4.2.6 pdmysql8.0.18 pdmysql8.0
-> Available repositories:   original ps-80 pxc-80 psmdb-40 psmdb-42 tools ppg-11 ppg-11.5 ppg-11.6 ppg-11.7 ppg-12 ppg-12.2 pdmdb-4.2 pdmdb-4.2.6 pdmysql-8.0 pdmysql-8.0.18
-> Available components:     release testing experimental

"""


def remove_percona_repository():
    """
  # This removes any percona repositories on the system
  - name: remove the Percona apt main repository
    apt_repository: repo='deb http://repo.percona.com/apt {{ ansible_lsb.codename }} main' state=absent update_cache=yes
    when: ansible_os_family == "Debian"

  - name: remove the Percona apt testing repositories
    apt_repository: repo='deb http://repo.percona.com/apt {{ ansible_lsb.codename }} testing' state=absent update_cache=yes
    when: ansible_os_family == "Debian"

  - name: remove the Percona yum repositories
    yum: name=percona-release state=absent
    when: ansible_os_family == "RedHat"

  - name: remove saved repo files in yum
    file: path={{ item }} state=absent
    with_items:
      - /etc/yum.repos.d/percona-release.repo
      - /etc/yum.repos.d/percona-release.repo.rpmsave
    when: ansible_os_family == "RedHat"
    :return:
    """
    pass


def execute_percona_release_command(host, command, name, arg=None):
    """Execute percona release command

    :param host:
    :param command:
    :param name:
    :param arg:
    :return:
    """
    cmd = "percona-release {} {} {}".format(command, name, arg)
    return host.run(cmd)


def assert_repository_syntax(repo_name):
    pass


def assert_repo_file(host, repo_name, repo_type):
    pass


def check_list_of_packages(host):
    pass


def test_repository_managment_debian(host):
    """Scenario:
    1. Enable repository
    2. Check that repository file was created
    3. Check repository file access rights
    4. Check repository file name
    5. Check repository file content
    6. Check packages from repository
    7. Disable repository
    8. Check that repository file moved to backup
    """
    dist_name = host.system_info.distribution
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")


@pytest.mark.parametrize("repository, component", TEST_REPOSITORIES_DATA)
def test_repository_managment_rpm(host, repository, component):
    """Scenario:
    1. Enable repository
    2. Check that repository file was created
    3. Check repository file access rights
    4. Check repository file name
    5. Check repository file content
    6. Check packages from repository
    7. Disable repository
    8. Check that repository file moved to backup
    """
    dist_name = host.system_info.distribution
    if dist_name.lower() not in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for RPM based platforms")


def test_product_management_debian(host):
    dist_name = host.system_info.distribution
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")

def test_product_management_rpm(host):
    dist_name = host.system_info.distribution
    if dist_name.lower() not in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for RPM based platforms")
