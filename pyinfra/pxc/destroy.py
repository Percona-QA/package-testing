#!/usr/bin/env python3
"""Terminate EC2 instances created by provision.py.

Two modes:
  - default: terminate the instance ids listed in the state file
        python destroy.py --state-file ./pxc-state.json
  - fallback: terminate everything matching the job-name/build-number tags
        python destroy.py --by-tags --job-name X --build-number N

A missing or empty state file is not an error (mirrors molecule destroy),
so this is safe to run unconditionally in a Jenkins post step.
"""

import argparse
import json
import os
import sys

import boto3

from os_config import DEFAULT_REGION, ROCKY_REGION

# Regions the job may create instances in (see os_config.py).
ALL_REGIONS = [DEFAULT_REGION, ROCKY_REGION]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-file", default=None,
                        help="State JSON written by provision.py")
    parser.add_argument("--by-tags", action="store_true",
                        help="Terminate by job-name/build-number tags instead")
    parser.add_argument("--job-name", default=None, help="job-name tag value")
    parser.add_argument("--build-number", default=None,
                        help="build-number tag value")
    return parser.parse_args()


def terminate(region, instance_ids):
    if not instance_ids:
        return
    ec2 = boto3.client("ec2", region_name=region)
    print("Terminating in {}: {}".format(region, instance_ids))
    ec2.terminate_instances(InstanceIds=instance_ids)
    ec2.get_waiter("instance_terminated").wait(InstanceIds=instance_ids)
    print("Terminated: {}".format(instance_ids))


def destroy_from_state(state_file):
    if not os.path.isfile(state_file):
        print("State file {} not found, nothing to destroy".format(state_file))
        return
    try:
        with open(state_file) as handle:
            state = json.load(handle)
    except (ValueError, OSError) as exc:
        print("Could not read state file {}: {}".format(state_file, exc))
        return
    instance_ids = [
        n["instance_id"] for n in state.get("nodes", []) if n.get("instance_id")
    ]
    if not instance_ids:
        print("No instances recorded in {}, nothing to destroy".format(state_file))
        return
    terminate(state["region"], instance_ids)


def destroy_by_tags(job_name, build_number):
    for region in ALL_REGIONS:
        ec2 = boto3.client("ec2", region_name=region)
        described = ec2.describe_instances(
            Filters=[
                {"Name": "tag:job-name", "Values": [job_name]},
                {"Name": "tag:build-number", "Values": [str(build_number)]},
                {"Name": "instance-state-name",
                 "Values": ["pending", "running", "stopping", "stopped"]},
            ]
        )
        instance_ids = [
            i["InstanceId"]
            for r in described["Reservations"]
            for i in r["Instances"]
        ]
        if instance_ids:
            terminate(region, instance_ids)
        else:
            print("No instances tagged {}/{} in {}".format(
                job_name, build_number, region))


def main():
    args = parse_args()
    if args.by_tags:
        if not args.job_name or args.build_number is None:
            sys.exit("--by-tags requires --job-name and --build-number")
        destroy_by_tags(args.job_name, args.build_number)
    else:
        if not args.state_file:
            sys.exit("Provide --state-file (or use --by-tags)")
        destroy_from_state(args.state_file)


if __name__ == "__main__":
    main()
