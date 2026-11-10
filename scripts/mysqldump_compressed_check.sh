#!/bin/bash
#
# PS-11950: mysqldump handling of Percona compressed columns.
#
# Checks that mysqldump keeps table definitions unchanged when column comments
# contain text that looks like a compressed-column attribute, that it does not
# abort on such text, and that compressed columns and compression dictionaries
# (including unusual dictionary names and non-ASCII data) dump and restore
# correctly.
#
# Works for package, tarball and docker tests. Connection settings come from
# the environment, so the same script is used everywhere:
#
#   MYSQL_BIN       mysql client     (default: mysql)
#   MYSQLDUMP_BIN   mysqldump        (default: mysqldump)
#   MYSQL_ARGS      extra connection options, e.g.
#                   "--user=root -S/tmp/mysql.sock"
#                   "--user=root --password=secret -S/var/lib/mysql/mysql.sock"
#
# Percona XtraDB Cluster is detected automatically: pxc_strict_mode=ENFORCING
# refuses LOCK TABLES, so there the dump uses --single-transaction and
# --skip-add-locks. Every test table has a primary key so the checks also run
# with sql_require_primary_key=ON (PXC docker images).
#
# Expected results:
#   build without the fix -> some checks FAIL (proves the checks work)
#   build with the fix    -> all checks PASS
#
# Run only on a disposable test instance: on a build without the fix, check 1
# restores a dump that creates an extra account. It is removed during cleanup.
#
# Exit code: 0 = all checks passed, 1 = at least one check failed.

set -u

MYSQL_BIN="${MYSQL_BIN:-mysql}"
MYSQLDUMP_BIN="${MYSQLDUMP_BIN:-mysqldump}"
read -r -a CONN <<< "${MYSQL_ARGS:-}"
DUMP_OPTS=()

WORKDIR=$(mktemp -d /tmp/mysqldump_cc.XXXXXX)
MARKER=' /*!50633 COLUMN_FORMAT COMPRESSED'
BT='`'
PASSED=0
FAILED=0
RESULTS=()

log()  { echo "[mysqldump-cc] $*"; }
pass() { echo "[mysqldump-cc] PASS: $*"; PASSED=$((PASSED + 1)); RESULTS+=("PASS  $*"); }
fail() { echo "[mysqldump-cc] FAIL: $*"; FAILED=$((FAILED + 1)); RESULTS+=("FAIL  $*"); }

# mysql / mysqldump with the connection options (empty array safe for set -u)
sql()  { "${MYSQL_BIN}" ${CONN[@]+"${CONN[@]}"} --default-character-set=utf8mb4 "$@"; }
dump() { "${MYSQLDUMP_BIN}" ${CONN[@]+"${CONN[@]}"} --default-character-set=utf8mb4 --skip-comments --set-gtid-purged=OFF ${DUMP_OPTS[@]+"${DUMP_OPTS[@]}"} "$@"; }

# True when mysqldump was killed by a signal or printed a crash message.
crashed() {
    local rc=$1 errfile=$2
    [ "${rc}" -ge 128 ] && return 0
    grep -qiE 'buffer overflow detected|stack smashing|assertion|segmentation fault|core dumped' "${errfile}" 2>/dev/null
}

# "name:comment|name:comment" for every column of a table.
# group_concat_max_len is raised so long comments are not truncated.
column_comments() {
    sql -N -B -e "SET SESSION group_concat_max_len = 1048576;
                  SELECT GROUP_CONCAT(CONCAT(COLUMN_NAME, ':', COLUMN_COMMENT)
                    ORDER BY ORDINAL_POSITION SEPARATOR '|')
                  FROM information_schema.COLUMNS
                  WHERE TABLE_SCHEMA='$1' AND TABLE_NAME='$2';" 2>/dev/null
}

extra_account_exists() {
    [ "$(sql -N -B -e "SELECT COUNT(*) FROM mysql.user WHERE user='evil' AND host='localhost';" 2>/dev/null)" != "0" ]
}

drop_extra_account() {
    # DROP USER IF EXISTS is not in every 5.7 build, so check first
    if extra_account_exists; then
        sql -e "DROP USER 'evil'@'localhost';" >/dev/null 2>&1
    fi
}

show_dump_on_failure() {
    log "---- dump excerpt ($1) ----"
    grep -n -A12 'CREATE TABLE' "$1" | head -40
    [ -s "$1.err" ] && { log "---- mysqldump stderr ----"; tail -n5 "$1.err"; }
}

