DEB_PKG_VERSIONS = ["11+204-1.buster", "204-1.buster", "1:11-5.buster", "1:11-5.stretch", "204-1.stretch",
                    "11+204-1.stretch", "1:11-5.bionic", '11+204-1.bionic', "204-1.bionic", "1:11-5.cosmic",
                    "11+204-1.cosmic", "204-1.cosmic", "1:11-5.disco", "11+204-1.disco", "204-1.disco"]

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
                         "binary": {"centos": "",
                                    "ubuntu": "",
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
                                    "binary": {"centos": "",
                                               "ubuntu": "",
                                               "debian": "",
                                               "debian9.9": "",
                                               "rhel": ""}}}
pgbackrest = {"ppg-11.5": {"version": "2.16",
                           "binary_version": "pgBackRest 2.16",
                           "binary": {"centos": "",
                                      "ubuntu": "",
                                      "debian": "",
                                      "rhel": ""}},
              "ppg-11.6": {"version": "2.20",
                           "binary_version": "pgBackRest 2.20",
                           "binary": {"centos": "",
                                      "ubuntu": "",
                                      "debian": "",
                                      "rhel": ""}}}
patroni = {"ppg-11.5": {'version': "",
                        "binary": {"centos": "",
                                   "ubuntu": "",
                                   "debian": "",
                                   "rhel": ""}},
           "ppg-11.6": {'version': "",
                        "binary": {"centos": "",
                                   "ubuntu": "",
                                   "debian": "",
                                   "rhel": ""}}
           }
pgaudit = {"ppg-11.5": {"version": "1.3",
                        "binary": {"centos": "",
                                   "ubuntu": "",
                                   "debian": "",
                                   "rhel": ""}},
           "ppg-11.6": {"version": "1.4.0",
                        "binary": {"centos": "",
                                   "ubuntu": "",
                                   "debian": "",
                                   "rhel": ""}}}


versions = {"ppg-11.6": {"version": "11.6", "deb_pkg_ver": DEB_PKG_VERSIONS,
                         "percona-postgresql-common": '210',
                         "percona-postgresql-client-common": "210",
                         "libpq_version": "110006",
                         "pgaudit": pgaudit['ppg-11.6'],
                         "pgbackrest": pgbackrest['ppg-11.6'],
                         "patroni": patroni['ppg-11.6'],
                         "pgrepack": pgrepack['ppg-11.6'], "libpq": "Version of libpq: 110006"},
            "ppg-11.5": {"version": "11.5", "deb_pkg_ver": DEB_PKG_VERSIONS,
                         "percona-postgresql-common": '204',
                         "percona-postgresql-client-common": "204",
                         "libpq_version": "110005",
                         "pgaudit": pgaudit['ppg-11.5'],
                         "pgbackrest": pgbackrest['ppg-11.5'],
                         "patroni": patroni['ppg-11.5'],
                         "pgrepack": pgrepack['ppg-11.5'], "libpq": "Version of libpq: 110005"
                         }
            }
