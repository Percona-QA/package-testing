#!/usr/bin/env python3
import os
import re

# -----------------------------
# Environment variables
# -----------------------------
base_dir = os.getenv("BASE_DIR")
proxysql_version = os.getenv("PROXYSQL_VERSION")
proxysql_major_version = os.getenv("PROXYSQL_MAJOR_VERSION")
tarball_name = os.getenv("TARBALL_NAME")

proxysql_version_major = proxysql_version.split('-')[0]
# -----------------------------
# File sets
# -----------------------------
proxysql_common_binaries = [
    "usr/bin/proxysql",
    "usr/bin/proxysql-admin",
    "usr/bin/percona-scheduler-admin",
]

proxysql_common_executables = proxysql_common_binaries + [
    "usr/bin/proxysql_galera_checker",
    "usr/bin/proxysql_node_monitor",
]

proxysql_common_files = [
    "etc/proxysql-admin.cnf",
    "etc/proxysql.cnf",
]

proxysql_symlinks = [
    ("lib/private/libidn2.so.0", "lib/private/libidn2.so.0.4.0"),
]

# -----------------------------
# Final selection based on major version
# -----------------------------
if proxysql_version_major.startswith("2.7"):
    proxysql_binaries = proxysql_common_binaries
    proxysql_executables = proxysql_common_executables
    proxysql_files = proxysql_common_files

elif proxysql_version_major.startswith("3."):
    proxysql_binaries = proxysql_common_binaries
    proxysql_executables = proxysql_common_executables
    proxysql_files = proxysql_common_files
