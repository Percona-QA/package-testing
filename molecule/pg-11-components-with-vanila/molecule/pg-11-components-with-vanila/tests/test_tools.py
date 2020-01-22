import os
import pytest

import testinfra.utils.ansible_runner

from .settings import versions

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

pg_versions = versions['ppg-11.6']


@pytest.fixture(scope="module")
def operating_system(host):
    return host.system_info.distribution


@pytest.fixture()
def load_data(host, operating_system):
    pgbench = "pgbench -i -s 1"
    if operating_system.lower() in ["redhat", "centos", 'rhel']:
        pgbench = '/usr/pgsql-11/bin/pgbench'
    cmd = host.run(pgbench)
    assert cmd.rc == 0, cmd.stdout
    select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
    assert host.run(select).rc == 0


@pytest.fixture()
def pgaudit(host):
    os = host.system_info.distribution
    with host.sudo("postgres"):
        enable_library = "psql -c \'ALTER SYSTEM SET shared_preload_libraries=\'pgaudit\'\';"
        result = host.check_output(enable_library)
        assert result.strip("\n") == "ALTER SYSTEM"
        enable_pgaudit = "psql -c 'CREATE EXTENSION pgaudit;'"
        result = host.check_output(enable_pgaudit)
        assert result.strip("\n") == "CREATE EXTENSION"
        cmd = """
        psql -c \"SELECT setting FROM pg_settings WHERE name='shared_preload_libraries';\" | awk 'NR==3{print $1}'
        """
        result = host.check_output(cmd)
        assert result.strip("\n") == "pgaudit"
        enable_ddl = """psql -c \"ALTER SYSTEM SET pgaudit.log = 'all';\""""
        result = host.check_output(enable_ddl)
        assert result.strip("\n") == "ALTER SYSTEM"
        reload_conf = "psql -c 'SELECT pg_reload_conf();'"
        result = host.run(reload_conf)
        assert result.rc == 0
        create_table = "psql -c \"CREATE TABLE t1 (id int,name varchar(30));\""
        result = host.run(create_table)
        assert result.rc == 0
        assert result.stdout.strip("\n") == "CREATE TABLE"
        log_file = "/var/log/postgresql/postgresql-11-main.log"
        if os.lower() in ["debian", "ubuntu"]:
            log_file = "/var/log/postgresql/postgresql-11-main.log"
        elif os.lower() in ["redhat", "centos", 'rhel']:
            log_files = "ls /var/lib/pgsql/11/data/log/"
            file_name = host.check_output(log_files).strip("\n")
            log_file = "".join(["/var/lib/pgsql/11/data/log/", file_name])
        file = host.file(log_file)
        file_content = file.content_string
    yield file_content
    with host.sudo("postgres"):
        drop_pgaudit = "psql -c 'DROP EXTENSION pgaudit;'"
        result = host.check_output(drop_pgaudit)
        assert result.strip("\n") == "DROP EXTENSION"
    cmd = "sudo systemctl restart postgresql"
    if os.lower() in ["redhat", "centos", 'rhel']:
        cmd = "sudo systemctl restart postgresql-11"
    result = host.run(cmd)
    assert result.rc == 0


@pytest.fixture()
def pgbackrest(host):
    return host.run("file /usr/bin/pgbackrest")


@pytest.fixture()
def pgbackrest_version(host, operating_system):
    return host.check_output("pgbackrest version").strip("\n")


@pytest.fixture(scope="module")
def configure_postgres_pgbackrest(host):
    with host.sudo("postgres"):
        wal_senders = """psql -c \"ALTER SYSTEM SET max_wal_senders=3;\""""
        assert host.check_output(wal_senders).strip("\n") == "ALTER SYSTEM"
        wal_level = """psql -c \"ALTER SYSTEM SET wal_level='replica';\""""
        assert host.check_output(wal_level).strip("\n") == "ALTER SYSTEM"
        archive = """psql -c \"ALTER SYSTEM SET archive_mode='on';\""""
        assert host.check_output(archive).strip("\n") == "ALTER SYSTEM"
        archive_command = """
        psql -c \"ALTER SYSTEM SET archive_command = 'pgbackrest --stanza=testing archive-push %p';\"
        """
        assert host.check_output(archive_command).strip("\n") == "ALTER SYSTEM"
        reload_conf = "psql -c 'SELECT pg_reload_conf();'"
        result = host.run(reload_conf)
        assert result.rc == 0


