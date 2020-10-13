from molecule.ppg.tests.versions.extensions import get_extensions_ppg11, get_extensions_ppg12

DISTROS = ['buster', 'stretch', 'bionic', 'focal']
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

DEB12_PACKAGES_TEMPLATE = [
    "percona-postgresql-{}",
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
                         ("percona-postgresql-plpython3-{}", "postgresql-plpython3"),
                         ("percona-postgresql-pltcl-{}", "postgresql-{}-pltcl"),
                         ("percona-postgresql-all", "postgresql-all")
                         ]

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


def fill_package_versions(packages, distros):
    result = []
    for d in distros:
        for p in packages:
            result.append(".".join([p, d]))
    return result


def get_pg11_versions(distros, packages, distro_type):
    ppg_11_versions = {
        "deb_packages": fill_template_form(DEB_PACKAGES_TEMPLATE, "11"),
        "deb_provides": fill_provides_template_form(DEB_PROVIDES_TEMPLATE, "11"),
        "rpm7_provides": fill_provides_template_form(RPM7_PROVIDES_TEMPLATE, "11"),
        'rpm_provides': fill_provides_template_form(RPM_PROVIDES_TEMPLATE, "11"),
        "rpm_packages": fill_template_form(RPM_PACKAGES_TEMPLATE, "11"),
        "rpm7_packages": fill_template_form(RPM7_PACKAGES_TEMPLATE, "11"),
        "rhel_files": fill_template_form(RHEL_FILES_TEMPLATE, "11"),
        "deb_files": fill_template_form(DEB_FILES_TEMPLATE, "11"),
        "extensions": get_extensions_ppg11(distro_type),
        "languages": LANGUAGES
                        }
    ppg_11_versions.update({"deb_pkg_ver": fill_package_versions(packages=packages,
                                                                 distros=distros)})
    return ppg_11_versions


def get_pg12_versions(distros, packages, distro_type):
    ppg_12_versions = {
                       "deb_packages": fill_template_form(DEB12_PACKAGES_TEMPLATE, "12"),
                       "deb_provides": fill_provides_template_form(DEB_PROVIDES_TEMPLATE, "12"),
                       "rpm7_provides": fill_provides_template_form(RPM7_PROVIDES_TEMPLATE, "12"),
                       'rpm_provides': fill_provides_template_form(RPM_PROVIDES_TEMPLATE, "12"),
                       "rpm_packages": fill_template_form(RPM_PACKAGES_TEMPLATE, "12"),
                       "rpm7_packages": fill_template_form(RPM7_PACKAGES_TEMPLATE, "12"),
                       "rhel_files": fill_template_form(RHEL_FILES_TEMPLATE, "12"),
                       "deb_files": fill_template_form(DEB_FILES_TEMPLATE, "12"),
                       "extensions": get_extensions_ppg12(distro_type),
                       "languages": LANGUAGES}

    ppg_12_versions.update({"deb_pkg_ver": fill_package_versions(packages=packages,
                                                                 distros=distros)})
    return ppg_12_versions


def get_pg13_versions(distros, packages, distro_type):
    ppg_13_versions = {
                       "deb_packages": fill_template_form(DEB12_PACKAGES_TEMPLATE, "13"),
                       "deb_provides": fill_provides_template_form(DEB_PROVIDES_TEMPLATE, "13"),
                       "rpm7_provides": fill_provides_template_form(RPM7_PROVIDES_TEMPLATE, "13"),
                       'rpm_provides': fill_provides_template_form(RPM_PROVIDES_TEMPLATE, "13"),
                       "rpm_packages": fill_template_form(RPM_PACKAGES_TEMPLATE, "13"),
                       "rpm7_packages": fill_template_form(RPM7_PACKAGES_TEMPLATE, "13"),
                       "rhel_files": fill_template_form(RHEL_FILES_TEMPLATE, "13"),
                       "deb_files": fill_template_form(DEB_FILES_TEMPLATE, "13"),
                       "extensions": get_extensions_ppg12(distro_type),
                       "languages": LANGUAGES}

    ppg_13_versions.update({"deb_pkg_ver": fill_package_versions(packages=packages,
                                                                 distros=distros)})
    return ppg_13_versions


def get_ppg_versions(distro_type):
    """Get dictionary with versions
    :param distro_type: deb or rpm
    :return:
    """

    return {"ppg-11.5": get_pg11_versions(packages=["11+204-1", "204-1", '1:11-5', '11+210-1'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-11.6": get_pg11_versions(packages=["11+204-1", "204-1", '2:11-6.2', '11+210-1'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-11.7": get_pg11_versions(packages=["11+214-1", "204-1", '2:11-7.2', '11+210-1'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-11.8": get_pg11_versions(packages=["11+204-1", '2:11-8.1', '215-1', '11+215-1'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-11.9": get_pg11_versions(packages=["11+204-1", '2:11-9.1', '216-1', '11+216-1'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-12.2": get_pg12_versions(packages=["2:12-3.1", "12+215-1", '215-1'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-12.3": get_pg12_versions(packages=["2:12-3.1", "12+215-1", '215-1'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-12.4": get_pg12_versions(packages=["2:12-4.2", "12+216-3", '216-3'],
                                          distros=DISTROS, distro_type=distro_type),
            "ppg-13.0": get_pg13_versions(packages=["2:13-0.1", "13+219-1", '219-1'],
                                          distros=DISTROS, distro_type=distro_type)
            }
