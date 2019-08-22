import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture(scope="module")
def operating_system(host):
    return host.system_info.distribution


@pytest.fixture()
def load_data(host):
    pgbench = "pgbench -i -s 1"
    assert host.run(pgbench).rc == 0
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
        elif os.lower() in ["redhat", "centos"]:
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
        print(result.stdout)
        print(result.stderr)
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
    if os.lower() in ["redhat", "centos"]:
        data_dir = "/var/lib/pgsql/11/data/*"
        service_name = "postgresql-11"
    else:
        data_dir = "/var/lib/postgresql/11/main/*"
        service_name = "postgresql"
    with host.sudo("root"):
        stop_postgresql = 'systemctl stop {}'.format(service_name)
        s = host.run(stop_postgresql)
        print(s.stderr)
        print(s.stdout)
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
        print(result.stdout)
        return [l.split("INFO:")[-1] for l in result.stdout.split("\n") if "INFO" in l]


@pytest.fixture()
def pgrepack(host):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos"]:
        cmd = "file /usr/pgsql-11/bin/pg_repack "
    else:
        # TODO need to be in PATH?
        cmd = "file /usr/lib/postgresql/11/bin/pg_repack"
    return host.check_output(cmd)


@pytest.fixture()
def pg_repack_functional(host):
    os = host.system_info.distribution
    with host.sudo("postgres"):
        pgbench = "pgbench -i -s 1"
        assert host.run(pgbench).rc == 0
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        assert host.run(select).rc == 0
        if os.lower() in ["redhat", "centos"]:
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
        assert host.run(pgbench).rc == 0
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        assert host.run(select).rc == 0
        if operating_system.lower() in ["redhat", "centos"]:
            cmd = "/usr/pgsql-11/bin/pg_repack --dry-run -d postgres"
        else:
            cmd = "/usr/lib/postgresql/11/bin/pg_repack --dry-run -d postgres"
        pg_repack_result = host.run(cmd)
    yield pg_repack_result


@pytest.fixture()
def pg_repack_client_version(host, operating_system):
    with host.sudo("postgres"):
        if operating_system.lower() in ["redhat", "centos"]:
            return host.run("/usr/pgsql-11/bin/pg_repack --version")
        elif operating_system.lower() in ["debian", "ubuntu"]:
            return host.run("/usr/lib/postgresql/11/bin/pg_repack --version")


@pytest.fixture()
def patroni(host):
    pass


def test_pgaudit_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os.lower() in ["redhat", "centos"]:
        pkgn = "percona-pgaudit"
    elif os in ["debian", "ubuntu"]:
        pkgn = "percona-postgresql-11-pgaudit"
        dbgsym_pkgn = "percona-postgresql-11-pgaudit-dbgsym"
        dbgsym_pkg = host.package(dbgsym_pkgn)
        assert dbgsym_pkg.is_installed
        assert "1.3" in dbgsym_pkg.version
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "1.3" in pkg.version


def test_pgaudit(pgaudit):
    assert "AUDIT" in pgaudit


def test_pgrepack_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os.lower() in ["redhat", "centos"]:
        pkgn = "percona-pg_repack11"
    elif os in ["debian", "ubuntu"]:
        pkgn = "percona-postgresql-11-repack"
        pkg_dbgsym = host.package("percona-postgresql-11-repack-dbgsym")
        assert pkg_dbgsym.is_installed
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "1.4" in pkg.version


