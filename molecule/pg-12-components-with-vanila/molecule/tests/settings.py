DEB116_PKG_VERSIONS = ["11+210-1.buster", "204-1.buster", "2:11-6.2.buster", "2:11-6.2.stretch", "204-1.stretch",
                       "11+210-1.stretch", "2:11-6.2.bionic", '11+210-1.bionic', "204-1.bionic", "2:11-6.2.cosmic",
                       "11+210-1.cosmic", "204-1.cosmic", "2:11-6.2.disco", "11+210-1.disco", "204-1.disco",
                       "210-1.stretch", "210-1.cosmic", "210-1.buster", '210-1.disco', "210-1.bionic"]

DEB116_PACKAGES = ["percona-postgresql-12", "percona-postgresql-client", "percona-postgresql",
                   "percona-postgresql-client-12", "percona-postgresql-client-common",
                   "percona-postgresql-contrib", "percona-postgresql-doc", "percona-postgresql-server-dev-all",
                   "percona-postgresql-doc-12", "percona-postgresql-plperl-12", "percona-postgresql-common",
                   "percona-postgresql-plpython3-12", "percona-postgresql-pltcl-12", "percona-postgresql-all",
                   "percona-postgresql-server-dev-12", "percona-postgresql-12-dbgsym",
                   "percona-postgresql-client-12-dbgsym", "percona-postgresql-plperl-12-dbgsym",
                   "percona-postgresql-plpython3-12-dbgsym", "percona-postgresql-pltcl-12-dbgsym"]

RPM_PACKAGES = ["percona-postgresql12", "percona-postgresql12-contrib", "percona-postgresql-common",
                "percona-postgresql12-debuginfo", "percona-postgresql12-devel", "percona-postgresql12-docs",
                "percona-postgresql12-libs", "percona-postgresql12-llvmjit", "percona-postgresql12-plperl",
                "percona-postgresql12-plpython", "percona-postgresql12-pltcl", "percona-postgresql12-server",
                "percona-postgresql12-test", "percona-postgresql-client-common", "percona-postgresql12-debuginfo",
                "percona-postgresql12-debugsource", "percona-postgresql12-devel-debuginfo",
                "percona-postgresql12-libs-debuginfo", "percona-postgresql12-plperl-debuginfo",
                "percona-postgresql12-plpython-debuginfo", "percona-postgresql12-plpython3-debuginfo",
                "percona-postgresql12-pltcl-debuginfo", "percona-postgresql12-server-debuginfo",
                "percona-postgresql12-test-debuginfo"]

RPM7_PACKAGES = ["percona-postgresql12", "percona-postgresql12-contrib", "percona-postgresql-common",
                 "percona-postgresql12-debuginfo", "percona-postgresql12-devel", "percona-postgresql12-docs",
                 "percona-postgresql12-libs", "percona-postgresql12-llvmjit", "percona-postgresql12-plperl",
                 "percona-postgresql12-plpython", "percona-postgresql12-pltcl", "percona-postgresql12-server",
                 "percona-postgresql12-test", "percona-postgresql-client-common"]

DEB_FILES = ["/etc/postgresql/12/main/postgresql.conf", "/etc/postgresql/12/main/pg_hba.conf",
             "/etc/postgresql/12/main/pg_ctl.conf", "/etc/postgresql/12/main/pg_ident.conf"]

RHEL_FILES = ["/var/lib/pgsql/12/data/postgresql.conf", "/var/lib/pgsql/12/data/pg_hba.conf",
              "/var/lib/pgsql/12/data/pg_ident.conf"]

EXTENSIONS = ['xml2', 'tcn', 'plpythonu', 'plpython3u', 'plpython2u', 'pltcl', 'hstore', 'plperlu', 'plperl', 'ltree',
              'hstore_plperlu', 'dict_xsyn', 'autoinc', 'hstore_plpython3u', 'insert_username', 'intagg', 'adminpack',
              'intarray', 'cube', 'lo', 'jsonb_plpython2u', 'jsonb_plperl', 'jsonb_plperlu', 'btree_gin', 'pgrowlocks',
              'bloom', 'seg', 'pageinspect', 'btree_gist', 'sslinfo', 'pg_visibility', 'ltree_plpython2u', 'refint',
              'jsonb_plpython3u', 'jsonb_plpythonu', 'moddatetime', 'ltree_plpythonu', 'dict_int', 'pg_freespacemap',
              'pgstattuple', 'hstore_plpythonu', 'uuid-ossp', 'tsm_system_time', 'tsm_system_rows', 'unaccent',
              'tablefunc', 'pgcrypto', 'pg_buffercache', 'amcheck', 'citext', 'isn',
              'hstore_plpython2u', 'ltree_plpython3u', 'fuzzystrmatch', 'earthdistance', 'hstore_plperl', 'pg_prewarm',
              'dblink', 'pltclu', 'file_fdw', 'pg_stat_statements', 'postgres_fdw']

