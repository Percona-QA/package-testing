#!/bin/bash

log="/tmp/psmdb_run.log"
echo -n > /tmp/psmdb_run.log

source /package-testing/VERSIONS

SLES=0
if [ -f /etc/os-release ]; then
  SLES=$(cat /etc/os-release | grep -c '^NAME=\"SLES' || true)
fi

set -e

if [ -z "$1" ]; then
  echo "This script needs parameter 3.0|3.2|3.4"
  exit 1
elif [ "$1" != "3.0" -a "$1" != "3.2" -a "$1" != "3.4" ]; then
  echo "Version not recognized!"
  exit 1
else
  VERSION="$1"
fi

# Enable auditLog and profiling/rate limit to see if services start with those
if [ "$VERSIONS" == "3.0" ]; then
  echo "Skipping usage of profiling rate limit functionality because not available in 3.0"
  sed -i 's/#operationProfiling:/operationProfiling:\n  mode: all\n  slowOpThresholdMs: 200/' /etc/mongod.conf
else
  sed -i 's/#operationProfiling:/operationProfiling:\n  mode: all\n  slowOpThresholdMs: 200\n  rateLimit: 100/' /etc/mongod.conf
fi
sed -i 's/#auditLog:/audit:\n  destination: file\n  path: \/tmp\/audit.json/' /etc/mongod.conf

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
  if [ -f /etc/redhat-release -o ${SLES} -eq 1 ]; then
    echo "$(date +%Y%m%d%H%M%S): contents of the mongo data dir: " >> $log
    ls -alh /var/lib/mongo/ >> $log
  else
    echo "$(date +%Y%m%d%H%M%S): contents of the mongodb data dir: " >> $log
    ls -alh /var/lib/mongodb/ >> $log
  fi
}

function clean_datadir {
  if [ -f /etc/redhat-release -o ${SLES} -eq 1 ]; then
    echo -e "removing the data files (on rhel distros)...\n"
    rm -rf /var/lib/mongo/*
  else
    echo -e "removing the data files (on debian distros)...\n"
    rm -rf /var/lib/mongodb/*
  fi
}

function test_hotbackup {
  rm -rf /tmp/backup
  mkdir -p /tmp/backup
  chown mongod:mongod -R /tmp/backup
  BACKUP_RET=$(mongo admin --eval 'db.runCommand({createBackup: 1, backupDir: "/tmp/backup"})'|grep -c '"ok" : 1')
  rm -rf /tmp/backup
  if [ ${BACKUP_RET} = 0 ]; then
    echo "Backup failed for storage engine: ${engine}"
    exit 1
  fi
}

function check_rocksdb {
  ROCKSDB_LOG_FILE=""
  if [ -f /etc/redhat-release -o ${SLES} -eq 1 ]; then
    ROCKSDB_LOG_FILE="/var/lib/mongo/db/LOG"
  else
    ROCKSDB_LOG_FILE="/var/lib/mongodb/db/LOG"
  fi
  # Check RocksDB library version
  ROCKSDB_VERSION=$(grep "RocksDB version" ${ROCKSDB_LOG_FILE}|tail -n1|grep -Eo "[0-9]+\.[0-9]+(\.[0-9]+)*$")
  if [ "${VERSION}" == "3.0" ]; then
    ROCKSDB_VERSION_NEEDED=${PSMDB30_ROCKSDB_VER}
  elif [ "${VERSION}" == "3.2" ]; then
    ROCKSDB_VERSION_NEEDED=${PSMDB32_ROCKSDB_VER}
  elif [ "${VERSION}" == "3.4" ]; then
    ROCKSDB_VERSION_NEEDED=${PSMDB34_ROCKSDB_VER}
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
  if [ "$1" == "3.4" -a ${engine} == "PerconaFT" ]; then
    echo "Skipping PerconaFT because version is 3.4"
  else
    stop_service
    clean_datadir
    echo "=================" | tee -a $log
    echo "testing ${engine}" | tee -a $log
    echo "=================" | tee -a $log
    sed -i "/engine: *${engine}/s/#//g" /etc/mongod.conf
    start_service
    mongo --eval "db.serverStatus().storageEngine" | tee -a $log
    if [ ${engine} == "rocksdb" ]; then
      check_rocksdb
    fi
    echo "importing the sample data"
    mongo < /package-testing/mongo_insert.js >> $log
    list_data >> $log
    if [[ ${engine} = "wiredTiger" || ${engine} = "rocksdb" ]] && [[ "$1" != "3.0" ]]; then
      echo "testing the hotbackup functionality"
      test_hotbackup
    fi
    stop_service
    echo "disable ${engine}"
    sed -i "/engine: *${engine}/s//#engine: ${engine}/g" /etc/mongod.conf
    clean_datadir
  fi
done
