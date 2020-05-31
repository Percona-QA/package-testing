DEB116_PKG_VERSIONS = ["12+214-1.buster", "204-1.buster", "2:12-2.4.buster", "2:12-2.4.stretch", "204-1.stretch",
                       "12+214-1.stretch", "2:12-2.4.bionic", '12+214-1.bionic', "204-1.bionic", "2:12-2.4.focal",
                       "12+214-1.focal", "204-1.focal", "2:12-2.4.disco", "12+214-1.disco", "204-1.disco",
                       "214-1.stretch", "214-1.focal", "214-1.buster", '214-1.disco', "214-1.bionic"]

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



DEB_PROVIDES = [("percona-postgresql-12", "postgresql-12"), ("percona-postgresql-client", "postgresql-client"),
                ("percona-postgresql", "postgresql"), ("percona-postgresql-client-12", "postgresql-client-12"),
                ("percona-postgresql-client-common", "postgresql-client-common"),
                ("percona-postgresql-contrib", "postgresql-contrib"), ("percona-postgresql-doc", "postgresql-doc"),
                ("percona-postgresql-server-dev-all", "postgresql-server-dev-all"),
                ('percona-postgresql-plperl-12', 'postgresql-plperl-12'),
                ("percona-postgresql-common", "postgresql-common"),
                ("percona-postgresql-plpython3-12", "postgresql-plpython3-12"),
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
