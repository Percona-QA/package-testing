pipeline {
  agent any
  parameters {
    string(name: 'PS_VERSION', defaultValue: '8.0.17-8', description: 'PS full version')
    string(name: 'PS_REVISION', defaultValue: 'e52ea8e', description: 'PS revision')
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
                if [ "${PS_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.12.tar.gz" 
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-rocks-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-$(echo ${PS_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Ubuntu Bionic
        stage('Ubuntu Xenial') {
          agent {
            label "min-xenial-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                if [ "${PS_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.glibc2.12.tar.gz" 
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl100.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-rocks-new/label_exp=min-jessie-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-$(echo ${PS_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl100.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-new/label_exp=min-jessie-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Ubuntu Xenial
        stage('Debian Buster') {
          agent {
            label "min-buster-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                if [ "${PS_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl102.deb.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-rocks-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-$(echo ${PS_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Debian Buster
        stage('Debian Stretch') {
          agent {
            label "min-stretch-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                if [ "${PS_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl102.deb.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-rocks-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-$(echo ${PS_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Debian Stretch
        stage('Centos7') {
          agent {
            label "min-centos-7-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                if [ "${PS_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl102.rpm.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release/label_exp=min-centos-7-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl101.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-rocks-new/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-$(echo ${PS_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl101.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-new/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Centos7
        stage('Centos6') {
          agent {
            label "min-centos-6-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PS_MAJOR_VERSION="$(echo ${PS_VERSION}|cut -d'.' -f1,2)"
                if [ "${PS_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl101.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-Server-${PS_VERSION}-Linux.x86_64.ssl101.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-rocks-new/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PS_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-Server-$(echo ${PS_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl101.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-server-${PS_MAJOR_VERSION}-binaries-release-new/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch master --depth 1
                cd package-testing/binary-tarball-tests/ps
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/ps/report.xml'
          } //End steps
        } //End stage Centos6
      } //End parallel
    } //End stage Run tests
  } //End stages
} //End pipeline