LANGUAGES = ["pltcl", "pltclu", "plperl", "plperlu", "plpythonu", "plpython2u", "plpython3u"]


pgrepack = {
            "ppg-12.2": {"version": "1.4.5",
                         "binary_version": "pg_repack 1.4.5",
                                    "binary": {"centos": "/usr/pgsql-12/bin/pg_repack: ELF 64-bit LSB executable,"
                                                         " x86-64, version 1 (SYSV),"
                                                         " dynamically linked (uses shared libs),"
                                                         " for GNU/Linux 2.6.32,"
                                                         " BuildID[sha1]=f61d3d7655a56d1aee52824b2a16a1648318b373,"
                                                         " not stripped",
                                               "ubuntu": "/usr/lib/postgresql/11/bin/pg_repack:"
                                                         " ELF 64-bit LSB shared object, x86-64,"
                                                         " version 1 (SYSV), dynamically linked,"
                                                         " interpreter /lib64/l,"
                                                         " for GNU/Linux 3.2.0,"
                                                         " BuildID[sha1]=6354cb6b54e6c7c114eafbb054307cd9880a08e4,"
                                                         " stripped",
                                               "debian": "/usr/lib/postgresql/11/bin/pg_repack:"
                                                         " ELF 64-bit LSB shared object, x86-64,"
                                                         " version 1 (SYSV), dynamically linked,"
                                                         " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                         " for GNU/Linux 3.2.0,"
                                                         " BuildID[sha1]=51ee777d6a32be840cd12e7c826a05f4af6e709a,"
                                                         " stripped",
                                               "debian9.9": "/usr/lib/postgresql/11/bin/pg_repack:"
                                                            " ELF 64-bit LSB shared object, x86-64,"
                                                            " version 1 (SYSV), dynamically linked,"
                                                            " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                            " for GNU/Linux 2.6.32,"
                                                            " BuildID[sha1]=882af5eb384bd255a2258bf842d9ec61c0c247dd,"
                                                            " stripped",
                                               "rhel": "/usr/pgsql-12/bin/pg_repack: ELF 64-bit LSB executable, x86-64,"
                                                       " version 1 (SYSV),"
                                                       " dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,"
                                                       " for GNU/Linux 3.2.0,"
                                                       " BuildID[sha1]=e37e73fdb0d4719e2eea1b784186bce7c26fd5d7,"
                                                       " not stripped"}}}
pgbackrest = {"ppg-12.2": {"version": "2.26",
                           "binary_version": "pgBackRest 2.26",
                           "binary": {"centos": "/usr/bin/pgbackrest: ELF 64-bit LSB executable,"
                                                " x86-64, version 1 (SYSV), dynamically linked (uses shared libs),"
                                                " for GNU/Linux 2.6.32,"
                                                " BuildID[sha1]=8946a6c12c9d6c1f5ee93ff23715b152fc064be1, not stripped",
                                      "ubuntu": "/usr/bin/pgbackrest: ELF 64-bit LSB shared object,"
                                                " x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l,"
                                                " for GNU/Linux 3.2.0,"
                                                " BuildID[sha1]=ce50eadfcbe1b0e170df51ec85aebb96db44b420, stripped",
                                      "debian": "/usr/bin/pgbackrest: ELF 64-bit LSB shared object, x86-64,"
                                                " version 1 (SYSV), dynamically linked,"
                                                " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                " for GNU/Linux 3.2.0,"
                                                " BuildID[sha1]=1d374746b869cd054bd13bc59a3984500bd4018d, stripped",
                                      "debian9.9": "/usr/bin/pgbackrest: ELF 64-bit LSB shared object,"
                                                   " x86-64, version 1 (SYSV), dynamically linked,"
                                                   " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                   " for GNU/Linux 2.6.32,"
                                                   " BuildID[sha1]=b2e1c41d6e6b6c26e6f6371348799e39fbd4cae1, stripped",
                                      "rhel": "/usr/bin/pgbackrest: ELF 64-bit LSB executable, x86-64,"
                                              " version 1 (SYSV), dynamically linked,"
                                              " interpreter /lib64/ld-linux-x86-64.so.2,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=ba1f33e28e40289682814fe2f69498288b872e83, not stripped,"
                                              " too many notes (256)"}}}
