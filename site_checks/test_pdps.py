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

# PXB
PXB_VER = '.'.join(PXB_VER_FULL.split('.')[:-1]) # 8.0.34-29
PXB_MAJOR_VERSION=''.join(PXB_VER_FULL.split('.')[:2]) # 80
PXB_BUILD_NUM = PXB_VER_FULL.split('.')[-1] # 1

# ORCH
ORCH_VER = ORCH_VER_FULL.split('-')[0]

# Create list of supported software files
if version.parse(PS_VER) > version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PS_VER) > version.parse("8.0.0") and version.parse(PS_VER) < version.parse("8.1.0"):
    DEB_SOFTWARE_FILES=['buster', 'bullseye', 'bookworm', 'bionic', 'focal', 'jammy']
    RHEL_SOFTWARE_FILES=['redhat/7', 'redhat/8', 'redhat/9']
elif version.parse(PS_VER) > version.parse("5.7.0") and version.parse(PS_VER) < version.parse("8.0.0"):
    assert not version.parse(PS_VER) > version.parse("5.7.0") and version.parse(PS_VER) < version.parse("8.0.0"), "PS 5.7 is not suported"

SOFTWARE_FILES=DEB_SOFTWARE_FILES+RHEL_SOFTWARE_FILES+['binary','source']

RHEL_EL={'redhat/7':'el7', 'redhat/8':'el8', 'redhat/9':'el9'}

