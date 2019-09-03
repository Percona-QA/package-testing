#!/usr/bin/env bash

ROLLBACK_DIR="/package-testing/scripts/psmdb_encryption"
KEY_FILE="${ROLLBACK_DIR}/mongodb-keyfile"
TOKEN_FILE="${ROLLBACK_DIR}/mongodb-test-vault-token"
CA_FILE="${ROLLBACK_DIR}/test.cer"
VAULT_SECRET="secret_v2/data/psmdb-test/perconadecrypt-test"

if [ -z "$1" ]; then
  echo "This script needs parameter 3.6|4.0|4.2 and keyfile|vault"
  exit 1
elif [ "$1" != "3.6" -a "$1" != "4.0" -a "$1" != "4.2" ]; then
  echo "Version not recognized!"
  exit 1
elif [ "$2" != "keyfile" -a "$2" != "vault" ]; then
  echo "key store not recognized!"
  exit 1
else
  VERSION="$1"
  KEY_STORE="$2"
fi

set -e
chmod 600 ${KEY_FILE}
chown mongod:mongod ${KEY_FILE}
chmod 600 ${TOKEN_FILE}
chown mongod:mongod ${TOKEN_FILE}
chmod 600 ${CA_FILE}
chown mongod:mongod ${CA_FILE}

if [ "${VERSION}" == "3.6" -a "${KEY_STORE}" == "keyfile" ]; then
  # 3.6 CBC
  rm -f ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted
  rm -f ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-CBC --inputPath ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/36-cbc
  md5sum -c ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json.md5
  popd

  # 3.6 GCM
  rm -f ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted
  rm -f ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-GCM --inputPath ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/36-gcm
  md5sum -c ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json.md5
  popd
fi

if [ "${VERSION}" == "3.6" -a "${KEY_STORE}" == "vault" ]; then
  # 3.6 CBC
  rm -f ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted
  rm -f ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json
  perconadecrypt --encryptionCipherMode AES256-CBC --vaultServerName 10.30.6.213 --vaultPort 8200 --vaultTokenFile ${TOKEN_FILE} --vaultSecret ${VAULT_SECRET} --vaultServerCAFile ${CA_FILE} --inputPath ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/36-cbc
  md5sum -c ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json.md5
  popd

  # 3.6 GCM
  rm -f ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted
  rm -f ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json
  perconadecrypt --encryptionCipherMode AES256-GCM --vaultServerName 10.30.6.213 --vaultPort 8200 --vaultTokenFile ${TOKEN_FILE} --vaultSecret ${VAULT_SECRET} --vaultServerCAFile ${CA_FILE} --inputPath ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/36-gcm
  md5sum -c ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json.md5
  popd
fi

if [ "${VERSION}" == "4.0" -a "${KEY_STORE}" == "keyfile" ]; then
  # 4.0 CBC
  rm -f ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted
  rm -f ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-CBC --inputPath ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json.md5
  popd

  # 4.0 GCM
  rm -f ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted
  rm -f ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-GCM --inputPath ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json.md5
  popd
fi

if [ "${VERSION}" == "4.0" -a "${KEY_STORE}" == "vault" ]; then
  # 4.0 CBC
  rm -f ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted
  rm -f ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json
  perconadecrypt --encryptionCipherMode AES256-CBC --vaultServerName 10.30.6.213 --vaultPort 8200 --vaultTokenFile ${TOKEN_FILE} --vaultSecret ${VAULT_SECRET} --vaultServerCAFile ${CA_FILE} --inputPath ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json.md5
  popd

  # 4.0 GCM
  rm -f ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted
  rm -f ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json
  perconadecrypt --encryptionCipherMode AES256-GCM --vaultServerName 10.30.6.213 --vaultPort 8200 --vaultTokenFile ${TOKEN_FILE} --vaultSecret ${VAULT_SECRET} --vaultServerCAFile ${CA_FILE} --inputPath ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json.md5
  popd
fi

if [ "${VERSION}" == "4.2" -a "${KEY_STORE}" == "keyfile" ]; then
  # 4.2 CBC
  rm -f ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-decrypted
  rm -f ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-json
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-CBC --inputPath ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-json.md5
  popd

  # 4.2 GCM
  rm -f ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-decrypted
  rm -f ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-json
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-GCM --inputPath ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-json.md5
  popd
fi

if [ "${VERSION}" == "4.2" -a "${KEY_STORE}" == "vault" ]; then
  # 4.2 CBC
  rm -f ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-decrypted
  rm -f ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-json
  perconadecrypt --encryptionCipherMode AES256-CBC --vaultServerName 10.30.6.213 --vaultPort 8200 --vaultTokenFile ${TOKEN_FILE} --vaultSecret ${VAULT_SECRET} --vaultServerCAFile ${CA_FILE} --inputPath ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/42-cbc/ycsb_test.usertable/removed.2019-09-03T06-33-05.0.bson.aes256-cbc-json.md5
  popd

  # 4.2 GCM
  rm -f ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-decrypted
  rm -f ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-json
  perconadecrypt --encryptionCipherMode AES256-GCM --vaultServerName 10.30.6.213 --vaultPort 8200 --vaultTokenFile ${TOKEN_FILE} --vaultSecret ${VAULT_SECRET} --vaultServerCAFile ${CA_FILE} --inputPath ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/42-gcm/ycsb_test.usertable/removed.2019-09-03T08-03-44.0.bson.aes256-gcm-json.md5
  popd
fi
