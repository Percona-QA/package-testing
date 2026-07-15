"""Run parameters passed via `pyinfra --data`, with molecule-compatible defaults.

Shared by all deploy files so the bootstrap and the two joiner phases read the
same values the same way. Empty strings are treated as "not set" (mirrors the
molecule `lookup('env', ...) == ""` defaults).
"""

from pyinfra import host


def _get(name, default):
    value = host.data.get(name)
    return value if value not in (None, "") else default


def product():
    return _get("product", "pxc80")


def install_repo():
    return _get("install_repo", "main")


def check_version():
    return _get("check_version", "yes")


def git_account():
    return _get("git_account", "Percona-QA")


def testing_branch():
    return _get("testing_branch", "master")


def upgrade_repo():
    # empty for the install test type -> the telemetry-blocked re-install runs,
    # same as the molecule converge (upgrade flows will set this later)
    return _get("upgrade_repo", "")
