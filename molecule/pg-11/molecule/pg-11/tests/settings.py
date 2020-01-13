DEB_PKG_VERSIONS = ["11+204-1.buster", "204-1.buster", "1:11-5.buster", "1:11-5.stretch", "204-1.stretch",
                    "11+204-1.stretch", "1:11-5.bionic", '11+204-1.bionic', "204-1.bionic", "1:11-5.cosmic",
                    "11+204-1.cosmic", "204-1.cosmic", "1:11-5.disco", "11+204-1.disco", "204-1.disco"]

DEB116_PKG_VERSIONS = ["11+210-1.buster", "204-1.buster", "2:11-6.2.buster", "2:11-6.2.stretch", "204-1.stretch",
                       "11+210-1.stretch", "2:11-6.2.bionic", '11+210-1.bionic', "204-1.bionic", "2:11-6.2.cosmic",
                       "11+210-1.cosmic", "204-1.cosmic", "2:11-6.2.disco", "11+210-1.disco", "204-1.disco",
                       "210-1.stretch", "210-1.cosmic", "210-1.buster", '210-1.disco', "210-1.bionic"]

DEB116_PACKAGES = ["percona-postgresql-11", "percona-postgresql-client", "percona-postgresql",
                   "percona-postgresql-client-11", "percona-postgresql-client-common",
                   "percona-postgresql-contrib", "percona-postgresql-doc", "percona-postgresql-server-dev-all",
                   "percona-postgresql-doc-11", "percona-postgresql-plperl-11", "percona-postgresql-common",
                   "percona-postgresql-plpython3-11", "percona-postgresql-pltcl-11", "percona-postgresql-all",
                   "percona-postgresql-server-dev-11", "percona-postgresql-11-dbgsym",
                   "percona-postgresql-client-11-dbgsym", "percona-postgresql-plperl-11-dbgsym",
                   "percona-postgresql-plpython3-11-dbgsym", "percona-postgresql-pltcl-11-dbgsym"]

DEB_PACKAGES = ["percona-postgresql-11", "percona-postgresql-client", "percona-postgresql",
                "percona-postgresql-client-11", "percona-postgresql-client-common",
                "percona-postgresql-contrib", "percona-postgresql-doc", "percona-postgresql-server-dev-all",
                "percona-postgresql-doc-11", "percona-postgresql-plperl-11", "percona-postgresql-common",
                "percona-postgresql-plpython-11", "percona-postgresql-plpython3-11",
                "percona-postgresql-pltcl-11", "percona-postgresql-all", "percona-postgresql-server-dev-11",
                "percona-postgresql-11-dbgsym", "percona-postgresql-client-11-dbgsym",
                "percona-postgresql-plperl-11-dbgsym", "percona-postgresql-plpython-11-dbgsym",
                "percona-postgresql-plpython3-11-dbgsym", "percona-postgresql-pltcl-11-dbgsym",
                "percona-postgresql-server-dev-11-dbgsym"]

RPM_PACKAGES = ["percona-postgresql11", "percona-postgresql11-contrib", "percona-postgresql-common",
                "percona-postgresql11-debuginfo", "percona-postgresql11-devel", "percona-postgresql11-docs",
                "percona-postgresql11-libs", "percona-postgresql11-llvmjit", "percona-postgresql11-plperl",
                "percona-postgresql11-plpython", "percona-postgresql11-pltcl", "percona-postgresql11-server",
                "percona-postgresql11-test", "percona-postgresql-client-common", "percona-postgresql11-debuginfo",
                "percona-postgresql11-debugsource", "percona-postgresql11-devel-debuginfo",
                "percona-postgresql11-libs-debuginfo", "percona-postgresql11-plperl-debuginfo",
                "percona-postgresql11-plpython-debuginfo", "percona-postgresql11-plpython3-debuginfo",
                "percona-postgresql11-pltcl-debuginfo", "percona-postgresql11-server-debuginfo",
                "percona-postgresql11-test-debuginfo"]

