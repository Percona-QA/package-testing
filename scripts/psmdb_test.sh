#!/bin/bash

DATADIR=""
BACKUPDIR="/tmp/backup"
CONFIGFILE="/etc/mongod.conf"

LOG="/tmp/psmdb_run.log"
echo -n > ${LOG}

source /package-testing/VERSIONS

SLES=0
if [ -f /etc/os-release ]; then
  SLES=$(cat /etc/os-release | grep -c '^NAME=\"SLES' || true)
fi

if [ -f /etc/redhat-release -o ${SLES} -eq 1 ]; then
  DATADIR="/var/lib/mongo"
else
  DATADIR="/var/lib/mongodb"
fi

set -e

if [ -z "$1" ]; then
  echo "This script needs parameter 3.0|3.2|3.4|3.6|4.0"
  exit 1
elif [ "$1" != "3.0" -a "$1" != "3.2" -a "$1" != "3.4" -a "$1" != "3.6" -a "$1" != "4.0" ]; then
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

function start_service {
  local redhatrelease=""
  if [ -f /etc/redhat-release ]; then
    redhatrelease=$(cat /etc/redhat-release | grep -o '[0-9]' | head -n 1)
  fi
  local lsbrelease=$(lsb_release -sc 2>/dev/null || echo "")
  if [ "${lsbrelease}" != "" -a "${lsbrelease}" = "trusty" ]; then
    echo "starting mongod service directly with init script..."
    /etc/init.d/mongod start
  elif [ "${redhatrelease}" = "5"  ]; then
    echo "starting mongod service directly with init script..."
    /etc/init.d/mongod start
  elif [ "${lsbrelease}" != "" -a ${SLES} -eq 1 ]; then
    echo "starting mongod with /sbin/service on SLES..."
    /sbin/service mongod start
  else
    echo "starting mongod service... "
    service mongod start
  fi
  echo "waiting 10s for service to boot up"
  sleep 10
}

function stop_service {
  local redhatrelease=""
  if [ -f /etc/redhat-release ]; then
    redhatrelease=$(cat /etc/redhat-release | grep -o '[0-9]' | head -n 1)
  fi
  local lsbrelease=$(lsb_release -sc 2>/dev/null || echo "")
  if [ "${lsbrelease}" != "" -a "${lsbrelease}" = "trusty" ]; then
    echo "stopping mongod service directly with init script..."
    /etc/init.d/mongod stop
  elif [ "${redhatrelease}" = "5"  ]; then
    echo "stopping mongod service directly with init script..."
    /etc/init.d/mongod stop
  elif [ "${lsbrelease}" != "" -a ${SLES} -eq 1 ]; then
    echo "stopping mongod with /sbin/service on SLES..."
    /sbin/service mongod stop
  else
    echo "stopping mongod service... "
    service mongod stop
  fi
  echo "waiting 10s for service to stop"
  sleep 10
}

function list_data {
  echo -e "listing files in datadir...\n"
  ls -alh ${DATADIR}/ >> ${LOG}
}