def test_pgrepack_binary(host, pgrepack):
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos"]:
        assert pgrepack == "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable, x86-64," \
                           " version 1 (SYSV), dynamically linked (uses shared libs)," \
                           " for GNU/Linux 2.6.32, BuildID[sha1]=b76f53a7d4ffe7dfab0d9bd5868e99bdfcfe48e9, not stripped"
    elif os.lower() == "debian":
        if host.system_info.release == '9.9':
            assert pgrepack == "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object," \
                           " x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2," \
                           " for GNU/Linux 2.6.32, BuildID[sha1]=0f89ea7cb7dcbe4435aefd2c74be0505a818614b, stripped"
        else:
            assert pgrepack == "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object," \
                               " x86-64, version 1 (SYSV), dynamically linked," \
                               " interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0," \
                               " BuildID[sha1]=9aef45d1e9a16645857aba84473dd8f150998d90, stripped"
    elif os.lower() == "ubuntu":
        assert pgrepack == "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object," \
                           " x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l," \
                           " for GNU/Linux 3.2.0, BuildID[sha1]=79aca6e4d94f971b1adc16c4d523ce69a85ad1d4, stripped"


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
    assert pg_repack_client_version.stdout.strip("\n") == "pg_repack 1.4.4"


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
    if os.lower() in ["redhat", "centos"]:
        pkgn = "percona-pgbackrest"
    elif os in ["debian", "ubuntu"]:
        pkgn = "percona-pgbackrest"
        doc_pkgn = "percona-pgbackrest-doc"
        docs_pkg = host.package(doc_pkgn)
        assert docs_pkg.is_installed
        assert "2.16" in docs_pkg.version
        dbg_pkg = "percona-pgbackrest-dbgsym"
        dbg = host.package(dbg_pkg)
        assert dbg.is_installed
        assert "2.16" in dbg.version
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "2.16" in pkg.version


def test_pgbackrest_version(pgbackrest_version):
    assert pgbackrest_version == "pgBackRest 2.16"


def test_pgbackrest_binary(pgbackrest, operating_system, host):
    assert pgbackrest.rc == 0
    if operating_system.lower() in ["redhat", "centos"]:
        assert pgbackrest.stdout.strip("\n") == "/usr/bin/pgbackrest: ELF 64-bit LSB executable," \
                                                " x86-64, version 1 (SYSV)," \
                                                " dynamically linked (uses shared libs)," \
                                                " for GNU/Linux 2.6.32," \
                                                " BuildID[sha1]=ee740c6f97b0910ac912eec89030c56fb28f77aa, not stripped"
    elif operating_system.lower() == 'debian':
        if host.system_info.release == "9.9":
            assert pgbackrest.stdout.strip("\n") == "/usr/bin/pgbackrest: ELF 64-bit LSB shared object," \
                                                    " x86-64, version 1 (SYSV)," \
                                                    " dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2," \
                                                    " for GNU/Linux 2.6.32," \
                                                    " BuildID[sha1]=b2e1c41d6e6b6c26e6f6371348799e39fbd4cae1, stripped"
        else:
            assert pgbackrest.stdout.strip("\n") == "/usr/bin/pgbackrest: ELF 64-bit LSB shared object," \
                                                    " x86-64, version 1 (SYSV)," \
                                                    " dynamically linked," \
                                                    " interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0," \
                                                    " BuildID[sha1]=1d374746b869cd054bd13bc59a3984500bd4018d, stripped"
    elif operating_system.lower == "ubuntu":
        assert pgbackrest.stdout.strip("\n") == "/usr/bin/pgbackrest: ELF 64-bit LSB shared object, x86-64," \
                                                " version 1 (SYSV), dynamically linked, interpreter /lib64/l," \
                                                " for GNU/Linux 3.2.0," \
                                                " BuildID[sha1]=ce50eadfcbe1b0e170df51ec85aebb96db44b420, stripped"


def test_pgbackrest_create_stanza(create_stanza):
    assert "INFO: stanza-create command end: completed successfully" in create_stanza.stdout


def test_pgbackrest_check(pgbackrest_check):
    assert "check command end: completed successfully" in pgbackrest_check[-1]


def test_pgbackrest_full_backup(pgbackrest_full_backup):
    print(pgbackrest_full_backup[-1])
    assert "expire command end: completed successfully" in pgbackrest_full_backup[-1]


def test_pgbackrest_restore(pgbackrest_restore, host):
    print(pgbackrest_restore)
    os = host.system_info.distribution
    if os.lower() in ["redhat", "centos"]:
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
    if os.lower() in ["ubuntu", "redhat", "centos"]:
        pkgn = "percona-patroni"
    elif os == "debian":
        pkgn = "percona-patroni"
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "1.6" in pkg.version


def test_patroni_service(host):
    pass
