---
name: write-testrail-cases
description: Use when writing, generating, or adding manual test cases to TestRail. Produces structured cases with preconditions, step-by-step actions with expected results, and all required metadata fields. Also use when asked to cover a User Story with test cases, prepare cases for a new feature, or post cases to a TestRail section via API.
---

# Write TestRail Cases

> **Core principle:** A test case exists to verify a business rule, not to document a click path. Navigation is the means; assertions about the resulting state are the point. A case whose expected results could be true even if the feature were broken is a failed case.

> **Evidence only, never assumption.** Every functional claim in a case — what a business rule does, what a config parameter changes, what a modal/toast says, whether feature X depends on Y — must trace to a source you actually read this session: an existing TestRail case, a Jira ticket, GitHub source/README/translations, the FOLIO wiki, or FOLIO API docs. Never infer behavior from general software knowledge or from "it's probably like feature Z". If a fact is unverified, fetch the source or **ask the user** — do not guess and move on. An unverifiable UI string may be written only with the flag `(verify exact wording on first execution)`.

> **Section style beats global defaults.** The team's conventions differ by area and even by section (preconditions format, permissions block, title prefixes, separators). When this file gives a default and the target section's recent cases consistently do something else, follow the section.

## Before you start

- No context file for the area, or it is stale (see `references/area-map.md` → Freshness) and the story is large → suggest running `build-app-context` first; proceed with enrichment if the user declines.

## Reference files

| File | Read when |
|---|---|
| `references/area-map.md` | Step 1 — area detection, context file rules, freshness |
| `references/context/<area>.md` | Step 1 — business rules, exact UI texts, domain model |
| `references/house-style.md` | Step 5 — Type / size / journey / priority / title conventions per area |
| `references/examples.md` | Step 2 — cross-area golden cases and anti-patterns (verification depth bar) |
| `references/examples/<area>.md` | Step 2 — golden case for the detected area, when the file exists |
| `references/writing-rules.md` | Step 6 — preconditions and steps rules, case template |
| `references/step-patterns.md` | Step 6 — reusable step shapes |
| `references/testrail-api.md` | Step 8 — metadata IDs, HTML markup, posting, fallback output |

## Mandatory Workflow (follow in this exact order)

1. **Detect the application area** from the story (see `references/area-map.md`) and **read the matching context file(s)**. If the area cannot be determined, ask.
   - Read the file's `## Changes since …` section (if present) first — it overrides older sections.
   - **1b. Assess context quality.** Run Lightweight Context Enrichment (below) if ANY is true: context file missing; header says DRAFT; header date older than 90 days or built for an older release than the story's Fix Version; fewer than 10 Key Business Rules; no "Exact UI Texts" section or fewer than 3 confirmed toasts; more than 5 items in "Known Gaps / Items to Verify".
2. **Read `references/examples.md` and `references/examples/<area>.md`** (if it exists for the detected area). New cases must match their verification depth, value precision and step shape.
3. **Read the User Story / Jira ticket** (Jira MCP if a key is given). Extract Summary, Description, Acceptance Criteria, Development Team (→ `custom_dev_team`), Fix Version, labels (ECS?), and the `refs` key(s). **`refs` = the work item(s) this case verifies** — often a Bug or Tech-Debt ticket, or several keys across projects (e.g. `UIF-525, MODFIN-391`). Include every ticket the user gave and every ticket the case directly verifies; do not auto-add links Jira merely shows; never invent a story key.
4. **Sample the target section.** Ask for the TestRail Section ID now (optional — the user may defer it). If given, fetch the 10 most recent cases of that section and note: preconditions format (`<ol>` / `<p>1)` / `<ul>` / table), permissions block (capabilities only vs Okapi + Eureka), title prefixes in use, separators (`->` / `=>`), Type, labels (`BFreviewed`), typical step count. These observations override the defaults in `house-style.md` and `writing-rules.md`.
4b. **Check for existing coverage.** Query TestRail for cases that already reference the story or its related keys: `get_cases/14&suite_id=21&refs=<KEY>` for every key from step 3 (the `refs` filter matches any listed key). Also search the target section by the feature's main noun (`search_test_cases` on title). For each match decide: **duplicate** (same scenario — do not generate), **update** (existing case covers the flow but its expected results are outdated by this story — propose the change, to be applied with the `test-case-updater` skill), or **unrelated**. List the matches with this decision in Scenario Analysis under "Existing coverage".
5. **Map the story to the context file's Key Business Rules**: each touched rule and each acceptance criterion is a scenario candidate. Then perform **Scenario Analysis** (below), present it, and **wait for confirmation**.
6. **Generate cases**, one per confirmed scenario, following `references/writing-rules.md` and `references/step-patterns.md`.
7. **Self-review every case** against the Self-review gate (below). Fix violations silently.
8. **Post**: get the Section ID if not yet given, show the posting preview, wait for explicit confirmation, post via API (`references/testrail-api.md`). If the API is unavailable, use the Fallback Output format from the same file.

