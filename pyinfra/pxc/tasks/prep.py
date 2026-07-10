"""Node preparation: port of molecule/pxc/playbooks/prepare.yml and
package-testing/tasks/test_prep.yml, plus the pre-install fixups from the
pxc{80,84}-{bootstrap,common}-install converge tasks.

Legacy branches for OSes outside the supported matrix (CentOS 7, Debian
buster, Amazon Linux 2) are intentionally not ported.
"""

from pathlib import Path

from pyinfra import host
from pyinfra.operations import apt, dnf, files, server

from tasks import system

PXC_DIR = Path(__file__).resolve().parents[1]
PUBLIC_KEYS = PXC_DIR.parents[1] / "molecule" / "pxc" / "playbooks" / "public_keys"

EPEL_GPG_KEY = "https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-{}"
EPEL_RELEASE_RPM = (
    "https://dl.fedoraproject.org/pub/epel/epel-release-latest-{}.noarch.rpm"
)


def _redhat_prep():
    distro = system.distro_id()
    major = system.major_version()

    if distro in ("rhel", "ol"):
        server.shell(
            name="Fix packaging locks and clear bad metadata",
            commands=[
                "killall -9 dnf dnf-automatic packagekitd yum || true",
                "rpm --rebuilddb || true",
                "dnf clean all || true",
                "rm -rf /var/cache/dnf || true",
            ],
        )

    # majors 8/9 only: the ansible original compares the version as a string
    # ('10' >= '8' is false), so EL10 and Amazon 2023 never get the keys there
    if major in (8, 9):
        server.shell(
            name="Install GPG keys for Percona repos",
            commands=[
                "rpm --import https://repo.percona.com/yum/RPM-GPG-KEY-Percona",
                "rpm --import https://repo.percona.com/yum/PERCONA-PACKAGING-KEY",
            ],
        )

    if distro in ("rhel", "ol") or (major == 8 and distro != "rocky"):
        server.shell(
            name="System upgrade for RedHat family",
            commands=["dnf upgrade -y --setopt=install_weak_deps=False"],
        )

    if major in (8, 9, 10):
        server.shell(
            name="Install GPG key for epel {}".format(major),
            commands=["rpm --import " + EPEL_GPG_KEY.format(major)],
        )
    # prepare.yml installs epel-release for the whole RedHat family on
    # majors 8 and 9 (including Rocky)
    if major in (8, 9):
        dnf.rpm(
            name="Setup epel {} repo".format(major),
            src=EPEL_RELEASE_RPM.format(major),
        )
    if major == 10:
        server.shell(name="Dnf update for epel 10", commands=["dnf update -y"])

    if not (major == 10 and not system.is_arm()):
        dnf.packages(
            name="Setup ca-certificates",
            packages=["ca-certificates"],
        )

    dnf.packages(
        name="Install needed packages for running tests",
        packages=["unzip", "wget", "python3", "jq", "net-tools"],
        latest=True,
    )

    if distro in ("rhel", "centos", "ol", "amzn"):
        server.shell(
            name="Clean and update package cache",
            commands=["dnf clean all", "dnf makecache"],
        )

    dnf.packages(name="Install firewalld if missing", packages=["firewalld"])
    if major in (8, 9):
        server.shell(
            name="Disable firewalld",
            commands=["systemctl stop firewalld && systemctl disable firewalld"],
        )


def _debian_prep():
    apt.update(name="Update the apt cache")
    server.shell(
        name="Upgrade deb packages",
        commands=["DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade"],
    )
    apt.packages(
        name="Install needed packages for running tests",
        packages=[
            "unzip",
            "wget",
            "gnupg",
            "gnupg2",
            "rsync",
            "acl",
            "jq",
            "net-tools",
            "systemd-sysv",
        ],
        latest=True,
    )


