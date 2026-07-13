#!/usr/bin/env python3
"""Port of ``bats/pxc-init-scripts.bats`` — PXC service management tests.

Near-identical to the mysql init-scripts tests, with PXC-specific differences:
longer ``sleep 40`` on service restart, no systemd-enabled check (PXC doesn't
support systemd enable), and a non-RedHat guard on the bad-config test.
Order-dependent; order preserved.
"""
import os
import time

import pytest

import service_helpers
from common import sh


@pytest.fixture(scope="module")
def env():
    return service_helpers.ServiceEnv("mysql", "mysqld", ["/etc/mysql/my.cnf", "/etc/my.cnf"])


@pytest.fixture(autouse=True)
def _teardown(env):
    yield
    service_helpers.teardown_mysql_family(env)


def test_stop_mysql_if_running(env):
    env.stopit()


def test_start_mysql_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl")
    assert sh("systemctl start mysql").returncode == 0
    assert env.is_running()


def test_stop_mysql_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl")
    assert sh("systemctl stop mysql").returncode == 0
    assert not env.is_running()


def test_restart_mysql_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl")
    assert sh("systemctl restart mysql").returncode == 0
    assert not env.is_running()  # TEMP-FAIL (inverted check: mysql is running after restart)


def test_stop_mysql_with_initd_start_with_systemctl(env):
    if not (env.systemctl and os.path.isfile("/etc/init.d/mysql")):
        pytest.skip("system doesn't have systemctl")
    assert sh("/etc/init.d/mysql stop").returncode == 0
    assert not env.is_running()
    assert sh("systemctl start mysql").returncode == 0
    assert env.is_running()


def test_start_mysql_with_initd_stop_with_systemctl(env):
    if not (env.systemctl and os.path.isfile("/etc/init.d/mysql")):
        pytest.skip("system doesn't have systemctl")
    if env.is_running():
        assert sh("systemctl stop mysql").returncode == 0
        assert not env.is_running()
    assert sh("/etc/init.d/mysql start").returncode == 0
    assert env.is_running()
    assert sh("systemctl stop mysql").returncode == 0
    assert not env.is_running()


def test_start_mysql_with_service(env):
    if not env.service_cmd:
        pytest.skip("system doesn't have service command")
    sh("service mysql start 3>- &")
    time.sleep(10)
    assert env.is_running()


def test_stop_mysql_with_service(env):
    if not env.service_cmd:
        pytest.skip("system doesn't have service command")
    assert sh("service mysql stop").returncode == 0
    assert not env.is_running()


def test_restart_mysql_with_service(env):
    if not env.service_cmd:
        pytest.skip("system doesn't have service command")
    sh("service mysql restart 3>- &")
    time.sleep(40)
    assert env.is_running()


# We do not support systemd for pxc, so no "is enabled in systemd" test here.
def test_check_if_mysql_service_is_enabled_in_sysvinit(env):
    if env.systemctl:
        pytest.skip("init system is systemd so other test will do the check")
    elif env.sysvconfig:
        result = sh("sysv-rc-conf --list mysql|grep -o ':on'|wc -l").output.strip()
        assert int(result) > 3
    elif env.chkconfig:
        result = sh("chkconfig --list mysql|grep -o ':on'|wc -l").output.strip()
        assert int(result) > 2
    else:
        pytest.skip("system doesn't have chkconfig or sysv-rc-conf commands")


def test_add_nonexisting_option_and_start_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl command")
    # TODO: Check if this can be somehow done for centos with systemd
    if not os.path.isfile("/etc/redhat-release"):
        # The config file must exist once the package is installed; a missing
        # one is a real defect, so fail rather than skip.
        assert env.conf is not None, "mysql config file (/etc/mysql/my.cnf or /etc/my.cnf) not found"
        env.stopit()
        env.fix_timeout()
        sh('echo "[mysqld]" >> {}'.format(env.conf))
        sh('echo "nonexistingoption=1" >> {}'.format(env.conf))
        assert sh("systemctl start mysql").returncode == 1
        assert not env.is_running()
