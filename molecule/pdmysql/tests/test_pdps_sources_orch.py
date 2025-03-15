import pytest
from packaging import version
from .settings import *

@pytest.mark.orch_source
def test_integration(host):
    with host.sudo():
        dist = host.system_info.distribution
        # Fetch MySQL version dynamically
        version_command = "mysql --version"
        result = host.run(version_command)
        assert result.rc == 0, f"Failed to get MySQL version: {result.stderr}"

        mysql_version = result.stdout.split()[4]  # Extract version part
        print(f"MySQL version: {mysql_version}")

        # Check the MySQL version and decide which authentication method to use
        if version.parse(mysql_version) > version.parse("8.0.0") and version.parse(mysql_version) < version.parse("8.1.0"):
            command = "mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'root';\""
        elif version.parse(mysql_version) >= version.parse("8.1.0"):
            command = "mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';\""
        else:
            # For MySQL 8.0.0 or earlier, you can leave it as is (or add any other adjustments)
            command = "mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';\""

        # Run the command to alter the root user's authentication
        result = host.run(command)
        assert result.rc == 0, f"Failed to alter MySQL root user: {result.stderr}"

        # Now, run the rest of the test
        test_cmd = "cd /root/orchestrator/ && ./tests/integration/test.sh mysql"
        test = host.run(test_cmd)
        print(test.stdout)
        print(test.stderr)
        assert test.rc == 0
