#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
import os
import json
import shutil
import re
from datetime import datetime
from packaging import version
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

# pak_version is with build value 1.0.1-2
# version is TA output and is without build value 1.0.1

pak_version = os.getenv("VERSION")
version = re.search(r'[0-9]+\.[0-9]+\.[0-9]+', pak_version).group(0)
revision = os.getenv("REVISION")
update = os.getenv("TA_UPDATE")

rhel_dists = ["redhat", "centos", "rhel", "oracleserver", "ol", "amzn"]
deb_dists = ["debian", "ubuntu"]

# list of packages that should be gathered by TA to check whether they are gathered
packages_list = ['percona-server-server', 'percona-server-client', 'percona-xtrabackup', 'percona-toolkit', 'percona-orchestrator', 'percona-haproxy', \
                 'proxysql2', 'percona-mysql-shell', 'percona-mysql-router', 'pmm2-client']

#os.environ['PERCONA_TELEMETRY_URL'] = 'https://check-dev.percona.com/v1/telemetry/GenericReport'

ta_root_dir = '/usr/local/percona/telemetry/'
ta_pillar_dir_ps = ta_root_dir + 'ps'
ta_history_dir = ta_root_dir + 'history/'
if pak_version == '1.0.1-1':
    ta_log_dir = "/var/log/percona/"
else:
    ta_log_dir = "/var/log/percona/telemetry-agent/"
ta_log_file = ta_log_dir + "telemetry-agent.log"
ta_error_log_file = ta_log_dir + "telemetry-agent-error.log"

ta_agent_defaults=[["RootPath", "/usr/local/percona/telemetry"],["PSMetricsPath", "/usr/local/percona/telemetry/ps"],
        ["PSMDBMongodMetricsPath", "/usr/local/percona/telemetry/psmdb"],["PSMDBMongosMetricsPath", "/usr/local/percona/telemetry/psmdbs"],
        ["PXCMetricsPath", "/usr/local/percona/telemetry/pxc"], ["PGMetricsPath", "/usr/local/percona/telemetry/pg"],
        ["HistoryPath", "/usr/local/percona/telemetry/history"], ["CheckInterval", 86400], ["HistoryKeepInterval", 604800]
    ]

ta_platform_defaults=[["ResendTimeout", 60], ["URL","https://check.percona.com/v1/telemetry/GenericReport"]
    ]

ta_dev_url='https:\\/\\/check-dev.percona.com\\/v1\\/telemetry\\/GenericReport'

ps_telem_defaults=[["percona_telemetry.grace_interval", "86400"], ["percona_telemetry.history_keep_interval", "604800"],
                       ["percona_telemetry.scrape_interval", "86400"], ["percona_telemetry.telemetry_root_dir", "/usr/local/percona/telemetry/ps"],
                       ["percona_telemetry_disable","OFF"]
                    ]


def set_ta_options(host, check_interval="", hist_keep_interval="", resend_timeout="", url=""):
    dist = host.system_info.distribution
    if dist.lower() in deb_dists:
        options_file = '/etc/default/percona-telemetry-agent'
    else:
        options_file = '/etc/sysconfig/percona-telemetry-agent'
    with host.sudo("root"):
        if check_interval:
            host.check_output(f"sed -iE 's/PERCONA_TELEMETRY_CHECK_INTERVAL=.*$/PERCONA_TELEMETRY_CHECK_INTERVAL={check_interval}/' {options_file}")
        if hist_keep_interval:
            host.check_output(f"sed -iE 's/PERCONA_TELEMETRY_HISTORY_KEEP_INTERVAL=.*$/PERCONA_TELEMETRY_HISTORY_KEEP_INTERVAL={hist_keep_interval}/' {options_file}")
        if resend_timeout:
            host.check_output(f"sed -iE 's/PERCONA_TELEMETRY_RESEND_INTERVAL=.*$/PERCONA_TELEMETRY_RESEND_INTERVAL={resend_timeout}/' {options_file}")
        if url:
            host.check_output(f"sed -iE 's/PERCONA_TELEMETRY_URL=.*$/PERCONA_TELEMETRY_URL={url}/' {options_file}")

def update_ta_options(host, check_interval="", hist_keep_interval="", resend_timeout="", url=""):
    with host.sudo("root"):
        set_ta_options(host, check_interval, hist_keep_interval, resend_timeout, url)
        host.check_output('systemctl restart percona-telemetry-agent')
    time.sleep(1)

def update_ps_options(host, grace_interval="", scrape_interval="", history_keep_interval=""):
    dist = host.system_info.distribution
    if dist.lower() in deb_dists:
        mysql_cnf = '/etc/mysql/mysql.conf.d/mysqld.cnf'
    else:
        mysql_cnf = '/etc/my.cnf'
    with host.sudo("root"):
        if 'percona_telemetry_disable' in host.file(mysql_cnf).content_string:
            host.check_output(f"sed -r '/^percona_telemetry_disable=.*$/d' -i {mysql_cnf}")
        if grace_interval:
            host.check_output(f"sed -r '/^percona_telemetry.grace_interval=.*$/d' -i {mysql_cnf} && sed -r '$ a\\percona_telemetry.grace_interval={grace_interval}' -i {mysql_cnf}")
        if history_keep_interval:
            host.check_output(f"sed -r '/^percona_telemetry.history_keep_interval=.*$/d' -i {mysql_cnf} && sed -r '$ a\\percona_telemetry.history_keep_interval={history_keep_interval}' -i {mysql_cnf}")
        if scrape_interval:
            host.check_output(f"sed -r '/^percona_telemetry.scrape_interval=.*$/d' -i {mysql_cnf} && sed -r '$ a\\percona_telemetry.scrape_interval={scrape_interval}' -i {mysql_cnf}")
        host.check_output('systemctl restart mysql')
    time.sleep(5)

