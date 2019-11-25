#!/usr/bin/env bash
export PATH=${HOME}/.local/bin:${PATH}

echo "Installing dependencies..."
if [ -f /etc/redhat-release ]; then
  sudo yum install -y libaio numactl openssl
  if [ $(grep -c "release 6" /etc/redhat-release) -eq 1 ]; then
    sudo yum install -y epel-release centos-release-scl
    sudo yum install -y rh-python36 rh-python36-python-pip
    source /opt/rh/rh-python36/enable
  else
    sudo yum install -y python3 python3-pip
  fi
else
  UCF_FORCE_CONFOLD=1 DEBIAN_FRONTEND=noninteractive sudo -E apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" -qq -y install openssl
  sudo apt install -y python3 python3-pip libaio1 libnuma1
fi
pip3 install --user testinfra pytest

TARBALL_NAME=$(basename "$(find . -maxdepth 1 -name '*.tar.gz'|head -n1)")
if [ -z "${TARBALL_NAME}" ]; then
  echo "Please put PS tarball into this directory!"
  exit 1
fi
if [ -z "${PS_VERSION}" ]; then
  echo "PS_VERSION environment variable needs to be set!"
  echo "export PS_VERSION=\"8.0.17-8\""
fi
if [ -z "${PS_REVISION}" ]; then
  echo "PS_REVISION environment variable needs to be set!"
  echo "export PS_REVISION=\"868a4ef\""
fi
tar xf "${TARBALL_NAME}"
PS_DIR_NAME=$(echo "${TARBALL_NAME}"|sed 's/.tar.gz$//'|sed 's/.deb$//'|sed 's/.rpm$//')
export BASE_DIR="${PWD}/${PS_DIR_NAME}"

echo "Running tests..."
python3 -m pytest -v --junit-xml report.xml $@
