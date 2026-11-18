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
4. **Team rules file.** Load the team's own AI/coding rules — they are authoritative and override anything in this skill when they disagree:
   - Thunderjet (acquisitions): `acquisitions/ai/ACQ_ORDERS_SYSTEM_PROMPT.md` (mod-orders, consortia, edge-orders) or `acquisitions/ai/ACQ_CROSS_MODULES_SYSTEM_PROMPT.md` (cross-modules, finance, invoices), plus `acquisitions/ai/prompt/PROMPT_TEMPLATES.md`. Team map: `references/team-thunderjet.md`.
   - Other teams: if the project has an `ai/` folder, use it; otherwise derive conventions from the 3 most recently changed features in the same folder (`git log -3 --name-only -- <folder>`) and record what you derived in the run summary.
5. **TestRail and Jira access.** Use the TestRail / Jira MCP tools when present; otherwise the credentials chain in `../write-testrail-cases/SKILL.md` ("TestRail API Integration → Credentials").

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

### 1.3 Existing coverage
Search before writing anything new:
- Karate: `grep -rn "<endpoint path>\|<field name>" <team folder>` — list features that already exercise the endpoint or field.
- Reusable features: every key in `<project>/src/main/resources/karate-config.js` and the `reusable/` folders; read the `# parameters:` header of each one you plan to call.
- TestRail: cases whose `refs` contain the story / fix key, and cases found by a semantic search on the rule. Note their Execution Type: an existing **Karate** case already linked by `@C` means the rule is covered.

Decide per rule: **already covered** (cite feature + scenario) / **extend an existing feature** (team rule: prefer adding a scenario to a related feature over a new file) / **new feature**.

### 1.4 Shared-state check (parallel safety)
Features run in parallel in a shared tenant. For each precondition ask: *does it change something tenant-wide?* (order/finance settings, approval requirement, circulation rules, configuration entries, acquisition units used by others). If yes:
1. Prefer a scenario that reaches the changed code path **without** the tenant-wide change (MODORDERS-1458: the fix applies whether or not approval is required, so the setting is left alone).
2. If impossible, the scenario must live in a feature or runner that is not run in parallel with features depending on that setting — say so in the PR and ask the team; never add `@parallel=false` to a new feature.