@pytest.mark.usefixtures("configure_postgres_pgbackrest")
@pytest.fixture()
def create_stanza(host):
    with host.sudo("postgres"):
        cmd = "pgbackrest stanza-create --stanza=testing --log-level-console=info"
        return host.run(cmd)


@pytest.mark.usefixtures("configure_postgres_pgbackrest")
@pytest.fixture()
def pgbackrest_check(host):
    with host.sudo("postgres"):
        cmd = "pgbackrest check --stanza=testing --log-level-console=info"
        result = host.run(cmd)
        assert result.rc == 0
        return [l.split("INFO:")[-1] for l in result.stdout.split("\n") if "INFO" in l]


@pytest.mark.usefixtures("load_data")
@pytest.mark.usefixtures("configure_postgres_pgbackrest")
@pytest.fixture()
def pgbackrest_full_backup(host):
    with host.sudo("postgres"):
        cmd = "pgbackrest backup --stanza=testing --log-level-console=info"
        result = host.run(cmd)
        assert result.rc == 0
        return [l.split("INFO:")[-1] for l in result.stdout.split("\n") if "INFO" in l]


@pytest.mark.usefixtures("configure_postgres_pgbackrest")
@pytest.fixture()
def pgbackrest_delete_data(host):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        data_dir = "/var/lib/pgsql/11/data/*"
        service_name = "postgresql-11"
    else:
        data_dir = "/var/lib/postgresql/11/main/*"
        service_name = "postgresql"
    with host.sudo("root"):
        stop_postgresql = 'systemctl stop {}'.format(service_name)
        s = host.run(stop_postgresql)
        assert s.rc == 0
    with host.sudo("postgres"):
        cmd = "rm -rf {}".format(data_dir)
        result = host.run(cmd)
        assert result.rc == 0


@pytest.mark.usefixtures("configure_postgres_pgbackrest")
@pytest.fixture()
def pgbackrest_restore(pgbackrest_delete_data, host):
    with host.sudo("postgres"):
        result = host.run("pgbackrest --stanza=testing --log-level-stderr=info restore")
        assert result.rc == 0
        return [l.split("INFO:")[-1] for l in result.stdout.split("\n") if "INFO" in l]


@pytest.fixture()
def pgrepack(host):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        cmd = "file /usr/pgsql-11/bin/pg_repack "
    else:
        # TODO need to be in PATH?
        cmd = "file /usr/lib/postgresql/11/bin/pg_repack"
    return host.check_output(cmd)


@pytest.fixture()
def pg_repack_functional(host, operating_system):
    os = host.system_info.distribution
    with host.sudo("postgres"):
        pgbench = "pgbench -i -s 1"
        if operating_system.lower() in ["redhat", "centos", 'rhel']:
            pgbench = '/usr/pgsql-11/bin/pgbench'
        cmd = host.run(pgbench)
        assert cmd.rc == 0, cmd.stdout
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        assert host.run(select).rc == 0
        if os.lower() in ["redhat", "centos", 'rhel']:
            cmd = "/usr/pgsql-11/bin/pg_repack -t pgbench_accounts -j 4"
        else:
            # TODO need to be in PATH?
            cmd = "/usr/lib/postgresql/11/bin/pg_repack -t pgbench_accounts -j 4"
        pg_repack_result = host.run(cmd)
    yield pg_repack_result


