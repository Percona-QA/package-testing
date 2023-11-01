#!/bin/bash
set -e

#install the clone plugin
mysql -e "INSTALL PLUGIN clone SONAME 'mysql_clone.so';"


# make sure clone plugin is active
CLONE_PLUGIN=$(mysql -e "SELECT PLUGIN_NAME, PLUGIN_STATUS FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME = 'clone';" | grep -c ACTIVE)

if [ ${CLONE_PLUGIN} == 1 ]; then
   echo "Clone plugin is installed and active"
else
   echo "ERROR: Clone plugin isn't installed or active"
   exit 1
fi

# run the clone command
mysql -e "CLONE LOCAL DATA DIRECTORY = '/tmp/bak';"
