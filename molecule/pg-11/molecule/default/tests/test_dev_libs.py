import os
import pytest

import testinfra.utils.ansible_runner

from .settings import DEB_PKG_VERSIONS


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

PACKAGES = ["libecpg-compat3", "libecpg-compat3-dbgsym", "libecpg-dev-dbgsym", "libecpg-dev", "libecpg6-dbgsym",
            'libecpg6', "libpgtypes3", "libpgtypes3-dbgsym", "libpq-dev", "libpq5-dbgsym", "libpq5"]


# @pytest.fixture()
# def fdw_extension(host):
#     with host.sudo("postgres"):
#         install_extension = host.run("psql -c 'CREATE EXTENSION \"postgres_fdw\";'")
#         try:
#             assert install_extension.rc == 0
#             assert install_extension.stdout.strip("\n") == "CREATE EXTENSION"
#         except AssertionError:
#             pytest.fail("Return code {}. Stderror: {}. Stdout {}".format(install_extension.rc,
#                                                                          install_extension.stderr,
#                                                                          install_extension.stdout))
#
#         try:
#             extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $1}'")
#             assert extensions.rc == 0
#             assert "postgres_fdw" in set(extensions.stdout.split())
#         except AssertionError:
#             pytest.fail("Return code {}. Stderror: {}. Stdout {}").format(extensions.rc, extensions.stderr,
#                                                                           extensions.stdout)
#
#
# @pytest.fixture()
# def fdw_functional(host):
#     pass


@pytest.fixture()
def build_libpq_programm(host):
    pg_include_cmd = "pg_config --includedir"
    pg_include = host.check_output(pg_include_cmd)
    lib_dir_cmd = "pg_config --libdir"
    lib_dir = host.check_output(lib_dir_cmd)
    print(lib_dir)
    return host.run(
        "gcc -o lib_version /tmp/libpq_command_temp_dir/lib_version.c -I{} -lpq -std=c99".format(pg_include))


@pytest.mark.parametrize("package", PACKAGES)
def test_deb_package_is_installed(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert pkg.version in DEB_PKG_VERSIONS


def test_build_libpq_programm(build_libpq_programm):
    print(build_libpq_programm.stdout)
    print(build_libpq_programm.stderr)


# def test_fdw_extenstion(fdw_extension):
#     pass
#
#
# def test_fdw_functional(fdw_functional):
#     pass
