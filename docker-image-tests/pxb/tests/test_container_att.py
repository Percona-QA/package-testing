#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
from settings import *


container_name = 'pxb-docker-test'


@pytest.fixture(scope='module')
def host():
    subprocess.call(['docker', 'rm', '-f', container_name],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '--entrypoint', 'sleep',
         '-d', docker_image, 'infinity']
    ).decode().strip()
    yield testinfra.get_host("docker://root@" + docker_id)
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestPxbBinaries:
    @pytest.mark.parametrize("binary", pxb_binaries)
    def test_binary_exists(self, host, binary):
        assert host.find_command(binary), f"{binary} not found in PATH"

    @pytest.mark.parametrize("binary", pxb_binaries)
    def test_binary_version(self, host, binary):
        output = host.check_output(f'{binary} --version 2>&1')
        assert pxb_version in output, (
            f"Expected version {pxb_version} in '{binary} --version' output: {output}"
        )

    @pytest.mark.parametrize("binary", pxb_binaries)
    def test_binary_revision(self, host, binary):
        if not pxb_revision:
            pytest.skip("PXB_REVISION not set")
        output = host.check_output(f'{binary} --version 2>&1')
        assert pxb_revision in output, (
            f"Expected revision {pxb_revision} in '{binary} --version' output: {output}"
        )
