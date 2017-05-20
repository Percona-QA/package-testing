#!/usr/bin/env bash
cp /package-testing/support-files/percona-dev.repo /etc/yum.repos.d/
rm -rf /etc/yum.repos.d/CentOS-Base.repo
yum install -y python-simplejson.x86_64 vim-enhanced
rpm -ivH /package-testing/support-files/epel-release-5-4.noarch.rpm
