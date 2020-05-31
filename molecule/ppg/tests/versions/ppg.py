DEB_PKG_VERSIONS = ["11+204-1.buster", "204-1.buster", "1:11-5.buster", "1:11-5.stretch", "204-1.stretch",
                    "11+204-1.stretch", "1:11-5.bionic", '11+204-1.bionic', "204-1.bionic", "1:11-5.cosmic",
                    "11+204-1.cosmic", "204-1.cosmic", "1:11-5.disco", "11+204-1.disco", "204-1.disco"]

DEB116_PKG_VERSIONS = ["11+210-1.buster", "204-1.buster", "2:11-6.2.buster", "2:11-6.2.stretch", "204-1.stretch",
                       "11+210-1.stretch", "2:11-6.2.bionic", '11+210-1.bionic', "204-1.bionic", "2:11-6.2.cosmic",
                       "11+210-1.cosmic", "204-1.cosmic", "2:11-6.2.disco", "11+210-1.disco", "204-1.disco",
                       "210-1.stretch", "210-1.cosmic", "210-1.buster", '210-1.disco', "210-1.bionic"]

DEB117_PKG_VERSIONS = ["11+214-1.buster", "204-1.buster", "2:11-7.2.buster", "2:11-7.2.stretch", "204-1.stretch",
                       "11+214-1.stretch", "2:11-7.2.bionic", '11+214-1.bionic', "204-1.bionic", "2:11-7.2.cosmic",
                       "11+214-1.cosmic", "204-1.cosmic", "2:11-7.2.disco", "11+214-1.disco", "204-1.disco",
                       "214-1.stretch", "214-1.cosmic", "214-1.buster", '214-1.disco', "214-1.bionic"]

DEB116_PACKAGES_TEMPLATE = ["percona-postgresql-{}",
                            "percona-postgresql-client",
                            "percona-postgresql",
                            "percona-postgresql-client-{}",
                            "percona-postgresql-client-common",
                            "percona-postgresql-contrib",
                            "percona-postgresql-doc",
                            "percona-postgresql-server-dev-all",
                            "percona-postgresql-doc-{}",
                            "percona-postgresql-plperl-{}",
                            "percona-postgresql-common",
                            "percona-postgresql-plpython3-{}",
                            "percona-postgresql-pltcl-{}",
                            "percona-postgresql-all",
                            "percona-postgresql-server-dev-{}",
                            "percona-postgresql-{}-dbgsym",
                            "percona-postgresql-client-{}-dbgsym",
                            "percona-postgresql-plperl-{}-dbgsym",
                            "percona-postgresql-plpython3-{}-dbgsym",
                            "percona-postgresql-pltcl-{}-dbgsym"
                            ]

DEB_PACKAGES_TEMPLATE = ["percona-postgresql-{}",
                         "percona-postgresql-client",
                         "percona-postgresql",
                         "percona-postgresql-client-{}",
                         "percona-postgresql-client-common",
                         "percona-postgresql-contrib",
                         "percona-postgresql-doc",
                         "percona-postgresql-server-dev-all",
                         "percona-postgresql-doc-{}",
                         "percona-postgresql-plperl-{}",
                         "percona-postgresql-common",
                         "percona-postgresql-plpython-{}",
                         "percona-postgresql-plpython3-{}",
                         "percona-postgresql-pltcl-{}",
                         "percona-postgresql-all",
                         "percona-postgresql-server-dev-{}",
                         "percona-postgresql-{}-dbgsym",
                         "percona-postgresql-client-{}-dbgsym",
                         "percona-postgresql-plperl-{}-dbgsym",
                         "percona-postgresql-plpython-{}-dbgsym",
                         "percona-postgresql-plpython3-{}-dbgsym",
                         "percona-postgresql-pltcl-{}-dbgsym",
                         "percona-postgresql-server-dev-{}-dbgsym"]

RPM_PACKAGES_TEMPLATE = ["percona-postgresql{}",
                         "percona-postgresql{}-contrib",
                         "percona-postgresql-common",
                         "percona-postgresql{}-debuginfo",
                         "percona-postgresql{}-devel",
                         "percona-postgresql{}-docs",
                         "percona-postgresql{}-libs",
                         "percona-postgresql{}-llvmjit",
                         "percona-postgresql{}-plperl",
                         "percona-postgresql{}-plpython",
                         "percona-postgresql{}-pltcl",
                         "percona-postgresql{}-server",
                         "percona-postgresql{}-test",
                         "percona-postgresql-client-common",
                         "percona-postgresql{}-debuginfo",
                         "percona-postgresql{}-debugsource",
                         "percona-postgresql{}-devel-debuginfo",
                         "percona-postgresql{}-libs-debuginfo",
                         "percona-postgresql{}-plperl-debuginfo",
                         "percona-postgresql{}-plpython-debuginfo",
                         "percona-postgresql{}-plpython3-debuginfo",
                         "percona-postgresql{}-pltcl-debuginfo",
                         "percona-postgresql{}-server-debuginfo",
                         "percona-postgresql{}-test-debuginfo"]

