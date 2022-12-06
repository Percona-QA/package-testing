pipeline {
  agent any
  parameters {
    string(name: 'PS_VERSION', defaultValue: '8.0.20-11', description: 'PS full version')
    string(name: 'PS_REVISION', defaultValue: '159f0eb', description: 'PS revision')
    booleanParam( 
      defaultValue: false,
      name: 'BUILD_TYPE_MINIMAL'
    )
  }
  stages {
    stage('Binary tarball test') {
      parallel {
        stage('Ubuntu Bionic') {
          agent {
            label "min-bionic-x64"
          }
          steps {
            script {
                currentBuild.displayName = "#${BUILD_NUMBER}-${PS_VERSION}-${PS_REVISION}"
              }
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-5.6.51-rel93.0-Linux.x86_64.ssl100.tar.gz"
                  TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-5.6.51-93/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q ${TARBALL_LINK}${TARBALL_NAME} 
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Ubuntu Bionic
        stage('Buster') {
          agent {
            label "min-buster-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-5.6.51-rel93.0-Linux.x86_64.ssl100.tar.gz"
                  TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-5.6.51-93/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Centos7
        stage('Centos7') {
          agent {
            label "min-centos-7-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-5.6.51-rel93.0-Linux.x86_64.ssl101.tar.gz"
                  TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/ps-5.6.51-93/"
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q ${TARBALL_LINK}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Centos7
      } //End parallel
    } //End stage Run tests
  } //End stages
} //End pipeline
