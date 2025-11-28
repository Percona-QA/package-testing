#!/usr/bin/env python3
import re
import pytest
import testinfra

from settings import *

def test_proxysql_version(host):
    if proxysql_major_version.startswith(("2.7", "3.")):
        expected_version = f"ProxySQL version {proxysql_version}-percona-1.1"
        output = host.check_output(f"{base_dir}/usr/bin/proxysql --version")

        assert re.search(re.escape(expected_version), output), \
            f"Expected version string not found in output: {output}"

def test_proxysql_admin_version(host):
    if proxysql_major_version.startswith(("2.7", "3.")):
        expected_version = f"proxysql-admin version {proxysql_version}"
        output = host.check_output(f"{base_dir}/usr/bin/proxysql-admin --version")

        assert re.search(re.escape(expected_version), output), \
            f"Expected version string not found in output: {output}"

def test_proxysql_scheduler_admin_version(host):
    if proxysql_major_version.startswith(("2.7", "3.")):
        expected_version = f"percona-scheduler-admin Version: {proxysql_version}"
        output = host.check_output(f"{base_dir}/usr/bin/percona-scheduler-admin --version")

        assert re.search(re.escape(expected_version), output), \
            f"Expected version string not found in output: {output}"

def test_files_exist(host):
    for f in proxysql_files:
        file_path = f"{base_dir}/{f}"
        file = host.file(file_path)
        assert file.exists, f"{file_path} does not exist"
        assert file.size > 0, f"{file_path} is empty"
