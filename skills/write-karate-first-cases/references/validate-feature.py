#!/usr/bin/env python3
"""Static and semantic validation of a Karate feature in folio-org/folio-integration-tests (any team).

Usage (from the root of a local clone):
  validate-feature.py <feature> [--runner <Runner.java>] [--root <root.feature>] [--changed-only] [--base origin/master]

  --runner        runner class that must register the feature (omit when the project registers through root features)
  --root          root feature that must call the feature (omit when the project registers through runners only)
  --changed-only  apply per-scenario checks only to scenarios added or changed against --base (use when
                  extending an existing feature: old scenarios are not judged by new rules)

Levels:
  ERROR  breaks execution, traceability or parallel safety; must be fixed (exit code 1)
  WARN   likely problem or deviation from the Karate Coding Standards; fix or explain in the PR
  INFO   recommendation; team-specific style where the team has not made it a rule

Team rules apply as ERROR only when the project's rules files (<project>/ai/*.md) state them.
"""
import argparse
import os
import re
import subprocess
import sys

import importlib.util

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("karate_context", os.path.join(HERE, "karate-context.py"))
kc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kc)

RES = "src/main/resources"
results = {"ERROR": [], "WARN": [], "INFO": []}


def report(level, msg):
    results[level].append(msg)


def team_rules_text(project):
    text = ""
    d = os.path.join(project, "ai")
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith(".md"):
                text += open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
    return text


