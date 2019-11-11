#!/bin/bash

echo "check that plugins are available"

GR_PLUGIN=$(mysql -e "SELECT PLUGIN_NAME, PLUGIN_STATUS FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME = 'group_replication';" | grep -c ACTIVE)

if [ ${GR_PLUGIN} == 1 ]; then
   echo "Group Replication plugin is installed and active"
else
   echo "ERROR: GR plugin isn't installed or active"
   exit 1
fi

# initialize and start the GR
mysql -e "SET GLOBAL group_replication_bootstrap_group=ON;"
mysql -e "START GROUP_REPLICATION;"

# wait for GR to initialize 
sleep 5

# check that the member is on-line
GR_STATUS=$(mysql -e "SELECT MEMBER_STATE FROM performance_schema.replication_group_members;" | grep -c ONLINE)


if [ ${GR_STATUS} == 1 ]; then
   echo "Group Replication member is online"
else
   echo "ERROR: GR MEMBER isn't ONLINE or ACTIVE"
   exit 1
fi


