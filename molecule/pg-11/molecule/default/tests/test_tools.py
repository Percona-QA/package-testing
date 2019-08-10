import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture(scope="module")
def operating_system(host):
    return host.system_info.distribution


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
        result = host.check_output(pgbench)
        print("Pgbench out {}".format(result))
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        print(host.check_output(select))
        if os.lower() in ["redhat", "centos"]:
            cmd = "/usr/pgsql-11/bin/pg_repack -t pgbench_accounts -j 4"
        else:
            # TODO need to be in PATH?
            cmd = "/usr/lib/postgresql/11/bin/pg_repack -t pgbench_accounts -j 4"
        pg_repack_result = host.run(cmd)
        print(pg_repack_result.stdout)
        print(pg_repack_result.rc)
    yield pg_repack_result


@pytest.fixture()
def pg_repack_dry_run(host, operating_system):
    with host.sudo("postgres"):
        pgbench = "pgbench -i -s 1"
        result = host.check_output(pgbench)
        print("Pgbench out {}".format(result))
        select = "psql -c 'SELECT COUNT(*) FROM pgbench_accounts;' | awk 'NR==3{print $1}'"
        print(host.check_output(select))
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


def test_pgrepack_binary(pgrepack):
    print(pgrepack)


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
    print(pg_repack_functional.stdout)


def test_pg_repack_dry_run(pg_repack_dry_run):
    assert pg_repack_dry_run.rc == 0
    print(pg_repack_dry_run.stdout)


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
        assert "2.15" in docs_pkg.version
        dbg_pkg = "percona-pgbackrest-dbgsym"
        dbg = host.package(dbg_pkg)
        assert dbg.is_installed
        assert "2.15" in dbg.version
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "2.15" in pkg.version


def test_pgbackrest(pgbackrest, operating_system):
    assert pgbackrest.rc == 0
    if operating_system.lower() in ["redhat", "centos"]:
        assert pgbackrest.stdout.strip("\n") == "/usr/bin/pgbackrest: ELF 64-bit LSB executable," \
                                         " x86-64, version 1 (SYSV), dynamically linked (uses shared libs)," \
                                         " for GNU/Linux 2.6.32," \
                                         " BuildID[sha1]=524db768c09d913aec12cf909d0c431c7e2f3f53, not stripped"
    elif operating_system.lower() in ['debian', 'ubuntu']:
        assert pgbackrest.stdout.strip("\n") == "/usr/bin/pgbackrest: ELF 64-bit LSB shared object," \
                                                " x86-64, version 1 (SYSV), dynamically linked," \
                                                " interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32," \
                                                " BuildID[sha1]=837c86bf3cc34677b67acc6e8ca9635b49ba44b5, stripped"


def test_patroni_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os.lower() in ["ubuntu", "redhat", "centos"]:
        pkgn = "percona-patroni"
    elif os == "debian":
        pkgn = "percona-patroni"
        dbgsym_pkgn = "percona-patroni-dbgsym"
        dbgsym_pkg = host.package(dbgsym_pkgn)
        assert dbgsym_pkg.is_installed
        assert "1.5" in dbgsym_pkg.version
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "1.5" in pkg.version