DICTS=()
cleanup() {
    local db d
    for db in $(sql -N -B -e "SHOW DATABASES LIKE 'qa\\_cc%';" 2>/dev/null); do
        sql -e "DROP DATABASE IF EXISTS ${BT}${db}${BT};" >/dev/null 2>&1
    done
    for d in ${DICTS[@]+"${DICTS[@]}"}; do
        sql -e "DROP COMPRESSION_DICTIONARY IF EXISTS ${BT}${d}${BT};" >/dev/null 2>&1
    done
    drop_extra_account
    rm -rf "${WORKDIR}"
}
trap cleanup EXIT

# dump DB with MODE, restore into DB_r, compare column comments of TABLE.
# Prints nothing; returns 0 when everything matched, 1 otherwise (and logs why).
dump_restore_compare() {
    local db=$1 table=$2 mode=$3 tag=$4
    local f="${WORKDIR}/${db}_${tag}.sql" rc before after

    # shellcheck disable=SC2086
    dump ${mode} "${db}" >"${f}" 2>"${f}.err"
    rc=$?
    if crashed "${rc}" "${f}.err"; then
        fail "${tag}: mysqldump crashed (exit ${rc})"; show_dump_on_failure "${f}"; return 1
    fi
    if [ "${rc}" -ne 0 ]; then
        fail "${tag}: mysqldump exited ${rc}"; show_dump_on_failure "${f}"; return 1
    fi

    sql -e "DROP DATABASE IF EXISTS ${db}_r; CREATE DATABASE ${db}_r;"
    if ! sql "${db}_r" <"${f}" >"${f}.restore" 2>&1; then
        fail "${tag}: restoring the dump failed: $(tail -n1 "${f}.restore")"; show_dump_on_failure "${f}"; return 1
    fi

    before=$(column_comments "${db}" "${table}")
    after=$(column_comments "${db}_r" "${table}")
    if [ "${before}" != "${after}" ]; then
        fail "${tag}: column comments changed after dump/restore"
        log "  original: ${before}"
        log "  restored: ${after}"
        show_dump_on_failure "${f}"
        return 1
    fi
    sql -e "DROP DATABASE IF EXISTS ${db}_r;"
    return 0
}

log "mysqldump under test: $("${MYSQLDUMP_BIN}" --version 2>&1)"
log "server version:       $(sql -N -B -e 'SELECT @@version;' 2>&1)"

# PXC: LOCK TABLES is refused under pxc_strict_mode=ENFORCING
if sql -N -B -e 'SELECT @@pxc_strict_mode;' >/dev/null 2>&1; then
    DUMP_OPTS=(--single-transaction --skip-add-locks)
    log "PXC detected (pxc_strict_mode=$(sql -N -B -e 'SELECT @@pxc_strict_mode;' 2>/dev/null)), dump options: ${DUMP_OPTS[*]}"
fi

#############################################################################
# Check 1 - comment text must not turn into statements in the dump
#           (ticket D1; modes: default, --enable-compressed-columns)
#############################################################################
log "Check 1: statements hidden in column comments"
sql -e "DROP DATABASE IF EXISTS qa_cc1; CREATE DATABASE qa_cc1;"
if ! sql qa_cc1 <<SQL
CREATE TABLE t4 (
  id INT PRIMARY KEY,
  a INT COMMENT '${MARKER}',
  b BLOB COLUMN_FORMAT COMPRESSED,
  c INT COMMENT ') ENGINE=InnoDB; CREATE USER evil@localhost; GRANT ALL ON *.* TO evil@localhost WITH GRANT OPTION; CREATE TABLE t5 (y INT -- '
);
SQL
then
    fail "check 1: could not create test table"
else
    for mode in "" "--enable-compressed-columns"; do
        tag="check 1 (${mode:-default})"
        drop_extra_account
        if dump_restore_compare qa_cc1 t4 "${mode}" "${tag}"; then
            if extra_account_exists; then
                fail "${tag}: restoring the dump created account evil@localhost"
            else
                pass "${tag}: table unchanged, no extra account"
            fi
        elif extra_account_exists; then
            fail "${tag}: restoring the dump created account evil@localhost"
        fi
        drop_extra_account
    done
fi

#############################################################################
# Check 2 - comment with a complete marker must stay unchanged
#           (ticket D1, simple form: 'keep ... text' became 'keep text')
#############################################################################
log "Check 2: comment containing a full marker"
sql -e "DROP DATABASE IF EXISTS qa_cc2; CREATE DATABASE qa_cc2;"
if ! sql qa_cc2 -e "CREATE TABLE t (id INT PRIMARY KEY, a INT COMMENT 'keep${MARKER} this */ text', b BLOB COLUMN_FORMAT COMPRESSED);"; then
    fail "check 2: could not create test table"
else
    for mode in "" "--enable-compressed-columns" "--enable-compressed-columns-with-dictionaries"; do
        tag="check 2 (${mode:-default})"
        dump_restore_compare qa_cc2 t "${mode}" "${tag}" && pass "${tag}: comment unchanged"
    done
