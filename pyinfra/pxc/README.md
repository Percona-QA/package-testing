# PXC package testing with pyinfra

pyinfra-based variant of the molecule PXC package tests
(`package-testing/molecule/pxc/`). Creates the same 3-node Percona XtraDB
Cluster on EC2 and runs the same checks, using
[pyinfra](https://pyinfra.com) instead of molecule/ansible.

Current scope: **install** test type, products **pxc80** and **pxc84**,
non-pro packages, all OSes supported by the corresponding molecule job.

## How it works

| molecule | pyinfra |
|---|---|
| `create_noble.yml` (molecule-ec2 driver) | `provision.py` (boto3) |
| IP JSON files + jq + envfile + `MOLECULE_ENV_FILE` | state JSON + `inventory.py` |
| `pxcXX-bootstrap-install` scenario (pxc1) | `deploy_bootstrap.py` |
| `pxcXX-common-install` scenario (pxc2/pxc3, `throttle: 1`) | `deploy_common.py` with `--serial` |
| `playbooks/logsbackup.yml` | `deploy_logsbackup.py` |
| `destroy_noble.yml` | `destroy.py` |

- `provision.py` launches 3 identical instances (AMI/type/subnet/security
  group/keypair/tags identical to the molecule job, see `os_config.py`) and
  writes a state JSON with instance ids and public/private IPs.
- `inventory.py` turns the state JSON into a pyinfra inventory with two
  groups: `bootstrap` (pxc1) and `joiners` (pxc2, pxc3). Each host gets the
  three private IPs (`pxc1_ip`/`pxc2_ip`/`pxc3_ip`) and its own `man_ip`,
  which feed the `wsrep_cluster_address`/`wsrep_node_address` template.
- `deploy_bootstrap.py` installs the packages and starts
  `mysql@bootstrap.service`; `deploy_common.py` joins pxc2 and pxc3 one at a
  time and asserts `wsrep_cluster_size == 3`, then runs the telemetry-blocked
  re-install checks. The step-by-step logic is a 1:1 port of the molecule
  converge tasks (see `tasks/`).

## Requirements

```
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt
```

AWS credentials via the usual env vars (`AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`). SSH access needs the `molecule-pkg-tests` private
key (Jenkins credential `MOLECULE_AWS_PRIVATE_KEY`).

## Running locally

```
export PXC_SSH_KEY_PATH=~/.ssh/molecule-pkg-tests.pem
./run.sh pxc80 ubuntu-noble testing
```

Or step by step:

```
export PXC_STATE_FILE=$PWD/pxc-state.json
export PXC_SSH_KEY_PATH=~/.ssh/molecule-pkg-tests.pem

python3 provision.py --os ol-9 --product pxc80 \
    --job-name local-test --build-number 0 --state-file "$PXC_STATE_FILE"

pyinfra -y --limit bootstrap inventory.py deploy_bootstrap.py \
    --data product=pxc80 --data install_repo=testing --data check_version=yes \
    --data git_account=Percona-QA --data testing_branch=master

pyinfra -y --limit joiners --serial inventory.py deploy_common.py \
    --data product=pxc80 --data install_repo=testing --data check_version=yes \
    --data git_account=Percona-QA --data testing_branch=master

pyinfra -y inventory.py deploy_logsbackup.py \
    --data workspace=$PWD --data test_phase=install

python3 destroy.py --state-file "$PXC_STATE_FILE"
```

Inspect the inventory without connecting: `pyinfra inventory.py debug-inventory`.

## `--data` variables

| name | default | meaning |
|---|---|---|
| `product` | `pxc80` | `pxc80` or `pxc84` |
| `install_repo` | `main` | `testing` / `main` / `experimental` |
| `check_version` | `yes` | run `version_check.sh` / `package_check.sh` |
| `git_account` | `Percona-QA` | GitHub org of package-testing to fetch on nodes |
| `testing_branch` | `master` | package-testing branch to fetch on nodes |
| `upgrade_repo` | `` (empty) | reserved for future upgrade flows; empty enables the telemetry-blocked re-install, same as molecule |
| `workspace` / `test_phase` | `.` / `install` | logsbackup destination |

Environment variables (needed by `inventory.py`): `PXC_STATE_FILE`,
`PXC_SSH_KEY_PATH`.

## Jenkins

Jobs `pxc-package-testing-pyinfra` (per-OS worker) and
`pxc-package-testing-pyinfra-parallel` (fan-out) live in
[Percona-Lab/jenkins-pipelines](https://github.com/Percona-Lab/jenkins-pipelines)
under `pxc/jenkins/`. The worker: provision -> deploy bootstrap -> deploy
common -> logs backup + destroy + tag-based cleanup safety net (instances are
tagged with `job-name`/`build-number`, like the molecule job).

## Cleanup

`destroy.py --state-file <file>` terminates the instances from a state file;
`destroy.py --by-tags --job-name X --build-number N` terminates by tags in
both used regions (us-west-1 and us-west-2 - rocky-linux AMIs live in
us-west-2, see `os_config.py`).
