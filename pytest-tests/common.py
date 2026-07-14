#!/usr/bin/env python3
"""Shared, import-friendly helpers for the pytest package-testing suites.

Kept separate from ``conftest.py`` so the plugin/service helper modules can
import ``sh`` / ``Result`` without depending on pytest's conftest machinery.
"""
import os
import re
import subprocess


class Result:
    """Wrapper around ``subprocess`` output that mimics bats' ``run`` result.

    In bats, after ``run <cmd>`` you inspect ``$status`` and ``${lines[N]}``.
    Here the equivalents are ``.returncode`` / ``.status`` and ``.lines[N]``.
    bats merged stderr into stdout, so ``.lines`` / ``.output`` combine both.
    """

    def __init__(self, completed):
        self.returncode = completed.returncode
        self.stdout = completed.stdout or ""
        self.stderr = completed.stderr or ""

    @property
    def status(self):  # bats aliased the exit code as $status
        return self.returncode

    @property
    def lines(self):
        # bats builds its ${lines[@]} via `IFS=$'\n' lines=($output)`, whose
        # unquoted word-splitting drops empty lines. Replicate that so line
        # indices match the originals (e.g. a password prompt emits a leading
        # blank line that bats never saw).
        return [l for l in (self.stdout + self.stderr).splitlines() if l != ""]

    @property
    def output(self):
        return (self.stdout + self.stderr).rstrip("\n")


def sh(cmd, **kwargs):
    """Run ``cmd`` via the shell and return a :class:`Result`.

    ``cmd`` may be a string (run with ``shell=True``) or a list. Never raises on
    non-zero exit — callers assert on ``.returncode`` just like bats did.
    """
    shell = isinstance(cmd, str)
    completed = subprocess.run(
        cmd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        **kwargs,
    )
    return Result(completed)


def sql(connection, query):
    """Run a mysql query with the standard ``-N -s`` flags and return trimmed stdout."""
    return sh('mysql {conn} -N -s -e {q}'.format(
        conn=connection, q=_shell_quote(query))).output.strip()


def _shell_quote(value):
    import shlex
    return shlex.quote(value)


def detect_mysql_version():
    """Parse ``X.Y`` out of ``mysqld --version`` (matches bats grep '[0-9]\\.[0-9]')."""
    out = sh("mysqld --version").output
    match = re.search(r"[0-9]\.[0-9]", out)
    return match.group(0) if match else ""


def detect_mongo_version():
    """Parse ``X.Y`` out of the ``mongo --version`` shell line."""
    out = sh("mongo --version").output
    for line in out.splitlines():
        if "shell" in line:
            match = re.search(r"[0-9]\.[0-9]", line)
            if match:
                return match.group(0)
    match = re.search(r"[0-9]\.[0-9]", out)
    return match.group(0) if match else ""


def detect_connection():
    """Return the mysql client connection args, honoring $CONNECTION.

    Mirrors bats helper logic: prefer /run/mysqld/mysqld.sock, else
    /var/lib/mysql/mysql.sock.
    """
    env = os.getenv("CONNECTION")
    if env:
        return env
    if os.path.exists("/run/mysqld/mysqld.sock"):
        return "-S/run/mysqld/mysqld.sock"
    return "-S/var/lib/mysql/mysql.sock"


def which(cmd):
    """True if ``cmd`` is on PATH (equivalent of bats' `which X` probes)."""
    return sh("which {} 2>/dev/null".format(cmd)).output.strip() != ""


def is_root():
    return os.geteuid() == 0
