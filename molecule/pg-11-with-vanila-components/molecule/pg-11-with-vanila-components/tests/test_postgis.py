import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_create_postigs_extension(host):
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION \"postgis\";'")
        assert install_extension.rc == 0, install_extension.stderr
        assert install_extension.stdout.strip("\n") == "CREATE EXTENSION", install_extension.stderr


def test_show_postgresql_version(host):
    rel = host.system_info.distribution
    cmd = ""
    if rel.lower() in ["debian", "ubuntu"]:
        cmd = "apt list *postgresql*"
    elif rel.lower() in ["redhat", "centos", 'rhel']:
        cmd = "yum list --show-duplicates *postgresql*"
    with host.sudo():
        result = host.run(cmd)
        print(result.stdout)
