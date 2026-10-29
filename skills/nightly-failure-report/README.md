# nightly-failure-report

Triage a FOLIO stripes-testing (Cypress) run from its Jenkins Allure report. The skill turns every failed test into
one concrete fix - a diff in stripes-testing, a fix in a FOLIO module with a Jira summary, or the exact data to
restore on the environment - each marked **Ready** or **Needs verification**, and builds a single self-contained
HTML report (`report.html`) with one card per fix.

It also uses what is already known about the failed tests:

- **tickets linked in TestRail** - bugs people linked to the tests' results in the last days, with their current Jira status;
- **earlier analyses** - what previous reports concluded about the same tests, so a fix that was applied but did not help is spotted.

Works with any agent that supports skills (Claude Code, Cursor, Codex, ...), on Windows, macOS and Linux.

## Requirements

| what | notes |
|---|---|
| Python 3.8+ | Standard library only - nothing to `pip install`. Any of `python3`, `python` or `py -3` works; the agent picks the one that runs. |
| git | Used to read the stripes-testing commit the run used and to clone FOLIO modules. |
| A stripes-testing clone | Its `origin` remote must be `folio-org/stripes-testing`. The skill only runs `git fetch origin master` in it; your working tree and current branch are not touched, so you can keep working while it runs. |
| Network access | `jenkins.ci.folio.org`, `github.com`, `folio-org.atlassian.net` (public Jira REST), and optionally `foliotest.testrail.io` and the snapshot environments. |

No shell requirement: the commands work in bash, zsh, PowerShell and cmd. Git Bash is not needed on Windows.

### Windows: `python3` may not work

A fresh Windows has a Microsoft Store stub named `python3` that prints nothing or opens the Store. The skill detects
this and uses `python` or `py -3` instead. If none of them work, install Python from https://www.python.org/downloads/
(check "Add python.exe to PATH") or turn the stub off in *Settings → Apps → Advanced app settings → App execution aliases*.

## Install

```bash
npx skills add folio-org/folio-eureka-ai-dev --skill nightly-failure-report
```

or copy this folder into your agent's skills folder (e.g. `.claude/skills/nightly-failure-report`).

## Configuration

Nothing has to be configured before the first run. Settings live in **one file in your home folder**, outside the
skill and outside any repository, so updating the skill never overwrites them and they cannot be committed by accident:

```
~/.folio-nightly-report/config.json        (Windows: C:\Users\<you>\.folio-nightly-report\config.json)
```

It is created on first use from [assets/config.template.json](assets/config.template.json). When the agent needs a
value that is still empty (a password, your stripes-testing path), it asks you once, saves it, and reuses it in later
sessions.

> Values you type in the chat stay in that conversation's history. If you prefer, edit `config.json` yourself instead
> of answering in the chat - the agent tells you the path when it asks.

```json
{
  "environments": {
    "snapshot":     { "ui": "...", "api": "https://folio-etesting-snapshot-kong.ci.folio.org", "tenant": "diku", "username": "", "password": "" },
    "snapshot-ecs": { "ui": "...", "api": "https://ecs-folio-etesting-snapshot-kong.ci.folio.org", "tenant": "consortium", "members": ["college", "university"], "username": "", "password": "" }
  },
  "testrail": { "base_url": "https://foliotest.testrail.io", "username": "", "password": "" },
  "paths":    { "stripes_testing_repo": "", "work_dir": "", "repos_dir": "" }
}
```

| key | used for | if empty |
|---|---|---|
| `environments.<name>.username` / `.password` | read-only API lookups (`env_get.py`) on that environment | asked when the first lookup is needed |
| `testrail.username` / `.password` | tickets linked to the tests, current test case text | asked; you can decline - the report then says linked tickets were not checked |
| `paths.stripes_testing_repo` | reading the test code at the run commit | the current workspace, if it is stripes-testing; otherwise asked |
| `paths.work_dir` | where each run's work folder is kept | `~/.folio-nightly-report/runs` |
| `paths.repos_dir` | shared cache of cloned FOLIO modules | `~/.cache/folio-repos` |

Admin credentials for the environments are intentionally empty in the template - ask your team for them.

### Managing it from the command line

The agent uses these; you can too (`<skill>` is this folder):

