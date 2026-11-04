#!/usr/bin/env python3
"""Convert pbs_test_runner.py's summary.json into a JUnit XML report for Jenkins.

summary.json is a list with one entry per test:

    {"name": "gtid_rewrite_test", "slot": "w1", "returncode": 0, "passed": true,
     "duration_seconds": 312.4, "log_path": ".../gtid_rewrite_test.log",
     "work_dir": "...", "failed_logs_path": null}

Each entry becomes a testcase. A failed test's message carries its exit code, and
the tail of its own log (log_path) goes into <system-out>.

Usage: pbs_summary_to_junit.py SUMMARY_JSON OUTPUT_XML CLASS_PREFIX EXIT_CODE [CONSOLE_LOG]
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

MAX_LOG_BYTES = 1024 * 1024


def read_tail(path, max_bytes=MAX_LOG_BYTES):
    if not path or not os.path.isfile(path):
        return ''
    with open(path, 'rb') as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - max_bytes))
        data = handle.read().decode('utf-8', errors='replace')
    prefix = '[... truncated, showing last 1 MiB ...]\n' if size > max_bytes else ''
    return 'Log: ' + path + '\n' + prefix + data


def load_summary(summary_file):
    if not os.path.isfile(summary_file):
        return []
    with open(summary_file) as handle:
        return json.load(handle)


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(2)
    summary_file, output_xml, class_prefix, exit_code = sys.argv[1:5]
    console_log = sys.argv[5] if len(sys.argv) > 5 else None

    results = load_summary(summary_file)
    suite_el = ET.Element('testsuite', name=class_prefix)
    counts = {'tests': 0, 'failures': 0}
    total_time = 0.0

    # The runner can stop before writing summary.json (bad config, unknown test,
    # timeout). Report that as a failure so the Jenkins build doesn't look green.
    if not results and exit_code != '0':
        el = ET.SubElement(suite_el, 'testcase', classname=class_prefix, name='pbs_test_runner', time='0')
        failure = ET.SubElement(el, 'failure', message='pbs_test_runner.py exited with ' + exit_code +
                                ' before writing summary.json')
        failure.text = read_tail(console_log, 64 * 1024)
        counts['tests'] = counts['failures'] = 1

    for result in results:
        duration = float(result.get('duration_seconds') or 0)
        el = ET.SubElement(suite_el, 'testcase', classname=class_prefix, name=result.get('name', '?'),
                           time=str(duration))
        counts['tests'] += 1
        total_time += duration
        if not result.get('passed'):
            counts['failures'] += 1
            message = 'exit code ' + str(result.get('returncode'))
            if result.get('failed_logs_path'):
                message += ', logs preserved in ' + result['failed_logs_path']
            ET.SubElement(el, 'failure', message=message)
        log_text = read_tail(result.get('log_path'))
        if log_text:
            ET.SubElement(el, 'system-out').text = log_text

    suite_el.set('tests', str(counts['tests']))
    suite_el.set('failures', str(counts['failures']))
    suite_el.set('errors', '0')
    suite_el.set('skipped', '0')
    suite_el.set('time', str(round(total_time, 1)))
    ET.ElementTree(suite_el).write(output_xml, encoding='utf-8', xml_declaration=True)
    print('Wrote {} ({tests} tests, {failures} failures)'.format(output_xml, **counts))


if __name__ == '__main__':
    main()