def generate_single_pillar_record(host):
    i = 0
    update_ps_options(host, "20","10")
    while i < 60:
        if len(host.file(ta_pillar_dir_ps).listdir()) < 1:
            time.sleep(1)
            i += 1
            if i == 59:
                pytest.fail(f'Telem file was not generated for 1 minute!')
        elif len(host.file(ta_pillar_dir_ps).listdir()) == 1:
            with host.sudo("root"):
                host.run('systemctl stop mysql')
                telem_file_name=host.file(ta_pillar_dir_ps).listdir()[0]
                host.run(f'mkdir -p /package-testing/telemetry/reference/')
                host.run(f'cp {ta_pillar_dir_ps}/{telem_file_name} /package-testing/telemetry/reference/')
                return telem_file_name
        else:
            pytest.fail(f'More than 1 telemetry file was generated!')

#########################################
############# TA PACKAGE  ###############
#########################################

def test_ta_package(host):
    dist = host.system_info.distribution
    pkg = host.package("percona-telemetry-agent")
    assert pkg.is_installed
    if dist.lower() in deb_dists:
        assert pak_version in pkg.version, pkg.version
    else:
        assert pak_version in pkg.version+'-'+pkg.release, pkg.version+'-'+pkg.release

def test_ta_version(host):
    result = host.run("/usr/bin/percona-telemetry-agent --version")
    assert version in result.stdout, result.stdout
    assert revision in result.stdout, result.stdout

def test_ta_service(host):
    dist = host.system_info.distribution
    if dist.lower() in deb_dists:
        options_file = '/etc/default/percona-telemetry-agent'
    else:
        options_file = '/etc/sysconfig/percona-telemetry-agent'
    ta_serv = host.service("percona-telemetry-agent")
    assert ta_serv.is_running
    assert ta_serv.is_enabled
    assert ta_serv.systemd_properties["User"] == 'daemon'
    assert ta_serv.systemd_properties["Group"] == 'percona-telemetry'
    try:
        ta_serv.systemd_properties["EnvironmentFile"]
        env_file_name = "EnvironmentFile"
    except KeyError as error:
        env_file_name = "EnvironmentFiles"
    assert options_file in ta_serv.systemd_properties[env_file_name]

def test_ta_dirs(host):
    dist = host.system_info.distribution
    rel = host.system_info.release
    assert host.file('/usr/local/percona').group == 'percona-telemetry'
    if dist.lower() in deb_dists and rel=='10':
        assert oct(host.file('/usr/local/percona').mode) in ['0o2775','0o775']
    else:
        assert oct(host.file('/usr/local/percona').mode) == '0o775'
    assert host.file(ta_root_dir).is_directory
    assert host.file(ta_root_dir).user == 'daemon'
    assert host.file(ta_root_dir).group == 'percona-telemetry'
    if dist.lower() in deb_dists and rel=='10':
        assert oct(host.file(ta_root_dir).mode) in ['0o2755','0o755']
    else:
        assert oct(host.file(ta_root_dir).mode) == '0o755'
    assert host.file(ta_history_dir).is_directory
    assert host.file(ta_history_dir).user == 'daemon'
    assert host.file(ta_history_dir).group == 'percona-telemetry'
    assert oct(host.file(ta_history_dir).mode) == '0o6755'
    assert host.file('/usr/local/percona/telemetry_uuid').is_file
    assert host.file('/usr/local/percona/telemetry_uuid').group == 'percona-telemetry'
    assert oct(host.file('/usr/local/percona/telemetry_uuid').mode) == '0o664'

# The rights for TA logs were updated starting from 1.0.1-2
def test_ta_log_files(host):
    if pak_version != '1.0.1-1':
        assert host.file(ta_log_dir).user == 'daemon'
        assert host.file(ta_log_dir).group == 'percona-telemetry'
        assert oct(host.file(ta_log_dir).mode) == '0o775'
    assert host.file(ta_log_file).is_file
    if pak_version != '1.0.1-1':
        assert host.file(ta_log_file).user == 'daemon'
        assert host.file(ta_log_file).group == 'percona-telemetry'
        assert oct(host.file(ta_log_file).mode) == '0o660'
    assert host.file(ta_error_log_file).is_file
    if pak_version != '1.0.1-1':
        assert host.file(ta_error_log_file).user == 'daemon'
        assert host.file(ta_error_log_file).group == 'percona-telemetry'
        assert oct(host.file(ta_error_log_file).mode) == '0o660'

def test_ta_rotation_params(host):
    rotate_file_content = host.file("/etc/logrotate.d/percona-telemetry-agent").content_string
    assert(ta_log_dir + "telemetry-agent*.log") in rotate_file_content
    assert 'weekly' in rotate_file_content
    assert 'rotate 4' in rotate_file_content
    assert 'compress' in rotate_file_content
    assert 'dateext' in rotate_file_content
    assert 'notifempty' in rotate_file_content
    assert 'copytruncate' in rotate_file_content

def test_ta_defaults_file(host):
    with host.sudo("root"):
        dist = host.system_info.distribution
        if dist.lower() in deb_dists:
            options_file = '/etc/default/percona-telemetry-agent'
        else:
            options_file = '/etc/sysconfig/percona-telemetry-agent'
        defaults_file_content = host.file(options_file).content_string
        assert 'PERCONA_TELEMETRY_CHECK_INTERVAL' in defaults_file_content
        assert 'PERCONA_TELEMETRY_HISTORY_KEEP_INTERVAL' in defaults_file_content
        assert 'PERCONA_TELEMETRY_RESEND_INTERVAL' in defaults_file_content
        assert 'PERCONA_TELEMETRY_URL' in defaults_file_content

