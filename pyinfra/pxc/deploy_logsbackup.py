"""Fetch /var/log from every node into the Jenkins workspace.

Replaces molecule/pxc/playbooks/logsbackup.yml. Run against the full
inventory (no --limit):

    pyinfra -y inventory.py deploy_logsbackup.py \
        --data workspace=$WORKSPACE --data test_phase=install

Tarballs land in <workspace>/PXC/<phase>_<private_ip>/ so the existing
`archiveArtifacts 'PXC/**/*.tar.gz'` Jenkins step keeps working.
"""

import os

from pyinfra import host
from pyinfra.operations import files, server

workspace = host.data.get("workspace") or "."
test_phase = host.data.get("test_phase") or "install"
man_ip = host.data.get("man_ip")
ssh_user = host.data.get("ssh_user")

archive_name = "{}_{}_logs.tar.gz".format(test_phase, man_ip)
remote_archive = "/tmp/" + archive_name
local_dir = os.path.join(workspace, "PXC", "{}_{}".format(test_phase, man_ip))
os.makedirs(local_dir, exist_ok=True)

server.shell(
    name="Archive /var/log",
    commands=[
        # tar exits 1 on 'file changed as we read it' - fine for log capture
        "tar -czf {} -C / var/log || [ $? -eq 1 ]".format(remote_archive),
        "chown {} {}".format(ssh_user, remote_archive),
    ],
)

files.get(
    name="Fetch the logs archive",
    src=remote_archive,
    dest=os.path.join(local_dir, archive_name),
    _sudo=False,
)
