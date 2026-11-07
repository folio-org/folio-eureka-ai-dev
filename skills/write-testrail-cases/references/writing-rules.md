# Writing Rules

## Test Case Structure

Every test case has these sections (in order):

**Metadata** — Type, Priority, Release, Test Group, References, and other classification fields.
**Preconditions** — numbered list (default `<ol>`; match the section): the user with their Capability Sets, required data with exact values, and the starting page/state.
**Steps** — actions with a concrete expected result for each step.

### Template

```
Title: [Imperative verb / factual phrase] [object] [qualifying condition]   [prefix only if used in the target section — see house-style.md]

Type:               [Functional | Other — dominant Type of the area, house-style.md]
Priority:           Medium   [High / Critical only per house-style.md → Global defaults]
Release:            [latest release from get_case_fields → custom_release; R2 2026 Umbrellaleaf as of 2026-11]
Test Group:         Extended   [Critical Path for core business-rule cases; never Smoke for manual]
User Journey:       No   [set to Yes for journey/lifecycle cases — see SKILL.md → "Journey vs atomic cases"]
Multi-Tenant:       No
Bug Created:        No
Unstable:           No
ECS Enabled:        No   [set to Yes only when the story explicitly tests ECS/cross-tenant behavior]
ECS Unsupported:    No   [fixed default — never ask]
Capabilities Ready: Yes
Execution Type:     Manual   [required]
Dev Team:           [Value from "Development Team" field in the User Story]
Customer Name:      [All | MOBIUS/GALILEO | LOC — only if the story targets a specific customer]
Labels:             ai   [always; + BFreviewed only if the section uses it]
References:         [Jira ticket IDs, comma-separated, e.g. MODFIN-273, UIF-657]

Preconditions:   [numbered — <ol> by default]
1. User with the following capability sets is logged in:
   - data - UI-[Module] [Resource] - [action]
   - procedural - UI-[Module] [Resource] - execute
2. [Required records with exact values, e.g. "Two Fiscal years exist. Fund A-FY-current: Allocated = 200.00, Encumbered = 50.00, Available = 150.00"]
3. [More data — one item per record or tightly related group of facts; steps reference "Preconditions #3"]
4. User is on [Starting app/page]

Steps:
1. Action:   [verb] [object] on [location] — navigation/setup clicks may be grouped as a bullet list inside one step when they share a single verification point
   Expected: [Observable UI or system result — prose by default; bullet list only for a true inventory of independently-checkable items]

2. Action:   [verb] [entity] from Preconditions #N
   Expected: [Column-by-column / field-by-field assertion with exact values]
```

---

## Writing Guidelines

> Write every test case as if it will be executed by a QA engineer who has never seen this feature before. Steps must be precise enough that any team member — Firebird, Spitfire, Vega, Volaris, Thunderjet — can execute the case without guessing. Same level of detail regardless of team or area.

### Preconditions

Target environment is Eureka, so **Capability Sets are the source of truth** for access requirements — always include them.

**Default (86% of recent human cases): capability sets only**, as a sub-list under the user item:

```
1. User with the following capability sets is logged in:
   - data - UI-<App> <Resource> - <action>
   - procedural - UI-<App> <Resource> - execute
   - settings - UI-<App> <Resource> - manage
```

Capability set syntax: `[type] - UI-[App] [Resource] - [action]`, type ∈ `data`, `procedural`, `settings`. Take names from, in order: the context file → recent cases of the target section (workflow step 4) → the module's `package.json` → `stripes.permissionSets` (`displayName`). If none has it, write `(capability set name not confirmed — verify)`; never invent one.

**Okapi + Eureka dual block** — only when the target section's recent cases use it (~7% overall). Then add, above the capability list:

```
Permissions (for Okapi env.):
- Permission: <Named FOLIO permission string>
For Eureka environment user with following capabilities/sets is logged in:
- …
```

Section-specific formats (Requests table, Invoices `<hr>` paragraph) are in `house-style.md`. Never list a legacy permission *instead of* a capability set.

- **Format: numbered list.** Default markup `<ol><li>` (see `testrail-api.md` → HTML). If the section consistently uses `<p>1) …</p>` (Orders) or `<ul>`, match it. Numbering is what lets steps say "Preconditions #N". **The list must be flat**: the user, each data record, and the starting page are separate top-level items — never nest a data record or login state under another item. Sub-bullets only for the capability-set list under the user item.
- **Grouping facts within one entry is expected, not just tolerated.** Real team-authored preconditions routinely pack several closely related facts into a single item (e.g. "Two Fiscal years exist. One has an assigned Acquisition unit" or "Fund A-FY-current: Allocated = 200.00, Encumbered = 50.00, Available = 150.00" as one line covering three values). Split into separate items only when the sub-facts belong to genuinely different records/entities, or when a step needs to reference one specific fact by position independently of the others. Don't force one-value-per-line where the team would naturally write one sentence.
- List required Capability Sets for the logged-in user, e.g.:
  ```
  data - UI-Data-Export Settings - edit
  data - UI-Data-Export Settings Lock - edit
  ```
