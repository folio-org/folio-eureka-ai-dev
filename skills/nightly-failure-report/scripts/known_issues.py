#!/usr/bin/env python3
"""Registry of known issues that persist across runs (stable keys KI-01, KI-02, ...).

Fix ids (F01, F02, ...) are per report. A known issue keeps its KI key in every run it shows up in,
next to the Jira key when there is one. The registry is known_issues.json in the folder that holds the
work folders (the parent of <workdir>; override with --registry <path>).

Usage:
  python known_issues.py match <workdir>
      Matches this run's failed tests (tests.json) to open and fixed issues: by test id, or by the
      issue's "error" regex on the test error. Writes <workdir>/known_matches.json and adds a
      "known:" line under each matched test in dump.md. A match on a "fixed" issue means it is back.
  python known_issues.py record <workdir>
      After analysis.json is final: for every fix with "known": "KI-07" (or a list), adds this run and
      fix id to the issue's "seen" list and the fix's tests to the issue's tests.
  python known_issues.py add <workdir|registry dir> --title "..." [--ticket KEY] [--tests C1,C2]
                             [--error REGEX] [--status open|fixed|closed] [--note "..."]
      Creates the next KI key and prints it. Add an issue when it shows up in a second run, or when it
      has a ticket (it will keep failing until the ticket is fixed).
  python known_issues.py set <workdir|registry dir> KI-07 status=fixed note="..." [ticket=KEY]
  python known_issues.py list <workdir|registry dir>
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

STATUSES = ('open', 'fixed', 'closed')


def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write('\n')
    os.replace(tmp, path)


def registry_path(target, override=None):
    if override:
        return os.path.abspath(os.path.expanduser(override))
    target = os.path.abspath(target)
    if os.path.isfile(os.path.join(target, 'tests.json')) or os.path.isfile(os.path.join(target, 'meta.json')):
        target = os.path.dirname(target)
    return os.path.join(target, 'known_issues.json')


def run_label(meta):
    job = meta.get('job', '')
    return f"{'ECS ' if 'ECS' in job else ''}#{meta.get('build', '?')}"


def by_key(reg):
    return {i['key']: i for i in reg['issues']}


def test_no(tid):
    return int(tid[1:]) if tid[1:].isdigit() else 0


def cmd_match(work, reg_path):
    reg = load(reg_path, {'issues': []})
    tests = load(os.path.join(work, 'tests.json'), [])
    label = run_label(load(os.path.join(work, 'meta.json'), {}))
    matches = {}
    for t in tests:
        text = ' '.join(str(t.get(k) or '') for k in ('err', 'msg'))
        for i in reg['issues']:
            if i.get('status') == 'closed':
                continue
            how = []
            if t['id'] in i.get('tests', []):
                how.append('test id')
            if i.get('error') and re.search(i['error'], text):
                how.append('error')
            if how:
                matches.setdefault(t['id'], []).append(dict(key=i['key'], by=' + '.join(how), status=i.get('status'),
                                                            ticket=i.get('ticket'), title=i['title']))
    save(os.path.join(work, 'known_matches.json'), dict(registry=common.disp(reg_path), run=label, tests=matches))

    dump = os.path.join(work, 'dump.md')
    if os.path.exists(dump):
        lines = [l for l in open(dump, encoding='utf-8').read().split('\n') if not l.startswith('  known:')]
        out = []
        for l in lines:
            out.append(l)
            m = re.match(r'- (C\d+) ', l)
            for k in matches.get(m.group(1), []) if m else []:
                back = ' - marked FIXED, it is back' if k['status'] == 'fixed' else ''
                out.append(f"  known: {k['key']}{' ' + k['ticket'] if k['ticket'] else ''} (by {k['by']}){back}: {k['title'][:100]}")
        open(dump, 'w', encoding='utf-8').write('\n'.join(out))

    per_issue = {}
    for tid, ks in matches.items():
        for k in ks:
            per_issue.setdefault(k['key'], []).append(tid)
    issues = by_key(reg)
    folder = os.path.basename(os.path.abspath(work))
    print(f"known issues: {len(reg['issues'])} in {common.disp(reg_path)}; matched {len(matches)}/{len(tests)} tests "
          f"to {len(per_issue)} issue(s) → {common.disp(work)}/known_matches.json")
    print("  (a test-id match is a hint: the test was in that issue before - confirm it has the same cause now)")
    for key, tids in sorted(per_issue.items()):
        i = issues[key]
        seen = ', '.join(dict.fromkeys(s['run'] for s in i.get('seen', []) if s.get('folder') != folder))
        flag = '  <-- marked FIXED, it is back' if i.get('status') == 'fixed' else ''
        print(f"  {key} [{i.get('status')}]{' ' + i['ticket'] if i.get('ticket') else ''} seen: {seen or '-'}{flag}")
        print(f"      {i['title'][:110]}")
        print(f"      tests: {' '.join(sorted(tids))}")


def cmd_record(work, reg_path):
    reg = load(reg_path)
    if not reg:
        sys.exit(f'no registry at {common.disp(reg_path)}')
    an = load(os.path.join(work, 'analysis.json'))
    if not an:
        sys.exit(f'no analysis.json in {common.disp(work)}')
    label = run_label(load(os.path.join(work, 'meta.json'), {}))
    folder = os.path.basename(os.path.abspath(work))
    issues = by_key(reg)
    links = [(f, key) for f in an['fixes'] for key in
             ([f['known']] if isinstance(f.get('known'), str) else f.get('known') or [])]
    for f, key in links:
        if key not in issues:
            sys.exit(f"{f['id']} refers to unknown issue {key} - add it first")
    # re-recording a run replaces its earlier entries on the issues it references
    # (one issue can have several fixes in a run)
    for key in {key for _, key in links}:
        issues[key]['seen'] = [s for s in issues[key].get('seen', []) if s.get('folder') != folder]
    done = []
    for f, key in links:
        i = issues[key]
        i['seen'].append(dict(run=label, folder=folder, fix=f['id'], tests=sorted(f.get('tests') or {})))
        i['tests'] = sorted(set(i.get('tests', [])) | set(f.get('tests') or {}), key=test_no)
        done.append(f"{key} ← {label} {f['id']}")
    save(reg_path, reg)
    print(f"recorded {len(done)} link(s) in {common.disp(reg_path)}")
    for d in done:
        print('  ' + d)


def parse_opts(args):
    opts, i = {}, 0
    while i < len(args):
        if args[i].startswith('--') and i + 1 < len(args):
            opts[args[i][2:]] = args[i + 1]
            i += 2
        else:
            sys.exit(f'unexpected argument {args[i]}\n{__doc__}')
    return opts


def cmd_add(reg_path, args):
    opts = parse_opts(args)
    if not opts.get('title'):
        sys.exit('--title is required')
    status = opts.get('status', 'open')
    if status not in STATUSES:
        sys.exit(f'--status must be one of {STATUSES}')
    if opts.get('error'):
        re.compile(opts['error'])
    reg = load(reg_path, {'issues': []})
    n = max([int(i['key'].split('-')[1]) for i in reg['issues']] or [0]) + 1
    issue = dict(key=f'KI-{n:02d}', title=opts['title'], status=status)
    for k in ('ticket', 'error', 'note'):
        if opts.get(k):
            issue[k] = opts[k]
    issue['tests'] = sorted({t.strip() for t in opts.get('tests', '').split(',') if t.strip()}, key=test_no)
    issue['seen'] = []
    reg['issues'].append(issue)
    os.makedirs(os.path.dirname(reg_path), exist_ok=True)
    save(reg_path, reg)
    print(issue['key'])


def cmd_set(reg_path, args):
    if not args:
        sys.exit(__doc__)
    reg = load(reg_path)
    issue = by_key(reg or {'issues': []}).get(args[0])
    if not issue:
        sys.exit(f'no issue {args[0]} in {common.disp(reg_path)}')
    for a in args[1:]:
        k, _, v = a.partition('=')
        if k not in ('status', 'note', 'ticket', 'title', 'error'):
            sys.exit(f'cannot set {k}')
        if k == 'status' and v not in STATUSES:
            sys.exit(f'status must be one of {STATUSES}')
        if k == 'error':
            re.compile(v)
        issue[k] = v
    save(reg_path, reg)
    print(f"{issue['key']}: " + ', '.join(f'{k}={issue.get(k)}' for k in ('status', 'ticket', 'note') if issue.get(k)))


def cmd_list(reg_path):
    reg = load(reg_path, {'issues': []})
    print(f'# {common.disp(reg_path)}')
    for i in reg['issues']:
        seen = ', '.join(f"{s['run']} {s['fix']}" for s in i.get('seen', []))
        print(f"{i['key']} [{i['status']}]{' ' + i['ticket'] if i.get('ticket') else ''}  {i['title'][:90]}")
        print(f"      seen: {seen or '-'}")


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    cmd, target, rest = args[0], args[1], args[2:]
    override = None
    if '--registry' in rest:
        j = rest.index('--registry')
        if j + 1 >= len(rest):
            sys.exit('--registry needs a path')
        override = rest[j + 1]
        rest = rest[:j] + rest[j + 2:]
    reg_path = registry_path(target, override)
    if cmd == 'match':
        cmd_match(target, reg_path)
    elif cmd == 'record':
        cmd_record(target, reg_path)
    elif cmd == 'add':
        cmd_add(reg_path, rest)
    elif cmd == 'set':
        cmd_set(reg_path, rest)
    elif cmd == 'list':
        cmd_list(reg_path)
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
