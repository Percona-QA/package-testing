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

# Create list of supported software files and PXC 57 specific version numbers
if version.parse(PXC_VER_UPSTREAM) >= version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['buster','bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['buster','bullseye', 'bookworm', 'bionic','focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'bionic','focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
    # Get PXC57 specific version numbers
    PXC57_WSREP_PROV_VER = PXC_VER_FULL.split('.')[-2] # for 5.7.43-31.65.1 = 65
    assert os.environ.get("PXC57_INNODB"), "PXC57_INNODB parameter is not defined!"
    PXC57_INNODB=os.environ.get("PXC57_INNODB")


SOFTWARE_FILES=DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES+['binary','source']

RHEL_EL={'redhat/7':'el7', 'redhat/8':'el8', 'redhat/9':'el9'}

def get_package_tuples():
    list = []
    for software_file in SOFTWARE_FILES:
        data = 'version_files=Percona-XtraDB-Cluster-' + PXC_VER_UPSTREAM + '&software_files=' + software_file
        req = requests.post("https://www.percona.com/products-api.php",data=data,headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
        assert req.status_code == 200
        assert req.text != '[]', software_file
        # Check binary tarballs
        if software_file == 'binary':
            glibc_versions=["2.17","2.34", "2.35"]
            for glibc_version in glibc_versions:
                if version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0"):
                    assert "Percona-XtraDB-Cluster_" + PXC_VER_FULL + "_Linux.x86_64.glibc"+glibc_version+"-minimal.tar.gz" in req.text
                    assert "Percona-XtraDB-Cluster_" + PXC_VER_FULL + "_Linux.x86_64.glibc"+glibc_version+".tar.gz" in req.text
                elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
                    assert "Percona-XtraDB-Cluster-" + PXC_VER_UPSTREAM + "-rel" + PXC57_INNODB + "-" + PXC57_WSREP_PROV_VER + "." + PXC_BUILD_NUM + ".Linux.x86_64.glibc"+glibc_version+"-minimal.tar.gz" in req.text
                    assert "Percona-XtraDB-Cluster-" + PXC_VER_UPSTREAM + "-rel" + PXC57_INNODB + "-" + PXC57_WSREP_PROV_VER + "." + PXC_BUILD_NUM + ".Linux.x86_64.glibc"+glibc_version+".tar.gz" in req.text
        # Check source tarballs
        elif software_file == 'source':
            if version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0"):
                assert "Percona-XtraDB-Cluster-" + PXC_VER_PERCONA + ".tar.gz" in req.text
                assert "percona-xtradb-cluster_" + PXC_VER_PERCONA + ".orig.tar.gz" in req.text
                assert "percona-xtradb-cluster-" + PXC_VER_FULL  + ".generic.src.rpm" in req.text
            elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
                assert "Percona-XtraDB-Cluster-" + PXC_VER_PERCONA + ".tar.gz" in req.text
                assert "percona-xtradb-cluster-5.7_" + PXC_VER_PERCONA + ".orig.tar.gz" in req.text
                assert "Percona-XtraDB-Cluster-57-" + PXC_VER_FULL + ".generic.src.rpm" in req.text
        # Test packages for every OS
        else:
            if version.parse(PXC_VER_UPSTREAM) > version.parse("8.0.0"):
                if software_file in DEB_SOFTWARE_FILES:
                    pxc_deb_name_suffix=PXC_VER_PERCONA + "-" + PXC_BUILD_NUM + "." + software_file + "_amd64.deb"
                    assert "percona-xtradb-cluster-server_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-test_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-client_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-garbd_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-full_" + pxc_deb_name_suffix in req.text
                    assert "libperconaserverclient21-dev_" + pxc_deb_name_suffix in req.text
                    assert "libperconaserverclient21_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-source_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-common_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-dbg_" + pxc_deb_name_suffix in req.text
                if software_file in RHEL_SOFTWARE_FILES:
                    pxc_rpm_name_suffix=PXC_VER_PERCONA + "." + PXC_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                    assert "percona-xtradb-cluster-server-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-test-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-client-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-garbd-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-full-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-devel-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-shared-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-icu-data-files-" + pxc_rpm_name_suffix in req.text
                    if software_file != "redhat/9":
                        assert "percona-xtradb-cluster-shared-compat-" + pxc_rpm_name_suffix in req.text
                    assert "percona-xtradb-cluster-debuginfo-" + pxc_rpm_name_suffix in req.text
            elif version.parse(PXC_VER_UPSTREAM) > version.parse("5.7.0") and version.parse(PXC_VER_UPSTREAM) < version.parse("8.0.0"):
                assert "dbg" in req.text or "debug" in req.text
                if software_file in DEB_SOFTWARE_FILES:
                    pxc_deb_name_suffix=PXC_VER_PERCONA + "-" + PXC_BUILD_NUM + "." + software_file + "_amd64.deb"
                    assert "libperconaserverclient20-dev_" + pxc_deb_name_suffix in req.text
                    assert "libperconaserverclient20_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-source-5.7_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-common-5.7_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-57_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-server-5.7_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-test-5.7_"  + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-client-5.7_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-garbd-5.7_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-full-57_" + pxc_deb_name_suffix in req.text
                    assert "percona-xtradb-cluster-5.7-dbg_" + pxc_deb_name_suffix in req.text
                if software_file in RHEL_SOFTWARE_FILES:
                    pxc_rpm_name_suffix=PXC_VER_PERCONA + "." + PXC_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                    assert "Percona-XtraDB-Cluster-server-57-" + pxc_rpm_name_suffix in req.text
                    assert "Percona-XtraDB-Cluster-test-57-" + pxc_rpm_name_suffix in req.text
                    assert "Percona-XtraDB-Cluster-client-57-" + pxc_rpm_name_suffix in req.text
                    assert "Percona-XtraDB-Cluster-garbd-57-" + pxc_rpm_name_suffix in req.text
                    assert "Percona-XtraDB-Cluster-full-57-" + pxc_rpm_name_suffix in req.text
                    assert "Percona-XtraDB-Cluster-devel-57-" + pxc_rpm_name_suffix in req.text
                    assert "Percona-XtraDB-Cluster-shared-57-" + pxc_rpm_name_suffix in req.text
                    if software_file == "redhat/7":
                        assert "Percona-XtraDB-Cluster-shared-compat-57-" + pxc_rpm_name_suffix in req.text
                    assert "Percona-XtraDB-Cluster-57-debuginfo-" + pxc_rpm_name_suffix in req.text

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
