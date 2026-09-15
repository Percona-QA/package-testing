"""Where to run shell and how to read bytes.

The only real difference between "inspect an installed package" and "inspect a
docker image" is that. Everything else in this package is shared.

Note the docker backend shells out to `docker exec` rather than running python
inside the container: the PXB image is redhat/ubi9-minimal and has no python3.
Parsing always happens in the caller's interpreter.
"""

import gzip
import io
import os
import subprocess

GZIP_MAGIC = b"\x1f\x8b"

# Overridable so the same code drives podman or a static docker CLI.
DOCKER_BIN = os.environ.get("DOCKER_BIN", "docker")


class Result(object):
    def __init__(self, rc, stdout, stderr):
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr

    @property
    def ok(self):
        return self.rc == 0

    def lines(self):
        return [l for l in (self.stdout or "").splitlines() if l.strip()]

    def __repr__(self):
        return "Result(rc=%d, stdout=%r)" % (self.rc, (self.stdout or "")[:200])


def _run(argv):
    # Not subprocess.run(capture_output=...): RHEL-8 targets ship python 3.6.
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return Result(
        process.returncode,
        out.decode("utf-8", "replace"),
        err.decode("utf-8", "replace"),
    )


def _maybe_gunzip(data):
    """Decompress by sniffing the magic bytes, never by extension.

    Debian gzips files under /usr/share/doc (the INFO_BIN vs INFO_BIN.gz split in
    tasks/test_pgo.yml is the precedent), so an SBOM can arrive as .json.gz on
    deb and plain on rpm. Sniffing handles both without branching on os_family.
    """
    if data[:2] == GZIP_MAGIC:
        return gzip.GzipFile(fileobj=io.BytesIO(data)).read()
    return data


class Backend(object):
    """Contract: run POSIX shell, read bytes, materialise files locally."""

    name = "backend"

    def run(self, command):
        raise NotImplementedError

    def read_bytes(self, path):
        raise NotImplementedError

    def export(self, path, dest_dir):
        """Copy path to dest_dir on the machine running this code (so trivy and
        cyclonedx-cli can read it) and return the local path."""
        raise NotImplementedError


class LocalBackend(Backend):
    """Installed packages on this machine -- the molecule target host."""

    name = "local"

    def run(self, command):
        return _run(["sh", "-c", command])

    def read_bytes(self, path):
        with open(path, "rb") as handle:
            return _maybe_gunzip(handle.read())

    def export(self, path, dest_dir):
        data = self.read_bytes(path)
        basename = os.path.basename(path)
        if basename.endswith(".gz"):
            basename = basename[:-3]
        local = os.path.join(dest_dir, basename)
        with open(local, "wb") as handle:
            handle.write(data)
        return local


class DockerBackend(Backend):
    """A running container started from the image under test."""

    name = "docker"

    def __init__(self, container_id, docker=None):
        self.container_id = container_id
        self.docker = docker or DOCKER_BIN

    def run(self, command):
        return _run([self.docker, "exec", self.container_id, "sh", "-c", command])

    def read_bytes(self, path):
        process = subprocess.Popen(
            [self.docker, "exec", self.container_id, "cat", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            raise IOError("cannot read %s from container %s: %s"
                          % (path, self.container_id, err.decode("utf-8", "replace")))
        return _maybe_gunzip(out)

    def export(self, path, dest_dir):
        data = self.read_bytes(path)
        basename = os.path.basename(path)
        if basename.endswith(".gz"):
            basename = basename[:-3]
        local = os.path.join(dest_dir, basename)
        with open(local, "wb") as handle:
            handle.write(data)
        return local
