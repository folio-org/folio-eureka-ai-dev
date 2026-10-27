#!/usr/bin/env python3
"""Download failed/broken test cases from a Jenkins Allure report.

Usage: python3 -I fetch_allure.py <allure_url> <workdir>

Writes:
  <workdir>/allure/summary.json, suites.json
  <workdir>/allure/tc/<uid>.json  (one per failed/broken test)
"""
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    base = sys.argv[1].split('#')[0].rstrip('/') + '/'
    out = os.path.join(sys.argv[2], 'allure')
    os.makedirs(os.path.join(out, 'tc'), exist_ok=True)

    summary = json.loads(get(base + 'widgets/summary.json'))
    json.dump(summary, open(os.path.join(out, 'summary.json'), 'w'))
    suites = json.loads(get(base + 'data/suites.json'))
    json.dump(suites, open(os.path.join(out, 'suites.json'), 'w'))

    uids = []

    def walk(node):
        for child in node.get('children', []):
            walk(child)
        if 'children' not in node and node.get('status') in ('failed', 'broken'):
            uids.append(node['uid'])

    walk(suites)
    uids = sorted(set(uids))

    def fetch(uid):
        path = os.path.join(out, 'tc', uid + '.json')
        if not os.path.exists(path):
            open(path, 'wb').write(get(f'{base}data/test-cases/{uid}.json'))

    with ThreadPoolExecutor(16) as pool:
        list(pool.map(fetch, uids))

    json.dump({'allure': base, 'uids': uids}, open(os.path.join(out, 'index.json'), 'w'))
    st = summary['statistic']
    print(f"total={st['total']} passed={st['passed']} failed={st['failed']} "
          f"broken={st['broken']} skipped={st['skipped']} downloaded={len(uids)}")


if __name__ == '__main__':
    main()
