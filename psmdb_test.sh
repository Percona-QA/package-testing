#!/bin/bash

log="/tmp/psmdb_run.log"
echo -n > /tmp/psmdb_run.log

set -e

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
	else
        	echo "starting mongod service... "
		service mongod start
	fi
	echo "waiting 5s for service to boot up"
	sleep 5
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
	else
        	echo "stopping mongod service... "
		service mongod stop
	fi
	echo "waiting 10s for service to stop"
	sleep 10
}

function list_data {
	if [ -f /etc/redhat-release ]; then
		echo "$(date +%Y%m%d%H%M%S): contents of the mongo data dir: " >> $log
		ls /var/lib/mongo/ >> $log
	else
		echo "$(date +%Y%m%d%H%M%S): contents of the mongodb data dir: " >> $log
		ls /var/lib/mongodb/ >> $log
	fi
}

function clean_datadir {
	if [ -f /etc/redhat-release ]; then
		echo "removing the data files (on rhel distros)..."
		rm -rf /var/lib/mongo/*
	else
		echo "removing the data files (on debian distros)..."
		rm -rf /var/lib/mongodb/*
	fi
}

function test_hotbackup {
	rm -rf /tmp/backup
	mkdir -p /tmp/backup
	BACKUP_RET=$(mongo admin --eval 'db.runCommand({createBackup: 1, backupDir: "/tmp/backup"})'|grep -c '"ok" : 1')
	rm -rf /tmp/backup
	if [ ${BACKUP_RET} = 0 ]; then
		echo "Backup failed for storage engine: ${engine}"
		exit 1
	fi
}

for engine in mmapv1 PerconaFT rocksdb wiredTiger; do
	stop_service
	clean_datadir
	sed -i "/engine: *${engine}/s/#//g" /etc/mongod.conf
	echo "testing ${engine}" | tee -a $log
	start_service
	echo "importing the sample data"
	mongo < /package-testing/mongo_insert.js >> $log
	list_data >> $log
	echo "testing the hotbackup functionality"
	if [ ${engine} = "wiredTiger" -o ${engine} = "rocksdb" ]; then
		test_hotbackup
	fi
	stop_service
	echo "disable ${engine}"
	sed -i "/engine: *${engine}/s//#engine: ${engine}/g" /etc/mongod.conf
	clean_datadir
done
