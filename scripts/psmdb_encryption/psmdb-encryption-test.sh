#!/bin/bash

source /package-testing/VERSIONS
source /package-testing/scripts/psmdb_common.sh
KEY_FILE="/package-testing/scripts/psmdb_encryption/mongodb-keyfile"
TOKEN_FILE="/package-testing/scripts/psmdb_encryption/mongodb-test-vault-token"
CA_FILE="/package-testing/scripts/psmdb_encryption/test.cer"

echo -n > ${LOG}

set -e

if [ -z "$1" ]; then
  echo "This script needs parameter keyring or vault"
  exit 1
elif [ "$1" != "keyfile" -a "$1" != "vault" ]; then
  echo "Key store not recognized!"
  exit 1
else
  KEY_STORE="$1"
fi

cp ${CONFIGFILE} ${BACKUP_CONFIGFILE}
if [ "$1" == "keyfile" ]; then
  chmod 600 ${KEY_FILE}
  chown mongod:mongod ${KEY_FILE}
  for cipher in AES256-CBC AES256-GCM; do
    echo "===============================================" | tee -a ${LOG}
    echo "testing encryption with ${cipher} using keyfile" | tee -a ${LOG}
    echo "===============================================" | tee -a ${LOG}
    echo "preparing datadir for testing encryption with ${cipher}" | tee -a ${LOG}
    stop_service
    clean_datadir
    sed -i "/^  engine: /s/^/#/g" ${CONFIGFILE}
    engine="wiredTiger"
    sed -i "/engine: *${engine}/s/#//g" ${CONFIGFILE}
    if [ ${cipher} = "AES256-CBC" ]; then
      sed -i "s|#security:|security:\n  enableEncryption: true\n  encryptionCipherMode: ${cipher}\n  encryptionKeyFile: ${KEY_FILE}|" ${CONFIGFILE}
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
    elif [ "$(mongo --quiet --eval "db.serverCmdLineOpts().parsed.security.encryptionKeyFile" | tail -n1)" != "${KEY_FILE}" ]; then
      echo "ERROR: Encryption key file is not set to: ${KEY_FILE}" | tee -a ${LOG}
      exit 1
    fi
    echo "adding some data and indexes with cipher ${cipher}" | tee -a ${LOG}
    mongo localhost:27017/test --eval "for(i=1; i <= 100000; i++) { db.series.insert( { id: i, name: 'series'+i })}" >> ${LOG}
    mongo localhost:27017/test --eval "db.series.ensureIndex({ name: 1 })" >> ${LOG}
    echo "testing the hotbackup functionality with ${cipher}" | tee -a ${LOG}
    test_hotbackup
  done
fi

cp ${BACKUP_CONFIGFILE} ${CONFIGFILE}
if [ "$1" == "vault" ]; then
  chmod 600 ${TOKEN_FILE}
  chown mongod:mongod ${TOKEN_FILE}
  chmod 600 ${CA_FILE}
  chown mongod:mongod ${CA_FILE}

  for cipher in AES256-CBC AES256-GCM; do
    echo "=============================================" | tee -a ${LOG}
    echo "testing encryption with ${cipher} using vault" | tee -a ${LOG}
    echo "=============================================" | tee -a ${LOG}
    echo "preparing datadir for testing encryption with ${cipher}" | tee -a ${LOG}
    stop_service
    clean_datadir
    sed -i "/^  engine: /s/^/#/g" ${CONFIGFILE}
    engine="wiredTiger"
    sed -i "/engine: *${engine}/s/#//g" ${CONFIGFILE}
    if [ ${cipher} = "AES256-CBC" ]; then
      sed -i "s|#security:|security:\n  enableEncryption: true\n  encryptionCipherMode: ${cipher}\n  vault:\n    serverName: 10.30.6.213\n    port: 8200\n    tokenFile: ${TOKEN_FILE}\n    serverCAFile: ${CA_FILE}\n    secret: secret_v2/data/psmdb-test/package-test|" ${CONFIGFILE}
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
    elif [ "$(mongo --quiet --eval "db.serverCmdLineOpts().parsed.security.vault.serverName" | tail -n1)" != "10.30.6.213" ]; then
      echo "ERROR: Encryption vault server is not set to: 10.30.6.213" | tee -a ${LOG}
      exit 1
    fi
    echo "adding some data and indexes with cipher ${cipher}" | tee -a ${LOG}
    mongo localhost:27017/test --eval "for(i=1; i <= 100000; i++) { db.series.insert( { id: i, name: 'series'+i })}" >> ${LOG}
    mongo localhost:27017/test --eval "db.series.ensureIndex({ name: 1 })" >> ${LOG}
    echo "testing the hotbackup functionality with ${cipher}" | tee -a ${LOG}
    test_hotbackup
  done
fi
