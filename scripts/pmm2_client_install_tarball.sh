#!/bin/bash

############################################################
# Help                                                     #
############################################################
Help()
{
   echo "Custom PMM 2 Client installation script. To handle custom installations path and"
   echo "To handle custom installation path and port listening tests"
   echo
   echo "Syntax: scriptTemplate [-h|l|p]"
   echo "options:"
   echo "h     Print this Help."
   echo "l     listening custom port mode. Sets default version to 2.27.0"
   echo "p     Installation path. Default: /usr/local/percona/pmm2"
   echo "v     Installing specified version 2.XX.X"
   echo
}

### Variables
custom_path=/pmm2-client-custom-path
default_path=/usr/local/percona/pmm2

# custom path flag and installation are supported from 2.26.0
version=${PMM_VERSION:-2.26.0}
min_ver=$(echo $version | awk -F'.' '{print $2}')

############################################################
# Process the input options.                               #
############################################################
while getopts ":hvlp:" option; do
   case $option in
      h) # display Help
        Help
        exit 0
        ;;
        v) # Enter a version
          if [ -n "$OPTARG" ]
          then
            version=$OPTARG
            min_ver=$(echo $version | awk -F'.' '{print $2}')
          fi
          if [ $min_ver -le 26 ]
          then
            path=$default_path
          fi
          ;;
      l) # listening custom port starts from 2.27.0
        if [ $min_ver -le 27 ]
        then
          echo "listen-port is not available for versions earlier 2.27.0!"
          exit 1
        fi
        ;;
      p) # Enter a custom path
        if [ $min_ver -le 26 ]
        then
          echo "pmm2-client setup in custom folder is not available for versions earlier 2.26.0!"
          exit 1
        fi
        if [ -n "$OPTARG" ]
        then
          path=$OPTARG
        else
          path=$custom_path
        fi
        ;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit 1
         ;;
   esac
done

### Main program
tarball_url=https://downloads.percona.com/downloads/TESTING/pmm/pmm2-client-${version}.tar.gz
if [ -z "${path}" ];
  then
    path=$default_path
fi
echo "Downloading ${tarball_url}"
mkdir -p ./tmp/
wget ${tarball_url} -nv -P ./tmp/
tar -xvf ./tmp/pmm2-client-${version}.tar.gz -C ./tmp/
echo "Installing tarball to ${path}"
mkdir -p ${path}
export PMM_DIR=${path}
cd ./tmp/pmm2-client-${version}
./install_tarball
echo "PATH=$PMM_DIR/bin:$PATH" >> /etc/environment
cd ../../