@pytest.mark.parametrize("ta_key, ref_value", ta_agent_defaults)
def test_ta_telem_default_values(host, ta_key, ref_value):
    with host.sudo("root"):
        log_file_params = host.file(ta_log_file).content_string.partition('\n')[0]
        cur_values = json.loads(log_file_params)
        telem_config = cur_values["config"]["Telemetry"]
        assert len(telem_config) == 9
        assert telem_config[ta_key] == ref_value

@pytest.mark.parametrize("ta_key, ref_value", ta_platform_defaults)
def test_ta_platform_default_values(host, ta_key, ref_value):
    with host.sudo("root"):
        log_file_params = host.file(ta_log_file).content_string.partition('\n')[0]
        cur_values=json.loads(log_file_params)
        platform_config=cur_values["config"]["Platform"]
        assert len(platform_config) == 2
        assert platform_config[ta_key] == ref_value

def test_ta_logrotate_dependency(host):
    if pak_version == '1.0.1-1':
        pytest.skip("This check only for 1.0.1-1 package version")
    else:
        with host.sudo("root"):
            dist = host.system_info.distribution
            if dist.lower() in deb_dists:
                dependencies_list = host.run('apt-cache depends percona-telemetry-agent').stdout
            else:
                dependencies_list = host.run('yum deplist percona-telemetry-agent').stdout
            assert 'logrotate' in dependencies_list

def test_ta_no_restart(host):
    with host.sudo("root"):
        if update != 'yes':
            ta_started_num = host.run(f'grep -c "values from config:" {ta_log_file}')
            assert int(ta_started_num.stdout) == 1, (ta_started_num.stdout, ta_started_num.stderr)
            ta_terminated_num = host.run(f'grep -c "Received signal: terminated, shutdow" {ta_log_file}')
            assert int(ta_terminated_num.stdout) == 0, (ta_terminated_num.stdout, ta_terminated_num.stderr)

# check that the old log file is not present after update and that its content is copied to the new log.  To be removed after 1.0.1-1 to 1.0.1-2 update
def test_ta_update(host):
    with host.sudo("root"):
        if update == 'yes':
#            ta_started_num = host.run(f'grep -c "values from config:" {ta_log_file}')
#            assert int(ta_started_num.stdout) == 2, (ta_started_num.stdout, ta_started_num.stderr)
#            ta_terminated_num = host.run(f'grep -c "Received signal: terminated, shutdow" {ta_log_file}')
#            assert int(ta_terminated_num.stdout) == 1, (ta_terminated_num.stdout, ta_terminated_num.stderr)
#            assert not host.file('/var/log/percona/telemetry-agent.log').is_file
        else:
            pytest.skip("This check only for TA update")
###############################################
################## MYSQL ######################
###############################################


def test_ps_ta_dir(host):
    assert host.file(ta_pillar_dir_ps).is_directory
    assert host.file(ta_pillar_dir_ps).user == 'mysql'
    assert host.file(ta_pillar_dir_ps).group == 'percona-telemetry'
    assert oct(host.file(ta_pillar_dir_ps).mode) == '0o6775'

def test_ps_ta_dir_selinux_attr(host):
    with host.sudo("root"):
        dist = host.system_info.distribution
        if dist.lower() in deb_dists:
            pytest.skip("This check only for RPM distributions")
        else:
            # Check for SElinux attr
            security_attrs = host.run(f'ls -laZ {ta_root_dir} | grep ps').stdout
            assert 'system_u:object_r:mysqld_db_t:s0' in security_attrs

def test_ps_service(host):
    # on centos and amznlinux2 the host.service("mysql") does not return is_running true 
    # when manually accessing server and checking systemctl the service is running
    dist = host.system_info.distribution
    rel = host.system_info.release
    if (dist == 'amzn' and rel == '2') or (dist == 'centos' and rel == '7'):
        result = host.run('ps auxww| grep -v grep  | grep -c "mysql"')
        stdout = int(result.stdout)
        assert stdout == 1
    else:
        mysql_serv = host.service("mysql")
        assert mysql_serv.is_running

def test_ps_telem_enabled(host):
    with host.sudo("root"):
        result = host.check_output('mysql -Ns -e "select count(*) from mysql.component where component_urn=\'file://component_percona_telemetry\';"')
        assert result == "1"

def test_ps_apparmor_file(host):
    with host.sudo("root"):
        dist = host.system_info.distribution
        if dist.lower() in deb_dists:
            aparr_file_content = host.file("/etc/apparmor.d/usr.sbin.mysqld").content_string
            assert "/usr/local/percona/telemetry/ps/ rw" in aparr_file_content
            assert "/usr/local/percona/telemetry/ps/** rw," in aparr_file_content
        else:
            pytest.skip("This check only for DEB distributions")

@pytest.mark.parametrize("ta_key, ref_value", ps_telem_defaults)
def test_ps_telem_defaults(host, ta_key, ref_value):
    with host.sudo("root"):
        telemetry_opt_result = host.check_output(f'mysql -Ns -e "show variables like \'{ta_key}\';"')
        assert ref_value in telemetry_opt_result

def test_ps_grace_is_waited(host):
    with host.sudo("root"):
        log_file=host.check_output('mysql -u root -Ns -e \'select @@log_error;\'')
        ps_telem_files_num_before = len(host.file(ta_pillar_dir_ps).listdir())
        update_ps_options(host, '20', '10')
        # we wait 5 sec after options update, so here we need to check grace before 20 mins after restart.
        time.sleep(10)
        ps_telem_files_num_after = len(host.file(ta_pillar_dir_ps).listdir())
        log_file_content = host.file(log_file).content_string
        assert "Applying Telemetry grace interval 20 seconds" in log_file_content
        assert ps_telem_files_num_before == ps_telem_files_num_after, (ps_telem_files_num_before, ps_telem_files_num_after)
        assert "Component percona_telemetry reported: \'Created telemetry file:" not in log_file_content


