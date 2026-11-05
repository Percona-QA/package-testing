#!/usr/bin/env python3
"""Convert pxc-qa's test_run_results.out into a JUnit XML report for Jenkins.

qa_framework.py writes one line per test, for example:

    Test replication.replication.py                     00:03:12 [Pass]
    Test ssl.ssl_qa.py                               w2 00:01:05 [Fail]
    Skipping disabled test correctness.chaosmonkey-test.py

A [Fail] line is followed by the tail of that test's log. That tail becomes the
failure message, and the full per-test log (workdir/.../tests_log/<test>.log)
goes into <system-out>.

Usage: qa_results_to_junit.py RESULTS_FILE WORKDIR OUTPUT_XML CLASS_PREFIX EXIT_CODE [CONSOLE_LOG]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

RESULT_RE = re.compile(
    r'^Test (?P<name>\S+?\.py)\s*(?:w\d+ )?(?P<h>\d+):(?P<m>\d{2}):(?P<s>\d{2}) \[(?P<status>Pass|Fail|Skipped)\]\s*$')
SKIP_RE = re.compile(r'^Skipping (?:disabled test )?(?P<name>\S+\.py)(?: - (?P<reason>.*))?\s*$')
MAX_LOG_BYTES = 1024 * 1024


def split_name(full_name):
    suite, _, test = full_name.partition('.')
    return (suite, test) if test else ('pxc-qa', full_name)


def read_test_log(workdir, test_file):
    stem = os.path.splitext(test_file)[0]
    for path in glob.glob(os.path.join(workdir, '**', 'tests_log', stem + '.log'), recursive=True):
        with open(path, 'rb') as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - MAX_LOG_BYTES))
            data = handle.read().decode('utf-8', errors='replace')
        prefix = '[... truncated, showing last 1 MiB ...]\n' if size > MAX_LOG_BYTES else ''
        return 'Log: ' + path + '\n' + prefix + data
    return ''


def tail(path, lines=200):
    if not path or not os.path.isfile(path):
        return ''
    with open(path, errors='replace') as handle:
        return ''.join(handle.readlines()[-lines:])


def parse(results_file):
    cases = []
    current_failure = None
    if not os.path.isfile(results_file):
        return cases
    with open(results_file, errors='replace') as handle:
        for raw in handle:
            line = raw.rstrip('\n')
            match = RESULT_RE.match(line)
            if match:
                seconds = int(match['h']) * 3600 + int(match['m']) * 60 + int(match['s'])
                case = {'name': match['name'], 'status': match['status'], 'time': seconds, 'details': []}
                cases.append(case)
                current_failure = case if match['status'] == 'Fail' else None
                continue
            match = SKIP_RE.match(line)
            if match:
                cases.append({'name': match['name'], 'status': 'Skipped', 'time': 0,
                              'details': [match['reason'] or 'disabled via disabled.list']})
                current_failure = None
                continue
            if current_failure is not None and line.strip():
                current_failure['details'].append(line)
    return cases


def main():
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(2)
    results_file, workdir, output_xml, class_prefix, exit_code = sys.argv[1:6]
    console_log = sys.argv[6] if len(sys.argv) > 6 else None

    cases = parse(results_file)
    # The framework can die before writing any result line (bad basedir, import
    # error, ...). Report that as a failure so the Jenkins build doesn't look green.
    if not cases and exit_code != '0':
        cases.append({'name': 'pxc-qa.qa_framework', 'status': 'Fail', 'time': 0,
                      'details': ['qa_framework.py exited with ' + exit_code + ' before reporting any test',
                                  tail(console_log)]})

    suite_el = ET.Element('testsuite', name=class_prefix)
    counts = {'tests': 0, 'failures': 0, 'skipped': 0}
    total_time = 0
    for case in cases:
        suite, test = split_name(case['name'])
        el = ET.SubElement(suite_el, 'testcase', classname=class_prefix + '.' + suite,
                           name=test, time=str(case['time']))
        counts['tests'] += 1
        total_time += case['time']
        details = '\n'.join(d for d in case['details'] if d)
        if case['status'] == 'Fail':
            counts['failures'] += 1
            failure = ET.SubElement(el, 'failure', message='test failed')
            failure.text = details
        elif case['status'] == 'Skipped':
            counts['skipped'] += 1
            ET.SubElement(el, 'skipped', message=details or 'skipped')
        log_text = read_test_log(workdir, test)
        if log_text:
            ET.SubElement(el, 'system-out').text = log_text

    for key, value in counts.items():
        suite_el.set(key, str(value))
    suite_el.set('errors', '0')
    suite_el.set('time', str(total_time))
    ET.ElementTree(suite_el).write(output_xml, encoding='utf-8', xml_declaration=True)
    print('Wrote {} ({tests} tests, {failures} failures, {skipped} skipped)'.format(output_xml, **counts))


if __name__ == '__main__':
    main()
