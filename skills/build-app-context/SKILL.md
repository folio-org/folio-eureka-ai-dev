---
name: build-app-context
description: Use when you need to build or refresh a context file for a FOLIO application area before writing test cases. This skill gathers live data from TestRail (existing cases), GitHub (README, docs, feature files, capability/permission definitions), and Jira (closed stories and bugs for the component), then distills everything into a structured context .md file and saves it to references/context/. Run this skill once per application area, then use write-testrail-cases normally.
license: Apache-2.0
metadata:
  author: folio-org
  version: 1.0.0
---

# Build App Context

Builds or refreshes a `references/context/<area>.md` file by gathering live data from TestRail, GitHub, and Jira. The resulting file is used by the `write-testrail-cases` skill as its primary domain knowledge source.

---

## Credentials

Read credentials using this fallback chain (try in order, stop at first hit):

1. `.env` file in the repository root — parse KEY=VALUE pairs
2. `~/.folio-credentials` — legacy local file
3. Environment variables — for CI/Codespaces

Keys to read:
```
TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_API_KEY
JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN
GITHUB_TOKEN (optional)
```

Never ask the user for credentials — try all three silently. If all three fail — report which keys are missing and stop.

---

## Phase 0 — Interactive Setup

### Phase 0.5 — Auto-resolve module metadata (run before asking questions)

Before presenting questions to the user, silently fetch the FOLIO responsibility matrix:

```
GET https://folio-org.atlassian.net/wiki/spaces/REL/pages/5210256/
    FOLIO+Module+JIRA+project-Team-PO-Dev+Lead+responsibility+matrix
```

Parse the table and build a lookup by area name / module name. For the area the user named (from their trigger message), extract:

| Field | Matrix column | Use for |
|---|---|---|
| `jira_prefix` | JIRA project | Jira JQL filter, area detection table in SKILL.md |
| `team` | Team | `custom_dev_team` default |
| `ui_repo` | Module (rows where module starts with `ui-`) | GitHub Phase 2 |
| `be_repo` | Module (rows where module starts with `mod-`) | GitHub Phase 2 |
| `tests_repo` | Tests repository | GitHub Phase 2 (additional repo) |
| `ecs_scope` | ECS (Central/Member/All)/NonECS/Both | Pre-fill `ECS Enabled` default |
| `eureka_app` | Application Trillium | Context file header |

A single area typically has 2–3 rows (one per module). Collect all matching rows.

If the area name matches multiple distinct teams (e.g. "ERM" is K-Int), note it in the Phase 0 questions.

If the page is not publicly accessible (auth required), skip this step silently and ask the user for repos manually as before.

**After auto-resolving**, skip questions 3 and 4 from the standard setup and show pre-filled values instead:

```
I found the following metadata for "<area>" in the FOLIO module matrix:

  JIRA prefix:    <prefix>
  Team:           <team>
  GitHub repos:   <ui_repo>, <be_repo>
  Tests repo:     <tests_repo> (if present)
  ECS scope:      <Central/Member/All | NonECS | Both>
  Eureka app:     <app name>

I still need from you:

1. TestRail section ID(s) for existing manual cases
   (Find it in the URL: ?/cases/view/14&section_id=XXXXX)

2. Jira component name (if different from "<prefix>") — or leave blank
   to use the JIRA project prefix directly.

3. Releases to focus on [default: Umbrellaleaf, Trillium, Sunflower]:

Confirm or correct the pre-filled values, then I'll start building.
```



**Fallback** (matrix not accessible or area not found) — ask all five questions in one message:

```
I'll build a context file for a FOLIO app area by pulling data from TestRail,
GitHub, and Jira. A few questions:

1. **App area name** — what should the context file be called?
   (e.g. "orders", "data-export", "bulk-edit")

2. **TestRail section ID(s)** — the section(s) containing existing manual
   test cases for this area. You can give one ID or a comma-separated list.
   (Find it in the TestRail URL: ?/cases/view/14&section_id=XXXXX)

3. **GitHub repositories** — which repos cover this area?
   Typically: ui-<name> and mod-<name>. Paste full repo names or URLs.
   (Leave blank to skip GitHub.)

4. **Jira component or epic** — component name or epic key.
   Examples: component = "Orders", epic = "UXPROD-1234"
   (Leave blank to skip Jira.)

5. **Releases to focus on** [default: Umbrellaleaf, Trillium, Sunflower]
```