def test_ps_telem_written(host):
    with host.sudo("root"):
        log_file=host.check_output('mysql -u root -Ns -e \'select @@log_error;\'')
        ps_telem_files_num_before = len(host.file(ta_pillar_dir_ps).listdir())
        time.sleep(40)
        ps_telem_files_num_after = len(host.file(ta_pillar_dir_ps).listdir())
        log_file_content = host.file(log_file).content_string
        assert ps_telem_files_num_before < ps_telem_files_num_after, (ps_telem_files_num_before, ps_telem_files_num_after)
        assert "Component percona_telemetry reported: \'Created telemetry file:" in log_file_content

def test_ps_created_file_params(host):
    telem_file=host.file(ta_pillar_dir_ps).listdir()[-1]
    assert oct(host.file(ta_pillar_dir_ps + "/" + telem_file).mode) == '0o644'
    assert telem_file.split('.')[-1] == 'json'
    # check that epoch date is correct
    filename_epoch = telem_file.split('-')[0]
    current_date = datetime.now()
    file_date = datetime.fromtimestamp(int(filename_epoch))
    diff_dates = current_date - file_date
    assert diff_dates.total_seconds() < 1800


def test_ps_telem_content(host):
    ps_telem_file_name = host.file(ta_pillar_dir_ps).listdir()
    ps_telem_file_content = host.file(ta_pillar_dir_ps + "/" + ps_telem_file_name[-1]).content_string
    ps_telem_dict=json.loads(ps_telem_file_content)
    with host.sudo("root"):
        db_instance_id_ref = host.check_output(f'mysql -Ns -e "select @@server_uuid;"')
        pillar_version_ref = host.check_output(f'mysql -Ns -e "select @@version;"')
        active_plugins_list = host.check_output(f'mysql -Ns -e "SELECT PLUGIN_NAME FROM information_schema.plugins WHERE PLUGIN_STATUS=\'ACTIVE\';"').splitlines()
        active_components_list = host.check_output(f'mysql -Ns -e "SELECT component_urn FROM mysql.component;"').splitlines()
        databases_count_ref = host.check_output(f'mysql -Ns -e "SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME NOT IN(\'mysql\', \'information_schema\', \'performance_schema\', \'sys\');"')
        se_engines_in_use_ref = host.check_output(f'mysql -Ns -e "SELECT DISTINCT ENGINE FROM information_schema.tables WHERE table_schema NOT IN (\'mysql\', \'information_schema\',\'performance_schema\', \'sys\');"').splitlines()
        assert ps_telem_dict['db_instance_id'] == db_instance_id_ref
        assert ps_telem_dict['pillar_version'] == pillar_version_ref
        assert ps_telem_dict['active_plugins'] == active_plugins_list
        assert ps_telem_dict['active_components'] == active_components_list
        assert int(ps_telem_dict['uptime']) > 10
        assert ps_telem_dict['databases_count'] == databases_count_ref
        assert ps_telem_dict['se_engines_in_use'] == ["InnoDB","ROCKSDB"]
        assert int(ps_telem_dict['databases_size']) > 2600000
        assert 'validate_password' in ps_telem_dict['active_plugins']
        assert 'file://component_validate_password' in ps_telem_dict['active_components']

def test_ps_telem_content_gr(host):
    # we check it separately BC it does not work with RocksDB
    with host.sudo("root"):
        host.check_output(f'mysql -e "SET GLOBAL group_replication_bootstrap_group=ON; START GROUP_REPLICATION;"')
    time.sleep(30)
    ps_telem_file_name = host.file(ta_pillar_dir_ps).listdir()
    ps_telem_file_content = host.file(ta_pillar_dir_ps + "/" + ps_telem_file_name[-1]).content_string
    ps_telem_dict=json.loads(ps_telem_file_content)
    assert ps_telem_dict['db_replication_id'] == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    assert ps_telem_dict['group_replication_info']['role'] == "PRIMARY"
    assert ps_telem_dict['group_replication_info']['single_primary_mode'] == "1"
    assert ps_telem_dict['group_replication_info']['group_size'] == "1"

def test_ps_telem_pillar_dir_cleaned_up(host):
    # telemetry files of the current server (started) are stored no longer than 1 week or hist keep interval.
    with host.sudo("root"):
        log_file=host.check_output('mysql -u root -Ns -e \'select @@log_error;\'')
        update_ps_options(host, '20', '10', '60')
        ps_telem_files_num_before = len(host.file(ta_pillar_dir_ps).listdir())
        time.sleep(120)
        ps_telem_files_num_after = len(host.file(ta_pillar_dir_ps).listdir())
        log_file_content = host.file(log_file).content_string
        removed=re.findall(r'Scheduling file (.*) owned by this server for deletion because it is older than 60 seconds', log_file_content)
        assert ps_telem_files_num_before < ps_telem_files_num_after
        assert len(removed) > 0
        for filename in removed:
            assert f"Component percona_telemetry reported: \'Removing telemetry file: {ta_pillar_dir_ps}/{filename}" in log_file_content
            assert filename not in host.file(ta_pillar_dir_ps).listdir()

