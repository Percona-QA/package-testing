#!/bin/bash

logfile=$1

if [ "$(egrep -c "WARNING" ${logfile})" != 0 ];then
        echo "WARNING: Warnings or Errors found in the installation logs:\n"
        egrep "WARNING" ${logfile}
        exit 1
else
        echo "Installation log is clean"
fi
