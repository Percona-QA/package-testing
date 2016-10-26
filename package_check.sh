#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps55, ps56 or ps57 !"
  echo "Usage: ./package_check.sh <prod>"
  exit 1
fi

SCRIPT_PWD=$(cd `dirname $0` && pwd)

source ${SCRIPT_PWD}/VERSIONS

if [ $1 = "ps55" ]; then
  version=${PS55_VER}
  release=${PS55_VER#*-}
  revision=${PS55_REV}
elif [ $1 = "ps56" ]; then
  version=${PS56_VER}
  release=${PS56_VER#*-}
  revision=${PS56_REV}
elif [ $1 = "ps57" ]; then
  version=${PS57_VER}
  release=${PS57_VER#*-}
  revision=${PS57_REV}
elif [ $1 = "pxc56" ]; then
  version=${PXC56_VER}
  release=${PXC56_VER#*-}
  revision=${PXC56_REV}
elif [ $1 = "pxc57" ]; then
  version=${PXC57_VER}
  release=${PXC57_VER#*-}
  revision=${PXC57_REV}
elif [ $1 = "pt" ]; then
  version=${PT_VER}
elif [ $1 = "pxb23" ]; then
  version=${PXB23_VER}
  pkg_version=${PXB23_PKG_VER}
elif [ $1 = "pxb24" ]; then
  version=${PXB24_VER}
  pkg_version=${PXB24_PKG_VER}
elif [ $1 = "psmdb30" ]; then
  version=${PSMDB30_VER}
elif [ $1 = "psmdb32" ]; then
  version=${PSMDB32_VER}
elif [ $1 = "pmm" ]; then
  version=${PMM_VER}
else
  echo "Illegal product selected!"
  exit 1
fi

product=$1
log="/tmp/${product}_package_check.log"
echo -n > $log

if [ ${product} = "ps55" -o ${product} = "ps56" -o ${product} = "ps57" ]; then
  if [ -f /etc/redhat-release ]; then
    centos_maj_version=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n 1)
    rpm_maj_version=$(echo ${product} | sed 's/^[a-z]*//') # 56
    if [ ${product} = "ps57" ]; then
      rpm_version="${version}" # 5.7.14-8
    else
      rpm_version=$(echo ${version} | sed 's/-/-rel/') # 5.6.32-rel78.0
    fi
    if [ ${product} = "ps55" ]; then
      rpm_num_pkgs="6"
      rpm_opt_package=""
    elif [ ${product} = "ps56" ]; then
      rpm_opt_package="Percona-Server-tokudb-${rpm_maj_version}"
      rpm_num_pkgs="7"
    elif [ ${product} = "ps57" ]; then
      if [ ${centos_maj_version} == "7" ]; then
        rpm_num_pkgs="8"
        rpm_opt_package="Percona-Server-tokudb-${rpm_maj_version} Percona-Server-shared-compat-${rpm_maj_version}"
      else
        rpm_num_pkgs="7"
        rpm_opt_package="Percona-Server-tokudb-${rpm_maj_version}"
      fi
    fi
    if [ "$(rpm -qa | grep Percona-Server | grep -c ${version})" == "${rpm_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in Percona-Server-server-${rpm_maj_version} Percona-Server-test-${rpm_maj_version} Percona-Server-${rpm_maj_version}-debuginfo Percona-Server-devel-${rpm_maj_version} Percona-Server-shared-${rpm_maj_version} Percona-Server-client-${rpm_maj_version} ${rpm_opt_package}; do
        if [ "$(rpm -qa | grep -c ${package}-${rpm_version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${rpm_version} is not installed"
          exit 1
        fi
      done
    fi
  else
    deb_maj_version=$(echo ${product} | sed 's/^[a-z]*//' | sed 's/./&\./') # 5.6
    if [ ${product} = "ps55" ]; then
      deb_opt_package=""
      deb_num_pkgs="6"
    else
      deb_opt_package="percona-server-tokudb-${deb_maj_version}"
      deb_num_pkgs="7"
    fi
    if [ "$(dpkg -l | grep percona-server | grep -c ${version})" == "${deb_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in percona-server-server-${deb_maj_version} percona-server-client-${deb_maj_version} percona-server-test-${deb_maj_version} percona-server-${deb_maj_version}-dbg percona-server-source-${deb_maj_version} percona-server-common-${deb_maj_version} ${deb_opt_package}; do
	      deb_version="$(dpkg -l | grep ${package} | awk '{print $3}')"
        if [ "$(dpkg -l | grep ${package} | grep -c ${version})" != 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed"
        else
          echo "WARNING: ${package} is not installed"
          exit 1
        fi
      done
    fi
  fi

elif [ ${product} = "pxc56" -o ${product} = "pxc57" ]; then
  if [ -f /etc/redhat-release ]; then
    centos_maj_version=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n 1)
    rpm_maj_version=$(echo ${product} | sed 's/^[a-z]*//') # 56

    if [ ${product} = "pxc56" ]; then
      rpm_opt_package=""
      rpm_num_pkgs="11"
    elif [ ${product} = "pxc57" ]; then
      if [ ${centos_maj_version} == "7" ]; then
        rpm_num_pkgs="10"
        rpm_opt_package="Percona-XtraDB-Cluster-shared-compat-${rpm_maj_version}"
      else
        rpm_num_pkgs="9"
        rpm_opt_package=""
      fi
    fi
    if [ "$(rpm -qa | grep Percona-XtraDB-Cluster | grep -c ${version})" == "${rpm_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in Percona-XtraDB-Cluster-${rpm_maj_version} Percona-XtraDB-Cluster-server-${rpm_maj_version} Percona-XtraDB-Cluster-test-${rpm_maj_version} Percona-XtraDB-Cluster-${rpm_maj_version}-debuginfo Percona-XtraDB-Cluster-devel-${rpm_maj_version} Percona-XtraDB-Cluster-shared-${rpm_maj_version} Percona-XtraDB-Cluster-client-${rpm_maj_version} Percona-XtraDB-Cluster-full-${rpm_maj_version} Percona-XtraDB-Cluster-garbd-${rpm_maj_version} ${rpm_opt_package}; do
        if [ "$(rpm -qa | grep -c ${package}-${version}-${release})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version}-${release} is not installed"
          exit 1
        fi
      done
    fi
  else
    deb_maj_version=$(echo ${product} | sed 's/^[a-z]*//' | sed 's/./&\./') # 5.6
    deb_opt_package=""
    deb_num_pkgs="9"
    if [ "$(dpkg -l | grep percona-xtradb-cluster | grep -c ${version})" == "${deb_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in percona-xtradb-cluster-${deb_maj_version} percona-xtradb-cluster-full-${deb_maj_version} percona-xtradb-cluster-debug-${deb_maj_version} percona-xtradb-cluster-server-${deb_maj_version} percona-xtradb-cluster-client-${deb_maj_version} percona-xtradb-cluster-test-${deb_maj_version} percona-xtradb-cluster-${deb_maj_version}-dbg percona-xtradb-cluster-source-${deb_maj_version} percona-xtradb-cluster-common-${deb_maj_version}; do
	      deb_version="$(dpkg -l | grep ${package} | awk '{print $3}')"
        if [ "$(dpkg -l | grep ${package} | grep -c ${version}-${release})" != 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed"
        else
          echo "WARNING: ${package} is not installed"
          exit 1
        fi
      done
    fi
  fi

elif [ ${product} = "pt" ]; then
  echo "Package check for PT is not implemented!"
  exit 1

elif [ ${product} = "pmm" ]; then
  echo "Package check for PMM is not implemented!"
  exit 1

elif [ ${product} = "pxb23" -o ${product} = "pxb24" ]; then
  if [ ${product} = "pxb24" ]; then
    extra_version="-24"
  else
    extra_version=""
  fi
  if [ -f /etc/redhat-release ]; then
    if [ "$(rpm -qa | grep percona-xtrabackup | grep -c ${version}-${pkg_version})" == "3" ]; then
      echo "all packages are installed"
    else
      for package in percona-xtrabackup${extra_version} percona-xtrabackup-test${extra_version} percona-xtrabackup${extra_version}-debuginfo; do
        if [ "$(rpm -qa | grep -c ${package}-${version}-${pkg_version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version}-${pkg_version} is not installed"
          exit 1
        fi
      done
    fi
  else
    if [ "$(dpkg -l | grep percona-xtrabackup | grep -c ${version}-${pkg_version})" == "3" ]; then
      echo "all packages are installed"
    else
      for package in percona-xtrabackup-dbg${extra_version} percona-xtrabackup-test${extra_version} percona-xtrabackup${extra_version}; do
        if [ "$(dpkg -l | grep -c ${package})" -gt 0 ] && [ "$dpkg -l | grep ${package} | awk '{$print $3}' == ${version}-${pkg_version}.$(lsb_release -sc)" ] ; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version}-${pkg_version} is not installed"
          exit 1
        fi
      done
    fi
  fi

elif [ ${product} = "psmdb30" -o ${product} = "psmdb32" ]; then
  rpm_num_pkgs="6"
  deb_num_pkgs="6"
  if [ ${product} = "psmdb32" ]; then
    extra_version="-32"
  else
    extra_version=""
  fi
  if [ -f /etc/redhat-release ]; then
    if [ "$(rpm -qa | grep Percona-Server-MongoDB | grep -c ${version})" == "${rpm_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in Percona-Server-MongoDB${extra_version}-debuginfo Percona-Server-MongoDB${extra_version} Percona-Server-MongoDB${extra_version}-mongos Percona-Server-MongoDB${extra_version}-server Percona-Server-MongoDB${extra_version}-shell Percona-Server-MongoDB${extra_version}-tools; do
        if [ "$(rpm -qa | grep -c ${package}-${version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version} is not installed"
          exit 1
        fi
      done
    fi
  else
    if [ "$(dpkg -l | grep percona-server-mongodb | grep -c ${version})" == "${deb_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in percona-server-mongodb${extra_version} percona-server-mongodb${extra_version}-dbg percona-server-mongodb${extra_version}-mongos percona-server-mongodb${extra_version}-server percona-server-mongodb${extra_version}-shell percona-server-mongodb${extra_version}-tools; do
        if [ "$(dpkg -l | grep ${package} | grep -c ${version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version} is not installed"
          exit 1
        fi
      done
    fi
  fi

fi

echo "${product} installed package versions are OK"
