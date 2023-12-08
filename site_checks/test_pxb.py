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
PXB_VER_UPSTREAM = PXB_VER_FULL.split('-')[0] # 8.0.34 OR 8.1.0 OR 2.4.28
MAJOR_VERSION=''.join(PXB_VER_FULL.split('.')[:2]) # 80

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
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'bionic', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PXB_VER) > version.parse("8.0.0") and version.parse(PXB_VER) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PXB_VER) > version.parse("2.0.0") and version.parse(PXB_VER) < version.parse("8.0.0"):
    DEB_SOFTWARE_FILES=['stretch', 'buster', 'bullseye', 'xenial', 'bionic', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']

SOFTWARE_FILES=['binary','source']+DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES

RHEL_EL={'redhat/7':'el7', 'redhat/8':'el8', 'redhat/9':'el9'}

def get_package_tuples():
    list = []
    for software_file in SOFTWARE_FILES:
        data = 'version_files=Percona-XtraBackup-' + PXB_VER + '&software_files=' + software_file
        req = requests.post("https://www.percona.com/products-api.php",data=data,headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
        assert req.status_code == 200
        assert req.text != '[]', software_file
        # Check binary tarballs
        if software_file == 'binary':
            glibc_version="2.17"
            assert "percona-xtrabackup-" + PXB_VER+ "-Linux-x86_64.glibc" + glibc_version + "-minimal.tar.gz" in req.text
            assert "percona-xtrabackup-" + PXB_VER+ "-Linux-x86_64.glibc" + glibc_version + ".tar.gz" in req.text
        # Check source tarballs
        elif software_file == 'source':
            assert "percona-xtrabackup-" + PXB_VER + ".tar.gz" in req.text
            assert "percona-xtrabackup-" + MAJOR_VERSION + '_' + PXB_VER  + ".orig.tar.gz" in req.text
            if version.parse(PXB_VER) > version.parse("8.0.0"):
                assert "percona-xtrabackup-" + MAJOR_VERSION + '-' + PXB_VER + '.' + PXB_BUILD_NUM +".generic.src.rpm" in req.text
            elif version.parse(PXB_VER) > version.parse("2.0.0") and version.parse(PXB_VER) < version.parse("8.0.0"):
                assert "percona-xtrabackup-" + MAJOR_VERSION + '-' + PXB_VER + '-' + PXB_BUILD_NUM +".generic.src.rpm"
        # Test packages for every OS
        else:
            if software_file in DEB_SOFTWARE_FILES:
                pxb_deb_name_suffix=MAJOR_VERSION + '_' + PXB_VER + "-" + PXB_BUILD_NUM + "." + software_file + "_amd64.deb"
                assert "percona-xtrabackup-" + pxb_deb_name_suffix in req.text
                assert "percona-xtrabackup-dbg-" + pxb_deb_name_suffix in req.text
                assert "percona-xtrabackup-test-" + pxb_deb_name_suffix in req.text
            elif software_file in RHEL_SOFTWARE_FILES:
                if version.parse(PXB_VER) > version.parse("8.0.0"):
                    pxb_rpm_name_suffix='-' + PXB_VER + "." + PXB_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                elif version.parse(PXB_VER) > version.parse("2.0.0") and version.parse(PXB_VER) < version.parse("8.0.0"):
                    pxb_rpm_name_suffix='-' + PXB_VER + "-" + PXB_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                assert "percona-xtrabackup-" + MAJOR_VERSION + pxb_rpm_name_suffix in req.text
                assert "percona-xtrabackup-" + MAJOR_VERSION + '-debuginfo' + pxb_rpm_name_suffix in req.text
                assert "percona-xtrabackup-test-" + MAJOR_VERSION + pxb_rpm_name_suffix in req.text

        files = json.loads(req.text)
        for file in files:
            list.append( (software_file,file['filename'],file['link']) )
    return list


LIST_OF_PACKAGES = get_package_tuples()

# Check that every link from website is working (200 reply and has some content-length)
@pytest.mark.parametrize(('software_file','filename','link'),LIST_OF_PACKAGES)
def test_packages_site(software_file,filename,link):
    print('\nTesting ' + software_file + ', file: ' + filename)
    print(link)
    req = requests.head(link)
    assert req.status_code == 200 and int(req.headers['content-length']) > 0, link
