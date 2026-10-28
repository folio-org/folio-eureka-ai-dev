#!/usr/bin/env python3
"""Render the HTML report from extracted data and the analysis.

Usage: python render.py <workdir>

Reads <workdir>/tests.json, meta.json, analysis.json (and linked_defects.json, if present) and
writes <workdir>/report.html.
Hard errors (the report is not built) are listed first; every fix also gets a readiness
verdict: "Ready" or "Needs verification" with the reasons, shown on its card.
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402,F401  (UTF-8 console output)

TYPES = ('test', 'app', 'data')
CAUSES = ('test-bug', 'outdated-test', 'env-pollution', 'parallel-conflict', 'app-bug', 'data-missing', 'infra')
CONF = ('Confirmed', 'Likely')
VAGUE = re.compile(r'\b(misc|other|various|several|investigate|needs? (check|investigation)|unclear|unknown|'
                   r'transient|changed or|or race)\b', re.I)
ECHO = re.compile(r'^(error:|did not find|timed out|expected |cannot read|`cy\.)', re.I)
ELLIPSIS = re.compile(r'^\s*[-+ ]?\s*(\.\.\.|…)\s*$|\s(\.\.\.|…)\s*$', re.M)
ASSERT = re.compile(r'\b(expect\(|\.should\(|cy\.expect|\.exists\(\)|\.absent\(\)|\.has\(|verify[A-Z]\w*\(|check[A-Z]\w*\()')
SKIP = re.compile(r'this\.skip\(\)|\bit\.skip\b|\bdescribe\.skip\b|^\+\s*if\s*\(.*\)\s*return;?', re.M)
WEAKER = [(re.compile(r'\.to\.(deep\.)?equal\(|\.to\.eql\('), re.compile(r'\.to\.include\(|\.to\.contain\(|AtLeast|\.to\.be\.(above|at\.least)'))]
DESTRUCTIVE_PATH = re.compile(r'polic|rules|specification|settings|configurations|profiles|mapping-rules', re.I)
PLACEHOLDER = re.compile(r'<[^<>]{2,80}>')
NOOP = re.compile(r'\(\)\s*=>\s*true\b')


def removed(diff):
    return [l[1:] for l in diff.split('\n') if l.startswith('-')]


def added(diff):
    return [l[1:] for l in diff.split('\n') if l.startswith('+')]


def weakens(diff):
    """Return a reason if the diff removes or loosens a check, else None."""
    rem, add = removed(diff), added(diff)
    rem_a = sum(1 for l in rem if ASSERT.search(l))
    add_a = sum(1 for l in add if ASSERT.search(l))
    if rem_a > add_a:
        return 'removes assertions'
    if SKIP.search(diff):
        return 'skips the test or returns early'
    for strict, loose in WEAKER:
        if any(strict.search(l) for l in rem) and any(loose.search(l) for l in add):
            return 'loosens an exact assertion'
    return None


def check(an, tests):
    errs = []
    by_id = {t['id']: t for t in tests}
    seen = {}
    for i, f in enumerate(an.get('fixes', [])):
        name = f.get('id') or f'#{i}'
        typ, ch, data, ftests = f.get('type'), f.get('changes') or [], f.get('data') or [], f.get('tests') or {}
        if typ not in TYPES:
            errs.append(f'{name}: type must be one of {TYPES}')
        if f.get('cause') not in CAUSES:
            errs.append(f'{name}: cause must be one of {CAUSES}')
        if f.get('confidence') not in CONF:
            errs.append(f'{name}: confidence must be one of {CONF}')
        for field in ('title', 'evidence'):
            if not f.get(field):
                errs.append(f'{name}: missing {field}')
        if VAGUE.search(f.get('title', '')):
            errs.append(f'{name}: vague title {f.get("title")!r}; one fix = one concrete problem')
        # an app bug that is already filed needs no diff: the fix is the existing ticket
        existing = typ == 'app' and f.get('ticket') and str(f.get('jira', '')).startswith('Existing:')
        if typ in ('test', 'app') and not ch and not existing:
            errs.append(f'{name}: a {typ} fix needs "changes"')
        if typ == 'data' and not data:
            errs.append(f'{name}: a data fix needs "data"')
        if typ == 'app' and not existing:
            if not f.get('repo') or f.get('repo') == 'stripes-testing':
                errs.append(f'{name}: an app fix needs "repo" (the FOLIO module)')
            if not f.get('ref'):
                errs.append(f'{name}: an app fix needs "ref" (module commit you read)')
            if not f.get('jira'):
                errs.append(f'{name}: an app fix needs a "jira" summary')
        for c in ch:
            where = f'{name}/{c.get("path")}'
            if not c.get('path'):
                errs.append(f'{name}: every change needs "path"')
            if typ == 'app' and not c.get('line'):
                errs.append(f'{where}: app changes need "line"')
            if not c.get('diff'):
                errs.append(f'{where}: every change needs a real "diff"')
                continue
            if ELLIPSIS.search(c['diff']):
                errs.append(f'{where}: diff contains "..." — write the full lines so the patch can be applied')
            if NOOP.search('\n'.join(added(c['diff']))):
                errs.append(f'{where}: diff adds a no-op predicate (() => true)')
            if not added(c['diff']) and not removed(c['diff']):
                errs.append(f'{where}: diff has no -/+ lines')
            cov = c.get('tests')
            if cov != 'all' and not (isinstance(cov, list) and cov):
                errs.append(f'{where}: "tests" must be "all" or a list of the test ids this change fixes')
        for d in data:
            if not (d.get('request') or d.get('ui')):
                errs.append(f'{name}: every data item needs "request" or "ui"')
        if not ftests:
            errs.append(f'{name}: no tests')
        for tid, note in ftests.items():
            if tid in seen:
                errs.append(f'{tid} is in both {seen[tid]} and {name}')
            seen[tid] = name
            if tid not in by_id:
                errs.append(f'{name}: unknown test {tid}')
            if note and ECHO.search(note):
                errs.append(f'{name}/{tid}: note repeats the error text; write what is wrong instead')

        # every test must be fixed by a change (or by the data/app fix itself)
        if typ == 'test' and ch:
            covered = set()
            shared = any(c.get('tests') == 'all' for c in ch)
            for c in ch:
                if isinstance(c.get('tests'), list):
                    covered |= set(c['tests'])
            ids = [t for t in ftests if t in by_id]
            if shared:
                clusters = collections.Counter(by_id[t]['cluster'] for t in ids)
                top = clusters.most_common(1)[0][1] if clusters else 0
                if len(ids) > 2 and top * 2 < len(ids) and not f.get('same_cause'):
                    errs.append(f'{name}: a change with tests="all" must fix one shared cause, but these {len(ids)} tests '
                                f'have {len(clusters)} different errors. Split the fix, give each test its own change, '
                                f'or add "same_cause" proving why one change fixes all of them.')
                odd = [t for t in ids if clusters and by_id[t]['cluster'] != clusters.most_common(1)[0][0]
                       and t not in covered and not ftests.get(t) and not f.get('same_cause')]
                if odd:
                    errs.append(f'{name}: tests with a different error need a note linking them to this cause: {odd[:20]}')
            else:
                missing = [t for t in ids if t not in covered]
                if missing:
                    errs.append(f'{name}: no change fixes {missing[:20]}; list them in a change\'s "tests" or move them to their own fix')
    missing = sorted(set(by_id) - set(seen))
    if missing:
        errs.append(f'{len(missing)} tests are not in any fix: {missing[:50]}')
    return errs


def readiness(f):
    """Reasons why a developer should verify before applying. Empty list = Ready."""
    r = []
    if f['confidence'] != 'Confirmed':
        r.append('Cause is likely, not proven')
    for c in f.get('changes') or []:
        w = weakens(c.get('diff', ''))
        if w and not (c.get('ticket') or f.get('ticket')):
            r.append(f'{c["path"].rsplit("/", 1)[-1]}: {w} with no ticket showing the behavior change is intended')
    if f.get('same_cause') and f['confidence'] != 'Confirmed':
        r.append('Tests fail with different errors; the claim that one change fixes all of them is not proven')
    if f.get('cause') == 'outdated-test' and not f.get('ticket'):
        r.append('No module commit or Jira ticket proves the UI/API change is intended (could be a regression)')
    for d in f.get('data') or []:
        req = d.get('request') or {}
        if PLACEHOLDER.search(json.dumps(req)):
            r.append('Data request has placeholders: look the values up on the environment first')
            break
    for d in f.get('data') or []:
        req = d.get('request') or {}
        if req.get('method') == 'DELETE' or (req.get('method') in ('PUT', 'PATCH') and DESTRUCTIVE_PATH.search(req.get('path', ''))):
            r.append('Changes shared environment configuration: agree with the environment owner')
            break
    return list(dict.fromkeys(r))


def unreferenced_open_links(f, linked):
    """Open tickets linked to this fix's tests in TestRail that the fix never mentions."""
    text = json.dumps({k: f.get(k) for k in ('title', 'evidence', 'ticket', 'jira', 'changes', 'tests', 'same_cause')})
    by_key = collections.defaultdict(list)
    for tid in f['tests']:
        for l in linked['tests'].get(tid, []):
            if linked['issues'].get(l['key'], {}).get('open') and l['key'] not in text:
                by_key[l['key']].append(tid)
    return [f"{k} ({linked['issues'][k].get('status')}) on {len(ts)} test(s): {', '.join(ts[:8])}"
            + (' ...' if len(ts) > 8 else '') for k, ts in by_key.items()]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    work = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    tests = json.load(open(os.path.join(work, 'tests.json'), encoding='utf-8'))
    meta = json.load(open(os.path.join(work, 'meta.json'), encoding='utf-8'))
    an = json.load(open(os.path.join(work, 'analysis.json'), encoding='utf-8'))
    linked_path = os.path.join(work, 'linked_defects.json')
    linked = json.load(open(linked_path, encoding='utf-8')) if os.path.exists(linked_path) else None
    errs = check(an, tests)
    if errs:
        sys.exit(f'analysis.json is not ready ({len(errs)} problems):\n- ' + '\n- '.join(errs))

    by_id = {t['id']: t for t in tests}
    fixes, out_tests = [], []
    for f in sorted(an['fixes'], key=lambda f: -len(f['tests'])):
        teams = collections.Counter(by_id[t]['team'] for t in f['tests'])
        reasons = readiness(f)
        fixes.append({**{k: f.get(k) for k in ('id', 'type', 'cause', 'title', 'confidence', 'evidence', 'same_cause', 'repo',
                                                 'ref', 'ticket', 'owner', 'changes', 'data', 'jira')},
                      'teams': [t for t, _ in teams.most_common()], 'ready': not reasons, 'reasons': reasons})
        for tid, note in f['tests'].items():
            t = by_id[tid]
            links = [{**l, **{k: linked['issues'].get(l['key'], {}).get(k) for k in ('summary', 'status', 'open')}}
                     for l in (linked['tests'].get(tid, []) if linked else [])]
            out_tests.append(dict(uid=t['uid'], id=tid, name=t['name'], team=t['team'], status=t['status'],
                                  stage=t['stage'], fix=f['id'], note=note, err=t['err'], spec=t['spec'],
                                  hp=t['hp'], ht=t['ht'], where=t['where'], linked=links))
    data = dict(fixes=fixes, tests=out_tests, sha=meta['sha'], allure=meta['allure'], build=meta.get('build', ''),
                linked=({k: linked[k] for k in ('run_id', 'run_name', 'since')} if linked else None))

    counts = {k: sum(len(f['tests']) for f in an['fixes'] if f['type'] == k) for k in TYPES}
    n_ready = sum(1 for t in out_tests if next(f for f in fixes if f['id'] == t['fix'])['ready'])
    pct = f"{meta['passed'] / meta['total'] * 100:.1f}%" if meta['total'] else '—'
    repl = {
        '__TITLE__': f"Nightly #{meta.get('build', '')} Fixes", '__BUILD__': str(meta.get('build', '')),
        '__PERIOD__': f"{meta['start']} – {meta['stop']}", '__ENV__': an.get('environment', ''),
        '__ALLURE__': meta['allure'], '__JOB__': meta.get('job', ''), '__TOTAL__': str(meta['total']),
        '__PASSPCT__': pct, '__PASSED__': str(meta['passed']), '__NFAIL__': str(len(tests)),
        '__FIXES__': str(len(fixes)), '__NREADY__': str(n_ready), '__SHORTSHA__': meta['sha'][:7],
    }
    tpl = open(os.path.join(here, '..', 'assets', 'template.html'), encoding='utf-8').read()
    for k, v in repl.items():
        tpl = tpl.replace(k, v)
    tpl = tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    out = os.path.join(work, 'report.html')
    open(out, 'w', encoding='utf-8').write(tpl)
    print(f"fixes={len(fixes)} tests={len(tests)} ready_tests={n_ready} "
          f"test={counts['test']} app={counts['app']} data={counts['data']} → {out}")
    for f in fixes:
        if not f['ready']:
            print(f"  needs verification {f['id']} ({len(f['teams'])} team(s)): " + '; '.join(f['reasons']))
    if linked:
        for f in an['fixes']:
            refs = unreferenced_open_links(f, linked)
            if refs:
                print(f"  {f['id']} does not mention open ticket(s) linked to its tests: " + '; '.join(refs)
                      + ' - confirm they are unrelated, or reference them')
    else:
        print('  no linked_defects.json: previously linked tickets were not checked (run linked_defects.py)')


if __name__ == '__main__':
    main()
