pipeline {
  agent {
    label 'docker'
  }
  parameters {
    string(name: 'PS_VERSION', defaultValue: '8.0.26-16', description: 'PS full version')
    string(name: 'PS_REVISION', defaultValue: '3d64165', description: 'PS revision')
    booleanParam( 
      defaultValue: false,
      name: 'BUILD_TYPE_MINIMAL'
    )
  }
  stages {
    stage('Binary tarball test') {
      parallel {
        stage('Ubuntu Jammy') {
          agent {
            label "min-jammy-x64"
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
        } //End stage Ubuntu Jammy
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
        stage('Debian Bullseye') {
          agent {
            label "min-bullseye-x64"
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
        } //End stage Debian Bullseye
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
        stage('Oracle Linux 8') {
          agent {
            label "min-ol-8-x64"
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
        } //End stage Oracle Linux 8
        stage('Oracle Linux 9') {
          agent {
            label "min-ol-9-x64"
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
        } //End stage Oracle Linux 9
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
    if [ -f /usr/bin/yum ]; then
      sudo yum install -y git wget
    else
      sudo apt install -y git wget
    fi
    export GLIBC_VERSION="2.17"
    if [ -f /usr/bin/apt-get ]; then
      DEBIAN_VERSION=$(lsb_release -sc)
      if [ ${DEBIAN_VERSION} = "jammy" ]; then
        export GLIBC_VERSION="2.35"
      fi
    fi
    TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc${GLIBC_VERSION}${MINIMAL}.tar.gz"
    TARBALL_LINK="https://www.percona.com/downloads/TESTING/ps-${PS_VERSION}/"
    rm -rf package-testing
    git clone https://github.com/kaushikpuneet07/package-testing.git --branch PS-8399 --depth 1
    cd package-testing/binary-tarball-tests/ps
    wget -q ${TARBALL_LINK}${TARBALL_NAME}
    ./run.sh || true
  '''
}