### 1.5 Scenario analysis (show, then wait for confirmation)

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
Karate by default: the outcome is decidable from HTTP requests/responses (including follow-up GETs, job polling, other modules' APIs). UI case only for UI wiring with no API equivalent (rendering, client-side validation, navigation, UI-only capability hiding) — written per `../write-testrail-cases/SKILL.md`, thin, and never re-asserting what a Karate case asserts.

### 2.2 Karate case content
TestRail cases are read and reviewed by people (QA, PO, developers), so they are written in **plain business language**. Endpoints, payloads, field paths and error codes live only in the Karate feature; translating the case into requests is the job of Phase 3. Step N in TestRail still equals the `# N.` comment in the feature, so the PR covers exactly what the case says.

- **Title:** the business outcome, sentence case, no "API:" prefix.
- **Preconditions** (`<ol>`):
  1. Tenant settings the rule depends on, in UI terms (Settings > Orders > Approvals...), with values, and an explicit note when a setting is intentionally left at default.
  2. **Capabilities the user needs, as Eureka capability sets** in the team's usual wording (`data - UI-Orders Orders - create`, `procedural - UI-Orders Order Unopen - execute`). Take the names from existing cases of the same area. They document the access a real user needs; the Karate implementation does **not** model them (the test users of the project have a fixed permission set), so do not create per-case users or permission setup in the feature.
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
  - Dev Team = owning team; Type and Priority per the sibling skill
  - `refs` = story key + fix key
- Section: the team's section for the area (for acquisitions: the section where the related manual cases live, e.g. Orders section 105). Ask only if it cannot be determined.
- Post after confirmation; collect the C-ids — Phase 3 needs them.

---

## Phase 3 — Implement the Karate feature

### 3.1 Placement and naming
- File: `<project>/src/main/resources/<team>/<module>/features/<name>.feature` (or the existing related feature when extending).
- Name: kebab-case, describes the scenario, **≤ 80 characters** including `.feature` (long names break Karate reports and Windows checkouts). Drop filler words ("correctly", "when", "should").

### 3.2 Writing the feature
Follow the team rules file first; `references/karate-feature-conventions.md` holds the skeleton and the rules that apply when the team has no rules file. The essentials, which must hold in every team:

- Header: `# For <JIRA-KEY>, https://foliotest.testrail.io/index.php?/cases/view/<id>[, …]`, then `Feature:` in Title Case.
- `Background`: `* print karate.info.scenarioName`, `* url baseUrl`, login and headers exactly as neighbouring features do; shared test data only if it is safe for parallel scenarios.
- Every scenario: `@C<id>` on its own line **first**, then `@Positive` / `@Negative`; Title Case scenario name equal to the TestRail title.
- IDs from `call uuid` inside the scenario — never shared between scenarios.
- Step comments `# N. <Title Case Text>` matching TestRail step N; unnumbered `# Prerequisites: …` for precondition setup. No `* print` in scenarios.
- Reusable features only by their `karate-config.js` key, with parameters from their `# parameters:` header. Do not write raw requests for something a reusable already does.
- `retry until` only to wait for async state; keep all conditions of a wait inside the `retry until` expression, then assert with `match` in a **separate** GET block.
- `match` with `$` right after the request; Karate markers for presence: `'##null'` (absent or null), `'#uuid'`, `'#string'`, `'#notnull'`.
- Admin headers only for modules the user lacks permissions for (team rule); switch with `configure headers`, never at the very end of a scenario.

### 3.3 Registration
- Runner class by Test Group: Critical Path → `*CriticalPathApiTest`, Extended → `*ExtendedApiTest`, otherwise `*ApiTest` (the class whose `TEST_BASE_PATH` points at the module's `features/`). Add the file name (without `.feature`) **at the end** of the `FEATURES` array.
- Root feature (`<module>/<module-root>.feature`, e.g. `mod-orders/orders.feature`): append `Scenario: <Feature title>` + `* call read('features/<name>.feature')` at the end.
- Append-only: never insert in the middle, never reorder.

### 3.4 Static validation (mandatory, before committing)
Run and fix until clean (`references/validate-feature.sh` does all of it):
1. Gherkin parses (`pip install gherkin-official`, parse the file).
2. Every reusable key used in the feature exists in `karate-config.js`.
3. File name length ≤ 80; no `* print` in scenarios; no `@parallel=false`; every scenario has exactly one `@C<id>` that matches a posted case.
4. The feature name appears once in the runner's `FEATURES` and once in the root feature.
5. Step comments 1..N match the TestRail steps of that case.

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

---

## Self-review gate (run before showing any case or committing)

- [ ] Every scenario has a "fails before fix because…" reason that matches the fix diff.
- [ ] No tenant-wide setting is changed in a parallel feature, or the PR explains why.
- [ ] TestRail steps and `# N.` comments match 1:1; titles match scenario names.
- [ ] Every assertion is on a business field with an exact or captured value; no step is status-only except triggers.
- [ ] Child entities verified through their own endpoint; cross-module effects verified in the other module.
- [ ] All reusable keys exist; parameters match their headers.
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
Rules source:     acquisitions/ai/ACQ_ORDERS_SYSTEM_PROMPT.md
```

## References
- `references/karate-feature-conventions.md` — feature skeleton and conventions for teams without a rules file.
- `references/team-thunderjet.md` — Thunderjet folders, runners, root features, reusables, pitfalls.
- `references/example-modorders-1458.md` — worked example: analysis, TestRail case, feature, PR.
- `references/validate-feature.sh` — static validation script.
- `../write-testrail-cases/SKILL.md` — UI case rules, HTML formatting, metadata, posting, clarifying questions.
