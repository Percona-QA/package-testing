#!/usr/bin/env python3
"""Port of ``bats/mysql-init-scripts.bats`` — PS service management tests.

Order-dependent (service state carried between tests); order preserved. The
autouse teardown fixture reverts config edits after every test, like bats'
``teardown()``.
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
    assert env.is_running()


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
    time.sleep(10)
    assert env.is_running()


# Added 'alias' check based on OL9 behavior. Check PS-8675 for details.
def test_check_if_mysql_service_is_enabled_in_systemd(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl command")
    result = sh("systemctl is-enabled mysql").output.strip()
    if result == "alias":
        result = sh("systemctl is-enabled mysqld").output.strip()
    assert result == "enabled"


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
    if not os.path.isfile("/etc/redhat-release") and not os.path.isfile("/etc/system-release"):
        env.stopit()
        env.fix_timeout()
        sh('echo "[mysqld]" >> {}'.format(env.conf))
        sh('echo "nonexistingoption=1" >> {}'.format(env.conf))
        assert sh("systemctl start mysql").returncode == 1
        assert not env.is_running()
        sh("sed -i '/nonexistingoption=/d' {}".format(env.conf))