def get_package_tuples():
    list = []
    for software_file in SOFTWARE_FILES:
        data = 'version_files=percona-distribution-mysql-ps-' + PS_VER_UPSTREAM + '&software_files=' + software_file
        req = requests.post("https://www.percona.com/products-api.php",data=data,headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"})
        assert req.status_code == 200
        assert req.text != '[]', software_file
        # Test binary tarballs
        if software_file == 'binary':
            glibc_versions=["2.17","2.27","2.28","2.31","2.34","2.35"]
            for glibc_version in glibc_versions:
                # Check PS tarballs:
                assert "Percona-Server-" + PS_VER + "-Linux.x86_64.glibc"+glibc_version+"-minimal.tar.gz" in req.text
                assert "Percona-Server-" + PS_VER + "-Linux.x86_64.glibc"+glibc_version+".tar.gz" in req.text
                if glibc_version in ['2.34', '2.35'] and version.parse(PS_VER) > version.parse("8.0.0") and version.parse(PS_VER) < version.parse("8.1.0"):
                    assert "Percona-Server-" + PS_VER + "-Linux.x86_64.glibc"+glibc_version+"-zenfs-minimal.tar.gz" in req.text
                    assert "Percona-Server-" + PS_VER + "-Linux.x86_64.glibc"+glibc_version+"-zenfs.tar.gz" in req.text
                # Check mysql-shell tarballs:
                if glibc_version not in ['2.35']:
                    assert "percona-mysql-shell-" + PS_VER_UPSTREAM + "-linux-glibc"+glibc_version+".tar.gz" in req.text
            # Check PT
            assert 'percona-toolkit' + PT_VER + '_x86_64.tar.gz'
            # Check PXB
            glibc_version="2.17"
            assert "percona-xtrabackup-" + PXB_VER+ "-Linux-x86_64.glibc" + glibc_version + "-minimal.tar.gz" in req.text
            assert "percona-xtrabackup-" + PXB_VER+ "-Linux-x86_64.glibc" + glibc_version + ".tar.gz" in req.text
            # Check ProxySQL
            glibc_versions=["2.17","2.23","2.27"]
            for glibc_version in glibc_versions:
                assert 'proxysql-' + PROXYSQL_VER + '-Linux-x86_64.glibc2.17.tar.gz' in req.text
        # Test source tarballs
        elif software_file == 'source':
            # Check PS sources:
            assert "percona-server-" + PS_VER + ".tar.gz" in req.text
            assert "percona-server_" + PS_VER  + ".orig.tar.gz" in req.text
            assert "percona-server-" + PS_VER_FULL  + ".generic.src.rpm" in req.text
            # Check mysql-shell sources:
            assert re.search(rf'percona-mysql-shell_{PS_VER_UPSTREAM}-\d+\.orig\.tar\.gz', req.text)
            assert re.search(rf'percona-mysql-shell-{PS_VER_UPSTREAM}-\d+\.generic\.src\.rpm', req.text)
            assert "percona-mysql-shell-" + PS_VER_UPSTREAM + ".tar.gz" in req.text
            # Check orchestrator sources:
            assert "percona-orchestrator-" + ORCH_VER + ".tar.gz" in req.text
            assert "percona-orchestrator-" + ORCH_VER_FULL + ".generic.src.rpm" in req.text
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
        # Test packages for every OS
        else:
            if software_file in DEB_SOFTWARE_FILES:
                # Check PS deb packages:
                ps_deb_name_suffix=PS_VER + "-" + PS_BUILD_NUM + "." + software_file + "_amd64.deb"
                assert "percona-server-server_" + ps_deb_name_suffix in req.text
                assert "percona-server-test_" + ps_deb_name_suffix in req.text
                assert "percona-server-client_" + ps_deb_name_suffix in req.text
                assert "percona-server-rocksdb_" + ps_deb_name_suffix in req.text
                assert "percona-mysql-router_" + ps_deb_name_suffix in req.text
                assert "libperconaserverclient21-dev_" + ps_deb_name_suffix in req.text or "libperconaserverclient22-dev_" + ps_deb_name_suffix in req.text
                assert "libperconaserverclient21_" + ps_deb_name_suffix in req.text or "libperconaserverclient22_" + ps_deb_name_suffix in req.text
                assert "percona-server-source_" + ps_deb_name_suffix in req.text
                assert "percona-server-common_" + ps_deb_name_suffix in req.text
                assert "percona-server-dbg_" + ps_deb_name_suffix in req.text
                # Check mysql-shell deb packages:
                assert "percona-mysql-shell_" + PS_VER_UPSTREAM in req.text
                # Check orchestrator deb packages:
                assert "percona-orchestrator-client_" + ORCH_VER in req.text
                assert "percona-orchestrator-cli_" + ORCH_VER in req.text
                assert "percona-orchestrator_" + ORCH_VER in req.text
                # Check PT deb packages:
                assert "percona-toolkit_" + PT_VER in req.text
                # Check PXB deb packages:
                pxb_deb_name_suffix=PXB_MAJOR_VERSION + '_' + PXB_VER + "-" + PXB_BUILD_NUM + "." + software_file + "_amd64.deb"
                assert "percona-xtrabackup-" + pxb_deb_name_suffix in req.text
                assert "percona-xtrabackup-dbg-" + pxb_deb_name_suffix in req.text
                assert "percona-xtrabackup-test-" + pxb_deb_name_suffix in req.text
                # Check proxysql deb packages:
                assert "proxysql2_" + PROXYSQL_VER in req.text
            if software_file in RHEL_SOFTWARE_FILES:
                # Check PS rpm packages:
                ps_rpm_name_suffix=PS_VER + "." + PS_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                assert "percona-server-server-" + ps_rpm_name_suffix in req.text
                assert "percona-server-test-" + ps_rpm_name_suffix in req.text
                assert "percona-server-client-" + ps_rpm_name_suffix in req.text
                assert "percona-server-rocksdb-" + ps_rpm_name_suffix in req.text
                assert "percona-mysql-router-" + ps_rpm_name_suffix in req.text
                assert "percona-server-devel-" + ps_rpm_name_suffix in req.text
                assert "percona-server-shared-" + ps_rpm_name_suffix in req.text
                assert "percona-icu-data-files-" + ps_rpm_name_suffix in req.text
                if software_file != "redhat/9":
                    assert "percona-server-shared-compat-" + ps_rpm_name_suffix in req.text
                assert "percona-server-debuginfo-" + ps_rpm_name_suffix in req.text
                # Check mysql rpm packages:
                assert 'percona-mysql-shell-' + PS_VER_UPSTREAM in req.text
                # Check orchestrator rpm packages:
                assert 'percona-orchestrator-' + ORCH_VER in req.text
                assert 'percona-orchestrator-cli-' + ORCH_VER in req.text
                assert 'percona-orchestrator-client-' + ORCH_VER in req.text
                # Check PT rpm packages:
                assert 'percona-toolkit-' + PT_VER in req.text
                # Check PXB rpm packages:
                pxb_rpm_name_suffix='-' + PXB_VER + "." + PXB_BUILD_NUM + "." + RHEL_EL[software_file] + ".x86_64.rpm"
                assert "percona-xtrabackup-" + PXB_MAJOR_VERSION + pxb_rpm_name_suffix in req.text
                assert "percona-xtrabackup-" + PXB_MAJOR_VERSION + '-debuginfo' + pxb_rpm_name_suffix in req.text
                assert "percona-xtrabackup-test-" + PXB_MAJOR_VERSION + pxb_rpm_name_suffix in req.text
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
    req = requests.head(link, allow_redirects=True)
    assert req.status_code == 200 and int(req.headers['content-length']) > 0, link
