pipeline {
  agent {
    label 'docker'
  }
  parameters {
    string(name: 'PS_VERSION', defaultValue: '8.0.22-13', description: 'PS full version')
    string(name: 'PS_REVISION', defaultValue: '0cc556b', description: 'PS revision')
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
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Ubuntu Focal
        stage('Ubuntu Bionic') {
          agent {
            label "min-bionic-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Ubuntu Bionic
        stage('Ubuntu Xenial') {
          agent {
            label "min-xenial-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Ubuntu Xenial
        stage('Debian Buster') {
          agent {
            label "min-buster-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Debian Buster
        stage('Debian Stretch') {
          agent {
            label "min-stretch-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Debian Stretch
        stage('Centos8') {
          agent {
            label "min-centos-8-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Centos8
        stage('Centos7') {
          agent {
            label "min-centos-7-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Centos7
        stage('Centos6') {
          agent {
            label "min-centos-6-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              run_test()
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Centos6
      } //End parallel
    } //End stage Run tests
  } //End stages
} //End pipeline

void run_test() {
  sh '''
    echo ${BUILD_TYPE_MINIMAL}
    PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
    MINIMAL=""
    if [ "${BUILD_TYPE_MINIMAL}" = "true" ]; then
      MINIMAL="-minimal"
    fi
    if [ "${PS_MAJOR_VERSION}" = "8.0" ]; then
      export GLIBC_VERSION="2.17"
      if [ -f /etc/redhat-release ] && [ $(grep -c "release 6" /etc/redhat-release) -eq 1 ]; then
        export GLIBC_VERSION="2.12"
      fi
      TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc${GLIBC_VERSION}${MINIMAL}.tar.gz"
      TARBALL_LINK="https://www.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
    elif [ "${PS_MAJOR_VERSION}" = "5.7" ]; then
      TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
      TARBALL_LINK="https://www.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
    fi
    rm -rf package-testing
    if [ -f /usr/bin/yum ]; then
      sudo yum install -y git wget
    else
      sudo apt install -y git wget lsb-release
    fi
    git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
    cd package-testing/binary-tarball-tests/ps
    wget -q ${TARBALL_LINK}${TARBALL_NAME}
    ./run.sh || true
  '''
}
