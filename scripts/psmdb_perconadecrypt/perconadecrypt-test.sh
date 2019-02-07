#!/usr/bin/env bash

ROLLBACK_DIR="/package-testing/scripts/psmdb_perconadecrypt"
KEY_FILE="/package-testing/scripts/mongodb-keyfile"

if [ -z "$1" ]; then
  echo "This script needs parameter 3.6|4.0"
  exit 1
elif [ "$1" != "3.6" -a "$1" != "4.0" ]; then
  echo "Version not recognized!"
  exit 1
else
  VERSION="$1"
fi

set -e

if [ ${VERSION} == "3.6" ]; then
  # 3.6 CBC
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-CBC --inputPath ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/36-cbc
  md5sum -c ${ROLLBACK_DIR}/36-cbc/ycsb_test.usertable.2019-02-07T17-26-07.0.bson.aes256-cbc-json.md5
  popd

  # 3.6 GCM
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-GCM --inputPath ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/36-gcm
  md5sum -c ${ROLLBACK_DIR}/36-gcm/ycsb_test.usertable.2019-02-07T17-31-46.0.bson.aes256-gcm-json.md5
  popd
fi

if [ ${VERSION} == "4.0" ]; then
  # 4.0 CBC
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-CBC --inputPath ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc --outputPath ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-decrypted --outFile ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json

  pushd ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/40-cbc/ycsb_test.usertable/removed.2019-02-07T17-41-17.0.bson.aes256-cbc-json.md5
  popd

  # 4.0 GCM
  perconadecrypt --encryptionKeyFile ${KEY_FILE} --encryptionCipherMode AES256-GCM --inputPath ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm --outputPath ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted

  bsondump --bsonFile ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-decrypted --outFile ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json

  pushd ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable
  md5sum -c ${ROLLBACK_DIR}/40-gcm/ycsb_test.usertable/removed.2019-02-07T17-44-42.0.bson.aes256-gcm-json.md5
  popd
fi
