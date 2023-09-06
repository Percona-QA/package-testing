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

#install the data masking plugin
mysql -e "INSTALL PLUGIN data_masking SONAME 'data_masking.so';"

# make sure DM plugin is active
DM_PLUGIN=$(mysql -e "SELECT PLUGIN_NAME, PLUGIN_STATUS FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME = 'data_masking';" | grep -c ACTIVE)

if [ ${DM_PLUGIN} == 1 ]; then
   echo "DM plugin is installed and active"
else
   echo "ERROR: DM plugin isn't installed or active"
   exit 1
fi

#use the Data Masking functions

mysql -e "SELECT mask_inner('This is a string', 5, 1);"
mysql -e "SELECT mask_inner('This is a string', 1, 5);"
mysql -e "SELECT mask_outer('This is a string', 5, 1);"
mysql -e "SELECT mask_outer('This is a string', 1, 5);"
mysql -e "SELECT mask_inner('This is a string', 5, 1, '*');"
mysql -e "SELECT mask_outer('This is a string', 5, 1, '#');"
mysql -e "SELECT mask_pan(gen_rnd_pan());"
mysql -e "SELECT mask_pan_relaxed(gen_rnd_pan());"
mysql -e "SELECT mask_ssn(gen_rnd_ssn());"
mysql -e "SELECT gen_range(1, 10);"
mysql -e "SELECT gen_rnd_email();"
mysql -e "SELECT gen_rnd_pan();"
mysql -e "SELECT gen_rnd_ssn();"
mysql -e "SELECT gen_rnd_us_phone();"

# Disable Data Masking plugin
mysql -e "UNINSTALL PLUGIN data_masking';
