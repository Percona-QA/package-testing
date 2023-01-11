#!/bin/bash

if [[ "$#" -ne 1 ]]; then
  echo "This script requires expected version parameter, ex.: X.XX.X"
  echo "Usage: ./pmm2_client_version_checker.sh 2.30.0"
  exit 1
fi

EXPECTED=$1

if [[ -z "$2" ]]; then
  FLAG=$2
fi

pmm-admin --version ${FLAG}
version_match=$(pmm-admin --version ${FLAG} 2>&1|grep -c "${EXPECTED}")
actual_version=$(pmm-admin --version ${FLAG} 2>&1|grep ^Version | awk -F ' ' '{print $2}')
if [ ${version_match} -eq 0 ]; then
  echo "PMM Client version ${actual_version} is not good! Expected: ${EXPECTED}" >&2;
  exit 1
else
  echo "PMM Client version is correct and ${EXPECTED}"
fi
bash -xe ../check_pmm2_client_upgrade.sh ${EXPECTED}

echo "PMM Client versions are OK"
