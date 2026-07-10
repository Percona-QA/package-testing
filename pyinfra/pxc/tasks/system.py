"""Fact helpers used by the PXC pyinfra deploys.

Equivalents of the ansible facts used by the molecule tasks:
  ansible_os_family                -> os_family()  ("debian" / "redhat")
  ansible_distribution             -> distro_id()  (os-release ID: ubuntu, debian,
                                      rhel, ol, rocky, amzn, centos)
  ansible_distribution_major_version -> major_version()
  ansible_architecture             -> arch() / is_arm()
"""

from pyinfra import host
from pyinfra.api import FactBase

DEBIAN_IDS = {"debian", "ubuntu"}
REDHAT_IDS = {"rhel", "centos", "ol", "rocky", "almalinux", "amzn", "fedora"}


class OsRelease(FactBase):
    """Parsed /etc/os-release as a dict."""

    command = "cat /etc/os-release"

    def process(self, output):
        info = {}
        for line in output:
            key, sep, value = line.partition("=")
            if sep:
                info[key.strip()] = value.strip().strip('"')
        return info


class MachineArch(FactBase):
    """Output of uname -m (x86_64 / aarch64)."""

    command = "uname -m"

    def process(self, output):
        return output[0].strip()


def os_info():
    return host.get_fact(OsRelease)


def distro_id():
    return os_info().get("ID", "")


def os_family():
    info = os_info()
    ids = {info.get("ID", "")} | set(info.get("ID_LIKE", "").split())
    if ids & DEBIAN_IDS:
        return "debian"
    if ids & REDHAT_IDS:
        return "redhat"
    return "unknown"


def major_version():
    version = os_info().get("VERSION_ID", "0")
    try:
        return int(version.split(".")[0])
    except ValueError:
        return 0


def arch():
    return host.get_fact(MachineArch)


def is_arm():
    return arch() == "aarch64"


def is_amazon():
    return distro_id() == "amzn"
