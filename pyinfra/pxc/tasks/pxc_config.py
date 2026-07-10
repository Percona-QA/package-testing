"""PXC configuration: wsrep my.cnf template, SSL certs, root .my.cnf."""

from pathlib import Path

from pyinfra import host
from pyinfra.operations import files

from tasks import system

PXC_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PXC_DIR / "templates"
REPO_ROOT = PXC_DIR.parents[1]
CERTS_DIR = REPO_ROOT / "support-files" / "certs"
ROOT_MYCNF = REPO_ROOT / "templates" / "my_57.j2"  # static, no template vars


def deploy_mysql_config():
    """Deploy the wsrep config with the 3 cluster IPs and this node's IP."""
    template_vars = {
        "PXC1_IP": host.data.get("pxc1_ip"),
        "PXC2_IP": host.data.get("pxc2_ip"),
        "PXC3_IP": host.data.get("pxc3_ip"),
        "man_ip": host.data.get("man_ip"),
    }
    if system.os_family() == "redhat":
        files.template(
            name="Copy PXC config (rpm)",
            src=str(TEMPLATES_DIR / "my_rpm_80.j2"),
            dest="/etc/my.cnf",
            **template_vars
        )
    else:
        files.template(
            name="Configure PXC on debian/ubuntu",
            src=str(TEMPLATES_DIR / "my_8.j2"),
            dest="/etc/mysql/my.cnf",
            mode="640",
            user="mysql",
            group="root",
            **template_vars
        )


def deploy_certs():
    files.sync(
        name="Copy pxc certs",
        src=str(CERTS_DIR),
        dest="/etc/mysql/certs",
    )


def deploy_root_mycnf():
    """Root credentials file - RedHat family only, matching molecule."""
    if system.os_family() == "redhat":
        files.put(
            name="Copy .my.cnf with credentials",
            src=str(ROOT_MYCNF),
            dest="/root/.my.cnf",
            mode="640",
            user="root",
            group="root",
        )