- List required data with **exact values for everything a step will later assert *as a number or fixed status***: monetary amounts, statuses, counts, relationships. If a step will verify `Available = 200.00`, the precondition must establish the starting `Available = 150.00 (Allocated 200.00 − Encumbered 50.00)`. For circulation/inventory flows where the team uses symbolic identifiers (`service point S`, `<barcode>`), keep those symbolic in preconditions too — see the two-part value rule under "Steps — Business-Logic Verification". Don't mix invented concrete barcodes into an otherwise symbolic case.
- List the starting system state (which app or page the user is on).
- **Default to a single, unnamed user** ("User with following Capability Sets is logged in...", "Staff user is on..."). This matches how the team actually writes cases — most real cases never name an actor at all. Introduce named actors (User A / User B) only when the scenario genuinely requires two distinct roles active at once — e.g. a proxy and a sponsor, a requester and staff processing the request, an admin setting something up for a restricted user to then be tested — and even then, name them by role where possible ("Admin user" / "Restricted user") rather than defaulting to letters. (Actor names, when used, live in Preconditions only — see Steps below for step phrasing.)
- **Cross-references to other cases:** A precondition may reference another case as a setup shortcut: `"Case C12345 can be used as precondition to this test case; otherwise follow the steps below:"`. Complex setup steps may use `<a href="index.php?/cases/view/XXXX">CXX</a>` links pointing to how-to cases (e.g. "how to create a fiscal year"). This is an accepted pattern — preserve it in existing cases; add it in new cases only when the referenced setup is genuinely too long to inline.
- **Structured parameter blocks:** When a precondition contains a multi-line parameter list (e.g. MARC field mappings, rollover settings), wrap it in `<pre><code>...</code></pre>` for readability.
- **For ECS cases:** always specify which tenant each data record belongs to (Central or member tenant name), which service points are configured, and what affiliation the user starts with:
  ```
  - Active Ledger exists in Central tenant for the current fiscal year; Fund A (Allocated = 200.00) exists in member tenant (College), related to the Ledger above
  - User is logged in with affiliation set to Central tenant
  - Item with barcode <barcode> exists in member tenant, status Available; pickup service point SP-Central is configured in Central tenant
  ```

### Steps — Case Shape (match the golden examples)

1. **Entry**: grouped navigation step(s) from the app entry point, each with a real verification (pane opened, exact counts like "3 members selected", buttons with states).
2. **First-open context**: when the case lands on its target pane/modal for the first time, verify the key elements relevant to the scenario — columns, labels, button states, counts. A full element-by-element inventory step is only needed when the pane/modal itself is the subject under test.
3. **Business assertions**: per-row / per-field verification steps — the core of the case.
4. **Interaction + re-verification** (when the scenario involves changing state): perform the change, then re-assert the new exact state (new counts, rows appearing/disappearing).

Sizing: follow the area median in `house-style.md` (overall human median is **7**, p25–p75 = 5–11). Integration journeys may legitimately reach 15–22 steps. **1-step cases are valid** for permission-denial tests: the precondition sets up the restricted user; the single step verifies the option/button is absent. A 2–3 step case outside permission-denial or short-norm areas (Fees&Fines, Course Reserves, Circulation Settings) means navigation, context verification or a business assertion is missing.

**Preconditions hold only data and state that exists before the test starts** (records, users, configuration, login, starting app). Any action the user performs in the UI during the test — selecting members, switching tabs, opening panes, applying filters — is a step with its own expected result, never a precondition. "User is on <page> with all 3 members selected" is wrong: member selection is a step (and per the golden examples, the selection modal itself gets verified).

### Steps — Business-Logic Verification (the most important rules)

