import os
import pytest

import testinfra.utils.ansible_runner

from molecule.ppg.tests.settings import get_settings, MAJOR_VER

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
pg_versions = get_settings(os.environ['MOLECULE_SCENARIO_NAME'])[os.getenv("VERSION")]
EXTENSIONS = pg_versions['extensions']


@pytest.fixture()
def postgresql_binary(host):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        return host.file("/usr/pgsql-{}/bin/postgres".format(MAJOR_VER))
    elif os in ["debian", "ubuntu"]:
        return host.file("/usr/lib/postgresql/{}/bin/postgres".format(MAJOR_VER))


@pytest.fixture()
def postgresql_query_version(host):
    with host.sudo("postgres"):
        return host.run("psql -c 'SELECT version()' | awk 'NR==3{print $2}'")


@pytest.fixture()
def extension_list(host):
    with host.sudo("postgres"):
        result = host.check_output("psql -c 'SELECT * FROM pg_available_extensions;' | awk 'NR>=3{print $1}'")
        result = result.split()
        return result


@pytest.fixture()
def insert_data(host):
    with host.sudo("postgres"):
        pgbench = "pgbench -i -s 1"
        result = host.run(pgbench)
        assert result.rc == 0
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        result = host.check_output(select)
    yield result.strip("\n")


def test_psql_client_version(host):
    result = host.run('psql --version')
    assert pg_versions['version'] in result.stdout, result.stdout


def test_postgresql_client_version(host):
    os = host.system_info.distribution
    pkg = "percona-postgresql-{}".format(MAJOR_VER)
    if os.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(pkg)
    assert MAJOR_VER in pkg.version


def test_postgresql_version(host):
    os = host.system_info.distribution
    pkg = "percona-postgresql-client-{}".format(MAJOR_VER)
    if os.lower() in ["redhat", "centos", 'rhel']:
        pkg = "percona-postgresql{}".format(MAJOR_VER)
    pkg = host.package(pkg)
    assert MAJOR_VER in pkg.version


def test_postgresql_is_running_and_enabled(host):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        postgresql = host.service("postgresql-{}".format(MAJOR_VER))
    else:
        postgresql = host.service("postgresql")
    assert postgresql.is_running


def test_postgres_binary(postgresql_binary):
    assert postgresql_binary.exists
    assert postgresql_binary.user == "root"


def test_pg_config_server_version(host):
    cmd = "pg_config --version"
    result = host.check_output(cmd)
    assert MAJOR_VER in result, result.stdout


def test_postgresql_query_version(postgresql_query_version):
    assert postgresql_query_version.rc == 0, postgresql_query_version.stderr
    assert postgresql_query_version.stdout.strip("\n") == pg_versions['version'], postgresql_query_version.stdout


def test_postgres_client_version(host):
    cmd = "psql --version"
    result = host.check_output(cmd)
    assert MAJOR_VER in result.strip("\n"), result.stdout


def test_insert_data(insert_data):
    assert insert_data == "100000", insert_data


def test_extenstions_list(extension_list, host):
    ds = host.system_info.distribution
    for extension in EXTENSIONS:
        if ds.lower() in ['centos', 'redhat', 'rhel']:
            if "python3" in extension:
                pytest.skip("Skipping python3 extensions for Centos or RHEL")
        if ds.lower() in ['debian', 'ubuntu'] and os.getenv("VERSION") in ["ppg-11.8", 'ppg-12.2', 'ppg-12.3']:
            if extension in ['plpythonu', "plpython2u", 'jsonb_plpython2u', 'ltree_plpython2u', 'jsonb_plpythonu',
                             'ltree_plpythonu', 'hstore_plpythonu', 'hstore_plpython2u']:
                pytest.skip("Skipping python2 extensions for DEB based in 12.2 pg")
        assert extension in extension_list


@pytest.mark.parametrize("extension", EXTENSIONS)
def test_enable_extension(host, extension):
    ds = host.system_info.distribution
    if ds.lower() in ["redhat", "centos", 'rhel']:
        if "python3" in extension:
            pytest.skip("Skipping python3 extensions for Centos or RHEL")
    if ds.lower() in ['debian', 'ubuntu'] and os.getenv("VERSION") in ["ppg-11.8", 'ppg-12.2', 'ppg-12.3']:
        if extension in ['plpythonu', "plpython2u", 'jsonb_plpython2u', 'ltree_plpython2u', 'jsonb_plpythonu',
                         'ltree_plpythonu', 'hstore_plpythonu', 'hstore_plpython2u']:
            pytest.skip("Skipping python2 extensions for DEB based in 12.2 pg")
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION \"{}\";'".format(extension))
        assert install_extension.rc == 0, install_extension.stderr
        assert install_extension.stdout.strip("\n") == "CREATE EXTENSION", install_extension.stderr
        extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $3}'")
        if "11" in os.getenv("VERSION"):
            extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $1}'")
        assert extensions.rc == 0, extensions.stderr
        assert extension in set(extensions.stdout.split()), extensions.stdout


@pytest.mark.parametrize("extension", EXTENSIONS[::-1])
def test_drop_extension(host, extension):
    ds = host.system_info.distribution
    if ds.lower() in ["redhat", "centos", 'rhel']:
        if "python3" in extension:
            pytest.skip("Skipping python3 extensions for Centos or RHEL")
    if ds.lower() in ['debian', 'ubuntu'] and os.getenv("VERSION") in ["ppg-11.8", 'ppg-12.2', 'ppg-12.3']:
        if extension in ['plpythonu', "plpython2u", 'jsonb_plpython2u', 'ltree_plpython2u', 'jsonb_plpythonu',
                         'ltree_plpythonu', 'hstore_plpythonu', 'hstore_plpython2u']:
            pytest.skip("Skipping python2 extensions for DEB based in 12.2 pg")
    with host.sudo("postgres"):
        drop_extension = host.run("psql -c 'DROP EXTENSION \"{}\";'".format(extension))
        assert drop_extension.rc == 0, drop_extension.stderr
        assert drop_extension.stdout.strip("\n") == "DROP EXTENSION", drop_extension.stdout
        extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $3}'")
        if "11" in os.getenv("VERSION"):
            extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $1}'")
        assert extensions.rc == 0, extensions.stderr
        assert extension not in set(extensions.stdout.split()), extensions.stdout


def test_plpgsql_extension(host):
    with host.sudo("postgres"):
        extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $3}'")
        if "11" in os.getenv("VERSION"):
            extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $1}'")
        assert extensions.rc == 0, extensions.stderr
        assert "plpgsql" in set(extensions.stdout.split()), extensions.stdout
