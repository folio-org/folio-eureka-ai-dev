#!/usr/bin/env python3
"""Print what a TestRail case says now, with the fields that matter for triage.

Usage: python testrail_case.py <case id> [<case id> ...] [--raw]

Case ids may have the C prefix (C123456). --raw prints the full JSON of each case instead.
TestRail credentials come from the config (testrail.*) or TESTRAIL_BASE_URL / TESTRAIL_USERNAME /
TESTRAIL_PASSWORD environment variables. Exit code 3: credentials are missing - ask the user and save
them with config.py set (or config.py import-testrail <.env>). Credentials are never printed.
"""
import datetime
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

VALID_GROUPS = {1: 'Smoke', 2: 'Critical Path', 3: 'Extended Path', 6: 'Backend', 7: 'Edge Cases'}


def text(value):
    """TestRail rich text (HTML or markdown) as plain lines."""
    if not value:
        return ''
    s = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</div>|</tr>', '\n', str(value))
    s = re.sub(r'(?i)<li[^>]*>', '- ', s)
    s = html.unescape(re.sub(r'<[^>]+>', '', s))
    return '\n'.join(l.rstrip() for l in s.splitlines() if l.strip())


def date(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC') if ts else '-'


def main():
    args = sys.argv[1:]
    raw = '--raw' in args
    ids = [a.upper().lstrip('C') for a in args if a != '--raw']
    if not ids or not all(i.isdigit() for i in ids):
        sys.exit(__doc__)
    base, headers = common.testrail(common.load_config())

    for cid in ids:
        try:
            req = urllib.request.Request(f'{base}/index.php?/api/v2/get_case/{cid}', headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                c = json.loads(r.read())
        except urllib.error.HTTPError as e:
            print(f'C{cid}: HTTP {e.code} {e.read().decode("utf-8", "replace")[:300]}\n')
            continue
        if raw:
            print(json.dumps(c, indent=1, ensure_ascii=False))
            continue
        group = c.get('custom_test_group')
        flags = []
        if c.get('is_deleted'):
            flags.append('DELETED - retire the test, do not fix it')
        if group not in VALID_GROUPS:
            flags.append(f'test group {group} is not 1/2/3/6/7 - retire the test, do not fix it')
        if c.get('custom_unstable'):
            flags.append('marked unstable (known flaky) - look for parallel-conflict/infra first')
        if c.get('custom_bug_created'):
            flags.append('a bug was already created - reference it instead of writing a new one')
        print(f"C{cid}: {c.get('title')}")
        print(f"  group={VALID_GROUPS.get(group, group)} team={c.get('custom_dev_team')} "
              f"release={c.get('custom_release')} ecs={c.get('custom_ecs_enabled')} "
              f"automation={c.get('custom_automation_type')} section={c.get('section_id')}")
        print(f"  refs={c.get('refs') or '-'}  updated={date(c.get('updated_on'))}  created={date(c.get('created_on'))}")
        for fl in flags:
            print(f'  ! {fl}')
        if c.get('custom_preconds'):
            print('  Preconditions:\n    ' + text(c['custom_preconds']).replace('\n', '\n    '))
        for n, step in enumerate(c.get('custom_steps_separated') or [], 1):
            print(f'  Step {n}: ' + text(step.get('content')).replace('\n', '\n    '))
            if step.get('expected'):
                print('    Expected: ' + text(step['expected']).replace('\n', '\n      '))
        if not c.get('custom_steps_separated') and c.get('custom_steps'):
            print('  Steps:\n    ' + text(c['custom_steps']).replace('\n', '\n    '))
        print()


if __name__ == '__main__':
    main()
