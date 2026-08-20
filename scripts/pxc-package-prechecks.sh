#!/bin/bash
set -e

compare_versions() {
    local version1="$1"
    local version2="$2"

    if [[ "$version1" == "$version2" ]]; then
        result=0
    fi

    local IFS='.'
    local version1_parts=($version1)
    local version2_parts=($version2)

    # Compare each part of the version numbers
    local max_parts=$(( ${#version1_parts[@]} > ${#version2_parts[@]} ? ${#version1_parts[@]} : ${#version2_parts[@]} ))
    for ((i = 0; i < max_parts; i++)); do
        local part1="${version1_parts[i]:-0}"
        local part2="${version2_parts[i]:-0}"

        if (( part1 > part2 )); then
            result=1
        elif (( part1 < part2 )); then
            result=2
        fi
    done


if [ "$result" -eq 0 ] || [ "$result" -eq 1 ]; then
    return 1
else
    return 0
fi
}






if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps56, ps57, ps80, ps81 or PS82 !"
  echo "Usage: ./package_check.sh <prod>"
  exit 1
fi

SCRIPT_PWD=$(cd `dirname $0` && pwd)

function check_xb_file(){
        if [[ -f /usr/bin/pxc_extra/pxb-$1/bin/xtrabackup ]]; then
            return 1
        else
            return 0
        fi
}


if [[ $1 =~ ^pxc8[1-9]{1}$ ]]; then
  echo "Proper PXC VERSION"

else
  echo "Illegal product selected!"
  exit 1
fi


if [[ $1 =~ ^pxc8[0-9]{1}$ ]]; then
  if [ -f /usr/bin/wsrep_sst_xtrabackup-v2 ]; then
    echo "File exists: /usr/bin/wsrep_sst_xtrabackup-v2"

    pxc_version=$(mysqld --version  | grep Ver | awk '{print$3}')
    pxc_version_trimmed=$(echo $pxc_version | grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
    pxc_version_trimmed_major_version=$( echo $pxc_version_trimmed | grep -o -E '[0-9]+\.[0-9]+')  

    xb_this_required_version=$(grep "XB_THIS_REQUIRED_VERSION=" /usr/bin/wsrep_sst_xtrabackup-v2 | cut -d "=" -f 2 | sed 's/"//g')
    xb_this_required_version_trimmed=$(echo $xb_this_required_version |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
    xb_this_required_version_trimmed_major_version=$(echo $xb_this_required_version_trimmed |  grep -o -E '[0-9]+\.[0-9]+')  

    xb_prev_required_version=$(grep "XB_PREV_REQUIRED_VERSION=" /usr/bin/wsrep_sst_xtrabackup-v2 | cut -d "=" -f 2 | sed 's/"//g')
    xb_prev_required_version_trimmed=$(echo $xb_prev_required_version |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
    xb_prev_required_version_trimmed_major_version=$(echo $xb_prev_required_version_trimmed |  grep -o -E '[0-9]+\.[0-9]+')  

    xb_prev_lts_required_version=$(grep "XB_PREV_LTS_REQUIRED_VERSION=" /usr/bin/wsrep_sst_xtrabackup-v2 | cut -d "=" -f 2 | sed 's/"//g')
    xb_prev_lts_required_version_trimmed=$(echo $xb_prev_lts_required_version |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
    xb_prev_lts_required_version_trimmed_major_version=$(echo $xb_prev_lts_required_version_trimmed |  grep -o -E '[0-9]+\.[0-9]+')  


    if [[ $1 == "pxc81" ]]; then
        echo "PXC81, Modding configs for one time"
        sed -i "s/XB_PREV_REQUIRED_VERSION=\"$xb_prev_required_version\"/XB_PREV_REQUIRED_VERSION=8.0.34/g" /usr/bin/wsrep_sst_xtrabackup-v2
        sed -i "s/XB_PREV_LTS_REQUIRED_VERSION=\"$xb_prev_lts_required_version\"/XB_PREV_LTS_REQUIRED_VERSION=8.0.34/g" /usr/bin/wsrep_sst_xtrabackup-v2

        xb_prev_required_version=$(grep "XB_PREV_REQUIRED_VERSION=" /usr/bin/wsrep_sst_xtrabackup-v2 | cut -d "=" -f 2 | sed 's/"//g')
        xb_prev_required_version_trimmed=$(echo $xb_prev_required_version |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
        xb_prev_required_version_trimmed_major_version=$(echo $xb_prev_required_version_trimmed |  grep -o -E '[0-9]+\.[0-9]+')  

        xb_prev_lts_required_version=$(grep "XB_PREV_LTS_REQUIRED_VERSION=" /usr/bin/wsrep_sst_xtrabackup-v2 | cut -d "=" -f 2 | sed 's/"//g')
        xb_prev_lts_required_version_trimmed=$(echo $xb_prev_lts_required_version |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
        xb_prev_lts_required_version_trimmed_major_version=$(echo $xb_prev_lts_required_version_trimmed |  grep -o -E '[0-9]+\.[0-9]+')  
    else
        echo "Not PXC81"
    fi

        # 1. Checking for the xb_this_required_version 

        if [[ $(check_xb_file $xb_this_required_version_trimmed_major_version ; echo $?) -eq 1 ]]; then
            pxc_extras_xtrabackup_version_this_required=$(/usr/bin/pxc_extra/pxb-$xb_this_required_version_trimmed_major_version/bin/xtrabackup -v |& grep -oP '(?<=xtrabackup version ).*' | awk '{print$1}')
            pxc_extras_xtrabackup_version_this_required_trimmed=$( echo $pxc_extras_xtrabackup_version_this_required |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
            echo "File exists.. for $xb_this_required_version_trimmed_major_version"

            if [[ $pxc_extras_xtrabackup_version_this_required_trimmed == $xb_this_required_version_trimmed ]]; then
            
                echo "The xtrabackup version is the same as the required version xb_this_required_version_trimmed"
            else
                echo "The xtrabackup version is not the same as the required version xb_this_required_version_trimmed"
                exit 1
            fi
        else
            echo "Failure The xtrabackup file does not exist major version"
            exit 1
        fi

        # 2. Checking for the xb_prev_required_version 

        echo "XB CHECK!! xb_prev_required_version"
        if [[ $(check_xb_file $xb_prev_required_version_trimmed_major_version ; echo $?) -eq 1 ]]; then
            pxc_extras_xtrabackup_prev_required_version=$(/usr/bin/pxc_extra/pxb-$xb_prev_required_version_trimmed_major_version/bin/xtrabackup -v |& grep -oP '(?<=xtrabackup version ).*' | awk '{print$1}')
            pxc_extras_xtrabackup_prev_required_version_trimmed=$( echo $pxc_extras_xtrabackup_prev_required_version |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
            echo "File exists.. for $pxc_extras_xtrabackup_prev_required_version_trimmed and value for xb_prev_required_version_trimmed is $xb_prev_required_version_trimmed"

            if [[ $(compare_versions $pxc_extras_xtrabackup_prev_required_version_trimmed $xb_prev_required_version_trimmed ; echo $?) -eq 1 ]]; then
                echo "The xtrabackup version is the same as the required version xb_prev_required_version_trimmed"
            else
                echo "The xtrabackup version is not the same as the required version xb_prev_required_version_trimmed"
                exit 1
            fi

        else
            echo "Failure The xtrabackup file does not exist major version"
            exit 1
        fi

        # 3. Checking for the xb_prev_lts_required_version 

        echo "XB CHECK!! xb_prev_lts_required_version"
        if [[ $(check_xb_file $xb_prev_lts_required_version_trimmed_major_version ; echo $?) -eq 1 ]]; then
            pxc_extras_xtrabackup_version_this_required=$(/usr/bin/pxc_extra/pxb-$xb_prev_lts_required_version_trimmed_major_version/bin/xtrabackup -v |& grep -oP '(?<=xtrabackup version ).*' | awk '{print$1}')
            pxc_extras_xtrabackup_version_this_required_trimmed=$( echo $pxc_extras_xtrabackup_version_this_required |  grep -o -E '[0-9]+\.[0-9]+\.[0-9]+')  
            echo "File exists.. for $pxc_extras_xtrabackup_version_this_required_trimmed"
            
            if [[ $(compare_versions $pxc_extras_xtrabackup_version_this_required_trimmed $xb_prev_lts_required_version_trimmed ; echo $?) -eq 1 ]]; then
                echo "The xtrabackup version is the same as the required version xb_prev_lts_required_version_trimmed"
            else
                echo "The xtrabackup version is not the same as the required version xb_prev_lts_required_version_trimmed"
                exit 1
            fi


        else
            echo "Failure The xtrabackup file does not exist major version"
            exit 1
        fi

   else
    echo "The files do not exist ERRORR!"
    exit 1
   fi 
else
    echo "Illegal product selected!"
    exit 1
fi


echo "All checks passed successfully!"
