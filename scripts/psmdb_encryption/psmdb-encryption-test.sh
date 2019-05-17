#!/bin/bash

source /package-testing/VERSIONS
source /package-testing/scripts/psmdb_common.sh

echo -n > ${LOG}

set -e

if [ -z "$1" ]; then
  echo "This script needs parameter keyring or vault"
  exit 1
elif [ "$1" != "keyring" -a "$1" != "vault" ]; then
  echo "Key store not recognized!"
  exit 1
else
  KEY_STORE="$1"
fi

cp ${CONFIGFILE} ${BACKUP_CONFIGFILE}
if [ "$1" == "keyring" ]; then
  chmod 600 /package-testing/scripts/psmdb_encryption/mongodb-keyfile
  chown mongod:mongod /package-testing/scripts/psmdb_encryption/mongodb-keyfile
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
      sed -i "s/#security:/security:\n  enableEncryption: true\n  encryptionCipherMode: ${cipher}\n  encryptionKeyFile: \/package-testing\/scripts\/psmdb_encryption\/mongodb-keyfile/" ${CONFIGFILE}
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
    elif [ "$(mongo --quiet --eval "db.serverCmdLineOpts().parsed.security.encryptionKeyFile" | tail -n1)" != "/package-testing/scripts/psmdb_encryption/mongodb-keyfile" ]; then
      echo "ERROR: Encryption key file is not set to: /package-testing/scripts/psmdb_encryption/mongodb-keyfile" | tee -a ${LOG}
      exit 1
    fi
    echo "adding some data and indexes with cipher ${cipher}" | tee -a ${LOG}
    mongo localhost:27017/test --eval "for(i=1; i <= 100000; i++) { db.series.insert( { id: i, name: 'series'+i })}" >> ${LOG}
    mongo localhost:27017/test --eval "db.series.ensureIndex({ name: 1 })" >> ${LOG}
    echo "testing the hotbackup functionality with ${cipher}" | tee -a ${LOG}
    test_hotbackup
  done
fi
