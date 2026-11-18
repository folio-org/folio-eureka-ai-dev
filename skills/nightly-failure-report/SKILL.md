---
name: nightly-failure-report
description: 'Analyze a Jenkins Allure report of a FOLIO stripes-testing (Cypress) run and build an HTML fix list - for every failed test, one concrete fix: a diff in stripes-testing, a fix in the FOLIO module code (with a Jira summary), or the exact data to create or restore on the environment - each marked Ready or Needs verification. Uses tickets already linked to the tests in TestRail, the findings of earlier analyses and a registry of known issues that persist across runs. Use when the user shares a jenkins.ci.folio.org .../allure/ link, or asks to analyze nightly, Cypress or Allure failures, triage a nightly run, or build a failure report.'
argument-hint: 'Allure report URL, e.g. https://jenkins.ci.folio.org/job/folioScheduledTesting/job/runNightlyCypressEurekaTests/594/allure/ - optionally a TestRail run id to read previously linked tickets from, a team scope, or a custom environment to look things up on'
---

# Nightly Failure Report

Turns a failed nightly Cypress run into a list of fixes that teams can apply. Every failed test belongs to exactly one fix, and every fix says what to change, where, and how sure we are.

## When to Use

- The user shares a Jenkins Allure link such as `https://jenkins.ci.folio.org/job/folioScheduledTesting/job/runNightlyCypressEurekaTests/594/allure/` (nightly jobs or `folioTestingTools/runCypressTests` reruns).
- The user asks to triage a nightly run, analyze Cypress or Allure failures, or build a failure report.

If the user limits the scope (e.g. "only Promin and Eureka tests"), analyze only tests with those team tags; still run every script on the whole run.

## Setup and conventions

Requirements: Python 3.8+ (standard library only) and `git`. No MCP server is required. See [README.md](README.md) for setup.

- **`SKILL_DIR`** is the folder of this file. All scripts are in `SKILL_DIR/scripts`.
- **Python command.** Use `python3` if `python3 --version` prints a version; otherwise `python`; otherwise `py -3` (Windows launcher). On Windows `python3` may be a Microsoft Store stub that prints nothing or opens the Store - then use `python`. Pick once and use it for every command below (written as `python`). Run scripts as `python -I "<SKILL_DIR>/scripts/<script>.py" ...` - `-I` keeps a downloaded file in the working folder from being imported.
- **Shell.** Commands use only quoted paths and arguments, so they work in bash, zsh, PowerShell and cmd. Shell variables do not persist between tool calls; write the real paths into each command.
- **Config.** User settings live in `~/.folio-nightly-report/config.json` (created on first use from `assets/config.template.json`): environments for lookups, TestRail credentials, paths. Manage it only with `config.py` (`show`, `get`, `set`, `add-env`, `import-testrail`, `workdir`, `repo`).
- **Missing values (exit code 3).** When a script prints `MISSING CONFIG: <keys>`, ask the user for exactly those values, save each with `python -I "<SKILL_DIR>/scripts/config.py" set <key> "<value>"`, and rerun. Tell the user once that values typed in the chat stay in the conversation, and that they can instead edit the config file themselves (the message prints its path). Saved values are reused in later runs; do not ask again.

## Output

An HTML page (`report.html`) with one card per fix. Each fix has a type:

| type | meaning | the fix must contain |
|---|---|---|
| `test` | the test is wrong or outdated | file:line in stripes-testing and a full diff |
| `app` | the FOLIO module behaves wrongly | module repo, the commit you read (`ref`), file:line, a full diff, a Jira summary (or an existing ticket) |
| `data` | the environment is missing data or has bad data or settings | the exact API request (method, path, JSON body) or exact UI steps |

Each fix is marked **Ready** or **Needs verification**, with the reasons. Teams apply Ready fixes as written, so a Ready fix must be correct, complete, and must not weaken the test. Prefer a smaller, honest Ready set over a long list of guesses.

Each card also has a **Copy AI prompt** button that gives a ready-to-paste prompt for applying the fix in the right repository.

## Procedure

### Step 1: Download and extract the run

