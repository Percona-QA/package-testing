#!/bin/bash


#!/usr/bin/env bash

while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
   fi

  shift
done


if [ -z "$custom_path" ]; then
    export custom_path=/pmm2-client-custom-path
fi
echo "Custom Path for Binaries is $custom_path"
export client_version=$(pmm-admin status | grep 'Version:' | awk -F' ' '{print $2}')

### Main program
wget https://downloads.percona.com/downloads/TESTING/pmm/pmm2-client-${client_version}.tar.gz
tar -xvf pmm2-client-${client_version}.tar.gz
export PMM_DIR=${custom_path}
cd pmm2-client-${client_version}
./install_tarball
