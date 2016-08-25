#!/bin/bash

log="/tmp/psmdb_run.log"
echo -n > /tmp/psmdb_run.log

set -e

function start_service {
	if [ "$(lsb_release -sc)" = "trusty" ]; then
        	echo "starting mongod service on trusty..."
		/etc/init.d/mongod start
	else
        	echo "starting mongod service... "
		service mongod start
	fi
	echo "waiting 5s for service to boot up"
	sleep 5
}

function stop_service {
	if [ "$(lsb_release -sc)" = "trusty" ]; then
        	echo "stopping mongod service on trusty..."
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

for engine in mmapv1 PerconaFT rocksdb wiredTiger; do
	stop_service
	clean_datadir
	sed -i "/engine: *${engine}/s/#//g" /etc/mongod.conf
	echo "testing ${engine}" | tee -a $log
	start_service
	echo "importing the sample data"
	mongo < /package-testing/mongo_insert.js >> $log
	list_data >> $log
	stop_service
	echo "disable ${engine}"
	sed -i "/engine: *${engine}/s//#engine: ${engine}/g" /etc/mongod.conf
	clean_datadir
done