@pytest.fixture()
def pg_repack_dry_run(host, operating_system):
    with host.sudo("postgres"):
        pgbench = "pgbench -i -s 1"
        if operating_system.lower() in ["redhat", "centos", 'rhel']:
            pgbench = '/usr/pgsql-11/bin/pgbench'
        cmd = host.run(pgbench)
        assert cmd.rc == 0, cmd.stdout
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        assert host.run(select).rc == 0
        if operating_system.lower() in ["redhat", "centos", 'rhel']:
            cmd = "/usr/pgsql-11/bin/pg_repack --dry-run -d postgres"
        else:
            cmd = "/usr/lib/postgresql/11/bin/pg_repack --dry-run -d postgres"
        pg_repack_result = host.run(cmd)
    yield pg_repack_result


@pytest.fixture()
def pg_repack_client_version(host, operating_system):
    with host.sudo("postgres"):
        if operating_system.lower() in ["redhat", "centos", 'rhel']:
            return host.run("/usr/pgsql-11/bin/pg_repack --version")
        elif operating_system.lower() in ["debian", "ubuntu"]:
            return host.run("/usr/lib/postgresql/11/bin/pg_repack --version")


@pytest.fixture()
def patroni(host):
    return host.run("/opt/patroni/bin/patroni")


@pytest.fixture()
def patroni_version(host):
    return host.run("/opt/patroni/bin/patroni --version")


def test_pgaudit_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os.lower() in ["redhat", "centos", 'rhel']:
        pkgn = "percona-pgaudit"
    elif os in ["debian", "ubuntu"]:
        pkgn = "percona-postgresql-11-pgaudit"
        dbgsym_pkgn = "percona-postgresql-11-pgaudit-dbgsym"
        dbgsym_pkg = host.package(dbgsym_pkgn)
        assert dbgsym_pkg.is_installed
        assert pg_versions['pgaudit']['version'] in dbgsym_pkg.version
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert pg_versions['pgaudit']['version'] in pkg.version


def test_pgaudit(pgaudit):
    assert "AUDIT" in pgaudit


def test_pgrepack_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os.lower() in ["redhat", "centos", 'rhel']:
        pkgn = "percona-pg_repack11"
    elif os in ["debian", "ubuntu"]:
        pkgn = "percona-postgresql-11-repack"
        pkg_dbgsym = host.package("percona-postgresql-11-repack-dbgsym")
        assert pkg_dbgsym.is_installed
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert pg_versions['pgrepack']['version'] in pkg.version


def test_pgrepack_binary(host, pgrepack):
    os = host.system_info.distribution
    if os.lower() == "centos":
        assert pgrepack == pg_versions['pgrepack']['binary']['centos'], pgrepack
    elif os.lower() in ['redhat', 'rhel']:
        assert pgrepack == pg_versions['pgrepack']['binary']['rhel'], pgrepack
    elif os.lower() == "debian":
        if host.system_info.release == '9.9':
            assert pgrepack == pg_versions['pgrepack']['binary']['debian9.9'], pgrepack
        else:
            assert pgrepack == pg_versions['pgrepack']['binary']['debian'], pgrepack
    elif os.lower() == "ubuntu":
        assert pgrepack == pg_versions['pgrepack']['binary']['ubuntu'], pgrepack


def test_pgrepack(host):
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION \"pg_repack\";'")
        try:
            assert install_extension.rc == 0
            assert install_extension.stdout.strip("\n") == "CREATE EXTENSION"
        except AssertionError:
            pytest.fail("Return code {}. Stderror: {}. Stdout {}".format(install_extension.rc,
                                                                         install_extension.stderr,
                                                                         install_extension.stdout))
            extensions = host.run("psql -c 'SELECT * FROM pg_extension;' | awk 'NR>=3{print $1}'")
            assert extensions.rc == 0
            assert "pg_repack" in set(extensions.stdout.split())


def test_pg_repack_client_version(pg_repack_client_version):
    assert pg_repack_client_version.rc == 0
    assert pg_repack_client_version.stdout.strip("\n") == pg_versions['pgrepack']['binary_version']


