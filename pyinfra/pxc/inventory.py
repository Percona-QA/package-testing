"""pyinfra inventory built from the state JSON written by provision.py.

Required environment variables (set by the Jenkins job or run.sh):
  PXC_STATE_FILE    path to the state JSON from provision.py
  PXC_SSH_KEY_PATH  path to the SSH private key (mode 0600)

Groups:
  bootstrap  pxc1 (bootstraps the cluster)
  joiners    pxc2, pxc3 (join the running cluster)
"""

import json
import os

_state_file = os.environ["PXC_STATE_FILE"]
_ssh_key = os.environ["PXC_SSH_KEY_PATH"]

with open(_state_file) as _handle:
    _state = json.load(_handle)

_ips = {node["role_name"]: node["private_ip"] for node in _state["nodes"]}


def _host(node):
    return (
        node["public_ip"],
        {
            "ssh_user": _state["ssh_user"],
            "ssh_key": _ssh_key,
            "ssh_known_hosts_file": "/dev/null",
            "ssh_strict_host_key_checking": "off",
            # everything the deploys do requires root
            "_sudo": True,
            "node_name": node["name"],
            "role_name": node["role_name"],
            # same semantics as molecule's man_ip: this node's private IP
            "man_ip": node["private_ip"],
            # molecule staggers the bats tests on pxc3 via this host var
            "sleep_before_tests": 40 if node["role_name"] == "pxc3" else 0,
            "pxc1_ip": _ips["pxc1"],
            "pxc2_ip": _ips["pxc2"],
            "pxc3_ip": _ips["pxc3"],
        },
    )


bootstrap = [_host(n) for n in _state["nodes"] if n["role"] == "bootstrap"]
joiners = [_host(n) for n in _state["nodes"] if n["role"] == "joiner"]