def _setup_debug_ssh_keys():
    # parity with prepare.yml: add the team public keys for debug access
    if not PUBLIC_KEYS.is_file():
        return
    ssh_user = host.data.get("ssh_user")
    if not ssh_user:
        return
    files.put(
        name="Upload debug public keys",
        src=str(PUBLIC_KEYS),
        dest="/tmp/molecule_public_keys",
        mode="644",
    )
    server.shell(
        name="Authorize debug public keys",
        commands=[
            "mkdir -p /home/{0}/.ssh"
            " && cat /tmp/molecule_public_keys >> /home/{0}/.ssh/authorized_keys"
            " && chown {0} /home/{0}/.ssh/authorized_keys"
            " && chmod 600 /home/{0}/.ssh/authorized_keys".format(ssh_user)
        ],
    )


def _download_package_testing(git_account, testing_branch):
    # test_prep.yml: the checks (version_check.sh etc.) run from /package-testing
    # on the target node, downloaded as a GitHub zip of the given branch
    server.shell(
        name="Download package-testing repo branch",
        commands=[
            "rm -rf /package-testing",
            "rm -f master.zip",
            'wget --no-check-certificate -O master.zip'
            ' "https://github.com/{}/package-testing/archive/{}.zip"'.format(
                git_account, testing_branch
            ),
            "unzip -q master.zip",
            "rm -f master.zip",
            'mv "package-testing-{}" /package-testing'.format(
                testing_branch.replace("/", "-")
            ),
        ],
    )
    server.shell(
        name="Install latest bats from github",
        commands=[
            "rm -f master.zip",
            "wget --no-check-certificate -O master.zip"
            " https://github.com/sstephenson/bats/archive/master.zip",
            "unzip -q master.zip",
            "rm -f master.zip",
            "bats-master/install.sh /usr/local",
            "rm -rf bats-master",
        ],
    )


def system_prep(product, git_account="Percona-QA", testing_branch="master"):
    """prepare.yml + test_prep.yml + the world.sql download from converge."""
    family = system.os_family()

    if product == "pxc80" and system.distro_id() in ("rhel", "ol"):
        server.shell(
            name="Update all dnf packages without reboot",
            commands=["dnf -y update"],
        )

    if family == "redhat":
        _redhat_prep()
    else:
        _debian_prep()

    _setup_debug_ssh_keys()
    _download_package_testing(git_account, testing_branch)

    if family == "redhat" and system.major_version() == 8:
        server.shell(
            name="Disable mysql dnf module on RHEL 8",
            commands=["dnf module disable mysql -y"],
        )

    server.shell(
        name="Download world database",
        commands=[
            "wget --no-check-certificate -P /package-testing"
            " https://raw.githubusercontent.com/Percona-QA/percona-qa/master/sample_db/world.sql"
        ],
    )


def pre_install_fixes(bootstrap):
    """OS fixups the converge tasks apply between repo setup and PXC install."""
    family = system.os_family()
    distro = system.distro_id()

    if bootstrap and family == "redhat" and system.major_version() == 8:
        dnf.packages(name="Install python3-libselinux", packages=["python3-libselinux"])

    if family == "redhat" and distro != "amzn":
        server.shell(
            name="Allow all users to connect to mysql (selinux)",
            commands=["setsebool -P mysql_connect_any 1"],
        )

    if distro == "ol":
        server.shell(name="Flush iptables", commands=["iptables -F"])

    if system.is_arm() and family == "debian":
        server.shell(
            name="Generate required locales",
            commands=["locale-gen en_US.UTF-8 en_IN.utf8"],
        )
        for line in ('LANG="en_US.UTF-8"', 'LC_ALL="en_US.UTF-8"'):
            files.line(
                name="Ensure /etc/default/locale has {}".format(line),
                path="/etc/default/locale",
                line=line,
            )
        files.file(
            name="Create empty usr.sbin.mysqld.in to avoid AppArmor error",
            path="/etc/apparmor.d/local/usr.sbin.mysqld.in",
            mode="644",
        )