```bash
python <skill>/scripts/config.py show                                   # print it, passwords masked
python <skill>/scripts/config.py set environments.snapshot.username <user>
python <skill>/scripts/config.py set environments.snapshot.password <password>
python <skill>/scripts/config.py import-testrail <path to a TestRail MCP server .env>   # reuse existing credentials
python <skill>/scripts/config.py add-env bugfest --api https://... --tenant fs09000000 --ui https://...
```

The file is written atomically and, on macOS/Linux, made readable only by you (`chmod 600`).

### Other environments

Mention an environment in the prompt ("look things up on bugfest: API ..., tenant ...") and the agent saves it as a
named environment (`config.py add-env`), asks for its credentials once, and you can refer to it by name later. For a
single lookup you don't want saved, the agent passes the details to `env_get.py` directly.

### Environment variables (optional)

Useful for CI or if you prefer them; they override the config file.

| variable | overrides |
|---|---|
| `TESTRAIL_BASE_URL`, `TESTRAIL_USERNAME`, `TESTRAIL_PASSWORD` | `testrail.*` |
| `STRIPES_TESTING_REPO` | `paths.stripes_testing_repo` |
| `NIGHTLY_TRIAGE_DIR` | `paths.work_dir` |
| `FOLIO_REPOS_DIR` | `paths.repos_dir` |
| `FOLIO_NIGHTLY_HOME` | the config folder itself (default `~/.folio-nightly-report`) |

## MCP servers

**None are required.** Jenkins/Allure, GitHub (via git) and Jira (public REST) are read directly; TestRail is read by
the bundled scripts with the credentials from the config.

Nice to have:

| server | why |
|---|---|
| TestRail MCP | ad-hoc case lookups in the chat while you discuss the report; the skill does not depend on it |
| Atlassian (Jira) MCP | file a bug from a report card, or comment on / link an existing ticket, without leaving the chat |
| GitHub MCP | open a PR with the fixes from the report |

To share the report, a client that can publish HTML pages (e.g. Claude Artifacts) gives you a link; otherwise the
report is a local file you can send as is.

## Usage

```
Analyze https://jenkins.ci.folio.org/job/folioScheduledTesting/job/runNightlyCypressEurekaTests/594/allure/
```

Optional additions to the prompt:

- a scope: "only Promin and Eureka team tests";
- a TestRail run to read linked tickets from (when every rerun gets a new run): "TestRail run 3695";
- an environment to check things on: "use the ECS snapshot" or the details of another one.

## Files on disk

| location | what | safe to delete? |
|---|---|---|
| `~/.folio-nightly-report/config.json` | your settings and credentials | only if you want to start over |
| `~/.folio-nightly-report/runs/<job>-<build>/` | one folder per analyzed run: downloaded Allure data, `analysis.json`, `report.html` | **no** - later analyses read earlier ones to see what was already tried; delete only very old runs |
| `~/.cache/folio-repos/` | blobless clones of FOLIO modules, updated on use | yes - re-cloned when needed |

## Troubleshooting

| symptom | fix |
|---|---|
| `python3` does nothing / opens the Microsoft Store | see *Windows: `python3` may not work* above |
| `Could not find the commit the run used` | `origin` in your stripes-testing clone is not `folio-org/stripes-testing`, or the path is wrong - check `config.py get paths.stripes_testing_repo` |
| `MISSING CONFIG: ...` | expected on first use: answer the agent's question or fill the key in `config.json` |
| `login ... failed: HTTP 401/422` | the saved environment credentials are wrong - `config.py set environments.<name>.password ...` |
| TestRail `HTTP 401` | wrong TestRail credentials; with SSO accounts use an API key from *My Settings → API Keys* as the password |
| `No TestRail run id found` | the build did not report to TestRail - give the run id in the prompt |
| Clones show up in your IDE's source control | set `paths.repos_dir` (or `FOLIO_REPOS_DIR`) to a folder outside your workspaces |

## Contents

| path | purpose |
|---|---|
| `SKILL.md` | the procedure the agent follows |
| `references/analysis-format.md` | format of `analysis.json`, the agent's findings |
| `references/environments.md` | environments for lookups and the rules (GET only) |
| `references/module-map.md` | which FOLIO module serves which API path |
| `assets/template.html` | the report page |
| `assets/config.template.json` | the initial config |
| `scripts/` | the scripts (see the table in `SKILL.md`) |
