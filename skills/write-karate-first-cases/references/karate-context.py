#!/usr/bin/env python3
"""Context helper for Karate tests in folio-org/folio-integration-tests.

Run from the root of a local clone. Read-only: it never changes files.

  karate-context.py reusables  <project>                     reusable catalog: key, file, parameters
  karate-context.py coverage   <project> [--endpoint "PUT orders/composite-orders"] [--field approvalDate]
                               [--code error-code] [--reusable openOrder] [--status 422] [<text> ...]
                               scenarios ranked by how many criteria they meet, with evidence;
                               reusable calls are expanded, so a scenario that calls openOrder counts as
                               a PUT on orders/composite-orders even if the request is not in the feature
  karate-context.py scenario   <feature-file> [<line>]        structured view of scenarios: requests, reusables, assertions
  karate-context.py check-calls <project> <feature-file>      reusable calls vs their documented parameters (used by validate-feature.sh)
  karate-context.py endpoints  <project> [<filter>]           endpoint -> features index
  karate-context.py exemplars  <folder> [-n N]                most recent features that follow the current standards
  karate-context.py registered <project> <feature-name>       runners and root features that register a feature
  karate-context.py profile    <project>                     team profile: teams, runners, registration style, root features, rules files
  karate-context.py appctx     <area>[,<area>]|all           freshness of write-testrail-cases context files (read-only)

Several projects: pass them comma-separated (`acquisitions,mod-inventory`) to coverage and endpoints.
<project> is the Maven module folder, for example `acquisitions`.
The scenario index is cached per git HEAD in $XDG_CACHE_HOME (or ~/.cache)/karate-context/; the repository is never written.
<folder> is a features folder, for example `acquisitions/src/main/resources/thunderjet/mod-orders/features`.
"""
import os
import re
import subprocess
import sys
from collections import defaultdict

RES = "src/main/resources"


def res(project):
    """Resource root holding the project's features: src/main/resources (most projects) or src/test/resources (e.g. mod-data-export)."""
    main = os.path.join(project, "src/main/resources")
    if os.path.isdir(main) and any(f.endswith(".feature") for _, _, fs in os.walk(main) for f in fs):
        return "src/main/resources"
    test = os.path.join(project, "src/test/resources")
    return "src/test/resources" if os.path.isdir(test) else "src/main/resources"


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def features(root):
    for d, _, files in os.walk(root):
        for f in files:
            if f.endswith(".feature"):
                yield os.path.join(d, f)


def parse_feature(path):
    """Return list of scenarios: {name, line, tags, body}."""
    lines = read(path).splitlines()
    scenarios, tags, cur = [], [], None
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("@"):
            tags.extend(s.split())
            continue
        m = re.match(r"(Scenario(?: Outline)?):\s*(.*)", s)
        if m:
            cur = {"name": m.group(2), "line": i, "tags": tags, "body": []}
            scenarios.append(cur)
            tags = []
            continue
        if cur is not None:
            cur["body"].append(line)
        if s and not s.startswith("#"):
            tags = [] if not s.startswith("@") else tags
    return scenarios


# ---------------------------------------------------------------- structured scenario index

def norm_path(expr):
    """`'orders/composite-orders', orderId` -> orders/composite-orders/{}"""
    parts = []
    for tok in re.findall(r"'[^']*'|\"[^\"]*\"|[^,]+", expr):
        tok = tok.strip()
        if not tok:
            continue
        if tok[0] in "'\"":
            parts += [p for p in tok[1:-1].strip("/").split("/") if p]
        else:
            parts.append("{}")
    return "/".join(parts)


