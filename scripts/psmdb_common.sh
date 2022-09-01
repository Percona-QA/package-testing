#!/usr/bin/env bash

DATADIR=""
BACKUPDIR="/tmp/backup"
CONFIGFILE="/etc/mongod.conf"
BACKUP_CONFIGFILE="/tmp/mongod.conf.backup"
LOG="/tmp/psmdb_run.log"

SLES=0
if [ -f /etc/os-release ]; then
  SLES=$(cat /etc/os-release | grep -c '^NAME=\"SLES' || true)
fi

if [ -f /etc/redhat-release -o ${SLES} -eq 1 ]; then
  DATADIR="/var/lib/mongo"
else
  DATADIR="/var/lib/mongodb"
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
