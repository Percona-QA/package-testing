#!/usr/bin/env python3
"""Provision 3 EC2 instances for PXC package testing (pyinfra variant).

Replicates the EC2 setup of package-testing/molecule/pxc/playbooks/create_noble.yml:
same AMIs, security group, keypair, subnet, instance profile and tags as the
molecule-based job, so the existing tag-based instance cleanup keeps working.

Writes a state JSON consumed by inventory.py and destroy.py.

Usage:
    python provision.py --os ol-9 --product pxc80 \
        --job-name pxc-package-testing-pyinfra --build-number 42 \
        --state-file ./pxc-state.json
"""

import argparse
import json
import socket
import sys
import time

import boto3

from os_config import (
    INSTANCE_PROFILE_ARN,
    KEY_NAME,
    ROOT_VOLUME_SIZE_GB,
    SECURITY_GROUP_PREFIX,
    SUPPORTED_OS,
    get_os_config,
)

NODES = [
    {"role": "bootstrap", "role_name": "pxc1"},
    {"role": "joiner", "role_name": "pxc2"},
    {"role": "joiner", "role_name": "pxc3"},
]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--os", required=True, dest="os_name",
                        help="OS to test, e.g. ol-9, ubuntu-noble, debian-12-arm")
    parser.add_argument("--product", required=True, choices=sorted(SUPPORTED_OS),
                        help="Product to test")
    parser.add_argument("--job-name", default="pxc-package-testing-pyinfra",
                        help="Jenkins job name (job-name tag)")
    parser.add_argument("--build-number", default="0",
                        help="Jenkins build number (build-number tag)")
    parser.add_argument("--state-file", required=True,
                        help="Path to write the state JSON")
    parser.add_argument("--region", default=None,
                        help="Override AWS region (default: per-OS)")
    parser.add_argument("--subnet-id", default=None,
                        help="Override subnet id (default: per-OS)")
    parser.add_argument("--key-name", default=KEY_NAME,
                        help="EC2 keypair name")
    parser.add_argument("--iit-billing-tag", default="pxc_package_testing",
                        help="Value for the iit-billing-tag instance tag")
    parser.add_argument("--ssh-wait-timeout", type=int, default=600,
                        help="Seconds to wait for TCP/22 on each instance")
    parser.add_argument("--settle-seconds", type=int, default=90,
                        help="Extra sleep after SSH is up (boot/cloud-init settle)")
    return parser.parse_args()


def ensure_security_group(ec2, vpc_id):
    """Return the id of the shared molecule SG, creating it if missing."""
    sg_name = "{}-{}".format(SECURITY_GROUP_PREFIX, vpc_id)
    existing = ec2.describe_security_groups(
        Filters=[
            {"Name": "group-name", "Values": [sg_name]},
            {"Name": "vpc-id", "Values": [vpc_id]},
        ]
    )["SecurityGroups"]
    if existing:
        return existing[0]["GroupId"]

    print("Creating security group {}".format(sg_name))
    sg_id = ec2.create_security_group(
        GroupName=sg_name,
        Description="Testing PXC package testing with Molecule",
        VpcId=vpc_id,
    )["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
            {
                "IpProtocol": "icmp",
                "FromPort": 8,
                "ToPort": -1,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
            {
                "IpProtocol": "-1",
                "UserIdGroupPairs": [{"GroupId": sg_id}],
            },
        ],
    )
    return sg_id


def write_state(args, region, os_config, echo=False):
    state = {
        "region": region,
        "os": args.os_name,
        "product": args.product,
        "ssh_user": os_config["ssh_user"],
        "job_name": args.job_name,
        "build_number": str(args.build_number),
        "nodes": NODES,
    }
    with open(args.state_file, "w") as state_file:
        json.dump(state, state_file, indent=2)
    if echo:
        print(json.dumps(state, indent=2))
    print("State written to {}".format(args.state_file))


def wait_for_ssh(host, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, 22), timeout=10):
                return
        except OSError:
            time.sleep(5)
    raise TimeoutError("Timed out waiting for SSH on {}:22".format(host))


def main():
    args = parse_args()

    if args.os_name not in SUPPORTED_OS[args.product]:
        sys.exit(
            "OS '{}' is not supported for product '{}'. Supported: {}".format(
                args.os_name, args.product, ", ".join(SUPPORTED_OS[args.product])
            )
        )

    os_config = get_os_config(args.os_name)
    region = args.region or os_config["region"]
    subnet_id = args.subnet_id or os_config["subnet_id"]

    ec2 = boto3.client("ec2", region_name=region)

    subnet = ec2.describe_subnets(SubnetIds=[subnet_id])["Subnets"][0]
    sg_id = ensure_security_group(ec2, subnet["VpcId"])

    print(
        "Launching 3x {} ({}) in {} / {}".format(
            os_config["image"], os_config["instance_type"], region, subnet_id
        )
    )
    reservation = ec2.run_instances(
        ImageId=os_config["image"],
        InstanceType=os_config["instance_type"],
        KeyName=args.key_name,
        MinCount=3,
        MaxCount=3,
        IamInstanceProfile={"Arn": INSTANCE_PROFILE_ARN},
        NetworkInterfaces=[
            {
                "DeviceIndex": 0,
                "SubnetId": subnet_id,
                "Groups": [sg_id],
                "AssociatePublicIpAddress": True,
            }
        ],
        BlockDeviceMappings=[
            {
                "DeviceName": os_config["root_device_name"],
                "Ebs": {
                    "VolumeType": "gp2",
                    "VolumeSize": ROOT_VOLUME_SIZE_GB,
                    "DeleteOnTermination": True,
                },
            }
        ],
    )
    instance_ids = [i["InstanceId"] for i in reservation["Instances"]]

    for node, instance_id in zip(NODES, instance_ids):
        name = "{}-{}-{}-{}-install-pyinfra".format(
            args.build_number, node["role_name"], args.product, args.os_name
        )
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[
                {"Key": "Name", "Value": name},
                {"Key": "ssh_user", "Value": os_config["ssh_user"]},
                {"Key": "iit-billing-tag", "Value": args.iit_billing_tag},
                {"Key": "job-name", "Value": args.job_name},
                {"Key": "build-number", "Value": str(args.build_number)},
            ],
        )
        node["name"] = name
        node["instance_id"] = instance_id

    # write the state early so destroy.py can clean up even if a later
    # wait step fails
    write_state(args, region, os_config)

    print("Waiting for instances to be running: {}".format(instance_ids))
    ec2.get_waiter("instance_running").wait(InstanceIds=instance_ids)

    described = ec2.describe_instances(InstanceIds=instance_ids)
    by_id = {
        i["InstanceId"]: i
        for r in described["Reservations"]
        for i in r["Instances"]
    }
    for node in NODES:
        instance = by_id[node["instance_id"]]
        node["public_ip"] = instance["PublicIpAddress"]
        node["private_ip"] = instance["PrivateIpAddress"]

    for node in NODES:
        print("Waiting for SSH on {} ({})".format(node["name"], node["public_ip"]))
        wait_for_ssh(node["public_ip"], args.ssh_wait_timeout)

    print("Waiting {}s for boot process to finish".format(args.settle_seconds))
    time.sleep(args.settle_seconds)

    write_state(args, region, os_config, echo=True)


if __name__ == "__main__":
    main()
