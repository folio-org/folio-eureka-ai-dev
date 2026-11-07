#!/usr/bin/env python3
"""Delta refresh for write-testrail-cases context files.

Builds the "## Changes since <date>" section for one or more context files from:
  - GitHub: en.json diff of the area's UI module(s) between the build date and HEAD
  - Jira:   stories/bugs moved to Done since the build date
  - TestRail: cases created since the build date in the area's root sections

The "What changed" summary is NOT generated here — the agent writes it from the
collected data (see build-app-context SKILL.md, Refresh Mode).

Usage:
  python3 delta_refresh.py --areas orders,finance            # print sections to stdout
  python3 delta_refresh.py --areas all --write                # update context files in place
  python3 delta_refresh.py --areas orders --since 2026-06-17 --skip-jira

Credentials (first hit wins): .env in the repo root, ~/.folio-credentials, environment.
Keys: TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_API_KEY, JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN.
GitHub access is anonymous (public folio-org repos, git over HTTPS).
"""
import argparse
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
CONTEXT_DIR = REPO_ROOT / "skills" / "write-testrail-cases" / "references" / "context"
CONFIG = HERE / "areas.json"
PROJECT_ID, SUITE_ID = 14, 21
TODAY = dt.date.today().isoformat()


# ---------- credentials ----------
def load_creds():
    keys = ["TESTRAIL_URL", "TESTRAIL_USER", "TESTRAIL_API_KEY",
            "JIRA_BASE_URL", "JIRA_USER_EMAIL", "JIRA_API_TOKEN"]
    creds = {}
    for path in [REPO_ROOT / ".env", Path.home() / ".folio-credentials"]:
        if path.exists():
            for line in path.read_text().splitlines():
                m = re.match(r"\s*([A-Z_]+)\s*=\s*(.*)\s*$", line)
                if m and m.group(1) in keys and m.group(1) not in creds:
                    creds[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    for k in keys:
        creds.setdefault(k, os.environ.get(k, ""))
    return creds


def http_json(url, user, token, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None)
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode())
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


# ---------- context header ----------
def build_date(text):
    """Base date for the delta: Delta-refreshed if present, else Built."""
    head = "\n".join(text.splitlines()[:30])
    m = re.search(r"Delta-refreshed:\s*(\d{4}-\d{2}-\d{2})", head)
    if m:
        return m.group(1)
    m = re.search(r"Built:\s*(\d{4}-\d{2}-\d{2})", head)
    return m.group(1) if m else None


# ---------- GitHub ----------
def git(repo_dir, *args):
    return subprocess.run(["git", "-C", str(repo_dir), *args], capture_output=True, text=True).stdout


def github_delta(repo, since, workdir, key_filter=None):
    path = Path(workdir) / repo
    if not path.exists():
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout",
                        f"https://github.com/folio-org/{repo}", str(path)], check=True)
    files = git(path, "ls-tree", "-r", "--name-only", "HEAD").split("\n")
    tfile = next((f for f in files if re.match(r"translations/[^/]+/en\.json$", f)), None)
    base = git(path, "rev-list", "-1", f"--before={since}T23:59", "HEAD").strip()
    tag = git(path, "describe", "--tags", "--abbrev=0", "HEAD").strip()
    added, changed, removed = {}, {}, {}
    if tfile and base:
        old = json.loads(git(path, "show", f"{base}:{tfile}") or "{}")
        new = json.loads(git(path, "show", f"HEAD:{tfile}") or "{}")
        keep = (lambda k: True) if not key_filter else (lambda k: re.search(key_filter, k, re.I))
        added = {k: v for k, v in new.items() if k not in old and keep(k)}
        changed = {k: (old[k], v) for k, v in new.items() if k in old and old[k] != v and keep(k)}
        new_values = set(map(str, new.values()))
        removed = {k: v for k, v in old.items() if k not in new and keep(k) and str(v) not in new_values}
    commits = [c for c in git(path, "log", f"--since={since}", "--no-merges",
                              "--format=%ad|%s", "--date=short", "HEAD").strip().split("\n")
               if c and not re.search(r"translat|lokalise|bump|deps|dependabot|release v|changelog|yarn|workflow|chore", c, re.I)]
    return dict(repo=repo, tfile=tfile, tag=tag, added=added, changed=changed, removed=removed, commits=commits)


