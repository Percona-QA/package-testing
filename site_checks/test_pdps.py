# Test website links for Percona Distribution for PS. Tarballs are not built for MySQL Router.
# Expected version formats:
# PS_VER_FULL="8.0.34-26.1"
# PXB_VER_FULL="8.0.34-29.1"
# ORCH_VER_FULL="3.2.6-10"
# PT_VER="3.5.4"
# PROXYSQL_VER="2.5.5"

import os
import requests
import pytest
import json
import re
from packaging import version

# Get versions from env vars
PS_VER_FULL= os.environ.get("PS_VER_FULL")
PXB_VER_FULL = os.environ.get("PXB_VER_FULL")
ORCH_VER_FULL = os.environ.get("ORCH_VER_FULL")
PT_VER = os.environ.get("PT_VER")
PROXYSQL_VER = os.environ.get("PROXYSQL_VER")


# Verify versions patterns
assert re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', PS_VER_FULL), "PS version format is not correct. Expected pattern with build: 8.0.34-26.1"
assert re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', PXB_VER_FULL), "PXB version format is not correct. Expected pattern with build: 8.0.34-29.1"
assert re.search(r'^\d+\.\d+\.\d+-\d+$', ORCH_VER_FULL), "Orchestrator version format is not correct. Expected pattern: 3.2.6-10"
assert re.search(r'^\d+\.\d+\.\d+$', PT_VER), "PT version format is not correct. Expected pattern: 3.5.5"
assert re.search(r'^\d+\.\d+\.\d+$', PROXYSQL_VER), "PROXYSQL version format is not correct. Expected pattern with build: 2.5.5"

# Get different version formats for PS, PXB, ORCH
# PS
PS_VER = '.'.join(PS_VER_FULL.split('.')[:-1]) # 8.0.34-26
PS_VER_UPSTREAM = PS_VER_FULL.split('-')[0] # 8.0.34
PS_BUILD_NUM = PS_VER_FULL.split('.')[-1] # 1
upstream_version, build_str = PS_VER_FULL.split("-")  # "8.0.34", "26.1"
minor_version = upstream_version.split(".")[-1]  # "34"
build_parts = build_str.split(".")  # ["26", "1"]

PS_LAST_VER = f"{int(minor_version) % 10}-{build_parts[1]}"  # Output: 4-1

# PXB
PXB_VER = '.'.join(PXB_VER_FULL.split('.')[:-1]) # 8.0.34-29
PXB_MAJOR_VERSION=''.join(PXB_VER_FULL.split('.')[:2]) # 80
PXB_BUILD_NUM = PXB_VER_FULL.split('.')[-1] # 1

# ORCH
ORCH_VER = ORCH_VER_FULL.split('-')[0]

