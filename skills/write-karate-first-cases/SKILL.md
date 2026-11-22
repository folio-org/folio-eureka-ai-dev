---
name: write-karate-first-cases
description: Use when a FOLIO story or bug fix of any team needs test coverage with a Karate focus — writes TestRail cases, implements the API-verifiable ones as Karate features in folio-org/folio-integration-tests following the owning team's conventions, opens a PR, and writes Manual cases (via write-testrail-cases) for everything Karate cannot verify. Also use to automate existing TestRail cases (C-ids) as Karate features.
---

# Karate-first: TestRail cases → Karate feature → pull request

> **Core principle.** A business rule is verified at the API layer. The deliverable is not only a TestRail case: it is the TestRail case **and** the Karate scenario that implements it, mapped 1:1 by the `@C<id>` tag and by step numbers, delivered as a PR to `folio-org/folio-integration-tests`.

> **Second principle.** A test that would also pass on the code *before* the change verifies nothing. Every scenario must be traceable to a line of the fix and must fail without it.

> **Third principle.** Karate is the focus, not the limit. Every acceptance criterion and every touched business rule ends up covered: by a Karate case when the API can decide it, otherwise by a Manual case. Nothing is dropped because Karate cannot reach it. Who executes Manual cases (developer, QA) is the team's process, not this skill's decision.

The skill works for every team in `folio-integration-tests`. Team-specific facts (folders, runners, registration style, rules files, reusables) are discovered in Phase 0, not assumed.

Outputs of one run:

1. TestRail cases, posted with C-ids: Karate cases for everything the API can decide, Manual cases for the rest.
2. A new or extended `.feature` in the owning team's folder of `folio-integration-tests`, registered the way that project registers features.
3. A PR from the user's fork, ready for review, with reviewer notes.
4. A run summary.

The user can stop after any phase ("cases only", "feature only, no PR"). If the input is a list of existing C-ids, skip Phase 2 and implement those cases.

---

## Phase 0 — Set up

1. **Ticket.** Fetch the Jira issue (summary, description, acceptance criteria, links, comments, Development Team, Fix Version). Follow links to the BE ticket that carries the fix (a "test-only" story often points to it in the description, as MODORDERS-1458 → MODORDERS-1456).
2. **Owning team, module and team profile.** Find the team from, in order: the ticket's Development Team; `teams-assignment.json` in `folio-integration-tests`; the `@FolioTest(team = "...", module = "...")` annotation of runner classes. Find the project (Maven module folder) that holds the module's features, then build the **team profile**:
   - `python3 references/karate-context.py profile <project>` prints the runners with their team and base path, the **registration style** (FEATURES array, one `@Test` per feature, or root features), root and init features, reusable folders, the `karate-config.js` keys and the team's rules files.
   - If `references/team-<team>.md` exists (for example `team-thunderjet.md`), read it: it is a saved profile with pitfalls. Re-check it against the `profile` output; the repository wins.
   - If there is no saved profile, note the profile in the run summary and offer to save it as `references/team-<team>.md` after the run.
3. **Repositories (local clones, read with shell tools).**
   - `folio-org/folio-integration-tests` — the test repo. Work in the user's fork (`<user>/folio-integration-tests`); if it does not exist, create it (`gh repo fork folio-org/folio-integration-tests --clone=false`, or ask the user to click *Fork* on GitHub). Branch from the latest upstream `master`.
   - The backend module repo (`folio-org/<module>`) and its API contract: `ramls/` or OpenAPI files, or the shared models repo when the module uses one (acquisitions: `folio-org/acq-models`).
