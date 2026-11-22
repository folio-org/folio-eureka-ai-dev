---
name: write-karate-first-cases
description: Use when a FOLIO story or bug fix of any team needs test coverage with a Karate focus — classifies every requirement (Karate, Manual, Split, already covered, extend existing), writes the TestRail cases, implements the API-verifiable ones as Karate features in folio-org/folio-integration-tests following the owning team's conventions, validates them and opens a PR; Manual cases go through write-testrail-cases. Also use to automate existing TestRail cases (C-ids) as Karate features.
---

# Karate-first coverage: requirements → TestRail cases → Karate features → pull request

> **Karate is the focus, not the limit.** Every acceptance criterion, every changed code path and every business rule the change touches gets a conscious decision: **Karate** (the API can decide it), **Manual** (it needs a UI, a person or an external system), **Split** (Karate for the rule, Manual for its UI part), **Covered** (an existing test already does it) or **Extend** (an existing test should be extended). Nothing is dropped; nothing is generated to raise a count. QA stays in the process: who executes Manual cases is the team's decision.

> **Evidence over assumption.** Expected behaviour comes from code, contract, acceptance criteria or agreed comments — never from an endpoint name or general knowledge. A test that would also pass on the code before the change verifies nothing; never claim it fails before the fix unless that was demonstrated or the diff shows it.

> **Any team.** Folders, runners, registration, reusables and rules are discovered per project. Saved team profiles are examples, not templates; one team's rules never become global.

Outputs of one run: a coverage matrix, TestRail cases with C-ids (Karate and Manual), a new or extended feature registered the project's way, a validated PR ready for review, and a run summary. The user can stop after any phase ("analysis only", "cases only", "no PR"). With a list of existing C-ids as input, skip Phase 3 and automate those cases.

## Responsibilities of the two skills

| `write-testrail-cases` (sibling, `../write-testrail-cases/`) | `write-karate-first-cases` (this skill) |
|---|---|
| Application knowledge: `area-map.md`, `context/<area>.md` (business rules, capability sets, settings, TestRail sections), freshness and enrichment | Automation strategy and the coverage matrix (Karate / Manual / Split / Covered / Extend) |
| TestRail conventions: `house-style.md`, `writing-rules.md`, `examples/`, `testrail-api.md` (fields, HTML, posting) | Existing automation discovery (`karate-context.py`) |
| Manual case quality and its self-review gate | Karate standards, implementation, registration, validation |
| Existing-case check in TestRail (duplicate / update / unrelated) | Integration: Karate and Manual cases of one story are consistent and not overlapping |

This skill reads the sibling's files and runs its workflow for Manual cases; it never re-implements them. Install both.

---

## Phase 0 — Discovery

1. **Access check.** Note which of Jira (folio-org and/or EBSCO), GitHub, TestRail and local clones are available. Use the matrix below; never fill a gap by guessing.

   | Missing | Effect | What to do |
   |---|---|---|
   | Jira | No AC, comments, links | Ask the user to paste the story and its comments; analysis confidence at most M |
   | GitHub API | No PR metadata or review comments | Use local clones and `git log --grep=<KEY>`; read review comments in the browser if available |
   | Module repo / fix not found | No diff, no unit tests | Cases from contract and AC only; every pre-fix failure is `unknown`; mandatory QA review |
   | TestRail | No existing-case check, no posting | Generate cases in the sibling's Fallback Output format; say the duplicate check was not done |
   | `folio-integration-tests` clone | No coverage or registration discovery | Stop before Phase 4; deliver analysis and cases only |

2. **Story, team, module, project.** Fetch the issue (summary, description, AC, Development Team, Fix Version, labels). Find the module, the owning team (Development Team → `teams-assignment.json` → `@FolioTest(team, module)` on runners) and the project folder that holds the module's features.
3. **Team profile.** `python3 references/karate-context.py profile <project>`: runners with team and base path, registration style, root and init features, reusable folders, `karate-config.js` keys, rules files. If `references/team-<team>.md` exists, read it and re-check it against the output (the repository wins). If not, offer at the end of the run to save one, built only from what `profile`, exemplars and rules files showed.
4. **Repositories.** Work in local clones: the user's fork of `folio-org/folio-integration-tests` (create it if missing; branch from the latest upstream `master`), the module repo, and its contract repo when it has one (`ramls/`, OpenAPI, or a shared models repo such as `folio-org/acq-models`).

