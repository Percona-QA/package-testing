def test_integration(host):
    with host.sudo():
        dist = host.system_info.distribution
        if dist.lower() not in ["redhat", "centos", 'rhel','oracleserver','ol']:
            command = "mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';\""
            result = host.run(command)
            assert result.rc == 0, (result.stderr, result.stdout)
        test_cmd = "cd /root/orchestrator/ && ./tests/integration/test.sh mysql"
        test = host.run(test_cmd)
        print(test.stdout)
        print(test.stderr)
        assert test.rc == 0