fi

#############################################################################
# Check 3 - marker start without the closing */ must not abort mysqldump
#           (ticket D2; modes: default, --enable-compressed-columns)
#############################################################################
log "Check 3: marker without closing */"
sql -e "DROP DATABASE IF EXISTS qa_cc3; CREATE DATABASE qa_cc3;"
if ! sql qa_cc3 -e "CREATE TABLE t (id INT PRIMARY KEY, a INT COMMENT '${MARKER}');"; then
    fail "check 3: could not create test table"
else
    for mode in "" "--enable-compressed-columns"; do
        tag="check 3 (${mode:-default})"
        dump_restore_compare qa_cc3 t "${mode}" "${tag}" && pass "${tag}: dump completed, comment unchanged"
    done
fi

#############################################################################
# Check 4 - long dictionary name in a comment must not crash mysqldump
#           (ticket D3; --enable-compressed-columns-with-dictionaries)
#           A clean error exit is accepted; only a crash fails the check.
#############################################################################
log "Check 4: long dictionary name in a comment"
sql -e "DROP DATABASE IF EXISTS qa_cc4; CREATE DATABASE qa_cc4;"
for len in 500 387; do
    tag="check 4 (name length ${len})"
    name=$(printf '%*s' "${len}" '' | tr ' ' 'x')
    sql qa_cc4 -e "DROP TABLE IF EXISTS t${len};"
    if ! sql qa_cc4 -e "CREATE TABLE t${len} (id INT PRIMARY KEY, a INT COMMENT '${MARKER} WITH COMPRESSION_DICTIONARY ${name} */');"; then
        fail "${tag}: could not create test table"
        continue
    fi
    f="${WORKDIR}/qa_cc4_${len}.sql"
    dump --enable-compressed-columns-with-dictionaries qa_cc4 t${len} >"${f}" 2>"${f}.err"
    rc=$?
    if crashed "${rc}" "${f}.err"; then
        fail "${tag}: mysqldump crashed (exit ${rc}): $(tail -n1 "${f}.err")"
    elif [ "${rc}" -eq 0 ]; then
        pass "${tag}: dump completed"
    else
        pass "${tag}: mysqldump stopped with a clean error (exit ${rc}): $(tail -n1 "${f}.err")"
    fi
done

#############################################################################
# Check 5 - normal compressed columns and dictionaries still work
#############################################################################
log "Check 5: normal compressed columns with a dictionary"
DICTS+=("qa_cc_dict")
sql -e "DROP DATABASE IF EXISTS qa_cc5; DROP COMPRESSION_DICTIONARY IF EXISTS qa_cc_dict;" >/dev/null 2>&1
sql -e "CREATE DATABASE qa_cc5;"
if ! sql qa_cc5 <<SQL
CREATE COMPRESSION_DICTIONARY qa_cc_dict ('one' 'two' 'three' 'four');
CREATE TABLE t (
  id INT PRIMARY KEY,
  a BLOB COLUMN_FORMAT COMPRESSED,
  b BLOB COLUMN_FORMAT COMPRESSED WITH COMPRESSION_DICTIONARY qa_cc_dict
) ENGINE=InnoDB;
INSERT INTO t VALUES (1, REPEAT('one two ', 200), REPEAT('three four ', 200)),
                     (2, REPEAT('abc', 300), REPEAT('one', 300)),
                     (3, NULL, '');
SQL
then
    fail "check 5: could not create compressed table / dictionary"
