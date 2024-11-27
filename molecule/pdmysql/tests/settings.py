import os

RHEL_DISTS = ["redhat", "centos", "rhel", "oracleserver", "ol", "amzn"]

DEB_DISTS = ["debian", "ubuntu"]

REPO = os.environ.get("REPO")

TELEMETRY_PATH = "/usr/local/percona/telemetry_uuid"

VERSION = os.environ['VERSION']
MAJOR_VERSION = VERSION.split('.')[0] + '.' + VERSION.split('.')[1]