RPM7_PACKAGES_TEMPLATE = ["percona-postgresql{}",
                          "percona-postgresql{}-contrib",
                          "percona-postgresql-common",
                          "percona-postgresql{}-debuginfo",
                          "percona-postgresql{}-devel",
                          "percona-postgresql{}-docs",
                          "percona-postgresql{}-libs",
                          "percona-postgresql{}-llvmjit",
                          "percona-postgresql{}-plperl",
                          "percona-postgresql{}-plpython",
                          "percona-postgresql{}-pltcl",
                          "percona-postgresql{}-server",
                          "percona-postgresql{}-test",
                          "percona-postgresql-client-common"]

DEB_FILES_TEMPLATE = ["/etc/postgresql/{}/main/postgresql.conf",
                      "/etc/postgresql/{}/main/pg_hba.conf",
                      "/etc/postgresql/{}/main/pg_ctl.conf",
                      "/etc/postgresql/{}/main/pg_ident.conf"]

RHEL_FILES_TEMPLATE = ["/var/lib/pgsql/{}/data/postgresql.conf",
                       "/var/lib/pgsql/{}/data/pg_hba.conf",
                       "/var/lib/pgsql/{}/data/pg_ident.conf"]

PG11_EXTENSIONS = [
    'xml2', 'tcn', 'plpythonu', 'plpython3u', 'plpython2u', 'pltcl', 'hstore', 'plperlu', 'plperl', 'ltree',
    'hstore_plperlu', 'dict_xsyn', 'autoinc', 'hstore_plpython3u', 'insert_username', 'intagg', 'adminpack',
    'intarray', 'cube', 'lo', 'jsonb_plpython2u', 'jsonb_plperl', 'jsonb_plperlu', 'btree_gin', 'pgrowlocks',
    'bloom', 'seg', 'pageinspect', 'btree_gist', 'sslinfo', 'pg_visibility', 'ltree_plpython2u', 'refint',
    'jsonb_plpython3u', 'jsonb_plpythonu', 'moddatetime', 'ltree_plpythonu', 'dict_int', 'pg_freespacemap',
    'pgstattuple', 'hstore_plpythonu', 'uuid-ossp', 'tsm_system_time', 'tsm_system_rows', 'unaccent',
    'tablefunc', 'pgcrypto', 'pg_buffercache', 'amcheck', 'citext',  'timetravel',  'isn',
    'hstore_plpython2u', 'ltree_plpython3u', 'fuzzystrmatch', 'earthdistance', 'hstore_plperl', 'pg_prewarm',
    'dblink', 'pltclu', 'file_fdw', 'pg_stat_statements', 'postgres_fdw'
]

PG12_EXTENSIONS = [
    'xml2', 'tcn', 'plpythonu', 'plpython3u', 'plpython2u', 'pltcl', 'hstore', 'plperlu', 'plperl', 'ltree',
    'hstore_plperlu', 'dict_xsyn', 'autoinc', 'hstore_plpython3u', 'insert_username', 'intagg', 'adminpack',
    'intarray', 'cube', 'lo', 'jsonb_plpython2u', 'jsonb_plperl', 'jsonb_plperlu', 'btree_gin', 'pgrowlocks',
    'bloom', 'seg', 'pageinspect', 'btree_gist', 'sslinfo', 'pg_visibility', 'ltree_plpython2u', 'refint',
    'jsonb_plpython3u', 'jsonb_plpythonu', 'moddatetime', 'ltree_plpythonu', 'dict_int', 'pg_freespacemap',
    'pgstattuple', 'hstore_plpythonu', 'uuid-ossp', 'tsm_system_time', 'tsm_system_rows', 'unaccent',
    'tablefunc', 'pgcrypto', 'pg_buffercache', 'amcheck', 'citext', 'isn',
    'hstore_plpython2u', 'ltree_plpython3u', 'fuzzystrmatch', 'earthdistance', 'hstore_plperl', 'pg_prewarm',
    'dblink', 'pltclu', 'file_fdw', 'pg_stat_statements', 'postgres_fdw'
]

LANGUAGES = ["pltcl", "pltclu", "plperl", "plperlu", "plpythonu", "plpython2u", "plpython3u"]

DEB_PROVIDES_TEMPLATE = [("percona-postgresql-{}", "postgresql-{}"),
                         ("percona-postgresql-client", "postgresql-client"),
                         ("percona-postgresql", "postgresql"),
                         ("percona-postgresql-client-{}", "postgresql-client-{}"),
                         ("percona-postgresql-client-common", "postgresql-client-common"),
                         ("percona-postgresql-contrib", "postgresql-contrib"),
                         ("percona-postgresql-doc", "postgresql-doc"),
                         ("percona-postgresql-server-dev-all", "postgresql-server-dev-all"),
                         ('percona-postgresql-plperl-{}', 'postgresql-plperl-{}'),
                         ("percona-postgresql-common", "postgresql-common"),
                         ("percona-postgresql-plpython3-{}", "postgresql-{}-plpython3"),
                         ("percona-postgresql-pltcl-{}", "postgresql-{}-pltcl"),
                         ("percona-postgresql-all", "postgresql-all"),
                         ("percona-postgresql-server-dev-{}", 'postgresql-server-dev-all-{}')]

