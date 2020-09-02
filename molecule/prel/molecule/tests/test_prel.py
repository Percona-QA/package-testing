import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

SKIPPED_REPOSITORIES = ["ppg", "pdmdb", "pdps", "pdpxc", "psmdb-42", ""]

PRODUCT_REPOS = {"ps56": ["ps-56", "tools"],
                 "ps57": ["ps-57"],
                 "ps80": ["ps-80", "tools"],
                 "pxc56": ["pxc-56", "tools"],
                 "pxc57": ["pxc-57"],
                 "pxc80": ["pxc-80", "tools"],
                 "pxb80": ["pxb-80"],
                 "psmdb36": ["psmdb-36"],
                 "psmdb40": ['psmdb-40', "tools"],
                 "psmdb42": ['psmdb-42', "tools"],
                 "ppg11": ["ppg-11"],
                 "ppg11.5": ["ppg-11.5"],
                 "ppg11.6": ["ppg-11.6"],
                 "ppg11.7": ["ppg-11.7"],
                 "ppg11.8": ["ppg-11.8"],
                 "ppg12": ["ppg-12"],
                 "ppg12.2": ["ppg-12.2"],
                 "ppg12.3": ["ppg-12.3"],
                 "pdmdb4.2": ["pdmdb-4.2"],
                 "pdmdb4.2.6": ["pdmdb-4.2.6"],
                 "pdmdb4.2.8": ["pdmdb-4.2.8"],
                 "pdmdb4.4.0": ["pdmdb-4.4.0"],
                 "pdpxc8.0.19": ["pdpxc-8.0.19"],
                 "pdpxc8.0": ["pdpxc-8.0"],
                 "pdps8.0.19": ["pdps-8.0.19"],
                 "pdps8.0": ["pdps-8.0"]
                 }

PRODUCT_PACKAGES = {"ps56": "Percona-Server",
                    "ps57": "Percona-Server",
                    "ps80": "percona-server",
                    "ps-80": "percona-server",
                    "pxc56": "Percona-XtraDB-Cluster",
                    "pxc57": "Percona-XtraDB-Cluster",
                    "pxc80": "percona-xtradb-cluster",
                    "pxb80": "percona-xtrabackup",
                    "pxc-80": "percona-xtradb-cluster",
                    "pxb-80": "percona-xtrabackup",
                    "psmdb34": "Percona-Server-MongoDB",
                    "psmdb36": "Percona-Server-MongoDB",
                    "psmdb40": "percona-server-mongodb",
                    "psmdb42": "percona-server-mongodb",
                    "psmdb-40": "percona-server-mongodb",
                    "psmdb-42": "percona-server-mongodb",
                    "psmdb-44": "percona-server-mongodb",
                    "ppg11": "percona-postgresql",
                    "ppg11.5": "percona-postgresql",
                    "ppg11.6": "percona-postgresql",
                    "ppg11.7": "percona-postgresql",
                    "ppg11.8": "percona-postgresql",
                    "ppg12": "percona-postgresql",
                    "ppg12.2": "percona-postgresql",
                    "ppg12.3": "percona-postgresql",
                    "ppg-11": "percona-postgresql",
                    "ppg-11.5": "percona-postgresql",
                    "ppg-11.6": "percona-postgresql",
                    "ppg-11.7": "percona-postgresql",
                    "ppg-11.8": "percona-postgresql",
                    "ppg-12": "percona-postgresql",
                    "ppg-12.2": "percona-postgresql",
                    "ppg-12.3": "percona-postgresql",
                    "pdmdb4.2": "percona-server-mongodb",
                    "pdmdb4.2.6": "percona-server-mongodb",
                    "pdmdb4.2.8": "percona-server-mongodb",
                    "pdmdb4.4.0": "percona-server-mongodb",
                    "pdpxc8.0.19": "percona-xtradb-cluster",
                    "pdpxc8.0.20": "percona-xtradb-cluster",
                    "pdpxc8.0": "percona-xtradb-cluster",
                    "pdps8.0.19": "percona-server",
                    "pdps8.0.20": "percona-server",
                    "pdps8.0": "percona-server",
                    "tools": "percona-toolkit",
                    "original": "percona-toolkit",
                    "pdmdb-4.2": "percona-server-mongodb",
                    "pdmdb-4.2.6": "percona-server-mongodb",
                    "pdmdb-4.2.8": "percona-server-mongodb",
                    "pdmdb-4.4.0": "percona-server-mongodb",
                    "pdpxc-8.0.19": "percona-xtradb-cluster",
                    "pdpxc-8.0.20": "percona-xtradb-cluster",
                    "pdpxc-8.0": "percona-xtradb-cluster",
                    "pdps-8.0.19": "percona-server",
                    "pdps-8.0.20": "percona-server",
                    "pdps-8.0": "percona-server"
                    }


REPOSITORIES = ["original", "ps-80", "pxc-80", "psmdb-40", "psmdb-42",
                "tools", "ppg-11", "ppg-11.5", "ppg-11.6", "ppg-11.7", "ppg-11.8",
                "ppg-12", "ppg-12.2", "ppg-12.3",
                "pdmdb-4.2", "pdmdb-4.2.6", "pdmdb-4.2.8", "pdpxc-8.0", "pdpxc-8.0.19",
                "pdps-8.0.19", "pdps-8.0"]
COMPONENTS = ['testing',
              'release',
              'experimental']
TEST_REPOSITORIES_DATA = [
    (
        repo, component, command
    ) for repo in REPOSITORIES for component in COMPONENTS for command in [
        "enable", 'enable-only']]


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


def percona_release_show(host):
    """Execute percona release command
    """
    with host.sudo("root"):
        cmd = "percona-release show"
        result = host.run(cmd)
        assert result.rc == 0, (result.stdout, result.stderr)
        print(result.stdout)
        return result.stdout


def check_list_of_packages(host, repository):
    dist_name = host.system_info.distribution
    product_name = PRODUCT_PACKAGES[repository]
    if dist_name in ['debian', 'ubuntu']:
        if repository in ['psmdb34', "psmdb36"]:
            product_name = "percona-server-mongodb"
        if repository in ['pxc57', 'pxc56']:
            product_name = "percona-xtradb-cluster"
        if repository in ['ps56', 'ps57']:
            product_name = "percona-server"
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
    dist_name = host.system_info.distribution
    codename = host.system_info.codename
    if any(rep in repository for rep in SKIPPED_REPOSITORIES) and component == 'experimental':
        pytest.skip("Unsupported repository {} for component".format(repository, component))
    if repository in ("ppg-12", "pdpxc-8.0", "pdps-8.0") and component == "testing":
        pytest.skip("Unsupported for testing repos")
    if ("ppg-11" or "pdmdb-4.2" in repository) and codename == "focal":
        pytest.skip("Not supported by focal")
    if ("ppg" or "pdmdb") in repository and codename == 'xenial':
        pytest.skip("Not supported by xenial")
    execute_percona_release_command(host,
                                    command=command,
                                    component=component,
                                    repository=repository)
    show_before = percona_release_show(host)
    assert repository in show_before, show_before
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
    show_after = percona_release_show(host)
    if repository != "original" and component != "testing":
        assert repository not in show_after, show_before
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
    if ("ppg" or "pdmdb") in product and codename == 'xenial':
        pytest.skip("Not supported by xenial")
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
