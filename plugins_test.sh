#!/bin/bash
mysql -e "CREATE FUNCTION fnv1a_64 RETURNS INTEGER SONAME 'libfnv1a_udf.so'"
mysql -e "CREATE FUNCTION fnv_64 RETURNS INTEGER SONAME 'libfnv_udf.so'"
mysql -e "CREATE FUNCTION murmur_hash RETURNS INTEGER SONAME 'libmurmur_udf.so'"
mysql -e "CREATE DATABASE world;"
mysql -e "CREATE DATABASE sbt;"
mysql -e "CREATE DATABASE sb;"
sed -i '18,21 s/^/-- /' /package-testing/world.sql
pv /package-testing/world.sql | mysql -D world
