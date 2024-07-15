#!/usr/bin/env python3
import pytest
import testinfra

from settings import *

def test_executables_exist(host):
    for executable in pxc_executables:
        assert host.file(base_dir+'/'+executable).exists
        assert oct(host.file(base_dir+'/'+executable).mode) == '0o755'

def test_mysql_version(host):
    if pxc_version_major in ['5.7', '5.6']:
        expected_version = 'mysql  Ver 14.14 Distrib ' + pxc57_client_version
        output = host.check_output(base_dir + '/bin/mysql --version')

        # Use regex to check if the expected version is in the output
        match = re.search(rf'{re.escape(expected_version)}', output)
        assert match, f"Expected version string not found in output: {output}"

def test_mysqld_version(host):
    if pxc_version_major in ['5.7','5.6']:
        expected = (
            'mysqld  Ver ' + pxc57_server_version_norel + ' for Linux on x86_64 (Percona XtraDB Cluster binary (GPL) ' +
            pxc57_server_version + ', Revision ' + pxc_revision + ', wsrep_' + wsrep_version + ')'
        )
        assert expected in host.check_output(base_dir+'/bin/mysqld --version')
    else:
        expected = (
            'mysqld  Ver ' + pxc_version + ' for Linux on x86_64 (Percona XtraDB Cluster binary (GPL) ' +
            pxc_version_percona + ', Revision ' + pxc_revision + ', WSREP version ' + wsrep_version + ')'
        )
        assert expected in host.check_output(base_dir+'/bin/mysqld --version')


def test_files_exist(host):
    for f in pxc_files:
        assert host.file(base_dir+'/'+f).exists
        assert host.file(base_dir+'/'+f).size != 0

def test_symlinks(host):
    for symlink in pxc_symlinks:
        assert host.file(base_dir+'/'+symlink[0]).is_symlink
        assert host.file(base_dir+'/'+symlink[0]).linked_to == base_dir+'/'+symlink[1]
        assert host.file(base_dir+'/'+symlink[1]).exists

def test_binaries_linked_libraries(host):
    for binary in pxc_binaries:
        assert '=> not found' not in host.check_output('ldd ' + base_dir + '/' + binary)
