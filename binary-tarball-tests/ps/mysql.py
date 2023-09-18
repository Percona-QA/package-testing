#!/usr/bin/env python3
import subprocess
import re
import os
import shlex

class MySQL:
    def __init__(self, base_dir):
        self.basedir = base_dir
        self.port = '3306'
        self.datadir = base_dir+'/data'
        self.socket = '/tmp/mysql.sock'
        self.logfile = base_dir+'/log/master.err'
        self.mysql = base_dir+'/bin/mysql'
        self.mysqld = base_dir+'/bin/mysqld'
        self.mysqladmin = base_dir+'/bin/mysqladmin'
        self.pidfile = base_dir+'/mysql.pid'
        self.mysql_install_db = base_dir+'/scripts/mysql_install_db'

        subprocess.call(['rm','-Rf',self.datadir])
        subprocess.call(['rm','-f',self.logfile])
        subprocess.call(['mkdir','-p',self.basedir+'/log'])
        output = subprocess.check_output([self.mysqld, '--version'],universal_newlines=True)
        x = re.search(r"[0-9]+\.[0-9]+", output)
        self.major_version = x.group()
        if self.major_version == "5.6":
            os.environ['LD_PRELOAD'] = self.basedir+'/lib/mysql/libjemalloc.so.1 '+self.basedir+'/lib/libHotBackup.so'
            self.psadmin = base_dir+'/bin/ps_tokudb_admin'
            subprocess.check_call([self.mysql_install_db, '--no-defaults', '--basedir='+self.basedir,'--datadir='+self.datadir])
        elif self.major_version == "5.7":
            os.environ['LD_PRELOAD'] = self.basedir+'/lib/mysql/libjemalloc.so.1 '+self.basedir+'/lib/libHotBackup.so'
            self.psadmin = base_dir+'/bin/ps-admin'
            subprocess.check_call([self.mysqld, '--no-defaults', '--initialize-insecure','--basedir='+self.basedir,'--datadir='+self.datadir])
        else:
            os.environ['LD_PRELOAD'] = self.basedir+'/lib/mysql/libjemalloc.so.1'
            self.psadmin = base_dir+'/bin/ps-admin'
            subprocess.check_call([self.mysqld, '--no-defaults', '--initialize-insecure','--basedir='+self.basedir,'--datadir='+self.datadir])

    def start(self):
        subprocess.Popen([self.mysqld,'--no-defaults','--basedir='+self.basedir,'--datadir='+self.datadir,'--tmpdir='+self.datadir,'--socket='+self.socket,'--port='+self.port,'--log-error='+self.logfile,'--pid-file='+self.pidfile,'--server-id=1','--master-info-repository=table','--relay-log-info-repository=table'], env=os.environ)
        subprocess.call(['sleep','5'])

    def stop(self):
        subprocess.check_call([self.mysqladmin,'-uroot','-S'+self.socket,'shutdown'])
        subprocess.call(['sleep','5'])

    def restart(self):
        self.stop()
        self.start()

    def purge(self):
        self.stop()
        subprocess.call(['rm','-Rf',self.datadir])
        subprocess.call(['rm','-f',self.logfile])

    def run_query(self,query):
        command = self.mysql+' --user=root -S'+self.socket+' -s -N -e '+shlex.quote(query)
        return subprocess.check_output(command,shell=True,universal_newlines=True)

    def install_function(self, fname, soname, return_type):
        query = 'CREATE FUNCTION {} RETURNS {} SONAME "{}";'.format(fname,return_type,soname)
        self.run_query(query)
        query = 'SELECT name FROM mysql.func WHERE dl = "{}";'.format(soname)
        output = self.run_query(query)
        assert fname in output

    def install_plugin(self, pname, soname):
        query = 'INSTALL PLUGIN {} SONAME "{}";'.format(pname,soname)
        self.run_query(query)
        query = 'SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = "{}";'.format(pname)
        output = self.run_query(query)
        assert 'ACTIVE' in output

    def install_component(self, cname):
        query = 'INSTALL COMPONENT "file://{}";'.format(cname)
        self.run_query(query)
        query = 'SELECT component_urn FROM mysql.component where component_urn like "%component_masking_functions%";'.format(cname)
        output = self.run_query(query)
        assert output is None

    def check_engine_active(self, engine):
        query = 'select SUPPORT from information_schema.ENGINES where ENGINE = "{}";'.format(engine)
        output = self.run_query(query)
        if 'YES' in output:
            return True
        else:
            return False

