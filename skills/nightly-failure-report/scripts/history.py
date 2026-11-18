#!/usr/bin/env python3
"""Share triage history (earlier analyses and the known-issue registry) with other people.

Usage:
  python history.py export <zip file> [--last <n>] [--teams promin,eureka] [--work-dir <dir>]
      Packs known_issues.json and, for each analyzed run (a work folder with analysis.json and
      meta.json), only the files later analyses and readers need: analysis.json, meta.json, tests.json,
      report.html, linked_defects.json, previous_findings.json, known_matches.json, dump.md and other
      top-level .md notes. Downloaded Allure data, screenshots, scripts, logs and anything outside the
      run folders (local config, credentials) are left out. --last keeps the newest <n> runs;
      --teams keeps only runs whose analysis has a fix for a test of those teams.
  python history.py import <zip file> [--work-dir <dir>] [--overwrite]
      Unpacks into the work folder root (paths.work_dir, see config.py), next to your own runs, so
      previous_findings.py, known_issues.py and render.py use them. Existing run folders are kept
      unless --overwrite. The known-issue registry is copied when you have none, merged when the
      issues match yours (same key and title), and otherwise saved as known_issues.imported.json
      for you to reconcile by hand.

The default work folder root is the config's paths.work_dir (or NIGHTLY_TRIAGE_DIR); --work-dir overrides it.
"""
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

RUN_FILES = ('analysis.json', 'meta.json', 'tests.json', 'report.html', 'linked_defects.json',
             'previous_findings.json', 'known_matches.json')
REGISTRY = 'known_issues.json'
# failed cy.request() messages (kept in tests.json) include the request headers: cookies with access tokens
REDACT = [
    (re.compile(r'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]*'), '<redacted-token>'),
    (re.compile(r'((?:folioAccessToken|folioRefreshToken)=)[^;\s"\\]+'), r'\1<redacted>'),
    (re.compile(r'((?:x-okapi-token|[Aa]uthorization|[Cc]ookie)\\?"?\s*[:=]\s*\\?"?)(?:Basic |Bearer )?[^\s"\\,;]{8,}'),
     r'\1<redacted>'),
    (re.compile(r'(\\?"password\\?"\s*:\s*\\?")[^"\\]+'), r'\1<redacted>'),
]


def redact(text):
    for pattern, repl in REDACT:
        text = pattern.sub(repl, text)
    return text


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def parse(args, flags=()):
    opts, pos, i = {}, [], 0
    while i < len(args):
        a = args[i]
        if a.startswith('--') and a[2:] in flags:
            opts[a[2:]] = True
            i += 1
        elif a.startswith('--') and i + 1 < len(args):
            opts[a[2:]] = args[i + 1]
            i += 2
        else:
            pos.append(a)
            i += 1
    return opts, pos


def root_of(opts):
    return os.path.abspath(os.path.expanduser(opts.get('work-dir') or common.work_root(common.load_config())))


def runs_in(root):
    out = []
    for name in os.listdir(root):
        d = os.path.join(root, name)
        if os.path.isfile(os.path.join(d, 'analysis.json')) and os.path.isfile(os.path.join(d, 'meta.json')):
            out.append((os.path.getmtime(os.path.join(d, 'analysis.json')), name, d))
    return [x[1:] for x in sorted(out, reverse=True)]


def has_team(run_dir, teams):
    tests = {t['id']: t.get('team') for t in load(os.path.join(run_dir, 'tests.json'))} \
        if os.path.isfile(os.path.join(run_dir, 'tests.json')) else {}
    for f in load(os.path.join(run_dir, 'analysis.json')).get('fixes', []):
        if any(tests.get(tid) in teams for tid in f.get('tests') or {}):
            return True
    return False


def with_runs(run_dir):
    """tests.json with the per-run history filled in. Folders extracted before extract.py wrote it keep
    it only in the downloaded Allure data, which is not exported."""
    import render
    tests = load(os.path.join(run_dir, 'tests.json'))
    allure = load(os.path.join(run_dir, 'meta.json')).get('allure', '')
    for t in tests:
        if t.get('runs') is None:
            t['runs'] = render.history_runs(run_dir, t, allure)
    return tests


