# PXB SBOM checks

Verifies the SBOM files Percona XtraBackup ships with each artifact — in
**installed rpm/deb packages**, in **docker images**, and in a plain
**directory** of files you downloaded.

PXB ships four files per artifact, all generated together:

| File | Format |
|---|---|
| `percona-xtrabackup-NN.cdx.json` | CycloneDX |
| `percona-xtrabackup-NN.spdx.json` | SPDX |
| `percona-xtrabackup-NN.sbom.txt` | fixed-width table (NAME/VERSION/LICENSE/LINKAGE/ORIGIN) |
| `percona-xtrabackup-NN.licenses.txt` | `name version license` per line |

## The gate

PXB does not ship SBOM files yet. The rule is **absence is tolerated, presence
is strict**, so these checks can merge without breaking a single current build
and go live automatically the moment packaging lands.

| `SBOM_CHECK_MODE` | files absent | files present and bad |
|---|---|---|
| `off` | skip | skip |
| `warn` *(default)* | skip | **fail** |
| `enforce` | **fail** | **fail** |

`SBOM_VULN_MODE` (same values, default `warn`) gates the trivy scan separately —
a new upstream CVE in a vendored library is a different signal from a malformed
SBOM, and sharing one red light means people learn to ignore both.

Other environment variables:

| Variable | Meaning |
|---|---|
| `SBOM_DIR` | check this directory instead of discovering. Escape hatch for verifying a pre-release package. |
| `PXB_VERSION` | the version the SBOM must describe. The only way to check this for a downloaded directory, which has no installed package to compare against. |
| `SBOM_EXTERNAL_TOOLS` | run trivy/cyclonedx-cli. **On by default in the molecule job**, which installs both on the target; set to `0` to skip them |
| `SBOM_CHECK_OCI` | also check the SBOM attached to a docker image as an OCI referrer (off: percona-docker publishes none today) |
| `SBOM_LICENSE_STRICT` | require identical licence operand sets across formats, not just overlap |
| `DOCKER_BIN`, `TRIVY_BIN`, `CYCLONEDX_BIN`, `ORAS_BIN` | binary overrides |

## Running it from your local host

Everything here runs on a laptop — no Jenkins agent, no VM. Three things you
can point it at: SBOM files **downloaded to a directory**, a **published docker
image**, and the **packages installed on this machine** (Linux only).

### Quickest: the CLI

The library is stdlib-only, so this needs no virtualenv and no `pip install`:

```bash
cd /path/to/package-testing

# SBOM files downloaded to a directory
python3 -m sbom_checks.check_sbom --mode dir --path ~/Downloads/pxb-sbom

# a published docker image
python3 -m sbom_checks.check_sbom \
    --mode docker --image percona/percona-xtrabackup:8.0.35-33

# the packages installed on this machine (Linux only)
python3 -m sbom_checks.check_sbom --mode package
```

Exit codes: `0` pass, `1` fail, `77` nothing to check.

### The pytest entrypoints

Use these when you want per-check pass/fail granularity or a junit report. They
need pytest, and nothing else — in particular **do not**
`pip install -r docker-image-tests/pxb/requirements.txt`: it pins
`pytest==5.2.1` / `testinfra==3.2.0` for the CI image and will not build on a
modern python. Only `test_container_att.py` needs testinfra; the SBOM tests do
not, which is why they are invoked directly instead of through `./run.sh`.

`sbom_checks/requirements.txt` lists what this library needs: nothing for the
library itself, and `pytest` only for the self-test.

One-time setup (a venv is required on Homebrew python, which is PEP 668
externally-managed):

```bash
python3 -m venv ~/.venvs/pxb-sbom
~/.venvs/pxb-sbom/bin/pip install pytest
```

**SBOM files in a directory** — `pytest-tests/test_pxb_sbom.py`:

```bash
cd /path/to/package-testing
SBOM_DIR=~/Downloads/pxb-sbom PXB_VERSION=9.7.1-rc1 \
  ~/.venvs/pxb-sbom/bin/python -m pytest -v pytest-tests/test_pxb_sbom.py
```

