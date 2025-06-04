# Test website links for Percona Distribution for PXC. Binary tarballs are not built for haproxy, Repl manager.
# Expected version formats:
# PXC_VER_FULL="8.0.34-26.1"
# PXB_VER_FULL="8.0.34-29.1"
# PT_VER="3.5.4"
# PROXYSQL_VER="2.5.5"
# HAPROXY_VER="2.8.1"
# REPL_MAN_VER="1.0"

import os
import requests
import pytest
import json
import re
from packaging import version

# Get versions from env vars
PXC_VER_FULL = os.environ.get("PXC_VER_FULL")
PXB_VER_FULL = os.environ.get("PXB_VER_FULL")
PT_VER = os.environ.get("PT_VER")
PROXYSQL_VER = os.environ.get("PROXYSQL_VER")
HAPROXY_VER = os.environ.get("HAPROXY_VER")
REPL_MAN_VER = os.environ.get("REPL_MAN_VER")

# Verify versions patterns
assert re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', PXC_VER_FULL), "PS version format is not correct. Expected pattern with build: 8.0.34-26.1"
assert re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', PXB_VER_FULL), "PXB version format is not correct. Expected pattern with build: 8.0.34-29.1"
assert re.search(r'^\d+\.\d+\.\d+$', PT_VER), "PT version format is not correct. Expected pattern: 3.5.5"
assert re.search(r'^\d+\.\d+\.\d+$', PROXYSQL_VER), "PROXYSQL version format is not correct. Expected pattern: 2.5.5"
assert re.search(r'^\d+\.\d+\.\d+$', HAPROXY_VER), "Orchestrator version format is not correct. Expected pattern: 3.2.6-10"
assert re.search(r'^\d+\.\d+$', REPL_MAN_VER), "Orchestrator version format is not correct. Expected pattern: 3.2.6-10"

# Get different version formats for PXC, PXB
# PXC
PXC_VER_PERCONA = '.'.join(PXC_VER_FULL.split('.')[:-1]) # 8.1.0-1, 8.0.34-26, 5.7.43-31.65
PXC_VER_UPSTREAM = PXC_VER_FULL.split('-')[0] # 8.0.34 OR 8.1.0 OR 5.7.43
PXC_BUILD_NUM = PXC_VER_FULL.split('.')[-1] # "1"

# PXB
PXB_VER = '.'.join(PXB_VER_FULL.split('.')[:-1]) # 8.0.34-26
PXB_MAJOR_VERSION=''.join(PXB_VER_FULL.split('.')[:2]) # 80
PXB_BUILD_NUM = PXB_VER_FULL.split('.')[-1] # 1

