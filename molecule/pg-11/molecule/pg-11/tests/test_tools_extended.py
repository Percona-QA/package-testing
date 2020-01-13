import os
import pytest

import testinfra.utils.ansible_runner

from .settings import versions


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

PACKAGES = ["libecpg-compat3", "libecpg-compat3-dbgsym", "libecpg-dev-dbgsym", "libecpg-dev", "libecpg6-dbgsym",
            'libecpg6', "libpgtypes3", "libpgtypes3-dbgsym", "libpq-dev", "libpq5-dbgsym", "libpq5"]

pg_versions = versions[os.getenv("PG_VERSION")]

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
def pythonu_function(host):
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION IF NOT EXISTS\"plpythonu\";'")
        assert install_extension.rc == 0
        create_function = """CREATE FUNCTION pymax (a integer, b integer)
          RETURNS integer
        AS $$
          if a > b:
            return a
          return b
        $$ LANGUAGE plpythonu;
                """
        execute_psql = host.run("psql -c \'{}\'".format(create_function))
        assert execute_psql.rc == 0
        assert execute_psql.stdout.strip("\n") == "CREATE FUNCTION"
        return execute_psql


@pytest.fixture()
def perl_function(host):
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION IF NOT EXISTS \"plperl\";'")
        assert install_extension.rc == 0
        create_function = """CREATE FUNCTION perl_max (integer, integer) RETURNS integer AS $$
    if ($_[0] > $_[1]) { return $_[0]; }
    return $_[1];
$$ LANGUAGE plperl;
        """
        execute_psql = host.run("psql -c \'{}\'".format(create_function))
        assert execute_psql.rc == 0
        assert execute_psql.stdout.strip("\n") == "CREATE FUNCTION"
        return execute_psql


@pytest.fixture()
def python3_function(host):
    os = host.system_info.distribution
    if os.lower() in ['centos', 'redhat', 'rhel']:
        pytest.skip("Skipping python3 extensions for Centos or RHEL")
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION IF NOT EXISTS \"plpython3u\";'")
        assert install_extension.rc == 0
        create_function = """CREATE FUNCTION pymax3 (a integer, b integer)
                  RETURNS integer
                AS $$
                  if a > b:
                    return a
                  return b
                $$ LANGUAGE plpython3u;
                        """
        execute_psql = host.run("psql -c \'{}\'".format(create_function))
        assert execute_psql.rc == 0, execute_psql.stderr
        assert execute_psql.stdout.strip("\n") == "CREATE FUNCTION", execute_psql.stdout
        return execute_psql


@pytest.fixture()
def tcl_function(host):
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION IF NOT EXISTS \"pltcl\";'")
        assert install_extension.rc == 0
        create_function = """CREATE FUNCTION tcl_max(integer, integer) RETURNS integer AS $$
    if {$1 > $2} {return $1}
    return $2
$$ LANGUAGE pltcl STRICT;
        """
        execute_psql = host.run("psql -c \'{}\'".format(create_function))
        assert execute_psql.rc == 0
        assert execute_psql.stdout.strip("\n") == "CREATE FUNCTION"
        return execute_psql


@pytest.fixture()
def build_libpq_programm(host):
    os = host.system_info.distribution
    pg_include_cmd = "pg_config --includedir"
    pg_include = host.check_output(pg_include_cmd)
    lib_dir_cmd = "pg_config --libdir"
    lib_dir = host.check_output(lib_dir_cmd)
    if os in ["centos", 'rhel', "redhat"]:
        return host.run(
            "export LIBPQ_DIR=/usr/pgsql-11/  && export LIBRARY_PATH=/usr/pgsql-11/lib/ &&"
            "gcc -o lib_version /tmp/libpq_command_temp_dir/lib_version.c -I{} -lpq -std=c99".format(pg_include))
    return host.run(
        "gcc -o lib_version /tmp/libpq_command_temp_dir/lib_version.c -I{} -lpq -std=c99".format(pg_include))


@pytest.mark.parametrize("package", PACKAGES)
def test_deb_package_is_installed(host, package):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert pkg.version in pg_versions['deb_pkg_ver']


def test_build_libpq_programm(host, build_libpq_programm):
    assert build_libpq_programm.rc == 0
    libpq_version = host.run("./lib_version ")
    assert libpq_version.stdout.strip("\n") == pg_versions['libpq']
    assert libpq_version.rc == 0


def test_pythonu_function(host, pythonu_function):
    with host.sudo("postgres"):
        result = host.run("psql -c \'SELECT pymax(1, 2);\' | awk 'NR>=3{print $1}'")
        assert result.rc == 0
        assert result.stdout.strip("\n(1") == "2"


def test_perl_function(host, perl_function):
    with host.sudo("postgres"):
        result = host.run("psql -c \'SELECT perl_max(1, 2);\' | awk 'NR>=3{print $1}'")
        assert result.rc == 0
        assert result.stdout.strip("\n(1") == "2"


def test_tcl_function(host, tcl_function):
    with host.sudo("postgres"):
        result = host.run("psql -c \'SELECT tcl_max(1, 2);\' | awk 'NR>=3{print $1}'")
        assert result.rc == 0
        assert result.stdout.strip("\n(1") == "2"


def test_python3(host, python3_function):
    with host.sudo("postgres"):
        result = host.run("psql -c \'SELECT pymax3(1, 2);\' | awk 'NR>=3{print $1}'")
        assert result.rc == 0
        assert result.stdout.strip("\n(1") == "2"