After the user answers, echo back a one-line confirmation:
> Building context for **<area>** from: TestRail section(s) <IDs> · GitHub: <repos> · Jira: <component/epic>

Then proceed through Phases 1–4 without further interruption.

---

## Phase 1 — Gather: TestRail

### 1.1 Pull existing cases

For each provided section ID, fetch all cases:

```
GET {TESTRAIL_URL}/index.php?/api/v2/get_cases/{project_id}&section_id={id}&limit=250&offset=0
Authorization: Basic base64(TESTRAIL_USER:TESTRAIL_API_KEY)
```

Paginate (increment offset by 250) until `_links.next` is null. Collect all cases across all provided section IDs.

**Fields to extract per case:**
- `id`, `title`, `custom_preconds`, `custom_steps_separated`, `custom_test_group`
- `custom_release`, `custom_ecs_enabled`, `updated_on`
- `refs` (linked Jira IDs)

### 1.2 Determine recency weights

Assign weight to each case based on `custom_release`:

| Release label | Weight |
|---|---|
| Umbrellaleaf (R2 2026) | 1.0 |
| Trillium (R1 2026) | 0.9 |
| Sunflower (R1 2025) | 0.8 |
| Ramsons (R2 2024) | 0.6 |
| Quesnelia (R1 2024) | 0.5 |
| Older / blank | 0.3 |

Use weights when voting on whether a text string is a real current UI element (high-weight occurrences beat low-weight ones).

### 1.3 Extract signals from cases

Process all cases (steps + preconditions as plain text after stripping HTML tags):

**A) Toast messages** — lines matching: `Toast message "..."`, `"..." toast message appears`, `System notifies that "..."`, `success.*"..."`, `"...successfully..."`.
- Canonicalize each extracted text: resolve `<name>`, `<number>`, `<PO number>` placeholders by looking at what fills the slot in the most common variant.
- Keep only strings with weighted frequency ≥ 3 (or top 30 if fewer).

**B) Modal/dialog titles** — phrases matching `"..." modal`, `"..." dialog`, `"..." popup`.
- Keep weighted frequency ≥ 2.

**C) Pane names** — phrases matching `"..." pane`.
- Keep weighted frequency ≥ 3.

**D) Accordion names** — phrases matching `"..." accordion`.
- Keep weighted frequency ≥ 3.

**E) Button labels** — phrases matching `"..." button`, `click "..."`, `select "..."`.
- Keep only those with weighted frequency ≥ 5 AND length ≤ 40 chars (filter out sentence-length matches).

**F) Status values** — phrases matching `status.*"..."`, `"..." status`, `= "..."` adjacent to known status fields (Workflow status, Payment status, Receipt status, Request status, etc.).
- Deduplicate; keep per-field groupings.

**G) Capability Sets** — lines in preconditions matching the pattern `Data - ...`, `Procedural - ...`, `Settings - ...`, `Module - ...`.
- Collect all unique capability set strings; deduplicate exactly.

**H) Verification patterns** — step sequences where action references a field name and expected result contains `=` or `displays` with a value. Capture 3–5 of the most representative multi-step sequences verbatim (these become the "Common Verification Patterns" section).

**I) Navigation paths** — phrases matching `navigate to ... > ... > ...` or `Settings > ... > ...`.
- Collect the 10 most common.

**J) ECS-specific signals** — from cases where `custom_ecs_enabled = true`: extract tenant names used in preconditions (Central, member-1, member-2, etc.), cross-tenant step patterns, affiliation switching steps.

### 1.4 Summarise business rules from case titles

Group case titles by implicit category:
- Titles containing "cannot", "not able", "without permission" → negative / capability boundary rules
- Titles containing "successfully", "can create/edit/delete" → positive rules
- Titles with status words → lifecycle rules

Extract noun phrases that repeat across ≥ 3 titles in the same category — these are implicit business rules. Format as: `"<subject> <verb> <object> when <condition>"`.

---

## Phase 2 — Gather: GitHub

For each provided repository (`owner/repo` format, inferred from URL if full URL given):

### 2.1 Discover relevant files