RPM7_PROVIDES_TEMPLATE = [("percona-postgresql{}", 'postgresql{}'),
                          ("percona-postgresql{}-contrib", 'postgresql{}-contrib'),
                          ("percona-postgresql-common", 'postgresql-common'),
                          ("percona-postgresql{}-devel", 'postgresql{}-devel'),
                          ("percona-postgresql{}-docs", "postgresql-docs"),
                          ("percona-postgresql{}-libs", 'postgresql{}-libs'),
                          ("percona-postgresql{}-llvmjit", 'postgresql{}-llvmjit'),
                          ('percona-postgresql{}-plperl', 'postgresql{}-plperl'),
                          ("percona-postgresql{}-pltcl", 'postgresql{}-pltcl'),
                          ('percona-postgresql{}-server', 'postgresql{}-server'),
                          ("percona-postgresql{}-test", 'postgresql{}-test'),
                          ("percona-postgresql-client-common", 'postgresql-client-common')]

RPM_PROVIDES_TEMPLATE = [("percona-postgresql{}", "postgresql{}"),
                         ("percona-postgresql{}-contrib", "postgresql{}-contrib"),
                         ("percona-postgresql-common", "postgresql-common"),
                         ("percona-postgresql{}-devel", "postgresql-devel"),
                         ("percona-postgresql{}-docs", "postgresql-docs"),
                         ("percona-postgresql{}-libs", "postgresql{}-libs"),
                         ("percona-postgresql{}-llvmjit", "postgresql{}-llvmjit"),
                         ("percona-postgresql{}-plperl", 'postgresql{}-plperl'),
                         ("percona-postgresql{}-plpython", 'postgresql-plpython'),
                         ("percona-postgresql{}-pltcl", 'postgresql{}-pltcl'),
                         ("percona-postgresql{}-server", 'postgresql{}-server'),
                         ("percona-postgresql{}-test", "postgresql{}-test"),
                         ("percona-postgresql-client-common", 'postgresql-client-common')
                ]


def fill_template_form(template, pg_version):
    """

    :param template:
    :param pg_version:
    :return:
    """
    return [t.format(pg_version) for t in template]


def fill_provides_template_form(provides_template, pg_version):
    """

    :param provides_template:
    :param pg_version:
    :return:
    """
    return [(t[0].format(pg_version), t[1].format(pg_version)) for t in provides_template]


ppg_11_versions = {
    "deb_pkg_ver": DEB_PKG_VERSIONS,
    "deb_packages": fill_template_form(DEB_PACKAGES_TEMPLATE, "11"),
    "deb_provides": fill_provides_template_form(DEB_PROVIDES_TEMPLATE, "11"),
    "rpm7_provides": fill_provides_template_form(RPM7_PROVIDES_TEMPLATE, "11"),
    'rpm_provides': fill_provides_template_form(RPM_PROVIDES_TEMPLATE, "11"),
    "rpm_packages": fill_template_form(RPM_PACKAGES_TEMPLATE, "11"),
    "rpm7_packages": fill_template_form(RPM7_PACKAGES_TEMPLATE, "11"),
    "rhel_files": fill_template_form(RHEL_FILES_TEMPLATE, "11"),
    "deb_files": fill_template_form(DEB_FILES_TEMPLATE, "11"),
    "extensions": PG11_EXTENSIONS,
    "languages": LANGUAGES
                    }

ppg_12_versions = {"deb_pkg_ver": "",
                   "deb_packages": fill_template_form(DEB_PACKAGES_TEMPLATE, "12"),
                   "deb_provides": fill_provides_template_form(DEB_PROVIDES_TEMPLATE, "12"),
                   "rpm7_provides": fill_provides_template_form(RPM7_PROVIDES_TEMPLATE, "12"),
                   'rpm_provides': fill_provides_template_form(RPM_PROVIDES_TEMPLATE, "12"),
                   "rpm_packages": fill_template_form(RPM_PACKAGES_TEMPLATE, "12"),
                   "rpm7_packages": fill_template_form(RPM7_PACKAGES_TEMPLATE, "12"),
                   "rhel_files": fill_template_form(RHEL_FILES_TEMPLATE, "12"),
                   "deb_files": fill_template_form(DEB_FILES_TEMPLATE, "12"),
                   "extensions": PG12_EXTENSIONS,
                   "languages": LANGUAGES}

ppg = {"ppg-11.5": ppg_11_versions,
       "ppg-11.6": ppg_11_versions,
       "ppg-11.7": ppg_11_versions,
       "ppg-11.8": ppg_11_versions,
       "ppg-12.2": ppg_12_versions,
       "ppg-12.3": ppg_12_versions}
