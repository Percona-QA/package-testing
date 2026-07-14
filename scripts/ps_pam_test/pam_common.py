#!/usr/bin/env python3
"""Shared helpers for the PAM pytest tests (ported from the *.bats versions).

These run locally on the target host where Percona Server is installed and drive
the ``mysql`` client through plain ``subprocess`` calls.
"""
import os
import shlex
import subprocess


class Result:
    def __init__(self, completed):
        self.returncode = completed.returncode
        self.stdout = completed.stdout or ""

    @property
    def out(self):
        return self.stdout.strip()


def sh(cmd, env=None):
    """Run ``cmd`` via the shell and return a :class:`Result` (stderr merged)."""
    full_env = None
    if env:
        full_env = dict(os.environ)
        full_env.update(env)
    completed = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=full_env,
    )
    return Result(completed)


def detect_connection():
    """Return the mysql client connection args, honoring $CONNECTION."""
    env = os.getenv("CONNECTION")
    if env:
        return env
    if os.path.exists("/run/mysqld/mysqld.sock"):
        return "-S/run/mysqld/mysqld.sock"
    return "-S/var/lib/mysql/mysql.sock"


def run_mysql(connection, query, db=None, user=None, password=None, env=None,
              suppress_stderr=False, check=False):
    """Run a ``mysql -N -s -e <query>`` command, mirroring the bats invocations.

    ``suppress_stderr`` appends ``2>/dev/null`` (used by the bats count/proxy
    queries so the captured output is clean). When ``check`` is true the call
    asserts the command exited 0, so a failing setup statement fails the test
    immediately instead of being silently ignored.
    """
    cmd = "mysql {conn} -N -s".format(conn=connection)
    if user is not None:
        cmd += " -u{}".format(user)
    if password is not None:
        cmd += " -p{}".format(password)
    cmd += " -e {}".format(shlex.quote(query))
    if db:
        cmd += " " + db
    if suppress_stderr:
        cmd += " 2>/dev/null"
    result = sh(cmd, env=env)
    if check:
        assert result.returncode == 0, (
            "mysql command failed (rc={}): {}\n{}".format(
                result.returncode, query, result.stdout))
    return result