def analyse_body(lines):
    """Requests, reusable calls, asserted fields, status codes and error codes of a scenario body."""
    requests, calls, fields, statuses, codes = [], [], set(), set(), set()
    reads = []  # raw argument of call read(...), resolved later against the feature's definitions
    path = None
    for raw in lines:
        l = raw.strip()
        if not l or l.startswith("#"):
            continue
        m = re.match(r"(?:Given|And|\*)\s+path\s+(.*)", l)
        if m:
            path = norm_path(m.group(1))
            continue
        m = re.match(r"(?:When|And|\*)\s+method\s+(\w+)", l)
        if m:
            requests.append(f"{m.group(1).upper()} {path or '?'}")
            path = None
            continue
        m = re.search(r"(?:^|[\s=])call(?:once)?\s+([A-Za-z_][A-Za-z0-9_]*)", l)
        if m and m.group(1) not in ("read", "uuid", "random_string") and not re.match(r"uuid\d+$", m.group(1)):
            calls.append(m.group(1))
        m = re.search(r"call(?:once)?\s+read\(\s*(?:\w+\s*\+\s*)?['\"](?:classpath:)?([^'\"]+)['\"]", l)
        if m:
            calls.append("read:" + os.path.basename(m.group(1)))
        m = re.search(r"call(?:once)?\s+read\(([^)]*)\)", l)
        if m:
            reads.append(m.group(1).strip())
        m = re.match(r"(?:Then|And|\*)\s+status\s+(\d+)", l)
        if m:
            statuses.add(m.group(1))
        if re.match(r"(?:Then|And|\*)\s+match\b", l) or "retry until" in l:
            # fields of the response or of any captured variable: $.a.b, response.a, invoice.poNumbers[0]
            for f in re.findall(r"(?:\$|\b[A-Za-z_][A-Za-z0-9_]*)((?:\.[A-Za-z_][A-Za-z0-9_]*|\[[^\]]*\])+)", l.split("==")[0] if "==" in l else l):
                fields.update(x for x in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", re.sub(r"\[[^\]]*\]", "", f)))
            if "errors" in l or "code" in l:
                codes.update(re.findall(r"['\"]([a-z][A-Za-z0-9]+(?:[A-Z][A-Za-z0-9]*)+|[a-z0-9]+(?:[-_][a-z0-9]+)+)['\"]", l))
    verify_calls = [c for c in calls if re.search(r"assert|verify|check|validate|expect", c, re.I)]
    return {"requests": requests, "calls": calls, "fields": sorted(fields), "statuses": sorted(statuses), "codes": sorted(codes),
            "verify_calls": verify_calls, "reads": reads}


def reusable_map(project):
    """karate-config key -> requests of the reusable feature (one level)."""
    out = {}
    config = os.path.join(project, res(project), "karate-config.js")
    if not os.path.exists(config):
        return out
    for key, ref in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:karate\.)?read\('classpath:([^']+)'\)", read(config), re.M):
        f = os.path.join(project, res(project), ref.split("@")[0])
        if os.path.exists(f):
            reqs = []
            for sc in parse_feature(f):
                reqs += analyse_body(sc["body"])["requests"]
            out[key] = sorted(set(reqs))
    return out


def feature_defs(text):
    """Variables a feature binds to other features: def x = read('classpath:a.feature') or def x = 'classpath:a.feature'."""
    defs = {}
    for name, ref in re.findall(r"def\s+([A-Za-z_]\w*)\s*=\s*(?:karate\.)?read\(\s*['\"](?:classpath:)?([^'\"]+\.feature[^'\"]*)['\"]\s*\)", text):
        defs[name] = ref
    for name, ref in re.findall(r"def\s+([A-Za-z_]\w*)\s*=\s*['\"](?:classpath:)?([^'\"]+\.feature)['\"]", text):
        defs.setdefault(name, ref)
    return defs


_project_defs = {}


def project_defs(project):
    """Feature paths bound to the same variable name everywhere in the project (karate-config.js and shared features).
    Used when a feature calls `read(utilFeature + '@Tag')` and utilFeature comes from a shared feature."""
    if project in _project_defs:
        return _project_defs[project]
    seen = defaultdict(set)
    files = list(features(os.path.join(project, res(project))))
    cfg = os.path.join(project, res(project), "karate-config.js")
    for f in files + ([cfg] if os.path.exists(cfg) else []):
        for k, v in feature_defs(read(f)).items():
            seen[k].add(v)
        for k, v in re.findall(r"^\s*([A-Za-z_]\w*)\s*:\s*['\"]classpath:([^'\"]+\.feature)['\"]", read(f), re.M):
            seen[k].add(v)
    _project_defs[project] = {k: next(iter(v)) for k, v in seen.items() if len(v) == 1}
    return _project_defs[project]


