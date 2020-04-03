import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_create_postigs_extension(host):
    with host.sudo("postgres"):
        install_extension = host.run("psql -c 'CREATE EXTENSION \"postgis\";'")
        assert install_extension.rc == 0, install_extension.stderr
        assert install_extension.stdout.strip("\n") == "CREATE EXTENSION", install_extension.stderr
