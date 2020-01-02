#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "This script requires the product parameter: pxb24, pxb80!"
  echo "Usage: ./$0 <product>"
  exit 1
fi

SCRIPT_PWD=$(cd `dirname $0` && pwd)
#SCRIPT_PWD="$HOME/package-testing"
log="/tmp/binary_check.log"
>${log}

source ${SCRIPT_PWD}/VERSIONS

if [ $1 = "pxb80" ]; then
    product=pxb80
    version=${PXB80_VER}
    major_version=$(echo ${version}| cut -f1-2 -d.)
    minor_version=$(echo ${version}|cut -f3 -d.)
    if [ -f /etc/redhat-release ]; then
        centos_version=$(cat /etc/redhat-release | grep -o "[0-9]" | head -n 1)
        if [ "${centos_version}" -gt 7 ]; then
            lib="libgcrypt183"
        elif [ "${centos_version}" -eq 7 ]; then
            lib="libgcrypt153"
        else
            lib="libgcrypt145" # for centos version 6
        fi
    else
        lib="libgcrypt20" # for debian/ubuntu
    fi
    echo "Downloading ${1} latest version..." >> "${log}"
    wget https://www.percona.com/downloads/Percona-XtraBackup-LATEST/Percona-XtraBackup-${major_version}-${minor_version}/binary/tarball/percona-xtrabackup-${version}-Linux-x86_64.${lib}.tar.gz
    tarball_dir="percona-xtrabackup-${version}-Linux-x86_64"

    echo "Extracting binary" >> "${log}"
    tar -xf percona-xtrabackup-${version}-Linux-x86_64.${lib}.tar.gz
    mv ${tarball_dir} ${product}
    tarball_dir=${product}

    exec_files="xbcloud xbcrypt xbstream xtrabackup"

elif [ $1 = "pxb24" ]; then
    product=pxb24
    version=${PXB24_VER}
    if [ -f /etc/redhat-release ]; then
        centos_version=$(cat /etc/redhat-release | grep -o "[0-9]" | head -n 1)
        if [ "${centos_version}" -gt 7 ]; then
            lib="libgcrypt183"
        elif [ "${centos_version}" -eq 7 ]; then
            lib="libgcrypt153"
        else
            lib="libgcrypt145" # for centos version 6
        fi
    else
        lib="libgcrypt20" # for debian/ubuntu
    fi

    echo "Downloading ${1} latest version..." >> "${log}"
    wget https://www.percona.com/downloads/Percona-XtraBackup-2.4/Percona-XtraBackup-${version}/binary/tarball/percona-xtrabackup-${version}-Linux-x86_64.${lib}.tar.gz
    tarball_dir="percona-xtrabackup-${version}-Linux-x86_64"

    echo "Extracting binary" >> "${log}"
    tar -xf percona-xtrabackup-${version}-Linux-x86_64.${lib}.tar.gz
    mv ${tarball_dir} ${product}
    tarball_dir=${product}

    exec_files="xbcloud xbcrypt xbstream xtrabackup innobackupex"

else
  echo "Incorrect product selected!"
  exit 1
fi

echo "Check symlinks for all executables" >> "${log}"
for binary in $exec_files; do
    echo "Check ${tarball_dir}/bin/${binary}" >> "${log}"
    ldd ${tarball_dir}/bin/${binary} | grep "not found"
    if [ "$?" -eq 0 ]; then
        echo "Err: Binary $binary in version ${version} has an incorrect linked library"
        exit 1
    else
        echo "Binary $binary check passed" >> "${log}"
    fi
done

echo "Check version for binaries in tarball: ${product}" >> "${log}"
if [ ${product} = "pxb23" -o ${product} = "pxb24" -o ${product} = "pxb80" ]; then
  version_check=$(${tarball_dir}/bin/xtrabackup --version 2>&1|grep -c ${version})
    if [ ${version_check} -eq 0 ]; then
      echo "xtrabackup version is incorrect! Expected version: ${version}"
      exit 1
    else
      echo "xtrabackup version is correctly displayed as: ${version}" >> "${log}"
    fi

    if [ ${product} = "pxb80" ]; then
        for i in xbstream xbcloud xbcrypt; do
            version_check=$(${tarball_dir}/bin/$i --help | grep -c "${version}")
            if [ "${version_check}" -eq 0 ]; then
                echo "${i} version is incorrect! Expected version: ${version}"
                exit 1
            else
                echo "${i} version is correctly displayed as: ${version}" >> "${log}"
            fi
        done
    fi
fi
