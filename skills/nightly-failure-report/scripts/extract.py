#!/usr/bin/env python3
"""Turn downloaded Allure test cases into analysis input.

Usage: python3 -I extract.py <workdir> <stripes-testing repo path>

For every failed/broken test it finds the root-cause stage (before / test body),
the root error, the run history, the spec, and the exact code line it failed at
(at the commit the run used). It then clusters tests by normalized error.

Writes:
  <workdir>/tests.json    full per-test data (input for render.py)
  <workdir>/meta.json     run stats, commit, Allure URL
  <workdir>/dump.md       compact, clustered view to read during analysis
"""
import collections
import datetime
import json
import os
import posixpath
import re
import subprocess
import sys
from glob import glob

WEBPACK = re.compile(r'webpack://@folio/stripes-testing/\./(cypress/(?:e2e|support)/[^\s)":]+?\.js):(\d+)')
TEAMS = r'\((thunderjet|promin|athena|vega|helios|corsair|folijet|spitfire|firebird|volaris|citation)\)'


def git(repo, *args):
    return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True)


class Source:
    def __init__(self, repo, sha):
        self.repo, self.sha, self.cache, self.icache = repo, sha, {}, {}
        r = git(repo, 'ls-tree', '-r', '--name-only', sha, '--', 'cypress')
        self.files = set(r.stdout.split())

    def lines(self, path):
        if path not in self.cache:
            r = git(self.repo, 'show', f'{self.sha}:{path}')
            self.cache[path] = r.stdout.split('\n') if r.returncode == 0 else None
        return self.cache[path]

    def line(self, path, n):
        src = self.lines(path)
        return src[n - 1].strip()[:180] if src and 0 < n <= len(src) else None

    def exists(self, path):
        return path in self.files

    def imports(self, spec):
        if spec in self.icache:
            return self.icache[spec]
        src = self.lines(spec) or []
        out = []
        for m in re.findall(r"from '(\.[^']+)'", '\n'.join(src)):
            q = posixpath.normpath(posixpath.join(posixpath.dirname(spec), m))
            for cand in (q + '.js', q + '/index.js', q):
                if cand.endswith('.js') and self.exists(cand):
                    out.append(cand)
                    break
        self.icache[spec] = out
        return out

    def grep(self, term, paths):
        if not paths:
            return []
        r = git(self.repo, 'grep', '-n', '-F', term, self.sha, '--', *paths)
        hits = []
        for ln in r.stdout.splitlines()[:6]:
            _, p, n, code = ln.split(':', 3)
            hits.append(dict(path=p, line=int(n), code=code.strip()[:180], guess=True))
        return hits


def failing_stage(t):
    for key in ('beforeStages', 'testStage', 'afterStages'):
        v = t.get(key)
        for s in (v if isinstance(v, list) else [v]):
            if s and s.get('status') in ('failed', 'broken'):
                return key, s
    return 'testStage', {}


def deepest_failed_step(stage):
    path = []
    node = stage
    while True:
        nxt = next((y for y in node.get('steps') or [] if y.get('status') in ('failed', 'broken')), None)
        if not nxt:
            return path
        path.append((nxt.get('name') or '')[:250])
        node = nxt


def short_error(m):
    if m.startswith('`cy.request()`'):
        meth = re.search(r'Method: (\w+)', m)
        url = re.search(r'failed on:\s*\n\n(\S+)', m)
        url = url.group(1).split('.org/', 1)[-1].split('?')[0] if url else ''
        st = re.search(r'Status: ([^\n]*)', m)
        body = re.search(r'"(?:message|title|detail)": "([^"]*)"', m) or re.search(r'Body: ([^\n]{0,160})', m)
        vals = re.findall(r'"value": "([^"]{1,80})"', m)
        return (f"{meth.group(1) if meth else ''} /{url} → {st.group(1) if st else ''}" + (f" · {body.group(1)}" if body else '')
                + (f" · values: {', '.join(dict.fromkeys(vals))[:120]}" if vals else ''))
    m = re.sub(r'[━┃┣┫╋┏┓┗┛┳┻╒═├└]+', ' ', m.split('\n\n')[0]).replace('\n', ' ')
    return re.sub(r'\s+', ' ', m).strip()[:300]