1. Find the stripes-testing clone: `python -I "<SKILL_DIR>/scripts/config.py" repo`. On exit code 3, use the current workspace if it is a stripes-testing clone (it has `cypress/e2e` and a `package.json` named `@folio/stripes-testing`), otherwise ask the user; save it with `config.py set paths.stripes_testing_repo "<path>"`. This is `REPO`.
2. Create the work folder: `python -I "<SKILL_DIR>/scripts/config.py" workdir <name>`, with `<name>` from the job and build: `nightly-<build>`, `nightly-ecs-<build>` (the ECS job), `rerun-<build>` (runCypressTests). It prints the path - this is `WORK`. Work folders are kept on purpose: `previous_findings.py` reads the earlier ones. Never delete them or put them in a temp folder.
3. Run, in order:

```
python -I "<SKILL_DIR>/scripts/fetch_allure.py" "<allure url>" "<WORK>"
python -I "<SKILL_DIR>/scripts/extract.py" "<WORK>" "<REPO>"
python -I "<SKILL_DIR>/scripts/linked_defects.py" "<WORK>"        # add --run <id> / --days <n> if needed
python -I "<SKILL_DIR>/scripts/previous_findings.py" "<WORK>"
python -I "<SKILL_DIR>/scripts/known_issues.py" match "<WORK>"
```

`extract.py` runs `git fetch origin master` in `REPO` (remote `origin` must be folio-org/stripes-testing) so the run commit is available; it does not touch the working tree or the current branch.

`linked_defects.py` collects the bug tickets people already linked to the failed tests: the `defects` field of the tests' TestRail results from 5 days before the build started until now (`--days` changes it), with each ticket's current Jira status. By default it reads the TestRail run the analyzed build reported to (its `TESTRAIL_RUN_ID` parameter, or `RunID: N` in the console). When the user gives another TestRail run - e.g. runs are not reused and every rerun gets a new one, but tickets were linked in an earlier run - pass it with `--run <id>`. If the script cannot find a run id, ask the user for one. It needs TestRail credentials (exit code 3 → ask, see above). If the user has none or does not want to give them, skip this step and say in the reply that linked tickets were not checked; the report shows the same. It writes `linked_defects.json` and adds a `linked:` line under each test in `dump.md`.

`previous_findings.py` reads earlier work folders (the siblings of `WORK` holding `analysis.json` and `meta.json`, newest first; add `--history <dir>` for other locations) and collects, per failed test, the fixes earlier analyses put it in: run, fix id, cause, confidence, title, evidence, ticket and changed paths. It writes `previous_findings.json` and adds a `previously:` line under each test in `dump.md`.

`known_issues.py match` reads the known-issue registry `known_issues.json` in the parent of `WORK` (the folder with all work folders). Known issues have stable keys `KI-01`, `KI-02`, ... that stay the same in every run, next to their Jira key when there is one - fix ids (`F01`, ...) are only valid inside one report. It matches each failed test by test id (the test was in that issue before - a hint, confirm the cause is the same now) or by the issue's `error` regex, writes `known_matches.json` and adds a `known:` line under each matched test in `dump.md`. A match on an issue marked `fixed` means it is back - say so in the fix evidence and the reply. Reuse a known issue's earlier analysis (its `note`, the earlier report) instead of re-deriving it, but check the evidence still holds. With no registry yet, it matches nothing; the first `add` (Step 4) creates it.

Read `<WORK>/dump.md`. It groups tests with the same normalized error into clusters, largest first. Each test line has the stage, the team (from the test tag), the start time, the run history `h=passed/total`, the error, and `at:` - the spec or fragment line at the run commit; `linked:` lists tickets linked to the test in TestRail with their status (open/closed) and the last date they were linked; `previously:` is the newest earlier finding for the test (details in `previous_findings.json`); `known:` is a known issue the test matches. Do not read the raw Allure JSON.

### Step 2: Investigate

