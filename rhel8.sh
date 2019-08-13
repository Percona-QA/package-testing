#!/bin/bash
# This scripts preps the rhel8 box to be handled with ansible

if [ -f /etc/redhat-release ] && [ "$(grep -c Red /etc/redhat-release)" == 1 ]; then
  echo "This is RHEL8"
  subscription-manager register --username=$RHEL_EMAIL --password=$RHEL_PASSWORD --auto-attach
  curl -o /etc/yum.repos.d/percona-dev.repo https://jenkins.percona.com/yum-repo/rhel8/rhel8-beta.repo
  yum install python3 python3-dnf -y
  ln -s /usr/bin/python3 /usr/bin/python
else
  echo "Not RHEL; nothing to do here"
fi
