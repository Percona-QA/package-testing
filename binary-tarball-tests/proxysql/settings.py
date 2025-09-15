#!/usr/bin/env python3
import os

def source_environment_file(filepath="/etc/environment"):
    """
    Loads environment variables from a given file into os.environ.
    """
    try:
        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip('\'"')
                    os.environ[key] = value
                    print(f"{line}")
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"Error while sourcing environment file: {e}")

def set_proxysql_vars():
    """
    Retrieves and returns environment-based settings for ProxySQL tarball tests.
    """
    source_environment_file()
    proxysql_version = os.getenv("Proxysql_version")
    base_dir = os.getenv("BASE_DIR")
    glibc_version = os.getenv("GLIBC_VERSION")
    tarball_name = os.getenv("TARBALL_NAME")
    proxysql_major_version = os.getenv("PROXYSQL_MAJOR_VERSION")

    # Parse version details if possible
    if proxysql_version and "-" in proxysql_version:
        proxysql_version_percona, proxysql_version_upstream = proxysql_version.split("-", 1)
    else:
        proxysql_version_percona = proxysql_version
        proxysql_version_upstream = ""

    return {
        "proxysql_version": proxysql_version,
        "base_dir": base_dir,
        "glibc_version": glibc_version,
        "tarball_name": tarball_name,
        "proxysql_major_version": proxysql_major_version,
        "proxysql_version_percona": proxysql_version_percona,
        "proxysql_version_upstream": proxysql_version_upstream,
    }

# Load environment variables into globals
vars = set_proxysql_vars()
proxysql_version = vars["proxysql_version"]
base_dir = vars["base_dir"]
glibc_version = vars["glibc_version"]
tarball_name = vars["tarball_name"]
proxysql_major_version = vars["proxysql_major_version"]
proxysql_version_percona = vars["proxysql_version_percona"]
proxysql_version_upstream = vars["proxysql_version_upstream"]

# Expected files/binaries in tarballs
if glibc_version == "2.31":
    proxysql2x_files = [
        "lib/private/libnettle.so.7.0",
        "lib/private/libidn2.so.0.3.6",
        "etc/proxysql-admin.cnf",
        "etc/proxysql.cnf",
    ]
else:
    proxysql2x_files = [
        "lib/private/libidn2.so.0.3.6",
        "etc/proxysql-admin.cnf",
        "etc/proxysql.cnf",
    ]

proxysql2x_binaries = [
    "usr/bin/proxysql-admin",
    "usr/bin/proxysql",
    "usr/bin/percona-scheduler-admin",
]

def get_artifact_sets():
    """
    Return expected binaries/files depending on ProxySQL version.
    Supports 2.7.x and 3.x.
    """
    vars = set_proxysql_vars()
    proxysql_major_version = vars["proxysql_major_version"]

    if proxysql_major_version.startswith(("2.7", "3.")):
        return proxysql2x_binaries, proxysql2x_files
    else:
        raise ValueError(f"Unsupported proxysql version: {proxysql_major_version}")