---

## Lightweight Context Enrichment

Fast, story-targeted, in-memory only. Not a `build-app-context` run; never writes to disk.

**GitHub — max 3 files, each ≤150 KB, in priority order:**
1. `translations/<ui-module>/en.json` — values for keys containing the story's feature keywords. **If the story is not Done (In Progress / In Review / In Code Review) and its strings are not on master, look for a branch named `<STORY-KEY>-*` (or the PR linked in Jira Development) in the ui-module and read `en.json` from that branch** — the feature's real labels live there before merge (2026-11-07: UICIRC-1361 branch labels differed from the story text). Tag such strings `[from PR branch — <branch>]`. `en.json` is the source; `en_US.json` is a Lokalise copy that lags behind (on 2026-11-07 it was missing e.g. all eHoldings package-record and Orders payment-terms strings).
2. `package.json` → `stripes.permissionSets` — candidate Capability Set names.
3. One Cypress fragment from `stripes-testing/cypress/support/fragments/<area>/` matching the feature — UI labels.

**Jira — story + directly linked issues only** (subtasks, related bugs, parent epic). Their ACs become business-rule candidates. Issues fetched for enrichment are context, not automatic `refs`.

**Do not fetch:** all closed stories/bugs for the component (that is `build-app-context` scope); more than 3 GitHub files.

Add a note to Scenario Analysis:
> ⚠️ Context was enriched from GitHub/Jira for this session. Run `build-app-context` to make it permanent.

If enrichment returns nothing useful:
> ⚠️ Context enrichment returned no additional data. Cases are based on the existing context file only — verify domain-specific details on first execution.

---

## Scenario Analysis

Present before generating:

```
I've read the story (refs: XXX-123), the <area> context (built <date>) and <N> recent cases from section <ID>. Business rules touched: <rule numbers/short names>.

Happy path:
1. [main action] with valid data → [exact end state] → Extended | Critical Path

Business-rule verification:
2. [action] releases/creates/updates [entity] with [exact state]

Regression of existing behavior (what this change touches, not new behavior):
3. [adjacent existing flow] still produces [exact state] after the change

UI verification:
4. [page/modal] shows required elements on open

Capability boundaries:
5. User without [Capability Set] cannot [action]; still can [what remains visible]

Negative / edge cases:
6. [action] fails when [condition]

Inferred integration scenarios (not in the ACs — from the context file, confirm scope):
J1. [cross-feature / over-time journey: rollover, create-from-template, new FY, ECS share]

Existing coverage (step 4b):
- C<id> <title> — duplicate | update (what changes) | unrelated

Does this coverage look complete?
```

Wait for the user's confirmation or corrections.

