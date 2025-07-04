
import os
import requests
import pytest
import json
import re
from packaging import version

PS_VER_FULL = os.environ.get("PS_VER_FULL")

# Verify format of passed PS_VER_FULL
assert PS_VER_FULL is not None, "Environment variable PS_VER_FULL must be set."
assert re.match(r'^\d+\.\d+\.\d+-\d+\.\d+$', PS_VER_FULL), \
    f"PS version format is not correct: {PS_VER_FULL}. Expected pattern: 8.0.34-26.1"

# Parse values
version_main, build_full = PS_VER_FULL.split("-")      # "8.0.42", "33.1"
PS_VER = f"{version_main}-{build_full.split('.')[0]}"  # "8.0.42-33"
PS_BUILD_NUM = build_full.split(".")[1]                 # "1"
MAJOR_VERSION = ".".join(version_main.split(".")[:2])

BASE_PATH = f"https://downloads.percona.com/downloads/Percona-Server-{MAJOR_VERSION}/Percona-Server-{PS_VER}"

if version.parse(PS_VER) > version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'focal', 'jammy','noble']
    RHEL_SOFTWARE_FILES=[ 'redhat/8', 'redhat/9']
elif version.parse(PS_VER) > version.parse("8.0.0") and version.parse(PS_VER) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'focal', 'jammy','noble']
    RHEL_SOFTWARE_FILES=['redhat/8', 'redhat/9']
elif version.parse(PS_VER) > version.parse("5.7.0") and version.parse(PS_VER) < version.parse("8.0.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'bionic', 'focal', 'jammy','noble']
    RHEL_SOFTWARE_FILES=['redhat/8', 'redhat/9']
else:
    raise AssertionError(f"Unsupported Percona Server version: {PS_VER}")

SOFTWARE_FILES=DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES+['binary','source']
RHEL_EL={ 'redhat/8':'8', 'redhat/9':'9'}

def get_package_tuples():
    packages = []
    for software_file in SOFTWARE_FILES:
        if "binary" in SOFTWARE_FILES:
            glibc_versions = ["2.35"] if version.parse(PS_VER) < version.parse("8.0.0") else ["2.28", "2.31", "2.34", "2.35"]
            for glibc_version in glibc_versions:
                for suffix in ["", "-minimal"]:
                    filename = f"Percona-Server-{PS_VER}-Linux.x86_64.glibc{glibc_version}{suffix}.tar.gz"
                    packages.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{filename}"))

                if glibc_version in ['2.34', '2.35'] and version.parse("8.0.0") < version.parse(PS_VER) < version.parse("8.1.0"):
                    for suffix in ["-zenfs", "-zenfs-minimal"]:
                        filename = f"Percona-Server-{PS_VER}-Linux.x86_64.glibc{glibc_version}{suffix}.tar.gz"
                        packages.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{filename}"))
        
        if "source" in SOFTWARE_FILES:
            for filename in [
                f"percona-server-{PS_VER}.tar.gz",
            ]:
                packages.append(("source", filename, f"{BASE_PATH}/source/tarball/{filename}"))


        # Test source tarballs
    for software_file in DEB_SOFTWARE_FILES:
        suffix = f"{PS_VER}-{PS_BUILD_NUM}.{software_file}_amd64.deb"
        deb_files = [
            f"percona-server-server_{suffix}",
            f"percona-server-test_{suffix}",
            f"percona-server-client_{suffix}",
            f"percona-server-rocksdb_{suffix}",
            f"percona-mysql-router_{suffix}",
            f"libperconaserverclient21-dev_{suffix}",
            f"libperconaserverclient21_{suffix}",
            f"percona-server-source_{suffix}",
            f"percona-server-common_{suffix}",
            f"percona-server-dbg_{suffix}"
        ]
        for file in deb_files:
            packages.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))

    # RPM packages
    for software_file in RHEL_SOFTWARE_FILES:
        el = RHEL_EL[software_file]
        suffix = f"{PS_VER}.{PS_BUILD_NUM}.el{el}.x86_64.rpm"
        rpm_files = [
            f"percona-server-server-{suffix}",
            f"percona-server-test-{suffix}",
            f"percona-server-client-{suffix}",
            f"percona-server-rocksdb-{suffix}",
            f"percona-mysql-router-{suffix}",
            f"percona-server-devel-{suffix}",
            f"percona-server-shared-{suffix}",
            f"percona-icu-data-files-{suffix}",
            f"percona-server-debuginfo-{suffix}"
        ]
        if software_file != "redhat/9":
            rpm_files.append(f"percona-server-shared-compat-{suffix}")
        for file in rpm_files:
            packages.append((software_file, file, f"{BASE_PATH}/binary/redhat/{el}/x86_64/{file}"))
    
    if version.parse(PS_VER) > version.parse("5.7.0") and version.parse(PS_VER) < version.parse("8.0.0"):
                assert any("dbg" in f or "debug" in f for f in deb_files + rpm_files), \
                    "Neither 'dbg' nor 'debug' found in expected filenames"
                if software_file in DEB_SOFTWARE_FILES:
                    suffix = f"{PS_VER}-{PS_BUILD_NUM}.{software_file}_amd64.deb"
                deb_files = [
                    f"percona-server-server-5.7_{suffix}",
                    f"percona-server-test-5.7_{suffix}",
                    f"percona-server-client-5.7_{suffix}",
                    f"percona-server-rocksdb-5.7_{suffix}",
                    f"percona-server-tokudb-5.7_{suffix}",
                    f"percona-server-source-5.7_{suffix}",
                    f"percona-server-common-5.7_{suffix}",
                    f"percona-server-5.7-dbg_{suffix}"
                ]
                for file in deb_files:
                    packages.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))

    if version.parse(PS_VER) > version.parse("5.7.0") and version.parse(PS_VER) < version.parse("8.0.0"):
                assert any("dbg" in f or "debug" in f for f in deb_files + rpm_files), \
                    "Neither 'dbg' nor 'debug' found in expected filenames"
                if software_file in RHEL_SOFTWARE_FILES:
                    el = RHEL_EL[software_file]
                    suffix = f"{PS_VER}.{PS_BUILD_NUM}.el{el}.x86_64.rpm"
                    rpm_files = [
                        f"Percona-Server-server-57-{suffix}",
                        f"Percona-Server-test-57-{suffix}",
                        f"Percona-Server-client-57-{suffix}",
                        f"Percona-Server-rocksdb-57-{suffix}",
                        f"Percona-Server-tokudb-57-{suffix}",
                        f"Percona-Server-devel-57-{suffix}",
                        f"Percona-Server-shared-57-{suffix}"
                    ]
                    if software_file != "redhat/9":
                        rpm_files.append(f"percona-server-shared-compat-{suffix}")
                    for file in rpm_files:
                        packages.append((software_file, file, f"{BASE_PATH}/binary/redhat/{el}/x86_64/{file}"))
                        

    return packages

LIST_OF_PACKAGES = get_package_tuples()

# Check that every link from website is working (200 reply and has some content-length)
@pytest.mark.parametrize(('software_file', 'filename', 'link'), LIST_OF_PACKAGES)
def test_packages_site(software_file, filename, link):
    print(f'\nTesting {software_file}, file: {filename}')
    print(link)
    try:
        req = requests.head(link, allow_redirects=True)
        assert req.status_code == 200, f"HEAD request failed with status {req.status_code}"
        content_length = int(req.headers.get('content-length', 0))
        assert content_length > 0, "Content length is zero"
    except AssertionError as e:
        print(f"FAIL: {filename} - {e}")
        raise
    else:
        print(f"PASS: {filename}")
