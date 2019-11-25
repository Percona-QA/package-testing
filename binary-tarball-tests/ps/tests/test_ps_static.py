#!/usr/bin/env python3
import pytest
import testinfra

from settings import *

def test_binaries_exist(host):
    for binary in ps_binaries:
        assert host.file(base_dir+'/'+binary).exists
        assert oct(host.file(base_dir+'/'+binary).mode) == '0o755'

def test_binaries_version(host):
    if ps_version_major in ['5.7','5.6']:
        assert 'mysql  Ver 14.14 Distrib '+ps_version+', for Linux (x86_64)' in host.check_output(base_dir+'/bin/mysql --version')
        assert 'mysqld  Ver '+ps_version+' for Linux on x86_64 (Percona Server (GPL), Release '+ps_version_percona+', Revision '+ps_revision+')' in host.check_output(base_dir+'/bin/mysqld --version')
    else:
        assert 'mysql  Ver '+ ps_version +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')' in host.check_output(base_dir+'/bin/mysql --version')
        assert 'mysqld  Ver '+ ps_version +' for Linux on x86_64 (Percona Server (GPL), Release '+ ps_version_percona +', Revision '+ ps_revision +')' in host.check_output(base_dir+'/bin/mysqld --version')

def test_files_exist(host):
    for f in ps_files:
        assert host.file(base_dir+'/'+f).exists
        assert host.file(base_dir+'/'+f).size != 0

def test_symlinks(host):
    for symlink in ps_symlinks:
        assert host.file(base_dir+'/'+symlink[0]).is_symlink
        assert host.file(base_dir+'/'+symlink[0]).linked_to == base_dir+'/'+symlink[1]
