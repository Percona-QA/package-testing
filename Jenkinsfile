pipeline {
  agent { label 'qaserver-03' }
  stages {
    stage ('Get latest code') {
      steps {
        checkout scm
      }
    }

    stage ('Setup Python virtual environment') {
      steps {
        sh '''
        python3 -m venv virtenv
        source virtenv/bin/activate
        pip install pytest molecule ansible wheel  python-vagrant paramiko
        '''
      }
    }

    stage ('Display versions') {
      steps {
        sh '''
          source virtenv/bin/activate
          docker -v
          python -V
          ansible --version
          molecule --version
        '''
      }
    }

    stage ('Molecule test') {
      steps {
        sh '''
          source virtenv/bin/activate
          cd package-testing
          git checkout pg_roles_testing
          cd molecule/pg-11
          molecule test
        '''
      }
    }

  }

}
