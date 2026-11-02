import os
import pytest
import testinfra.utils.ansible_runner
from .settings import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

# PT_VERSION may be passed with package release (3.7.2-1) or without it (3.7.2)
PT_VERSION = os.getenv("PT_VERSION")
PT_UPSTREAM_VERSION = PT_VERSION.split('-')[0]

PTBINS = ['pt-align', 'pt-archiver', 'pt-config-diff', 'pt-deadlock-logger', 'pt-diskstats',
          'pt-duplicate-key-checker', 'pt-fifo-split', 'pt-find', 'pt-fingerprint',
          'pt-fk-error-logger', 'pt-galera-log-explainer', 'pt-heartbeat', 'pt-index-usage', 'pt-ioprofile', 'pt-kill',
          'pt-mext', 'pt-mongodb-query-digest', 'pt-mongodb-summary', 'pt-mysql-summary',
          'pt-online-schema-change', 'pt-pmp', 'pt-query-digest', 'pt-show-grants', 'pt-sift',
          'pt-slave-find', 'pt-slave-restart', 'pt-replica-find', 'pt-replica-restart', 'pt-stalk', 'pt-summary',
          'pt-table-checksum', 'pt-table-sync', 'pt-table-usage', 'pt-upgrade',
          'pt-variable-advisor', 'pt-visual-explain', 'pt-k8s-debug-collector', 'pt-mongodb-index-check',
          'pt-pg-summary', 'pt-secure-collect']


def test_check_pt_deb_package(host):
    dist = host.system_info.distribution
    if dist.lower() in RHEL_DISTS:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package('percona-toolkit')
    assert pkg.is_installed
    assert PT_VERSION in pkg.version, pkg.version


def test_check_pt_rpm_package(host):
    dist = host.system_info.distribution
    if dist.lower() in DEB_DISTS:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package('percona-toolkit')
    assert pkg.is_installed
    assert PT_VERSION in pkg.version + '-' + pkg.release, pkg.version + '-' + pkg.release


@pytest.mark.parametrize("pt_bin", PTBINS)
def test_pt_binaries(host, pt_bin):
    cmd = '{} --version'.format(pt_bin)
    result = host.run(cmd)
    assert PT_UPSTREAM_VERSION in result.stdout, result.stdout
