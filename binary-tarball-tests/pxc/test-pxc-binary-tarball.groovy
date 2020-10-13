pipeline {
  agent any
  parameters {
    string(name: 'PXC_VERSION', defaultValue: '8.0.20-11.1', description: 'PXC full version')
    string(name: 'PXC_REVISION', defaultValue: '683b26a', description: 'PXC revision')
    string(name: 'WSREP_VERSION', defaultValue: '26.4.3', description: 'WSREP version')
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
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-pxc-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
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
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-pxc-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
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
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-pxc-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
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
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-pxc-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
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
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-pxc-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
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
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-pxc-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
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
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release/label_exp=min-centos-6-x64/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}-Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-pxc-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/report.xml'
          } //End steps
        } //End stage CentOS7
       } //End parallel
    } //End stage Run tests
  } //End stages
} //End pipeline
