import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

SKIPPED_REPOSITORIES = ["ppg", "pdmdb", "pdps", "pdpxc", "psmdb-42", ""]

PRODUCT_REPOS = {"ps56": ["original", "tools"],
                 "ps57": ["original", "tools"],
                 "ps80": ["ps-80", "tools"],
                 "pxc56": ["original", "tools"],
                 "pxc57": ["original", "tools"],
                 "pxc80": ["pxc-80", "tools"],
                 "pxb80": ["tools"],
                 "psmdb34": ["original", "tools"],
                 "psmdb36": ["original", "tools"],
                 "psmdb40": ['psmdb-40', "tools"],
                 "psmdb42": ['psmdb-42', "tools"],
                 "ppg11": ["ppg-11"],
                 "ppg11.5": ["ppg-11.5"],
                 "ppg11.6": ["ppg-11.6"],
                 "ppg11.7": ["ppg-11.7"],
                 "ppg12": ["ppg-12"],
                 "ppg12.2": ["ppg-12.2"],
                 "ppg12.3": ["ppg-12.3"],
                 "pdmdb4.2": ["pdmdb-4.2"],
                 "pdmdb4.2.6": ["pdmdb-4.2.6"],
                 "pdpxc8.0.19": ["pdpxc-8.0.19"],
                 "pdpxc8.0": ["pdpxc-8.0"],
                 "pdps8.0.19": ["pdps-8.0.19"],
                 "pdps8.0": ["pdps-8.0"]
                 }


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
    elif "pdmdb" in repo_name:
        return "percona-server-mongodb"
    elif "psmdb" in repo_name:
        if "4" in repo_name:
            return "percona-server-mongodb"
        return "Percona-Server-MongoDB"
    elif "pxc" in repo_name:
        if "57" or "56" in repo_name:
            return "Percona-Server"
        return "percona-xtradb-cluster"
    elif "ps" in repo_name:
        return "percona-server"
    elif "original" in repo_name:
        return "percona-toolkit"
    elif "pxb" in repo_name:
        return "percona-xtrabackup"
    elif "tools" in repo_name:
        return "percona-toolkit"
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


def check_list_of_packages(host, repository):
    dist_name = host.system_info.distribution
    product_name = get_package_by_repo(repository)
    with host.sudo("root"):
        cmd = "apt-cache search percona | grep {}".format(product_name)
        if dist_name.lower() in ["redhat", "centos", 'rhel']:
            cmd = "yum list percona* | grep {}".format(product_name)
        result = host.run(cmd)
        assert product_name in result.stdout, (result.stdout, result.stderr)


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
    if any(rep in repository for rep in SKIPPED_REPOSITORIES) and component == 'experimental':
        pytest.skip("Unsupported repository {} for component".format(repository, component))
    if repository in ("ppg-12", "pdpxc-8.0", "pdps-8.0") and component == "testing":
        pytest.skip()
    dist_name = host.system_info.distribution
    codename = host.system_info.codename
    if ("ppg-11" or "pdmdb-4.2" in repository) and codename == "focal":
        pytest.skip("Not supported by focal")
    execute_percona_release_command(host,
                                    command=command,
                                    component=component,
                                    repository=repository)
    apt_update(host)
    repo_file = host.file(
        "/etc/apt/sources.list.d/percona-{}-{}.list".format(repository, component))
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        repo_file = host.file(
            "/etc/yum.repos.d/percona-{}-{}.repo".format(repository, component))
    assert repo_file.user == "root", repo_file.user
    assert repo_file.group == "root", repo_file.group
    check_list_of_packages(host, repository)
    execute_percona_release_command(host, command="disable",
                                    repository=repository,
                                    component=component)
    apt_update(host)
    backup_repo_file = host.file("/etc/apt/sources.list.d/percona-{}-{}.list.bak".format(repository, component))
    if dist_name.lower() in ["redhat", "centos", 'rhel']:
        backup_repo_file = host.file("/etc/yum.repos.d/percona-{}-{}.repo.bak".format(repository, component))
    assert backup_repo_file.user == "root"
    assert backup_repo_file.group == "root"
    apt_update(host)
    remove_percona_repository(host, "percona*")


@pytest.mark.parametrize("product", PRODUCT_REPOS.keys())
def test_setup_product(host, product):
    dist_name = host.system_info.distribution
    codename = host.system_info.codename
    if ("ppg-11" or "pdmdb-4.2" in product) and codename == "focal":
        pytest.skip("Not supported by focal")
    execute_percona_release_command(host, command="setup", repository=product)
    apt_update(host)
    for repo in PRODUCT_REPOS[product]:
        repo_file = host.file("/etc/apt/sources.list.d/percona-{}-release.list".format(repo))
        if dist_name.lower() in ["redhat", "centos", 'rhel']:
            repo_file = host.file("/etc/yum.repos.d/percona-{}-release.repo".format(repo))
        assert repo_file.user == "root", repo_file.user
        assert repo_file.group == "root", repo_file.group
    check_list_of_packages(host, product)
    for repo in PRODUCT_REPOS[product]:
        execute_percona_release_command(host, command="disable", repository=repo,
                                        component="release")
        backup_repo_file = host.file(
            "/etc/apt/sources.list.d/percona-{}-release.list.bak".format(repo))
        if dist_name.lower() in ["redhat", "centos", 'rhel']:
            backup_repo_file = host.file("/etc/yum.repos.d/percona-{}-release.repo.bak".format(repo))
        assert backup_repo_file.user == "root"
        assert backup_repo_file.group == "root"
    remove_percona_repository(host, "percona*")


