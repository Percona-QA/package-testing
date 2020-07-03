import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

PRODUCTS = ["ps56", "ps57", "ps80",
            "psmdb34", "psmdb36", "psmdb40", "psmdb42",
            "pxb80", "pxc56", "pxc57", "pxc80",
            "ppg11", "ppg11.5", "ppg11.6",
            "ppg11.7", "ppg11.8", "ppg12", "ppg12.2", "ppg12.3",
            "pdmdb4.2", "pdmdb4.2.6", "pdpxc8.0.19", 'pdps8.0.19',
            "pdpxc-8.0", "pdps-8.0"]
REPOSITORIES = ["original", "ps-80", "pxc-80", "psmdb-40", "psmdb-42",
                "tools", "ppg-11", "ppg-11.5", "ppg-11.6", "ppg-11.7", "ppg-11.8",
                "ppg-12", "ppg-12.2", "ppg-12.3",
                "pdmdb-4.2", "pdmdb-4.2.6", "pdpxc-8.0", "pdpxc-8.0.19",
                "pdps-8.0.19", "pdps-8.0"]
COMPONENTS = ['testing',
              'release',
              'experimental']
TEST_REPOSITORIES_DATA = [
    (
        repo, component, command
    ) for repo in REPOSITORIES for component in COMPONENTS for command in [
        "enable", 'enable-only']]


def get_package_by_repo(repo_name):
    if "ppg" in repo_name:
        return "percona-postgresql"
    elif "psmdb" in repo_name:
        return "percona-server-mongodb"
    elif "pxc" in repo_name:
        return "percona-xtradb-cluster"
    elif "ps" in repo_name:
        return "percona-server"
    else:
        return "Unsupported"


@pytest.fixture()
def repo_file_template(host):
    dist_name = host.system_info.distribution
    repo_file = "/etc/apt/sources.list.d/percona-{}-{}"
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        repo_file = "/etc/yum.repos.d/percona-{}-{}"
    return repo_file


def apt_update(host):
    """Execute apt-get update on host

    :param host:
    :return:
    """
    dist_name = host.system_info.distribution
    if dist_name.lower() not in ["redhat", "centos", 'rhel']:
        with host.sudo("root"):
            result = host.run("apt-get update -y")
            assert result.rc == 0, result.stderr
            return result


def remove_percona_repository(host, repo_file):
    """Delete repository file
    """
    with host.sudo("root"):
        cmd = "sudo rm -f {}".format(repo_file)
        result = host.run(cmd)
        assert result.rc == 0, result.stderr


def execute_percona_release_command(host,
                                    repository="",
                                    component="",
                                    command="enable"):
    """Execute percona release command
    :param host:
    :param component:
    :param command:
    :param repository:
    :return:
    """
    with host.sudo("root"):
        cmd = "percona-release {command} {repository} {component}".format(command=command,
                                                                          repository=repository,
                                                                          component=component)
        result = host.run(cmd)
        assert result.rc == 0, (result.stdout, result.stderr)
        return result


def assert_repo_file(host, repo_name, repo_type=None):
    dist_name = host.system_info.distribution
    repo_dir = "/etc/apt/sources.list.d/"
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        repo_dir = "/etc/yum/yum.repos.d/"
    repo_file = "percona-{}".format(repo_name)
    if repo_type:
        repo_file = "percona-{}-{}".format(repo_name, repo_type)
    cmd = "ls {} | grep {}".format(repo_dir, repo_file)
    result = host.run(cmd)
    assert result.rc == 0, result.stdout


def check_list_of_packages(host, product_name):
    dist_name = host.system_info.distribution
    cmd = "apt-cache search percona*"
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        cmd = "yum list percona* | grep {}".format(product_name)
    result = host.run(cmd)
    assert product_name in result.stdout


def test_package_installed(host):
    pkg = host.package('percona-release')
    assert pkg.is_installed


@pytest.mark.parametrize("repository, component, command", TEST_REPOSITORIES_DATA)
def test_enable_repo(host, repository, component, command):
    """Check enable repository command
    Scenario:
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
    execute_percona_release_command(host,
                                    command=command,
                                    component=component,
                                    repository=repository)
    apt_update(host)
    repo_file = host.file("/etc/apt/sources.list.d/percona-{}-{}.list".format(repository, component))
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        repo_file = host.file("/etc/yum/yum.repos.d/percona-{}-{}.repo".format(repository, component))
    assert repo_file.user == "root", repo_file.user
    assert repo_file.group == "root", repo_file.group
    execute_percona_release_command(host, command="disable",
                                    repository=repository,
                                    component=component)
    backup_repo_file = host.file("/etc/apt/sources.list.d/percona-{}-{}.list.bak".format(repository, component))
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        backup_repo_file = host.file("/etc/yum/yum.repos.d/percona-{}-{}.repo.bak".format(repository, component))
    assert backup_repo_file.user == "root"
    assert backup_repo_file.group == "root"


@pytest.mark.parametrize("product", PRODUCTS)
def test_setup_product(host, product):
    dist_name = host.system_info.distribution
    execute_percona_release_command(host, command="setup", repository=product)