patroni = {"ppg-12.2": {'version': "1.6.5",
                        "binary_version": "patroni 1.6.5"}
           }
pgaudit = {"ppg-12.2": {"version": "1.4"}}

DEB_PROVIDES = [("percona-postgresql-12", "postgresql-12"), ("percona-postgresql-client", "postgresql-client"),
                ("percona-postgresql", "postgresql"), ("percona-postgresql-client-12", "postgresql-client-12"),
                ("percona-postgresql-client-common", "postgresql-client-common"),
                ("percona-postgresql-contrib", "postgresql-contrib"), ("percona-postgresql-doc", "postgresql-doc"),
                ("percona-postgresql-server-dev-all", "postgresql-server-dev-all"),
                ('percona-postgresql-plperl-12', 'postgresql-plperl-12'),
                ("percona-postgresql-common", "postgresql-common"),
                ("percona-postgresql-plpython3-12", "postgresql-12-plpython3"),
                ("percona-postgresql-pltcl-12", "postgresql-12-pltcl"), ("percona-postgresql-all", "postgresql-all"),
                ("percona-postgresql-server-dev-12", 'postgresql-server-dev-all-12')]

RPM7_PROVIDES = [("percona-postgresql12", 'postgresql12'),
                 ("percona-postgresql12-contrib", 'postgresql12-contrib'),
                 ("percona-postgresql-common", 'postgresql-common'),
                 ("percona-postgresql12-devel", 'postgresql12-devel'),
                 ("percona-postgresql12-docs", "postgresql-docs"),
                 ("percona-postgresql12-libs", 'postgresql12-libs'),
                 ("percona-postgresql12-llvmjit", 'postgresql12-llvmjit'),
                 ('percona-postgresql12-plperl', 'postgresql12-plperl'),
                 ("percona-postgresql12-pltcl", 'postgresql12-pltcl'),
                 ('percona-postgresql12-server', 'postgresql12-server'),
                 ("percona-postgresql12-test", 'postgresql12-test'),
                 ("percona-postgresql-client-common", 'postgresql-client-common')]

RPM_PROVIDES = [("percona-postgresql12", "postgresql12"),
                ("percona-postgresql12-contrib", "postgresql12-contrib"),
                ("percona-postgresql-common", "postgresql-common"),
                ("percona-postgresql12-devel", "postgresql-devel"),
                ("percona-postgresql12-docs", "postgresql-docs"),
                ("percona-postgresql12-libs", "postgresql12-libs"),
                ("percona-postgresql12-llvmjit", "postgresql12-llvmjit"),
                ("percona-postgresql12-plperl", 'postgresql12-plperl'),
                ("percona-postgresql12-plpython", 'postgresql-plpython'),
                ("percona-postgresql12-pltcl", 'postgresql12-pltcl'),
                ("percona-postgresql12-server", 'postgresql12-server'),
                ("percona-postgresql12-test", "postgresql12-test"),
                ("percona-postgresql-client-common", 'postgresql-client-common')
                ]


versions = {"ppg-12.2": {"version": "12.2", "deb_pkg_ver": DEB116_PKG_VERSIONS,
                         "deb_packages": DEB116_PACKAGES,
                         "percona-postgresql-common": '214',
                         "percona-postgresql-client-common": "214",
                         "libpq_version": "120002",
                         "pgaudit": pgaudit['ppg-12.2'],
                         "pgbackrest": pgbackrest['ppg-12.2'],
                         "patroni": patroni['ppg-12.2'],
                         "pgrepack": pgrepack['ppg-12.2'], "libpq": "Version of libpq: 120002",
                         "deb_provides": DEB_PROVIDES,
                         "rpm7_provides": RPM7_PROVIDES,
                         'rpm_provides': RPM_PROVIDES}
            }
