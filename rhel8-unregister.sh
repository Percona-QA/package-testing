#!/usr/bin/env bash
if [ -f /etc/redhat-release ] && [ "$(grep -c Red /etc/redhat-release)" == 1 ]; then
  echo "This is RHEL8 - unregisterring"
  subscription-manager unregister
  subscription-manager clean
else
  echo "Not RHEL; nothing to do here"
fi