```
GET https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1
Authorization: Bearer {GITHUB_TOKEN}   (omit header if no token)
```

From the file tree, select files matching these patterns:

| Priority | Pattern | What to extract |
|---|---|---|
| High | `README.md`, `doc/*.md`, `docs/*.md`, `**/CHANGELOG.md` | Feature descriptions, business rules, known limitations |
| High | `**/*.feature`, `**/test/**/*.feature` | Karate/Cucumber scenarios → implied business rules and UI flows |
| Medium | `**/permissions.json`, `**/moduleDescriptor.json`, `**/descriptors/*.json` | Exact capability/permission names and their descriptions |
| Medium | `src/main/resources/swagger.api/*.yaml` or `**/*openapi*.yaml` | API endpoints and schemas (record types, field names) |
| Low | `translations/ui-*/en_US.json`, `translations/ui-*/en.json` | Exact UI label strings keyed by translation key |

Fetch at most **20 files** total, prioritising by the order above. Skip files > 200 KB.

### 2.2 Extract from each file type

**README / doc / CHANGELOG:**
- Pull sections describing features, workflows, limitations, and known issues.
- Note version-specific behaviour ("Since Ramsons", "Deprecated in Sunflower").

**Feature files (.feature):**
- Extract scenario titles (lines starting with `Scenario:` or `Scenario Outline:`).
- Extract Given/When/Then steps that describe UI interactions or business assertions.
- Map Cucumber steps to implied UI texts (e.g. `And I should see "..." label` → UI string candidate).

**moduleDescriptor.json / permissions.json:**
- Extract all `"permissionName"` or `"id"` values under `"provides"` / `"permissionSets"`.
- Map legacy permission names to Eureka Capability Set equivalents where the mapping is explicit in the file (look for `"replaces"` or `"eureka"` keys).
- If no mapping found, flag as `(verify Capability Set name — legacy permission: <name>)`.

**en_US.json / en.json (translations):**
- Extract values (not keys) for entries whose keys contain: `modal`, `button`, `label`, `toast`, `message`, `title`, `header`, `pane`, `accordion`, `action`, `success`, `error`, `confirm`.
- These are the exact UI strings rendered in the interface — highest reliability for UI text extraction.

### 2.3 Reconcile GitHub strings with TestRail strings

For each UI text extracted from translations or feature files, check if it also appeared in TestRail cases (Phase 1 extractions). If both sources agree → mark as **[confirmed]**. If only GitHub → mark as **[from source, verify in env]**. If only TestRail (weighted freq ≥ 5) → mark as **[from cases]**.

---

## Phase 3 — Gather: Jira

### 3.1 Pull closed stories

```
POST {JIRA_BASE_URL}/rest/api/3/issue/search
Authorization: Basic base64(JIRA_USER_EMAIL:JIRA_API_TOKEN)
Content-Type: application/json

{
  "jql": "project = FOLIO AND component = \"<component>\" AND issuetype in (Story, \"New Feature\") AND status = Done ORDER BY updated DESC",
  "maxResults": 100,
  "fields": ["summary", "description", "customfield_10014", "fixVersions", "labels", "status", "issuetype"]
}
```

If the user gave an epic key instead of a component, use:
```
"jql": "\"Epic Link\" = <epic_key> AND issuetype in (Story) AND status = Done ORDER BY updated DESC"
```

Paginate with `startAt` until all results collected (up to 500 stories; stop earlier if results go older than 2 years).

### 3.2 Pull bugs

```
POST {JIRA_BASE_URL}/rest/api/3/issue/search
Authorization: Basic base64(JIRA_USER_EMAIL:JIRA_API_TOKEN)
Content-Type: application/json

{
  "jql": "project = FOLIO AND component = \"<component>\" AND issuetype = Bug AND status = Done ORDER BY updated DESC",
  "maxResults": 100,
  "fields": ["summary", "description", "fixVersions", "labels"]
}
```

Paginate with `startAt` until all results collected, then keep the latest 100 bugs for distillation.

### 3.3 Extract from stories and bugs

**From story descriptions:**
- Pull Acceptance Criteria sections (look for `h3. Acceptance Criteria`, `*Acceptance Criteria*`, or `**Scenarios:**` headings).
- Each acceptance criterion → candidate business rule.

