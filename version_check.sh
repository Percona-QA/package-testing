#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps56, ps57 or ps80!"
  echo "Usage: ./version_check.sh <prod>"
  exit 1
fi

SCRIPT_PWD=$(cd $(dirname "$0") && pwd)

source "${SCRIPT_PWD}"/VERSIONS

if [ "$1" = "ps56" ]; then
  version=${PS56_VER}
  release=${PS56_VER#*-}
  revision=${PS56_REV}
elif [ "$1" = "ps57" ]; then
  version=${PS57_VER}
  release=${PS57_VER#*-}
  revision=${PS57_REV}
elif [ "$1" = "ps80" ]; then
  version=${PS80_VER}
  release=${PS80_VER#*-}
  revision=${PS80_REV}
elif [ "$1" = "pxc56" ]; then
  version=${PXC56_VER%-*}
  release=${PXC56_VER#*-}
  revision=${PXC56_REV}
  innodb_ver=${PXC56_INNODB}
  wsrep=${PXC56_WSREP}
elif [ "$1" = "pxc57" ]; then
  version=${PXC57_VER%-*}
  release=${PXC57_VER#*-}
  revision=${PXC57_REV}
  innodb_ver=${PXC57_INNODB}
  wsrep=${PXC57_WSREP}
elif [ "$1" = "pxc80" ]; then
  version=${PXC80_VER%-*}
  release=${PXC80_VER#*-}
  revision=${PXC80_REV}
  innodb_ver=${PXC80_INNODB}
  wsrep=${PXC80_WSREP}
elif [ "$1" = "pt" ]; then
  version=${PT_VER}
elif [ "$1" = "pxb23" ]; then
  version=${PXB23_VER}
elif [ "$1" = "pxb24" ]; then
  version=${PXB24_VER}
elif [ "$1" = "pxb80" ]; then
  version=${PXB80_VER}
elif [ "$1" = "pmm" ]; then
  version=${PMM_VER}
elif [ "$1" = "pmm2" ]; then
  version=${PMM2_VER}
elif [ "$1" = "pmm2-rc" ]; then
  version=${PMM2_RC_VER}
elif [ "$1" = "proxysql" ]; then
  version=${PROXYSQL_VER}
elif [ "$1" = "proxysql2" ]; then
  version=${PROXYSQL2_VER}
elif [ "$1" = "sysbench" ]; then
  version=${SYSBENCH_VER}
elif [ "$1" = "pbm" ]; then
  version=${PBM_VER}
  revision=${PBM_REV}
elif [ "$1" = "psmdb34" ]; then
  version=${PSMDB34_VER}
elif [ "$1" = "psmdb36" ]; then
  version=${PSMDB36_VER}
elif [ "$1" = "psmdb40" ]; then
  version=${PSMDB40_VER}
elif [ "$1" = "psmdb42" ]; then
  version=${PSMDB42_VER}
elif [ "$1" = "psmdb44" ]; then
  version=${PSMDB44_VER}
elif [ "$1" = "psmdb50" ]; then
  version=${PSMDB50_VER}
else
  echo "Illegal product selected!"
  exit 1
fi

product=$1
log="/tmp/${product}_version_check.log"
echo -n > "${log}"

if [ "${product}" = "ps56" -o "${product}" = "ps57" -o "${product}" = "ps80" ]; then
  for i in @@INNODB_VERSION @@VERSION; do
    if [ "$(mysql -e "SELECT ${i}; "| grep -c "${version}")" = 1 ]; then
      echo "${i} is correct" >> "${log}"
    else
      echo "${i} is incorrect it shows $(mysql -e "SELECT ${i};")"
      exit 1
    fi
 done
 if [ "${product}" = "ps56" -o "${product}" = "ps57" ]; then
    if [ "$(mysql -e "SELECT @@TOKUDB_VERSION; "| grep -c "${version}")" = 1 ]; then
      echo "@@TOKUDB_VERSION is correct" >> "${log}"
    else
      echo "@@TOKUDB_VERSION is incorrect it shows $(mysql -e "SELECT @@TOKUDB_VERSION;")"
    fi
  fi

  if [ "$(mysql -e "SELECT @@VERSION_COMMENT;" | grep ${revision} | grep -c ${release})" = 1 ]; then
    echo "@@VERSION COMMENT is correct" >> "${log}"
  else
    echo "@@VERSION_COMMENT is incorrect"
    exit 1
  fi

  if [ ${product} = "ps80" ]; then
    if [ -z ${install_mysql_shell} ] || [ ${install_mysql_shell} = "yes" ] ; then
      if [ "$(mysqlsh --version | grep -c ${version})" = 1 ]; then
        echo "mysql-shell version is correct" >> "${log}"
      else
        echo "ERROR: mysql-shell version is incorrect"
        exit 1
      fi
    elif [ ${install_mysql_shell} = "no" ]; then
      echo "MYSQL Shell check is disabled.." >> "${log}"
    else
      echo "Invalid input in ${install_mysql_shell} variable"
    fi
  fi

elif [ ${product} = "pxc56" -o ${product} = "pxc57" -o ${product} = "pxc80" ]; then
  for i in @@INNODB_VERSION @@VERSION; do
    if [ "$(mysql -e "SELECT ${i}; "| grep -c ${version}-${innodb_ver})" = 1 ]; then
      echo "${i} is correct" >> "${log}"
    else
      echo "${i} is incorrect"
      exit 1
    fi
  done

  if [ "$(mysql -e "SELECT @@VERSION_COMMENT;" | grep ${revision} | grep rel${innodb_ver} | grep -c ${release})" = 1 ]; then
    echo "@@VERSION COMMENT is correct" >> "${log}"
  else
    echo "@@VERSION_COMMENT is incorrect"
    mysql -e "SELECT @@VERSION_COMMENT;"
    exit 1
  fi

  if [ "$(mysql -e "SHOW STATUS LIKE 'wsrep_provider_version';" | grep -c ${wsrep})" = 1 ]; then
    echo "wsrep_provider_version is correct" >> "${log}"
  else
    echo "wsrep_provider_version is incorrect"
    exit 1
  fi

elif [ ${product} = "pt" ]; then
  for i in `cat /package-testing/pt`; do
    version_check=$(${i} --version|grep -c ${version})
    if [ ${version_check} -eq 0 ]; then
      echo "${i} version is not good!"
      exit 1
    else
      echo "${i} version is correct and ${version}" >> "${log}"
    fi
  done

elif [ ${product} = "pmm" ]; then
  version_check=$(pmm-admin --version 2>&1|grep -c ${version})
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> "${log}"
  fi

elif [ ${product} = "pmm2" -o ${product} = "pmm2-rc" ]; then
  pmm-admin --version
  version_check=$(pmm-admin --version 2>&1|grep -c "${version}")
  actual_version=$(pmm-admin --version 2>&1|grep ^Version | awk -F ' ' '{print $2}')
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version ${actual_version} is not good! Expected: ${version}" >&2;
    exit 1
  else
    echo "${product} version is correct and ${version}"
  fi
  bash -xe ./check_pmm2_client_upgrade.sh ${version}

elif [ "${product}" = "pxb24" -o "${product}" = "pxb80" ]; then
    for binary in xtrabackup xbstream xbcloud xbcrypt; do
        version_check=$($binary --version 2>&1| grep -c "${version}")
        installed_version=$($binary --version 2>&1|tail -1|awk '{print $3}')
        if [ "${version_check}" -eq 0 ]; then
            echo "${binary} version is incorrect! Expected version: ${version} Installed version: ${installed_version}"
            exit 1
        else
            echo "${binary} version is correctly displayed as: ${version}" >> "${log}"
        fi
    done

elif [ ${product} = "proxysql" -o ${product} = "proxysql2" ]; then
  # Define binaries lists depending on product.
  # proxysql 1.X.X packages contain 'proxysql' and 'proxysql-admin' binaries.
  # proxysql 2.X.X packages contain 'proxysql', 'proxysql-admin', 'percona-scheduler-admin' and 'pxc_scheduler_handler' binaries.
  if [ ${product} = "proxysql" ]; then
    binaries_list='proxysql proxysql-admin'
  else
    binaries_list='proxysql proxysql-admin percona-scheduler-admin pxc_scheduler_handler'
  fi
    # Check version of each binary.
  for binary in ${binaries_list}; do
    # proxysql and proxysql-admin/pxc_scheduler_handler have different formats of version output.
    # proxysql 2.X.X-percona-X.X, proxysql-admin/pxc_scheduler_handler 2.X.X
    if [ "${binary}" != "proxysql" ]; then
      version=$(echo "${version}" | awk -F '-' '{print $1}')
    fi
    version_check=$(${binary} --version 2>&1|grep -c ${version})
    installed_version=$(${binary} --version)
    if [ ${version_check} -eq 0 ]; then
      echo "${binary} version ${version} is not good!. Installed version: ${installed_version}"
      exit 1
    else
      echo "${binary} version is correct and ${version}" >> "${log}"
    fi
  done

elif [ ${product} = "sysbench" ]; then
  version_check=$(sysbench --version 2>&1|grep -c ${version})
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> "${log}"
  fi

elif [ ${product} = "pbm" ]; then
  agent_version_check=$(pbm-coordinator --version 2>&1|grep -oE "Version .*$"|grep -c ${version})
  agent_revision_check=$(pbm-coordinator --version 2>&1|grep -oE "Commit .*$"|grep -c ${revision})
  coordinator_version_check=$(pbm-coordinator --version 2>&1|grep -oE "Version .*$"|grep -c ${version})
  coordinator_revision_check=$(pbm-coordinator --version 2>&1|grep -oE "Commit .*$"|grep -c ${revision})
  control_version_check=$(pbmctl version 2>&1|grep -oE "Version .*$"|grep -c ${version})
  control_revision_check=$(pbmctl version 2>&1|grep -oE "Commit .*$"|grep -c ${revision})
  if [ ${agent_version_check} -eq 0 -o ${coordinator_version_check} -eq 0 -o ${control_version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> "${log}"
  fi
  if [ ${agent_revision_check} -eq 0 -o ${coordinator_revision_check} -eq 0 -o ${control_revision_check} -eq 0 ]; then
    echo "${product} revision is not good!"
    exit 1
  else
    echo "${product} revision is correct and ${revision}" >> "${log}"
  fi

elif [ ${product} = "psmdb34" -o ${product} = "psmdb36" -o ${product} = "psmdb40" -o ${product} = "psmdb42" -o ${product} = "psmdb44" ]; then
  ##PSMDB-544
  declare -A new_bin_version=(["3.6"]="21" ["4.0"]="22" ["4.2"]="11" ["4.4"]="2")
  ver="${version%-*}"; major_ver="${ver%.*}"; minor_ver="${ver##*.}"
  binary=(mongo mongod mongos bsondump mongoexport mongofiles mongoimport mongorestore mongotop mongostat)
  if (( $minor_ver >= "${new_bin_version[$major_ver]}" )); then
     binary+=(mongobridge perconadecrypt)
  fi
  for binary in ${binary[@]}; do
    binary_version_check=$(${binary} --version|head -n1|grep -c "${version}")
    if [ ${binary_version_check} -eq 0  ]; then
       echo "${product} version is not good for binary ${binary}!"
       exit 1
    fi
  done

fi
echo "${product} versions are OK"