# Create list of supported software files
if version.parse(PS_VER) > version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PS_VER) > version.parse("8.0.0") and version.parse(PS_VER) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=[ 'bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PS_VER) > version.parse("5.7.0") and version.parse(PS_VER) < version.parse("8.0.0"):
    assert not version.parse(PS_VER) > version.parse("5.7.0") and version.parse(PS_VER) < version.parse("8.0.0"), "PS 5.7 is not suported"

SOFTWARE_FILES=DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES+['binary','source']

RHEL_EL={'redhat/7':'7', 'redhat/8':'8', 'redhat/9':'9'}

BASE_PATH = f"https://downloads.percona.com/downloads/percona-distribution-mysql-ps/percona-distribution-mysql-ps-{PS_VER_UPSTREAM}"

def get_package_tuples():
    packages = []
    for software_file in SOFTWARE_FILES:
      #  data = 'version_files=percona-distribution-mysql-ps-' + PS_VER_UPSTREAM + '&software_files=' + software_file
      #  req = requests.post("https://www.percona.com/products-api.php",data=data,headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
        for software_file in SOFTWARE_FILES:
            if software_file == "binary":
                glibc_versions = ["2.35"] if version.parse(PS_VER) < version.parse("8.0.0") else ["2.28", "2.31", "2.34", "2.35"]
                for glibc_version in glibc_versions:
                    # Check PS tarballs:
                    for suffix in ["", "-minimal"]:
                        filename =  f"Percona-Server-{PS_VER}-Linux.x86_64.glibc{glibc_version}{suffix}.tar.gz"
                        packages.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{filename}"))

                    if glibc_version in ['2.34', '2.35'] and version.parse("8.0.0") < version.parse(PS_VER) < version.parse("8.1.0"):
                        for suffix in ["-zenfs", "-zenfs-minimal"]:
                            filename = f"Percona-Server-{PS_VER}-Linux.x86_64.glibc{glibc_version}{suffix}.tar.gz"
                            packages.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{filename}"))

                    if glibc_version == "2.17":
                        xb_files = [ 
                        f"percona-xtrabackup-{PXB_VER}-Linux-x86_64.glibc{glibc_version}-minimal.tar.gz",
                        f"percona-xtrabackup-{PXB_VER}-Linux-x86_64.glibc{glibc_version}.tar.gz"
                        ]
                        for file in xb_files:
                            packages.append((software_file, xb_files, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))

                # Check ProxySQL
                    if glibc_version in ["2.17","2.23"]:
                        for glibc_version in glibc_versions:
                            filename= f"proxysql-{PROXYSQL_VER}-Linux-x86_64.glibc2.17.tar.gz"
                            packages.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))
                # Check mysql-shell tarballs:
            # Check PT
          #  filename = f"'percona-toolkit' + PT_VER + '_x86_64.tar.gz'"
           # packages.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{filename}"))
            # Check PXB
            
        # Test source tarballs
            elif software_file == "source":
            # Check PS sources:
                source_files = [
                    f"percona-server-{PS_VER}.tar.gz",
                    f"percona-mysql-shell-{PS_VER_UPSTREAM}.tar.gz",
                    f"percona-orchestrator-{ORCH_VER}.tar.gz",
                    f"percona-xtrabackup-{PXB_VER}.tar.gz"
                ]
                for file in source_files:
                    packages.append(("source", file, f"{BASE_PATH}/source/tarball/{file}"))
        # Test packages for every OS
        for software_file in DEB_SOFTWARE_FILES:
            ps_deb_name_suffix= f"{PS_VER}-{PS_BUILD_NUM}.{software_file}_amd64.deb"
            deb_files = [
            f"percona-server-server_{ps_deb_name_suffix}",
            f"percona-server-test_{ps_deb_name_suffix}",
            f"percona-server-client_{ps_deb_name_suffix}",
            f"percona-server-rocksdb_{ps_deb_name_suffix}",
            f"percona-mysql-router_{ps_deb_name_suffix}",
            f"percona-server-source_{ps_deb_name_suffix}",
            f"percona-server-common_{ps_deb_name_suffix}",
            f"percona-server-dbg_{ps_deb_name_suffix}",
                # Check mysql-shell deb packages:
            f"percona-mysql-shell_{PS_VER_UPSTREAM}-1-1.{software_file}_amd64.deb",
                # Check orchestrator deb packages:
            f"percona-orchestrator-client_{ORCH_VER_FULL}.{software_file}_amd64.deb",
            f"percona-orchestrator-cli_{ORCH_VER_FULL}.{software_file}_amd64.deb",
            f"percona-orchestrator_{ORCH_VER_FULL}.{software_file}_amd64.deb"]
                # Check PT deb packages:
          #  f"percona-toolkit_{PT_VER}.1" ]
            for file in deb_files:
                packages.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))
                # Check PXB deb packages:
            pxb_deb_name_suffix= f"{PXB_MAJOR_VERSION}_{PXB_VER}-{PXB_BUILD_NUM}.{software_file}_amd64.deb"
            filename= [f"percona-xtrabackup-{pxb_deb_name_suffix}",
            f"percona-xtrabackup-dbg-{pxb_deb_name_suffix}",
            f"percona-xtrabackup-test-{pxb_deb_name_suffix}" ]
            for file in filename:
                packages.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))

        for software_file in RHEL_SOFTWARE_FILES:
                # Check PS rpm packages:
            el = RHEL_EL[software_file]
            ps_rpm_name_suffix= f"{PS_VER}.{PS_BUILD_NUM}.el{el}.x86_64.rpm"
            rpm_files = [
            f"percona-server-server-{ps_rpm_name_suffix}",
            f"percona-server-test-{ps_rpm_name_suffix}",
            f"percona-server-client-{ps_rpm_name_suffix}",
            f"percona-server-rocksdb-{ps_rpm_name_suffix}",
            f"percona-mysql-router-{ps_rpm_name_suffix}",
            f"percona-server-devel-{ps_rpm_name_suffix}",
            f"percona-server-shared-{ps_rpm_name_suffix}",
            f"percona-icu-data-files-{ps_rpm_name_suffix}",
            f"percona-server-debuginfo-{ps_rpm_name_suffix}",
            f'percona-orchestrator-{ORCH_VER_FULL}.el{el}.x86_64.rpm',
            f'percona-orchestrator-cli-{ORCH_VER_FULL}.el{el}.x86_64.rpm',
            f'percona-orchestrator-client-{ORCH_VER_FULL}.el{el}.x86_64.rpm']

            if software_file != "redhat/9":
                rpm_files.append(f"percona-server-shared-compat-{ps_rpm_name_suffix}"),
            for file in rpm_files:
                packages.append((software_file, file, f"{BASE_PATH}/binary/redhat/{el}/x86_64/{file}"))
                el = RHEL_EL[software_file]
                pxb_rpm_name_suffix=  f"{PXB_VER}.{PXB_BUILD_NUM}.el{el}.x86_64.rpm"
                filename= [
                f"percona-xtrabackup-{PXB_MAJOR_VERSION}-{pxb_rpm_name_suffix}",
                f"percona-xtrabackup-{PXB_MAJOR_VERSION}-debuginfo-{pxb_rpm_name_suffix}",
                f"percona-xtrabackup-test-{PXB_MAJOR_VERSION}-{pxb_rpm_name_suffix}"]
                for file in filename:
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

