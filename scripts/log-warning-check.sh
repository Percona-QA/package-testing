#!/bin/bash

logfile=$1

if [ "$(egrep -c "WARNING" ${logfile})" != 0 ];then
        echo "!!! WARNING Detected !!!"
        exit 1
else
        echo "Installation log is clean"
fi

