#!/bin/bash
set -e
mysql -e "CREATE DATABASE world;"
pv /home/vagrant/world_innodb.sql | mysql -D world