def resolve_read(expr, defs):
    """`'classpath:a/b.feature@Tag'` or `commonFeature + '@Tag'` -> 'a/b.feature@Tag' (or None when dynamic)."""
    m = re.match(r"^['\"](?:classpath:)?([^'\"]+)['\"]$", expr)
    if m:
        return m.group(1)
    m = re.match(r"^([A-Za-z_]\w*)\s*\+\s*['\"]([^'\"]*)['\"]$", expr)
    if m and m.group(1) in defs:
        return defs[m.group(1)] + m.group(2)
    if re.match(r"^[A-Za-z_]\w*$", expr) and expr in defs:
        return defs[expr]
    return None


def locate(project, ref):
    file_part = ref.split("@")[0]
    if os.path.isabs(file_part) or file_part.startswith("file:"):
        return None
    for base in (os.path.join(project, res(project)), os.path.join("common", RES), os.path.join("common-consortia", RES)):
        p = os.path.join(base, file_part)
        if file_part and os.path.isfile(p):
            return p
    return None


_expand_cache = {}


def expand_target(project, ref, reus, depth=0):
    """Requests made by a called feature (optionally one tagged scenario), following its own calls up to 3 levels."""
    key = (project, ref)
    if key in _expand_cache:
        return _expand_cache[key]
    path = locate(project, ref)
    out = set()
    if path and depth < 3:
        tag = "@" + ref.split("@", 1)[1] if "@" in ref else None
        text = read(path)
        defs = {**project_defs(project), **feature_defs(text)}
        for sc in parse_feature(path):
            if tag and tag not in sc["tags"]:
                continue
            a = analyse_body(sc["body"])
            out.update(a["requests"])
            for c in a["calls"]:
                out.update(reus.get(c, []))
                if c in defs:
                    out |= expand_target(project, defs[c], reus, depth + 1)
            for expr in a["reads"]:
                r = resolve_read(expr, defs)
                if r:
                    out |= expand_target(project, r, reus, depth + 1)
    _expand_cache[key] = out
    return out


def git_head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "nogit"
    except OSError:
        return "nogit"


def build_index(project):
    import json, hashlib
    cache_dir = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "karate-context")
    version = hashlib.sha1(open(__file__, "rb").read()).hexdigest()[:8]  # a new helper version rebuilds the index
    key = hashlib.sha1(f"{os.getcwd()}|{project}|{git_head()}|{version}".encode()).hexdigest()[:16]
    cache = os.path.join(cache_dir, key + ".json")
    dirty = subprocess.run(["git", "status", "--porcelain", "--", project], capture_output=True, text=True).stdout.strip()
    if os.path.exists(cache) and not dirty:
        return json.load(open(cache))
    reus = reusable_map(project)
    runners_ = runner_index(project)
    callers = callers_index(project)
    index = []
    for path in sorted(features(os.path.join(project, res(project)))):
        if "/reusable/" in path:
            continue
        name = os.path.basename(path)[:-8]
        defs = {**project_defs(project), **feature_defs(read(path))}
        for sc in parse_feature(path):
            a = analyse_body(sc["body"])
            implied = {r for c in a["calls"] for r in reus.get(c, [])}
            for c in a["calls"]:
                if c in defs:
                    implied |= expand_target(project, defs[c], reus)
            for expr in a["reads"]:
                ref = resolve_read(expr, defs)
                # expand helpers (tagged scenarios, reusable/util/global features); not whole test features called from root features
                if ref and ("@" in ref or not re.search(r"(^|/)features/[^@]+\.feature$", ref) or "/util/" in ref or "/reusable/" in ref):
                    implied |= expand_target(project, ref, reus)
            implied = sorted(implied - set(a["requests"]))
            index.append({
                "file": os.path.relpath(path), "line": sc["line"], "name": sc["name"],
                "ctags": [t for t in sc["tags"] if re.match(r"@C\d+$", t)],
                "runner": runners_.get(name, []), "roots": callers.get(name, []),
                "text": "\n".join(sc["body"]), **a, "implied": implied,
            })
    if not dirty:
        os.makedirs(cache_dir, exist_ok=True)
        json.dump(index, open(cache, "w"))
    return index