`PXB_VERSION` is optional but worth setting: a downloaded directory has no
installed package to compare against, so without it the run checks structure,
licences and cross-format consistency but **not which release the SBOM is for**.
With it, `test_root_component_is_the_expected_release` verifies the root
component in both the CycloneDX and SPDX documents. Comparison tolerates a
package release suffix, so an SBOM saying `9.7.1-rc1` satisfies
`PXB_VERSION=9.7.1-rc1.2`.

On a target host with PXB installed, the version is taken from the installed
package automatically. Setting `PXB_VERSION` *replaces* that expectation rather
than adding to it — when it is set the installed version is never consulted, so
the comparison is always SBOM-against-`PXB_VERSION`. A `PXB_VERSION` that
disagrees with the installed package is not itself reported.

Only the version is overridable. The expected **name** always comes from the
installed package, falling back to the SBOM filename stem — so in a directory
run the name check compares the root component inside the JSON against the
filename, and nothing stronger.

**A docker image** — `docker-image-tests/pxb/tests/test_pxb_sbom.py`:

```bash
cd /path/to/package-testing/docker-image-tests/pxb
PXB_DOCKER_ACC=percona PXB_VERSION=8.0.35-33 \
  ~/.venvs/pxb-sbom/bin/python -m pytest -v tests/test_pxb_sbom.py
```

The image reference is composed as `$PXB_DOCKER_ACC/percona-xtrabackup:$PXB_VERSION`
(`docker-image-tests/pxb/settings.py`), so use `perconalab` for pre-release
builds. Note that here `PXB_VERSION` is the image **tag**, not an assertion:
the image has the package installed, so the expected root component is read from
the rpm inside it (a tag like `8.0.35-33` against an rpm version of `8.0.35`).

### Useful modifiers

| Want | Add |
|---|---|
| assert which release the SBOM describes | `PXB_VERSION=9.7.1-rc1` |
| fail instead of skip when no SBOM is found | `SBOM_CHECK_MODE=enforce` |
| also run trivy / cyclonedx-cli | `SBOM_EXTERNAL_TOOLS=1` (needed for a directory run; the molecule and docker jobs already do) |
| fail on HIGH/CRITICAL CVEs | `SBOM_VULN_MODE=enforce` |
| require identical licences across formats | `SBOM_LICENSE_STRICT=1` |
| also check the registry-attached SBOM | `SBOM_CHECK_OCI=1` (needs `oras`) |
| use podman, or a docker CLI not named `docker` | `DOCKER_BIN=podman` |
| a junit report | `--junitxml=report.xml` |

`DOCKER_BIN` matters more often than it looks: if `docker` is a **shell alias**
for podman, the alias does not survive into `subprocess`, so it has to be passed
explicitly.

### Two things that will catch you out

- **Every SBOM test skips against today's artifacts.** PXB does not ship SBOM
  files yet, so that is the designed `warn` behaviour and not a broken setup.
  Run with `SBOM_CHECK_MODE=enforce` to turn the skip into a hard stop that
  prints the full discovery trail — every location searched, and how many files
  the installed package declared. Discovery happens in a fixture, so pytest
  reports this as one error per test rather than a single failure; they all
  carry the same `SBOM-NOT-SHIPPED` message.
- **Do not leave `SBOM_DIR` exported when checking a docker image.** The docker
  entrypoint passes it to discovery too, where it is a path *inside the
  container*, not on your host — a stale export silently redirects the search.

### The self-test

Runs the whole pipeline against the prototype fixtures in `testdata/`, with no
infrastructure at all:

```bash
~/.venvs/pxb-sbom/bin/python -m pytest -v sbom_checks/tests/
```

## Where it is wired in

| Consumer | Runs on | Invoked by |
|---|---|---|
| `pytest-tests/test_pxb_sbom.py` | the molecule target host | `tasks/check_pxb_sbom.yml`, included from `playbooks/pxb_{80,84,97,innovation_lts}.yml` |
| `docker-image-tests/pxb/tests/test_pxb_sbom.py` | the Jenkins agent | the existing `docker-image-tests/pxb/run.sh` |
| `sbom_checks.check_sbom` (CLI) | anywhere | by hand; not used by CI |

