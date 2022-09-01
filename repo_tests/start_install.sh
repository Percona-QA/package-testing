#!/bin/bash

########################################################################
# Created By Manish Chawla, Percona LLC                                #
# This script starts the installation of packages from percona repo    #
# Assumptions:                                                         #
# 1. Vagrant and virtual box are installed and running                 #
# 2. The machine has enough cpu and memory to create virtual machines  #
# Usage:                                                               #
# 1. Run the script as: ./start_install.sh                             #
# 2. Logs are available in: logdir                                     #
########################################################################

# Set script variables
export logdir="$HOME/install_logs"

log_date=$(date +"%d_%m_%Y_%M")
if [ ! -d ${logdir} ]; then
    mkdir ${logdir}
fi

echo "Starting install of packages on: Xenial"
vagrant up xenial | tee ${logdir}/install_log_xenial_${log_date}_log
if [ "$?" -ne 0 ]; then
    echo "ERR: Installation of packages failed on xenial. Please check the log at: ${logdir}/install_log_xenial_${log_date}_log"
else
    echo "Installation of packages was successful on xenial. Logs available at: ${logdir}/install_log_xenial_${log_date}_log"
fi
echo "Cleaning the xenial environment"
vagrant destroy xenial -f

echo "###################################################################################"

echo "Starting install of packages on: Centos7"
vagrant up centos7 | tee ${logdir}/install_log_centos7_${log_date}_log
if [ "$?" -ne 0 ]; then
    echo "ERR: Installation of packages failed on centos7. Please check the log at: ${logdir}/install_log_centos7_${log_date}_log"
else
    echo "Installation of packages was successful on centos7. Logs available at: ${logdir}/install_log_centos7_${log_date}_log"
fi
echo "Cleaning the centos7 environment"
vagrant destroy centos7 -f

echo "###################################################################################"
