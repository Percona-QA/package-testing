#!/bin/bash
#
# PS-11950 regression test for Percona mysqldump compressed-columns handling.
#
# skip_compressed_columns() in client/mysqldump.cc searches the whole
# SHOW CREATE TABLE text for the compressed-column markers without skipping
# quoted strings. The same marker text placed inside a column COMMENT is then
# treated as a real column-format extension. This exercises the three defects:
#
#   D1 - SQL injection into the dump: stripping the fake marker removes a
#        closing quote, turning attacker comment text into SQL that runs on
#        restore (default and --enable-compressed-columns).
#   D2 - a start marker with no closing "*/" aborts/crashes the dump.
#   D3 - an oversized dictionary name overflows a fixed stack buffer
#        (--enable-compressed-columns-with-dictionaries).
#
# The test runs against the installed mysqldump and the already-running
# instance. It returns non-zero if the binary under test is still vulnerable,
# so it can gate a package build.
#
# NOTE: for D1 the dump is restored, which on a VULNERABLE build actually
# creates a superuser on this instance. The package-testing host is disposable
# and the injected account is dropped during cleanup.

set -u

MYSQL="${MYSQL:-mysql}"
MYSQLDUMP="${MYSQLDUMP:-mysqldump}"

WORKDIR=$(mktemp -d /tmp/ps11950.XXXXXX)
MARKER=' /*!50633 COLUMN_FORMAT COMPRESSED'
FAILED=0

log()  { echo "[ps11950] $*"; }
fail() { echo "[ps11950] FAIL: $*"; FAILED=1; }
pass() { echo "[ps11950] PASS: $*"; }

cleanup() {
    "${MYSQL}" -e "DROP DATABASE IF EXISTS ps11950_d1;
                   DROP DATABASE IF EXISTS ps11950_d2;
                   DROP DATABASE IF EXISTS ps11950_d3;
                   DROP USER IF EXISTS evil@localhost;" >/dev/null 2>&1
    rm -rf "${WORKDIR}"
}
trap cleanup EXIT

log "mysqldump under test: $(${MYSQLDUMP} --version 2>&1)"

#############################################################################
# D1 - SQL injection into the dump (default and --enable-compressed-columns)
#############################################################################
log "D1: setting up injection table"
"${MYSQL}" -e "DROP DATABASE IF EXISTS ps11950_d1; CREATE DATABASE ps11950_d1;"
"${MYSQL}" ps11950_d1 <<SQL
CREATE TABLE t4 (
  a INT COMMENT '${MARKER}',
  b BLOB COLUMN_FORMAT COMPRESSED,
  c INT COMMENT ') ENGINE=InnoDB; CREATE USER evil@localhost; GRANT ALL ON *.* TO evil@localhost WITH GRANT OPTION; CREATE TABLE t5 (y INT -- '
);
SQL
if [ $? -ne 0 ]; then
    fail "D1: could not create injection table (is this a compressed-columns build?)"
else
    for mode in "" "--enable-compressed-columns"; do
        tag=${mode:-default}
        dump="${WORKDIR}/d1_${tag//-/}.sql"
        "${MYSQLDUMP}" ${mode} --skip-comments ps11950_d1 >"${dump}" 2>"${dump}.err"
        dump_rc=$?

        # Make sure no injected account lingers before the restore check.
        "${MYSQL}" -e "DROP USER IF EXISTS evil@localhost;" >/dev/null 2>&1

        if [ ${dump_rc} -ne 0 ]; then
            fail "D1 (${tag}): mysqldump exited ${dump_rc}; $(tail -n1 "${dump}.err")"
            continue
        fi

        # Restore into the live instance; a vulnerable dump runs the injection.
        "${MYSQL}" ps11950_d1 <"${dump}" >/dev/null 2>&1
        evil=$("${MYSQL}" -N -e \
            "SELECT COUNT(*) FROM mysql.user WHERE user='evil' AND host='localhost';" 2>/dev/null)

        if [ "${evil}" = "1" ]; then
            fail "D1 (${tag}): restoring the dump created superuser evil@localhost (SQL injection)"
        else
            pass "D1 (${tag}): no injected account created on restore"
        fi
        "${MYSQL}" -e "DROP USER IF EXISTS evil@localhost;" >/dev/null 2>&1
    done
fi

#############################################################################
# D2 - start marker with no closing "*/" must not crash the dump
#############################################################################
log "D2: setting up table with unterminated marker"
"${MYSQL}" -e "DROP DATABASE IF EXISTS ps11950_d2; CREATE DATABASE ps11950_d2;"
"${MYSQL}" ps11950_d2 -e "CREATE TABLE t (a INT COMMENT '${MARKER}');"
if [ $? -ne 0 ]; then
    fail "D2: could not create table"
else
    "${MYSQLDUMP}" --skip-comments ps11950_d2 >"${WORKDIR}/d2.sql" 2>"${WORKDIR}/d2.err"
    rc=$?
    if [ ${rc} -ne 0 ]; then
        fail "D2: mysqldump aborted/crashed (exit ${rc}); $(tail -n1 "${WORKDIR}/d2.err")"
    else
        pass "D2: mysqldump completed cleanly on unterminated marker"
    fi
fi

#############################################################################
# D3 - oversized dictionary name must not overflow the stack buffer
#       (--enable-compressed-columns-with-dictionaries)
#############################################################################
log "D3: setting up table with oversized dictionary name"
BIGNAME=$(printf 'x%.0s' $(seq 1 500))
"${MYSQL}" -e "DROP DATABASE IF EXISTS ps11950_d3; CREATE DATABASE ps11950_d3;"
"${MYSQL}" ps11950_d3 -e \
    "CREATE TABLE t (a INT COMMENT '${MARKER} WITH COMPRESSION_DICTIONARY ${BIGNAME} */');"
if [ $? -ne 0 ]; then
    fail "D3: could not create table"
else
    "${MYSQLDUMP}" --enable-compressed-columns-with-dictionaries --skip-comments \
        ps11950_d3 >"${WORKDIR}/d3.sql" 2>"${WORKDIR}/d3.err"
    rc=$?
    if [ ${rc} -ne 0 ]; then
        fail "D3: mysqldump aborted/crashed (exit ${rc}); $(tail -n1 "${WORKDIR}/d3.err")"
    else
        pass "D3: mysqldump completed cleanly on oversized dictionary name"
    fi
fi

#############################################################################
if [ ${FAILED} -ne 0 ]; then
    log "RESULT: FAILED - mysqldump is vulnerable to PS-11950"
    exit 1
fi
log "RESULT: PASSED - mysqldump handles compressed-column markers in comments safely"
exit 0
