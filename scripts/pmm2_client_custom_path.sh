#!/bin/bash

############################################################
# Help                                                     #
############################################################
Help()
{
   echo "Custom PMM 2 Client instalation script."
   echo
   echo "Syntax: scriptTemplate [-h|l|p]"
   echo "options:"
   echo "h     Print this Help."
   echo "l     listening custom port mode. Sets default version to 2.27.0"
   echo "p     Installation path. Default: /pmm2-client-custom-path"
   echo
}

### Variables
custom_path=/pmm2-client-custom-path
version=${PMM_VERSION:-2.26.0}

############################################################
# Process the input options.                               #
############################################################
while getopts ":hlp:" option; do
   case $option in
      h) # display Help
        Help
        exit 0
        ;;
      l) # listening custom port  starts from 2.27
        version=${PMM_VERSION:-2.27.0}
        ;;
      p) # Enter a custom path
        path=$OPTARG
        ;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit 1
         ;;
   esac
done

### Main program
wget https://downloads.percona.com/downloads/TESTING/pmm/pmm2-client-${version}.tar.gz
tar -xvf pmm2-client-${version}.tar.gz
pushd /
mkdir -p ${custom_path}
pushd ${custom_path}
export PMM_DIR=$(pwd)
popd
popd
mv pmm2-client-${version} pmm2-client
cd pmm2-client
./install_tarball
