#!/usr/bin/env python3
"""Post one test result to a TestRail run (only when the user asks to record failures with tickets).

Usage:
  python testrail_result.py <run id> <case id> --status failed [--defects KEY[,KEY]]
                            [--comment "<html>" | --comment-file <path>] [--dry-run]

--status is a TestRail status name or label, case-insensitive (failed, retest, deferred, ...); the ids
are looked up on the instance, so custom statuses work. --defects takes Jira keys only (MODINV-1433),
never URLs: the TestRail-Jira integration builds the links. The comment is HTML (<p>, <br>, <strong>).
--dry-run prints the request body without sending it. Results cannot be edited or deleted through the
API - a new result supersedes the old one.

TestRail credentials come from the config (testrail.*) or TESTRAIL_* environment variables. Exit code 3:
they are missing - ask the user and save them with config.py set. Credentials are never printed.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

KEY = re.compile(r'^[A-Z][A-Z0-9]+-\d+$')


def call(base, headers, path, body=None):
    req = urllib.request.Request(f'{base}/index.php?/api/v2/{path}', headers=headers,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 method='POST' if body is not None else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f'{path}: HTTP {e.code} {e.read().decode("utf-8", "replace")[:300]}')


def main():
    args = sys.argv[1:]
    if len(args) < 2 or not args[0].isdigit() or not args[1].upper().lstrip('C').isdigit():
        sys.exit(__doc__)
    run_id, case_id, rest = args[0], args[1].upper().lstrip('C'), args[2:]
    opts, dry = {}, '--dry-run' in rest
    rest = [a for a in rest if a != '--dry-run']
    for i in range(0, len(rest), 2):
        if not rest[i].startswith('--') or i + 1 >= len(rest):
            sys.exit(__doc__)
        opts[rest[i][2:]] = rest[i + 1]
    if not opts.get('status'):
        sys.exit('--status is required')

    body = {}
    defects = [d.strip() for d in opts.get('defects', '').split(',') if d.strip()]
    bad = [d for d in defects if not KEY.match(d)]
    if bad:
        sys.exit(f'--defects takes Jira keys only (e.g. MODINV-1433), not: {", ".join(bad)}')
    if defects:
        body['defects'] = ', '.join(defects)
    comment = opts.get('comment')
    if opts.get('comment-file'):
        with open(os.path.expanduser(opts['comment-file']), encoding='utf-8') as f:
            comment = f.read()
    if comment:
        body['comment'] = comment

    base, headers = common.testrail(common.load_config())
    statuses = call(base, headers, 'get_statuses')
    wanted = opts['status'].strip().lower()
    status = next((s for s in statuses if wanted in (s['name'].lower(), s['label'].lower())), None)
    if not status:
        sys.exit(f"unknown status {opts['status']}; available: {', '.join(s['label'] for s in statuses)}")
    body = {'status_id': status['id'], **body}

    if dry:
        print(f'DRY RUN - would POST add_result_for_case/{run_id}/{case_id} (status {status["label"]}):')
        print(json.dumps(body, indent=1, ensure_ascii=False))
        return
    res = call(base, headers, f'add_result_for_case/{run_id}/{case_id}', body)
    print(f"C{case_id} in run {run_id}: result {res.get('id')} posted, status {status['label']}"
          + (f", defects {body['defects']}" if body.get('defects') else ''))


if __name__ == '__main__':
    main()
