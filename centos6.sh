#!/bin/bash

cp $(dirname $0)/centos6-repos/centos6-eol.repo /etc/yum.repos.d/CentOS-Base.repo
cp $(dirname $0)/centos6-repos/centos6-epel-eol.repo /etc/yum.repos.d/epel.repo
yum -y install centos-release-scl
cp $(dirname $0)/centos6-repos/centos6-scl-eol.repo /etc/yum.repos.d/CentOS-SCLo-scl.repo
cp $(dirname $0)/centos6-repos/centos6-scl-rh-eol.repo /etc/yum.repos.d/CentOS-SCLo-scl-rh.repo
yum -y install epel-release.noarch