def export(zip_path, opts):
    root = root_of(opts)
    runs = runs_in(root)
    if opts.get('teams'):
        teams = {t.strip().lower() for t in opts['teams'].split(',') if t.strip()}
        runs = [r for r in runs if has_team(r[1], teams)]
    if opts.get('last'):
        runs = runs[:int(opts['last'])]
    if not runs and not os.path.isfile(os.path.join(root, REGISTRY)):
        sys.exit(f'nothing to export in {common.disp(root)}')
    zip_path = os.path.abspath(os.path.expanduser(zip_path))
    n_files = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        if os.path.isfile(os.path.join(root, REGISTRY)):
            with open(os.path.join(root, REGISTRY), encoding='utf-8') as fh:
                z.writestr(REGISTRY, redact(fh.read()))
            n_files += 1
        for name, d in runs:
            for f in sorted(os.listdir(d)):
                p = os.path.join(d, f)
                if not os.path.isfile(p) or not (f in RUN_FILES or f.endswith('.md')):
                    continue
                if f == 'tests.json':
                    text = json.dumps(with_runs(d), indent=1, ensure_ascii=False)
                else:
                    with open(p, encoding='utf-8', errors='replace') as fh:
                        text = fh.read()
                z.writestr(f'{name}/{f}', redact(text))
                n_files += 1
    size = os.path.getsize(zip_path) / 1e6
    print(f'exported {len(runs)} run(s), {n_files} files, {size:.1f} MB → {common.disp(zip_path)}')
    print('  runs: ' + ', '.join(name for name, _ in runs))
    print('  .md notes in run folders are included - check them before sending the file')


def merge_registry(mine, theirs):
    """Merge when every shared key has the same title; returns the merged registry or None on conflict."""
    by_key = {i['key']: i for i in mine['issues']}
    conflicts = [i['key'] for i in theirs['issues'] if i['key'] in by_key and by_key[i['key']]['title'] != i['title']]
    if conflicts:
        return None, conflicts
    for i in theirs['issues']:
        if i['key'] not in by_key:
            mine['issues'].append(i)
            continue
        m = by_key[i['key']]
        m['tests'] = sorted(set(m.get('tests', [])) | set(i.get('tests', [])))
        seen = {(s.get('folder'), s.get('fix')) for s in m.get('seen', [])}
        m['seen'] = m.get('seen', []) + [s for s in i.get('seen', []) if (s.get('folder'), s.get('fix')) not in seen]
        for k in ('ticket', 'note', 'error'):
            if i.get(k) and not m.get(k):
                m[k] = i[k]
    mine['issues'].sort(key=lambda i: int(i['key'].split('-')[1]))
    return mine, []


def import_(zip_path, opts):
    root = root_of(opts)
    os.makedirs(root, exist_ok=True)
    overwrite = opts.get('overwrite')
    added, kept = [], []
    with zipfile.ZipFile(os.path.expanduser(zip_path)) as z:
        names = z.namelist()
        for n in names:
            parts = n.split('/')
            if n.startswith(('/', '\\')) or ':' in n or '..' in parts or '\\' in n or len(parts) > 2:
                sys.exit(f'refusing to import {zip_path}: unexpected path {n}')
        for run in sorted({n.split('/')[0] for n in names if '/' in n}):
            dest = os.path.join(root, run)
            if os.path.exists(dest) and not overwrite:
                kept.append(run)
                continue
            os.makedirs(dest, exist_ok=True)
            for n in names:
                if n.startswith(run + '/') and not n.endswith('/'):
                    with open(os.path.join(dest, n.split('/', 1)[1]), 'wb') as f:
                        f.write(z.read(n))
            added.append(run)
        reg_msg = 'no known-issue registry in the file'
        if REGISTRY in names:
            theirs = json.loads(z.read(REGISTRY).decode('utf-8'))
            mine_path = os.path.join(root, REGISTRY)
            if not os.path.exists(mine_path):
                merged, conflicts = theirs, []
            else:
                merged, conflicts = merge_registry(load(mine_path), theirs)
            if merged is None:
                side = os.path.join(root, 'known_issues.imported.json')
                with open(side, 'w', encoding='utf-8') as f:
                    json.dump(theirs, f, indent=1, ensure_ascii=False)
                reg_msg = (f'registry NOT merged - keys with different titles: {", ".join(conflicts)}; '
                           f'saved as {common.disp(side)} to reconcile by hand')
            else:
                with open(mine_path, 'w', encoding='utf-8') as f:
                    json.dump(merged, f, indent=1, ensure_ascii=False)
                    f.write('\n')
                reg_msg = f'registry: {len(merged["issues"])} issue(s) in {common.disp(mine_path)}'
    print(f'imported {len(added)} run(s) into {common.disp(root)}' + (f": {', '.join(added)}" if added else ''))
    if kept:
        print(f"  kept your existing {', '.join(kept)} (use --overwrite to replace)")
    print('  ' + reg_msg)


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] not in ('export', 'import'):
        sys.exit(__doc__)
    opts, pos = parse(args[1:], flags=('overwrite',))
    if len(pos) != 1:
        sys.exit(__doc__)
    (export if args[0] == 'export' else import_)(pos[0], opts)


if __name__ == '__main__':
    main()