# ---------- Jira ----------
def jira_delta(creds, projects, since):
    if not (creds["JIRA_BASE_URL"] and creds["JIRA_API_TOKEN"]):
        return None
    jql = (f"project in ({','.join(projects)}) AND issuetype in (Story, Bug, \"New Feature\") "
           f"AND statusCategory = Done AND resolved >= {since} ORDER BY resolved DESC")
    url = creds["JIRA_BASE_URL"].rstrip("/") + "/rest/api/3/search/jql"
    out, token = [], None
    while True:
        body = {"jql": jql, "maxResults": 100, "fields": ["summary", "issuetype"]}
        if token:
            body["nextPageToken"] = token
        data = http_json(url, creds["JIRA_USER_EMAIL"], creds["JIRA_API_TOKEN"], body)
        for i in data.get("issues", []):
            out.append((i["key"], i["fields"]["issuetype"]["name"], i["fields"]["summary"]))
        token = data.get("nextPageToken")
        if not token or len(out) >= 300:
            return out


# ---------- TestRail ----------
_sections = None


def testrail_sections(creds):
    global _sections
    if _sections is None:
        base = creds["TESTRAIL_URL"].rstrip("/") + "/index.php?/api/v2/"
        res, offset = [], 0
        while True:
            data = http_json(f"{base}get_sections/{PROJECT_ID}&suite_id={SUITE_ID}&offset={offset}",
                             creds["TESTRAIL_USER"], creds["TESTRAIL_API_KEY"])
            batch = data.get("sections", data) if isinstance(data, dict) else data
            res += batch
            if not isinstance(data, dict) or not data.get("_links", {}).get("next"):
                break
            offset += len(batch)
        _sections = res
    return _sections


def testrail_delta(creds, root_names, since):
    if not (creds["TESTRAIL_URL"] and creds["TESTRAIL_API_KEY"]):
        return None
    secs = testrail_sections(creds)
    by_id = {s["id"]: s for s in secs}

    def root(i):
        while by_id.get(i) and by_id[i]["parent_id"]:
            i = by_id[i]["parent_id"]
        return by_id[i]["name"] if i in by_id else None

    base = creds["TESTRAIL_URL"].rstrip("/") + "/index.php?/api/v2/"
    after = int(dt.datetime.fromisoformat(since).replace(tzinfo=dt.timezone.utc).timestamp())
    cases, offset = [], 0
    while True:
        data = http_json(f"{base}get_cases/{PROJECT_ID}&suite_id={SUITE_ID}&created_after={after}&limit=250&offset={offset}",
                         creds["TESTRAIL_USER"], creds["TESTRAIL_API_KEY"])
        batch = data.get("cases", data) if isinstance(data, dict) else data
        cases += [c for c in batch if root(c["section_id"]) in root_names]
        if not isinstance(data, dict) or not data.get("_links", {}).get("next"):
            break
        offset += len(batch)
    return cases


# ---------- rendering ----------
def esc(v):
    return str(v).replace("|", "\\|").replace("\n", " ")