def test_ps_telem_pillar_dir_cleaned_up_hist_max(host):
    # any telemetry files are stored no longer than 1 week.
    # create telem file with timestamp older than 1 week
    with host.sudo("root"):
        log_file=host.check_output('mysql -u root -Ns -e \'select @@log_error;\'')
        host.check_output(f"touch {ta_pillar_dir_ps}/1711821793-test-old-history.json")
        time.sleep(30)
        log_file_content = host.file(log_file).content_string
        assert re.findall(r'Scheduling file 1711821793-test-old-history.json owned by other server for deletion because it is older than 604800 seconds', log_file_content)
        assert "1711821793-test-old-history.json" not in host.file(ta_pillar_dir_ps).listdir()

def test_ps_telem_disable_running(host):
    with host.sudo("root"):
        update_ps_options(host, '20', '10', '604800') 
        host.check_output(f'mysql -Ns -e "UNINSTALL COMPONENT \'file://component_percona_telemetry\';"')
        telemetry_opt_result = host.check_output(f'mysql -Ns -e "show variables like \'percona_telemetry%\';"')
        percona_telemetry_disable_result = host.check_output(f'mysql -Ns -e  "select @@percona_telemetry_disable;"')
        ps_telem_files_num_before=len(host.file(ta_pillar_dir_ps).listdir())
        time.sleep(40)
        ps_telem_files_num_after=len(host.file(ta_pillar_dir_ps).listdir())
        assert 'percona_telemetry.grace_interval' not in telemetry_opt_result
        assert 'percona_telemetry.history_keep_interval' not in telemetry_opt_result
        assert 'percona_telemetry.scrape_interval' not in telemetry_opt_result
        assert 'percona_telemetry.telemetry_root_dir' not in telemetry_opt_result
        assert percona_telemetry_disable_result == '0'
        assert ps_telem_files_num_before == ps_telem_files_num_after

def test_ps_telem_disabled_permanent(host):
    dist = host.system_info.distribution
    if dist.lower() in deb_dists:
        mysql_cnf = '/etc/mysql/mysql.conf.d/mysqld.cnf'
    else:
        mysql_cnf = '/etc/my.cnf'
    with host.sudo("root"):
        log_file=host.check_output('mysql -u root -Ns -e \'select @@log_error;\'')
        host.check_output('systemctl stop mysql')
        # clean up log file 
        host.check_output(f'truncate -s 0 {log_file}')
        # remove telemetry options from comfig
        host.check_output(f"sed -r '/^percona_telemetry.grace_interval=.*$/d' -i {mysql_cnf}")
        host.check_output(f"sed -r '/^percona_telemetry.history_keep_interval=.*$/d' -i {mysql_cnf}")
        host.check_output(f"sed -r '/^percona_telemetry.scrape_interval=.*$/d' -i {mysql_cnf}")
        host.check_output(f"echo percona_telemetry_disable=1 >> {mysql_cnf}")
        host.check_output('systemctl restart mysql')
        time.sleep(15)
        log_file_content = host.file(log_file).content_string
        telemetry_opt_result = host.check_output(f'mysql -Ns -e "show variables like \'percona_telemetry%\';"')
        percona_telemetry_disable_result = host.check_output(f'mysql -Ns -e  "select @@percona_telemetry_disable;"')
        assert "Component percona_telemetry reported: 'Applying Telemetry grace interval" not in log_file_content
        assert 'percona_telemetry.grace_interval' not in telemetry_opt_result
        assert 'percona_telemetry.history_keep_interval' not in telemetry_opt_result
        assert 'percona_telemetry.scrape_interval' not in telemetry_opt_result
        assert 'percona_telemetry.telemetry_root_dir' not in telemetry_opt_result
        assert 'percona_telemetry.telemetry_root_dir' not in telemetry_opt_result
        assert percona_telemetry_disable_result == '1'
        host.check_output('systemctl restart mysql')
        time.sleep(15)
        log_file_content = host.file(log_file).content_string
        telemetry_opt_result = host.check_output(f'mysql -Ns -e "show variables like \'percona_telemetry%\';"')
        percona_telemetry_disable_result = host.check_output(f'mysql -Ns -e  "select @@percona_telemetry_disable;"')
        assert "Component percona_telemetry reported: 'Applying Telemetry grace interval" not in log_file_content
        assert 'percona_telemetry.grace_interval' not in telemetry_opt_result
        assert 'percona_telemetry.history_keep_interval' not in telemetry_opt_result
        assert 'percona_telemetry.scrape_interval' not in telemetry_opt_result
        assert 'percona_telemetry.telemetry_root_dir' not in telemetry_opt_result
        assert 'percona_telemetry.telemetry_root_dir' not in telemetry_opt_result
        assert percona_telemetry_disable_result == '1'

#########################################
############# TA FUNCTIONS  #############
#########################################

# We generate 1 record and copy generated file to '/package-testing/telemetry/reference/'
def test_telemetry_scrape_postponed(host):
    with host.sudo("root"):
        host.run('systemctl stop mysql')
        host.run(f'rm -rf {ta_pillar_dir_ps}/*')
        generate_single_pillar_record(host)
        update_ta_options(host, check_interval='10', url=ta_dev_url)
        time.sleep(7)
        ta_log_file_content = host.file(ta_log_file).content_string
        assert "sleeping for 10 seconds before first iteration" in ta_log_file_content
        assert "start metrics processing iteration" not in ta_log_file_content
        assert len(host.file(ta_pillar_dir_ps).listdir()) == 1

def test_telemetry_sending(host):
    with host.sudo("root"):
        pillar_ref_file = host.file('/package-testing/telemetry/reference/').listdir()[0]
        time.sleep(10)
        i = 0
        while i < 60:
            log_file_content = host.file(ta_log_file).content_string
            if 'Sending request' not in log_file_content:
                time.sleep(1)
                i += 1
            elif 'Received response:' not in log_file_content:
                time.sleep(1)
                i += 1
            else:
                time.sleep(1)
                break
        assert 'Sending request to host=check-dev.percona.com.","file":"' + ta_pillar_dir_ps + '/' + pillar_ref_file in log_file_content
        assert 'Received response: 200 OK","file":"' + ta_pillar_dir_ps + '/' + pillar_ref_file in log_file_content

