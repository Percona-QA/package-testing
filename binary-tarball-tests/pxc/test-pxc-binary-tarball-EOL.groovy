pipeline {
  agent {
    label "micro-amazon"
    }
  parameters {
    string(name: 'PXC_VERSION', defaultValue: '5.7.44.3', description: 'PXC full version')
    string(name: 'PXC_REVISION', defaultValue: 'd328acc', description: 'PXC revision')
    string(name: 'WSREP_VERSION', defaultValue: '31.65', description: 'WSREP version')
    string(name: 'PXC57_PKG_VERSION', defaultValue: '5.7.44-rel50-65.3', description: 'PXC-5.7 package version')
    choice(name: 'REPO', choices: ['testing', 'main'], description: 'Choose repository: testing or main')
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
            withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
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
             withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
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
             withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
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
             withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
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
             withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
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
             withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage CentOS7
        stage('Oracle Linux 8') {
          agent {
            label "min-ol-8-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
              }
             withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
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
             withCredentials([usernamePassword(credentialsId: 'PS_PRIVATE_REPO_ACCESS', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              run_test()
            }
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
    MINIMAL=""
    if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
      MINIMAL="-minimal"
    fi
    export GLIBC_VERSION="2.17"
    if [ -f /usr/bin/apt-get ]; then
      DEBIAN_VERSION=$(lsb_release -sc)
      if [ ${DEBIAN_VERSION} = "jammy" ]; then
        export GLIBC_VERSION="2.35"
      fi
    fi
    TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc${GLIBC_VERSION}${MINIMAL}.tar.gz"
    if [ "${REPO}" = "main" ]; then
        TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/pxc-57-eol/tarballs/Percona-XtraDB-Cluster-${PXC_VERSION}/"
    else
        TARBALL_LINK="https://repo.percona.com/private/${USERNAME}-${PASSWORD}/qa-test/pxc-gated-${PXC_VERSION}/"
    fi
    rm -rf package-testing
    if [ -f /usr/bin/yum ]; then
      sudo yum install -y git wget tar
    else
      sudo apt install -y git wget tar
    fi
    git clone https://github.com/kaushikpuneet07/package-testing.git --branch fix-tarball-eol --depth 1
    cd package-testing/binary-tarball-tests/pxc
    wget -q ${TARBALL_LINK}${TARBALL_NAME}
    ./run.sh || true
  '''
}