function clean_datadir {
  echo -e "removing the data files...\n"
  rm -rf ${DATADIR}/*
}

function test_hotbackup {
  MD5_BEFORE=$(mongo localhost:27017/test --quiet --eval "db.runCommand({ dbHash: 1 }).md5" | tail -n1)
  rm -rf ${BACKUPDIR}
  mkdir -p ${BACKUPDIR}
  chown mongod:mongod -R ${BACKUPDIR}
  BACKUP_RET=$(mongo localhost:27017/admin --eval "db.runCommand({createBackup: 1, backupDir: '${BACKUPDIR}'})"|grep -c '"ok" : 1')
  if [ ${BACKUP_RET} = 0 ]; then
    echo "Backup failed for storage engine: ${engine}" | tee -a ${LOG}
    exit 1
  fi
  stop_service
  clean_datadir
  cp -r ${BACKUPDIR}/* ${DATADIR}/
  chown -R mongod:mongod ${DATADIR}
  start_service
  MD5_AFTER=$(mongo localhost:27017/test --quiet --eval "db.runCommand({ dbHash: 1 }).md5" | tail -n1)
  if [ "${MD5_BEFORE}" != "${MD5_AFTER}" ]; then
    echo "ERROR: dbHash before and after hotbackup are not the same!" | tee -a ${LOG}
    exit 1
  else
    echo "dbHash is the same before and after hotbackup: ${MD5_BEFORE}:${MD5_AFTER}" | tee -a ${LOG}
  fi
  rm -rf ${BACKUPDIR}
}

function check_rocksdb {
  ROCKSDB_LOG_FILE="${DATADIR}/db/LOG"
  # Check RocksDB library version
  ROCKSDB_VERSION=$(grep "RocksDB version" ${ROCKSDB_LOG_FILE}|tail -n1|grep -Eo "[0-9]+\.[0-9]+(\.[0-9]+)*$")
  if [ "${VERSION}" == "3.0" ]; then
    ROCKSDB_VERSION_NEEDED=${PSMDB30_ROCKSDB_VER}
  elif [ "${VERSION}" == "3.2" ]; then
    ROCKSDB_VERSION_NEEDED=${PSMDB32_ROCKSDB_VER}
  elif [ "${VERSION}" == "3.4" ]; then
    ROCKSDB_VERSION_NEEDED=${PSMDB34_ROCKSDB_VER}
  elif [ "${VERSION}" == "3.6" ]; then
    ROCKSDB_VERSION_NEEDED=${PSMDB36_ROCKSDB_VER}
  else
    echo "Wrong parameter to script: $1"
    exit 1
  fi
  if [ "${ROCKSDB_VERSION}" != "${ROCKSDB_VERSION_NEEDED}" ]; then
    echo "Wrong version of RocksDB library! Needed: ${ROCKSDB_VERSION_NEEDED} got: ${ROCKSDB_VERSION}"
    exit 1
  fi
  # Check RocksDB supported compression libraries
  COMP_LIB_SNAPPY=$(grep "Snappy supported: 1" ${ROCKSDB_LOG_FILE}|wc -l)
  COMP_LIB_ZLIB=$(grep "Zlib supported: 1" ${ROCKSDB_LOG_FILE}|wc -l)
  COMP_LIB_BZIP=$(grep "Bzip supported: 1" ${ROCKSDB_LOG_FILE}|wc -l)
  COMP_LIB_LZ4=$(grep "LZ4 supported: 1" ${ROCKSDB_LOG_FILE}|wc -l)
  if [ ${COMP_LIB_SNAPPY} -lt 1 -o ${COMP_LIB_ZLIB} -lt 1 -o ${COMP_LIB_BZIP} -lt 1 -o ${COMP_LIB_LZ4} -lt 1 ]; then
    echo "Error when checking compression libraries in RocksDB."
    echo "Snappy: ${COMP_LIB_SNAPPY}"
    echo "Zlib: ${COMP_LIB_ZLIB}"
    echo "Bzip: ${COMP_LIB_BZIP}"
    echo "LZ4: ${COMP_LIB_LZ4}"
    exit 1
  fi
  # Check RocksDB support for FastCRC
  FAST_CRC=$(grep "Fast CRC32 supported: 1" ${ROCKSDB_LOG_FILE}|wc -l)
  if [ ${FAST_CRC} -lt 1 ]; then
    echo "FastCRC is not enabled for MongoRocks."
    echo "$(grep "Fast CRC32 supported" ${ROCKSDB_LOG_FILE})"
    exit 1
  fi
}

for engine in mmapv1 PerconaFT rocksdb wiredTiger inMemory; do
  if [ "$1" != "3.2" -a "${engine}" == "PerconaFT" ]; then
    echo "Skipping PerconaFT because version is >3.2"
  elif [ "$1" = "4.0" -a "${engine}" == "rocksdb" ]; then
      echo "Skipping rocksdb because version is 4.0"
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

if [ "$1" == "3.6" ] || [ "$1" == "4.0" ]; then
  for cipher in AES256-CBC AES256-GCM; do
    echo "==================================" | tee -a ${LOG}
    echo "testing encryption with ${cipher}" | tee -a ${LOG}
    echo "==================================" | tee -a ${LOG}
    echo "preparing datadir for testing encryption with ${cipher}" | tee -a ${LOG}
    stop_service
    clean_datadir
    sed -i "/^  engine: /s/^/#/g" ${CONFIGFILE}
    engine="wiredTiger"
    sed -i "/engine: *${engine}/s/#//g" ${CONFIGFILE}
    if [ ${cipher} = "AES256-CBC" ]; then
      sed -i "s/#security:/security:\n  enableEncryption: true\n  encryptionCipherMode: ${cipher}\n  encryptionKeyFile: \/package-testing\/scripts\/mongodb-keyfile/" ${CONFIGFILE}
    else
      sed -i "s/encryptionCipherMode: AES256-CBC/encryptionCipherMode: AES256-GCM/" ${CONFIGFILE}
    fi
    start_service
    if [ "$(mongo --quiet --eval "db.serverCmdLineOpts().parsed.security.enableEncryption" | tail -n1)" != "true" ]; then
      echo "ERROR: Encryption is not enabled!" | tee -a ${LOG}
      exit 1
    elif [ "$(mongo --quiet --eval "db.serverCmdLineOpts().parsed.security.encryptionCipherMode" | tail -n1)" != "${cipher}" ]; then
      echo "ERROR: Cipher mode is not set to: ${cipher}" | tee -a ${LOG}
      exit 1
    elif [ "$(mongo --quiet --eval "db.serverCmdLineOpts().parsed.security.encryptionKeyFile" | tail -n1)" != "/package-testing/scripts/mongodb-keyfile" ]; then
      echo "ERROR: Encryption key file is not set to: /package-testing/scripts/mongodb-keyfile" | tee -a ${LOG}
      exit 1
    fi
    echo "adding some data and indexes with cipher ${cipher}" | tee -a ${LOG}
    mongo localhost:27017/test --eval "for(i=1; i <= 100000; i++) { db.series.insert( { id: i, name: 'series'+i })}" >> ${LOG}
    mongo localhost:27017/test --eval "db.series.ensureIndex({ name: 1 })" >> ${LOG}
    echo "testing the hotbackup functionality with ${cipher}" | tee -a ${LOG}
    test_hotbackup
  done
fi
