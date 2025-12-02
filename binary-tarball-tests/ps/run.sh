#!/usr/bin/bash

set -x

export PATH=${HOME}/.local/bin:${PATH}
echo "FETCHING from /etc/environment"
source /etc/environment

echo "Installing dependencies..."

# ---------------------------------------------------------
#  Detect Amazon Linux 2023
# ---------------------------------------------------------
if grep -qiE 'platform:al2023|Amazon Linux 2023|ID="amzn"' /etc/os-release; then
  echo "Detected Amazon Linux 2023"

  sudo dnf install -y \
      openssl \
      libaio \
      numactl \
      tar \
      python3 \
      python3-pip

  # pytest dependencies
  pip3 install --user pytest-testinfra pytest

else
# ---------------------------------------------------------
#  RHEL / CentOS
# ---------------------------------------------------------
if [ -f /etc/redhat-release ]; then
  echo "Detected RedHat/CentOS"

  sudo yum install -y libaio numactl openssl tar
  sudo yum install -y perl-Data-Dumper

  if [ $(grep -c "release 6" /etc/redhat-release) -eq 1 ]; then
    sudo yum install -y epel-release centos-release-scl
    sudo yum install -y rh-python36 rh-python36-python-pip
    source /opt/rh/rh-python36/enable
  else
    sudo yum install -y python3 python3-pip
  fi

else
# ---------------------------------------------------------
#  Debian / Ubuntu
# ---------------------------------------------------------
  echo "Detected Debian/Ubuntu family"

  UCF_FORCE_CONFOLD=1 DEBIAN_FRONTEND=noninteractive sudo -E apt-get \
      -o Dpkg::Options::="--force-confdef" \
      -o Dpkg::Options::="--force-confold" \
      -qq -y install openssl

  if [[ $(lsb_release -sc) == "xenial" ]]; then
    DEBIAN_FRONTEND=noninteractive sudo add-apt-repository -y ppa:deadsnakes/ppa
    DEBIAN_FRONTEND=noninteractive sudo apt update
    DEBIAN_FRONTEND=noninteractive sudo apt -y install python3.6
    sudo rm /usr/bin/python3 && sudo ln -sf /usr/bin/python3.6 /usr/bin/python3
    wget -O get-pip.py "https://bootstrap.pypa.io/get-pip.py" && sudo python3 get-pip.py
  else
    sudo apt install -y python3 python3-pip
  fi

  sudo apt-get update -y
  sudo apt install -y libaio1 libnuma1 libldap-2.4-2 libaio-dev

fi
fi  # closes AL2023 + RHEL + Debian logic



# ---------------------------------------------------------
#  pip install (special case for Debian bookworm/noble)
# ---------------------------------------------------------
if command -v lsb_release >/dev/null 2>&1; then
  CODENAME=$(lsb_release -sc)
else
  CODENAME=""
fi

if [[ "$CODENAME" == "bookworm" || "$CODENAME" == "noble" || "$CODENAME" == "trixie" ]]; then
  pip3 install --user --break-system-packages pytest-testinfra pytest
else
  pip3 install --user pytest-testinfra pytest
fi


# ---------------------------------------------------------
#  PS_VERSION / PS_REVISION validation
# ---------------------------------------------------------
if [ -z "${PS_VERSION}" ]; then
  echo "PS_VERSION environment variable needs to be set!"
  echo "export PS_VERSION=\"8.0.17-8\""
fi

if [ -z "${PS_REVISION}" ]; then
  echo "PS_REVISION environment variable needs to be set!"
  echo "export PS_REVISION=\"868a4ef\""
fi


# ---------------------------------------------------------
#  BASE_DIR setup
# ---------------------------------------------------------
echo "non pro base dir setting.."
if [[ "$PRO" != "true" ]]; then
  echo "PRO IS NOT TRUE HERE!!!"
  TARBALL_NAME=$(basename "$(find . -maxdepth 1 -name '*.tar.gz'|head -n1)")
  if [ -z "${TARBALL_NAME}" ]; then
    echo "Please put PS tarball into this directory!"
    exit 1
  fi
  tar xf "${TARBALL_NAME}"
  PS_DIR_NAME=$(echo "${TARBALL_NAME}"|sed 's/.tar.gz$//'|sed 's/.deb$//'|sed 's/.rpm$//')
  export BASE_DIR="${PWD}/${PS_DIR_NAME}"
  echo "BASE_DIR is for non PRO $BASE_DIR"
else
  echo "PRO is TRUE HERE !!! base dir setting.."
  export BASE_DIR="/usr/percona-server"
  echo "BASE_DIR is for PRO $BASE_DIR"
fi

if [ -z "${BASE_DIR}" ]; then
  echo "BASE_DIR environment variable needs to be set!"
  exit 1
fi


# ---------------------------------------------------------
#  Run Tests
# ---------------------------------------------------------
echo "Running tests..."
python3 -m pytest -v --junit-xml report.xml $@
