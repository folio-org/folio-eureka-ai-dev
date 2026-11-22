---
name: write-karate-first-cases
description: Use when a FOLIO story or bug fix needs API test coverage end to end — writes Karate-first TestRail cases, implements them as Karate features in folio-org/folio-integration-tests following the owning team's conventions, and opens a PR. Also use to automate existing TestRail cases (C-ids) as Karate features. Thin UI (Cypress) cases only for behaviour with no API equivalent.
---

# Karate-first: TestRail cases → Karate feature → pull request

> **Core principle.** A business rule is verified at the API layer. The deliverable is not only a TestRail case: it is the TestRail case **and** the Karate scenario that implements it, mapped 1:1 by the `@C<id>` tag and by step numbers, delivered as a PR to `folio-org/folio-integration-tests`.

> **Second principle.** A test that would also pass on the code *before* the change verifies nothing. Every scenario must be traceable to a line of the fix and must fail without it.

Outputs of one run:

1. TestRail cases (Karate cases + thin UI cases where unavoidable), posted with C-ids.
2. A new or extended `.feature` in the owning team's folder of `folio-integration-tests`, registered in the runner.
3. A PR from the user's fork, ready for review, with reviewer notes.
4. A run summary.

The user can stop after any phase ("cases only", "feature only, no PR"). If the input is a list of existing C-ids, skip Phase 2 and implement those cases.

---

## Phase 0 — Set up

1. **Ticket.** Fetch the Jira issue (summary, description, acceptance criteria, links, comments, Development Team, Fix Version). Follow links to the BE ticket that carries the fix (a "test-only" story often points to it in the description, as MODORDERS-1458 → MODORDERS-1456).
2. **Owning team and module.** Use, in order: the ticket's Development Team; `teams-assignment.json` in `folio-integration-tests`; the `@FolioTest(team = "...", module = "...")` annotation of runner classes. The team decides the folder (`<project>/src/main/resources/<team>/<module>/`) and the conventions.
3. **Repositories (local clones, read with shell tools).**
   - `folio-org/folio-integration-tests` — the test repo. Work in the user's fork (`<user>/folio-integration-tests`); if it does not exist, create it (`gh repo fork folio-org/folio-integration-tests --clone=false`, or ask the user to click *Fork* on GitHub). Branch from the latest upstream `master`.
   - The backend module repo (`folio-org/<module>`) and `folio-org/acq-models` (acquisitions schemas) or the module's `ramls/` / OpenAPI files.
4. **Application context from `write-testrail-cases`** (the sibling skill holds the team's knowledge of each FOLIO app; this skill reuses it instead of rediscovering it):
   - Detect the area with `../write-testrail-cases/references/area-map.md` and read `../write-testrail-cases/references/context/<area>.md`, starting with its `## Changes since …` section. Read every area the story crosses (an orders story that encumbers money also loads `finance.md`; one that pays also loads `invoices.md`).
   - Use from the context file: **Key Business Rules** (scenario candidates and regression risks, Phase 1.5), **Required Capability Sets** (exact names for preconditions, Phase 2.2), the record hierarchy and settings (preconditions and shared-state check), the area's feature sections (for example *Multi-Year Prepayment*), **Known Gaps** (open questions), and the `Sources:` line (the area's TestRail section subtree, Phase 2.3).
   - Freshness: if the file is missing, marked DRAFT, older than 90 days or built for an older release than the story's Fix Version, run the sibling skill's *Lightweight Context Enrichment* for this story and suggest `build-app-context` in the run summary.
   - Also read `../write-testrail-cases/references/house-style.md` (Type, Priority, title conventions per area), `references/writing-rules.md` (preconditions and steps) and `references/examples/<area>.md` when it exists (the verification depth to match).