| need | command |
|---|---|
| A ticket linked to the test (`linked:` in `dump.md`) | Read it before investigating: `curl -s "https://folio-org.atlassian.net/rest/api/2/issue/<KEY>?fields=summary,status,description,issuelinks,comment"` (public, no auth; `curl` ships with Windows 10+, macOS and Linux). Compare its steps and error with this failure. |
| Test code at the run commit | `git -C "<REPO>" show <sha>:<path>` (`sha` is in `<WORK>/meta.json`); read only the lines you need. |
| Screenshot of a UI failure | `python -I "<SKILL_DIR>/scripts/screenshot.py" "<WORK>" C123 C456`, then open the PNGs. Do this for every UI failure whose error does not say what the page showed. |
| Module source | `python -I "<SKILL_DIR>/scripts/app_repo.py" <repo>` (prints the clone path and `ref`), then `git -C "<clone path>" grep -n "<exact error message>"`. Clones live in one shared cache outside the workspace and are updated on each call. |
| Why the behavior changed | `python -I "<SKILL_DIR>/scripts/ticket.py" <repo> <path> [<from>,<to>]` lists recent commits with Jira keys. A commit dated after the run start is not deployed yet. |
| What the test case says now | `python -I "<SKILL_DIR>/scripts/testrail_case.py" C123 [C456 ...]` (a connected TestRail MCP server works too). Check: deleted, or a test group other than 1/2/3/6/7, means retire the test, not fix it; `unstable` means known flaky (look for `parallel-conflict`/`infra` before `app-bug`); "bug already created" or an open issue in `refs` means a bug is already filed, so reference it instead of writing a new `jira`; `updated` after the run start plus steps matching the new behavior support `outdated-test`. The script flags these. |
| Live ids, settings, API behavior | `python -I "<SKILL_DIR>/scripts/env_get.py" <env> "<path?query>" [--tenant college]` - see [references/environments.md](references/environments.md). |

To find which module serves a failing API path, see [references/module-map.md](references/module-map.md).

The nightly run's own environment is torn down after the run, so lookups go to the snapshot environments (configured by default) or to an environment the user names. Reruns (`folioTestingTools/runCypressTests`) often target a long-lived environment (e.g. a sprint-testing one) that stays up - then look things up on that environment itself rather than on snapshot. If the user gives other environment details in the prompt (hosts, tenant, admin user), save them with `config.py add-env <name> --api <url> --tenant <tenant> [--ui <url>] [--members a,b]` and use that name; credentials are asked and saved like any other missing value. For a one-off lookup the user does not want saved, pass them to `env_get.py` directly (`--api ... --login-tenant ... --username ... --password ...`).

### Step 3: Decide the fix

Start from what is already known about each test: a known issue (`known:`), an earlier finding (`previously:`) and linked tickets (`linked:`).

- **Same error as the earlier finding**: check whether its fix was applied (look for the changed paths at the run commit). Not applied - reuse the finding and say so. Applied but the test still fails the same way - the earlier cause was wrong or incomplete; say that in `evidence`.
- **Different error than before**: the earlier blocker may be fixed and the test now fails further on (e.g. a step it never reached before). Say so, and do not trust its run history for the new step.
- An earlier "cause not established, monitor" finding that fails again is a second data point - use it.

Work cluster by cluster, biggest first. Start with the tickets already linked to the tests (`linked:`):

- An **open** linked ticket is the first candidate cause. If its description matches this failure (same steps, same error or symptom), use it: put the key in `ticket` and the evidence, and for an `app` fix write `jira` as `Existing: <KEY> <summary>` instead of a new bug. Still verify the failure is the same; a ticket linked for an older failure can be stale.
- A **closed** linked ticket whose symptom is back points to a regression (or an incomplete fix): say so in the evidence and reference the key.
- If a linked ticket turns out to be unrelated, say why in one sentence in the test's note, so the reader does not have to check it again.

Then pick a `cause`:

- **`env-pollution`** - many tests in different areas fail with the same API error after time T. Find the earliest test that changes a global setting and whose `after()` crashed before restoring it. Fix: `data` (restore now) plus `changes` to the culprit's cleanup, type `test`.
- **`parallel-conflict`** - fixed ids or names in fixtures, a global setting set or reset by parallel specs, exact tenant-wide counts. Fix: unique data, no reset, assert on own data, or a `nonParallel` tag.
- **`outdated-test`** - the UI or API changed on purpose. Prove it with `ticket.py` on the module file that renders the text or field, and put the Jira key or commit URL in `ticket`. If there is no ticket, it is either a regression (`app-bug`) or stays `outdated-test` with Needs verification. Never delete or loosen an assertion without a ticket.
- **`app-bug`** - the module rejects a valid request, returns 5xx, or the UI misbehaves against its own API. Prove it: the module GET returns what its PUT rejects, the validator contradicts the schema, the screenshot shows the broken UI. Point to the exact module line (`ref` + `line`), write the diff and a `jira` summary. Use `ticket.py` to find the commit that introduced it.
- **`data-missing`** - reference data or settings are missing or broken. Give the exact request; look up ids and values on the environment or in the test.
- **`test-bug`** - cleanup crash in `after()`, wrong selector, JS error in the spec. Give the diff.
- **`infra`** - an external service is down or slow (KB sandbox, Z39.50 target). Fix the test only when it waits wrongly (e.g. poll by id instead of name search); otherwise give a data or app fix for the service config.

