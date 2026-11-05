#!/bin/bash
#
# PS-11950 regression test for Percona mysqldump compressed-columns handling.
#
# skip_compressed_columns() in client/mysqldump.cc searches the whole
# SHOW CREATE TABLE text for the compressed-column markers without skipping
# quoted strings. The same marker text placed inside a column COMMENT is then
# treated as a real column-format extension. This exercises three defects,
# reported here as individual, clearly pass/fail tests:
#
#   Test 1 - D1 (default): SQL injection into the dump. Stripping a fake marker
#            removes a closing quote, turning attacker comment text into SQL
#            that runs on restore.
#   Test 2 - D1 (--enable-compressed-columns): same injection, other mode.
#   Test 3 - D2: a start marker with no closing "*/" must not crash the dump.
#   Test 4 - D3: an oversized dictionary name must not overflow the stack
#            buffer (--enable-compressed-columns-with-dictionaries).
#
# The script runs against the installed mysqldump and the already-running
# instance. It prints PASS/FAIL per test, a summary, and returns non-zero if
# any test failed (i.e. the binary under test is still vulnerable).
#
# NOTE: for the D1 tests the dump is restored, which on a VULNERABLE build
# actually creates a superuser on this instance. The package-testing host is
# disposable and the injected account is dropped during cleanup.

MYSQL="${MYSQL:-mysql}"
MYSQLDUMP="${MYSQLDUMP:-mysqldump}"

WORKDIR=$(mktemp -d /tmp/ps11950.XXXXXX)
MARKER=' /*!50633 COLUMN_FORMAT COMPRESSED'

# Ordered list of test labels and their results, filled as we go.
TEST_NAMES=()
TEST_RESULTS=()

log() { echo "[ps11950] $*"; }

# record <result PASS|FAIL> <test name> [detail]
record() {
    local result="$1" name="$2" detail="$3"
    TEST_NAMES+=("${name}")
    TEST_RESULTS+=("${result}")
    if [ "${result}" = "PASS" ]; then
        echo "[ps11950] PASS: ${name}"
    else
        echo "[ps11950] FAIL: ${name}${detail:+ -- ${detail}}"
    fi
}

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
# Tests 1 & 2 - D1: SQL injection into the dump
#############################################################################
"${MYSQL}" -e "DROP DATABASE IF EXISTS ps11950_d1; CREATE DATABASE ps11950_d1;"
"${MYSQL}" ps11950_d1 <<SQL
CREATE TABLE t4 (
  a INT COMMENT '${MARKER}',
  b BLOB COLUMN_FORMAT COMPRESSED,
  c INT COMMENT ') ENGINE=InnoDB; CREATE USER evil@localhost; GRANT ALL ON *.* TO evil@localhost WITH GRANT OPTION; CREATE TABLE t5 (y INT -- '
);
SQL
d1_setup_rc=$?

for mode in "" "--enable-compressed-columns"; do
    tag=${mode:-default}
    name="Test $([ -z "${mode}" ] && echo 1 || echo 2): D1 SQL injection (${tag})"

    if [ ${d1_setup_rc} -ne 0 ]; then
        record FAIL "${name}" "could not create injection table (is this a compressed-columns build?)"
        continue
    fi

    dump="${WORKDIR}/d1_${tag//-/}.sql"
    "${MYSQLDUMP}" ${mode} --skip-comments ps11950_d1 >"${dump}" 2>"${dump}.err"
    dump_rc=$?

    # Make sure no injected account lingers before the restore check.
    "${MYSQL}" -e "DROP USER IF EXISTS evil@localhost;" >/dev/null 2>&1

    if [ ${dump_rc} -ne 0 ]; then
        record FAIL "${name}" "mysqldump exited ${dump_rc}; $(tail -n1 "${dump}.err")"
        continue
    fi

    # Restore into the live instance; a vulnerable dump runs the injection.
    "${MYSQL}" ps11950_d1 <"${dump}" >/dev/null 2>&1
    evil=$("${MYSQL}" -N -e \
        "SELECT COUNT(*) FROM mysql.user WHERE user='evil' AND host='localhost';" 2>/dev/null)

    if [ "${evil}" = "1" ]; then
        record FAIL "${name}" "restoring the dump created superuser evil@localhost (SQL injection)"
    else
        record PASS "${name}"
    fi
    "${MYSQL}" -e "DROP USER IF EXISTS evil@localhost;" >/dev/null 2>&1
done

#############################################################################
# Test 3 - D2: start marker with no closing "*/" must not crash the dump
#############################################################################
name="Test 3: D2 unterminated marker does not crash mysqldump"
"${MYSQL}" -e "DROP DATABASE IF EXISTS ps11950_d2; CREATE DATABASE ps11950_d2;"
"${MYSQL}" ps11950_d2 -e "CREATE TABLE t (a INT COMMENT '${MARKER}');"
if [ $? -ne 0 ]; then
    record FAIL "${name}" "could not create table"
else
    "${MYSQLDUMP}" --skip-comments ps11950_d2 >"${WORKDIR}/d2.sql" 2>"${WORKDIR}/d2.err"
    rc=$?
    if [ ${rc} -ne 0 ]; then
        record FAIL "${name}" "mysqldump aborted/crashed (exit ${rc}); $(tail -n1 "${WORKDIR}/d2.err")"
    else
        record PASS "${name}"
    fi
fi

#############################################################################
# Test 4 - D3: oversized dictionary name must not overflow the stack buffer
#          (--enable-compressed-columns-with-dictionaries)
#############################################################################
name="Test 4: D3 oversized dictionary name does not overflow mysqldump"
BIGNAME=$(printf 'x%.0s' $(seq 1 500))
"${MYSQL}" -e "DROP DATABASE IF EXISTS ps11950_d3; CREATE DATABASE ps11950_d3;"
"${MYSQL}" ps11950_d3 -e \
    "CREATE TABLE t (a INT COMMENT '${MARKER} WITH COMPRESSION_DICTIONARY ${BIGNAME} */');"
if [ $? -ne 0 ]; then
    record FAIL "${name}" "could not create table"
else
    "${MYSQLDUMP}" --enable-compressed-columns-with-dictionaries --skip-comments \
        ps11950_d3 >"${WORKDIR}/d3.sql" 2>"${WORKDIR}/d3.err"
    rc=$?
    if [ ${rc} -ne 0 ]; then
        record FAIL "${name}" "mysqldump aborted/crashed (exit ${rc}); $(tail -n1 "${WORKDIR}/d3.err")"
    else
        record PASS "${name}"
    fi
fi

#############################################################################
# Summary
#############################################################################
echo
echo "========================= PS-11950 test summary ========================="
failed=0
for i in "${!TEST_NAMES[@]}"; do
    printf '  [%-4s] %s\n' "${TEST_RESULTS[$i]}" "${TEST_NAMES[$i]}"
    [ "${TEST_RESULTS[$i]}" = "FAIL" ] && failed=$((failed + 1))
done
total=${#TEST_NAMES[@]}
echo "------------------------------------------------------------------------"
echo "  ${total} tests, $((total - failed)) passed, ${failed} failed"
echo "========================================================================"

if [ ${failed} -ne 0 ]; then
    log "RESULT: FAILED - mysqldump is vulnerable to PS-11950"
    exit 1
fi
log "RESULT: PASSED - mysqldump handles compressed-column markers in comments safely"
exit 0
