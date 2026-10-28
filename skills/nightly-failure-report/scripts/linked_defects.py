#!/usr/bin/env python3
"""Collect bug tickets previously linked to the failed tests in TestRail.

Usage: python linked_defects.py <workdir> [--run <TestRail run id>] [--days 5]

For every failed test in <workdir>/tests.json, reads the TestRail results of that case in one
TestRail run, from <days> days before the analyzed build started until now, and collects the Jira
keys in their "defects" field. Then reads each ticket's status from Jira (public REST, no auth).

The TestRail run is, in order:
  --run <id>                              (use when runs are not reused, e.g. a new run per rerun)
  TESTRAIL_RUN_ID parameter of the build  (runCypressTests)
  "RunID: <id>" in the build console      (scheduled nightly jobs)

TestRail credentials: the config (testrail.*, see config.py), or TESTRAIL_BASE_URL / TESTRAIL_USERNAME /
TESTRAIL_PASSWORD environment variables. Exit code 3: they are missing - ask the user and save them with
config.py set (or config.py import-testrail <.env>), or skip this step. Credentials are never printed.

Writes <workdir>/linked_defects.json and adds a "linked:" line under each test in dump.md.
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402,F401  (UTF-8 console output)

JIRA = 'https://folio-org.atlassian.net'
KEY = re.compile(r'\b[A-Z][A-Z0-9]+-\d+\b')
TEAM_FIELD = 'customfield_10057'


def get(url, headers=None, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(int(e.headers.get('Retry-After') or 10))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(3)


def find_run_id(build_url):
    """TESTRAIL_RUN_ID build parameter, else the first 'RunID: N' line of the console."""
    try:
        d = json.loads(get(build_url + 'api/json?tree=actions[parameters[name,value]]'))
        for a in d.get('actions', []):
            for p in a.get('parameters') or []:
                if p.get('name') == 'TESTRAIL_RUN_ID' and str(p.get('value') or '').strip().isdigit():
                    return int(p['value']), 'build parameter TESTRAIL_RUN_ID'
    except urllib.error.URLError:
        pass
    req = urllib.request.Request(build_url + 'consoleText')
    with urllib.request.urlopen(req, timeout=120) as r:
        for raw in r:
            m = re.search(r'RunID:\s*(\d+)', raw.decode('utf8', 'replace'))
            if m:
                return int(m.group(1)), 'build console "RunID"'
    return None, None


def case_results(base, headers, run_id, case_id, after):
    """All results of one case in one run created after <after> (epoch seconds).

    get_results_for_case has no date filter (created_after only works for get_results_for_run),
    but returns the newest results first, so paging stops at the first page older than <after>.
    """
    out, path = [], f'get_results_for_case/{run_id}/{case_id}&limit=250'
    while path:
        try:
            d = json.loads(get(f'{base}/index.php?/api/v2/{path}', headers))
        except urllib.error.HTTPError as e:
            return None if e.code == 400 else out  # 400: case is not in this run
        page = d.get('results', d if isinstance(d, list) else [])
        out += [r for r in page if r['created_on'] >= after]
        nxt = (d.get('_links') or {}).get('next') if isinstance(d, dict) else None
        path = nxt.split('/api/v2/', 1)[1] if nxt and page and min(r['created_on'] for r in page) >= after else None
    return out


def jira_issue(key):
    try:
        d = json.loads(get(f'{JIRA}/rest/api/2/issue/{key}?fields=summary,status,resolution,resolutiondate,'
                           f'fixVersions,{TEAM_FIELD}'))
    except urllib.error.HTTPError as e:
        return dict(key=key, error=f'HTTP {e.code}')
    f = d['fields']
    status = f.get('status') or {}
    return dict(
        key=key, summary=f.get('summary'), status=status.get('name'),
        open=(status.get('statusCategory') or {}).get('key') != 'done',
        resolution=(f.get('resolution') or {}).get('name'), resolved=(f.get('resolutiondate') or '')[:10] or None,
        team=(f.get(TEAM_FIELD) or {}).get('value'), fix_versions=[v['name'] for v in f.get('fixVersions') or []])


def fmt(link, issues):
    i = issues.get(link['key'], {})
    state = 'unknown' if i.get('error') else ('open' if i.get('open') else 'closed')
    status = i.get('status') or i.get('error') or '?'
    return f"{link['key']} ({status}, {state}, linked {link['last_linked']})"


def annotate_dump(work, per_test, issues):
    path = os.path.join(work, 'dump.md')
    if not os.path.exists(path):
        return
    lines = open(path, encoding='utf-8').read().split('\n')
    lines = [l for l in lines if not l.startswith(('  linked:', '  linked (others):'))]  # idempotent reruns
    out = []
    for l in lines:
        out.append(l)
        m = re.match(r'- (C\d+) ', l)
        if m and per_test.get(m.group(1)):
            out.append('  linked: ' + '; '.join(fmt(x, issues) for x in per_test[m.group(1)]))
        elif l.startswith('- +') and 'more with the same error' in l:
            ids = re.findall(r'\b(C\d+) ', l.split(':', 1)[1])
            parts = [f"{c}: " + ', '.join(fmt(x, issues) for x in per_test[c]) for c in ids if per_test.get(c)]
            if parts:
                out.append('  linked (others): ' + '; '.join(parts))
    open(path, 'w', encoding='utf-8').write('\n'.join(out))


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        sys.exit(__doc__)
    work, run_id, days = args[0], None, 5
    i = 1
    while i < len(args):
        if args[i] == '--run' and i + 1 < len(args):
            run_id, i = int(args[i + 1]), i + 2
        elif args[i] == '--days' and i + 1 < len(args):
            days, i = int(args[i + 1]), i + 2
        else:
            sys.exit(__doc__)

    meta = json.load(open(os.path.join(work, 'meta.json'), encoding='utf-8'))
    tests = json.load(open(os.path.join(work, 'tests.json'), encoding='utf-8'))
    build_url = meta['allure'].split('allure')[0]
    source = '--run argument'
    if run_id is None:
        run_id, source = find_run_id(build_url)
        if run_id is None:
            sys.exit(f'No TestRail run id found for {build_url}; pass --run <id>')

    base, headers = common.testrail(common.load_config())
    run = json.loads(get(f'{base}/index.php?/api/v2/get_run/{run_id}', headers))
    start = datetime.datetime.strptime(meta['start'], '%b %d, %Y %H:%M').replace(tzinfo=datetime.timezone.utc)
    since = start - datetime.timedelta(days=days)
    after = int(since.timestamp())

    case_ids = sorted({t['id'] for t in tests if re.fullmatch(r'C\d+', t['id'])})
    with ThreadPoolExecutor(6) as pool:
        results = dict(zip(case_ids, pool.map(lambda c: case_results(base, headers, run_id, c[1:], after), case_ids)))

    per_test, not_in_run = {}, []
    for cid, res in results.items():
        if res is None:
            not_in_run.append(cid)
            continue
        links = {}
        for r in res:
            when = datetime.datetime.fromtimestamp(r['created_on'], datetime.timezone.utc).strftime('%Y-%m-%d')
            for key in KEY.findall(r.get('defects') or ''):
                l = links.setdefault(key, dict(key=key, first_linked=when, last_linked=when, results=0))
                l['first_linked'] = min(l['first_linked'], when)
                l['last_linked'] = max(l['last_linked'], when)
                l['results'] += 1
        if links:
            per_test[cid] = sorted(links.values(), key=lambda x: x['last_linked'], reverse=True)

    keys = sorted({l['key'] for ls in per_test.values() for l in ls})
    with ThreadPoolExecutor(8) as pool:
        issues = {i['key']: i for i in pool.map(jira_issue, keys)}

    json.dump(dict(run_id=run_id, run_name=run.get('name'), run_source=source, days=days,
                   since=since.strftime('%Y-%m-%d %H:%M UTC'), tests=per_test, issues=issues,
                   not_in_run=not_in_run),
              open(os.path.join(work, 'linked_defects.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    annotate_dump(work, per_test, issues)

    n_open = sum(1 for i in issues.values() if i.get('open'))
    print(f"run={run_id} ({run.get('name')}; from {source}) since={since:%Y-%m-%d} "
          f"cases={len(case_ids)} not_in_run={len(not_in_run)} tests_with_links={len(per_test)} "
          f"tickets={len(issues)} open={n_open} → {work}/linked_defects.json")
    for cid, ls in sorted(per_test.items()):
        print(f"  {cid}: " + '; '.join(fmt(l, issues) for l in ls))
    if not_in_run:
        print(f"  not in run {run_id}: {', '.join(not_in_run[:30])}" + (' ...' if len(not_in_run) > 30 else ''))


if __name__ == '__main__':
    main()