4. **Application context from `write-testrail-cases`** (the sibling skill holds the team's knowledge of each FOLIO app; this skill reuses it instead of rediscovering it):
   - Detect the area with `../write-testrail-cases/references/area-map.md` and read `../write-testrail-cases/references/context/<area>.md`, starting with its `## Changes since …` section. Read every area the story crosses (an orders story that encumbers money also loads `finance.md`; one that pays also loads `invoices.md`).
   - Use from the context file: **Key Business Rules** (scenario candidates and regression risks, Phase 1.5), **Required Capability Sets** (exact names for preconditions, Phase 2.2), the record hierarchy and settings (preconditions and shared-state check), the area's feature sections (for example *Multi-Year Prepayment*), **Known Gaps** (open questions), and the `Sources:` line (the area's TestRail section subtree, Phase 2.3).
   - Freshness: if the file is missing, marked DRAFT, older than 90 days or built for an older release than the story's Fix Version, run the sibling skill's *Lightweight Context Enrichment* for this story and suggest `build-app-context` in the run summary.
   - Also read `../write-testrail-cases/references/house-style.md` (Type, Priority, title conventions per area), `references/writing-rules.md` (preconditions and steps) and `references/examples/<area>.md` when it exists (the verification depth to match).
5. **Coding rules (read in full before Phase 3, from the latest upstream `master`).** Precedence: the team's rules files → Karate Coding Standards wiki page → `references/karate-standards.md` → exemplar features of the folder → this skill.
   - Team rules files: every `.md` under `<project>/ai/` (listed by `profile`). Read all of them, not only the one named after the module: rules overlap across modules. Example: acquisitions has `ACQ_ORDERS_SYSTEM_PROMPT.md`, `ACQ_CROSS_MODULES_SYSTEM_PROMPT.md` and `prompt/PROMPT_TEMPLATES.md`.
   - All teams: the FOLIJET wiki page *Karate Coding Standards & Best Practices* (https://folio-org.atlassian.net/wiki/spaces/FOLIJET/pages/114098928). It is from 2024; where it differs from a team rules file, the team file wins (see the known differences in `references/karate-standards.md`).
   - `references/karate-standards.md` — digest of the wiki page and of what teams learned while rewriting old tests (FAT-13426, FAT-20199) and restructuring runners (PR #2426). It applies to every team; read it once per run.
   - Teams without an `ai/` folder: the wiki page and the digest are the rules; the 2 best exemplar features of the folder (`karate-context.py exemplars`) show the local style (Background, login, headers). Record what you derived in the run summary.
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
   | Team profile | Folders, runners, registration style, root features, rules files | `references/karate-context.py profile <project>` (step 2) |
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
A new case or scenario that repeats an existing Karate test adds runtime and maintenance and nothing else. Tests get merged and renamed over time (acquisitions: the FAT-13426 / FAT-20199 refactoring), so search by behaviour, not by file name (`references/karate-standards.md`, section 8):
- Karate: `python3 references/karate-context.py coverage <project> <term> [<term> ...]` with the endpoint, the changed field, the error code and the state transition (it searches the whole project and prints scenario, `@C` tag and runner). When the story crosses modules owned by other projects (for example orders → inventory), search those projects too. Run several term combinations. Open every hit and read the scenario: what it sets up, what triggers, what it asserts.
- Reusable features: `karate-context.py reusables <project>` (keys of `karate-config.js` with their parameters) plus the project's `reusable/`, `global/` and `util/` features listed by `profile`; read the header of each one you plan to call.
- TestRail: run the sibling skill's existing-coverage check (`../write-testrail-cases/SKILL.md`, step 4b): `refs` filter for every key, title search in the area's sections. Mark each match **duplicate** / **update** (expected results outdated by the story — propose the change for the `test-case-updater` skill) / **unrelated**. An existing **Karate** case whose `@C` tag is in a feature means the rule is covered.

Decide per rule and show it in the Coverage column of 1.5:
- **covered** — same precondition, same trigger, same asserted outcome: cite feature + scenario + C-id; no new case, no new scenario.
- **extend** — same workflow, missing assertion or variant: add the assertion or a scenario to that feature (team rule: prefer this over a new file); a missing assertion goes into the existing TestRail case as a new expected result, not into a new case.
- **new** — no scenario reaches the changed code path.

Registration must not duplicate either: a feature runs from exactly one runner or root feature (Phase 3.3).

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
| 3 | UI shows initial approval date after reopen | Manual | — | C736774 (manual, updated) | not needed |

Shared state: approvals.isApprovalRequired NOT toggled (tenant-wide; fix does not depend on it)
Karate 2 / Manual 0
```

Columns are mandatory. A Karate row with an empty "Fails before fix because" is removed or rewritten. Wait for confirmation unless the run is unattended (then state the assumption at the top and continue).

---

## Phase 2 — TestRail cases

### 2.1 Layer decision
For every scenario of 1.5 choose:
- **Karate** (default) — the outcome is decidable from HTTP requests and responses: follow-up GETs, job polling, events visible through another module's API, data in another module.
- **Manual** — Karate cannot decide it: UI rendering and wiring (labels, toasts, panes, client-side validation, navigation, capability-based hiding), exact UI texts, files a user downloads and opens, delivery to external systems (email, EDI/FTP, vendor portals), anything that needs a person's judgement, and API behaviour the test environment cannot reproduce (state the reason in the case).
- **Split** — the rule goes to a Karate case, its UI part to a Manual case that references it ("business rule verified by C<id>") instead of re-checking it.

Manual cases are full cases, not thin placeholders. They are written by the `write-testrail-cases` workflow (its steps 2, 4, 6–8), reusing the context, story analysis and coverage check already done here — do not repeat them. Its rules apply in full: exact UI texts from the context file, section style, house style, self-review gate. Karate and Manual cases of one story go to the same section. Manual cases keep the standard Manual metadata of the sibling skill (Execution Type = Manual); when they are later automated in Cypress, the team updates the case.

### 2.2 Karate case content
TestRail cases are read and reviewed by people (QA, PO, developers), so they are written in **plain business language**. Endpoints, payloads, field paths and error codes live only in the Karate feature; translating the case into requests is the job of Phase 3. Step N in TestRail still equals the `# N.` comment in the feature, so the PR covers exactly what the case says.

- **Title:** the business outcome, sentence case, no "API:" prefix.
- **Preconditions** (`<ol>`):
  1. Tenant settings the rule depends on, in UI terms (Settings > Orders > Approvals...), with values, and an explicit note when a setting is intentionally left at default.
  2. **Capabilities the user needs, as Eureka capability sets** in the team's usual wording (`data - UI-Orders Orders - create`, `procedural - UI-Orders Order Unopen - execute`). Take the names from the context file's *Required Capability Sets* section, then from existing cases of the same section. They document the access a real user needs; the Karate implementation does **not** model them (the test users of the project have a fixed permission set), so do not create per-case users or permission setup in the feature.
  3. Records the case needs, with meaningful values and symbolic names (Fund A with $10,000 budget, Order O in Pending). No reusable names, no UUIDs.
- **Steps:** one business action per step, in the domain's words ("Open Order O", "Unopen Order O, deleting holdings", "Add a PO line with multi-year payment on, prepayment term 2 years, 1 fiscal year distribution"). No URLs, no HTTP methods, no UI clicks.
- **Expected:** the business outcome with exact values ("Order O is rejected with the message that the number of fiscal year distributions must match the prepayment term", "Approval date is the same as after the first opening"). Status codes and error codes are not written in the case; the feature asserts them. Values captured during the run are named (remember as D1) and compared later.
- No UI-only checks (labels, toasts, layout) in a Karate case; those belong to a Manual case.

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
  - Test Group = Critical Path for core rules and permissions, Extended for regressions of bug fixes and edge cases — in projects with per-group runners this also selects the runner class (Phase 3.3)
  - Dev Team = owning team; Type and Priority per `../write-testrail-cases/references/house-style.md` for the area, overridden by the section sample
  - `refs` = story key + fix key
- Section, chosen by the skill: take the area's section subtree from the context file's `Sources:` line (for example Orders: 105 and its children), list the subsections with `get_sections`, and pick the one whose name matches the feature; if related cases were found in Phase 1.3, prefer their section. Then sample its 10 most recent cases (sibling skill, step 4) and follow their preconditions format, capability block and title style. Ask only when two subsections fit equally.
- Post after confirmation; collect the C-ids — Phase 3 needs them.

---

## Phase 3 — Implement the Karate feature

### 3.1 Placement and naming
- File: in the features folder the team profile shows for the module (usually `<project>/src/main/resources/<team>/<module>/features/`, sometimes with subfolders such as `features/consortia/`), or the existing related feature when extending.
- Name: kebab-case, describes the scenario, **≤ 80 characters** including `.feature` (long names break Karate reports and Windows checkouts). Drop filler words ("correctly", "when", "should").

### 3.2 Writing the feature
Start from the closest exemplar found in Phase 0 (same folder, same kind of workflow): copy its header layout, `Background`, login and headers, then write the scenarios. Pick every call from the reusable catalog. Apply `references/lessons.md`.

Follow the team rules files first; `references/karate-feature-conventions.md` holds the skeleton for teams without one. The essentials, which hold in every team:

- Header: `# For <JIRA-KEY>, https://foliotest.testrail.io/index.php?/cases/view/<id>[, …]`, then `Feature:` in Title Case.
- `Background`: `* print karate.info.scenarioName`, `* url baseUrl`, login and headers exactly as neighbouring features do; shared test data only if it is safe for parallel scenarios.
- Every scenario: `@C<id>` on its own line **first**, then `@Positive` / `@Negative`; Title Case scenario name equal to the TestRail title.
- IDs from `call uuid` inside the scenario — never shared between scenarios.
- Step comments `# N. <Title Case Text>` matching TestRail step N; unnumbered `# Prerequisites: …` for precondition setup. No `* print` in scenarios.
- One scenario = one complete workflow (setup, trigger, check); never split dependent steps into separate scenarios. Codes and names that must be unique (fiscal year series, fund codes) come from `call random_string`, not literals.
- Reusable features the way the project exposes them: by `karate-config.js` key when it is there (`* def v = call createOrder { id: '#(orderId)' }`), otherwise as neighbouring features load them (a `def x = read(...)` in `Background`); parameters from the reusable's header; never re-`read()` a reusable the config already loads. Do not write raw requests for something a reusable already does; if it lacks one parameter, add it as optional to the reusable and say so in the PR.
- Several similar records: a Karate `table` passed to one reusable call, not `Scenario Outline`.
- Order-independent assertions on collections (`[*]` with `contains`); `contains` on objects that may gain fields.
- `retry until` only to wait for async state, never `call pause` when there is a state to poll. Where the team rules require it (acquisitions), keep all conditions of a wait inside the `retry until` expression and assert with `match` in a separate request block.
- `match` with `$` right after the request; Karate markers for presence: `'##null'` (absent or null), `'#uuid'`, `'#string'`, `'#notnull'`.
- Users and headers exactly as the folder's features use them (some teams log in a test user and an admin, others use one admin token); do not invent per-case users.

### 3.3 Registration
Register the feature the way the team profile shows, never in a new way:

| Registration style (from `profile`) | Projects (examples) | What to add |
|---|---|---|
| `FEATURES` array | acquisitions, data-import | The file name, without `.feature`, at the end of the array of the runner chosen by Test Group (`*CriticalPathApiTest`, `*ExtendedApiTest`, otherwise the default runner). No new `@Test` methods, enums or runner classes (PR #2426) |
| One `@Test` per feature | mod-calendar, mod-users | A new `@Test` method at the end of the class, copying the neighbouring method's shape (`runFeatureTest("<name>")`, thread count, ordering annotations) |
| Root feature | mod-circulation (`root.feature`, `root-extended.feature`) | A `* call read('<same path style as the other lines>/<name>.feature')` at the end of the root feature that matches the Test Group |
| Array + root feature | acquisitions (`orders.feature`, `cross-modules.feature`, …) | Both: the array entry and a `Scenario: <Feature title>` with `* call read('features/<name>.feature')` at the end of the root feature |

- A feature runs from exactly one runner or root feature; `karate-context.py registered <project> <name>` must show one path.
- Append-only: never insert in the middle, never reorder.

### 3.4 Static validation (mandatory, before committing)
Run and fix until clean (`references/validate-feature.sh` does all of it):
1. Gherkin parses (`pip install gherkin-official`, parse the file).
2. Every reusable key used in the feature exists (`karate-config.js`, a `def` in the feature, or a global/util feature of the project).
3. File name length ≤ 80; no `* print` in scenarios; no `@parallel=false`; no `Scenario Outline`; no `callonce uuid` or unquoted `#(...)` in call arguments; no `read()` of a reusable already in `karate-config.js`; every scenario has exactly one `@C<id>` that matches a posted case.
4. Registration: in at most one runner of the project, once in the given root feature, and run by something. Call: `validate-feature.sh <feature> <runner or -> <root feature or ->`.
5. Step comments 1..N without gaps and matching the TestRail steps of that case. Projects with a rules folder (`<project>/ai/`) also fail on `retry until` mixed with `match` and on a scenario ending with `configure headers`; elsewhere these are warnings.

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
6. **Learn from the review.** When reviewers comment on the PR, apply the fixes and add each comment that is a general rule (not specific to this story) to `references/lessons.md`: the rule, the PR and the reviewer's wording in short. Suggest the same rule to the team for their rules file when it applies team-wide. After the first run for a team without a saved profile, offer to save it as `references/team-<team>.md`.

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
- [ ] The team's rules files (all of `<project>/ai/`, if any) and the Karate Coding Standards page were read; every scenario is a complete workflow with its own IDs and unique codes.
- [ ] Every acceptance criterion and touched business rule is covered by a Karate case, a Manual case or an existing case; nothing was dropped because Karate cannot reach it.
- [ ] TestRail fields are HTML and carry the "AI" label; Execution Type = Karate, Automation Scope = Karate Approved.
- [ ] TestRail cases contain no endpoints, HTTP methods, status codes or UI clicks; capabilities are listed as Eureka capability sets; the feature does not model them.
- [ ] Static validation passed; registration is append-only.

## Run summary (always print at the end; keep field names stable)

```
Run summary
Story:            MODORDERS-1458 (fix: MODORDERS-1456, mod-orders #1332)
Team / module:    Thunderjet / mod-orders (project acquisitions; registration: FEATURES array + root feature)
Cases:            2 posted (Karate 2 / Manual 0): C1621341, C1621342
Existing coverage: C736774 (manual UI, updated by the team) — not duplicated
Feature:          acquisitions/.../mod-orders/features/open-order-approval-details-not-overwritten.feature (2 scenarios)
Registered in:    OrdersExtendedApiTest, orders.feature
PR:               folio-org/folio-integration-tests#2619 (ready for review, not executed; nightly run covers it)
Shared state:     approvals.isApprovalRequired left at default
Open questions:   Q1 — mod-orders keeps client-supplied approvalDate on PUT (scenario 2)
App context:      write-testrail-cases context/orders.md (built 2026-11-07), finance.md
Section:          Orders > <subsection> (chosen from context Sources + section sample)
Rules source:     acquisitions/ai/* (2 system prompts + templates), Karate Coding Standards wiki
Team profile:     references/team-thunderjet.md (checked against profile output)
```

## References
- `references/karate-standards.md` — digest of the Karate Coding Standards wiki page, the FAT-13426 / FAT-20199 refactoring and the PR #2426 runner structure; precedence and known differences.
- `references/karate-context.py` — read-only helper for any project: team profile, reusable catalog, coverage search, endpoint index, exemplar features, registration check.
- `references/lessons.md` — rules learned from PR reviews; apply on every run.
- `references/karate-feature-conventions.md` — feature skeleton and conventions for teams without a rules file.
- `references/team-<team>.md` — saved team profiles with pitfalls (`team-thunderjet.md` is the first; add more after runs for other teams).
- `references/example-modorders-1458.md` — worked example: analysis, TestRail case, feature, PR.
- `references/validate-feature.sh` — static validation script.
- `../write-testrail-cases/SKILL.md` — Manual UI case workflow, existing-coverage check, HTML formatting, metadata, posting, clarifying questions.
- `../write-testrail-cases/references/` — `area-map.md`, `context/<area>.md`, `house-style.md`, `writing-rules.md`, `examples/<area>.md`: application knowledge shared by both skills.
