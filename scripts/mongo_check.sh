#!/bin/bash

#checking data after upgrade
if [ "$(mongo < /package-testing/scripts/mongo_check.js | grep -c 14Q3)" -eq 3 ]; then
	echo "data is here"
else 
	echo "data is inconsistent and/or missing after upgrade"
	exit 1
fi
