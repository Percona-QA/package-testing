#!/bin/bash
if [ "$#" -ne 3 ]; then
  echo "This script requires the product parameter: pxb24/pxb80/pxb81 main/testing normal/minimal!"
  echo "Usage: $0 <product> <repo> <binary type>"
  exit 1
fi

SCRIPT_PWD=$(cd `dirname $0` && pwd)
log="/tmp/binary_check.log"
>${log}

version=${PXB_VERSION}
major_version="${version%%-*}"
minor_version="${version##*-}"
echo "Downloading ${1} latest version..." >> "${log}"
if [ "$3" = "normal" ]; then
   wget https://downloads.percona.com/downloads/TESTING/issue-PKG56/percona-xtrabackup-${major_version}-${minor_version}-Linux-x86_64.glibc2.28.tar.gz
   tarball_dir="percona-xtrabackup-${major_version}-${minor_version}-Linux-x86_64.glibc2.28"
else
   # Download minimal version
   wget https://downloads.percona.com/downloads/TESTING/issue-PKG56/percona-xtrabackup-${major_version}-${minor_version}-Linux-x86_64.glibc2.28-minimal.tar.gz
   tarball_dir="percona-xtrabackup-${major_version}-${minor_version}-Linux-x86_64.glibc2.28-minimal"
fi

echo "Extracting binary" >> "${log}"
tar -xf ${tarball_dir}.tar.gz
mv ${tarball_dir} pxb80
tarball_dir=pxb80

exec_files="xbcloud xbcrypt xbstream xtrabackup"