def cluster_key(m):
    if m.startswith('`cy.request()`'):
        url = re.search(r'failed on:\s*\n\n(\S+)', m)
        url = url.group(1).split('.org/', 1)[-1].split('?')[0] if url else ''
        url = re.sub(r'[0-9a-f-]{36}|\d+-\d+|\d{3,}', 'ID', url)
        st = re.search(r'Status: (\d+)', m)
        body = re.search(r'"(?:message|title)": "([^"]*)"', m) or re.search(r'Body: (.{0,90})', m)
        return f"API {st.group(1) if st else '?'} {url} :: {body.group(1)[:90] if body else ''}"
    first = m.split('\n')[0]
    first = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'ID', first)
    first = re.sub(r'\b(AT|at|autotest)_[\w.\-]+', 'NAME', first)
    return 'UI ' + re.sub(r'"[^"]*"', '"X"', re.sub(r'\d+', 'N', first))[:120]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    work, repo = sys.argv[1], os.path.expanduser(sys.argv[2])
    idx = json.load(open(os.path.join(work, 'allure', 'index.json')))
    summary = json.load(open(os.path.join(work, 'allure', 'summary.json')))
    cases = [json.load(open(f)) for f in glob(os.path.join(work, 'allure', 'tc', '*.json'))]

    start = datetime.datetime.fromtimestamp(summary['time']['start'] / 1000, datetime.timezone.utc)
    stop = datetime.datetime.fromtimestamp(summary['time']['stop'] / 1000, datetime.timezone.utc)
    git(repo, 'fetch', '-q', 'origin', 'master')
    sha = git(repo, 'log', 'origin/master', f'--before={start.isoformat()}', '-1', '--format=%H').stdout.strip()
    if not sha:
        sys.exit('Could not find the commit the run used. Check the repo path and that origin/master is fetched.')
    src = Source(repo, sha)

    tests = []
    for t in cases:
        labels = {}
        for lab in t.get('labels', []):
            labels.setdefault(lab['name'], lab['value'])
        key, stage = failing_stage(t)
        msg = stage.get('statusMessage') or t.get('statusMessage') or ''
        traces = (stage.get('statusTrace') or '') + '\n' + (t.get('statusTrace') or '')
        cid = re.match(r'(C\d+)', t['name'])
        cid = cid.group(1) if cid else t['uid'][:8]
        team = re.findall(TEAMS, t['name'], re.I)
        hist = (t.get('extra') or {}).get('history', {}).get('statistic') or {}
        pkg = labels.get('package', '')
        spec = 'cypress/e2e/' + pkg.replace('cypress.e2e.', '').rsplit('.cy.js', 1)[0].replace('.', '/') + '.cy.js' if pkg else ''

        locs = []
        for p, n in WEBPACK.findall(traces):
            item = dict(path=p, line=int(n), code=src.line(p, int(n)))
            if item['code'] and item not in locs:
                locs.append(item)
        e2e = [x for x in locs if '/e2e/' in x['path']]
        sup = [x for x in locs if '/support/' in x['path'] and 'stripes.js' not in x['path']]
        where = e2e[:1] + sup[:1]
        if not e2e and spec:
            first = msg.split('\n')[0]
            terms = [x for x in re.findall(r'"([^"]{4,80})"', first)
                     if not re.search(r'\d{3,}\.\d+|^[0-9a-f-]{36}$|^AT_|^at_|autotest|tag\d', x)]
            hits = []
            for term in terms[:2]:
                hits += src.grep(term, [spec]) or src.grep(term, [x for x in src.imports(spec) if '/fragments/' in x])[:2]
            where += hits[:2]
            if not where:
                where = [dict(path=spec, line=None, code=None, guess=True)]

        tests.append(dict(
            uid=t['uid'], id=cid, name=re.sub(r'^C\d+\s*', '', t['name']), full_name=t['name'],
            team=team[0].lower() if team else 'untagged', status=t['status'],
            stage='setup (before)' if key == 'beforeStages' else 'test body',
            err=short_error(msg), msg=msg[:3000], step=(deepest_failed_step(stage) or [''])[-1],
            spec=spec.replace('cypress/e2e/', ''), suite=labels.get('suite'),
            hp=hist.get('passed'), ht=hist.get('total'), flaky=t.get('flaky'),
            start=datetime.datetime.fromtimestamp(t['time']['start'] / 1000, datetime.timezone.utc).strftime('%H:%M'),
            cluster=cluster_key(msg), where=where))

    st = summary['statistic']
    meta = dict(allure=idx['allure'], sha=sha, start=start.strftime('%b %d, %Y %H:%M'),
                stop=stop.strftime('%b %d, %Y %H:%M') + ' UTC', total=st['total'], passed=st['passed'],
                failed=st['failed'], broken=st['broken'], skipped=st['skipped'],
                setup=sum(1 for t in tests if t['stage'].startswith('setup')))
    m = re.search(r'/job/([^/]+)/job/([^/]+)/(\d+)/allure', idx['allure'])
    if m:
        meta.update(job=f'{m.group(1)} · {m.group(2)}', build=m.group(3))
    json.dump(tests, open(os.path.join(work, 'tests.json'), 'w'), indent=1)
    json.dump(meta, open(os.path.join(work, 'meta.json'), 'w'), indent=1)

    clusters = collections.defaultdict(list)
    for t in tests:
        clusters[t['cluster']].append(t)
    with open(os.path.join(work, 'dump.md'), 'w') as f:
        f.write(f"# {len(tests)} failed/broken tests, {len(clusters)} clusters, commit {sha[:7]}, run start {meta['start']} UTC\n\n")
        for k, ts in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
            f.write(f"## [{len(ts)}] {k}\n")
            ordered = sorted(ts, key=lambda x: x['start'])
            detail, rest = (ordered, []) if len(ordered) <= 5 else (ordered[:3], ordered[3:])
            for t in detail:
                w = ' | '.join(f"{x['path'].replace('cypress/', '')}:{x['line']} {x['code'][:90]}" for x in t['where'] if x.get('line'))
                f.write(f"- {t['id']} {t['status'][0].upper()}/{'before' if t['stage'].startswith('setup') else 'test'} {t['team']} {t['start']} h={t['hp']}/{t['ht']} {t['name'][:70]}\n"
                        f"  err: {t['err'][:200]}\n")
                if t['step'] and not t['step'].startswith(('do (', 'assert', 'then')):
                    f.write(f"  step: {t['step'][:100]}\n")
                f.write(f"  at: {w[:240]}\n" if w else f"  spec: {t['spec']}\n")
            if rest:
                f.write(f"- +{len(rest)} more with the same error (id team time hist): "
                        + ', '.join(f"{t['id']} {t['team']} {t['start']} {t['hp']}/{t['ht']}" for t in rest) + '\n')
            f.write('\n')
    print(f"tests={len(tests)} clusters={len(clusters)} commit={sha[:7]} → {work}/dump.md")


if __name__ == '__main__':
    main()