5. **Coding rules (read in full before Phase 3, from the latest upstream `master`).** Precedence: team rules files → Karate Coding Standards wiki page → `references/karate-standards.md` → this skill.
   - Thunderjet (acquisitions): **both** `acquisitions/ai/ACQ_ORDERS_SYSTEM_PROMPT.md` and `acquisitions/ai/ACQ_CROSS_MODULES_SYSTEM_PROMPT.md`, whatever the module (an orders story often touches finance or invoices), plus `acquisitions/ai/prompt/PROMPT_TEMPLATES.md`. Team map: `references/team-thunderjet.md`.
   - All teams: the FOLIJET wiki page *Karate Coding Standards & Best Practices* (https://folio-org.atlassian.net/wiki/spaces/FOLIJET/pages/114098928). It is from 2024; where it differs from a team rules file, the team file wins (see the known differences in `references/karate-standards.md`).
   - `references/karate-standards.md` — digest of the sources above and of what the team learned while rewriting old tests (FAT-13426, FAT-20199) and restructuring the runners (PR #2426). Read it once per run; open the original PRs when a rule needs an example.
   - Other teams without an `ai/` folder: derive conventions from the 3 most recently changed features in the same folder (`git log -3 --name-only -- <folder>`) and record what you derived in the run summary.
6. **Context map.** Collect these before Phase 1; each one answers a question the skill otherwise guesses. Record in the run summary which were unavailable.

   | Source | What it answers | How |
   |---|---|---|
   | Jira story: description, AC, comments, linked issues, epic siblings | The rule, agreed edge cases, decisions made in comments | Jira MCP; read all comments, not only the description |
   | Fix PR in the module repo: diff **and its unit tests** | Changed code paths; the test names and inputs show the cases the developer had in mind | `git log --grep=<FIX-KEY>` / Jira Development panel |
   | `ErrorCodes.java` (or equivalent) | Exact `code` and message for negative scenarios | module repo |
   | `ModuleDescriptor-template.json`, schemas and examples (`acq-models` for acquisitions) | Endpoints, permissions, field names, enums, valid request bodies | module repo, `folio-org/acq-models` |
   | `samples/` JSON in folio-integration-tests | Request bodies the team already uses | `<project>/src/main/resources/samples/` |
   | Reusable catalog | Which call already does a step, and its parameters | `references/karate-context.py reusables <project>` |
   | Coverage search | Existing scenarios for the same behaviour | `references/karate-context.py coverage <project> <terms>` and `endpoints` |
   | Exemplar features | The current team style to imitate (Background, headers, comments) | `references/karate-context.py exemplars <features folder>`; read the top 2 in full |
   | TestRail: cases with the story/fix key, manual cases in the same section | What QA already checks manually; titles and capability-set wording | TestRail MCP |
   | App context (`write-testrail-cases`) | Business rules, capability sets, settings, known gaps, TestRail sections of the area | `../write-testrail-cases/references/context/<area>.md` (step 4) |
   | Team lessons | Review feedback from earlier runs | `references/lessons.md` |

7. **TestRail and Jira access.** Use the TestRail / Jira MCP tools when present; otherwise the credentials chain in `../write-testrail-cases/SKILL.md` ("TestRail API Integration → Credentials").

---

## Phase 1 — Analyse

### 1.1 Read the fix, not only the story
Find the merged change (Jira "Development" panel, PR links, or `git log --grep=<FIX-KEY>` in the module repo) and read its diff. Write down:
- **Before / after behaviour** per changed code path, in one line each (e.g. *before: approval fields set on every transition to Open; after: set only when empty*).
- **Trigger conditions** — which request, which state transition, which settings make the changed line execute.
- **Error codes** introduced or changed (`ErrorCodes.java` or equivalent: `code` + `message`).

If no fix is found (story not yet implemented), work from the API contract and mark the cases `Contract: not available — placeholder` (see Phase 2).

### 1.2 API surface
From the module repo:
- `descriptors/ModuleDescriptor-template.json` → endpoint `methods` + `pathPattern`, `permissionsRequired`, `permissionsDesired`.
- Schemas → exact field names, enums, `readOnly`, formats.
- Settings the rule depends on and **where they live** (e.g. `/orders-storage/settings` key `approvals`), and whether the module caches them (cache TTL, bypass header such as `x-okapi-bypass-cache`).

### 1.3 Existing coverage (no duplicates)
A new case or scenario that repeats an existing Karate test adds runtime and maintenance and nothing else. Old tests were merged and renamed during the FAT-13426 / FAT-20199 refactoring, so search by behaviour, not by file name (`references/karate-standards.md`, section 8):
- Karate: `python3 references/karate-context.py coverage <project> <term> [<term> ...]` with the endpoint, the changed field, the error code and the state transition (it searches the whole project, `cross-modules/` included, and prints scenario, `@C` tag and runner). Run several term combinations. Open every hit and read the scenario: what it sets up, what triggers, what it asserts.
- Reusable features: every key in `<project>/src/main/resources/karate-config.js` and the `reusable/` folders; read the `# parameters:` header of each one you plan to call.
- TestRail: run the sibling skill's existing-coverage check (`../write-testrail-cases/SKILL.md`, step 4b): `refs` filter for every key, title search in the area's sections. Mark each match **duplicate** / **update** (expected results outdated by the story — propose the change for the `test-case-updater` skill) / **unrelated**. An existing **Karate** case whose `@C` tag is in a feature means the rule is covered.

Decide per rule and show it in the Coverage column of 1.5:
- **covered** — same precondition, same trigger, same asserted outcome: cite feature + scenario + C-id; no new case, no new scenario.
- **extend** — same workflow, missing assertion or variant: add the assertion or a scenario to that feature (team rule: prefer this over a new file); a missing assertion goes into the existing TestRail case as a new expected result, not into a new case.
- **new** — no scenario reaches the changed code path.

The runner must not duplicate either: a feature name is registered in exactly one runner class of the project (PR #2426 structure, Phase 3.3).

### 1.4 Shared-state check (parallel safety)
Features run in parallel in a shared tenant. For each precondition ask: *does it change something tenant-wide?* (order/finance settings, approval requirement, circulation rules, configuration entries, acquisition units used by others). If yes:
1. Prefer a scenario that reaches the changed code path **without** the tenant-wide change (MODORDERS-1458: the fix applies whether or not approval is required, so the setting is left alone).
2. If impossible, the scenario must live in a feature or runner that is not run in parallel with features depending on that setting — say so in the PR and ask the team; never add `@parallel=false` to a new feature.

### 1.5 Scenario analysis (show, then wait for confirmation)

Scenario sources, in this order: the acceptance criteria; the before/after lines of the fix; the **Key Business Rules** of the area context file that the change touches. For each touched rule decide whether the story changes it (new scenario), depends on it (precondition) or risks breaking it (regression scenario, usually Extended). Regression scenarios on existing behaviour are part of the analysis, not an extra.

```
Story: MODORDERS-1458 — fix in MODORDERS-1456 (mod-orders PR #1332)
Before/after: approvalDate/approvedById overwritten on every transition to Open → set only when empty

| # | Scenario | Layer | Fails before fix because | Coverage | Target |
|---|----------|-------|--------------------------|----------|--------|
| 1 | Approval details from first opening survive unopen + open | Karate | 2nd open overwrote both fields | none | new feature, Extended |
| 2 | Approval date set while Pending survives opening; approvedById filled | Karate | open overwrote approvalDate | none | same feature |
| 3 | UI shows initial approval date after reopen | UI | — | C736774 (manual, updated) | not needed |

Shared state: approvals.isApprovalRequired NOT toggled (tenant-wide; fix does not depend on it)
Karate 2 / UI 0
```

Columns are mandatory. A Karate row with an empty "Fails before fix because" is removed or rewritten. Wait for confirmation unless the run is unattended (then state the assumption at the top and continue).

---

## Phase 2 — TestRail cases

### 2.1 Layer decision
Karate by default: the outcome is decidable from HTTP requests/responses (including follow-up GETs, job polling, other modules' APIs). Manual UI case only for UI wiring with no API equivalent (rendering, client-side validation, navigation, UI-only capability hiding, exact UI texts).

Manual UI cases are written by the `write-testrail-cases` workflow (its steps 2, 4, 6–8), reusing the context, story analysis and coverage check already done here — do not repeat them. Its rules apply in full: exact UI texts from the context file, section style, house style, self-review gate. Two additions: a UI case never re-asserts what a Karate case of the same story asserts (it may reference it: "business rule covered by C<id>"), and both kinds go to the same section. These are the cases the developer executes by hand before Done and that a UI developer later automates in Cypress.

### 2.2 Karate case content
TestRail cases are read and reviewed by people (QA, PO, developers), so they are written in **plain business language**. Endpoints, payloads, field paths and error codes live only in the Karate feature; translating the case into requests is the job of Phase 3. Step N in TestRail still equals the `# N.` comment in the feature, so the PR covers exactly what the case says.

- **Title:** the business outcome, sentence case, no "API:" prefix.
- **Preconditions** (`<ol>`):
  1. Tenant settings the rule depends on, in UI terms (Settings > Orders > Approvals...), with values, and an explicit note when a setting is intentionally left at default.
  2. **Capabilities the user needs, as Eureka capability sets** in the team's usual wording (`data - UI-Orders Orders - create`, `procedural - UI-Orders Order Unopen - execute`). Take the names from the context file's *Required Capability Sets* section, then from existing cases of the same section. They document the access a real user needs; the Karate implementation does **not** model them (the test users of the project have a fixed permission set), so do not create per-case users or permission setup in the feature.
  3. Records the case needs, with meaningful values and symbolic names (Fund A with $10,000 budget, Order O in Pending). No reusable names, no UUIDs.
- **Steps:** one business action per step, in the domain's words ("Open Order O", "Unopen Order O, deleting holdings", "Add a PO line with multi-year payment on, prepayment term 2 years, 1 fiscal year distribution"). No URLs, no HTTP methods, no UI clicks.
- **Expected:** the business outcome with exact values ("Order O is rejected with the message that the number of fiscal year distributions must match the prepayment term", "Approval date is the same as after the first opening"). Status codes and error codes are not written in the case; the feature asserts them. Values captured during the run are named (remember as D1) and compared later.
- No UI-only checks (labels, toasts, layout) in a Karate case; those belong to a UI case.

Assertion rules (apply to the case and, more concretely, to the feature):
- A trigger step must be followed by a step that checks the resulting state.
- Assert the state, not the echo: re-read the entity and every related entity (child entities through their own endpoint).
- Negative cases: the case states what is rejected and that nothing changed; the feature asserts the exact status, `errors[*].code` and a GET proving nothing changed.
- **False-pass guard:** for every case answer "would this pass on the pre-fix code, or if the feature ran twice?" If yes, rewrite (add a control record, capture-and-compare, or a state that makes the old behaviour visible).
- Unsourced values are written as `<value> [Qn]` and logged as open questions (see `../write-testrail-cases/SKILL.md`, "Clarifying Questions").

### 2.3 Metadata and posting
- Field formats, HTML rich-text rules, the "AI" label, the posting preview and error handling: follow `../write-testrail-cases/SKILL.md` exactly. **Preconditions and steps are HTML** (`<ol>`, `<ul>`, `<p>`), never plain text or Markdown.
- Karate-specific values (resolve option IDs with `get_case_fields`; IDs below are from foliotest.testrail.io, Nov 2026):
  - Execution Type = Karate (`custom_automation_type` 3)
  - Automation Scope = Karate Approved (`custom_automation_scope` 6)
  - Automated For = current release (`custom_case_automated_in`), only after the PR is opened
  - Test Group = Critical Path for core rules and permissions, Extended for regressions of bug fixes and edge cases — **this also selects the runner class** (Phase 3.3)
  - Dev Team = owning team; Type and Priority per `../write-testrail-cases/references/house-style.md` for the area, overridden by the section sample
  - `refs` = story key + fix key
- Section, chosen by the skill: take the area's section subtree from the context file's `Sources:` line (Orders: 105 and its children), list the subsections with `get_sections`, and pick the one whose name matches the feature; if related cases were found in Phase 1.3, prefer their section. Then sample its 10 most recent cases (sibling skill, step 4) and follow their preconditions format, capability block and title style. Ask only when two subsections fit equally.
- Post after confirmation; collect the C-ids — Phase 3 needs them.

---

## Phase 3 — Implement the Karate feature

### 3.1 Placement and naming
- File: `<project>/src/main/resources/<team>/<module>/features/<name>.feature` (or the existing related feature when extending).
- Name: kebab-case, describes the scenario, **≤ 80 characters** including `.feature` (long names break Karate reports and Windows checkouts). Drop filler words ("correctly", "when", "should").

### 3.2 Writing the feature
Start from the closest exemplar found in Phase 0 (same folder, same kind of workflow): copy its header layout, `Background`, login and headers, then write the scenarios. Pick every call from the reusable catalog. Apply `references/lessons.md`.

Follow the team rules file first; `references/karate-feature-conventions.md` holds the skeleton and the rules that apply when the team has no rules file. The essentials, which must hold in every team:

- Header: `# For <JIRA-KEY>, https://foliotest.testrail.io/index.php?/cases/view/<id>[, …]`, then `Feature:` in Title Case.
- `Background`: `* print karate.info.scenarioName`, `* url baseUrl`, login and headers exactly as neighbouring features do; shared test data only if it is safe for parallel scenarios.
- Every scenario: `@C<id>` on its own line **first**, then `@Positive` / `@Negative`; Title Case scenario name equal to the TestRail title.
- IDs from `call uuid` inside the scenario — never shared between scenarios.
- Step comments `# N. <Title Case Text>` matching TestRail step N; unnumbered `# Prerequisites: …` for precondition setup. No `* print` in scenarios.
- One scenario = one complete workflow (setup, trigger, check); never split dependent steps into separate scenarios. Codes and names that must be unique (fiscal year series, fund codes) come from `call random_string`, not literals.
- Reusable features only by their `karate-config.js` key (`* def v = call createOrder { id: '#(orderId)' }`), with parameters from their `# parameters:` header; never re-`read()` a reusable the config already loads. Do not write raw requests for something a reusable already does; if it lacks one parameter, add it as optional to the reusable and say so in the PR.
- Several similar records: a Karate `table` passed to one reusable call, not `Scenario Outline`.
- Order-independent assertions on collections (`[*]` with `contains`); `contains` on objects that may gain fields.
- `retry until` only to wait for async state; keep all conditions of a wait inside the `retry until` expression, then assert with `match` in a **separate** GET block.
- `match` with `$` right after the request; Karate markers for presence: `'##null'` (absent or null), `'#uuid'`, `'#string'`, `'#notnull'`.
- Admin headers only for modules the user lacks permissions for (team rule); switch with `configure headers`, never at the very end of a scenario.

### 3.3 Registration
- Runner class by Test Group: Critical Path → `*CriticalPathApiTest`, Extended → `*ExtendedApiTest`, otherwise `*ApiTest` (the class whose `TEST_BASE_PATH` points at the module's `features/`). Add the file name (without `.feature`) **at the end** of the `FEATURES` array. Since PR #2426 that array is the only registration in Java: no new `@Test` methods, enums or runner classes, and the name must not appear in any other runner.
- Root feature (`<module>/<module-root>.feature`, e.g. `mod-orders/orders.feature`): append `Scenario: <Feature title>` + `* call read('features/<name>.feature')` at the end.
- Append-only: never insert in the middle, never reorder.

### 3.4 Static validation (mandatory, before committing)
Run and fix until clean (`references/validate-feature.sh` does all of it):
1. Gherkin parses (`pip install gherkin-official`, parse the file).
2. Every reusable key used in the feature exists in `karate-config.js`.
3. File name length ≤ 80; no `* print` in scenarios; no `@parallel=false`; no `Scenario Outline`; no `callonce uuid` or unquoted `#(...)` in call arguments; no `read()` of a reusable already in `karate-config.js`; every scenario has exactly one `@C<id>` that matches a posted case.
4. The feature name appears once in the runner's `FEATURES`, in no other runner of the project, and once in the root feature.
5. Step comments 1..N without gaps and matching the TestRail steps of that case; no `retry until` and `match` in the same request block; no scenario ends with `configure headers`.

Do not run `mvn test` unless the user asks and an environment is available (it needs a FOLIO Eureka environment and takes long). Say in the PR that the test was not executed.

---

## Phase 4 — Pull request

1. Branch `<JIRA-KEY>-<short-slug>` from current upstream `master`; one commit `<JIRA-KEY>: Karate test - <outcome>`.
2. Push to the user's fork. Open a PR **ready for review** to `folio-org/folio-integration-tests:master` (`gh pr create`, or the GitHub compare page with `?expand=1&title=…&body=…` when the API is unavailable). Running the tests is not a merge gate: Karate runs nightly, independent of builds, and a failing test produces a Slack report and a P2 defect that the team fixes. Run locally (or via the Rancher Jenkins job) when the developer can; otherwise say in the PR that it was not executed.
3. PR body (English, business style):
   - **Purpose** — story and fix keys, the rule in one sentence.
   - **Changes** — feature file, each scenario with its `@C` tag, registration (runner + root feature).
   - **Notes for reviewers** — why each scenario fails on the pre-fix code; shared-state decisions; assumptions (`[Qn]`, unverified API behaviour); execution status (run locally / Rancher job link / not executed, will be covered by the nightly run).
   - **TestRail** — case links.
4. Do not request reviewers on the user's behalf; tell the user who usually reviews the folder (recent committers: `git log -5 --format='%an' -- <folder>`).
5. If the user wants it, add the PR link as a comment on the Jira story.
6. **Learn from the review.** When reviewers comment on the PR, apply the fixes and add each comment that is a general rule (not specific to this story) to `references/lessons.md`: the rule, the PR and the reviewer's wording in short. Suggest the same rule to the team for their rules file when it is acquisitions-wide.

---

## Self-review gate (run before showing any case or committing)

- [ ] Every scenario has a "fails before fix because…" reason that matches the fix diff.
- [ ] No tenant-wide setting is changed in a parallel feature, or the PR explains why.
- [ ] TestRail steps and `# N.` comments match 1:1; titles match scenario names.
- [ ] Every assertion is on a business field with an exact or captured value; no step is status-only except triggers.
- [ ] Child entities verified through their own endpoint; cross-module effects verified in the other module.
- [ ] All reusable keys exist; parameters match their headers.
- [ ] No case or scenario repeats an existing Karate test (Coverage column filled with feature + scenario for every "covered" or "extend" row).
- [ ] The area context file(s) were read; every touched Key Business Rule is a scenario, a precondition or explicitly out of scope; capability set names come from the context file.
- [ ] Both Thunderjet rules files and the Karate Coding Standards page were read; every scenario is a complete workflow with its own IDs and unique codes.
- [ ] TestRail fields are HTML and carry the "AI" label; Execution Type = Karate, Automation Scope = Karate Approved.
- [ ] TestRail cases contain no endpoints, HTTP methods, status codes or UI clicks; capabilities are listed as Eureka capability sets; the feature does not model them.
- [ ] Static validation passed; registration is append-only.

## Run summary (always print at the end; keep field names stable)

```
Run summary
Story:            MODORDERS-1458 (fix: MODORDERS-1456, mod-orders #1332)
Team / module:    Thunderjet / mod-orders
Cases:            2 posted (Karate 2 / UI 0): C1621341, C1621342
Existing coverage: C736774 (manual UI, updated by the team) — not duplicated
Feature:          acquisitions/.../mod-orders/features/open-order-approval-details-not-overwritten.feature (2 scenarios)
Registered in:    OrdersExtendedApiTest, orders.feature
PR:               folio-org/folio-integration-tests#2619 (ready for review, not executed; nightly run covers it)
Shared state:     approvals.isApprovalRequired left at default
Open questions:   Q1 — mod-orders keeps client-supplied approvalDate on PUT (scenario 2)
App context:      write-testrail-cases context/orders.md (built 2026-11-07), finance.md
Section:          Orders > <subsection> (chosen from context Sources + section sample)
Rules source:     ACQ_ORDERS_SYSTEM_PROMPT.md, ACQ_CROSS_MODULES_SYSTEM_PROMPT.md, Karate Coding Standards wiki
```

## References
- `references/karate-standards.md` — digest of the Karate Coding Standards wiki page, the FAT-13426 / FAT-20199 refactoring and the PR #2426 runner structure; precedence and known differences.
- `references/karate-context.py` — read-only helper: reusable catalog, coverage search, endpoint index, exemplar features, registration check.
- `references/lessons.md` — rules learned from PR reviews; apply on every run.
- `references/karate-feature-conventions.md` — feature skeleton and conventions for teams without a rules file.
- `references/team-thunderjet.md` — Thunderjet folders, runners, root features, reusables, pitfalls.
- `references/example-modorders-1458.md` — worked example: analysis, TestRail case, feature, PR.
- `references/validate-feature.sh` — static validation script.
- `../write-testrail-cases/SKILL.md` — Manual UI case workflow, existing-coverage check, HTML formatting, metadata, posting, clarifying questions.
- `../write-testrail-cases/references/` — `area-map.md`, `context/<area>.md`, `house-style.md`, `writing-rules.md`, `examples/<area>.md`: application knowledge shared by both skills.
