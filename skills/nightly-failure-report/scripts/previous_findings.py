#!/usr/bin/env python3
"""Collect what earlier analyses concluded about the tests that failed in this run.

Usage: python previous_findings.py <workdir> [--history <dir>] [--limit 5]

Looks at earlier work folders - every sibling of <workdir> (or of each --history dir) that holds both
analysis.json and meta.json - newest run first. For every failed test in <workdir>/tests.json it
records the fixes those analyses put it in: run, fix id, type, cause, confidence, title, evidence,
ticket, changed paths, and the test's note.

Writes <workdir>/previous_findings.json and adds a "previously:" line under each test in dump.md.
Read-only for the earlier folders.
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402,F401  (UTF-8 console output)


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def run_start(meta):
    try:
        return datetime.datetime.strptime(meta['start'], '%b %d, %Y %H:%M')
    except (KeyError, ValueError):
        return datetime.datetime.min


def earlier_runs(work, history_dirs):
    here = os.path.normcase(os.path.abspath(work))
    found = {}
    for parent in history_dirs:
        if not os.path.isdir(parent):
            continue
        for name in os.listdir(parent):
            d = os.path.join(parent, name)
            key = os.path.normcase(os.path.abspath(d))
            if key == here or key in found:
                continue
            if os.path.isfile(os.path.join(d, 'analysis.json')) and os.path.isfile(os.path.join(d, 'meta.json')):
                found[key] = d
    runs = []
    for d in found.values():
        try:
            runs.append((d, load(os.path.join(d, 'meta.json')), load(os.path.join(d, 'analysis.json'))))
        except (OSError, ValueError):
            continue
    return sorted(runs, key=lambda r: run_start(r[1]), reverse=True)


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        sys.exit(__doc__)
    work, history, limit = args[0], [], 5
    i = 1
    while i < len(args):
        if args[i] == '--history' and i + 1 < len(args):
            history.append(args[i + 1]); i += 2
        elif args[i] == '--limit' and i + 1 < len(args):
            limit = int(args[i + 1]); i += 2
        else:
            sys.exit(__doc__)
    history = history or [os.path.dirname(os.path.abspath(work))]

    current_meta = load(os.path.join(work, 'meta.json'))
    ids = {t['id'] for t in load(os.path.join(work, 'tests.json'))}
    runs = [r for r in earlier_runs(work, history) if run_start(r[1]) <= run_start(current_meta)]

    per_test = {}
    for d, meta, an in runs:
        label = f"{meta.get('job', '?')} #{meta.get('build', '?')} ({meta.get('start', '?')})"
        for f in an.get('fixes', []):
            for tid, note in (f.get('tests') or {}).items():
                if tid not in ids or len(per_test.get(tid, [])) >= limit:
                    continue
                per_test.setdefault(tid, []).append(dict(
                    run=label, folder=d, fix=f.get('id'), type=f.get('type'), cause=f.get('cause'),
                    confidence=f.get('confidence'), title=f.get('title'), evidence=f.get('evidence'),
                    ticket=f.get('ticket'), jira=f.get('jira'), note=note,
                    paths=sorted({c.get('path') for c in f.get('changes') or [] if c.get('path')})))

    json.dump(dict(runs=[dict(folder=d, job=m.get('job'), build=m.get('build'), start=m.get('start')) for d, m, _ in runs],
                   tests=per_test),
              open(os.path.join(work, 'previous_findings.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    dump = os.path.join(work, 'dump.md')
    if os.path.exists(dump):
        lines = [l for l in open(dump, encoding='utf-8').read().split('\n') if not l.startswith('  previously:')]
        out = []
        for l in lines:
            out.append(l)
            m = re.match(r'- (C\d+) ', l)
            if m and per_test.get(m.group(1)):
                p = per_test[m.group(1)][0]
                more = f" (+{len(per_test[m.group(1)]) - 1} older)" if len(per_test[m.group(1)]) > 1 else ''
                out.append(f"  previously: {p['run']} {p['fix']} [{p['cause']}, {p['confidence']}] {p['title'][:110]}{more}")
        open(dump, 'w', encoding='utf-8').write('\n'.join(out))

    print(f"earlier analyses={len(runs)} tests with earlier findings={len(per_test)}/{len(ids)} "
          f"→ {work}/previous_findings.json")
    for d, m, _ in runs[:8]:
        print(f"  {m.get('job')} #{m.get('build')} {m.get('start')}  {common.disp(d)}")


if __name__ == '__main__':
    main()
