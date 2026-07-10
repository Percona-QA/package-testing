"""EC2 platform configuration for PXC package testing with pyinfra.

Values are extracted from the per-OS molecule platform definitions in
package-testing/molecule/pxc/pxc{80,84}-bootstrap-install/molecule/<os>/molecule.yml
so that the pyinfra job provisions the same instances as the molecule job.

Note: rocky-linux images live in us-west-2 (different subnet), everything
else in us-west-1.
"""

DEFAULT_REGION = "us-west-1"
DEFAULT_SUBNET_ID = "subnet-04a8ad1b1d4da874c"

ROCKY_REGION = "us-west-2"
ROCKY_SUBNET_ID = "subnet-0430e63d7cdbcd237"

KEY_NAME = "molecule-pkg-tests"
INSTANCE_PROFILE_ARN = "arn:aws:iam::119175775298:instance-profile/jenkins-psmdb-slave"
SECURITY_GROUP_PREFIX = "molecule-pxc-package-testing"
ROOT_VOLUME_SIZE_GB = 30

OS_CONFIGS = {
    "ubuntu-noble": {
        "image": "ami-0e2c5839c3019cf98",
        "instance_type": "t2.large",
        "ssh_user": "ubuntu",
        "root_device_name": "/dev/sda1",
    },
    "ubuntu-noble-arm": {
        "image": "ami-06098d756d39a2267",
        "instance_type": "c6g.large",
        "ssh_user": "ubuntu",
        "root_device_name": "/dev/sda1",
    },
    "ubuntu-jammy": {
        "image": "ami-0dc5e9ff792ec08e3",
        "instance_type": "t2.large",
        "ssh_user": "ubuntu",
        "root_device_name": "/dev/sda1",
    },
    "ubuntu-jammy-arm": {
        "image": "ami-076ce4c214a7e0764",
        "instance_type": "c6g.large",
        "ssh_user": "ubuntu",
        "root_device_name": "/dev/sda1",
    },
    "debian-11": {
        "image": "ami-02dda1c84e46dbe0a",
        "instance_type": "t2.large",
        "ssh_user": "admin",
        "root_device_name": "/dev/xvda",
    },
    "debian-11-arm": {
        "image": "ami-0f887c9b8838fb051",
        "instance_type": "c6g.large",
        "ssh_user": "admin",
        "root_device_name": "/dev/xvda",
    },
    "debian-12": {
        "image": "ami-071175b60c818694f",
        "instance_type": "t2.large",
        "ssh_user": "admin",
        "root_device_name": "/dev/xvda",
    },
    "debian-12-arm": {
        "image": "ami-08afcd4a569ee9120",
        "instance_type": "c6g.large",
        "ssh_user": "admin",
        "root_device_name": "/dev/xvda",
    },
    "debian-13": {
        "image": "ami-0157ed312f9c59a91",
        "instance_type": "t2.large",
        "ssh_user": "admin",
        "root_device_name": "/dev/xvda",
    },
    "debian-13-arm": {
        "image": "ami-0eb530f507a9eb9cc",
        "instance_type": "c6g.large",
        "ssh_user": "admin",
        "root_device_name": "/dev/xvda",
    },
    "ol-8": {
        "image": "ami-06339041e422fab06",
        "instance_type": "t2.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "ol-9": {
        "image": "ami-0d1958c85fb6a7b3e",
        "instance_type": "t2.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "rhel-8": {
        "image": "ami-0186e3fec9b0283ee",
        "instance_type": "t2.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "rhel-8-arm": {
        "image": "ami-01be8515d27094d60",
        "instance_type": "c6g.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "rhel-9": {
        "image": "ami-0fa0ed170a59f4917",
        "instance_type": "t2.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "rhel-9-arm": {
        "image": "ami-04dbd1a24794a6d04",
        "instance_type": "c6g.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "rhel-10": {
        "image": "ami-0f7153f6999a5ef60",
        "instance_type": "t2.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "rhel-10-arm": {
        "image": "ami-02fd5035c09f46e15",
        "instance_type": "c6g.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/sda1",
    },
    "rocky-linux-8": {
        "image": "ami-04310224db1f2a278",
        "instance_type": "t2.large",
        "ssh_user": "rocky",
        "root_device_name": "/dev/xvda",
        "region": ROCKY_REGION,
        "subnet_id": ROCKY_SUBNET_ID,
    },
    "rocky-linux-8-arm": {
        "image": "ami-0d4e5716e8f0b62b0",
        "instance_type": "c6g.large",
        "ssh_user": "rocky",
        "root_device_name": "/dev/xvda",
        "region": ROCKY_REGION,
        "subnet_id": ROCKY_SUBNET_ID,
    },
    "rocky-linux-9": {
        "image": "ami-023eeffe03f0dd455",
        "instance_type": "t2.medium",
        "ssh_user": "rocky",
        "root_device_name": "/dev/xvda",
        "region": ROCKY_REGION,
        "subnet_id": ROCKY_SUBNET_ID,
    },
    "rocky-linux-9-arm": {
        "image": "ami-09aad1f3c008ab0b4",
        "instance_type": "c6g.large",
        "ssh_user": "rocky",
        "root_device_name": "/dev/xvda",
        "region": ROCKY_REGION,
        "subnet_id": ROCKY_SUBNET_ID,
    },
    "amazon-linux-2023": {
        "image": "ami-061ad72bc140532fd",
        "instance_type": "t2.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/xvda",
    },
    "amazon-linux-2023-arm": {
        "image": "ami-03a1b0d298ba6b328",
        "instance_type": "c6g.large",
        "ssh_user": "ec2-user",
        "root_device_name": "/dev/xvda",
    },
}

# OS lists per product, matching the node_to_test cascade parameter of the
# pxc-package-testing Jenkins job (non-pro).
SUPPORTED_OS = {
    "pxc80": [
        "ubuntu-noble",
        "ubuntu-jammy",
        "ubuntu-noble-arm",
        "ubuntu-jammy-arm",
        "debian-12",
        "debian-11",
        "debian-12-arm",
        "debian-11-arm",
        "ol-8",
        "ol-9",
        "rhel-8",
        "rhel-9",
        "rhel-8-arm",
        "rhel-9-arm",
        "rocky-linux-8",
        "rocky-linux-8-arm",
        "rocky-linux-9",
        "rocky-linux-9-arm",
        "amazon-linux-2023",
        "amazon-linux-2023-arm",
    ],
    "pxc84": [
        "ubuntu-noble",
        "ubuntu-jammy",
        "ubuntu-noble-arm",
        "ubuntu-jammy-arm",
        "debian-13",
        "debian-12",
        "debian-11",
        "debian-13-arm",
        "debian-12-arm",
        "debian-11-arm",
        "ol-8",
        "ol-9",
        "rhel-8",
        "rhel-9",
        "rhel-10",
        "rhel-8-arm",
        "rhel-9-arm",
        "rhel-10-arm",
        "rocky-linux-8",
        "rocky-linux-8-arm",
        "rocky-linux-9",
        "rocky-linux-9-arm",
        "amazon-linux-2023",
        "amazon-linux-2023-arm",
    ],
}


def get_os_config(os_name):
    """Return the full config for an OS, with region/subnet defaults applied."""
    if os_name not in OS_CONFIGS:
        raise KeyError(
            "Unknown OS '%s'. Supported: %s" % (os_name, ", ".join(sorted(OS_CONFIGS)))
        )
    config = dict(OS_CONFIGS[os_name])
    config.setdefault("region", DEFAULT_REGION)
    config.setdefault("subnet_id", DEFAULT_SUBNET_ID)
    return config