RPM7_PACKAGES = ["percona-postgresql11", "percona-postgresql11-contrib", "percona-postgresql-common",
                 "percona-postgresql11-debuginfo", "percona-postgresql11-devel", "percona-postgresql11-docs",
                 "percona-postgresql11-libs", "percona-postgresql11-llvmjit", "percona-postgresql11-plperl",
                 "percona-postgresql11-plpython", "percona-postgresql11-pltcl", "percona-postgresql11-server",
                 "percona-postgresql11-test", "percona-postgresql-client-common"]

DEB_FILES = ["/etc/postgresql/11/main/postgresql.conf", "/etc/postgresql/11/main/pg_hba.conf",
             "/etc/postgresql/11/main/pg_ctl.conf", "/etc/postgresql/11/main/pg_ident.conf"]

RHEL_FILES = ["/var/lib/pgsql/11/data/postgresql.conf", "/var/lib/pgsql/11/data/pg_hba.conf",
              "/var/lib/pgsql/11/data/pg_ident.conf"]

EXTENSIONS = ['xml2', 'tcn', 'plpythonu', 'plpython3u', 'plpython2u', 'pltcl', 'hstore', 'plperlu', 'plperl', 'ltree',
              'hstore_plperlu', 'dict_xsyn', 'autoinc', 'hstore_plpython3u','insert_username', 'intagg', 'adminpack',
              'intarray', 'cube', 'lo', 'jsonb_plpython2u', 'jsonb_plperl', 'jsonb_plperlu', 'btree_gin', 'pgrowlocks',
              'bloom', 'seg', 'pageinspect', 'btree_gist', 'sslinfo', 'pg_visibility', 'ltree_plpython2u', 'refint',
              'jsonb_plpython3u', 'jsonb_plpythonu', 'moddatetime', 'ltree_plpythonu', 'dict_int', 'pg_freespacemap',
              'pgstattuple', 'hstore_plpythonu', 'uuid-ossp', 'tsm_system_time', 'tsm_system_rows', 'unaccent',
              'tablefunc', 'pgcrypto', 'pg_buffercache', 'amcheck', 'citext',  'timetravel',  'isn',
              'hstore_plpython2u', 'ltree_plpython3u', 'fuzzystrmatch', 'earthdistance', 'hstore_plperl', 'pg_prewarm',
              'dblink', 'pltclu', 'file_fdw', 'pg_stat_statements', 'postgres_fdw']

LANGUAGES = ["pltcl", "pltclu", "plperl", "plperlu", "plpythonu", "plpython2u", "plpython3u"]


pgrepack = {"ppg-11.5": {"version": "1.4.4",
                         "binary_version": "pg_repack 1.4.4",
                         "binary": {"centos": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable, x86-64,"
                                              " version 1 (SYSV), dynamically linked (uses shared libs),"
                                              " for GNU/Linux 2.6.32,"
                                              " BuildID[sha1]=b76f53a7d4ffe7dfab0d9bd5868e99bdfcfe48e9, not stripped",
                                    "ubuntu": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=79aca6e4d94f971b1adc16c4d523ce69a85ad1d4, stripped",
                                    "debian": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV),"
                                              " dynamically linked,interpreter"
                                              " /lib64/ld-linux-x86-64.so.2,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=9aef45d1e9a16645857aba84473dd8f150998d90, stripped",
                                    "debian9.9": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV),"
                                              " dynamically linked,"
                                              " interpreter /lib64/ld-linux-x86-64.so.2,for GNU/Linux 2.6.32,"
                                              " BuildID[sha1]=0f89ea7cb7dcbe4435aefd2c74be0505a818614b, stripped",
                                    "rhel": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable, x86-64,"
                                            " version 1 (SYSV), dynamically linked,"
                                            " interpreter /lib64/ld-linux-x86-64.so.2,"
                                            " for GNU/Linux 3.2.0,"
                                            " BuildID[sha1]=a43932c618eeeca37607301c219935b23e13f498, not stripped"}},
            "ppg-11.6": {"version": "1.4.5",
                         "binary_version": "pg_repack 1.4.5",
                                    "binary": {"centos": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable,"
                                                         " x86-64, version 1 (SYSV),"
                                                         " dynamically linked (uses shared libs), for GNU/Linux 2.6.32,"
                                                         " BuildID[sha1]=bd2f6cc2747db832da8302ce8ceaddd6cf56dad0,"
                                                         " not stripped",
                                               "ubuntu": "",
                                               "debian": "",
                                               "debian9.9": "/usr/lib/postgresql/11/bin/pg_repack:"
                                                            " ELF 64-bit LSB shared object, x86-64,"
                                                            " version 1 (SYSV), dynamically linked,"
                                                            " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                            " for GNU/Linux 2.6.32,"
                                                            " BuildID[sha1]=882af5eb384bd255a2258bf842d9ec61c0c247dd,"
                                                            " stripped",
                                               "rhel": ""}}}
