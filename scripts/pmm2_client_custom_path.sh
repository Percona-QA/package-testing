#!/bin/bash

while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare $param="$2"
   fi

  shift
done

############################################################
# Help                                                     #
############################################################
Help()
{
   echo "Custom PMM 2 Client installation script."
   echo
   echo "Syntax: scriptTemplate [-h|l|p]"
   echo "options:"
   echo "h     Print this Help."
   echo "l     listening custom port mode. Sets default version to 2.27.0"
   echo "p     Installation path. Default: /pmm2-client-custom-path"
   echo
}

if [ -z "$version" ]; then
    export version=${PMM_VERSION:-2.27.0}
fi

### Variables
custom_path=/pmm2-client-custom-path

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
        if [ -z "$version" ]; then
          export version=${PMM_VERSION:-2.27.0}
        fi
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
