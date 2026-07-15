"""pyinfra deploy for the PXC joiner nodes (pxc2, pxc3) - CLUSTER phase.

Second of the two joiner phases. Runs AFTER deploy_common_install.py, with
--parallel 1 (NOT --serial): this keeps pyinfra's per-operation barrier across
the joiners so the wsrep_cluster_size==3 check runs only after every joiner has
started mysql, while still executing each operation one host at a time (no
concurrent SST joins, no concurrent restarts that would drop cluster quorum).
--serial would run the whole deploy on pxc2 first, so its cluster-size check
would see only 2 nodes and fail. This mirrors the molecule scenario's ansible
linear strategy + throttle:1.

    pyinfra -y --limit joiners --parallel 1 inventory.py deploy_common_cluster.py \
        --data product=pxc80 --data install_repo=testing \
        --data check_version=yes \
        --data git_account=Percona-QA --data testing_branch=master
"""

from pyinfra import host
from pyinfra.operations import dnf, server, systemd

from tasks import pxc_install, runvars, system

product = runvars.product()
check_version = runvars.check_version()
upgrade_repo = runvars.upgrade_repo()

systemd.service(
    name="Start mysql service (join the cluster)",
    service="mysql",
    running=True,
)

server.shell(name="Print PXC version", commands=["mysqld --version"])

if check_version == "yes":
    server.shell(
        name="Check PXC version",
        commands=["/package-testing/version_check.sh {}".format(product)],
    )
    if product == "pxc80":
        server.shell(
            name="Check PXC package versions",
            commands=["/package-testing/package_check.sh pxc80"],
        )

server.shell(
    name="Run bats tests for mysql init scripts",
    commands=[
        "sleep {}; /usr/local/bin/bats"
        " /package-testing/bats/pxc-init-scripts.bats".format(
            host.data.get("sleep_before_tests", 0)
        )
    ],
)

systemd.service(
    name="Start mysql service after init-scripts tests",
    service="mysql",
    running=True,
)

server.shell(
    name="Check that the PXC cluster is up and running (size 3)",
    commands=[
        "mysql -e \"SHOW GLOBAL STATUS LIKE 'wsrep_cluster_size';\""
        " | awk '{print$2}' | sed -n '2 p' | grep '3'"
    ],
)

# Telemetry checks: re-install, block the telemetry server, install again -
# expected result: telemetry_uuid has only the instance id
pxc_install.install_pxc(product, phase="post_cluster")

if system.distro_id() == "rhel":
    dnf.packages(
        name="Install iptables on RHEL",
        packages=["iptables", "iptables-services"],
    )
    if product == "pxc80":
        systemd.service(
            name="Enable and start iptables service",
            service="iptables",
            running=True,
            enabled=True,
        )

if upgrade_repo == "" and (product == "pxc84" or not system.is_amazon()):
    server.shell(
        name="Block check-dev.percona.com (telemetry server)",
        commands=["iptables -A OUTPUT -d check-dev.percona.com -j DROP"],
    )

if upgrade_repo == "":
    pxc_install.install_pxc(product, phase="telemetry_blocked")

server.shell(
    name="Output telemetry_uuid content",
    commands=["cat /usr/local/percona/telemetry_uuid"],
)

if not system.is_amazon():
    server.shell(
        name="Verify telemetry version and package installation",
        commands=["/package-testing/check_tel_ver_pack.sh"],
    )

server.shell(
    name="List installed percona packages",
    commands=[
        "(dpkg -l 2>/dev/null || rpm -qa)"
        " | grep -iE 'percona|sysbench|mysql|mongo|proxysql|maria' || true"
    ],
)
