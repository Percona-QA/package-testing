m:pipeline {
  agent any
  parameters {
    string(name: 'PXC_VERSION', defaultValue: '5.6.50-28.44', description: 'PXC full version')
    string(name: 'PXC_REVISION', defaultValue: '93ea5c8', description: 'PXC revision')
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
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "8.0" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_${PXC_VERSION}_Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release-cve/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc/NON-PRO/NON-PRO
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release-cve/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc/NON-PRO/NON-PRO
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release-cve/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release-cve/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release-cve/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo apt install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release-cve/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
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
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binaries-release-cve/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/test/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.7" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster-${PXC57_PKG_VERSION}.Linux.x86_64.glibc2.12${MINIMAL}.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/percona-xtradb-cluster-${PXC_MAJOR_VERSION}-binary-tarball/label_exp=min-centos-6-x64-new/lastSuccessfulBuild/artifact/tarball/"
                elif [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="Percona-XtraDB-Cluster_$(echo ${PXC_VERSION}|sed 's/-/-rel/')-Linux.x86_64.ssl102.tar.gz"
                  JENKINS_JOB="https://jenkins.percona.com/job/Percona-XtraDB-Cluster_${PXC_MAJOR_VERSION}-binaries-release-new/label_exp=min-stretch-x64/lastSuccessfulBuild/artifact/tarball/"
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                wget -q --auth-no-challenge --http-user=${JENKINS_API_USER} --http-password=${JENKINS_API_PWD} ${JENKINS_JOB}${TARBALL_NAME}
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
          } //End steps
        } //End stage CentOS7
        stage('Centos6') {
          agent {
            label "min-centos-6-x64"
          }
          steps {
            withCredentials([usernamePassword(credentialsId: 'JenkinsAPI', passwordVariable: 'JENKINS_API_PWD', usernameVariable: 'JENKINS_API_USER')]) {
              sh '''
                PXC_MAJOR_VERSION="$(echo ${PXC_VERSION}|cut -d'.' -f1,2)"
                MINIMAL=""
                if [ BUILD_TYPE_MINIMAL ]; then
                  MINIMAL="-minimal"
                fi
                if [ "${PXC_MAJOR_VERSION}" = "5.6" ]; then
                  TARBALL_NAME="https://downloads.percona.com/downloads/TESTING/pxc56_centos6/Percona-XtraDB-Cluster-5.6.50-rel90.0-28.44.1.Linux.x86_64.ssl101.tar.gz"
                  TARBALL_LINK="https://downloads.percona.com/downloads/TESTING/pxc-${PXC_VERSION}/"
		else
		  echo "ERROR: Wrong PXC version"
		  exit 1
                fi
                rm -rf package-testing
                sudo yum install -y git wget
                git clone https://github.com/Percona-QA/package-testing.git --branch PXC-3447-PXC-package-testing-job --depth 1
                cd package-testing/binary-tarball-tests/pxc/NON-PRO
                ./run.sh || true
              '''
            }
            junit 'package-testing/binary-tarball-tests/pxc/NON-PRO/report.xml'
          } //End steps
        } //End stage CentOS6
       } //End parallel
    } //End stage Run tests
  } //End stages
} //End pipeline
