#!/usr/bin/env python3
"""Context helper for Karate tests in folio-org/folio-integration-tests.

Run from the root of a local clone. Read-only: it never changes files.

  karate-context.py reusables  <project>                     reusable catalog: key, file, parameters
  karate-context.py coverage   <project> <term> [<term> ...]  scenarios that use ALL terms (endpoint, field, error code...)
  karate-context.py endpoints  <project> [<filter>]           endpoint -> features index
  karate-context.py exemplars  <folder> [-n N]                most recent features that follow the current standards
  karate-context.py registered <project> <feature-name>       runners and root features that register a feature

<project> is the Maven module folder, for example `acquisitions`.
<folder> is a features folder, for example `acquisitions/src/main/resources/thunderjet/mod-orders/features`.
"""
import os
import re
import subprocess
import sys
from collections import defaultdict

RES = "src/main/resources"


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


def runner_index(project):
    """feature name -> [runner class] from FEATURES arrays in src/test/java."""
    idx = defaultdict(list)
    for d, _, files in os.walk(os.path.join(project, "src/test/java")):
        for f in files:
            if not f.endswith(".java"):
                continue
            text = read(os.path.join(d, f))
            m = re.search(r"String\[\]\s+FEATURES\s*=\s*\{(.*?)\};", text, re.S)
            if not m:
                continue
            for name in re.findall(r'"([^"]+)"', m.group(1)):
                idx[name].append(f[:-5])
    return idx


def cmd_reusables(project):
    config = os.path.join(project, RES, "karate-config.js")
    text = read(config)
    rows = []
    for key, ref in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:karate\.)?read\('classpath:([^']+)'\)", text, re.M):
        file_part = ref.split("@")[0]
        path = os.path.join(project, RES, file_part)
        params = ""
        if os.path.exists(path):
            header = re.findall(r"#\s*parameters?:\s*(.*(?:\n\s*#\s+(?!\d+\.).*)*)", read(path), re.I)
            if header:
                params = re.sub(r"\s*\n\s*#\s*", " ", header[0]).strip()
            else:
                body = read(path)
                optional = sorted(set(re.findall(r"karate\.get\('([A-Za-z_][A-Za-z0-9_]*)'", body)))
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
    root = os.path.join(project, RES)
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
    root = os.path.join(project, RES)
    idx = defaultdict(set)
    for path in features(root):
        if "/reusable/" in path:
            continue
        for p in re.findall(r"^\s*Given path\s+'([^']+)'", read(path), re.M):
            if not filt or filt in p:
                idx[p].add(os.path.basename(path)[:-8])
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
    runners = runner_index(project).get(name, [])
    roots = []
    for path in features(os.path.join(project, RES)):
        if re.search(rf"features/{re.escape(name)}\.feature", read(path)) and not path.endswith(f"/{name}.feature"):
            roots.append(os.path.relpath(path))
    print(f"runners:       {', '.join(runners) or 'none'}")
    print(f"root features: {', '.join(roots) or 'none'}")
    if len(runners) > 1:
        print("WARNING: registered in more than one runner; the feature runs twice")


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "reusables":
        cmd_reusables(argv[2])
    elif cmd == "coverage" and len(argv) >= 4:
        cmd_coverage(argv[2], argv[3:])
    elif cmd == "endpoints":
        cmd_endpoints(argv[2], argv[3] if len(argv) > 3 else "")
    elif cmd == "exemplars":
        n = int(argv[argv.index("-n") + 1]) if "-n" in argv else 3
        cmd_exemplars(argv[2], n)
    elif cmd == "registered" and len(argv) >= 4:
        cmd_registered(argv[2], argv[3])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