**From story summaries:**
- Group by verb ("View", "Create", "Edit", "Delete", "Share", "Export", "Import", "Open", "Close", "Cancel", "Approve", "Reorder", etc.).
- Build a capability map: `"User can <verb> <object> [when <condition>]"`.

**From bug summaries:**
- Bugs describe what should NOT happen or edge cases that need protection.
- Format as negative/edge-case business rules: `"<object> must not <behaviour> when <condition>"` or `"<action> should fail when <condition>"`.

**From fix versions:**
- Note which FOLIO release (flower name) each story/bug targets — use to date-stamp business rules.

---

## Phase 4 — Distill: Build the Context File

Assemble the collected signals into a structured markdown file. Use the template below. Fill every section; mark gaps explicitly rather than omitting them.

```markdown
# FOLIO <Area Name> App — Business Logic Context

> Generated by the `build-app-context` skill on <date>.
> Sources: TestRail section(s) <IDs> (<N> cases, releases <range>)
>          GitHub: <repos>
>          Jira: component/epic <name> (<N> stories, <N> bugs)
> Strings marked [confirmed] appear in both GitHub translations and TestRail cases.
> Strings marked [from source] come from GitHub only — verify in env before asserting.
> Strings marked [from cases] come from TestRail cases (weighted freq shown).

---

## What is <Area>

<2–4 sentences from README / story descriptions. What problem does this app solve? Who uses it?>

---

## Key Terms

| Term | Definition |
|---|---|
| <term> | <definition> |

---

## Record Hierarchy / Architecture

<ASCII diagram or bullet tree showing the main entities and their relationships.>

---

## Lifecycle / Workflow

<Status transitions as ASCII flow or table. Include all statuses and transitions found in cases/stories.>

| Status | Description |
|---|---|

---

## Main Sections / UI Structure

### Panes
<Bulleted list from Phase 1D extraction, [confirmed] or [from cases] tags.>

### Accordions
<Bulleted list from Phase 1D extraction.>

### Key Navigation Paths
<List from Phase 1I, format: `App > Section > Subsection`.>

---

## Exact UI Texts

> Use these verbatim in expected results. Never paraphrase.

### Toast Messages

| Event | Toast text | Source |
|---|---|---|
| <event> | `<exact text with <placeholders>>` | [confirmed] / [from cases (N)] / [from source] |

### Modal / Dialog Titles

| Modal | Trigger | Source |
|---|---|---|
| `<title>` | <what opens it> | [confirmed] / [from cases (N)] |

### Button Labels (key actions)
<Comma-separated list of confirmed button label strings.>

### Error / Warning Messages

| Condition | Message text | Source |
|---|---|---|

---

## Status Values

### <Field name (e.g. Workflow Status)>
<value1>, <value2>, ...

### <Field name (e.g. Payment Status)>
<value1>, <value2>, ...

---

## Capability Sets (Eureka)

> Extracted from TestRail preconditions. Legacy permission names (if found) shown for reference only — never use them in new test cases.

| Action | Capability Set |
|---|---|
| <action> | `<Data / Procedural / Settings / Module - Module Name Resource - Action>` |

<If legacy names found but no Eureka mapping confirmed:>
> ⚠️ The following legacy permission names appeared in older cases — Eureka Capability Set equivalents not yet confirmed; verify before use:
> - `<legacy permission name>`

---

## Common Verification Patterns

> Copy these into expected results. They reflect how the team actually writes assertions for this area.

### <Pattern name (e.g. Fund distribution verification after status change)>

```
Action:   <step>
Expected: <expected with exact field names and values>
```

<Repeat for 3–5 patterns extracted from Phase 1H.>

---

## ECS / Multi-Tenant Notes

<Only if ECS cases found in Phase 1J. Describe tenant setup, cross-tenant flows, and which steps require affiliation switching. Otherwise write: "No ECS-specific test cases found in this section.">

---

## Key Business Rules for Test Cases

> Numbered list. Every rule is either confirmed by ≥3 test case titles, an acceptance criterion from Jira, or a finding from a bug fix story.
> Source tagged in parentheses: (cases), (jira), (github), (cases + jira).

1. <rule> (<source>)
2. <rule> (<source>)
...

---

## Known Gaps / Items to Verify

> Strings or rules that could not be confirmed from two independent sources. Verify in env before relying on them in test cases.

- [ ] <string or rule> — found only in <source>
```

