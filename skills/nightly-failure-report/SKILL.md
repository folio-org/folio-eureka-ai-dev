---
name: nightly-failure-report
description: 'Analyze a Jenkins Allure report of a FOLIO stripes-testing (Cypress) run and build an HTML fix list - for every failed test, one concrete fix: a diff in stripes-testing, a fix in the FOLIO module code (with a Jira summary), or the exact data to create or restore on the environment - each marked Ready or Needs verification. Use when the user shares a jenkins.ci.folio.org .../allure/ link, or asks to analyze nightly, Cypress or Allure failures, triage a nightly run, or build a failure report.'
argument-hint: 'Allure report URL, e.g. https://jenkins.ci.folio.org/job/folioScheduledTesting/job/runNightlyCypressEurekaTests/594/allure/'
---

# Nightly Failure Report

Turns a failed nightly Cypress run into a list of fixes that teams can apply. Every failed test belongs to exactly one fix, and every fix says what to change, where, and how sure we are.

## When to Use

- The user shares a Jenkins Allure link such as `https://jenkins.ci.folio.org/job/folioScheduledTesting/job/runNightlyCypressEurekaTests/594/allure/`.
- The user asks to triage a nightly run, analyze Cypress or Allure failures, or build a failure report.

## Prerequisites

- `python3` (standard library only) and `git`.
- A local clone of [stripes-testing](https://github.com/folio-org/stripes-testing), referred to as `REPO` (default `~/stripes-testing`). Run `git -C $REPO fetch` so the run commit is available.
- Network access to `jenkins.ci.folio.org` and `github.com`.

## Output

An HTML page (`report.html`) with one card per fix. Each fix has a type:

| type | meaning | the fix must contain |
|---|---|---|
| `test` | the test is wrong or outdated | file:line in stripes-testing and a full diff |
| `app` | the FOLIO module behaves wrongly | module repo, the commit you read (`ref`), file:line, a full diff, a Jira summary |
| `data` | the environment is missing data or has bad data or settings | the exact API request (method, path, JSON body) or exact UI steps |

Each fix is marked **Ready** or **Needs verification**, with the reasons. Teams apply Ready fixes as written, so a Ready fix must be correct, complete, and must not weaken the test. Prefer a smaller, honest Ready set over a long list of guesses.

Each card also has a **Copy AI prompt** button that gives a ready-to-paste prompt for applying the fix in the right repository.

## Procedure

### Step 1: Download and extract the run

- `SKILL_DIR` = the directory of this file.
- `WORK` = a new empty temporary folder, e.g. `<tmp>/nightly-<build>`.

```bash
python3 -I "$SKILL_DIR/scripts/fetch_allure.py" "<allure url>" "$WORK"
python3 -I "$SKILL_DIR/scripts/extract.py" "$WORK" "$REPO"
```

Read `$WORK/dump.md`. It groups tests with the same normalized error into clusters, largest first. Each test line has the stage, the team (from the test tag), the start time, the run history `h=passed/total`, the error, and `at:` - the spec or fragment line at the run commit. Do not read the raw Allure JSON.

### Step 2: Investigate

| need | command |
|---|---|
| Test code at the run commit | `git -C $REPO show <sha>:<path> \| sed -n 'A,Bp'` (`sha` is in `$WORK/meta.json`) |
| Screenshot of a UI failure | `python3 -I $SKILL_DIR/scripts/screenshot.py $WORK C123 C456`, then open the PNGs. Do this for every UI failure whose error does not say what the page showed. |
| Module source | `bash $SKILL_DIR/scripts/app_repo.sh $WORK <repo>` (prints `ref`), then `git -C $WORK/repos/<repo> grep -n "<exact error message>"` |
| Why the behavior changed | `bash $SKILL_DIR/scripts/ticket.sh $WORK <repo> <path> [<from>,<to>]` lists recent commits with Jira keys. A commit dated after the run start is not deployed yet. |

To find which module serves a failing API path, see [references/module-map.md](references/module-map.md).

### Step 3: Decide the fix

Work cluster by cluster, biggest first, and pick a `cause`:

- **`env-pollution`** - many tests in different areas fail with the same API error after time T. Find the earliest test that changes a global setting and whose `after()` crashed before restoring it. Fix: `data` (restore now) plus `changes` to the culprit's cleanup, type `test`.
- **`parallel-conflict`** - fixed ids or names in fixtures, a global setting set or reset by parallel specs, exact tenant-wide counts. Fix: unique data, no reset, assert on own data, or a `nonParallel` tag.
- **`outdated-test`** - the UI or API changed on purpose. Prove it with `ticket.sh` on the module file that renders the text or field, and put the Jira key or commit URL in `ticket`. If there is no ticket, it is either a regression (`app-bug`) or stays `outdated-test` with Needs verification. Never delete or loosen an assertion without a ticket.
- **`app-bug`** - the module rejects a valid request, returns 5xx, or the UI misbehaves against its own API. Prove it: the module GET returns what its PUT rejects, the validator contradicts the schema, the screenshot shows the broken UI. Point to the exact module line (`ref` + `line`), write the diff and a `jira` summary. Use `ticket.sh` to find the commit that introduced it.
- **`data-missing`** - reference data or settings are missing or broken. Give the exact request; look up ids and values on the environment or in the test.
- **`test-bug`** - cleanup crash in `after()`, wrong selector, JS error in the spec. Give the diff.
- **`infra`** - an external service is down or slow (KB sandbox, Z39.50 target). Fix the test only when it waits wrongly (e.g. poll by id instead of name search); otherwise give a data or app fix for the service config.

One fix = one concrete problem. Tests that only share a theme ("Data import specs ...") are separate fixes. A singleton gets its own fix with the failing line, one screenshot, and at most one module lookup.

### Step 4: Write analysis.json

Write `$WORK/analysis.json` once, in English. Read [references/analysis-format.md](references/analysis-format.md) for the format and field rules first.

### Step 5: Render

```bash
python3 -I "$SKILL_DIR/scripts/render.py" "$WORK"
```

`render.py` refuses to build the report when:

- a title is vague (misc, other, various, several, unknown, ...) or a note just repeats the error;
- a diff contains an ellipsis, has no `-`/`+` lines, or adds a no-op like `() => true`;
- one shared change (`"tests": "all"`) covers tests with mostly different errors - that is a bucket, not a fix. Split it, give each test its own change, or, only when one root cause really produces different symptoms (shared fixture, cascade), add `same_cause` with the proof;
- a test is not fixed by any change, or appears in two fixes;
- an `app` fix has no `ref`, `line`, or `jira`.

It marks a fix **Needs verification** when:

- confidence is `Likely`;
- a diff removes or loosens an assertion, or skips a test, without a `ticket`;
- the cause is `outdated-test` without a `ticket`;
- a data request contains `<placeholders>`;
- a data request changes shared configuration (DELETE, or PUT/PATCH on policies, rules, specifications, settings, profiles).

Fix the hard errors and rerun. Then read the "needs verification" lines it prints: if more evidence can remove a reason (find the ticket, look up the real id), do it now and rerun.

### Step 6: Share

The report is `$WORK/report.html`, a single self-contained file. Do not restyle it. If your tool can publish an HTML page (for example, Claude Artifacts), publish it; otherwise give the user the file path.

Reply with the link or path and a short summary:

- tests with a Ready fix vs. Needs verification;
- counts by fix type;
- the biggest fixes;
- any environment action someone must take before the next run.

## Scripts

| script | purpose |
|---|---|
| `scripts/fetch_allure.py` | Downloads the summary and every failed or broken test case from the Allure report. |
| `scripts/extract.py` | Finds the root-cause stage, error, history and failing code line of each test; clusters tests by error; writes `dump.md`, `tests.json`, `meta.json`. |
| `scripts/screenshot.py` | Downloads Allure screenshots for given test ids. |
| `scripts/app_repo.sh` | Clones a FOLIO module (blobless) and prints the `ref` to cite. |
| `scripts/ticket.sh` | Lists recent commits and Jira keys that touched a module file or line range. |
| `scripts/render.py` | Validates `analysis.json` and builds `report.html` from `assets/template.html`. |
