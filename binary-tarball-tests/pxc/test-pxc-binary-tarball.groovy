pipeline {
  agent any 
  parameters {
    string(name: 'PXC_VERSION', defaultValue: '8.0.21-12.1', description: 'PXC full version')
    string(name: 'PXC_REVISION', defaultValue: 'c25872b', description: 'PXC revision')
    string(name: 'WSREP_VERSION', defaultValue: '26.4.3', description: 'WSREP version')
    string(name: 'PXC57_PKG_VERSION', defaultValue: '5.7.31-rel34-43.2', description: 'PXC-5.7 package version')
    booleanParam( 
      defaultValue: false,
      name: 'BUILD_TYPE_MINIMAL'
    )
  }
  stages {
    stage('Binary tarball test') {
      parallel {
        stage('Ubuntu Xenial') {
          agent {
            label "min-xenial-x64"
          }
          steps {
            script {
              currentBuild.displayName = "#${BUILD_NUMBER}-${PXC_VERSION}-${PXC_REVISION}"
            }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Ubuntu Xenial
        stage('Ubuntu Bionic') {
          agent {
            label "min-bionic-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Ubuntu Bionic
        stage('Ubuntu Focal') {
          agent {
            label "min-focal-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Ubuntu Xenial
        stage('Debian Stretch') {
          agent {
            label "min-stretch-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Debian Stretch
        stage('Debian Buster') {
          agent {
            label "min-buster-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage Debian Buster
        stage('Centos8') {
          agent {
            label "min-centos-8-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage CentOS8
        stage('Centos7') {
          agent {
            label "min-centos-7-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage CentOS7
       } //End parallel
    } //End stage Run tests
  } //End stages
} //End pipeline

void run_test() {
  sh '''
    echo ${BUILD_TYPE_MINIMAL}
    PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
    MINIMAL=""
    if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
      MINIMAL="-minimal"
    fi
    if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
      TARBALL_NAME="Percona-XtraDB-Cluster-${PXC_VERSION}-Linux.x86_64.glibc2.17${MINIMAL}.tar.gz"
      TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION}/"
    elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
      TARBALL_NAME="Percona-XtraDB-Cluster-${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
      TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION}/"
    fi
    rm -rf package-testing
    if [ -f /usr/bin/yum ]; then
      sudo yum install -y git wget
    else
      sudo apt install -y git wget lsb-release
    fi
    git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
    cd package-testing/binary-tarball-tests/pxc
    wget -q ${TARBALL_LINK}${TARBALL_NAME}
    ./run.sh || true
  '''
}
