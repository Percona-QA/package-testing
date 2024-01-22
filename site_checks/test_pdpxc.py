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
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PXC_VER_PERCONA) > version.parse("8.0.0") and version.parse(PXC_VER_PERCONA) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PXC_VER_PERCONA) > version.parse("5.7.0") and version.parse(PXC_VER_PERCONA) < version.parse("8.0.0"):
    assert not version.parse(PXC_VER_PERCONA) > version.parse("5.7.0") and version.parse(PXC_VER_PERCONA) < version.parse("8.0.0"), "PS 5.7 is not suported"

SOFTWARE_FILES=DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES+['binary','source']

RHEL_EL={'redhat/7':'el7', 'redhat/8':'el8', 'redhat/9':'el9'}

def get_package_tuples():
    list = []
    for software_file in SOFTWARE_FILES:
        data = 'version_files=percona-distribution-mysql-pxc-' + PXC_VER_UPSTREAM + '&software_files=' + software_file
        req = requests.post("https://www.percona.com/products-api.php",data=data,headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
        assert req.status_code == 200
        assert req.text != '[]', software_file
        # Test binary tarballs
        if software_file == 'binary':
            glibc_versions=["2.17","2.34", "2.35"]
            for glibc_version in glibc_versions:
                # Check PXC tarballs:
                assert "Percona-XtraDB-Cluster_" + PXC_VER_FULL + "_Linux.x86_64.glibc"+glibc_version+"-minimal.tar.gz" in req.text
                assert "Percona-XtraDB-Cluster_" + PXC_VER_FULL + "_Linux.x86_64.glibc"+glibc_version+".tar.gz" in req.text
            # Check PT
            assert 'percona-toolkit' + PT_VER + '_x86_64.tar.gz'
            # Check PXB
            glibc_version="2.17"
            assert "percona-xtrabackup-" + PXB_VER+ "-Linux-x86_64.glibc" + glibc_version + "-minimal.tar.gz" in req.text
            assert "percona-xtrabackup-" + PXB_VER+ "-Linux-x86_64.glibc" + glibc_version + ".tar.gz" in req.text
            # Check ProxySQL
            glibc_versions=["2.17","2.23"]
            for glibc_version in glibc_versions:
                assert "proxysql-" + PROXYSQL_VER + "-Linux-x86_64.glibc" + glibc_version + ".tar.gz" in req.text
        # Test source tarballs
        elif software_file == 'source':
            # Check PXC sources:
            assert "Percona-XtraDB-Cluster-" + PXC_VER_PERCONA + ".tar.gz" in req.text
            assert "percona-xtradb-cluster_" + PXC_VER_PERCONA + ".orig.tar.gz" in req.text
            assert "percona-xtradb-cluster-" + PXC_VER_FULL  + ".generic.src.rpm" in req.text
            # Check Percona Toolkit sources:
            assert "percona-toolkit-" + PT_VER + ".tar.gz" in req.text
            assert re.search(rf'percona-toolkit-{PT_VER}-\d+\.src\.rpm', req.text)
            # Check Percona XtraBackup sources:
            assert "percona-xtrabackup-" + PXB_VER + ".tar.gz" in req.text
            assert "percona-xtrabackup-" + PXB_MAJOR_VERSION + '_' + PXB_VER  + ".orig.tar.gz" in req.text
            assert "percona-xtrabackup-" + PXB_MAJOR_VERSION + '-' + PXB_VER + '.' + PXB_BUILD_NUM +".generic.src.rpm" in req.text
            # Check proxysql2 sources:
            assert "proxysql2-" + PROXYSQL_VER + ".tar.gz" in req.text
            assert "proxysql2_" + PROXYSQL_VER + ".orig.tar.gz" in req.text
            assert re.search(rf'proxysql2-{PROXYSQL_VER}-\d+\.\d+\.generic\.src\.rpm', req.text)
            # Check percona-haproxy sources:
            assert "percona-haproxy-" + HAPROXY_VER + ".tar.gz" in req.text
            assert "percona-haproxy_" + HAPROXY_VER + ".orig.tar.gz" in req.text
            assert re.search(rf'percona-haproxy-{HAPROXY_VER}-\d+\.generic\.src\.rpm', req.text)
            # Check prepl_manager sources:
            assert "percona-replication-manager-" + REPL_MAN_VER + ".tar.gz" in req.text
        else:
            if software_file in DEB_SOFTWARE_FILES:
                # Check PXC deb packages:
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
                # Check PT deb packages:
                assert "percona-toolkit_" + PT_VER in req.text
                # Check PXB deb packages:
                pxb_deb_name_suffix=PXB_MAJOR_VERSION + '_' + PXB_VER + "-" + PXB_BUILD_NUM + "." + software_file + "_amd64.deb"
                assert "percona-xtrabackup-" + pxb_deb_name_suffix in req.text
                assert "percona-xtrabackup-dbg-" + pxb_deb_name_suffix in req.text
                assert "percona-xtrabackup-test-" + pxb_deb_name_suffix in req.text
                # Check haproxy deb packages:
                assert "percona-haproxy_" + HAPROXY_VER in req.text
                assert "percona-haproxy-doc_" + HAPROXY_VER in req.text
                assert "percona-vim-haproxy_" + HAPROXY_VER in req.text
                # Check percona-replication-manager deb packages:
                assert "percona-replication-manager_" + REPL_MAN_VER in req.text
                # Check proxysql deb packages:
                assert "proxysql2_" + PROXYSQL_VER in req.text
            if software_file in RHEL_SOFTWARE_FILES:
                # Check PXC rpm packages:
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
                # Check PT rpm packages:
                assert 'percona-toolkit-' + PT_VER in req.text
                # Check PXB rpm packages:
                pxb_rpm_name_suffix='-' + PXB_VER + "." + PXB_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                assert "percona-xtrabackup-" + PXB_MAJOR_VERSION + pxb_rpm_name_suffix in req.text
                assert "percona-xtrabackup-" + PXB_MAJOR_VERSION + '-debuginfo' + pxb_rpm_name_suffix in req.text
                assert "percona-xtrabackup-test-" + PXB_MAJOR_VERSION + pxb_rpm_name_suffix in req.text
                # Check haproxy rpm packages:
                assert "percona-haproxy-" + HAPROXY_VER in req.text
                assert "percona-haproxy-debuginfo-" + HAPROXY_VER in req.text
                # Check percona-replication-manager rpm packages:
                assert "percona-replication-manager-" + REPL_MAN_VER in req.text
                # Check proxysql rpm packages:
                assert "proxysql2-" + PROXYSQL_VER in req.text
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
