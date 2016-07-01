#!/bin/bash
set -e
mysql -e "CREATE FUNCTION fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so'"
mysql -e "CREATE FUNCTION fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so'"
mysql -e "CREATE FUNCTION murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so'"
mysql -e "INSTALL PLUGIN auth_pam SONAME 'auth_pam.so';"
mysql -e "INSTALL PLUGIN audit_log SONAME 'audit_log.so';"
mysql -e "INSTALL PLUGIN handlersocket SONAME 'handlersocket.so';"
mysql -e "SHOW PLUGINS;"
mysql -e "CREATE DATABASE world;"
pv /package-testing/world.sql | mysql -D world