## Phase 1 — Context collection

Collect before analysing. Record each source as used, unavailable or not applicable in the run summary.

| Source | What it gives | How |
|---|---|---|
| Story: description, AC, **all comments**, linked bugs/stories, parent epic and its children | The rule, clarifications that change it, decisions, related behaviour | Jira MCP; comments often override the description |
| Fix PR: diff and surrounding code | Changed paths, trigger conditions, before/after behaviour | Jira Development panel, PR links, `git log --grep=<FIX-KEY>` in the module repo |
| **Unit tests of the fix PR** | Edge cases and inputs the developer had in mind; expected outputs | Same diff; list each test name with what it asserts |
| Error codes, validation, permissions | Exact `code` and message; `permissionsRequired`; status transitions | `ErrorCodes.java` (or equivalent), `ModuleDescriptor-template.json`, schemas |
| Related history | Earlier changes to the same code and their tests; review comments | `git log -- <file>` in the module repo; PR pages when accessible |
| Application context | Key Business Rules, Required Capability Sets, settings, Known Gaps, TestRail sections | `../write-testrail-cases/references/area-map.md` → `context/<area>.md` for every area the story crosses; read `## Changes since …` first |
| Existing Karate coverage | Scenarios already exercising the same endpoint, field, code or workflow | `karate-context.py coverage` (Phase 2) |
| Reusables | What already exists and its parameters | `karate-context.py reusables <project>` |
| Exemplar features | Local style (Background, login, headers, comments) | `karate-context.py exemplars <features folder>`; read the top 2 |
| Coding rules | Team rules files → Karate Coding Standards wiki → `references/karate-standards.md` | `<project>/ai/*.md` (all of them); wiki page 114098928; digest |
| TestRail | Cases with the story/fix keys; manual cases of the area | Sibling skill, step 4b |
| Lessons | Rules learned from reviews | `references/lessons.md` (entries of matching scope) |

**Stale or missing application context** (no file, DRAFT, older than 90 days, built for an older release than the Fix Version): run the sibling's *Lightweight Context Enrichment* for this story; if it still lacks the touched rules, say so, lower confidence and suggest `build-app-context`. Never fill the gap from general knowledge.

**Token economy.** Read the diff and the touched files, not whole repositories; use `karate-context.py` instead of reading features one by one (its index is cached per git HEAD); open only the scenarios that `coverage` ranks highest.

## Phase 2 — Requirement analysis

Build the coverage matrix described in `references/analysis.md` (columns, decision rules, evidence levels, confidence, QA-review triggers, example).

1. **Requirements.** One row per AC, per before/after line of the fix, per touched Key Business Rule (changed → scenario, depended on → precondition, at risk → regression row). For each, consider positive, relevant negative and boundary cases, missing permission, invalid data, status transitions and effects in other modules — only where the code or requirement distinguishes them.
2. **Contradictions and gaps.** Compare AC, comments, diff and unit tests. Every disagreement or unsourced value becomes an open question `Qn`; the row keeps evidence `A` until answered.
3. **Existing coverage.** For every row: `karate-context.py coverage <projects> --endpoint "<METHOD> <path>" --field <f> --code <c> --reusable <key>` over all projects the story touches. Reusable calls are expanded, so differently named scenarios are found by what they do. Open each top hit and compare precondition, trigger and asserted outcome → `Covered` or `Extend`. Run the sibling's TestRail check for the same rows.
4. **Shared state.** For every precondition ask whether it changes something tenant-wide (settings, rules, configuration, shared global records). Prefer a path to the changed code that does not need it; if impossible, say so and ask the team; never add `@parallel=false`.
5. **Decision** per row (Karate / Manual / Split / Covered / Extend), pre-fix failure evidence, confidence, QA review flag.

Show the matrix and wait for confirmation unless the run is unattended (then state the assumptions at the top and continue). A Karate row whose pre-fix failure is `unknown` stays only if it guards a requirement that has no other coverage; say so.

## Phase 3 — TestRail cases

