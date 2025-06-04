# Test website links for PXB.
# Expected version formats:
# PXB_VER_FULL="8.0.34-29.1"

import os
import requests
import pytest
import json
import re
from packaging import version

PXB_VER_FULL = os.environ.get("PXB_VER_FULL")
PXB_VERSION= re.sub(r'\.\d+$', '', PXB_VER_FULL)
PXB_VER_UPSTREAM = PXB_VER_FULL.split('-')[0] # 8.0.34 OR 8.1.0 OR 2.4.28
MAJOR_VERSION=''.join(PXB_VER_FULL.split('.')[:2]) # 80
MAJOR_MINOR_VERSION = '.'.join(PXB_VER_UPSTREAM.split('.')[:2])  
# Validate that full PXB version is passed (with build number): 2.4.28-1, 8.0.34-29.1; 8.1.0-1.1
if version.parse(PXB_VER_UPSTREAM) > version.parse("8.0.0"):
    assert re.search(r'^\d+\.\d+\.\d+-\d+\.\d+$', PXB_VER_FULL), "PXB 8.0/8.1 version is not full. Pass '8.1.0-1.1' / '8.0.34-26.1'" # 8.1.0-1.1 or  8.0.34-26.1
    PXB_VER = '.'.join(PXB_VER_FULL.split('.')[:-1]) #8.0.34-26
    PXB_BUILD_NUM = PXB_VER_FULL.split('.')[-1] # "1"
elif version.parse(PXB_VER_UPSTREAM) > version.parse("2.0.0") and version.parse(PXB_VER_UPSTREAM) < version.parse("8.0.0"):
    PXB_VER = PXB_VER_UPSTREAM #2.4.28-26
    PXB_BUILD_NUM = PXB_VER_FULL.split('-')[-1] # "1"
    assert re.search(r'^\d+\.\d+\.\d+-\d+$', PXB_VER_FULL), "PXB 2.4 version is not full.  Pass '2.4.28-1'" # 2.4.28-26

# Create list of supported software files
if version.parse(PXB_VER) > version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=[ 'redhat/8', 'redhat/9']
elif version.parse(PXB_VER) > version.parse("8.0.0") and version.parse(PXB_VER) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/8', 'redhat/9']
elif version.parse(PXB_VER) > version.parse("2.0.0") and version.parse(PXB_VER) < version.parse("8.0.0"):
    DEB_SOFTWARE_FILES=['stretch', 'buster', 'bullseye', 'xenial', 'bionic', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/8', 'redhat/9']

SOFTWARE_FILES=['binary','source']+DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES

RHEL_EL={'redhat/8':'8', 'redhat/9':'9'}

BASE_PATH = f"https://downloads.percona.com/downloads/Percona-XtraBackup-{MAJOR_MINOR_VERSION}/Percona-XtraBackup-{PXB_VERSION}"

def get_package_tuples():
    packages = []
    for software_file in SOFTWARE_FILES:
        if "binary" in SOFTWARE_FILES:
            glibc_versions = ["2.35"] if version.parse(PXB_VER) < version.parse("8.0.0") else ["2.28", "2.31", "2.34", "2.35"]
            for glibc_version in glibc_versions:
                for suffix in ["", "-minimal"]:
                    filename = f"percona-xtrabackup-{PXB_VER}-Linux-x86_64.glibc{glibc_version}-minimal.tar.gz"
                    packages.append(("binary", filename, f"{BASE_PATH}/binary/tarball/{filename}"))
        # Check source tarballs
        if "source" in SOFTWARE_FILES:
            for filename in [
                f"percona-xtrabackup-{PXB_VER}.tar.gz" 
            ]:
                packages.append(("source", filename, f"{BASE_PATH}/source/tarball/{filename}"))

        # Test packages for every OS
        for software_file in DEB_SOFTWARE_FILES:
            pxb_deb_name_suffix= f"{MAJOR_VERSION}_{PXB_VER}-{PXB_BUILD_NUM}.{software_file}_amd64.deb"
            deb_file= [
                f"percona-xtrabackup-{pxb_deb_name_suffix}",
                f"percona-xtrabackup-dbg-{pxb_deb_name_suffix}",
                f"percona-xtrabackup-test-{pxb_deb_name_suffix}" ]
            for file in deb_file:
                packages.append((software_file, file, f"{BASE_PATH}/binary/debian/{software_file}/x86_64/{file}"))
                

        for software_file in RHEL_SOFTWARE_FILES:
            el = RHEL_EL[software_file]
            if version.parse(PXB_VER) > version.parse("8.0.0"):
                pxb_rpm_name_suffix= f"-{PXB_VER}.{PXB_BUILD_NUM}.el{el}.x86_64.rpm"
            elif version.parse(PXB_VER) > version.parse("2.0.0") and version.parse(PXB_VER) < version.parse("8.0.0"):
                pxb_rpm_name_suffix= f"-{PXB_VER}-{PXB_BUILD_NUM}.el{el}.x86_64.rpm"
            rhel_file=[
                f"percona-xtrabackup-{MAJOR_VERSION}{pxb_rpm_name_suffix}",
                f"percona-xtrabackup-{MAJOR_VERSION}-debuginfo{pxb_rpm_name_suffix}",
                f"percona-xtrabackup-test-{MAJOR_VERSION}{pxb_rpm_name_suffix}"]
            for file in rhel_file:
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
