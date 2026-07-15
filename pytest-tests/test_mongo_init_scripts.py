#!/usr/bin/env python3
"""Port of ``bats/mongo-init-scripts.bats`` — PSMDB service management tests.

Order-dependent; order preserved. The autouse teardown reverts config edits
after each test.
"""
import os
import time

import pytest

import service_helpers
from common import sh


@pytest.fixture(scope="module")
def env():
    return service_helpers.ServiceEnv("mongod", "mongod ", ["/etc/mongod.conf"])


@pytest.fixture(autouse=True)
def _teardown(env):
    yield
    service_helpers.teardown_mongo(env)


def test_stop_mongo_if_running(env):
    env.stopit()


def test_start_mongo_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl")
    assert sh("systemctl start mongod").returncode == 0
    assert env.is_running()


def test_stop_mongo_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl")
    assert sh("systemctl stop mongod").returncode == 0
    assert not env.is_running()


def test_restart_mongo_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl")
    assert sh("systemctl restart mongod").returncode == 0
    assert env.is_running()


def test_stop_mongo_with_initd_start_with_systemctl(env):
    if not (env.systemctl and os.path.isfile("/etc/init.d/mongod")):
        pytest.skip("system doesn't have systemctl")
    assert sh("/etc/init.d/mongod stop").returncode == 0
    assert not env.is_running()
    assert sh("systemctl start mongod").returncode == 0
    assert env.is_running()


def test_start_mongo_with_initd_stop_with_systemctl(env):
    if not (env.systemctl and os.path.isfile("/etc/init.d/mongod")):
        pytest.skip("system doesn't have systemctl")
    if env.is_running():
        assert sh("systemctl stop mongod").returncode == 0
        assert not env.is_running()
    assert sh("/etc/init.d/mongod start 3>&-").returncode == 0
    assert env.is_running()
    assert sh("systemctl stop mongod").returncode == 0
    assert not env.is_running()


def test_start_mongo_with_service(env):
    if not env.service_cmd:
        pytest.skip("system doesn't have service command")
    assert sh("service mongod start 3>&-").returncode == 0
    assert env.is_running()


def test_stop_mongo_with_service(env):
    if not env.service_cmd:
        pytest.skip("system doesn't have service command")
    assert sh("service mongod stop").returncode == 0
    assert not env.is_running()


def test_restart_mongo_with_service(env):
    if not env.service_cmd:
        pytest.skip("system doesn't have service command")
    assert sh("service mongod restart 3>&-").returncode == 0
    assert env.is_running()


def test_check_if_mongo_service_is_enabled_in_systemd(env):
    if not env.systemctl:
        pytest.skip("system is 4.0 or doesn't have systemctl command")
    result = sh("systemctl is-enabled mongod").output.strip()
    assert result == "enabled"


def test_check_if_mongo_service_is_enabled_in_sysvinit(env):
    if env.systemctl:
        pytest.skip("init system is systemd so other test will do the check")
    elif env.sysvconfig:
        result = sh("sysv-rc-conf --list mongod|grep -o ':on'|wc -l").output.strip()
        assert int(result) > 3
    elif env.chkconfig:
        result = sh("chkconfig --list mongod|grep -o ':on'|wc -l").output.strip()
        assert int(result) > 1
    else:
        pytest.skip("system doesn't have chkconfig or sysv-rc-conf commands")


def test_add_nonexisting_option_and_start_with_systemctl(env):
    if not env.systemctl:
        pytest.skip("system doesn't have systemctl command")
    # The config file must exist once the package is installed; a missing one
    # is a real defect, so fail rather than skip.
    assert env.conf is not None, "mongo config file (/etc/mongod.conf) not found"
    env.stopit()
    sh('echo "nonexistingoption: true" >> {}'.format(env.conf))
    assert sh("systemctl start mongod").returncode == 1
    assert not env.is_running()
    time.sleep(10)


def test_add_nonexisting_option_and_start_with_service(env):
    if not env.service_cmd:
        pytest.skip("system doesn't have service command")
    # The config file must exist once the package is installed; a missing one
    # is a real defect, so fail rather than skip.
    assert env.conf is not None, "mongo config file (/etc/mongod.conf) not found"
    env.stopit()
    sh('echo "nonexistingoption: true" >> {}'.format(env.conf))
    assert sh("service mongod start").returncode == 1
    assert not env.is_running()
    time.sleep(10)