One fix = one concrete problem. Tests that only share a theme ("Data import specs ...") are separate fixes. A singleton gets its own fix with the failing line, one screenshot, and at most one module lookup.

### Step 4: Write analysis.json

Write `<WORK>/analysis.json` once, in English. Read [references/analysis-format.md](references/analysis-format.md) for the format and field rules first.

Set `"known": "KI-NN"` on every fix that is a known issue (the card shows the key, the ticket and the earlier runs it was seen in). When a fix is not in the registry yet but is the same problem as in an earlier run, or has a Jira ticket (it keeps failing until the ticket is fixed), add it first and use the printed key:

```
python -I "<SKILL_DIR>/scripts/known_issues.py" add "<WORK>" --title "<problem, as in the fix title>" --ticket <KEY> --tests C1,C2 [--error "<regex>"] [--note "<what was applied / where the notes are>"]
```

A one-off failure stays a plain fix without `known`. When a fix for a known issue is applied or its ticket is closed, update the issue: `known_issues.py set "<WORK>" KI-NN status=fixed note="..."` (`closed` stops matching it; `fixed` keeps matching, so a comeback is flagged).

### Step 5: Render

```
python -I "<SKILL_DIR>/scripts/render.py" "<WORK>"
```

`render.py` refuses to build the report when:

- a title is vague (misc, other, various, several, unknown, ...) or a note just repeats the error;
- a diff contains an ellipsis, has no `-`/`+` lines, or adds a no-op like `() => true`;
- one shared change (`"tests": "all"`) covers tests with mostly different errors - that is a bucket, not a fix. Split it, give each test its own change, or, only when one root cause really produces different symptoms (shared fixture, cascade), add `same_cause` with the proof;
- a test is not fixed by any change, or appears in two fixes;
- an `app` fix has no `ref`, `line`, or `jira` (unless it points to an existing ticket).

It marks a fix **Needs verification** when:

- confidence is `Likely`;
- a diff removes or loosens an assertion, or skips a test, without a `ticket`;
- the cause is `outdated-test` without a `ticket`;
- a data request contains `<placeholders>`;
- a data request changes shared configuration (DELETE, or PUT/PATCH on policies, rules, specifications, settings, profiles).

It also prints, per fix, the **open** tickets linked to its tests in TestRail that the fix does not mention. Each one must be either referenced in the fix or explained as unrelated in the test's note.

Fix the hard errors and rerun. Then read the "needs verification" and linked-ticket lines it prints: if more evidence can remove a reason (find the ticket, look up the real id), do it now and rerun.

