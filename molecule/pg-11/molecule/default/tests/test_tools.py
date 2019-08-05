import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture()
def pgaudit(host):
    cmd = "sudo systemctl restart postgresql"
    result = host.run(cmd)
    assert result.rc == 0
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
        print(result)
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
        os = host.system_info.distribution
        log_file = "/var/log/postgresql/postgresql-11-main.log"
        if os.lower() == "debian":
            log_file = "/var/log/postgresql/postgresql-11-main.log"
        elif os.lower() == "redhat":
            log_file = "/var/log/postgresql/postgresql-11-main.log"
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

    # TODO add drop extension and restart nginx


@pytest.fixture()
def pgbackrest(host):
    """
    $ file /usr/bin/pgbackrest
/usr/bin/pgbackrest: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.32, BuildID[sha1]=5e3f6123d02e0013b53f6568f99409378d43ad89, not stripped
    :param host:
    :return:
    """


@pytest.fixture()
def ptrack(host):
    pass


@pytest.fixture()
def patroni(host):
    pass


def test_pgaudit_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os == "RedHat":
        pkgn = "percona-pgaudit"
    elif os == "debian":
        pkgn = "percona-postgresql-11-pgaudit"
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
    if os == "RedHat":
        pkgn = "percona-pg_repack11"
    elif os == "debian":
        pkgn = "percona-postgresql-11-repack"
        pkg_dbgsym = host.package("percona-postgresql-11-repack-dbgsym")
        assert pkg_dbgsym.is_installed
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "1.4" in pkg.version


def test_pgrepack(host):
    pass


def test_pgbackrest_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os == "RedHat":
        pkgn = "percona-pgbackrest"
    elif os == "debian":
        pkgn = "percona-pgbackrest"
        doc_pkgn = "percona-pgbackrest-doc"
        docs_pkg = host.package(doc_pkgn)
        assert docs_pkg.is_installed
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "2.15" in pkg.version


def test_pgbackrest(host):
    pass


def test_patroni_package(host):
    os = host.system_info.distribution
    pkgn = ""
    if os == "RedHat":
        pkgn = "percona-patroni"
    elif os == "debian":
        pkgn = "percona-patroni"
        dbgsym_pkgn = "percona-patroni-dbgsym"
        dbgsym_pkg = host.package(dbgsym_pkgn)
        assert dbgsym_pkg.is_installed
    if pkgn == "":
        pytest.fail("Unsupported operating system")
    pkg = host.package(pkgn)
    assert pkg.is_installed
    assert "2.15" in pkg.version
