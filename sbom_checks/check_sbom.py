"""Command line entrypoint for the SBOM checks.

    python3 -m sbom_checks.check_sbom --mode package
    python3 -m sbom_checks.check_sbom --mode docker --image percona/percona-xtrabackup:9.7.1
    python3 -m sbom_checks.check_sbom --mode dir --path ./sbom_checks/testdata/pxb
    python3 -m sbom_checks.check_sbom --product ps --mode dir --path ./sbom_checks/testdata/ps

--product defaults to $SBOM_PRODUCT, else pxb.

Exit codes:  0 pass   1 fail   77 skipped (nothing to check, gate is not enforce)
"""

import argparse
import subprocess
import sys
import uuid

from . import audit, config, discovery, external_tools, products
from .backends import DOCKER_BIN, DockerBackend, LocalBackend

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_SKIP = 77


def _start_container(image):
    name = "sbom-cli-%s" % uuid.uuid4().hex[:8]
    container = subprocess.check_output([
        DOCKER_BIN, "run", "--name", name, "--entrypoint", "sleep",
        "-d", image, "infinity",
    ]).decode().strip()
    return container


def _stop_container(container):
    subprocess.call([DOCKER_BIN, "rm", "-f", container],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _tool_problems(report, sbom_set, run_tools):
    """Requested tools that did not produce a usable result.

    Without this the CLI reported "cyclonedx-cli not installed" or "trivy could
    not complete the scan" and still exited 0, so a run that validated nothing
    looked identical to a clean one. The pytest entrypoint has enforced this
    since _require_tool; this is the same rule for the CLI.
    """
    if not run_tools:
        # --no-tools means the tools were never asked for, so their absence is
        # not a setup failure.
        return []
    if not sbom_set.paths.get("cdx"):
        # _run_tools returns early with cyclonedx still MISSING when there is no
        # CycloneDX document. That MISSING means "did not run", not "binary
        # absent", and enforcing it would blame the tool on a host where it is
        # installed. A missing document is reported by the completeness check.
        return []

    problems = []
    status = report.tool_status.get("cyclonedx", external_tools.MISSING)
    if external_tools.unusable(status):
        problems.append(
            "cyclonedx-cli is %s, but the external tools were requested.\n"
            "    Install it, or pass --no-tools to skip the external tools."
            % status)

    # trivy only when the vulnerability gate actually wants it. _run_tools seeds
    # the status as OFF in that case, so this is belt and braces.
    if config.vuln_mode() != config.OFF:
        status = report.tool_status.get("trivy", external_tools.MISSING)
        if external_tools.unusable(status):
            problems.append(
                "trivy is %s, but the vulnerability scan was requested.\n"
                "    Install it, set %s=off, or pass --no-tools."
                % (status, config.ENV_VULN_MODE))
    return problems


def build_parser():
    parser = argparse.ArgumentParser(
        prog="check_sbom", description="Verify Percona product SBOM files.")
    parser.add_argument("--product", choices=sorted(products.PRODUCTS),
                        help="which product's SBOM files these are "
                             "(default: $%s, else %s)"
                             % (config.ENV_PRODUCT, products.DEFAULT))
    parser.add_argument("--mode", choices=("package", "docker", "dir"), default="package",
                        help="where to look: installed packages, a docker image, "
                             "or a plain directory")
    parser.add_argument("--image", help="docker image reference (--mode docker)")
    parser.add_argument("--path", help="directory holding SBOM files (--mode dir)")
    parser.add_argument("--package", help="package name to check (default: autodetect)")
    parser.add_argument("--expect-name", help="expected SBOM root component name")
    parser.add_argument("--expect-version",
                        help="expected SBOM root component version "
                             "(default: the product's version variable, "
                             "e.g. $PXB_VERSION or $PS_VERSION)")
    parser.add_argument("--no-tools", action="store_true",
                        help="skip trivy and cyclonedx-cli even when installed")
    # Tri-state, defaulting to None so the gate decides: strict licence
    # comparison is on by default, and this pair exists to force either way
    # without setting an environment variable. A plain store_true would be a
    # no-op now that the default is on.
    parser.add_argument("--strict-licenses", dest="strict_licenses",
                        action="store_true", default=None,
                        help="require identical licence operand sets across "
                             "formats (the default)")
    parser.add_argument("--no-strict-licenses", dest="strict_licenses",
                        action="store_false",
                        help="compare licences by overlap instead of requiring "
                             "identical sets across formats")
    return parser


def run(args):
    container = None
    product = config.product(args.product)
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
        sets, considered = discovery.discover(backend, sbom_dir=sbom_dir, product=product)

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
        expect_version = args.expect_version or config.expect_version(product)
        # Also for docker: the image installs the rpm, so the root component can
        # be cross-checked against the package the same way.
        if args.mode in ("package", "docker") and not expect_name:
            expect_name = discovery.expected_root_name(backend, sets[0], product)
            if not expect_version and expect_name:
                expect_version = discovery.installed_version(backend, expect_name)

        failed = False
        for sbom_set in sets:
            report = audit.audit(
                backend, sbom_set,
                expect_name=expect_name, expect_version=expect_version,
                strict_licenses=args.strict_licenses,
                run_tools=not args.no_tools,
            )
            print("")
            print(report.text())
            for note in report.tool_notes:
                print("  %s" % note)

            if not report.ok:
                failed = True

            for problem in _tool_problems(report, sbom_set, not args.no_tools):
                print("  %s" % problem)
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
