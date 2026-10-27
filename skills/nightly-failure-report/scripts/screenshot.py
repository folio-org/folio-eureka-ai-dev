#!/usr/bin/env python3
"""Download the Allure screenshots of given tests so you can look at them.

Usage: python3 -I screenshot.py <workdir> <test id> [<test id> ...]

Saves <workdir>/shots/<test id>-<n>.png and prints the paths. Open the images to see what the page showed.
"""
import json
import os
import sys
import urllib.request
from glob import glob


def attachments(stage, out):
    for a in stage.get('attachments') or []:
        if a.get('type', '').startswith('image/'):
            out.append(a['source'])
    for s in stage.get('steps') or []:
        attachments(s, out)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    work, ids = sys.argv[1], set(sys.argv[2:])
    base = json.load(open(os.path.join(work, 'allure', 'index.json')))['allure']
    os.makedirs(os.path.join(work, 'shots'), exist_ok=True)
    found = set()
    for f in glob(os.path.join(work, 'allure', 'tc', '*.json')):
        t = json.load(open(f))
        tid = t['name'].split(' ', 1)[0]
        if tid not in ids:
            continue
        found.add(tid)
        srcs = []
        for key in ('beforeStages', 'testStage', 'afterStages'):
            v = t.get(key)
            for s in (v if isinstance(v, list) else [v]):
                if s:
                    attachments(s, srcs)
        if not srcs:
            print(f'{tid}: no screenshot in Allure')
        for i, src in enumerate(srcs[:3], 1):
            path = os.path.join(work, 'shots', f'{tid}-{i}.png')
            if not os.path.exists(path):
                with urllib.request.urlopen(f'{base}data/attachments/{src}', timeout=60) as r:
                    open(path, 'wb').write(r.read())
            print(path)
    for tid in sorted(ids - found):
        print(f'{tid}: test not found among failed tests')


if __name__ == '__main__':
    main()