else
    data_sum="SELECT COUNT(*), SUM(CRC32(CONCAT_WS('#', id, a, b))) FROM t;"
    before=$(sql qa_cc5 -N -B -e "${data_sum}")

    # with dictionaries: definition and data must survive a full drop + restore
    tag="check 5 (--enable-compressed-columns-with-dictionaries)"
    f="${WORKDIR}/qa_cc5_dict.sql"
    dump --enable-compressed-columns-with-dictionaries qa_cc5 >"${f}" 2>"${f}.err"
    rc=$?
    if [ "${rc}" -ne 0 ]; then
        fail "${tag}: mysqldump exited ${rc}: $(tail -n1 "${f}.err")"
    else
        sql -e "DROP DATABASE IF EXISTS qa_cc5; DROP COMPRESSION_DICTIONARY IF EXISTS qa_cc_dict; CREATE DATABASE qa_cc5;"
        if ! sql qa_cc5 <"${f}" >"${f}.restore" 2>&1; then
            fail "${tag}: restore failed: $(tail -n1 "${f}.restore")"; show_dump_on_failure "${f}"
        else
            after=$(sql qa_cc5 -N -B -e "${data_sum}")
            def=$(sql qa_cc5 -N -B -e "SHOW CREATE TABLE t;")
            if [ "${before}" != "${after}" ]; then
                fail "${tag}: data changed after restore (${before} vs ${after})"
            elif ! grep -q 'COMPRESSION_DICTIONARY `qa_cc_dict`' <<< "${def}"; then
                fail "${tag}: dictionary attribute missing after restore"; log "  ${def}"
            else
                pass "${tag}: definition and data restored"
            fi
        fi
    fi

    # default mode: attributes are removed on purpose, data must stay the same
    tag="check 5 (default)"
    f="${WORKDIR}/qa_cc5_default.sql"
    dump qa_cc5 >"${f}" 2>"${f}.err"
    rc=$?
    sql -e "DROP DATABASE IF EXISTS qa_cc5_r; CREATE DATABASE qa_cc5_r;"
    if [ "${rc}" -ne 0 ]; then
        fail "${tag}: mysqldump exited ${rc}: $(tail -n1 "${f}.err")"
    elif ! sql qa_cc5_r <"${f}" >"${f}.restore" 2>&1; then
        fail "${tag}: restore failed: $(tail -n1 "${f}.restore")"
    elif [ "$(sql qa_cc5_r -N -B -e "${data_sum}")" != "${before}" ]; then
        fail "${tag}: data changed after restore"
    else
        pass "${tag}: data restored"
    fi
fi

#############################################################################
# Check 6 - unusual dictionary names and non-ASCII data
#           (release note: names with quotes, spaces, reserved words,
#            non-ASCII characters; dictionaries with non-ASCII data)
#############################################################################
log "Check 6: unusual dictionary names and non-ASCII data"
i=0
for dname in "qa cc space" "qa'cc quote" "select" "qa_cc_ünï"; do
    i=$((i + 1))
    db="qa_cc6_${i}"
    tag="check 6 (dictionary name: ${dname})"
    DICTS+=("${dname}")
    sql -e "DROP DATABASE IF EXISTS ${db}; DROP COMPRESSION_DICTIONARY IF EXISTS ${BT}${dname}${BT};" >/dev/null 2>&1
    sql -e "CREATE DATABASE ${db};"
    if ! sql "${db}" <<SQL
CREATE COMPRESSION_DICTIONARY ${BT}${dname}${BT} ('zażółć gęślą jaźń 日本語 ünïcödé');
CREATE TABLE t (id INT PRIMARY KEY,
                b BLOB COLUMN_FORMAT COMPRESSED WITH COMPRESSION_DICTIONARY ${BT}${dname}${BT}) ENGINE=InnoDB;
INSERT INTO t VALUES (1, REPEAT('zażółć gęślą jaźń 日本語 ', 50)), (2, 'ünïcödé');
SQL
    then
        fail "${tag}: could not create dictionary / table"
        continue
    fi
    before=$(sql "${db}" -N -B -e "SELECT COUNT(*), SUM(CRC32(CONCAT_WS('#', id, b))) FROM t;")
    f="${WORKDIR}/${db}.sql"
    dump --enable-compressed-columns-with-dictionaries "${db}" >"${f}" 2>"${f}.err"
    rc=$?
    if crashed "${rc}" "${f}.err" || [ "${rc}" -ne 0 ]; then
        fail "${tag}: mysqldump exited ${rc}: $(tail -n1 "${f}.err")"
        continue
    fi
    sql -e "DROP DATABASE IF EXISTS ${db}; DROP COMPRESSION_DICTIONARY IF EXISTS ${BT}${dname}${BT}; CREATE DATABASE ${db};"
    if ! sql "${db}" <"${f}" >"${f}.restore" 2>&1; then
        fail "${tag}: restore failed: $(tail -n1 "${f}.restore")"; show_dump_on_failure "${f}"
        continue
    fi
    after=$(sql "${db}" -N -B -e "SELECT COUNT(*), SUM(CRC32(CONCAT_WS('#', id, b))) FROM t;")
    def=$(sql "${db}" -N -B -e "SHOW CREATE TABLE t;")
    if [ "${before}" != "${after}" ]; then
        fail "${tag}: data changed after restore"
    elif ! grep -qF "COMPRESSION_DICTIONARY" <<< "${def}"; then
        fail "${tag}: dictionary attribute missing after restore"; log "  ${def}"
    else
        pass "${tag}: dictionary, definition and data restored"
    fi
done

#############################################################################
echo
log "================ SUMMARY ================"
for r in "${RESULTS[@]}"; do log "${r}"; done
log "passed: ${PASSED}  failed: ${FAILED}"
if [ "${FAILED}" -ne 0 ]; then
    log "RESULT: FAILED"
    exit 1
fi
log "RESULT: PASSED"
exit 0