def test_pg_repack_functional(pg_repack_functional):
    assert pg_repack_functional.rc == 0
    messages = pg_repack_functional.stderr.split("\n")
    assert 'NOTICE: Setting up workers.conns' in messages
    assert 'NOTICE: Setting up workers.conns', 'INFO: repacking table "public.pgbench_accounts"' in messages


def test_pg_repack_dry_run(pg_repack_dry_run):
    assert pg_repack_dry_run.rc == 0
    messages = pg_repack_dry_run.stderr.split("\n")
    assert 'INFO: Dry run enabled, not executing repack' in messages
    assert 'INFO: repacking table "public.pgbench_accounts"' in messages
    assert 'INFO: repacking table "public.pgbench_branches"' in messages
    assert 'INFO: repacking table "public.pgbench_tellers"' in messages


def test_pgbackrest_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os.lower() in ["redhat", "centos", 'rhel']:
        pkgn = "percona-pgbackrest"
    elif os in ["debian", "ubuntu"]:
        pkgn = "percona-pgbackrest"
        doc_pkgn = "percona-pgbackrest-doc"
        docs_pkg = host.package(doc_pkgn)
        assert docs_pkg.is_installed
        assert pg_versions['pgbackrest']['version'] in docs_pkg.version
        dbg_pkg = "percona-pgbackrest-dbgsym"
        dbg = host.package(dbg_pkg)
        assert dbg.is_installed
        assert pg_versions['pgbackrest']['version'] in dbg.version
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert pg_versions['pgbackrest']['version'] in pkg.version


def test_pgbackrest_version(pgbackrest_version):
    assert pgbackrest_version == pg_versions['pgbackrest']['binary_version']


def test_pgbackrest_binary(pgbackrest, operating_system, host):
    assert pgbackrest.rc == 0
    if operating_system.lower() == "centos":
        assert pgbackrest.stdout.strip("\n") == pg_versions['pgbackrest']['binary']['centos'],\
            pgbackrest.stdout.strip("\n")
    elif operating_system.lower() in ["redhat", 'rhel']:
        assert pgbackrest.stdout.strip("\n") == pg_versions['pgbackrest']['binary']['rhel'],\
            pgbackrest.stdout.strip("\n")
    elif operating_system.lower() == 'debian':
        if host.system_info.release == "9.9":
            assert pgbackrest.stdout.strip("\n") == pg_versions['pgbackrest']['binary']['debian9.9'],\
                pgbackrest.stdout.strip("\n")
        else:
            assert pgbackrest.stdout.strip("\n") == pg_versions['pgbackrest']['binary']['debian'],\
                pgbackrest.stdout.strip("\n")
    elif operating_system.lower == "ubuntu":
        assert pgbackrest.stdout.strip("\n") == pg_versions['pgbackrest']['binary']['ubuntu'],\
            pgbackrest.stdout.strip("\n")


def test_pgbackrest_create_stanza(create_stanza):
    assert "INFO: stanza-create command end: completed successfully" in create_stanza.stdout


def test_pgbackrest_check(pgbackrest_check):
    assert "check command end: completed successfully" in pgbackrest_check[-1]


def test_pgbackrest_full_backup(pgbackrest_full_backup):
    assert "expire command end: completed successfully" in pgbackrest_full_backup[-1]


def test_pgbackrest_restore(host):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos", 'rhel']:
        service_name = "postgresql-11"
    else:
        service_name = "postgresql"
    with host.sudo("root"):
        stop_postgresql = 'systemctl start {}'.format(service_name)
        assert host.run(stop_postgresql).rc == 0
    with host.sudo("postgres"):
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        result = host.run(select)
        assert result.rc == 0
        assert result.stdout.strip("\n") == "100000"


def test_patroni_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os.lower() in ["ubuntu", "redhat", "centos", 'rhel']:
        pkgn = "percona-patroni"
    elif os == "debian":
        pkgn = "percona-patroni"
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert pg_versions['patroni']['version'] in pkg.version


def test_patroni_version(patroni_version):
    assert patroni_version.rc == 0, patroni_version.stderr
    assert patroni_version.stdout.strip("\n") == pg_versions['patroni']['binary_version']
