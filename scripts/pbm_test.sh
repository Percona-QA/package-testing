#/usr/bin/env bash
set -e

if [ $(pbmctl list storage 2>&1|grep -c "local-filesystem") != "1" ]; then
  exit "PBM storage is not defined correctly!"
fi

if [ $(pbmctl list nodes 2>&1|grep -c "127.0.0.1:27017") != "1" ]; then
  exit "MongoDB instance is not visible in PBM list nodes!"
fi

# insert data
mongo --quiet --eval 'for(i=1; i <= 100000; i++) { db.test.insert( {_id: i, name: "Test_"+i })}' test

# save dbHash
DBHASH_BEFORE=$(mongo --quiet --eval 'db.runCommand({ dbHash: 1 }).md5' test|tail -n1)

# create backup and store backup name
pbmctl run backup --description="backup1" --storage=local-filesystem
BACKUP_NAME=$(pbmctl list backups 2>&1|grep "backup1"|sed 's/\.json.*/.json/'|tail -n1)

# drop data and check documents don't exist
mongo --quiet --eval 'db.dropDatabase()' test
if [ "$(mongo --quiet --eval 'db.test.count()' test|tail -n1)" != "0" ]; then
  echo "Document count in db.test.test is not: 0 !"
  exit 1
fi

# do restore
pbmctl run restore --storage=local-filesystem ${BACKUP_NAME}

# check dbHash is the same and document count is ok
DBHASH_AFTER=$(mongo --quiet --eval 'db.runCommand({ dbHash: 1 }).md5' test|tail -n1)
if [ "${DBHASH_BEFORE}" != "${DBHASH_AFTER}" ]; then
  echo "DB hash after restore is not the same as before!"
fi
if [ "$(mongo --quiet --eval 'db.test.count()' test|tail -n1)" != "100000" ]; then
  echo "Document count in db.test.test is not: 100000 !"
  exit 1
fi

echo "PBM tests look OK!"