def render(area, since, gh, jira, tr):
    out = [f"## Changes since {since} (delta refresh {TODAY})", "",
           "> Delta, not a rebuild: sections above reflect the original build. Where this section contradicts them, **this section wins**.",
           "> Sources: " + "; ".join(f"GitHub folio-org/{g['repo']} ({g['tfile'] or 'no translations'}, HEAD {g['tag']})" for g in gh)
           + f"; Jira Done issues resolved since {since}; TestRail suite {SUITE_ID} cases created since {since}.", "",
           "### What changed", "",
           "<!-- Agent: replace this comment with 3-8 bullets, each tied to a Jira key or commit, summarising the data below. -->", ""]
    rows = [(k, v) for g in gh for k, v in g["added"].items()]
    chg = [(k, o, n) for g in gh for k, (o, n) in g["changed"].items()]
    rem = [(k, v) for g in gh for k, v in g["removed"].items()]
    if rows or chg or rem:
        out += [f"### UI strings changed since {since} [source — en.json, {TODAY}]", "",
                "> `en.json` is the source of truth; `en_US.json` is a Lokalise copy that can lag behind. `{x}` are placeholders.", ""]
        if rows:
            out += ["**New strings**", "", "| Key | Text |", "|---|---|"] + [f"| `{k}` | {esc(v)} |" for k, v in rows] + [""]
        if chg:
            out += ["**Changed strings** (assert the new text)", "", "| Key | Old | New |", "|---|---|---|"] + \
                   [f"| `{k}` | {esc(o)} | {esc(n)} |" for k, o, n in chg] + [""]
        if rem:
            out += ["**Removed strings — do not assert**", "", "| Key | Text |", "|---|---|"] + [f"| `{k}` | {esc(v)} |" for k, v in rem] + [""]
    commits = [c for g in gh for c in g["commits"]][:20]
    if commits:
        out += ["### Code changes (commit subjects)", ""] + [f"- {c.replace('|', ' — ', 1)}" for c in commits] + [""]
    out += [f"### Jira — Done since {since}", ""]
    if jira is None:
        out += ["- Not collected (Jira credentials missing or --skip-jira).", ""]
    elif not jira:
        out += ["- No Done stories or bugs.", ""]
    else:
        out += [f"- {k} {t} — {esc(s)}" for k, t, s in jira] + [""]
    if tr is None:
        out += [f"### TestRail — cases created since {since}", "", "- Not collected (TestRail credentials missing or --skip-testrail).", ""]
    else:
        manual = [c for c in tr if c.get("custom_automation_type") == 2]
        out += [f"### TestRail — cases created since {since}: {len(tr)} ({len(manual)} manual)", ""]
        out += [f"- C{c['id']} {esc(c['title'].strip())}" + (f" — refs {esc(c['refs'])}" if c.get("refs") else "")
                for c in sorted(manual, key=lambda c: -c["created_on"])[:40]] or ["- No new manual cases."]
        out += [""]
    return "\n".join(out).rstrip() + "\n"


def write_back(path, text, section):
    text = re.sub(r"\n+---\n+## Changes since .*", "", text, flags=re.S).rstrip()  # replace previous delta
    text = re.sub(r"(> Built: [^·\n]+)(?:· Delta-refreshed: \S+ )?·", lambda m: f"{m.group(1).rstrip()} · Delta-refreshed: {TODAY} ·", text, count=1)
    path.write_text(text + "\n\n---\n\n" + section)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--areas", required=True, help="comma-separated area names from areas.json, or 'all'")
    ap.add_argument("--since", help="override the base date (YYYY-MM-DD); default: Delta-refreshed or Built from the file header")
    ap.add_argument("--write", action="store_true", help="replace the Changes since section in the context file")
    ap.add_argument("--skip-jira", action="store_true")
    ap.add_argument("--skip-testrail", action="store_true")
    args = ap.parse_args()

    config = json.loads(CONFIG.read_text())
    names = list(config) if args.areas == "all" else args.areas.split(",")
    creds = load_creds()
    with tempfile.TemporaryDirectory() as work:
        for name in names:
            cfg = config[name]
            path = CONTEXT_DIR / f"{name}.md"
            text = path.read_text()
            since = args.since or build_date(text)
            if not since:
                print(f"[{name}] no Built/Delta-refreshed date in header — pass --since", file=sys.stderr)
                continue
            gh = [github_delta(r, since, work, cfg.get("key_filter")) for r in cfg.get("repos", [])]
            jira = None if args.skip_jira else jira_delta(creds, cfg["jira"], since)
            tr = None if args.skip_testrail else testrail_delta(creds, cfg["testrail_roots"], since)
            section = render(name, since, gh, jira, tr)
            if args.write:
                write_back(path, text, section)
                print(f"[{name}] updated ({since} → {TODAY})", file=sys.stderr)
            else:
                print(f"\n<!-- {name} -->\n{section}")


if __name__ == "__main__":
    main()