Then record this run in the registry (adds the run and fix id to each referenced issue's `seen` list; safe to rerun after edits):

```
python -I "<SKILL_DIR>/scripts/known_issues.py" record "<WORK>"
```

### Step 6: Share

The report is `<WORK>/report.html`, a single self-contained file. Do not restyle it. If your tool can publish an HTML page (for example, Claude Artifacts), publish it; otherwise give the user the file path.

Reply with the link or path and a short summary:

- tests with a Ready fix vs. Needs verification;
- counts by fix type;
- the biggest fixes;
- known issues seen again (KI key, ticket, earlier runs) - especially ones marked `fixed` that came back;
- any environment action someone must take before the next run;
- whether linked tickets were checked (and which TestRail run).

Fix ids are shown on the cards (`F05`) and are what the user names when discussing a report; KI keys are what to use across runs. Each test row has a run-history bar (newest run on top, up to 15 runs; green passed, red failed or broken) linking to each run's Allure result.

### Step 7 (only when the user asks): Post results with tickets to TestRail

When the user asks to record failures explained by a Jira ticket in the run's TestRail run (the run `linked_defects.py` used, or the one the user names), post one result per test:

```
python -I "<SKILL_DIR>/scripts/testrail_result.py" <run id> <case id> --status failed --defects <KEY> --comment "<html>" --dry-run
```

Check the dry run, then send it without `--dry-run`. A connected TestRail MCP server with an add-result tool works too; the rules are the same:

- **Status `failed`** by default. Nightly runs test master, where nothing is normally deferred. `deferred` means the failure is caused by a ticket that is not expected to be fixed for the target release any time soon - use it only with a strong reason, and ask the user first.
- **Defects: Jira keys only** (`MODINV-1433`; several: `MODINV-1433,MODINV-1439`). Never a URL - the TestRail-Jira integration builds the link, and a full link breaks it. The script rejects anything else.
- **Comment:** HTML (`<p>`, `<strong>`, `<br>`), short: what failed and how it matches the ticket. If part of the failure is not covered by the ticket, say so in a separate paragraph ("Not covered by the ticket: ...") so the defect does not hide it. Do not mention environments, hosts, tenants or admin users - TestRail results can be read by many people.
- Do not set a version. Results cannot be edited or deleted through the API; a new result supersedes the old one. If the run is closed, TestRail refuses the result - tell the user; do not post to another run instead.

The posted defects are what `linked_defects.py` reads in the next analysis.

### Sharing triage history (only when the user asks)

Earlier analyses and the known-issue registry make the next analysis better, so they are worth handing over (e.g. to whoever triages a team's tests while you are away). They are local files; share them with:

```
python -I "<SKILL_DIR>/scripts/history.py" export "<zip file>" [--teams promin,eureka] [--last 10]
python -I "<SKILL_DIR>/scripts/history.py" import "<zip file>"
```

`export` packs the registry and, per analyzed run, only the analysis results, reports and `.md` notes - no Allure downloads, screenshots, scripts, logs, config or credentials. Tell the user to look through the `.md` notes it lists before sending the file. `import` puts the runs next to the recipient's own work folders (existing ones are kept) and merges the registry when the KI keys agree; otherwise it saves the incoming one as `known_issues.imported.json` and says which keys clash.

## Scripts

| script | purpose |
|---|---|
| `scripts/config.py` | Reads and writes the user config: environments, TestRail credentials, paths; creates work folders. |
| `scripts/fetch_allure.py` | Downloads the summary and every failed or broken test case from the Allure report. |
| `scripts/extract.py` | Finds the root-cause stage, error, history and failing code line of each test; clusters tests by error; writes `dump.md`, `tests.json`, `meta.json`. |
| `scripts/linked_defects.py` | Collects tickets linked to the failed tests in TestRail (last N days, the build's run or `--run`) with their Jira status; writes `linked_defects.json`, annotates `dump.md`. |
| `scripts/previous_findings.py` | Collects earlier analyses' findings for the failed tests from sibling work folders; writes `previous_findings.json`, annotates `dump.md`. |
| `scripts/known_issues.py` | Known-issue registry (`known_issues.json` next to the work folders, stable `KI-NN` keys across runs): `match` annotates this run's tests, `add` / `set` maintain issues, `record` adds this run to each referenced issue, `list` prints them. |
| `scripts/screenshot.py` | Downloads Allure screenshots for given test ids. |
| `scripts/app_repo.py` | Clones or updates a FOLIO module (blobless, shared cache) and prints the `ref` to cite. |
| `scripts/ticket.py` | Lists recent commits and Jira keys that touched a module file or line range. |
| `scripts/testrail_case.py` | Prints a TestRail case's current steps and triage flags (deleted, invalid group, unstable, bug created). |
| `scripts/testrail_result.py` | Posts one result (status by name, Jira keys as defects, HTML comment) to a TestRail run; `--dry-run` previews it. Step 7 only. |
| `scripts/env_get.py` | Sends one GET to a configured (or one-off) FOLIO environment as its admin; never other methods. |
| `scripts/render.py` | Validates `analysis.json` and builds `report.html` from `assets/template.html`; shows linked tickets, known issues and run history per test, and warns about open tickets a fix does not mention. |
| `scripts/history.py` | Exports earlier analyses and the known-issue registry to a zip for other people, and imports one. |
| `scripts/common.py` | Shared helpers (UTF-8 output, config access); not run directly. |
