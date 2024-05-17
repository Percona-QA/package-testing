#!/bin/bash

set -e

if [ "$#" = 2 ]; then
  if [ $2 = "pro" ]; then
    pro_suf="-pro"
  else
    echo "Wrong second argument! It is not pro!"
    exit 1
  fi
elif [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps56, ps57, ps80, ps81 !"
  echo "Usage: ./version_check.sh <prod> [pro]"
  exit 1
fi

SCRIPT_PWD=$(cd `dirname $0` && pwd)

source ${SCRIPT_PWD}/VERSIONS

if [ $1 = "ps56" ]; then
  version=${PS56_VER}
  release=${PS56_VER#*-}
  revision=${PS56_REV}
elif [ $1 = "ps57" ]; then
  version=${PS57_VER}
  release=${PS57_VER#*-}
  revision=${PS57_REV}
elif [ $1 = "ps80" ]; then
  if [ "$2" = "pro" ]; then
    version=${PS80_PRO_VER}
    release=${PS80_PRO_VER#*-}
    revision=${PS80_PRO_REV}
  else
    version=${PS80_VER}
    release=${PS80_VER#*-}
    revision=${PS80_REV}
  fi
elif [[ $1 =~ ^ps8[1-9]{1}$ ]]; then
  version=${PS_INN_LTS_VER}
  release=${PS_INN_LTS_VER#*-}
  revision=${PS_INN_LTS_REV}  
elif [ $1 = "pxc56" ]; then
  version=${PXC56_VER}
  release=${PXC56_VER#*-}
  revision=${PXC56_REV}
elif [ $1 = "pxc57" ]; then
  version=${PXC57_VER}
  release=${PXC57_VER#*-}
  revision=${PXC57_REV}
elif [ $1 = "pxc80" ]; then
  version=${PXC80_VER}
  release=${PXC80_VER#*-}
  revision=${PXC80_REV}
elif [[ "$1" =~ ^pxc8[1-9]{1}$ ]]; then
  version=${PXC_INN_LTS_VER}
  release=${PXC_INN_LTS_VER#*-}
  revision=${PXC_INN_LTS_REV}
elif [ $1 = "pt" ]; then
  version=${PT_VER}
elif [ $1 = "pxb23" ]; then
  version=${PXB23_VER}
  pkg_version=${PXB23_PKG_VER}
elif [ $1 = "pxb24" ]; then
  version=${PXB24_VER}
  pkg_version=${PXB24_PKG_VER}
elif [ $1 = "pxb80" ]; then
  version=${PXB80_VER}
  pkg_version=${PXB80_PKG_VER}
elif [[ $1 =~ ^pxb8[1-9]{1}$ ]]; then
  version=${PXB_INN_LTS_VER}
  pkg_version=${PXB_INN_LTS_PKG_VER}
elif [ $1 = "psmdb30" ]; then
  version=${PSMDB30_VER}
elif [ $1 = "psmdb32" ]; then
  version=${PSMDB32_VER}
elif [ $1 = "psmdb34" ]; then
  version=${PSMDB34_VER}
elif [ $1 = "psmdb36" ]; then
  version=${PSMDB36_VER}
elif [ $1 = "psmdb40" ]; then
  version=${PSMDB40_VER}
elif [ $1 = "psmdb42" ]; then
  version=${PSMDB42_VER}
elif [ $1 = "psmdb44" ]; then
  version=${PSMDB44_VER}
elif [ $1 = "psmdb50" ]; then
  version=${PSMDB50_VER}
elif [ $1 = "pmm" ]; then
  version=${PMM_VER}
elif [ $1 = "pbm" ]; then
  version=${PBM_VER}
  pkg_version=${PBM_PKG_VER}
elif [ $1 = "repo" ]; then
  version=${REPO_VER}
else
  echo "Illegal product selected!"
  exit 1
fi

product=$1
log="/tmp/${product}_package_check.log"
echo -n > $log

if [[ ${product} = "ps56" || ${product} = "ps57" ]] || [[ ${product} =~ ^ps8[0-9]{1}$ ]]; then
  if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then
    if [ -f /etc/system-release -a $(grep -c Amazon /etc/system-release) -eq 1 ]; then
      centos_maj_version="7"
    else
      centos_maj_version=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n 1)
    fi
    rpm_maj_version=$(echo ${product} | sed 's/^[a-z]*//') # 56
    if [ ${product} = "ps56" ]; then
      rpm_version=$(echo ${version} | sed 's/-/-rel/') # 5.6.32-rel78.0
    else
      rpm_version="${version}" # 5.7.14-8
    fi
    if [ "${product}" = "ps56" ]; then
      rpm_opt_package="Percona-Server-tokudb-${rpm_maj_version} Percona-Server-selinux-${rpm_maj_version}"
      rpm_num_pkgs="8"
    elif [ "${product}" = "ps57" ] && [ "${ps57_tokudb}" = "no" ]; then
      if [ "${centos_maj_version}" == "7" ]; then
        rpm_num_pkgs="8"
        rpm_opt_package="Percona-Server-rocksdb-${rpm_maj_version} Percona-Server-shared-compat-${rpm_maj_version}"
      else
        rpm_num_pkgs="7"
        rpm_opt_package="Percona-Server-rocksdb-${rpm_maj_version}"
      fi
    elif [ "${product}" = "ps57" ]; then
      if [ "${centos_maj_version}" == "7" ]; then
        rpm_num_pkgs="9"
        rpm_opt_package="Percona-Server-tokudb-${rpm_maj_version} Percona-Server-rocksdb-${rpm_maj_version} Percona-Server-shared-compat-${rpm_maj_version}"
      else
        rpm_num_pkgs="8"
        rpm_opt_package="Percona-Server-tokudb-${rpm_maj_version} Percona-Server-rocksdb-${rpm_maj_version}"
      fi
    elif [[ ${product} =~ ^ps8[0-9]{1}$ ]]; then
      if [ "${centos_maj_version}" == "9" ]; then
        rpm_num_pkgs="7"
        rpm_opt_package="percona-server-rocksdb${pro_suf}"
      else
        rpm_num_pkgs="8"
        rpm_opt_package="percona-server-rocksdb percona-server-shared-compat"
      fi
    fi
    if [[ ${product} =~ ^ps8[0-9]{1}$ ]]; then
      ps_name="percona-server"
      rpm_pkgs_list="${ps_name}-server${pro_suf} ${ps_name}-test${pro_suf} ${ps_name}${pro_suf}-debuginfo ${ps_name}-devel${pro_suf} ${ps_name}-shared${pro_suf} ${ps_name}-client${pro_suf}"
    else
      ps_name="Percona-Server"
      rpm_pkgs_list="${ps_name}-server-${rpm_maj_version} ${ps_name}-test-${rpm_maj_version} ${ps_name}-${rpm_maj_version}-debuginfo ${ps_name}-devel-${rpm_maj_version} ${ps_name}-shared-${rpm_maj_version} ${ps_name}-client-${rpm_maj_version}"
    fi
    if [ "$(rpm -qa | grep "${ps_name}" | grep -c "${version}")" == "${rpm_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in ${rpm_pkgs_list} ${rpm_opt_package}; do
        if [ "$(rpm -qa | grep -c ${package}-${rpm_version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package} is not installed"
          exit 1
        fi
      done
    fi
  else
    deb_maj_version=$(echo ${product} | sed 's/^[a-z]*//' | sed 's/./&\./') # 5.6
    if [ ${product} = "ps56" ]; then
      deb_opt_package="percona-server-tokudb-${deb_maj_version}"
      deb_num_pkgs="7"
    elif [ "${product}" = "ps57" ] && [ "${ps57_tokudb}" = "no" ]; then
      deb_opt_package="percona-server-rocksdb-${deb_maj_version}"
      deb_num_pkgs="7"
    elif [ "${product}" = "ps57" ]; then
      deb_opt_package="percona-server-rocksdb-${deb_maj_version} percona-server-tokudb-${deb_maj_version}"
      deb_num_pkgs="8"
    else
      deb_opt_package="percona-server-rocksdb"
      deb_num_pkgs="7"
    fi
    if [[ ${product} =~ ^ps8[0-9]{1}$ ]]; then
      deb_dbg_pkg="percona-server${pro_suf}-dbg"
    else
      deb_dbg_pkg="percona-server-${deb_maj_version}-dbg"
    fi
    if [ "$(dpkg -l | grep percona-server | grep -c ${version})" == "${deb_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      for package in percona-server-server${pro_suf} percona-server-client${pro_suf} percona-server-test${pro_suf} ${deb_dbg_pkg} percona-server${pro_suf}-source percona-server${pro_suf}-common ${deb_opt_package}; do
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
  if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then
    if [ -f /etc/system-release -a $(grep -c Amazon /etc/system-release) -eq 1 ]; then
      centos_maj_version="7"
    else
      centos_maj_version=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n 1)
    fi  
      echo "the centos maj version is: $centos_maj_version"

    rpm_maj_version=$(echo ${product} | sed 's/^[a-z]*//') # 56

    if [ ${product} = "pxc56" ]; then
      rpm_opt_package=""
      rpm_num_pkgs="11"
	  garbd_maj_version=3
    elif [ ${product} = "pxc57" ]; then
      if [ ${centos_maj_version} == "7" ]; then
        rpm_num_pkgs="10"
        rpm_opt_package="Percona-XtraDB-Cluster-shared-compat-${rpm_maj_version}"
      else
        rpm_num_pkgs="9"
        rpm_opt_package=""
      fi      
	  garbd_maj_version=$(echo ${product} | sed 's/^[a-z]*//')
    echo "RPM Num Packages: $rpm_num_pkgs and $rpm_opt_package"
    fi

    if [ "$(rpm -qa | grep Percona-XtraDB-Cluster | grep -c ${version})" == "${rpm_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      echo "RPM QA PART"
      for package in Percona-XtraDB-Cluster-server-${rpm_maj_version} Percona-XtraDB-Cluster-test-${rpm_maj_version} Percona-XtraDB-Cluster-${rpm_maj_version}-debuginfo Percona-XtraDB-Cluster-devel-${rpm_maj_version} Percona-XtraDB-Cluster-shared-${rpm_maj_version} Percona-XtraDB-Cluster-client-${rpm_maj_version} Percona-XtraDB-Cluster-full-${rpm_maj_version} ${rpm_opt_package}; do
        if [ "$(rpm -qa | grep -c ${package}-${version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version}-${release} is not installed"
          exit 1
        fi
      done
      if [ "$(rpm -qa | grep -c Percona-XtraDB-Cluster-garbd-${garbd_maj_version})" -gt 0 ]; then
        echo "$(date +%Y%m%d%H%M%S): Percona-XtraDB-Cluster-garbd-${garbd_maj_version} is installed" >> ${log}
      else
        echo "WARNING: Percona-XtraDB-Cluster-garbd-${garbd_maj_version} is not installed"
        exit 1
      fi
    fi

  else
    deb_maj_version=$(echo ${product} | sed 's/^[a-z]*//' | sed 's/./&\./') # 5.6
    deb_maj_version_nodot=$(echo ${product} | sed 's/^[a-z]*//') # 56
    deb_opt_package=""
    deb_num_pkgs="10"
    echo "IN DPKG PART"
    if [ "$(dpkg -l | grep percona-xtradb-cluster | grep -c ${version})" == "${deb_num_pkgs}" ]; then
      echo "all packages are installed"
    else
      # -full and -garbd packages are missing from check currently because they are not installed in all configs
      for package in percona-xtradb-cluster-full-${deb_maj_version_nodot} percona-xtradb-cluster-server-debug-${deb_maj_version} percona-xtradb-cluster-server-${deb_maj_version} percona-xtradb-cluster-client-${deb_maj_version} percona-xtradb-cluster-test-${deb_maj_version} percona-xtradb-cluster-${deb_maj_version}-dbg percona-xtradb-cluster-common-${deb_maj_version}; do
        if [ "$(dpkg -l | grep ${package} | grep -c ${version})" != 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed"
        else
          echo "WARNING: ${package} is not installed"
          exit 1
        fi
      done
    fi
  fi

elif [[ ${product} =~ ^pxc8[1-9]{1}$ ]]; then
  echo "Package check for PXC-8x is not implemented!"
  exit 0

elif [ ${product} = "pt" ]; then
  echo "Package check for PT is not implemented!"
  exit 1

elif [ ${product} = "pmm" ]; then
  echo "Package check for PMM is not implemented!"
  exit 1

elif [ ${product} = "pxb23" -o ${product} = "pxb24" -o ${product} = "pxb80" ]; then
  if [ ${product} = "pxb24" ]; then
    extra_version="-24"
  elif [ ${product} = "pxb80" ]; then
    extra_version="-80"
  else
    extra_version=""
  fi
  if [ -f /etc/redhat-release ] || [ -f /etc/system-release ] ; then
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

elif [ "${product}" = "psmdb30" -o "${product}" = "psmdb32" -o "${product}" = "psmdb34" -o "${product}" = "psmdb36" -o "${product}" = "psmdb40" ]; then
  centos_maj_version=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -n 1)
  if [ "${centos_maj_version}" == "6" -o "${centos_maj_version}" == "7" ]; then
    rpm_num_pkgs="6"
  else
    rpm_num_pkgs="10"
  fi
  deb_num_pkgs="6"
  if [ ${product} = "psmdb32" ]; then
    extra_version="-32"
  elif [ ${product} = "psmdb34" ]; then
    extra_version="-34"
  elif [ ${product} = "psmdb36" ]; then
    extra_version="-36"
  else
    extra_version=""
  fi
  SLES=0
  if [ -f /etc/os-release ]; then
    SLES=$(cat /etc/os-release | grep -c '^NAME=\"SLES' || true)
  fi
  if [ -f /etc/redhat-release -o ${SLES} -eq 1 ]; then
    if [ "$(rpm -qa | grep -i Percona-Server-MongoDB | grep -c ${version})" == "${rpm_num_pkgs}" ]; then
      echo "all packages are installed"
    elif [ ${SLES} -eq 1 ]; then
      for package in Percona-Server-MongoDB${extra_version}-debugsource Percona-Server-MongoDB${extra_version}-mongos-debuginfo Percona-Server-MongoDB${extra_version}-server-debuginfo Percona-Server-MongoDB${extra_version}-shell-debuginfo Percona-Server-MongoDB${extra_version}-tools-debuginfo Percona-Server-MongoDB${extra_version} Percona-Server-MongoDB${extra_version}-mongos Percona-Server-MongoDB${extra_version}-server Percona-Server-MongoDB${extra_version}-shell Percona-Server-MongoDB${extra_version}-tools; do
        if [ "$(rpm -qa | grep -c ${package}-${version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version} is not installed"
          exit 1
        fi
      done
    else
      if [ "${product}" = "psmdb40" -o "${product}" = "psmdb42" -o "${product}" = "psmdb44" ]; then
        psmdb_name="percona-server-mongodb"
      else
        psmdb_name=""
      fi
      if [ "${centos_maj_version}" == "6" -o "${centos_maj_version}" == "7" ]; then
        debuginfo_packages="${psmdb_name}${extra_version}-debuginfo"
      else
        debuginfo_packages="${psmdb_name}-mongos-debuginfo ${psmdb_name}-server-debuginfo ${psmdb_name}-shell-debuginfo ${psmdb_name}-tools-debuginfo ${psmdb_name}-debugsource"
      fi
      for package in ${debuginfo_packages} ${psmdb_name}${extra_version} ${psmdb_name}${extra_version}-mongos ${psmdb_name}${extra_version}-server ${psmdb_name}${extra_version}-shell ${psmdb_name}${extra_version}-tools; do
        if [ "$(rpm -qa | grep -c "${package}"-"${version}")" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): '${package}' is installed" >> "${log}"
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

elif [ "${product}" == "pbm" ]; then
  if [ -f /etc/redhat-release ]; then
    if [ "$(rpm -qa | grep percona-backup-mongodb | grep -c ${version}-${pkg_version})" == "3" ]; then
      echo "all packages are installed"
    else
      for package in percona-backup-mongodb-coordinator percona-backup-mongodb-agent percona-backup-mongodb-pbmctl; do
        if [ "$(rpm -qa | grep -c ${package}-${version}-${pkg_version})" -gt 0 ]; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version}-${pkg_version} is not installed"
          exit 1
        fi
      done
    fi
  else
    if [ "$(dpkg -l | grep percona-backup-mongodb | grep -c ${version}-${pkg_version})" == "3" ]; then
      echo "all packages are installed"
    else
      for package in percona-backup-mongodb-coordinator percona-backup-mongodb-agent percona-backup-mongodb-pbmctl; do
        if [ "$(dpkg -l | grep -c ${package})" -gt 0 ] && [ "$(dpkg -l | grep ${package} | awk '{$print $3}')" == "${version}-${pkg_version}.$(lsb_release -sc)" ] ; then
          echo "$(date +%Y%m%d%H%M%S): ${package} is installed" >> ${log}
        else
          echo "WARNING: ${package}-${version}-${pkg_version} is not installed"
          exit 1
        fi
      done
    fi
  fi

elif [ "${product}" == "repo" ]; then
  if [ -f /etc/redhat-release ] || [ -f /etc/system-release ]; then
    if [ "$(rpm -qa | grep percona-release | grep -c ${version})" == "1" ]; then
      echo "repo packages is installed"
    else 
      echo "WARNING percona-release-${version} is not installed"
      exit 1 
    fi
  else
    if [ "$(dpkg -l | grep percona-release | grep -c ${version})" == "1" ]; then
      echo "repo packages is installed"
    else
      echo "WARNING: percona-release-${version} is not installed"
      exit 1
    fi
  fi
fi

echo "${product} installed package versions are OK"
