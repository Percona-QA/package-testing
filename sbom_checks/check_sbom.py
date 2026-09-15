"""Command line entrypoint for the PXB SBOM checks.

    python3 -m sbom_checks.check_sbom --mode package
    python3 -m sbom_checks.check_sbom --mode docker --image percona/percona-xtrabackup:9.7.1
    python3 -m sbom_checks.check_sbom --mode dir --path ./sbom_checks/testdata

Exit codes:  0 pass   1 fail   77 skipped (nothing to check, gate is not enforce)
"""

import argparse
import subprocess
import sys
import uuid

from . import audit, config, discovery
from .backends import DOCKER_BIN, DockerBackend, LocalBackend

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_SKIP = 77


def _start_container(image):
    name = "pxb-sbom-cli-%s" % uuid.uuid4().hex[:8]
    container = subprocess.check_output([
        DOCKER_BIN, "run", "--name", name, "--entrypoint", "sleep",
        "-d", image, "infinity",
    ]).decode().strip()
    return container


def _stop_container(container):
    subprocess.call([DOCKER_BIN, "rm", "-f", container],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="check_sbom", description="Verify Percona XtraBackup SBOM files.")
    parser.add_argument("--mode", choices=("package", "docker", "dir"), default="package",
                        help="where to look: installed packages, a docker image, "
                             "or a plain directory")
    parser.add_argument("--image", help="docker image reference (--mode docker)")
    parser.add_argument("--path", help="directory holding SBOM files (--mode dir)")
    parser.add_argument("--package", help="package name to check (default: autodetect)")
    parser.add_argument("--expect-name", help="expected SBOM root component name")
    parser.add_argument("--expect-version",
                        help="expected SBOM root component version "
                             "(default: $PXB_VERSION)")
    parser.add_argument("--no-tools", action="store_true",
                        help="skip trivy and cyclonedx-cli even when installed")
    parser.add_argument("--strict-licenses", action="store_true",
                        help="require identical licence operand sets across formats")
    return parser


def run(args):
    container = None
    sbom_dir = args.path or config.sbom_dir()

    if args.mode == "docker":
        if not args.image:
            print("--mode docker requires --image")
            return EXIT_FAIL
        container = _start_container(args.image)
        backend = DockerBackend(container)
    elif args.mode == "dir":
        if not sbom_dir:
            print("--mode dir requires --path (or $%s)" % config.ENV_DIR)
            return EXIT_FAIL
        backend = LocalBackend()
    else:
        backend = LocalBackend()

    try:
        sets, considered = discovery.discover(backend, sbom_dir=sbom_dir)

        print("discovery:")
        for note in considered:
            print("  %s" % note)

        mode = config.check_mode()
        decision = config.decide(mode, bool(sets))

        if decision == config.SKIP_ALL:
            print("%s is off -- nothing checked" % config.ENV_CHECK_MODE)
            return EXIT_SKIP
        if decision == config.SKIP_ABSENT:
            print(config.absent_message(args.image or args.package or "this system",
                                        considered))
            return EXIT_SKIP
        if decision == config.FAIL_ABSENT:
            print(config.absent_message(args.image or args.package or "this system",
                                        considered))
            return EXIT_FAIL

        expect_name = args.expect_name
        expect_version = args.expect_version or config.expect_version()
        # Also for docker: the image installs the rpm, so the root component can
        # be cross-checked against the package the same way.
        if args.mode in ("package", "docker") and not expect_name:
            expect_name = discovery.expected_root_name(backend, sets[0])
            if not expect_version and expect_name:
                expect_version = discovery.installed_version(backend, expect_name)

        failed = False
        for sbom_set in sets:
            report = audit.audit(
                backend, sbom_set,
                expect_name=expect_name, expect_version=expect_version,
                strict_licenses=args.strict_licenses or None,
                run_tools=not args.no_tools,
            )
            print("")
            print(report.text())
            for note in report.tool_notes:
                print("  %s" % note)

            if not report.ok:
                failed = True

            if report.vuln_findings:
                vmode = config.vuln_mode()
                print("  vulnerability scan findings (%s=%s):" % (config.ENV_VULN_MODE, vmode))
                print(report.vuln_text())
                if vmode == config.ENFORCE:
                    failed = True
                else:
                    print("  not failing the run: %s is %r, not %r"
                          % (config.ENV_VULN_MODE, vmode, config.ENFORCE))

        return EXIT_FAIL if failed else EXIT_OK
    finally:
        if container:
            _stop_container(container)


def main(argv=None):
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