def test_telemetry_uuid_created(host):
    telem_uuid_file="/usr/local/percona/telemetry_uuid"
    assert host.file(telem_uuid_file).is_file
    pattern = r'instanceId:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'
    telemetry_uuid_content = host.file(telem_uuid_file).content_string
    assert re.search(pattern, telemetry_uuid_content)

def test_telemetry_history_saved(host):
    with host.sudo("root"):
        pillar_ref_file = host.file('/package-testing/telemetry/reference/').listdir()[0]
        log_file_content = host.file(ta_log_file).content_string
        assert 'writing metrics to history file","pillar file":"' + ta_pillar_dir_ps + '/' + pillar_ref_file in log_file_content
        assert 'failed to write history file","file":"' + ta_history_dir + pillar_ref_file not in log_file_content
        assert len(host.file(ta_history_dir).listdir()) == 1

def test_tetemetry_removed_from_pillar(host):
    with host.sudo("root"):
        pillar_ref_file = host.file('/package-testing/telemetry/reference/').listdir()[0]
        log_file_content = host.file(ta_log_file).content_string
        assert 'removing metrics file","file":"' + ta_pillar_dir_ps + '/' + pillar_ref_file in log_file_content
        assert 'failed to remove metrics file, will try on next iteration","file":"' + ta_pillar_dir_ps + '/' + pillar_ref_file not in log_file_content
        assert len(host.file(ta_pillar_dir_ps).listdir()) == 0

def test_telemetry_history_file_valid_json(host):
    with host.sudo("root"):
        pillar_ref_file = host.file('/package-testing/telemetry/reference/').listdir()[0]
        history_file=host.file(ta_history_dir + pillar_ref_file).content_string
        assert json.loads(history_file)

def test_installed_packages_scraped(host):
    with host.sudo("root"):
        log_file_content = host.file(ta_log_file).content_string
        assert 'scraping installed Percona packages' in log_file_content

def test_ta_metrics_sent(host):
    with host.sudo("root"):
        pillar_ref_file = host.file('/package-testing/telemetry/reference/').listdir()[0]
        history_file = host.file(ta_history_dir + pillar_ref_file).content_string
        assert '"id":' in history_file
        assert '"createTime":' in history_file
        assert '"instanceId":' in history_file
        assert '"productFamily":' in history_file
        assert '"metrics":' in history_file
        assert '"installed_packages"' in history_file
        assert '"OS"' in history_file
        assert '"deployment"' in history_file
        assert '"hardware_arch"' in history_file

