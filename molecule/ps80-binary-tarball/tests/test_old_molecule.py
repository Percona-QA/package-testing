#!/usr/bin/env python3
import pytest
import testinfra
import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_regular_tarball(host):
    """
    run.sh owns BASE_DIR and extraction logic.
    This test only executes it.
    """
    cmd = "cd /package-testing/binary-tarball-tests/ps && ./run.sh"
    result = host.run(cmd)

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    assert result.rc == 0

