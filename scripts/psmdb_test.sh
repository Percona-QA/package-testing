#!/bin/bash

source /package-testing/VERSIONS
source /package-testing/scripts/psmdb_common.sh

echo -n > ${LOG}

set -e

if [ -z "$1" ]; then
  echo "This script needs parameter 3.0|3.2|3.4|3.6|4.0|4.2|4.4"
  exit 1
elif [ "$1" != "3.0" -a "$1" != "3.2" -a "$1" != "3.4" -a "$1" != "3.6" -a "$1" != "4.0" -a "$1" != "4.2" -a "$1" != "4.4" ]; then
  echo "Version not recognized!"
  exit 1
else
  VERSION="$1"
fi

# Enable auditLog and profiling/rate limit to see if services start with those
if [ "$VERSION" == "3.0" ]; then
  echo "Skipping usage of profiling rate limit functionality because not available in 3.0"
  sed -i 's/#operationProfiling:/operationProfiling:\n  mode: all\n  slowOpThresholdMs: 200/' ${CONFIGFILE}
else
  sed -i 's/#operationProfiling:/operationProfiling:\n  mode: all\n  slowOpThresholdMs: 200\n  rateLimit: 100/' ${CONFIGFILE}
fi
sed -i 's/#auditLog:/audit:\n  destination: file\n  path: \/tmp\/audit.json/' ${CONFIGFILE}

# Enable --useDeprecatedMongoRocks for 3.6 to be able to start service with mongorocks
if [ "$VERSION" == "3.6" ]; then
  echo "Adding --useDeprecatedMongoRocks option to mongod.cnf"
  sed -i '/engine: rocksdb/a \  useDeprecatedMongoRocks: true' ${CONFIGFILE}
fi

# make a backup config file
cp ${CONFIGFILE} ${BACKUP_CONFIGFILE}

for engine in mmapv1 PerconaFT rocksdb inMemory wiredTiger; do
  if [ "$1" != "3.2" -a "${engine}" == "PerconaFT" ]; then
    echo "Skipping PerconaFT because version is >3.2"
  elif [ "$1" = "4.0" -o "$1" = "4.2" -o "$1" = "4.4" ] && [ "${engine}" == "rocksdb" ]; then
    echo "Skipping rocksdb because version is >3.6"
  elif [ "$1" = "4.2" -o "$1" = "4.4" ] && [ "${engine}" == "mmapv1" ]; then
    echo "Skipping mmapv1 because version is >4.0"
  else
    stop_service
    clean_datadir
    echo "=================" | tee -a ${LOG}
    echo "testing ${engine}" | tee -a ${LOG}
    echo "=================" | tee -a ${LOG}
    sed -i "/engine: *${engine}/s/#//g" ${CONFIGFILE}
    start_service
    mongo --eval "db.serverStatus().storageEngine" | tee -a ${LOG}
    if [ ${engine} == "rocksdb" ]; then
      check_rocksdb
    fi
    echo "importing the sample data"
    mongo < /package-testing/scripts/mongo_insert.js >> ${LOG}
    list_data >> ${LOG}
    if [[ ${engine} = "wiredTiger" || ${engine} = "rocksdb" ]] && [[ "$1" != "3.0" ]]; then
      echo "testing the hotbackup functionality"
      test_hotbackup
    fi
    stop_service
    echo "disable ${engine}"
    sed -i "/engine: *${engine}/s//#engine: ${engine}/g" ${CONFIGFILE}
    clean_datadir
  fi
  start_service
done
