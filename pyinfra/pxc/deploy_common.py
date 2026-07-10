"""pyinfra deploy for the PXC joiner nodes (pxc2, pxc3).

Port of pxc{80,84}-common-install/tasks/main.yml (non-pro, install).
Must run AFTER deploy_bootstrap.py, one host at a time:

    pyinfra -y --limit joiners --serial inventory.py deploy_common.py \
        --data product=pxc80 --data install_repo=testing \
        --data check_version=yes \
        --data git_account=Percona-QA --data testing_branch=master
"""

from pyinfra import host
from pyinfra.operations import dnf, server, systemd

from tasks import prep, pxc_config, pxc_install, repo, system

product = host.data.get("product", "pxc80")
install_repo = host.data.get("install_repo") or "main"
check_version = host.data.get("check_version") or "yes"
git_account = host.data.get("git_account") or "Percona-QA"
testing_branch = host.data.get("testing_branch") or "master"
# empty for the install test type -> the telemetry-blocked re-install runs,
# same as the molecule converge (upgrade flows will set this later)
upgrade_repo = host.data.get("upgrade_repo") or ""

prep.system_prep(product, git_account, testing_branch)
repo.enable_repo(product, install_repo)
prep.pre_install_fixes(bootstrap=False)
pxc_install.install_pxc(product, phase="initial")

pxc_config.deploy_mysql_config()
pxc_config.deploy_root_mycnf()
pxc_config.deploy_certs()

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