pgbackrest = {"ppg-11.5": {"version": "2.16",
                           "binary_version": "pgBackRest 2.16",
                           "binary": {"centos": "/usr/bin/pgbackrest: ELF 64-bit LSB executable,x86-64,"
                                                " version 1 (SYSV),dynamically linked (uses shared libs),"
                                                " for GNU/Linux 2.6.32,"
                                                " BuildID[sha1]=ee740c6f97b0910ac912eec89030c56fb28f77aa, not stripped",
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
                                      "rhel": "/usr/bin/pgbackrest: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV),"
                                              " dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=7b29febffa6997744eb3be2e5bc1bc97647722e5,"
                                              " with debug_info, not stripped, too many notes (256)"}},
              "ppg-11.6": {"version": "2.20",
                           "binary_version": "pgBackRest 2.20",
                           "binary": {"centos": "/usr/bin/pgbackrest: ELF 64-bit LSB executable,"
                                                " x86-64, version 1 (SYSV), dynamically linked (uses shared libs),"
                                                " for GNU/Linux 2.6.32,"
                                                " BuildID[sha1]=4189028da7f21d6a0b4fa300cfe3605a1e3523ad, not stripped",
                                      "ubuntu": "",
                                      "debian": "",
                                      "debian9.9": "/usr/bin/pgbackrest: ELF 64-bit LSB shared object,"
                                                   " x86-64, version 1 (SYSV), dynamically linked,"
                                                   " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                   " for GNU/Linux 2.6.32,"
                                                   " BuildID[sha1]=b28fdcb98063422df7c1eac6623054016f1f2781, stripped",
                                      "rhel": ""}}}
patroni = {"ppg-11.5": {'version': "",
                        "binary_version": ""},
           "ppg-11.6": {'version': "1.6.3",
                        "binary_version": "patroni 1.6.3"}
           }
pgaudit = {"ppg-11.5": {"version": "1.3"},
           "ppg-11.6": {"version": "1.4.0"}}


versions = {"ppg-11.6": {"version": "11.6", "deb_pkg_ver": DEB116_PKG_VERSIONS,
                         "deb_packages": DEB116_PACKAGES,
                         "percona-postgresql-common": '210',
                         "percona-postgresql-client-common": "210",
                         "libpq_version": "110006",
                         "pgaudit": pgaudit['ppg-11.6'],
                         "pgbackrest": pgbackrest['ppg-11.6'],
                         "patroni": patroni['ppg-11.6'],
                         "pgrepack": pgrepack['ppg-11.6'], "libpq": "Version of libpq: 110006"},
            "ppg-11.5": {"version": "11.5", "deb_pkg_ver": DEB_PKG_VERSIONS,
                         "deb_packages": DEB_PACKAGES,
                         "percona-postgresql-common": '204',
                         "percona-postgresql-client-common": "204",
                         "libpq_version": "110005",
                         "pgaudit": pgaudit['ppg-11.5'],
                         "pgbackrest": pgbackrest['ppg-11.5'],
                         "patroni": patroni['ppg-11.5'],
                         "pgrepack": pgrepack['ppg-11.5'], "libpq": "Version of libpq: 110005"
                         }
            }