def changed_lines(feature, base):
    """Line numbers added/changed in the working tree compared with base; None if git is unavailable."""
    try:
        out = subprocess.run(["git", "diff", "-U0", base, "--", feature], capture_output=True, text=True).stdout
    except OSError:
        return None
    if not out:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", feature], capture_output=True).returncode == 0
        return set() if tracked else None  # untracked new file: everything is new
    lines = set()
    for a, b in re.findall(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", out, re.M):
        start, count = int(a), int(b or 1)
        lines.update(range(start, start + count))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--runner")
    ap.add_argument("--root")
    ap.add_argument("--changed-only", action="store_true")
    ap.add_argument("--base", default="origin/master")
    a = ap.parse_args()

    feature = a.feature
    project = feature.split("/src/")[0]
    RES = kc.res(project)
    name = os.path.basename(feature)[:-8]
    text = open(feature, encoding="utf-8").read()
    lines = text.splitlines()
    rules = team_rules_text(project)
    has_rules = bool(rules)

    def team(rule_regex, msg, default="INFO"):
        """ERROR when the team's rules files state the rule, otherwise `default`."""
        if has_rules and re.search(rule_regex, rules, re.I | re.S):
            report("ERROR", msg + " (team rule)")
        else:
            report(default, msg)

    # ---- syntax
    try:
        from gherkin.parser import Parser
        Parser().parse(text)
    except ImportError:
        report("WARN", "Gherkin not checked: pip install gherkin-official")
    except Exception as e:  # noqa: BLE001
        report("ERROR", f"Gherkin does not parse: {str(e).splitlines()[0]}")

    scenarios = kc.parse_feature(feature)
    scope = None
    if a.changed_only:
        cl = changed_lines(feature, a.base)
        if cl is not None:
            ends = [s["line"] for s in scenarios[1:]] + [len(lines) + 1]
            scope = {s["name"] for s, end in zip(scenarios, ends) if cl & set(range(s["line"] - 3, end))}
    judged = [s for s in scenarios if scope is None or s["name"] in scope]
    report("INFO", f"{len(scenarios)} scenario(s), {len(judged)} judged" + (" (changed only)" if scope is not None else ""))

    # ---- feature-level rules
    header = "\n".join(lines[: next((i for i, l in enumerate(lines) if l.startswith("Feature:")), 0)])
    if "@parallel=false" in text:
        team(r"parallel=false", "@parallel=false: the Karate Coding Standards ask for scenarios that run in parallel; if the team serialises on purpose, say why in the PR", "WARN")
    if re.search(r"callonce\s+uuid\d*", text):
        report("ERROR", "callonce uuid: IDs shared by all scenarios break parallel runs; use 'call uuid' inside each scenario")
    if re.search(r"^\s*\*\s*def\s+\w+\s*=\s*call\s+uuid", "\n".join(l for l in text.split("Scenario")[0].splitlines()), re.M):
        report("WARN", "IDs generated in Background are shared by every scenario; generate them inside each scenario unless the data is read-only")
    if len(name) + 8 > 80:
        team(r"80", f"file name has {len(name) + 8} characters (> 80 breaks Karate reports)", "WARN")
    if not re.match(r"#\s*For\s+[A-Z][A-Z0-9]+-\d+", lines[0] if lines else ""):
        report("WARN", "first line should be '# For <JIRA-KEY>, <TestRail case URL>' for traceability")
    for ref in re.findall(r"read\('classpath:([^']+/reusable/[^']+\.feature)", text):
        if ref in open(os.path.join(project, RES, "karate-config.js"), encoding="utf-8").read() if os.path.exists(os.path.join(project, RES, "karate-config.js")) else False:
            report("WARN", f"{ref} is already loaded in karate-config.js; call it by its key")
    if re.search(r"call\s+[A-Za-z_]+\s*\{[^}]*:\s*#\(", text):
        report("WARN", "unquoted #(...) in call arguments; write '#(...)' (Karate Coding Standards)")
    if re.search(r"call\s+pause\b", text):
        report("WARN", "call pause: poll the expected state with 'retry until' when there is one")
    for lit in sorted(set(re.findall(r"['\"]([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})['\"]", text))):
        if lit not in header:
            report("WARN", f"hard-coded UUID {lit}: generate with 'call uuid' unless it is reference data of the tenant")
    for m in re.finditer(r"code:\s*['\"]([A-Z]{2,}[A-Z0-9]*\d{2,})['\"]", text):
        report("WARN", f"hard-coded code '{m.group(1)}': codes must be unique across parallel scenarios; build them from 'call random_string'")

    # ---- reusable keys and parameters
    config = os.path.join(project, RES, "karate-config.js")
    config_text = open(config, encoding="utf-8").read() if os.path.exists(config) else ""
    repo_root = os.path.dirname(project) or "."
    step_lines = [re.sub(r"'[^']*'|\"[^\"]*\"", "''", l) for l in lines if re.match(r"\s*(\*|Given|When|Then|And|But)\s", l)]
    dyn_prefixes = set(re.findall(r"karate\.set\(\s*['\"]([A-Za-z_]+)['\"]\s*\+", config_text))
    for key in sorted(set(re.findall(r"(?:^|[\s=])call(?:once)?\s+([A-Za-z_][A-Za-z0-9_]*)", "\n".join(step_lines)))):
        if key in ("read", "login") or re.match(r"uuid\d*$", key):
            continue
        if any(re.fullmatch(re.escape(p) + r"\d+", key) for p in dyn_prefixes):
            continue
        if re.search(rf"^\s*{key}\s*:", config_text, re.M) or re.search(rf"def\s+{key}\s*=", text):
            continue
        found = subprocess.run(["grep", "-rlE", rf"def {key}\s*=", os.path.join(project, RES), os.path.join(repo_root, "common", "src/main/resources")],
                               capture_output=True, text=True).stdout.strip()
        if not found:
            report("ERROR", f"'{key}' is called but not defined (karate-config.js, the feature, or a global/util feature)")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        kc.cmd_check_calls(project, feature)
    for l in buf.getvalue().splitlines():
        if l.startswith("ERROR:"):
            report("ERROR", l[6:].strip())
        elif l.startswith("WARN:"):
            report("WARN", l[5:].strip())

    # ---- per-scenario rules
    seen_c = {}
    for s in judged:
        body = s["body"]
        code = [l.strip() for l in body if l.strip() and not l.strip().startswith("#")]
        ctags = [t for t in s["tags"] if re.match(r"@C\d+$", t)]
        label = f"'{s['name'][:70]}'"
        if len(ctags) != 1:
            report("ERROR", f"{label}: {len(ctags)} @C tags; exactly one links the scenario to its TestRail case")
        for t in ctags:
            if t in seen_c:
                report("ERROR", f"{label}: {t} also used by '{seen_c[t][:60]}'")
            seen_c[t] = s["name"]
            if f"cases/view/{t[2:]}" not in header:
                report("WARN", f"{label}: {t} not linked in the header comments (skill convention for traceability)")
        if not any(t in s["tags"] for t in ("@Positive", "@Negative")):
            report("INFO", f"{label}: no @Positive / @Negative tag")
        if lines[s["line"] - 1].strip().startswith("Scenario Outline"):
            report("WARN", f"{label}: Scenario Outline; prepare data with a Karate table and one reusable call")
        nums = [int(m.group(1)) for l in body for m in [re.match(r"\s*# (\d+)\. ", l)] if m]
        if nums and nums != list(range(1, len(nums) + 1)):
            # the 1..N rule exists for TestRail traceability; scenarios without a case keep their own numbering
            report("ERROR" if ctags else "INFO", f"{label}: step comments {nums} are not 1..N" + ("; they must map to TestRail steps" if ctags else ""))
        if any(re.match(r"\*\s*print\s+['\"]", l) for l in code):
            team(r"NEVER add `\* print", f"{label}: '* print' step markers; use '# N.' comments")
        has_match = any(re.match(r"(And|Then|\*)\s+match\b", l) for l in code)
        has_retry = any("retry until" in l for l in code)
        has_status = any(re.match(r"(Then|And)\s+status\b", l) for l in code)
        calls_verify = any(re.search(r"call(?:once)?\s+(?:verify\w*|read\([^)]*(?:assert|verify|check|validate|expect)[^)]*\))", l, re.I) for l in code)
        has_match = has_match or any(re.match(r"\*\s+assert\b", l) for l in code)
        if not (has_match or calls_verify):
            # a called helper scenario may assert: read(var + '@Tag') whose target scenario contains match/assert
            defs = {**kc.project_defs(project), **kc.feature_defs(text)}
            for l in code:
                m = re.search(r"call(?:once)?\s+read\(([^)]*)\)", l)
                ref = kc.resolve_read(m.group(1).strip(), defs) if m else None
                target = kc.locate(project, ref) if ref else None
                if target:
                    tag = "@" + ref.split("@", 1)[1] if "@" in ref else None
                    for tsc in kc.parse_feature(target):
                        if (not tag or tag in tsc["tags"]) and any(re.match(r"\s*(\*|And|Then)\s+(match|assert)\b", b) for b in tsc["body"]):
                            calls_verify = True
        if not (has_match or has_retry or calls_verify):
            report("ERROR" if not has_status else "WARN",
                   f"{label}: no business assertion (match / retry until / verify reusable)" + ("; only status codes are checked" if has_status else ""))
        for i, l in enumerate(code):
            if re.match(r"(When|And|\*)\s+method\b", l):
                nxt = code[i + 1] if i + 1 < len(code) else ""
                if not re.match(r"(Then|And)\s+status\b", nxt):
                    report("WARN", f"{label}: '{l}' is not followed by 'Then status'")
        if code and code[-1].startswith("* configure headers"):
            team(r"configure headers|headersAdmin", f"{label}: ends with 'configure headers'")
        block = []
        for l in code + ["Given"]:
            if l.startswith("Given") or l == "Given":
                if any(b.startswith("And retry until") for b in block) and any(re.match(r"(And|Then)\s+match", b) for b in block):
                    team(r"No Mixing with And Match|retry until", f"{label}: 'retry until' and 'match' in the same request block")
                block = []
            block.append(l)
        for l in code:
            if re.match(r"(And|Then|\*)\s+match\s+\S+\[\d+\]", l) and "==" in l and "[*]" not in l:
                report("INFO", f"{label}: '{l[:90]}' assumes collection order; use [*] with contains unless the API sorts by contract")
                break

    # ---- registration
    runner_list = kc.runner_index(project).get(name, [])
    callers = kc.callers_index(project).get(name, [])
    if len(runner_list) > 1:
        report("ERROR", f"registered in {len(runner_list)} runners ({', '.join(runner_list)}): it would run twice")
    if a.runner and os.path.basename(a.runner)[:-5] not in runner_list:
        report("ERROR", f"not registered in {os.path.basename(a.runner)}")
    if a.root:
        root_text = open(a.root, encoding="utf-8").read()
        n = len(re.findall(rf"read\('[^']*\b{re.escape(name)}\.feature", root_text))
        if n != 1:
            report("ERROR", f"called {n} times from {os.path.basename(a.root)} (expected 1)")
    if not runner_list and not callers:
        # helpers are often reached dynamically (karate.call, a path built from a type name, another project's runner)
        refs = subprocess.run(["grep", "-rl", "--include=*.java", "--include=*.feature", "--include=*.js", name, "."],
                              capture_output=True, text=True).stdout.split()
        refs = [r for r in refs if not r.endswith(f"/{name}.feature")]
        if refs:
            report("INFO", f"not registered directly; referenced from {os.path.relpath(refs[0])}" + (f" and {len(refs) - 1} more" if len(refs) > 1 else "")
                   + " (helper or dynamic call): confirm it is executed")
        else:
            report("ERROR", "not registered: no runner, root feature or other file refers to it, so nothing runs it")

    for level in ("ERROR", "WARN", "INFO"):
        for msg in results[level]:
            print(f"{level:5} {msg}")
    print(f"\n{len(results['ERROR'])} error(s), {len(results['WARN'])} warning(s), {len(results['INFO'])} info")
    return 1 if results["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
