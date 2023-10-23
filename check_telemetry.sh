# This script performs basic checks for telemetry script from Phase 0.
# Based on parameters passed, it checks that:
# * the telemetry file was created and has both valid instanceID and PRODUCT_FAMILY_XX (telemetry sending was enabled during run and was successful "-e" param)
# * the telemetry file was not created (telemertry sending was disabled during run "-d" param)
# * the telemetry file was created and has valid instanceID and no PRODUCT_FAMILY_XX (telemertry sending was enabled during run and was not successful "-u" param)

#!/bin/bash

set -e

if [ "$#" -ne 2 ]; then
  echo "This script requires 2 prameters:"
  echo "* product parameter: ps, pxc, ppg, psmdb!"
  echo "* result parameter: -e (enabled telemetry); -d (disabled telemetry); -u (unsuccessful telemetry) "
  echo "Usage: ./package_check.sh <prod> <result>"
  exit 1
fi

FILE_LOCATION="/usr/local/percona/telemetry_uuid"

if [ $1 = "ps" ]; then
  PERCONA_PRODUCT_FAMILY="PRODUCT_FAMILY_PS"
elif [ $1 = "pxc" ]; then
  PERCONA_PRODUCT_FAMILY="PRODUCT_FAMILY_PXC"
elif [ $1 = "ppg" ]; then
  PERCONA_PRODUCT_FAMILY="PRODUCT_FAMILY_POSTGRESQL"
elif [ $1 = "psmdb" ]; then
  PERCONA_PRODUCT_FAMILY="PRODUCT_FAMILY_PSMDB"
else
  echo "Illegal product selected!"
  exit 1
fi

if [ $2 = "-e" ]; then
  if [[ -s ${FILE_LOCATION} ]]; then
    if [[ $(grep -c ${PERCONA_PRODUCT_FAMILY}:1 ${FILE_LOCATION}) -ne 1 ]]; then
      echo "The telemetry is enabled and ${PERCONA_PRODUCT_FAMILY} is not present in ${FILE_LOCATION}! Please check!"
      exit 1
    fi
    if [[ $(sed -n 's/instanceId://p' /usr/local/percona/telemetry_uuid|grep -c "^[0-9a-fA-F]\{8\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{12\}$" ) -ne 1 ]]; then
      echo "The telemetry is enabled and generated instanceId is incorrect or not present in ${FILE_LOCATION}! Please check!"
      exit 1
    fi
  else
    echo "The telemetry is enabled and ${FILE_LOCATION} is not present! Check!"
    exit 1
  fi
elif [ $2 = "-u" ]; then
  if [[ -s ${FILE_LOCATION} ]]; then
    if [[ $(grep -c ${PERCONA_PRODUCT_FAMILY}:1 ${FILE_LOCATION}) -eq 1 ]]; then
      echo "The telemetry is not sent and ${PERCONA_PRODUCT_FAMILY} is present in ${FILE_LOCATION}! Please check!"
      exit 1
    fi
    if [[ $(sed -n 's/instanceId://p' /usr/local/percona/telemetry_uuid|grep -c "^[0-9a-fA-F]\{8\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{4\}-[0-9a-fA-F]\{12\}$" ) -ne 1 ]]; then
      echo "The telemetry is enabled and generated instanceId is incorrect or not present in ${FILE_LOCATION}! Please check!"
      exit 1
    fi
  else
    echo "The telemetry is enabled and ${FILE_LOCATION} is not present! Check!"
    exit 1
  fi
elif [ $2 = "-d" ]; then
  if [[ -s ${FILE_LOCATION} ]]; then
    echo "The telemetry is disabled and ${FILE_LOCATION} is present! Check!"
    exit 1
  fi
else
  echo "Illegal action selected!"
  exit 1
fi

echo "Everything is fine"