---

## Phase 5 — Save and Report

### Save the file

Write the distilled context to:
```
write-testrail-cases/references/context/<area>.md
```

IMPORTANT: The only valid output path is inside the
write-testrail-cases skill directory. If the agent is
running from the repo root, the full relative path is:
write-testrail-cases/references/context/<area>.md
Never write to references/context/ at the repo root.

If the file already exists, overwrite it and note the previous version date in the header.

### Update the area detection table in SKILL.md

Open `SKILL.md` and find the area detection table. If the area already has a row, update the Jira prefixes/keywords column. If it's a new area, add a row:

```
| <Area Name> | `references/context/<area>.md` | <Jira prefixes>; "<keywords from story summaries>" |
```

### Report to the user

```
✅ Context file built: references/context/<area>.md

Summary:
  TestRail: <N> cases processed (<N> recent, <N> older)
  GitHub:   <N> files read from <repos>
  Jira:     <N> stories + <N> bugs processed

Extracted:
  Toast messages:         <N> (confirmed: <N>, from cases only: <N>)
  Modal titles:           <N>
  Capability Sets:        <N> unique
  Business rules:         <N>
  Verification patterns:  <N>

⚠️  Items needing env verification: <N> (listed in "Known Gaps" section)

The context file is ready. You can now run write-testrail-cases for <area>.
```

---

## Error Handling

| Situation | Action |
|---|---|
| TestRail section returns 0 cases | Warn: "Section <ID> returned no cases — check the section ID and project access." Still proceed with GitHub and Jira. |
| GitHub rate limit hit (403) | If no token: ask user to add `GITHUB_TOKEN` to `~/.folio-credentials`. If token present: wait 60s and retry once. |
| GitHub repo not found (404) | Skip that repo, note in report: "Repo <name> not found or not accessible." |
| Jira component returns 0 results | Try without `component` filter using only the project key. If still 0, warn and skip. |
| Jira v2 returns empty results | Switch to `/rest/api/3/` — v2 is deprecated in this environment. |
| Jira API returns 401 | Report credentials error for `JIRA_API_TOKEN`. |
| File > 200 KB on GitHub | Skip and note filename in report. |
| Translation file missing | Note "No translation file found — UI texts rely on TestRail cases and feature files only." |
| Resulting context file > 400 lines | Trim the Verification Patterns section to the 3 most representative patterns; trim Toast and Modal tables to top 20 each by weighted frequency. Context files must stay readable — quality over quantity. |

---

## Known Jira Access Limitations

The following Jira projects are confirmed inaccessible with the
current API token (all queries return 0 results):

| Area | Jira projects | Workaround |
|---|---|---|
| OAI-PMH | MODOAIPMH, UIOAIPMH, EDGOAIPMH | Skip Phase 3 |
| MARC Authority | UIMARCAUTH, MODELINKS | Skip Phase 3 |
| Licenses | ERM | Skip Phase 3 |
| Agreements | ERM | Skip Phase 3 |
| eHoldings | ERM | Skip Phase 3 |

For these areas: run Phase 1 (TestRail) + Phase 2 (GitHub) only.
Do not retry Phase 3 — log "Jira inaccessible" in context file
header and proceed without Jira signals.

---

## Refresh Mode

If the user says "refresh" or "update context for <area>" and the file already exists:

1. Pull only cases updated since the file's generation date (use TestRail `updated_after` filter).
2. Pull only Jira issues updated in the last 90 days.
3. Fetch GitHub only if the user explicitly says "also refresh GitHub".
4. Merge new signals with existing ones: new toasts/modals are added, old ones with no recent case support are moved to "Known Gaps".
5. Update the generation date in the file header.
6. Report: "Refreshed <area>.md: +<N> new signals, <N> items moved to Known Gaps."

---

## Quick Reference

```
Trigger:    "build context for <area>" / "update context for <area>"
Inputs:     Area name, TestRail section IDs, GitHub repos, Jira component/epic
Outputs:    references/context/<area>.md  +  updated area detection row in SKILL.md
Reads:      ~/.folio-credentials
Runtime:    ~2–5 min per area (depends on case count and GitHub file count)
```