# Create list of supported software files
# note: 8.1 etc (innovation releases) are not supported by PXC yest bu added in this check script.
if version.parse(PXC_VER_PERCONA) > version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=[ 'redhat/8', 'redhat/9']
elif version.parse(PXC_VER_PERCONA) > version.parse("8.0.0") and version.parse(PXC_VER_PERCONA) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=[ 'bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=[ 'redhat/8', 'redhat/9']
elif version.parse(PXC_VER_PERCONA) > version.parse("5.7.0") and version.parse(PXC_VER_PERCONA) < version.parse("8.0.0"):
    assert not version.parse(PXC_VER_PERCONA) > version.parse("5.7.0") and version.parse(PXC_VER_PERCONA) < version.parse("8.0.0"), "PS 5.7 is not suported"

SOFTWARE_FILES=DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES+['binary','source']

RHEL_EL={'redhat/7':'7', 'redhat/8':'8', 'redhat/9':'9'}
BASE_PATH = f"https://downloads.percona.com/downloads/percona-distribution-mysql-pxc/percona-distribution-mysql-pxc-{PXC_VER_UPSTREAM}"


def get_package_tuples():
    list = []
    for software_file in SOFTWARE_FILES:
        # Test source tarballs
        if software_file == 'source':
            # Check PXC sources:
            source_file= [
            f"Percona-XtraDB-Cluster-{PXC_VER_PERCONA}.tar.gz",
            f"percona-xtrabackup-{PXB_VER}.tar.gz" ,
            f"proxysql2-{PROXYSQL_VER}.tar.gz" ,
            f"percona-haproxy-{HAPROXY_VER}.tar.gz",
            f"percona-replication-manager-{REPL_MAN_VER}.tar.gz"]
            for file in source_file:
                list.append(("source", file, f"{BASE_PATH}/source/tarball/{file}"))
        
    for software_file in DEB_SOFTWARE_FILES:
                # Check PXC deb packages:
        pxc_deb_name_suffix=PXC_VER_PERCONA + "-" + PXC_BUILD_NUM + "." + software_file + "_amd64.deb"
        deb_files=[
                f"percona-xtradb-cluster-server_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster-test_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster-client_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster-garbd_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster-full_{pxc_deb_name_suffix}",
                f"libperconaserverclient22-dev_{pxc_deb_name_suffix}",
                f"libperconaserverclient22_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster-source_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster-common_{pxc_deb_name_suffix}",
                f"percona-xtradb-cluster-dbg_{pxc_deb_name_suffix}" ]
        for file in deb_files:
            list.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))
        pxb_deb_name_suffix= f"{PXB_MAJOR_VERSION}_{PXB_VER}-{PXB_BUILD_NUM}.{software_file}_amd64.deb"
        filename =[
                f"percona-xtrabackup-{pxb_deb_name_suffix}",
                f"percona-xtrabackup-dbg-{pxb_deb_name_suffix}",
                f"percona-xtrabackup-test-{pxb_deb_name_suffix}",
                f"percona-haproxy_{HAPROXY_VER}-1.{software_file}_amd64.deb",
                f"percona-replication-manager_{REPL_MAN_VER}-1.{software_file}_amd64.deb" ]
        for file in filename:
            list.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))
    for software_file in RHEL_SOFTWARE_FILES:
                # Check PXC rpm packages:
        el = RHEL_EL[software_file]
        pxc_rpm_name_suffix= f"{PXC_VER_PERCONA}.{PXC_BUILD_NUM}.el{el}.x86_64.rpm"
        rpm_files= [
                f"percona-xtradb-cluster-server-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-test-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-client-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-garbd-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-full-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-devel-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-shared-{pxc_rpm_name_suffix}",
                f"percona-xtradb-cluster-icu-data-files-{pxc_rpm_name_suffix}"]
        if software_file != "redhat/9":
            rpm_files.append(f"percona-xtradb-cluster-shared-compat-{pxc_rpm_name_suffix}"),
            rpm_files.append(f"percona-xtradb-cluster-debuginfo-{pxc_rpm_name_suffix}")
        for file in rpm_files:
            list.append((software_file, file, f"{BASE_PATH}/binary/redhat/{el}/x86_64/{file}"))

        pxb_rpm_name_suffix=f"-{PXB_VER}.{PXB_BUILD_NUM}.el{el}.x86_64.rpm"
        filename= [
                f"percona-xtrabackup-{PXB_MAJOR_VERSION}{pxb_rpm_name_suffix}",
                f"percona-xtrabackup-{PXB_MAJOR_VERSION}-debuginfo{pxb_rpm_name_suffix}",
                f"percona-xtrabackup-test-{PXB_MAJOR_VERSION}{pxb_rpm_name_suffix}",
                f"percona-haproxy-{HAPROXY_VER}-1.el{el}.x86_64.rpm",
                f"percona-haproxy-debuginfo-{HAPROXY_VER}-1.el{el}.x86_64.rpm",
                f"percona-replication-manager-{REPL_MAN_VER}-1.el{el}.x86_64.rpm"]
        for file in filename:
            list.append((software_file, file, f"{BASE_PATH}/binary/redhat/{el}/x86_64/{file}"))    
            

    return list

LIST_OF_PACKAGES = get_package_tuples()
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
