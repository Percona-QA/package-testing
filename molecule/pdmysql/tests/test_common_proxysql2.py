import os
import pytest
import testinfra.utils.ansible_runner

from .settings import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")

VERSION = os.getenv("PROXYSQL_VERSION")

def skip_proxysql_tests(host):
    dist = host.system_info.distribution.lower()
    major = host.system_info.release.split(".")[0]

    result = host.run("mysqld --version")
    if result.rc != 0:
        return False

    # mysqld  Ver 9.7.1-1 ...
    ps_major = int(result.stdout.split()[2].split(".")[0])

    return (
        dist in ("redhat", "rhel", "oracle", "ol")
        and major == "8"
        and ps_major >= 9
    )


def test_package_is_installed(host):
    assert (
        host.package("proxysql2").is_installed
        or host.package("proxysql3").is_installed
    ), "Neither proxysql2 nor proxysql3 is installed"


def test_proxysql_version(host):
    result = host.run("proxysql --version")
    assert result.rc == 0, result.stderr
    assert VERSION in result.stdout, result.stdout


@pytest.mark.pkg_source
def test_sources_version(host):
    if REPO in ("testing", "experimental"):
        pytest.skip("This test is only for the main repository")

    dist = host.system_info.distribution.lower()
    major = int(host.system_info.release.split(".")[0])

    # Run only on RHEL/Oracle Linux 9 and 10
    if dist not in ("redhat", "oracle") or major not in (9, 10):
        pytest.skip("This test runs only on RHEL/Oracle Linux 9 and 10")

    result = host.run("rpm -qi proxysql3")
    assert result.rc == 0, result.stderr
    assert VERSION in result.stdout, result.stdout