1. **Section.** Chosen by the skill: the area's section subtree from the context file's `Sources:` line, `get_sections`, the subsection whose name matches the feature; prefer the section of related cases found in Phase 2. Sample its 10 most recent cases (sibling step 4) for preconditions format, capability block and title style. Ask only when two subsections fit equally.
2. **Karate cases** — plain business language (read by QA, PO, developers):
   - Title: the business outcome. Preconditions (HTML): settings in UI terms with values; capabilities as Eureka capability sets from the context file's *Required Capability Sets*; records with symbolic names and meaningful values. No UUIDs, reusable names or endpoints.
   - Steps: one business action each. Expected: the business outcome with exact values; captured values named (remember as D1). No status codes, payloads or UI clicks; the feature asserts those. Step N = comment `# N.` in the feature.
   - A trigger step is followed by a check of the resulting state; negative cases state what is rejected and that nothing changed.
   - Metadata: Execution Type = Karate, Automation Scope = Karate Approved, Test Group (Critical Path for core rules and permissions, Extended for regressions and edge cases), Dev Team, Type/Priority per `house-style.md` and the section sample, `refs` = story + fix keys, label "AI". Field IDs, HTML rules and posting: `../write-testrail-cases/references/testrail-api.md`.
3. **Manual cases** — run the sibling workflow (its steps 2, 4, 6–8) on the Manual and Split rows, reusing the context, matrix and coverage check from Phases 1–2. Its rules apply in full (exact UI texts, section style, self-review gate). A Manual case of a Split row references the Karate case ("business rule verified by C<id>") instead of re-checking the rule. Same section as the Karate cases; Execution Type = Manual.
4. **Covered / Extend rows** — Covered: nothing new. Extend: add the expected result to the existing case (propose the change for the `test-case-updater` skill when the case belongs to another team). Never create a parallel case.
5. Show the posting preview, post after confirmation, collect the C-ids.

## Phase 4 — Karate implementation

1. **Placement.** The features folder the profile shows for the module, or the existing feature for Extend rows. File name: kebab-case, describes the rule, ≤ 80 characters with `.feature`.
2. **Write from the closest exemplar** of the folder (header layout, `Background`, login, headers), then apply `references/karate-standards.md` (rules with their scope), the team rules files and the lessons. The skeleton and the case-to-scenario mapping are in `references/karate-feature-conventions.md`.
   - Header `# For <JIRA-KEY>, <TestRail URLs>`; per scenario `@C<id>` first, then `@Positive` / `@Negative`; scenario name = case title; `# N.` comments = TestRail steps; `# Prerequisites:` for setup.
   - One complete workflow per scenario; IDs from `call uuid` and unique codes from `call random_string` inside it; no shared mutable data.
   - Reusables before raw requests, with every documented parameter passed explicitly; missing parameter → add it to the reusable as optional and say so in the PR.
   - Tables instead of Scenario Outline; `retry until` on async state; assertions on business fields with exact or captured values; order-independent collection checks; negative cases assert status, error code and that nothing changed.
3. **Register** the project's way (`profile` names the style; all styles are in `karate-standards.md`): append to the `FEATURES` array of the runner chosen by Test Group, or add a `@Test` method like its neighbours (`runFeatureTest(...)`, `feature("classpath:…").run()`, or enum entry + method in older runners), or a call at the end of the root feature — or both array and root feature where the project uses both. A feature runs from exactly one place.
4. Never modify unrelated features, historical tests or production code to make validation pass.

## Phase 5 — Validation

