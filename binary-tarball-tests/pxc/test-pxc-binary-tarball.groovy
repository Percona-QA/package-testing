pipeline {
  agent {
    label "micro-amazon"
    }
  parameters {
    string(name: 'PXC_VERSION', defaultValue: '8.0.30-22.1', description: 'PXC full version')
    string(name: 'PXC_REVISION', defaultValue: '167c5ac', description: 'PXC revision')
    string(name: 'WSREP_VERSION', defaultValue: '26.4.3', description: 'WSREP version')
    string(name: 'PXC57_PKG_VERSION', defaultValue: '5.7.33-rel36-49.1', description: 'PXC-5.7 package version')
    booleanParam( 
      defaultValue: false,
      name: 'BUILD_TYPE_MINIMAL'
    )
  }
  stages {
    stage('Binary tarball test') {
      parallel {
        stage('Ubuntu Focal') {
          agent {
            label "min-focal-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Ubuntu Focal
        stage('Ubuntu Jammy') {
          agent {
            label "min-jammy-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Ubuntu Jammy
        stage('Debian Buster') {
          agent {
            label "min-buster-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Debian Buster
        stage('Debian Bullseye') {
          agent {
            label "min-bullseye-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Debian Bullseye
        stage('Debian Bookworm') {
          agent {
            label "min-bookworm-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Debian Bookworm
        stage('Centos7') {
          agent {
            label "min-centos-7-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage CentOS7
        stage('Centos8') {
          agent {
            label "min-centos-8-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage CentOS8
        stage('Oracle Linux 9') {
          agent {
            label "min-ol-9-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
            run_test()
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage OracleLinux 9
       } //End parallel
    } //End stage Run tests
  } //End stages
} //End pipeline

void run_test() {
  sh '''
    echo ${BUILD_TYPE_MINIMAL}
    PXC_VERSION_MAJOR="$(echo ${PXC_VERSION}|cut -d'-' -f1)"
    PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
    MINIMAL=""
    if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
      MINIMAL="-minimal"
    fi
    if [ "${PXC_MAJOR_VERSION}" = "8.3" ] || [ "${PXC_MAJOR_VERSION}" = "8.4" ]; then
      export GLIBC_VERSION="2.17"
      if [ -f /usr/bin/apt-get ]; then
        DEBIAN_VERSION=$(lsb_release -sc)
        if [ ${DEBIAN_VERSION} = "jammy" ]; then
          export GLIBC_VERSION="2.35"
        fi
      fi
      TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc${GLIBC_VERSION}${MINIMAL}.tar.gz"
      TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION_MAJOR}/"
    elif [ "${PXC_MAJOR_VERSION}" = 5.7 ]; then
      export GLIBC_VERSION="2.17"
      if [ -f /etc/redhat-release ] && [ $(grep -c "release 6" /etc/redhat-release) -eq 1 ]; then
        export GLIBC_VERSION="2.12"
      fi
      TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc${GLIBC_VERSION}${MINIMAL}.tar.gz"
      TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION}/"
    fi
    rm -rf package-testing
    if [ -f /usr/bin/yum ]; then
      sudo yum install -y git wget tar
    else
      sudo apt install -y git wget tar
    fi
    git clone https://github.com/kaushikpuneet07/package-testing.git --branch pxc81-tar --depth 1
    cd package-testing/binary-tarball-tests/pxc
    wget -q ${TARBALL_LINK}${TARBALL_NAME}
    ./run.sh || true
  '''
}
