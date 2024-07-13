#!/bin/bash
# Check if package is installed or not
package_name="percona-telemetry-agent"
package_check=$(dpkg -l | grep -w "$package_name")
if [ -n "$package_check" ]; then
    echo "Package '$package_name' is installed."
else
    echo "Package '$package_name' is not installed."
    exit 1
fi
output=$(/usr/bin/percona-telemetry-agent --version)
SCRIPT_PWD=$(cd $(dirname "$0") && pwd)
source "${SCRIPT_PWD}"/VERSIONS
# Extract the version from the output
version=$(echo "$output" | grep -oP 'Version:\s*v?\K[0-9]+\.[0-9]+\.[0-9]+')
# Expected version
expected_version="${TA_VER}"
# Compare the extracted version with the expected version
if [ "$version" == "$expected_version" ]; then
    echo "Telemetry Agent version is correct: $version"
    exit 0
else
    echo "Telemetry Agent version is incorrect: $version (expected: $expected_version)"
    exit 1
fi