Both Jenkins jobs expose the gate as a build parameter (in the
`jenkins-pipelines` repo): `pxb-package-testing-molecule` has `SBOM_CHECK_MODE`
and `SBOM_VULN_MODE` — passed through from `pxb-pt-testing-molecule-all` —
and `pxb-docker-tests` adds `SBOM_CHECK_OCI`.

## What is checked

1. **Discovery** — `$SBOM_DIR`, then `rpm -ql`/`dpkg -L` of the installed
   `percona-xtrabackup*` package, then `find` under
   `/usr/share/percona-xtrabackup*`. Both rpm and deb install the files in the
   package's own directory (`/usr/share/percona-xtrabackup-97/sbom/`), so the
   fallback is scoped to it and cannot pick up SBOMs belonging to other
   packages. Filenames are still never hardcoded. Every candidate location and
   rejection is printed even on a skip, because otherwise a broken discovery
   ladder is indistinguishable from "no SBOM shipped yet".
2. **One set only** — a set is identified by `(directory, filename stem)`, so a
   stale or backup copy in a sibling directory stays a separate set rather than
   merging with the real one. Finding more than one set is reported: only the
   first is validated, and silently mixing CycloneDX from one directory with
   SPDX from another would make the consistency check meaningless.
3. **Completeness** — all four formats are present.
4. **Structure** — CycloneDX `bomFormat`/`specVersion`/`serialNumber`, unique
   `bom-ref`, every component carries name/version/purl/licence; SPDX
   `spdxVersion`/`SPDXID`/`dataLicense`, a `DESCRIBES` root, every package
   reachable by `CONTAINS`, unique and charset-legal SPDXIDs.
5. **Identity** — the SBOM's root component matches what it should describe.
   The version comes from the installed package, or from `$PXB_VERSION` when
   set (the only option for a directory of downloaded files); the name comes
   from the installed package, falling back to the filename stem. Reported
   separately from structural problems, because "this SBOM is for the wrong
   release" and "this SBOM is malformed" are different failures.
6. **Cross-format consistency** — three tiers, reported separately so a
   licence-vocabulary difference cannot masquerade as a missing component:
   all four files describe exactly the same `(name, version)` set; every
   component states a licence at all; and those licences are equivalent once
   normalised.
7. **Schema** — `cyclonedx validate`, against the spec version declared *in the
   document* rather than a hardcoded one.
8. **Vulnerabilities** — `trivy sbom --severity HIGH,CRITICAL --ignore-unfixed`.

   Both tools are optional, and each reports an explicit status — `ok`,
   `missing` or `failed` — rather than just findings. A tool that did not run
   makes its check **skip**; it can never pass on an empty result, which is what
   made an absent binary look like a clean validation. `failed` also keeps a
   trivy that could not start (a rate-limited vulnerability-DB pull from
   ghcr.io, say) from being reported as a vulnerability.
9. **OCI referrers** — opt-in, for docker images only.

## Notes and limitations

- **Debian gzips files under `/usr/share/doc`**, so an SBOM shipped there
  would arrive as `.json.gz` on deb and plain on rpm. PXB installs under
  `/usr/share/percona-xtrabackup-NN/` instead, where nothing is compressed, but
  the reader still sniffs the gzip magic bytes — never the file extension or
  `os_family` — so either layout works.
- **The molecule job installs both tools on the target** via
  `tasks/install_sbom_tools.yml` — trivy pinned to 0.74.0 (matching
  `installTrivy.groovy`) and cyclonedx-cli from its latest release, both
  arch-aware. Installs are non-blocking: a platform where either will not run
  degrades to a skipped check, never a failed converge. Disable with the
  `SBOM_EXTERNAL_TOOLS` build parameter.
- **trivy currently finds almost nothing.** PXB purls are
  `pkg:generic/<name>@<version>`, which match CVE feeds poorly, and some
  components have version `unknown`. A green trivy result is not evidence of no
  vulnerabilities. Adding CPEs or type-specific purls upstream is what would
  make this meaningful.
- **`xxhash` legitimately appears twice** (standalone 0.8.3 and the copy bundled
  in lz4, 1.10.0). Consistency keys on `(name, version)`; deduplicating on name
  alone would produce false failures.
- SPDXIDs are mangled (`unordered_dense` → `SPDXRef-Package-unordered-dense`),
  so packages are matched on the `name` field, never on SPDXID.
