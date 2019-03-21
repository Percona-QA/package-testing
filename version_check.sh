#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps55, ps56, ps57 or ps80!"
  echo "Usage: ./version_check.sh <prod>"
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
elif [ $1 = "ps80" ]; then
  version=${PS80_VER}
  release=${PS80_VER#*-}
  revision=${PS80_REV}
elif [ $1 = "pxc56" ]; then
  version=${PXC56_VER%-*}
  release=${PXC56_VER#*-}
  revision=${PXC56_REV}
  innodb_ver=${PXC56_INNODB}
  wsrep=${PXC56_WSREP}
elif [ $1 = "pxc57" ]; then
  version=${PXC57_VER%-*}
  release=${PXC57_VER#*-}
  revision=${PXC57_REV}
  innodb_ver=${PXC57_INNODB}
  wsrep=${PXC57_WSREP}
elif [ $1 = "pt" ]; then
  version=${PT_VER}
elif [ $1 = "pxb23" ]; then
  version=${PXB23_VER}
elif [ $1 = "pxb24" ]; then
  version=${PXB24_VER}
elif [ $1 = "pxb80" ]; then
  version=${PXB80_VER}
elif [ $1 = "pmm" ]; then
  version=${PMM_VER}
elif [ $1 = "pmm2" ]; then
  version=${PMM2_VER}
elif [ $1 = "proxysql" ]; then
  version=${PROXYSQL_VER}
elif [ $1 = "sysbench" ]; then
  version=${SYSBENCH_VER}
elif [ $1 = "pbm" ]; then
  version=${PBM_VER}
  revision=${PBM_REV}
else
  echo "Illegal product selected!"
  exit 1
fi

# This function checks that pxb 8.0 tools have correct version
function xbt_test {
  for i in xbstream xbcloud xbcrypt; do
    version_check=$($i --help | grep -c ${version})
    if [ ${version_check} -eq 0 ]; then
       echo "${i} version is not good!"
       exit 1
    else
       echo "${i} version is correct and ${version}" >> ${log}
    fi
  done
}

product=$1
log="/tmp/${product}_version_check.log"
echo -n > ${log}

if [ ${product} = "ps55" -o ${product} = "ps56" -o ${product} = "ps57" -o ${product} = "ps80" ]; then
  for i in @@INNODB_VERSION @@VERSION @@TOKUDB_VERSION; do
    if [ ${product} = "ps55" -a ${i} = "@@TOKUDB_VERSION" ]; then
      echo "${i} is empty" >> ${log}
    elif [ "$(mysql -e "SELECT ${i}; "| grep -c ${version})" = 1 ]; then
      echo "${i} is correct" >> ${log}
    else
      echo "${i} is incorrect"
      exit 1
    fi
  done

  if [ "$(mysql -e "SELECT @@VERSION_COMMENT;" | grep ${revision} | grep -c ${release})" = 1 ]; then
    echo "@@VERSION COMMENT is correct" >> ${log}
  else
    echo "@@VERSION_COMMENT is incorrect"
    exit 1
  fi

elif [ ${product} = "pxc56" -o ${product} = "pxc57" ]; then
  for i in @@INNODB_VERSION @@VERSION; do
    if [ "$(mysql -e "SELECT ${i}; "| grep -c ${version}-${innodb_ver})" = 1 ]; then
      echo "${i} is correct" >> ${log}
    else
      echo "${i} is incorrect"
      exit 1
    fi
  done

  if [ "$(mysql -e "SELECT @@VERSION_COMMENT;" | grep ${revision} | grep rel${innodb_ver} | grep -c ${release})" = 1 ]; then
    echo "@@VERSION COMMENT is correct" >> ${log}
  else
    echo "@@VERSION_COMMENT is incorrect"
    exit 1
  fi

  if [ "$(mysql -e "SHOW STATUS LIKE 'wsrep_provider_version';" | grep -c ${wsrep})" = 1 ]; then
    echo "wsrep_provider_version is correct" >> ${log}
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
      echo "${i} version is correct and ${version}" >> ${log}
    fi
  done

elif [ ${product} = "pmm" ]; then
  version_check=$(pmm-admin --version 2>&1|grep -c ${version})
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> ${log}
  fi

elif [ ${product} = "pmm2" ]; then
  version_check=$(pmm-agent --version 2>&1|grep -c ${version})
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> ${log}
  fi

elif [ ${product} = "pxb23" -o ${product} = "pxb24" -o ${product} = "pxb80" ]; then
  version_check=$(xtrabackup --version 2>&1|grep -c ${version})
    if [ ${version_check} -eq 0 ]; then
      echo "${product} version is not good!"
      exit 1
    else
      echo "${product} version is correct and ${version}" >> ${log}
    fi
    if [ ${product} = "pxb80" ]; then
      xbt_test
    fi

elif [ ${product} = "proxysql" ]; then
  version_check=$(proxysql --version 2>&1|grep -c ${version})
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> ${log}
  fi

elif [ ${product} = "sysbench" ]; then
  version_check=$(sysbench --version 2>&1|grep -c ${version})
  if [ ${version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> ${log}
  fi

elif [ ${product} = "pbm" ]; then
  agent_version_check=$(pbm-agent --version 2>&1|head -n1|grep -oE "[0-9]*\.[0-9]*\.[0-9]*"|grep -c ${version})
  agent_revision_check=$(pbm-agent --version 2>&1|head -n1|grep -oE "commit .*$"|sed 's/commit //'|grep -c ${revision})
  coordinator_version_check=$(pbm-coordinator --version 2>&1|head -n1|grep -oE "[0-9]*\.[0-9]*\.[0-9]*"|grep -c ${version})
  coordinator_revision_check=$(pbm-coordinator --version 2>&1|head -n1|grep -oE "commit .*$"|sed 's/commit //'|grep -c ${revision})
  control_version_check=$(pbmctl --version 2>&1|head -n1|grep -oE "[0-9]*\.[0-9]*\.[0-9]*"|grep -c ${version})
  control_revision_check=$(pbmctl --version 2>&1|head -n1|grep -oE "commit .*$"|sed 's/commit //'|grep -c ${revision})
  if [ ${agent_version_check} -eq 0 -o ${coordinator_version_check} -eq 0 -o ${control_version_check} -eq 0 ]; then
    echo "${product} version is not good!"
    exit 1
  else
    echo "${product} version is correct and ${version}" >> ${log}
  fi
  if [ ${agent_revision_check} -eq 0 -o ${coordinator_revision_check} -eq 0 -o ${control_revision_check} -eq 0 ]; then
    echo "${product} revision is not good!"
    exit 1
  else
    echo "${product} revision is correct and ${revision}" >> ${log}
  fi

fi
echo "${product} versions are OK"
