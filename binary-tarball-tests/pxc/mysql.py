#!/usr/bin/env python3
import subprocess
import re
import os
import time

class MySQL:
    def __init__(self, base_dir):
        self.basedir = base_dir
        self.node1_cnf = base_dir+'/node1.cnf'
        self.node2_cnf = base_dir+'/node2.cnf'
        self.node3_cnf = base_dir+'/node3.cnf'
        self.node1_datadir = base_dir+'/node1'
        self.node2_datadir = base_dir+'/node2'
        self.node3_datadir = base_dir+'/node3'
        self.node1_socket = '/tmp/node1_mysql.sock'
        self.node2_socket = '/tmp/node2_mysql.sock'
        self.node3_socket = '/tmp/node3_mysql.sock'
        self.node1_logfile = base_dir+'/log/node1.err'
        self.node2_logfile = base_dir+'/log/node2.err'
        self.node3_logfile = base_dir+'/log/node3.err'
        self.mysql = base_dir+'/bin/mysql'
        self.mysqld = base_dir+'/bin/mysqld'
        self.mysqladmin = base_dir+'/bin/mysqladmin'
        self.pidfile = base_dir+'/mysql.pid'
        self.mysql_install_db = base_dir+'/scripts/mysql_install_db'
        self.wsrep_provider = base_dir+'/lib/libgalera_smm.so'

        subprocess.call(['rm', '-Rf', self.node1_datadir])
        subprocess.call(['rm', '-Rf', self.node2_datadir])
        subprocess.call(['rm', '-Rf', self.node3_datadir])
        subprocess.call(['rm', '-f', self.node1_logfile])
        subprocess.call(['rm', '-f', self.node2_logfile])
        subprocess.call(['rm', '-f', self.node3_logfile])
        subprocess.call(['mkdir', '-p', self.basedir+'/log'])
        output = subprocess.check_output([self.mysqld, '--version'], universal_newlines=True)
        x = re.search(r"[0-9]+\.[0-9]+", output)
        self.major_version = x.group()
        if self.major_version != "8.0":
            self.sst_opts = ["--wsrep_sst_method=xtrabackup-v2", "--wsrep_sst_auth=root:"]
        else:
            self.sst_opts = ["--wsrep_sst_method=xtrabackup-v2"]
        if self.major_version == "5.6":
            subprocess.check_call([self.mysql_install_db, '--no-defaults', '--basedir=' + self.basedir,
                                   '--datadir='+ self.node1_datadir])
            subprocess.check_call([self.mysql_install_db, '--no-defaults', '--basedir=' + self.basedir,
                                   '--datadir=' + self.node2_datadir])
            subprocess.check_call([self.mysql_install_db, '--no-defaults', '--basedir=' + self.basedir,
                                   '--datadir=' + self.node3_datadir])
        else:
            self.psadmin = base_dir+'/bin/ps-admin'
            subprocess.check_call([self.mysqld, '--no-defaults', '--initialize-insecure', '--basedir=' + self.basedir,
                                   '--datadir=' + self.node1_datadir])
            subprocess.check_call([self.mysqld, '--no-defaults', '--initialize-insecure', '--basedir=' + self.basedir,
                                   '--datadir=' + self.node2_datadir])
            subprocess.check_call([self.mysqld, '--no-defaults', '--initialize-insecure', '--basedir=' + self.basedir,
                                   '--datadir=' + self.node3_datadir])

    def startup_check(self, socket):
        ping_query = self.basedir + '/bin/mysqladmin --user=root --socket=' + socket + ' ping > /dev/null 2>&1'
        for startup_timer in range(120):
            ping_check = subprocess.call(ping_query, shell=True, stderr=subprocess.DEVNULL)
            ping_status = ("{}".format(ping_check))
            if int(ping_status) == 0:
                break  # break the loop if mysqld is running
            time.sleep(1)

    def start(self):
        subprocess.Popen([self.mysqld, '--defaults-file=' + self.node1_cnf,  '--basedir=' + self.basedir,
                          '--datadir=' + self.node1_datadir,
                          '--tmpdir=' + self.node1_datadir, '--socket=' + self.node1_socket,
                          '--log-error=' + self.node1_logfile, '--wsrep_provider=' + self.wsrep_provider,
                          *self.sst_opts, '--wsrep-new-cluster'], env=os.environ)
        self.startup_check(self.node1_socket)
        os.system("cat " + self.node1_logfile)
        subprocess.Popen([self.mysqld, '--defaults-file=' + self.node2_cnf, '--basedir=' + self.basedir,
                          '--datadir=' + self.node2_datadir,
                          '--tmpdir=' + self.node2_datadir, '--socket=' + self.node2_socket,
                          '--log-error=' + self.node2_logfile, '--wsrep_provider=' + self.wsrep_provider,
                          *self.sst_opts], env=os.environ)
        self.startup_check(self.node2_socket)
        os.system("cat " + self.node2_logfile)
        subprocess.Popen([self.mysqld, '--defaults-file=' + self.node3_cnf, '--basedir=' + self.basedir,
                          '--datadir=' + self.node3_datadir,
                          '--tmpdir=' + self.node3_datadir, '--socket=' + self.node3_socket,
                          '--log-error=' + self.node3_logfile, '--wsrep_provider=' + self.wsrep_provider,
                          *self.sst_opts], env=os.environ)
        self.startup_check(self.node3_socket)
        os.system("cat " + self.node3_logfile)

    def stop(self):
        subprocess.check_call([self.mysqladmin, '-uroot', '-S'+self.node3_socket, 'shutdown'])
        subprocess.check_call([self.mysqladmin, '-uroot', '-S'+self.node2_socket, 'shutdown'])
        subprocess.check_call([self.mysqladmin, '-uroot', '-S'+self.node1_socket, 'shutdown'])
        subprocess.call(['sleep', '5'])

    def restart(self):
        self.stop()
        self.start()

    def purge(self):
        self.stop()
        subprocess.call(['rm', '-Rf', self.node1_datadir])
        subprocess.call(['rm', '-Rf', self.node2_datadir])
        subprocess.call(['rm', '-Rf', self.node3_datadir])
        subprocess.call(['rm', '-f', self.node1_logfile])
        subprocess.call(['rm', '-f', self.node2_logfile])
        subprocess.call(['rm', '-f', self.node3_logfile])

    def run_query(self,query):
        command = self.mysql+' --user=root -S'+self.node1_socket+' -s -N -e '+query
        return subprocess.check_output(command, shell=True, universal_newlines=True)

    def install_function(self, fname, soname, return_type):
        query = '"CREATE FUNCTION {} RETURNS {} SONAME \\\"{}\\\";"'.format(fname, return_type, soname)
        self.run_query(query)
        query = '"SELECT name FROM mysql.func WHERE dl = \\\"{}\\\";"'.format(soname)
        output = self.run_query(query)
        assert fname in output

    def install_plugin(self, pname, soname):
        query = '"INSTALL PLUGIN {} SONAME \\\"{}\\\";"'.format(pname,soname)
        self.run_query(query)
        query = '"SELECT plugin_status FROM information_schema.plugins WHERE plugin_name = \\\"{}\\\";"'.format(pname)
        output = self.run_query(query)
        assert 'ACTIVE' in output

    def check_engine_active(self, engine):
        query = '"select SUPPORT from information_schema.ENGINES where ENGINE = \\\"{}\\\";"'.format(engine)
        output = self.run_query(query)
        if 'YES' in output:
            return True
        else:
            return False
