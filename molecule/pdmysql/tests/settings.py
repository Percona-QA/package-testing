import os

RHEL_DISTS = ["redhat", "centos", "rhel", "oracleserver", "ol", "amzn"]

DEB_DISTS = ["debian", "ubuntu"]

REPO = os.environ.get("REPO")

TELEMETRY_PATH = "/usr/local/percona/telemetry_uuid"