def match_endpoint(want, have):
    """`PUT orders/composite-orders` matches `PUT orders/composite-orders/{}`; method optional."""
    parts = want.split(None, 1)
    method, path = (parts[0].upper(), parts[1]) if len(parts) == 2 else (None, parts[0])
    path = path.strip("/")
    for h in have:
        hm, hp = h.split(" ", 1)
        if (method is None or method == hm) and (hp == path or hp.startswith(path + "/") or re.sub(r"\{\}", "", hp).strip("/") == path):
            return h
    return None


def cmd_coverage2(projects, args):
    crit = {"endpoint": [], "field": [], "code": [], "reusable": [], "status": [], "text": []}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--") and a[2:] in crit and i + 1 < len(args):
            crit[a[2:]].append(args[i + 1]); i += 2
        else:
            crit["text"].append(a); i += 1
    total = sum(len(v) for v in crit.values())
    if not total:
        print(__doc__); return
    results = []
    for project in projects.split(","):
        for sc in build_index(project):
            ev = []
            for e in crit["endpoint"]:
                h = match_endpoint(e, sc["requests"]) or match_endpoint(e, sc["implied"])
                if h:
                    ev.append(f"endpoint {h}" + ("" if h in sc["requests"] else " (via reusable)"))
            ev += [f"field {f}" for f in crit["field"] if f in sc["fields"]]
            ev += [f"asserted code {c}" for c in crit["code"] if c in sc["codes"] or c in sc["text"]]
            ev += [f"calls {r}" for r in crit["reusable"] if r in sc["calls"]]
            ev += [f"status {st}" for st in crit["status"] if st in sc["statuses"]]
            ev += [f"text '{t}'" for t in crit["text"] if t.lower() in (sc["text"] + sc["name"]).lower()]
            if ev:
                results.append((len(ev), sc, ev))
    results.sort(key=lambda r: -r[0])
    full = [r for r in results if r[0] == total]
    print(f"{len(full)} scenario(s) meet all {total} criteria; {len(results) - len(full)} meet some (top 15 shown)\n")
    for score, sc, ev in results[:15]:
        print(f"[{score}/{total}] {sc['file']}:{sc['line']}")
        print(f"  Scenario: {sc['name']}")
        print(f"  TestRail: {' '.join(sc['ctags']) or 'no @C tag'}   Runs from: {', '.join(sc['runner'] + sc['roots']) or 'NOT REGISTERED'}")
        print(f"  Evidence: {'; '.join(ev)}")
        verify = sc.get("verify_calls") or []
        print(f"  Asserts:  {', '.join(sc['fields'][:12]) or 'no field assertions'}" + (f"  status {','.join(sc['statuses'])}" if sc['statuses'] else "")
              + (f"  via {', '.join(sorted(set(verify)))}" if verify else ""))
    print("\nText and structure matching is a filter, not a verdict: open each hit and compare precondition, trigger and asserted outcome.")


def cmd_scenario(path, line=None):
    for sc in parse_feature(path):
        if line and sc["line"] != int(line):
            continue
        a = analyse_body(sc["body"])
        print(f"{path}:{sc['line']}  {sc['name']}  {' '.join(sc['tags'])}")
        for k in ("requests", "calls", "fields", "statuses", "codes"):
            print(f"  {k:9} {', '.join(a[k]) or '-'}")


def runners(project):
    """Yield (class name, text) for JUnit runner classes of a project."""
    for d, _, files in os.walk(os.path.join(project, "src/test/java")):
        for f in files:
            if f.endswith(".java"):
                yield f[:-5], read(os.path.join(d, f))