def test_ta_metrics_values_sent(host):
    # get OS
    test_host_os = host.run("grep PRETTY_NAME /etc/os-release | sed 's/PRETTY_NAME=//g;s/\"//g'").stdout
    test_host_arch = host.system_info.arch
    # get  instanceId from telemetry_uuid
    telemetry_uuid_content = host.file('/usr/local/percona/telemetry_uuid').content_string
    pattern = r'instanceId:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'
    match = re.search(pattern, telemetry_uuid_content)
    extracted_uuid = match.group(1)
    print(f'instanceId = {extracted_uuid}')

    # check metrics in the history files
    with host.sudo("root"):
        pillar_ref_file = host.file('/package-testing/telemetry/reference/').listdir()[0]
        history_file=host.file(ta_history_dir + pillar_ref_file).content_string

    history_dict=json.loads(history_file)
    assert re.search(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',history_dict['reports'][0]['id'])
    assert datetime.strptime(history_dict['reports'][0]['createTime'], "%Y-%m-%dT%H:%M:%SZ")
    assert history_dict['reports'][0]['instanceId'] == extracted_uuid
    assert history_dict['reports'][0]['productFamily'] == 'PRODUCT_FAMILY_PS'
    # check metrics
    metrics_list=history_dict['reports'][0]['metrics']
    for metric in metrics_list:
        if metric['key'] == 'OS':
            assert metric['value'] in test_host_os
        if metric['key'] == 'deployment':
            assert 'PACKAGE' in metric['value']
        if metric['key'] == 'hardware_arch':
            assert test_host_arch in metric['value']

def test_ps_metrics_sent(host):
    # check metrics in the history files
    with host.sudo("root"):
        pillar_ref_name = host.file('/package-testing/telemetry/reference/').listdir()[0]
        pillar_ref_file = host.file('/package-testing/telemetry/reference/' + pillar_ref_name).content_string
        reference_dict = json.loads(pillar_ref_file)
        ref_uptime = reference_dict['uptime']
        ref_databases_count = reference_dict['databases_count']
        ref_databases_size = reference_dict['databases_size']
        ref_se_engines_in_use = str(reference_dict['se_engines_in_use']).replace('\'', '\"').replace(' ', '')
        ref_db_instance_id = reference_dict['db_instance_id']
        ref_pillar_version = reference_dict['pillar_version']
        # ref_replication_info = reference_dict['replication_info']
        ref_active_plugins = str(reference_dict['active_plugins']).replace('\'', '\"').replace(' ', '')
        ref_active_components = str(reference_dict['active_components']).replace('\'', '\"').replace(' ', '')
        # get content of pillar history file
        history_file = host.file(ta_history_dir + pillar_ref_name).content_string
        with host.sudo("root"):
            host.run(f'mkdir -p /package-testing/telemetry/reference/hist')
            host.run(f"cp {ta_history_dir}{pillar_ref_name} /package-testing/telemetry/reference/hist/")
        history_dict = json.loads(history_file)
        # check metrics
        metrics_list=history_dict['reports'][0]['metrics']
        for metric in metrics_list:
            if metric['key'] == 'uptime':
                assert metric['value'] == ref_uptime
            if metric['key'] == 'databases_count':
                assert metric['value'] == ref_databases_count
            if metric['key'] == 'databases_size':
                assert metric['value'] == ref_databases_size
            if metric['key'] == 'se_engines_in_use':
                assert metric['value'] == ref_se_engines_in_use
            if metric['key'] == 'db_instance_id':
                assert metric['value'] == ref_db_instance_id
            if metric['key'] == 'pillar_version':
                assert metric['value'] == ref_pillar_version
            if metric['key'] == 'active_plugins':
                assert metric['value'] == ref_active_plugins
            if metric['key'] == 'active_components':
                assert metric['value'] == ref_active_components

@pytest.mark.parametrize("pkg_name", packages_list)
def test_ps_mandatory_packages(host, pkg_name):
    with host.sudo("root"):
        dist = host.system_info.distribution

        # not all the tools have aarch support so we install not all the packages on it
        if 'aarch64' in host.system_info.arch and pkg_name in ['percona-xtrabackup', 'percona-toolkit', 'percona-orchestrator', 'percona-haproxy', \
               'proxysql2', 'percona-mysql-shell', 'percona-mysql-router', 'pmm2-client']:
            pytest.skip("This package not supported by aarch")
        if dist.lower() in deb_dists:
            if 'noble' in host.system_info.codename and pkg_name in ['percona-haproxy','proxysql2']:
                pytest.skip("This package is supported on noble now") 
        pillar_ref_name = host.file('/package-testing/telemetry/reference/').listdir()[0]
        hist_file = host.file(ta_history_dir + pillar_ref_name).content_string
        hist_values=json.loads(hist_file)
        hist_metrics_list=hist_values['reports'][0]['metrics']
        for metric in hist_metrics_list:
            if metric['key'] == 'installed_packages':
                hist_packages_dict_str = metric['value']
                assert pkg_name.lower() in hist_packages_dict_str.lower()

def test_ps_packages_values(host):
    with host.sudo("root"):
        pillar_ref_name = host.file('/package-testing/telemetry/reference/').listdir()[0]
        hist_file = host.file(ta_history_dir + pillar_ref_name).content_string
        hist_values=json.loads(hist_file)
        hist_metrics_list=hist_values['reports'][0]['metrics']
        for metric in hist_metrics_list:
            if metric['key'] == 'installed_packages':
                hist_packages_dict_str = metric['value']
                hist_packages_dict = json.loads(hist_packages_dict_str)
                for ind in range(len(hist_packages_dict)):
                    hist_pkg_name = hist_packages_dict[ind]['name']
                    hist_pkg_version = hist_packages_dict[ind]['version']
                    hist_pkg_repo = hist_packages_dict[ind]['repository']
                    dist = host.system_info.distribution
                    rel = host.system_info.release
                    # FOR DEB PACKAGES
                    if dist.lower() in deb_dists:
                        # Get values of the packages installed on the server
                        # version of package
                        pkg_version_repo = host.run(f'apt-cache -q=0 policy {hist_pkg_name} | grep "\\*\\*\\*"')
                        pkg_version_match = re.search(r'[0-9]+\.[0-9]+(\.[0-9]+)?(-[0-9]+)?((-|.)[0-9]+)?',pkg_version_repo.stdout)
                        pkg_version = pkg_version_match.group(0)
                        if re.search(r'[0-9]+\.[0-9]+\.[0-9]+\-[0-9]+\.[0-9]+', pkg_version):
                            pkg_version = re.sub(r'.([0-9]+)$',r'-\g<1>', pkg_version)
                        # repository name and type
                        repo_url = host.run(f'apt-cache -q=0 policy {hist_pkg_name} | grep -A1 "\\*\\*\\*"| grep "http"')
                        repo_url_split = repo_url.stdout.strip(" ").split(" ")
                        url_repo_name = repo_url_split[1].split("/")[3]
                        url_repo_type = repo_url_split[2].split("/")[1]
                        if 'repo.percona' in repo_url.stdout and url_repo_type == 'main':
                            url_repo_type = 'release'
                        repository_str = "{'name': '" + url_repo_name + "', 'component': '"+ url_repo_type + "'}"
                    else:
                    # FOR RPM PACKAGES
                        if (dist == 'amzn' and rel == '2') or (dist == 'centos' and rel == '7'):
                            get_pkg_info = host.run(f"repoquery --qf '%{{version}}|%{{release}}|%{{ui_from_repo}}' --installed {hist_pkg_name}")
                        else:
                            get_pkg_info = host.run(f"yum repoquery --qf '%{{version}}|%{{release}}|%{{from_repo}}' --installed {hist_pkg_name}")
                        pkg_info = get_pkg_info.stdout.strip('\n').split('|')
                        pkg_version, pkg_release, pkg_repository = pkg_info
                        pkg_release = pkg_release.replace('.','-')
                        pkg_full_version = pkg_version + '-' + pkg_release
                        pkg_version_match = re.search(r'[0-9]+\.[0-9]+(\.[0-9]+)?(-[0-9]+)?((-|.)[0-9]+)?', pkg_full_version)
                        pkg_version = pkg_version_match.group(0)
                        # get repository info. Values are empty if package was installed from commandline
                        if pkg_repository in ['@commandline','installed'] or re.search(r'\/@*', pkg_repository):
                            repository_str = "{'name': '', 'component': ''}"
                        else:
                            repo_name_full = pkg_repository.strip('@, -x86_64, aarch')
                            repo_name = '-'.join(repo_name_full.split('-')[0:-1])
                            repo_type = repo_name_full.split('-')[-1]
                            repository_str = "{'name': '" + repo_name + "', 'component': '"+ repo_type + "'}"
                    # Assert if values in history file differ from installed on server
                    if hist_pkg_name == 'percona-server-server':
                        assert re.search(r'[0-9]+\.[0-9]+\.[0-9]+\-[0-9]+\-[0-9]+', pkg_version), hist_pkg_name
                    assert pkg_version == hist_pkg_version, hist_pkg_name
                    assert str(hist_pkg_repo) == repository_str, hist_pkg_name
                    # assert str(package['repository']) == repository_str

def test_telemetry_removed_from_history(host):
    with host.sudo("root"):
        update_ta_options(host, check_interval="10", hist_keep_interval="10")
        time.sleep(40)
        log_file_content = host.file(ta_log_file).content_string
        assert len(host.file(ta_history_dir).listdir()) == 0
        assert 'cleaning up history metric files","directory":"' + ta_root_dir + 'history' in log_file_content
        assert 'error removing metric file, skipping' not in log_file_content

def test_no_other_errors(host):
    with host.sudo("root"):
        log_file_content = host.file(ta_log_file).content_string
        assert '"level":"error"' not in log_file_content
        assert host.file(ta_error_log_file).size == 0

def test_stop_service(host):
    ta_serv = host.service("percona-telemetry-agent")
    with host.sudo("root"):
        host.check_output("systemctl stop percona-telemetry-agent")
        assert not ta_serv.is_running

def test_disable_service(host):
    ta_serv = host.service("percona-telemetry-agent")
    with host.sudo("root"):
        host.check_output("systemctl disable percona-telemetry-agent")
        assert not ta_serv.is_enabled


####################################################
############# ROTATION & REMOVAL TESTS #############
####################################################


def test_log_rotation(host):
    if pak_version == '1.0.1-1':
        pytest.skip("This test for package version 1.0.1-2+")
    else:
        with host.sudo("root"):    
            log_files_num_before = len(host.file(ta_log_dir).listdir())
            assert log_files_num_before == 2
            # we do not rorate empty files but error log is empty by default so we need to write smth into it
            host.check_output(f"echo 'String for test' >> {ta_error_log_file}")
            host.check_output("logrotate -f /etc/logrotate.d/percona-telemetry-agent")
            log_files_num_after = len(host.file(ta_log_dir).listdir())
            assert log_files_num_after == 4
            log_files_list = host.file(ta_log_dir).listdir()
            log_files_string = ''.join(log_files_list)
            assert re.search(r'telemetry-agent.log-[0-9]+.gz', log_files_string)
            assert re.search(r'telemetry-agent-error.log-[0-9]+.gz', log_files_string)
            # # remove old rotated logs add with old date and rotate again to check that no more than 4 logs are kept
            # host.check_output(f"touch {ta_log_dir}/telemetry-agent.log-20240812.gz {ta_log_dir}/telemetry-agent.log-20240812.gz telemetry-agent.log-20240812.gz")


def test_path_absent_after_removal(host):
    dist = host.system_info.distribution
    rel = host.system_info.release
    with host.sudo("root"):
        if dist.lower() in deb_dists:
            host.check_output("apt autoremove -y percona-server-server")
        else:
            if (dist == 'amzn' and rel == '2') or (dist == 'centos' and rel == '7'):
                host.check_output("yum autoremove -y percona-server-server")
            else:
                host.check_output("yum remove -y percona-server-server")
        assert not host.file(ta_pillar_dir_ps).exists

def test_ta_manually_remove_service_deb(host):
    dist = host.system_info.distribution
    if dist.lower() not in deb_dists:
        pytest.skip("This test only for DEB distributions")
    with host.sudo("root"):
        pkg = host.package("percona-telemetry-agent")
        host.check_output("apt autoremove -y percona-telemetry-agent")
        assert not pkg.is_installed

# In case ta package is installed before PS package (not as dependency) - it is not removed with the pillar package.
# So to check that everything is cleaned up - we delete it separately. Keeping JIC commented out
def test_ta_package_removed(host):
    dist = host.system_info.distribution
    with host.sudo("root"):
        pkg = host.package("percona-telemetry-agent")
        assert not pkg.is_installed

def test_ta_service_removed_both(host):
    with host.sudo("root"):
        ta_serv = host.service("percona-telemetry-agent")
        assert not ta_serv.exists

def test_ta_service_removed_deb(host):
    dist = host.system_info.distribution
    if dist.lower() not in deb_dists:
        pytest.skip("This test only for DEB distributions")
    with host.sudo("root"):
        ta_serv_result = host.run("systemctl status percona-telemetry-agent")
    assert "Unit percona-telemetry-agent.service could not be found." in ta_serv_result.stderr, ta_serv_result

def test_ta_service_removed_rpm(host):
    dist = host.system_info.distribution
    if dist.lower() in deb_dists:
        pytest.skip("This test only for RPM distributions")
    with host.sudo("root"):
        # https://perconadev.atlassian.net/browse/PKG-46
        ta_serv_result = host.run("systemctl status percona-telemetry-agent")
    assert "Unit percona-telemetry-agent.service could not be found." in ta_serv_result.stderr, ta_serv_result


def test_ta_history_dir_kept(host):
    assert host.file(ta_history_dir).exists

def test_ta_process_not_running(host):
    result = host.run('ps auxww| grep -v grep  | grep -c "percona-telemetry-agent"')
    stdout = int(result.stdout)
    assert stdout == 0

def test_ta_grop_removed(host):
    assert not host.group("percona-telemetry").exists
