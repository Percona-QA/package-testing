import os
import pytest
import testinfra.utils.ansible_runner
import re
from .settings import *
from packaging import version

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

PXB_VERSION = os.getenv("PXB_VERSION")
DEB_PERCONA_BUILD_PXB_VERSION = ''
RPM_PERCONA_BUILD_PXB_VERSION = ''
if re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', PXB_VERSION): # if full package PXB_VERSION 8.0.32-25.1 is passed we need to re-assign it for tests
    DEB_PERCONA_BUILD_PXB_VERSION = re.sub(r'.(\d+)$',r'-\g<1>', PXB_VERSION) # convert to format passed by host.package.version for deb 8.0.32-25-1
    RPM_PERCONA_BUILD_PXB_VERSION = PXB_VERSION # re-assign for RPM tests and use 8.0.32-25.1
    PXB_VERSION = '.'.join(PXB_VERSION.split('.')[:-1]) # use VERSION 8.0.32-25 without package build number for non-package tests

PT_VERSION = os.getenv("PT_VERSION")

# Get 80/81/etc version number
PXB_MAJOR_VER=''.join(PXB_VERSION.split('.')[:2])

PXB_DEBPACKAGES = ['percona-xtrabackup-' + PXB_MAJOR_VER,
            'percona-xtrabackup-test-' + PXB_MAJOR_VER,
            'percona-xtrabackup-dbg-' + PXB_MAJOR_VER]

PXB_RPMPACKAGES = ['percona-xtrabackup-' + PXB_MAJOR_VER,
            'percona-xtrabackup-test-' + PXB_MAJOR_VER,
            'percona-xtrabackup-' + PXB_MAJOR_VER + '-debuginfo']

PTBINS = ['pt-align', 'pt-archiver', 'pt-config-diff', 'pt-deadlock-logger', 'pt-diskstats',
          'pt-duplicate-key-checker', 'pt-fifo-split', 'pt-find', 'pt-fingerprint',
          'pt-fk-error-logger', 'pt-galera-log-explainer', 'pt-heartbeat', 'pt-index-usage', 'pt-ioprofile', 'pt-kill',
          'pt-mext', 'pt-mongodb-query-digest', 'pt-mongodb-summary', 'pt-mysql-summary',
          'pt-online-schema-change', 'pt-pmp', 'pt-query-digest', 'pt-show-grants', 'pt-sift',
          'pt-slave-delay', 'pt-slave-find', 'pt-slave-restart', 'pt-stalk', 'pt-summary',
          'pt-table-checksum', 'pt-table-sync', 'pt-table-usage', 'pt-upgrade',
          'pt-variable-advisor', 'pt-visual-explain', 'pt-k8s-debug-collector', 'pt-mongodb-index-check',
          'pt-pg-summary', 'pt-secure-collect']

@pytest.mark.parametrize("package", PXB_DEBPACKAGES)
def test_check_pxb_deb_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    if DEB_PERCONA_BUILD_PXB_VERSION:
        assert DEB_PERCONA_BUILD_PXB_VERSION in pkg.version, pkg.version
    else:
        assert PXB_VERSION in pkg.version, pkg.version

@pytest.mark.parametrize("package", PXB_RPMPACKAGES)
def test_check_pxb_rpm_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in DEB_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    if RPM_PERCONA_BUILD_PXB_VERSION:
        assert RPM_PERCONA_BUILD_PXB_VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release
    else:
        assert PXB_VERSION in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release

def test_pxb_binary_version(host):
    cmd = "xtrabackup --version"
    result = host.run(cmd)
    assert result.rc == 0, result.stderr
    assert PXB_VERSION in result.stderr, (result.stdout, result.stdout)

@pytest.mark.pkg_source
def test_sources_pxb_version(host):
    if REPO == "testing" or REPO == "experimental":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    if DEB_PERCONA_BUILD_PXB_VERSION:
        cmd = "apt-cache madison percona-xtrabackup-{} | grep Source | grep \"{}\"".format(PXB_MAJOR_VER, DEB_PERCONA_BUILD_PXB_VERSION)
    else:
        cmd = "apt-cache madison percona-xtrabackup-{} | grep Source | grep \"{}\"".format(PXB_MAJOR_VER, PXB_VERSION)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert PXB_VERSION in result.stdout, result.stdout

def test_check_pt_deb_package(host):
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package('percona-toolkit')
    assert pkg.is_installed
    assert PT_VERSION in pkg.version, pkg.version

def test_check_pt_rpm_package(host):
    dist = host.system_info.distribution
    if dist.lower() in DEB_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package('percona-toolkit')
    assert pkg.is_installed
    assert PT_VERSION in pkg.version, pkg.version

@pytest.mark.parametrize("pt_bin", PTBINS)
def test_pt_binaries(host, pt_bin):
    cmd = '{} --version'.format(pt_bin)
    result = host.run(cmd)
    assert PT_VERSION in result.stdout, result.stdout

@pytest.mark.pkg_source
def test_sources_pt_version(host):
    if REPO == "testing" or REPO == "experimental":
        pytest.skip("This test only for main repo")
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for DEB distributions")
    cmd = "apt-cache madison percona-toolkit | grep Source | grep \"{}\"".format(PT_VERSION)
    result = host.run(cmd)
    assert result.rc == 0, (result.stderr, result.stdout)
    assert PT_VERSION in result.stdout, result.stdout
