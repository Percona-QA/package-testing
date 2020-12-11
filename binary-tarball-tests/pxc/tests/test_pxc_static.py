#!/usr/bin/env python3
import pytest
import testinfra

from settings import *

def test_binaries_exist(host):
    for binary in pxc_binaries:
        assert host.file(base_dir+'/'+binary).exists
        assert oct(host.file(base_dir+'/'+binary).mode) == '0o755'

def test_binaries_version(host):
    if pxc_version_major in ['5.7','5.6']:
        assert 'mysql  Ver 14.14 Distrib '+pxc57_client_version+', for Linux (x86_64) using  6.0' in host.check_output(base_dir+'/bin/mysql --version')
        assert 'mysqld  Ver '+pxc_version+' for Linux on x86_64 (Percona XtraDB Cluster binary (GPL) '+pxc57_server_version+', Revision '+pxc_revision+', wsrep_'+wsrep_version+')' in host.check_output(base_dir+'/bin/mysqld --version')
    else:
        assert 'mysql  Ver '+ pxc_version +' for Linux on x86_64 (Percona XtraDB Cluster binary (GPL) '+ pxc_version_percona +', Revision '+ pxc_revision +', WSREP version '+wsrep_version+')' in host.check_output(base_dir+'/bin/mysql --version')
        assert 'mysqld  Ver '+ pxc_version +' for Linux on x86_64 (Percona XtraDB Cluster binary (GPL) '+ pxc_version_percona +', Revision '+ pxc_revision +', WSREP version '+wsrep_version+')' in host.check_output(base_dir+'/bin/mysqld --version')

def test_files_exist(host):
    for f in pxc_files:
        assert host.file(base_dir+'/'+f).exists
        assert host.file(base_dir+'/'+f).size != 0

def test_symlinks(host):
    for symlink in pxc_symlinks:
        assert host.file(base_dir+'/'+symlink[0]).is_symlink
        assert host.file(base_dir+'/'+symlink[0]).linked_to == base_dir+'/'+symlink[1]
