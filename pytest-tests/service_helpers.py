#!/usr/bin/env python3
"""Shared init-system helpers for the *-init-scripts test modules.

Ports the capability probing and ``is_running`` / ``stopit`` / ``fix_timeout`` /
``teardown`` shell functions that were duplicated at the top of
``mysql-init-scripts.bats``, ``pxc-init-scripts.bats`` and
``mongo-init-scripts.bats``.
"""
import os

from common import sh, which


class ServiceEnv:
    """Captures init-system capabilities and service/config identity."""

    def __init__(self, service, proc_pattern, conf_candidates):
        self.service = service            # systemd/service unit name, e.g. "mysql" / "mongod"
        self.proc_pattern = proc_pattern  # ps grep pattern, e.g. "mysqld" / "mongod "
        self.systemctl = which("systemctl")
        self.service_cmd = which("service")
        self.sysvconfig = which("sysv-rc-conf")
        self.chkconfig = which("chkconfig")
        self.conf = next((c for c in conf_candidates if os.path.isfile(c)), None)

    def is_running(self):
        """True if the daemon process is up (and systemd reports active)."""
        count = sh("ps aux | grep -v grep | grep '{}' | wc -l".format(self.proc_pattern)).output.strip()
        if count in ("", "0"):
            return False
        if self.systemctl and not self._is_active():
            return False
        return True

    def _is_active(self):
        # Check is-active's return code (0 iff active) rather than string-matching
        # stdout: our sh() merges stderr into stdout, so a systemctl warning
        # (e.g. "unit file changed on disk, run daemon-reload") would corrupt an
        # "active" match. Also handle mysql.service being an alias of
        # mysqld.service (see PS-8675), mirroring the is-enabled check.
        if sh("systemctl is-active --quiet {}".format(self.service)).returncode == 0:
            return True
        if self.service == "mysql":
            return sh("systemctl is-active --quiet mysqld").returncode == 0
        return False

    def stopit(self):
        if self.is_running():
            if self.systemctl:
                assert sh("systemctl stop {}".format(self.service)).returncode == 0
            else:
                assert sh("service {} stop".format(self.service)).returncode == 0
            assert not self.is_running()

    def fix_timeout(self):
        """Shorten mysql start timeouts so failure cases return quickly."""
        if os.path.isfile("/etc/default/mysql"):
            sh("sed -i 's/STARTTIMEOUT=900/STARTTIMEOUT=30/g' /etc/default/mysql")
            sh("sed -i 's/startup_timeout=900/startup_timeout=30/g' /etc/default/mysql")
        if self.systemctl and os.path.isfile("/lib/systemd/system/mysql.service"):
            sh("sed -i 's/TimeoutSec=600/TimeoutSec=30/g' /lib/systemd/system/mysql.service")
            sh("systemctl daemon-reload")


def teardown_mysql_family(env):
    """Revert edits made by the mysql/pxc init-scripts tests (bats teardown())."""
    if os.path.isfile("/etc/default/mysql"):
        sh("sed -i 's/STARTTIMEOUT=30/STARTTIMEOUT=900/g' /etc/default/mysql")
    if env.systemctl and os.path.isfile("/lib/systemd/system/mysql.service"):
        sh("sed -i 's/TimeoutSec=30/TimeoutSec=600/g' /lib/systemd/system/mysql.service")
        sh("systemctl daemon-reload")
    if env.conf and os.path.isfile(env.conf):
        sh("sed -i '${{/nonexistingoption=1/d}}' {}".format(env.conf))
        sh("sed -i '${{/\\[mysqld\\]/d}}' {}".format(env.conf))


def teardown_mongo(env):
    """Revert edits made by the mongo init-scripts tests (bats teardown())."""
    if env.conf and os.path.isfile(env.conf):
        sh("sed -i '${{/nonexistingoption: true/d}}' {}".format(env.conf))