- **Every case must verify the business rule outcome, not just the UI mechanics of triggering it.** The trigger flow (menus, modals, Submit) is compressed; the state verification is detailed.
- **For quantitative assertions: absolute values, never relative.** Where a step verifies a specific number — money, counts, percentages, budget buckets — write `Encumbered = 0.00`, `Available = 200.00 (restored to full allocation)`, never "increased by 50.00" or "decreased accordingly". The executor must be able to compare a number on screen with a number in the case. Finance/Orders/Invoices cases are largely this kind, and the team writes concrete amounts in preconditions too (real example C648502: "Fund A having current budget with money allocation $100 … Allowable expenditure percentage 110%"). **But use concreteness only where the exact number is the point.** When only a threshold or direction is under test, the team writes it relatively — real example C380517 (insufficient-funds) uses *"enter any value exceeding money allocation for Fund B"* rather than a specific figure, because the exact amount is irrelevant to what's being verified. Match the number's role: exact when asserted, symbolic/relative when only the boundary matters.
- **For non-quantitative / circulation-style flows: symbolic placeholders are the team's norm — do not invent fake concrete values.** Check in, Check out, Requests, Loans, Inventory cases typically use abstract identifiers the executor fills in at run time: `service point S` / `S1`, `<barcode>`, `<title>`, `<material type>`, "Item with at least one open request". Real example (C7148 preconditions): *"User with Check In permissions … with service points S and S1 assigned. Item with at least one open request, with top request with pickup service point S."* Do NOT fabricate a specific barcode like `12345` or a named service point like `SP-A` when the team would write `S`/`<barcode>` — invented concrete values just add noise the executor has to ignore. Use concrete values here only when the exact value is itself under test (e.g. a barcode with a trailing space, a specific fee amount).
- **Verify all entities the action touches**, per the context file. Example — closing a PO must assert: encumbrance transaction status, budget values, PO status and "Reason for closure" on the PO record, POL receipt/payment statuses.
- **Prefer explicit column-level verification for business-critical tables.** Never "transaction is displayed" for transaction or budget-value tables — assert exact values such as `Type = "Encumbrance"`, `Source = <PO number>`, `Amount = $50.00`, `Status = "Released"`. A concise summary assertion is acceptable for navigation/lookup tables where it still proves the intended behavior.
- **Reference preconditions by number** in steps: "the unlocked mapping profile from Preconditions #3".
- **Toast messages: exact text with placeholders**, e.g. `"<amount> was successfully allocated to the budget <Fund-FY>"`. Never "success toast is displayed". If the exact text is unknown and not in the context file or examples, write the most likely exact text and flag it: `(verify exact wording on first execution)`.

### Steps — Granularity and Format

- **Navigation/setup actions may be grouped into one step** as a bullet list when they share a single verification point (see examples.md, Example 1, step 1). Verification/assertion actions are never grouped — one assertion target per step.
- **Break a multi-part action (or precondition) into a lead-in line + bulleted sub-lines — never one run-on sentence.** When a single step (or a precondition item) fills several form fields, sets several options, or performs a short chain of sub-actions, write a lead-in clause ending in a colon, then put each field/option/sub-action on its own line as a bullet. This is a direct tester request and matches the real corpus. Do the same for the expected result when it confirms several field values. Example:

  ```
  Action:
  Navigate to Settings > Data Import > Match profiles, click "New" to create a match profile:
  - Existing record type = MARC Authority
  - Existing record field = "Authority: 001"
  - Incoming record field = "MARC Authority: 001"
  - Match criteria = "Exactly matches" (the only available option)
  - Click "Save as profile & Close"
  Expected:
  Match profile is saved and appears in the Match profiles list with:
  - Name = <profile name>
  - Existing record field = "Authority: 001"
  - Incoming record field = "MARC Authority: 001"
  ```

  When posting via API, encode the lead-in as `<p>` and each bullet as a real `<ul><li>` (see `testrail-api.md` → HTML markup). A raw `\n- ...` inside one `<p>` collapses into a single run-on line in TestRail. (This is distinct from the "Prose first" rule below: a single coherent *observation* stays prose; a *set of discrete field values / sub-actions* becomes bullets.)
