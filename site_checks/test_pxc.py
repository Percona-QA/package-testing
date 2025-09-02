# Test website links for PXC.
# Expected version format:
# PXC_VER_FULL="8.0.34-26.1"
# PXC_VER_FULL="5.7.43-31.65.1"
# PXC57_INNODB="47"

import os
import requests
import pytest
import json
import re
from packaging import version

PXC_VER_FULL = os.environ.get("PXC_VER_FULL")

PXC_VER_UPSTREAM = PXC_VER_FULL.split('-')[0] # 8.0.34 OR 8.1.0 OR 5.7.43

# Validate that full PXC version are passed (with build number): 8.1.0-1.1; 8.0.34-26.1; 5.7.43-31.65.1
if version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0"):
    assert re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', PXC_VER_FULL), "PXC 8.0/8.1 version is not full. Expected pattern 8.1.0-1.1 " # 8.1.0-1.1 or  8.0.34-26.1
elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
    assert re.search(r'^\d+\.\d+\.\d+-\d+\.\d+\.\d+$', PXC_VER_FULL), "PXC 5.7 version is not full. Expected pattern '5.7.43-31.65.1'" # 5.7.43-31.65.1

# Get different version formats for PXC
PXC_VER_PERCONA = '.'.join(PXC_VER_FULL.split('.')[:-1]) # 8.1.0-1, 8.0.34-26, 5.7.43-31.65
PXC_BUILD_NUM = PXC_VER_FULL.split('.')[-1] # 1
DATA_VERSION=''.join(PXC_VER_FULL.split('.')[:2])

BASE_PATH = f"https://downloads.percona.com/downloads/Percona-XtraDB-Cluster-{DATA_VERSION}/Percona-XtraDB-Cluster-{PXC_VER_UPSTREAM}"

# Create list of supported software files and PXC 57 specific version numbers
if version.parse(PXC_VER_UPSTREAM) >= version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'focal', 'jammy', 'noble']
    RHEL_SOFTWARE_FILES=[ 'redhat/8', 'redhat/9']
elif version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'focal', 'jammy', 'noble']
    RHEL_SOFTWARE_FILES=['redhat/8', 'redhat/9']
elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'bionic','focal', 'jammy', 'noble']
    RHEL_SOFTWARE_FILES=['redhat/8', 'redhat/9']
    # Get PXC57 specific version numbers
    PXC57_WSREP_PROV_VER = PXC_VER_FULL.split('.')[-2] # for 5.7.43-31.65.1 = 65
    os.environ.get("PXC57_INNODB"), "PXC57_INNODB parameter is not defined!"
    PXC57_INNODB=os.environ.get("PXC57_INNODB")


SOFTWARE_FILES=DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES+['binary','source']

RHEL_EL={'redhat/8':'8', 'redhat/9':'9'}

