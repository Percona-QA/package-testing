"""pyinfra deploy for the PXC bootstrap node (pxc1).

Port of pxc{80,84}-bootstrap-install/tasks/main.yml (non-pro, install).

Run against the "bootstrap" inventory group:
    pyinfra -y --limit bootstrap inventory.py deploy_bootstrap.py \
        --data product=pxc80 --data install_repo=testing \
        --data check_version=yes \
        --data git_account=Percona-QA --data testing_branch=master
"""

from pyinfra import host
from pyinfra.operations import server

from tasks import prep, pxc_config, pxc_install, repo, system

product = host.data.get("product", "pxc80")
install_repo = host.data.get("install_repo") or "main"
# TODO: flip check_version to yes after initial debugging
check_version = host.data.get("check_version") or "no"
git_account = host.data.get("git_account") or "Percona-QA"
testing_branch = host.data.get("testing_branch") or "master"

prep.system_prep(product, git_account, testing_branch)
repo.enable_repo(product, install_repo)
prep.pre_install_fixes(bootstrap=True)
pxc_install.install_pxc(product, phase="initial")

if product == "pxc80":
    server.shell(
        name="Check telemetry (enabled)",
        commands=["/package-testing/check_telemetry.sh pxc -e"],
    )
    server.shell(
        name="Output telemetry_uuid content",
        commands=["cat /usr/local/percona/telemetry_uuid"],
    )

server.shell(name="Stop mysql service", commands=["systemctl stop mysql"])

pxc_config.deploy_mysql_config()
pxc_config.deploy_certs()

server.shell(
    name="Bootstrap the cluster",
    commands=["systemctl start mysql@bootstrap.service"],
)

if system.os_family() == "redhat":
    server.shell(
        name="Set root password",
        commands=["/package-testing/setpass_57.sh"],
    )
    pxc_config.deploy_root_mycnf()

server.shell(name="Print PXC version", commands=["mysqld --version"])
server.shell(
    name="Print wsrep provider version",
    commands=[
        "mysql -uroot --password='U?fY)9s7|3gxUm'"
        " -e \"SHOW STATUS LIKE 'wsrep_provider_version';\""
    ],
)
server.shell(
    name="Print InnoDB version",
    commands=[
        "mysql -uroot --password='U?fY)9s7|3gxUm' -e 'SELECT @@INNODB_VERSION;'"
    ],
)

if check_version == "yes":
    server.shell(
        name="Check PXC version",
        commands=["/package-testing/version_check.sh {}".format(product)],
    )

if product == "pxc80" and not system.is_amazon():
    server.shell(
        name="Verify telemetry version and package installation",
        commands=["/package-testing/check_tel_ver_pack.sh"],
    )

server.shell(
    name="Give the cluster time to settle before joiners start",
    commands=["sleep 60"],
)