1. **Static and semantic checks** — `python3 references/validate-feature.py <feature> [--runner <Runner.java>] [--root <root.feature>] [--changed-only]` (`--changed-only` when extending an existing feature). Fix every ERROR; fix or explain every WARN in the PR; INFO is advice. It checks Gherkin, `@C` tags and header links, step numbering, reusable existence and required parameters, UUID generation and shared Background data, hard-coded IDs and codes, Scenario Outline, retry and assertion patterns, status after each request, scenarios without business assertions, and registration (once, in the right place, not twice). Team rules are errors only where the team's rules files state them.
2. **Coverage check** — every matrix row has its case(s); every Karate case has exactly one scenario with its `@C` tag; TestRail steps and `# N.` comments match; no new scenario repeats a `Covered` row (re-run `karate-context.py coverage` with the new scenario's endpoint and fields: only the new scenario should assert that outcome).
3. **Self-review** — for every scenario answer, and fix or report what fails:
   1. Which requirement row does it verify?
   2. Is each expected value backed by code, contract, AC or an agreed comment (evidence F)?
   3. Would it detect a regression of that rule (would a plausible wrong implementation fail it)?
   4. Pre-fix failure: demonstrated, shown by the diff, or unknown — stated as such?
   5. Is the same behaviour asserted elsewhere?
   6. Could an existing reusable shorten it?
   7. Independent, repeatable, safe in parallel?
   8. Are the assertions on business outcomes, not only status codes?
   9. Would a maintainer understand it from the comments and names?
   10. Does it follow the target team's actual conventions (exemplar, rules files)?
4. **Pre-fix demonstration** (optional, when an environment with the pre-fix module version is available): run the scenario there and record `demonstrated` in the matrix. Otherwise keep `by diff` or `unknown`. Do not run `mvn test` without an environment and the user's go-ahead.

## Phase 6 — Delivery

1. Branch `<JIRA-KEY>-<short-slug>` from upstream `master`; one commit `<JIRA-KEY>: Karate test - <outcome>`; push to the user's fork; open a PR **ready for review** (`gh pr create`, or the compare page with `?expand=1&title=…&body=…`). Running the tests is not a merge gate where the team relies on nightly runs; state the execution status.
2. PR body (English): **Purpose** (story, fix, rule); **Changes** (features, scenarios with `@C` tags, registration, reusable changes); **Coverage** (matrix summary: generated, reused or extended, Manual cases); **Notes for reviewers** (pre-fix evidence per scenario, shared-state decisions, open questions, validator warnings kept and why, execution status); **TestRail** links.
3. Do not request reviewers; name the usual reviewers (`git log -5 --format='%an' -- <folder>`). Offer to link the PR in the Jira story.
4. **After review**: apply fixes; record general rules in `references/lessons.md` following its entry rules (scope, status, rationale, no duplicates). Offer to save a new team profile.

## Run summary (always print; keep field names stable)

```
Run summary
Story:             MODORDERS-1458 (fix: MODORDERS-1456, mod-orders #1332)
Team / project:    Thunderjet / acquisitions (registration: FEATURES array + root feature)
Context:           Jira ok (5 comments); fix diff ok; unit tests 3; app context orders.md (2026-11-07); TestRail ok
Coverage matrix:   3 rows - Karate 2, Manual 0, Split 0, Covered 1 (C736774), Extend 0
Cases:             posted C1621341, C1621342 (Karate); no Manual cases needed
Feature:           mod-orders/features/open-order-approval-details-not-overwritten.feature (2 scenarios, new)
Registered in:     OrdersExtendedApiTest, mod-orders/orders.feature
Validation:        0 errors, 0 warnings
Pre-fix evidence:  by diff 2, demonstrated 0
Confidence:        H (all rows F)
QA review:         not required
Open questions:    Q1 - mod-orders keeps a client-supplied approvalDate on PUT (row R2)
PR:                folio-org/folio-integration-tests#2619 (ready for review, not executed; nightly run covers it)
Rules:             acquisitions/ai/* + Karate Coding Standards; profile team-thunderjet.md (checked)
```

## References
- `references/analysis.md` — coverage matrix, decision rules, evidence and confidence levels, mandatory QA review triggers.
- `references/karate-standards.md` — rules with scope (all teams / one team), source precedence, registration styles, duplicate search.
- `references/karate-feature-conventions.md` — feature skeleton and TestRail-to-scenario mapping.
- `references/karate-context.py` — read-only helper: `profile`, `reusables`, `coverage`, `endpoints`, `exemplars`, `registered`, `scenario`, `check-calls`.
- `references/validate-feature.py` (and the `validate-feature.sh` wrapper) — validation with ERROR / WARN / INFO levels.
- `references/lessons.md` — rules learned from reviews, with scope, status and rationale.
- `references/team-thunderjet.md` — saved team profile (example).
- `references/example-modorders-1458.md` — worked example.
- `../write-testrail-cases/` — application context, TestRail conventions, Manual case workflow.
