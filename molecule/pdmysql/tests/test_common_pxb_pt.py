import os
import pytest
import testinfra.utils.ansible_runner
from .settings import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

DEBPACKAGES = ['percona-xtrabackup-80',
               'percona-xtrabackup-test-80',
               'percona-xtrabackup-dbg-80']

RPMPACKAGES = ['percona-xtrabackup-80',
               'percona-xtrabackup-test-80',
               'percona-xtrabackup-80-debuginfo']

PTBINS = ['pt-align', 'pt-archiver', 'pt-config-diff', 'pt-deadlock-logger', 'pt-diskstats',
          'pt-duplicate-key-checker', 'pt-fifo-split', 'pt-find', 'pt-fingerprint',
          'pt-fk-error-logger', 'pt-heartbeat', 'pt-index-usage', 'pt-ioprofile', 'pt-kill',
          'pt-mext', 'pt-mongodb-query-digest', 'pt-mongodb-summary', 'pt-mysql-summary',
          'pt-online-schema-change', 'pt-pmp', 'pt-query-digest', 'pt-show-grants', 'pt-sift',
          'pt-slave-delay', 'pt-slave-find', 'pt-slave-restart', 'pt-stalk', 'pt-summary',
          'pt-table-checksum', 'pt-table-sync', 'pt-table-usage', 'pt-upgrade',
          'pt-variable-advisor', 'pt-visual-explain']

PXB_VERSION = os.getenv("PXB_VERSION")
PT_VERSION = os.getenv("PT_VERSION")
REPO = os.environ.get("REPO")

@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PXB_VERSION in pkg.version, pkg.version

@pytest.mark.parametrize("package", RPMPACKAGES)
def test_check_rpm_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in DEB_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert PXB_VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release

def test_binary_version(host):
    cmd = "xtrabackup --version"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert PXB_VERSION in result.stderr, (result.stdout, result.stdout)


@pytest.mark.parametrize("pt_bin", PTBINS)
def test_pt_binaries(host, pt_bin):
    cmd = '{} --version'.format(pt_bin)
    result = host.run(cmd)
    assert PT_VERSION in result.stdout, result.stdout

def test_sources_pxb_version(host):
    if REPO == "testing":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    cmd = "apt-cache madison percona-xtrabackup-80 | grep Source | grep \"{}\"".format(PXB_VERSION)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert PXB_VERSION in result.stdout, result.stdout

def test_sources_pt_version(host):
    if REPO == "testing":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    cmd = "apt-cache madison percona-toolkit | grep Source | grep \"{}\"".format(PT_VERSION)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert PT_VERSION in result.stdout, result.stdout