**Regression is mandatory, not optional.** For every changed rule, list the existing flows that share the same entity, API, setting, or UI component (from the context file's domain model and side effects) and propose at least one scenario that proves they still behave as before. A bug fix gets: the fixed behavior + the neighboring behavior the fix could break.

### Journey vs atomic cases

- **Lifecycle / workflow stories** (request lifecycle with notices, order open→receive→pay, import job stages) → **one journey case per flow variant**, verifying every checkpoint along the way. Flow variants (Page vs Hold, item vs title level) are separate journey cases, never per-checkpoint stubs.
- **Feature / element stories** (new column, modal, validation, setting) → atomic cases per scenario, sized to the area median.
- When a condition resolves to several end states ("item with an open request" → In transit at a non-pickup SP, Awaiting pickup at the pickup SP), default to one journey covering all outcomes and confirm in Scenario Analysis (real example: C7148).
- For finance/rollover/template features, prefer a few bundled `Functional` journey cases over one case per AC (real example: UIOR-1530 → 4 bundled cases C1385639/C1395029/C1404901/C1404902, not 13 stubs).
- `User Journey = Yes` only in areas that actually use the flag (see `house-style.md`) or for an explicit end-to-end circulation lifecycle. Multi-step ≠ journey flag.

### Scenario Coverage Checklist

- [ ] Primary happy path with exact end state
- [ ] **Every Key Business Rule the story touches — explicit state assertions**
- [ ] **Regression of adjacent existing behavior** (same entity / API / setting / component)
- [ ] UI elements (buttons, labels, columns, counts) — for new pages/modals
- [ ] Edit / duplicate / delete (Cancel, confirm, removal from list), where applicable
- [ ] Capability boundaries — what the restricted user cannot do AND what they still can
- [ ] Negative: invalid input, wrong profile, empty files, referenced records blocking deletion
- [ ] Edge: boundary values, repeated identifiers, records referenced in several places
- [ ] Status changes with exact before/after values; toasts verbatim
- [ ] **Every entry point** of the touched action (Actions menu on each tab, row ellipsis, detail-page Actions, bulk toolbar) and **every selection state** (none / one valid / one invalid / mixed / multiple) — learned from Fees/Fines Waive vs real case C465
- [ ] Interactive modal buttons (Swap, Recalculate) — dedicated scenario
- [ ] Search & filter pane, pagination, date ranges — when the story touches them
- [ ] Multi-tenant / ECS — only if the story labels or text require it
- [ ] Effects verified at their real destination: notices → mailbox (subject + body tokens), exports → downloaded file, finance → transaction + budget values (not just a toast or a log row)
- [ ] UI built from backend data (links, display names, statuses) — a step confirms the target record/API actually carries the field, not only that the UI shows something

---

## Self-review gate (run before showing any case)

**Substance**
- [ ] At least one step asserts the business-rule outcome with exact values; no expected result could pass on a broken feature.
- [ ] All entities the action touches (per context file) are verified; regression scenario present for each changed rule.
- [ ] Every UI string / rule traces to a source read this session, or carries the `(verify exact wording on first execution)` flag.
- [ ] Numbers absolute where asserted; symbolic placeholders (`S`, `<barcode>`) in circulation/inventory flows — no invented concrete values.
- [ ] Business-critical tables (transactions, budgets) verified column by column.
- [ ] Each record type (instance / holdings / item; task / job) verified on its own — never inferred from another.
- [ ] Links in expected results name the target record that must open.

**Shape**
- [ ] Entry step → business assertion(s) → re-verification after a state change.
- [ ] Step count near the area median (`house-style.md`). ≤3 steps only for permission-denial cases or areas whose median is ≤3; otherwise a context or assertion step is missing. **A case shorter than half the area median is merged into a sibling case with the same preconditions** (e.g. "column hidden by default" + "column shown after enabling" = one case), not shipped separately.
- [ ] Every capability set name comes from the context file, a recent case in the target section, or `package.json` → `stripes.permissionSets` of the module; a name you could not find is written as `(capability set name not confirmed — verify)`, never guessed.
- [ ] Preconditions are data/state only (no in-test UI actions), flat, numbered so steps can say "Preconditions #N", with starting values for everything asserted later.
- [ ] Permissions block matches the section (default: Eureka capability sets only); never a legacy permission instead of a capability set.
- [ ] Steps imperative, no actor prefix; single unnamed user unless two roles are genuinely needed.
- [ ] Expected results terse and observable — no rationale, ticket-scope essays, or multi-sentence NOTEs.
- [ ] 2+ `field = value` pairs → lead-in line + bullets, never a semicolon run-on.

**Metadata**
- [ ] Title follows `house-style.md` → Titles; prefix only if already used in the target section.
- [ ] Type, Priority, Test Group, Journey flag match the area's measured norms (default Priority = Medium, Test Group = Extended).
- [ ] `refs` = what the case verifies; label `ai` present; `BFreviewed` only if the section uses it.
- [ ] No generated case duplicates a case found in step 4b; cases marked "update" are proposed as edits, not re-created.
- [ ] HTML payload renders the same as the preview shown to the user (`testrail-api.md` → pre-post check).

---

## Quick Reference Checklist

- [ ] Context file read (freshness checked); story mapped to Key Business Rules
- [ ] Target section sampled (if ID given) — its conventions override defaults
- [ ] examples.md read; verification density matches
- [ ] Scenario list confirmed by the user, including regression and inferred journeys
- [ ] Self-review gate passed for every case
- [ ] Posting preview confirmed; IDs resolved at runtime; created `C…` numbers reported