- **Use imperative style in steps**: "Click ...", "Navigate to ...", "Select ...", "Open ...". Do not prefix steps with an actor name (no "User clicks") — the actor is defined once in Preconditions (usually just "User"), not repeated in every step.
- **Don't attach status adjectives to records that don't have that status concept.** Write "A MARC Authority record exists with heading X", NOT "An **Active** MARC Authority record" — MARC Authority / Instance / Holdings / Item records have no "Active" state, and the team doesn't use the word for them (tester feedback). Reserve status words for records where the status is a real, named field value in that area (an **Active** Budget/Fund/Ledger in Finance, an **Active** Organization, an order in **Pending/Open/Closed**). When unsure whether a status term is real for a record type, check the context file rather than adding a default adjective.
- Expected result must be a concrete, observable UI or system state.
- **Keep expected results short and observable — never pad them with rationale, ticket-scope reasoning, or hedging essays.** The Expected Result field states *what the executor should see*, in as few words as possible (`"Edit" and "Delete" are absent from the Actions menu` — not a paragraph explaining which Jira ticket requires that and which other ticket doesn't gate it). Do NOT write meta-commentary like "these two restrictions are explicitly in scope for MODDICONV-436 (not gated by UIDATIMP-1768)…" or multi-sentence justifications about unshipped tickets — that reasoning belongs in the story/PR discussion, not in a test step (tester feedback). If an expected result reads like an explanation or an argument, cut it down to the single checkable state. When a result has several discrete observable facts, use short bullets (per the multi-part rule above), each a terse observable — not a sentence of prose each.
- **HARD RULE — a verification of 2+ discrete `field = value` pairs (or ANY field=value where a value is itself a long phrase/sentence) is ALWAYS a lead-in line + bullets, never a semicolon run-on.** This overrides "Prose first" below. A record/detail-view/summary check that reads a list of fields is an *inventory*, not one observation. (Two short facts like a toast + a resulting state may stay prose joined by a semicolon — as in the golden Example 1 — but the moment you're listing named fields, or one value is a full sentence, bullet it.) ❌ NEVER write:

  ```
  Expected: Detail view shows Name = "X"; Description = "…"; Action = "Delete"; FOLIO record type = "Authority"; linked Field mapping profile = "X"
  ```

  ✅ ALWAYS write:

  ```
  Expected: Action profile detail view shows:
  - Name = "X"
  - Description = "…"
  - Action = "Delete"
  - FOLIO record type = "Authority"
  - Linked Field mapping profile = "X"
  ```

  A chain of `A = …; B = …; C = …` separated by semicolons is the exact "wall of text" testers keep rejecting — semicolon-joined field lists are the trigger. If you typed a second `; <Field> =`, convert the whole thing to bullets.
- **Prose first only for a single coherent observation.** The team packs a *single* observation into one sentence — e.g. *"Modal appears with message Route <title> (<material type>) (Barcode: <barcode>) to <Service point S>. Print slip is checked by default."* That is one modal message + its default state, not a field inventory, so it stays prose. Prose is for: a toast, a modal message, a status change, a single field value, or 2–3 tightly-related facts that read as one natural sentence. The moment the result becomes a *list of independently-checkable field values, columns, or budget buckets*, switch to bullets (see the HARD RULE above). Don't explode a single coherent observation into bullets just because it mentions three nouns — but don't cram a real field-list into one line either.
- For modal dialogs, verify the elements relevant to the scenario inline with the trigger step. Add a dedicated full-inventory step only when the modal itself is the subject under test, or when validating a complex enabled/disabled state matrix.
- For list/table verifications, list the exact columns expected.
- When a modal has interactive buttons that change form state (Swap, Recalculate, Calculate), add a dedicated scenario for that button — fields, error messages, and button states must update correctly after clicking it.
- When a step has a genuine execution caveat, add **one short `NOTE:` sentence** inside the expected result — not a paragraph. A `NOTE:` is for a real caveat that changes how the executor judges pass/fail (e.g. `NOTE: known display bug MODX-123 may show "Updated" — verify at the record`), never a place to explain ticket scope, hedge about unshipped work, or justify the assertion. If you're tempted to write two or more sentences of NOTE, delete it — the expected state itself should carry the information.
- **For ECS cases:** after every action in one tenant, add a verification step in the other tenant if the story requires cross-tenant consistency. Name the tenant explicitly in both action and expected result. Tenant switching is its own step with its own expected result.
- Cover scenario types in order: happy path → business-rule verification → edge cases → negative → capability boundaries.

**Don'ts ✗**
- Don't write vague expected results: "works correctly", "is successful", "confirming X is displayed"
- Don't pad expected results (or NOTE lines) with rationale, ticket-scope reasoning, or hedging about unshipped work — state the observable result tersely and stop
- Don't write relative value assertions: "increased by", "reduced accordingly"
- Don't skip expected results for intermediate steps
- Don't bundle multiple user roles into one test case — one role per case
- Don't omit capability boundary scenarios when the story involves roles or restrictions
- Don't list a legacy permission instead of a capability set (the Okapi line is allowed only alongside capabilities, where the section uses it)
- Don't combine UI element verification with action steps
- Don't group assertion steps — grouping is for navigation/setup clicks only
- Don't use `→` inside a single step to chain actions across verification points
- Don't use `|` as a title separator
- Don't invent UI labels, statuses, or toast texts that contradict the context file or examples

