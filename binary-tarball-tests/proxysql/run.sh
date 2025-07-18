#!/usr/bin/env bash
set -x
source /etc/environment

export BASE_DIR=${BASE_DIR}
#!/usr/bin/env bash
export PATH=${HOME}/.local/bin:${PATH}
export PROXYSQL_VERSION=${PROXYSQL_VERSION}
export WSREP_VERSION=${WSREP_VERSION}
export TARBALL_NAME=${TARBALL_NAME}

PROXYSQL_MAJOR_VERSION="$(echo ${PROXYSQL_VERSION}|cut -d'.' -f1,2)"

if grep -qi "Amazon Linux 2023" /etc/os-release; then
  OS_TYPE="al2023"
else
  OS_TYPE="other"
fi
echo "Detected OS: ${OS_TYPE}"
echo "Installing dependencies..."
if [ "$OS_TYPE" = "al2023" ]; then
  sudo dnf install -y libaio numactl openssl socat lsof libev python3 python3-pip
  
elif [ -f /etc/redhat-release ]; then
  sudo yum install -y libaio numactl openssl socat lsof
  # below needed for 5.6 mysql_install_db
  sudo yum install -y perl-Data-Dumper
  if [ $(grep -c "release 6" /etc/redhat-release) -eq 1 ]; then
    sudo ../../centos6.sh
    sudo yum install -y rh-python36 rh-python36-python-pip
    source /opt/rh/rh-python36/enable
  else
    sudo yum install -y python3 python3-pip
  fi
  sudo yum install -y libev
  if [ "${PROXYSQL_MAJOR_VERSION}" = "5.7" ]; then
    sudo yum install -y https://repo.percona.com/yum/percona-release-latest.noarch.rpm
    sudo percona-release enable pxb-24 testing
    sudo yum install -y percona-xtrabackup-24
  fi
else
  UCF_FORCE_CONFOLD=1 DEBIAN_FRONTEND=noninteractive sudo -E apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" -qq -y install openssl
  if [[ $(lsb_release -sc) == 'xenial' ]]; then
    DEBIAN_FRONTEND=noninteractive sudo add-apt-repository -y ppa:deadsnakes/ppa
    DEBIAN_FRONTEND=noninteractive sudo apt update
    DEBIAN_FRONTEND=noninteractive sudo apt -y install python3.6
    sudo rm /usr/bin/python3 && sudo ln -sf /usr/bin/python3.6 /usr/bin/python3
    wget -O get-pip.py "https://bootstrap.pypa.io/get-pip.py" && sudo python3 get-pip.py
    sudo apt install -y libcurl4-openssl-dev
  else
    sudo apt install -y python3 python3-pip
  fi
  sudo apt install -y python3 python3-pip libaio1 libnuma1 socat lsof curl libev4
  if [ "${PROXYSQL_MAJOR_VERSION}" = "5.7" ]; then
    wget -q https://repo.percona.com/apt/percona-release_latest.$(lsb_release -sc)_all.deb
    sudo dpkg -i percona-release_latest.$(lsb_release -sc)_all.deb
    sudo percona-release enable pxb-24 testing
    sudo apt update
    sudo apt-get install -y percona-xtrabackup-24
  fi
fi
if [[ $(lsb_release -sc) == 'bookworm' || $(lsb_release -sc) == 'noble' ]]; then
  pip3 install --user --break-system-packages pytest-testinfra pytest
else
  pip3 install --user pytest-testinfra pytest
fi

tar xf "${TARBALL_NAME}"
if [ ! -d "$BASE_DIR" ]; then
  echo "Error: Base directory $BASE_DIR does not exist!"
  exit 1
fi

cp conf/*.cnf "$BASE_DIR/"

echo "Running tests..."
python3 -m pytest --ignore="${PROXYSQL_DIR_NAME}"/percona-xtradb-cluster-tests -v --junit-xml report.xml $@

#PRO=$(echo ${PRO})