def feature_names_in_runner(text):
    """Names a runner registers: FEATURES array entries and runFeatureTest(...) arguments."""
    names = []
    m = re.search(r"String\[\]\s+FEATURES\s*=\s*\{(.*?)\};", text, re.S)
    if m:
        names += re.findall(r'"([^"]+)"', m.group(1))
    names += re.findall(r'runFeatureTest\(\s*"([^"]+)"', text)
    # pre-PR #2426 style: enum Feature { FEATURE_1("name", true), ... } + runFeatureTest(Feature.FEATURE_1.getFileName())
    names += re.findall(r'FEATURE_\d+\(\s*"([^"]+)"', text)
    # one @Test per feature with the Karate runner API: feature("classpath:.../x.feature").run() or feature(PATH + "x.feature")
    names += [os.path.basename(n) for n in re.findall(r'feature\(\s*(?:[A-Z_]+\s*\+\s*)?"(?:classpath:)?([^"]+?)\.feature"', text)]
    # setup/teardown or tests run directly: runFeature(TEST_BASE_PATH + "x.feature") / runFeature("classpath:.../x.feature")
    names += [os.path.basename(n) for n in re.findall(r'runFeature\(\s*(?:[A-Z_]+\s*\+\s*)?"(?:classpath:)?([^"]+?)\.feature"', text)]
    return [os.path.basename(n)[:-8] if n.endswith(".feature") else os.path.basename(n) for n in names]


def runner_index(project):
    """feature name -> [runner class]."""
    idx = defaultdict(list)
    for cls, text in runners(project):
        for name in feature_names_in_runner(text):
            idx[name].append(cls)
    return idx


def callers_index(project):
    """feature name -> [features that call it with read('...name.feature')] (root features)."""
    idx = defaultdict(list)
    for path in features(os.path.join(project, res(project))):
        for ref in re.findall(r"read\(\s*(?:[A-Za-z_]\w*\s*\+\s*)?['\"](?:classpath:)?([^'\"@]+\.feature)", read(path)):
            name = os.path.basename(ref)[:-8]
            if not path.endswith(f"/{name}.feature"):
                idx[name].append(os.path.relpath(path))
    return idx


def parse_params_header(text):
    """Text of a `# parameters:` header; continuation lines only while the previous line ends with a comma."""
    lines = text.splitlines()
    for i, l in enumerate(lines):
        m = re.match(r"\s*#\s*parameters?:\s*(.*)", l, re.I)
        if not m:
            continue
        out = [m.group(1).strip()]
        j = i + 1
        while out[-1].endswith(",") and j < len(lines) and re.match(r"\s*#", lines[j]):
            out.append(re.sub(r"^\s*#\s*", "", lines[j]).strip())
            j += 1
        text_ = " ".join(out).rstrip(",")
        parts = [x.strip() for x in text_.split(",") if x.strip()]
        # only a plain list of identifiers is machine-readable; prose ("same as createInvoiceLine but ...") is skipped
        if parts and all(re.fullmatch(r"[A-Za-z_]\w*\??", x) for x in parts):
            return text_
        return None
    return None


def reusable_params(project):
    """key -> (required set, optional set) for reusables with a `# parameters:` header."""
    out = {}
    config = os.path.join(project, res(project), "karate-config.js")
    if not os.path.exists(config):
        return out
    for key, ref in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:karate\.)?read\('classpath:([^']+)'\)", read(config), re.M):
        path = os.path.join(project, res(project), ref.split("@")[0])
        if not os.path.exists(path):
            continue
        header = parse_params_header(read(path))
        if not header:
            continue
        names = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)(\??)", header)
        # optional = marked with ? in the header, or read with a default in the code (karate.get('x', default))
        defaulted = set(re.findall(r"karate\.get\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*,", read(path)))
        req = {n for n, q in names if not q and n not in defaulted}
        opt = {n for n, q in names if q or n in defaulted} | defaulted
        if req or opt:
            out[key] = (req, opt)
    return out


