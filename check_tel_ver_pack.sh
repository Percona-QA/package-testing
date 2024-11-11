#!/bin/bash

# Function to check if a package is installed on Debian-based systems
check_package_debian() {
    package_name=$1
    package_check=$(dpkg -l | grep -w "$package_name")
    if [ -n "$package_check" ]; then
        echo "Package '$package_name' is installed."
    else
        echo "Package '$package_name' is not installed."
        exit 1
    fi
}

# Function to check if a package is installed on RedHat-based systems
check_package_redhat() {
    package_name=$1
    package_check=$(rpm -q "$package_name")
    if [ "$?" -eq 0 ]; then
        echo "Package '$package_name' is installed."
    else
        echo "Package '$package_name' is not installed."
        exit 1
    fi
}

# Check the OS type
if [ -f /etc/redhat-release ]; then
    OS="RedHat"
elif [ -f /etc/debian_version ]; then
    OS="Debian"
else
    echo "Unsupported OS."
    exit 1
fi

# Package name
package_name="percona-telemetry-agent"

# Check if the package is installed based on the OS type
if [ "$OS" == "RedHat" ]; then
    check_package_redhat "$package_name"
elif [ "$OS" == "Debian" ]; then
    check_package_debian "$package_name"
fi

# Get the version of the installed package
output=$(/usr/bin/percona-telemetry-agent --version)

# Get the script's directory
SCRIPT_PWD=$(cd $(dirname "$0") && pwd)

# Source the VERSIONS file
source "${SCRIPT_PWD}/VERSIONS"

# Extract the version from the output
version=$(echo "$output" | grep -oP 'Version:\s*v?\K[0-9]+\.[0-9]+\.[0-9]+')
commit_hash=$(echo "$output" | grep -oP 'Commit:\s*\K[0-9a-f]+')

# Expected version
expected_version="${TA_VER}"
expected_commit="${TA_COMMIT}"

# Compare the extracted version with the expected version
if [ "$version" == "$expected_version" ]; then
    echo "Telemetry Agent version is correct: $version"
else
    echo "Telemetry Agent version is incorrect: $version (expected: $expected_version)"
    exit 1
fi

# Compare the extracted commit hash with the expected commit hash
if [ "$commit_hash" == "$expected_commit" ]; then
    echo "Telemetry Agent commit hash is correct: $commit_hash"
    exit 0
else
    echo "Telemetry Agent commit hash is incorrect: $commit_hash (expected: $expected_commit)"
    exit 1
fi