def get_package_tuples():
    list = []
    for software_file in SOFTWARE_FILES:
      #  data = 'version_files=Percona-XtraDB-Cluster-' + PXC_VER_UPSTREAM + '&software_files=' + software_file
       # req = requests.post("https://www.percona.com/products-api.php",data=data,headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
      #  freq.status_code == 200
       # freq.text != '[]', software_file
        # Check binary tarballs
        if "binary" in SOFTWARE_FILES:
            glibc_versions = ["2.35"] if version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0") else ["2.28", "2.31", "2.34", "2.35"]
            for glibc_version in glibc_versions:
                if version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0"):
                    for suffix in ["", "-minimal"]:
                        filename = [
                            f"Percona-XtraDB-Cluster_{PXC_VER_FULL}_Linux.x86_64.glibc{glibc_version}{suffix}.tar.gz",
                            f"Percona-XtraDB-Cluster_{PXC_VER_FULL}_Linux.x86_64.glibc{glibc_version}.tar.gz"]
                        for file in filename:
                            list.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{file}"))

                elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
                    for filename in [
                        f"Percona-XtraDB-Cluster_" + PXC_VER_UPSTREAM + "-rel" + PXC57_INNODB + "-" + PXC57_WSREP_PROV_VER + "." + PXC_BUILD_NUM + ".Linux.x86_64.glibc"+glibc_version+"-minimal.tar.gz",
                        f"Percona-XtraDB-Cluster_" + PXC_VER_UPSTREAM + "-rel" + PXC57_INNODB + "-" + PXC57_WSREP_PROV_VER + "." + PXC_BUILD_NUM + ".Linux.x86_64.glibc"+glibc_version+".tar.gz"
                    ]:
                        list.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{file}"))

        # Check source tarballs
        elif software_file == 'source':
            if version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0"):
                for filename in [
                    f"Percona-XtraDB-Cluster-" + PXC_VER_PERCONA + ".tar.gz" ,
                    f"percona-xtradb-cluster_" + PXC_VER_PERCONA + ".orig.tar.gz" ,
                    f"percona-xtradb-cluster-" + PXC_VER_FULL  + ".generic.src.rpm"
                ]:
                    list.append(("source", filename, f"{BASE_PATH}/source/tarball/{filename}"))

            elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
                for filename in [
                    f"Percona-XtraDB-Cluster-" + PXC_VER_PERCONA + ".tar.gz",
                    f"percona-xtradb-cluster-5.7_" + PXC_VER_PERCONA + ".orig.tar.gz",
                    f"Percona-XtraDB-Cluster-57-" + PXC_VER_FULL + ".generic.src.rpm"
                ]:
                    list.append(("source", filename, f"{BASE_PATH}/source/tarball/{filename}"))

        # Test packages for every OS
        else:
            if version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0"):
                if software_file in DEB_SOFTWARE_FILES:
                    pxc_deb_name_suffix=PXC_VER_PERCONA + "-" + PXC_BUILD_NUM + "." + software_file + "_amd64.deb"
                    deb_files = [
                        f"percona-xtradb-cluster-server_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster-test_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster-client_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster-garbd_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster-full_" + pxc_deb_name_suffix ,
                        f"libperconaserverclient21-dev_" + pxc_deb_name_suffix ,
                        f"libperconaserverclient21_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster-source_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster-common_" + pxc_deb_name_suffix ,
                        f"percona-xtradb-cluster-dbg_" + pxc_deb_name_suffix ,
                        ]
                    for file in deb_files:
                        list.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))

                if software_file in RHEL_SOFTWARE_FILES:
                    pxc_rpm_name_suffix=PXC_VER_PERCONA + "." + PXC_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                    el = RHEL_EL[software_file]
                    rpm_files = [
                        f"percona-xtradb-cluster-server-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-test-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-client-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-garbd-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-full-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-devel-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-shared-" + pxc_rpm_name_suffix ,
                        f"percona-xtradb-cluster-icu-data-files-" + pxc_rpm_name_suffix 
                    ]
                    if software_file != "redhat/9":
                        rpm_files.append(f"percona-server-shared-compat-{pxc_rpm_name_suffix}")
                    for file in rpm_files:
                        list.append((software_file, file, f"{BASE_PATH}/binary/redhat/{el}/x86_64/{file}"))

    
            elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
                assert any("dbg" in f or "debug" in f for f in deb_files + rpm_files), \
                    "Neither 'dbg' nor 'debug' found in expected filenames"
                if software_file in DEB_SOFTWARE_FILES:
                    pxc_deb_name_suffix=PXC_VER_PERCONA + "-" + PXC_BUILD_NUM + "." + software_file + "_amd64.deb"
                    deb_files = [
                    f"libperconaserverclient20-dev_" + pxc_deb_name_suffix ,
                    f"libperconaserverclient20_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-source-5.7_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-common-5.7_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-57_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-server-5.7_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-test-5.7_"  + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-client-5.7_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-garbd-5.7_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-full-57_" + pxc_deb_name_suffix ,
                    f"percona-xtradb-cluster-5.7-dbg_" + pxc_deb_name_suffix ]

                    for file in deb_files:
                        list.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))

                if software_file in RHEL_SOFTWARE_FILES:
                    pxc_rpm_name_suffix=PXC_VER_PERCONA + "." + PXC_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                    el = RHEL_EL[software_file]
                    rpm_files = [
                    f"Percona-XtraDB-Cluster-server-57-" + pxc_rpm_name_suffix ,
                    f"Percona-XtraDB-Cluster-test-57-" + pxc_rpm_name_suffix ,
                    f"Percona-XtraDB-Cluster-client-57-" + pxc_rpm_name_suffix ,
                    f"Percona-XtraDB-Cluster-garbd-57-" + pxc_rpm_name_suffix ,
                    f"Percona-XtraDB-Cluster-full-57-" + pxc_rpm_name_suffix ,
                    f"Percona-XtraDB-Cluster-devel-57-" + pxc_rpm_name_suffix ,
                    f"Percona-XtraDB-Cluster-shared-57-" + pxc_rpm_name_suffix ,
                    f"Percona-XtraDB-Cluster-57-debuginfo-" + pxc_rpm_name_suffix ]
                    if software_file != "redhat/9":
                        rpm_files.append(f"percona-server-shared-compat-{pxc_rpm_name_suffix}")
                    for file in rpm_files:
                        list.append((software_file, file, f"{BASE_PATH}/binary/redhat/{el}/x86_64/{file}"))
                
    return list


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