def object_keys(lit):
    """Top-level keys of a Karate/JS object literal `{ a: 1, 'b': x, c: { d: 1 } }`."""
    depth, keys, token = 0, [], ""
    for ch in lit.strip()[1:-1] + ",":
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == "," and depth == 0:
            m = re.match(r"\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?\s*:", token)
            if m:
                keys.append(m.group(1))
            token = ""
        else:
            token += ch
    return keys


def cmd_check_calls(project, feature):
    params = reusable_params(project)
    errors = 0
    text = read(feature)
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("#"):
            continue
        m = re.search(r"(?:^|[\s=])call(?:once)?\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\{.*\})?\s*$", line)
        if not m or m.group(1) not in params:
            continue
        req, opt = params[m.group(1)]
        if not m.group(2):
            if req and not re.search(r"call(?:once)?\s+\w+\s+\w+", line):
                defined_all = set(re.findall(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", text))
                if req - defined_all:
                    print(f"WARN:  line {n}: {m.group(1)} called without arguments; documented parameters: {', '.join(sorted(req))}")
            continue
        keys = set(object_keys(m.group(2)))
        missing = req - keys
        unknown = keys - req - opt
        defined = set(re.findall(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", text))
        hard = {x for x in missing if x not in defined}
        soft = missing - hard
        if hard:
            # Karate logs a failed embedded expression and continues, so this rarely breaks the run: warning, not error
            print(f"WARN:  line {n}: {m.group(1)} is called without documented parameter(s) {', '.join(sorted(hard))}; the reusable may send an empty or literal value")
        if soft:
            print(f"WARN:  line {n}: {m.group(1)} gets {', '.join(sorted(soft))} only from the caller's variables; pass them explicitly")
        if unknown:
            print(f"WARN:  line {n}: {m.group(1)} gets undocumented parameter(s) {', '.join(sorted(unknown))}; the reusable may ignore them")
    if not errors:
        print("ok:   reusable calls match their documented parameters")
    return 1 if errors else 0


def cmd_reusables(project):
    config = os.path.join(project, res(project), "karate-config.js")
    text = read(config)
    rows = []
    for key, ref in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:karate\.)?read\('classpath:([^']+)'\)", text, re.M):
        file_part = ref.split("@")[0]
        path = os.path.join(project, res(project), file_part)
        params = ""
        if os.path.exists(path):
            header = parse_params_header(read(path))
            if header:
                params = header
            else:
                body = read(path)
                optional = sorted(set(re.findall(r"karate\.get\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]", body)))
                args = sorted(set(re.findall(r"__arg\.([A-Za-z_][A-Za-z0-9_]*)", body)) - set(optional))
                found = args + [o + "?" for o in optional]
                if found:
                    params = "inferred from code: " + ", ".join(found)
        rows.append((key, ref, params or "(no # parameters header: read the file)"))
    for helper in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*function", text, re.M):
        rows.append((helper, "(function in karate-config.js)", ""))
    print(f"{len(rows)} keys in {config}\n")
    for key, ref, params in rows:
        print(f"{key}\n  file:   {ref}\n  params: {params}" if params else f"{key}\n  file:   {ref}")


def cmd_coverage(project, terms):
    root = os.path.join(project, res(project))
    runners = runner_index(project)
    hits = 0
    for path in sorted(features(root)):
        if "/reusable/" in path:
            continue
        for sc in parse_feature(path):
            body = "\n".join(sc["body"])
            if all(t.lower() in body.lower() or t.lower() in sc["name"].lower() for t in terms):
                hits += 1
                name = os.path.basename(path)[:-8]
                ctags = [t for t in sc["tags"] if re.match(r"@C\d+$", t)]
                matched = [l.strip() for l in sc["body"] if any(t.lower() in l.lower() for t in terms)][:4]
                print(f"{os.path.relpath(path)}:{sc['line']}")
                print(f"  Scenario: {sc['name']}")
                print(f"  TestRail: {' '.join(ctags) or 'no @C tag'}   Runner: {', '.join(runners.get(name, [])) or 'not in a FEATURES array'}")
                for l in matched:
                    print(f"    | {l[:140]}")
    print(f"\n{hits} scenario(s) use all of: {', '.join(terms)}")


def cmd_endpoints(project, filt):
    idx = defaultdict(set)
    for sc in build_index(project):
        for r in set(sc["requests"]) | set(sc["implied"]):
            if not filt or filt in r:
                idx[r].add(os.path.basename(sc["file"])[:-8])
    for p in sorted(idx, key=lambda k: -len(idx[k])):
        names = sorted(idx[p])
        print(f"{p}  ({len(names)} features)\n  " + ", ".join(names[:15]) + (" ..." if len(names) > 15 else ""))

def compliance(path):
    text = read(path)
    checks = {
        "no @parallel=false": "@parallel=false" not in text,
        "no callonce uuid": not re.search(r"callonce uuid\d*", text),
        "no print in scenarios": not re.search(r"^\s+\* print '", text, re.M),
        "@C tags": bool(re.search(r"^\s*@C\d+\s*$", text, re.M)),
        "# N. comments": bool(re.search(r"^\s*# \d+\. ", text, re.M)),
        "def v = call": "def v = call" in text,
        "no Scenario Outline": "Scenario Outline" not in text,
    }
    return sum(checks.values()), checks


def cmd_exemplars(folder, n):
    out = subprocess.run(["git", "log", "--name-only", "--format=", "--diff-filter=AM", "--", folder],
                         capture_output=True, text=True).stdout.split()
    seen, ranked = set(), []
    for f in out:
        if f.endswith(".feature") and f not in seen and os.path.exists(f) and "/reusable/" not in f:
            seen.add(f)
            score, checks = compliance(f)
            ranked.append((score, len(ranked), f, checks))
        if len(ranked) >= 40:
            break
    ranked.sort(key=lambda r: (-r[0], r[1]))
    for score, _, f, checks in ranked[:n]:
        missing = [k for k, v in checks.items() if not v]
        print(f"{f}\n  score {score}/{len(checks)}" + (f"  missing: {', '.join(missing)}" if missing else ""))


def cmd_registered(project, name):
    runner_list = runner_index(project).get(name, [])
    roots = callers_index(project).get(name, [])
    print(f"runners:          {', '.join(runner_list) or 'none'}")
    print(f"called by (roots): {', '.join(roots) or 'none'}")
    if len(runner_list) > 1:
        print("WARNING: registered in more than one runner; the feature runs twice")
    if not runner_list and not roots:
        print("WARNING: not registered; nothing runs this feature")


def cmd_profile(project):
    print(f"Project: {project}")
    rules = []
    for d in (os.path.join(project, "ai"), os.path.join(project, "docs")):
        for root, _, files in os.walk(d):
            rules += [os.path.join(root, f) for f in files if f.endswith(".md")]
    print("Rules files:      " + (", ".join(rules) or f"none (no {project}/ai/): derive conventions from exemplars"))
    config = os.path.join(project, res(project), "karate-config.js")
    if os.path.exists(config):
        keys = re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:karate\.)?read\(", read(config), re.M)
        print(f"karate-config.js: {config} ({len(keys)} reusable keys)")
    else:
        print("karate-config.js: none in project; check common/ and the runner's TestModuleConfiguration")
    reus = sorted({os.path.relpath(d) for d, _, fs in os.walk(os.path.join(project, res(project))) if d.endswith("reusable") or d.endswith("global")})
    print("Reusable folders: " + (", ".join(reus) or "none"))
    inits = sorted(os.path.relpath(p) for p in features(os.path.join(project, res(project))) if re.search(r"/(init|root)[^/]*\.feature$", p))
    print("Init/root features: " + (", ".join(inits) or "none"))
    print("\nRunners:")
    for cls, text in sorted(runners(project)):
        team = re.search(r'@FolioTest\(team\s*=\s*"([^"]+)",\s*module\s*=\s*"([^"]+)"', text)
        if not team:
            continue
        base = re.search(r'TEST_BASE_PATH\s*=\s*"?([^";]+)', text)
        names = feature_names_in_runner(text)
        if "String[] FEATURES" in text:
            style = f"FEATURES array ({len(names)})"
        elif re.search(r'feature\(\s*(?:[A-Z_]+\s*\+\s*)?"', text) and names:
            style = f"one @Test per feature via feature(...).run() ({len(names)})"
        elif re.search(r"enum Feature\b", text):
            style = f"enum Feature + one @Test per feature ({len(names)}; pre-PR #2426 style)"
        elif re.search(r'runFeatureTest\(\s*"root', text):
            style = "root feature(s): " + ", ".join(n for n in names if n.startswith("root"))
        elif names:
            style = f"one @Test per feature ({len(names)})"
        else:
            style = "custom (read the class)"
        shared = re.search(r"(Shared\w+Tenant)", text)
        print(f"  {cls}: team={team.group(1) if team else '?'} module={team.group(2) if team else '?'}")
        print(f"    base={base.group(1).strip() if base else '?'}  registration={style}" + (f"  tenant={shared.group(1)}" if shared else ""))


def cmd_appctx(areas, today=None):
    """Freshness of write-testrail-cases context files (read-only).
    Rule from write-testrail-cases references/area-map.md -> Freshness: stale when the newer of Built and
    Delta-refreshed is older than 90 days, or the story Fix Version is newer than the header Release."""
    import datetime
    here = os.path.dirname(os.path.abspath(__file__))
    ctx = os.path.normpath(os.path.join(here, "..", "..", "write-testrail-cases", "references", "context"))
    today = today or datetime.date.today()
    names = sorted(f[:-3] for f in os.listdir(ctx) if f.endswith(".md")) if os.path.isdir(ctx) else []
    wanted = names if areas in ("all", "*") else [a.strip() for a in areas.split(",")]
    for area in wanted:
        path = os.path.join(ctx, area + ".md")
        if not os.path.isfile(path):
            print(f"{area}: MISSING - no context file; follow the write-testrail-cases missing-context path")
            continue
        head = "".join(open(path, encoding="utf-8", errors="replace").readlines()[:6])
        # content dates only: "Built: <date>" and "<...>refreshed: <date>"; header normalization is not a refresh
        header = head.split("\n> Generated")[0]
        dates = [datetime.date.fromisoformat(d) for d in
                 re.findall(r"(?:Built|[Rr]efresh(?:ed)?|generated_on)\s*:?\s*(?:on\s*)?(20\d\d-\d\d-\d\d)", header)]
        release = re.search(r"Release:\s*([^·\n]+)", head)
        release = release.group(1).strip() if release else "not recorded"
        if "DRAFT" in head.upper():
            state = "DRAFT"
        elif not dates:
            state = "NO DATE"
        else:
            age = (today - max(dates)).days
            state = f"{'STALE' if age > 90 else 'fresh'} (last update {max(dates)}, {age} days)"
        note = "" if release != "not recorded" else " (compare the story Fix Version manually)"
        print(f"{area}: {state}; release: {release}{note}")
    if not names:
        print(f"context folder not found: {ctx}")


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "reusables":
        cmd_reusables(argv[2])
    elif cmd == "coverage" and len(argv) >= 4:
        cmd_coverage2(argv[2], argv[3:])
    elif cmd == "check-calls" and len(argv) >= 4:
        return cmd_check_calls(argv[2], argv[3])
    elif cmd == "scenario":
        cmd_scenario(argv[2], argv[3] if len(argv) > 3 else None)
    elif cmd == "endpoints":
        for project in argv[2].split(","):
            cmd_endpoints(project, argv[3] if len(argv) > 3 else "")
    elif cmd == "exemplars":
        n = int(argv[argv.index("-n") + 1]) if "-n" in argv else 3
        cmd_exemplars(argv[2], n)
    elif cmd == "registered" and len(argv) >= 4:
        cmd_registered(argv[2], argv[3])
    elif cmd == "profile":
        cmd_profile(argv[2])
    elif cmd == "appctx":
        cmd_appctx(argv[2])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
