#!/usr/bin/env python3
import os

ps_version = os.getenv('PS_VERSION')
ps_revision = os.getenv('PS_REVISION')

ps_version_upstream, ps_version_percona = ps_version.split("-")
ps_version_major = ps_version_upstream.split(".")[0] + '.' + ps_version_upstream.split(".")[1]

docker_acc = "percona"
docker_product = "percona-server"
docker_tag = ps_version_upstream
docker_image = docker_acc + "/" + docker_product + ":" + docker_tag

ps80_packages = ['percona-server-client', 'percona-server-rocksdb', 'percona-server-server', 'percona-server-shared', 'percona-server-shared-compat', 'percona-server-tokudb']
ps80_binaries = ['/usr/bin/mysql', '/usr/sbin/mysqld', '/usr/bin/ps-admin', '/usr/bin/mysqladmin', '/usr/bin/mysqlbinlog', '/usr/sbin/mysqld-debug', '/usr/bin/mysqldump', '/usr/bin/mysqldumpslow', '/usr/bin/mysqlimport', '/usr/bin/mysqlpump', '/usr/bin/mysqlshow', '/usr/bin/mysqlslap', '/usr/bin/mysqlcheck', '/usr/bin/mysql_config_editor', '/usr/bin/mysql_config', '/usr/bin/mysql_config-64', '/usr/bin/mysql_ldb', '/usr/bin/mysql_secure_installation', '/usr/bin/mysql_ssl_rsa_setup', '/usr/bin/mysql_upgrade', '/usr/bin/mysql_tzinfo_to_sql']

if ps_version_major == "8.0":
    ps_packages = ps80_packages
if ps_version_major == "8.0":
    ps_binaries = ps80_binaries

ps_pwd = "pwd1234#"
