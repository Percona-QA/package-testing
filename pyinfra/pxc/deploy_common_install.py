"""pyinfra deploy for the PXC joiner nodes (pxc2, pxc3) - INSTALL phase.

First of the two joiner phases. This part is cluster-independent (prep,
system upgrade, repo setup, package install, config, certs), so it runs on
both joiners CONCURRENTLY (default parallelism) to match the concurrency the
molecule/ansible linear strategy had on its non-throttled tasks:

    pyinfra -y --limit joiners inventory.py deploy_common_install.py \
        --data product=pxc80 --data install_repo=testing \
        --data check_version=yes \
        --data git_account=Percona-QA --data testing_branch=master

The cluster-forming phase (mysql start/join, checks, telemetry) lives in
deploy_common_cluster.py and MUST run after this, with --parallel 1.
"""

from tasks import prep, pxc_config, pxc_install, repo, runvars

product = runvars.product()

prep.system_prep(product, runvars.git_account(), runvars.testing_branch())
repo.enable_repo(product, runvars.install_repo())
prep.pre_install_fixes(bootstrap=False)
pxc_install.install_pxc(product, phase="initial")

pxc_config.deploy_mysql_config()
pxc_config.deploy_root_mycnf()
pxc_config.deploy_certs()
