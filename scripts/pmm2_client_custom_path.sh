#!/bin/bash

VERSION=${PMM_VERSION:-2.26.0}
path=/pmm2-client-custom-path

# Get the options
while getopts ":hn:" option; do
   case $option in
      p) # Enter a custom path
         path=$OPTARG;;
      port) # custom port starts rom 2.27
         VERSION=${PMM_VERSION:-2.27.0};;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done


wget https://downloads.percona.com/downloads/TESTING/pmm/pmm2-client-${VERSION}.tar.gz
tar -xvf pmm2-client-${VERSION}.tar.gz
pushd /
mkdir -p ${path}
pushd ${path}
export PMM_DIR=$(pwd)
popd
popd
mv pmm2-client-${VERSION} pmm2-client
cd pmm2-client
./install_tarball
