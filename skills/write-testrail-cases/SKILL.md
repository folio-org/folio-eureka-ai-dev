---
name: write-testrail-cases
description: Use when writing, generating, or adding manual test cases to TestRail. Produces structured cases with preconditions, step-by-step actions with expected results, and all required metadata fields. Also use when asked to cover a User Story with test cases, prepare cases for a new feature, or post cases to a TestRail section via API.
---

# Write TestRail Cases

> **Core principle:** A test case exists to verify a business rule, not to document a click path. Navigation is the means; assertions about the resulting state are the point. A case whose expected results could be true even if the feature were broken is a failed case.

## Mandatory Workflow (follow in this exact order)

1. **Detect the application area** from the story (see Area Detection below) and **read the matching context file** in `references/context/`. Never skip this. If the area cannot be determined, ask the user.

   **1b. Assess context quality.** After reading the context file, check if enrichment is needed (see Lightweight Context Enrichment below). Trigger enrichment automatically if ANY of these are true:
   - Context file does not exist
   - File header says DRAFT
   - File has fewer than 10 Key Business Rules
   - File has no "Exact UI Texts" section or fewer than 3 confirmed toasts
   - File has more than 5 items in "Known Gaps / Items to Verify"

2. **Read `references/examples.md`** — golden cases from the team's TestRail. New cases must match their verification depth and style.
3. **Read the User Story / Jira ticket** (fetch via Jira MCP if an ID is given). Extract: Summary, Description, Acceptance Criteria, Development Team (→ `custom_dev_team`), the story's own ticket key (→ `refs`). **`refs` is the key(s) the user explicitly gave or the story being covered — never linked bugs, subtasks, parent epics, or review tasks**, even if Jira shows them as related.
4. **Map the story to the context file's "Key Business Rules"** section: list every rule the story touches or changes. Each touched rule is a scenario candidate. Each acceptance criterion is a scenario candidate.head -2 ~/Library/CloudStorage/OneDrive-EPAM/teams_coverage_long.csv
5. **Perform Scenario Analysis** and present the scenario list to the user for confirmation (format below). Wait for confirmation.
6. **Generate cases**, one per confirmed scenario, following the Writing Guidelines and Step Patterns.
7. **Self-review every case** against the Self-review gate before showing it. Fix violations silently.
8. **Ask for the TestRail Section ID**, show the posting preview, wait for explicit confirmation, then post via API.

---

## Lightweight Context Enrichment

> Runs automatically when triggered by step 1b. This is NOT a full `build-app-context` run — it is fast and targeted to the specific story. Do not write anything to disk.

### What to fetch

**GitHub — max 3 files, in priority order:**

1. `translations/<ui-module>/en_US.json` — extract values for translation keys that contain the story's main feature keywords (e.g. if story is about "batch allocation", extract keys containing "batch", "allocation", "budget"). Use the GitHub repo from the area detection table.
2. `package.json` → `stripes.permissionSets` — extract all `permissionName` / `displayName` values as candidate Capability Set names.
3. One Cypress fragment file from `stripes-testing/cypress/support/fragments/<area>/` that matches the story's feature — extract UI label strings and selector names.

**Jira — story + directly linked issues only:**

- The story itself is already fetched in step 3 — reuse it.
- Fetch all issues directly linked to the story: subtasks, related bugs, parent epic (one API call each).
- Extract acceptance criteria from each linked issue → additional business rule candidates.
- **These linked issues are a context source only — never add their keys to `refs`.** `refs` always stays exactly what step 3 set (the story's own key, or whatever the user explicitly provided).

### What NOT to fetch

- All closed stories for the component — that is `build-app-context` scope.
- All bugs for the component.
- More than 3 GitHub files.
- Any file larger than 150 KB.

### How to use enriched data

- Add extracted strings to in-memory context for this session only.
- Do NOT write to the context file on disk — context files are read-only for this skill.
- In the Scenario Analysis output, add a note:

  > ⚠️ Context was enriched from GitHub/Jira for this session (context file triggered enrichment). Run `build-app-context` to make the enrichment permanent.

- If enrichment also returns zero useful data (GitHub unreachable, Jira returns nothing) — proceed with what the context file has and note it in Scenario Analysis:

  > ⚠️ Context enrichment attempted but returned no additional data. Cases are based on the existing context file only — verify domain-specific details on first execution.

---

## Area Detection and Context Files

Context files live in `references/context/`. Determine the area from (in priority order): **the apps and entities actually described in the story text**, the Development Team field, and only then the Jira project prefix as a hint. **If the story content contradicts the prefix mapping, trust the story content.** Confirm your detection in one line ("Story describes <X> — loading <file> context") rather than asking, unless detection is ambiguous — then ask.

**The story itself is the source of truth.** If the user's instructions contradict the story (e.g. "this is not an ECS story" while the story has an `ecs` label, mentions tenants/affiliations, or lives in a consortia module), do not silently follow either side — flag the conflict in one line and ask which to trust before generating. The same applies to ECS Enabled: derive it from the story's labels and text, not from assumptions.

| Area | Context file | Jira prefixes / keywords |
|---|---|---|
| Agreements | `references/context/agreements.md` | ERM, UIAG; "agreement", "agreement line", "SAS" |
| Bulk Edit | `references/context/bulk-edit.md` | UIBULKED, MODBULKOPS; "bulk edit", "identifier", "in-app", "commit changes", "preview of records matched", "errors accordion", "reason for error", "bulk edit profile", "query builder", "matched records", "suppress from discovery" |
| Check In | `references/context/check-in.md` | UICHKIN, CIRC; "check in", "return", "backdate" |
| Check Out | `references/context/check-out.md` | UICHKOUT, CIRC; "check out", "loan", "patron block" |
| Orders | `references/context/orders.md` | UIOR, MODORDERS; "purchase order", "POL", "PO line", "encumbrance", "fund distribution", "order template", "open order", "unopen", "reopen", "claiming", "donor information", "bindery active", "routing list", "acquisitions unit" |
| Invoices | `references/context/invoices.md` | UINV, MODINVOICE, MODINVOSTO; "invoice", "invoice line", "voucher", "approve invoice", "pay invoice", "cancel invoice", "pending payment", "lock total", "release encumbrance", "batch group", "adjustment", "pro rate", "export to accounting", "vendor invoice number", "approve and pay in one click", "update order status", "duplicate invoice" |
| Receiving | `references/context/receiving.md` | UIREC; "piece", "receive", "receiving title" |
| Finance | `references/context/finance.md` | UIF, MODFIN; "fund", "budget", "ledger", "fiscal year", "allocation", "encumbrance", "transfer", "rollover", "expense class", "acquisition unit" |
| Inventory | `references/context/inventory.md` | UIIN, MODINV; "instance", "holdings", "item" |
| Requests | `references/context/requests.md` | UIREQ; "request", "hold", "page", "recall", "pickup" |
| Mediated Requests | `references/context/mediated-requests.md` | UIREQMED, MODREQMED; "mediated request", "secure tenant", "secure request", "interim service point" |
| Users | `references/context/users.md` | UIU, MODUSERS; "patron", "user record", "custom fields", "proxy", "service points", "profile picture" |
| Data Import | `references/context/data-import.md` | UIDATIMP, MODDATAIMP, MODDICORE, MODSOURMAN, MODSOURCE, MODELINKS; "import", "job profile", "match profile", "action profile", "field mapping profile", "data import", "MARC import", "EDIFACT import", "LDR 05", "MARC Holdings", "file extension" |
| Data Export | `references/context/data-export.md` | UIDEXP, MDEXP; "export", "mapping profile", ".mrc" |
| MARC Authority | `references/context/marc-authority.md` | UIMARCAUTH, MODELINKS; "authority", "quickMARC" |
| eHoldings | `references/context/eholdings.md` | UIEH; "package", "title", "provider", "KB", "EBSCO" |
| Licenses | `references/context/licenses.md` | UILIC, MODLIC, ERM; "license", "amendment", "term", "core document", "supplementary document" |
| Lists | `references/context/lists.md` | UILISTS, MODLISTS, MODFQM; "list", "FQM", "query" |
| OAI-PMH | `references/context/oai-pmh.md` | MODOAIPMH; "harvest", "OAI" |
| Consortium Manager | `references/context/consortium-manager.md` | UICONSET (ui-consortia-settings), MODCON; "consortium", "ECS", "affiliation", "shared setting", "central tenant", "member tenant", "select members", "confirm share to all", "confirm member libraries", "authorization roles", "authorization policies", "data import logs", "data export logs" |

A story can span two areas (e.g. closing an order affects Finance) — read both context files.

If a context file for the detected area does not exist, notify the user:
> "I don't have a context file for this area yet. I'll generate cases based on the User Story alone — results may be less accurate for domain-specific preconditions."

### How to use the context file

- **Key Business Rules section is the scenario source.** For each rule the story touches, decide: does this story change the rule, depend on it, or risk breaking it? Touched rules become scenarios.
- Use the domain model to write realistic preconditions: which records must exist, in what status, with what values (e.g. an encumbrance requires a Fund, a Budget in an active Fiscal Year, an Open PO with a POL fund distribution).
- Use documented side effects to build verification steps: if the context file says an action touches N entities (e.g. PO Close → encumbrance released, budget Available restored, PO status + reason for closure, POL statuses), the case verifies ALL of them.
- Use exact terminology from the context file (statuses, field names, transaction types) — never invent UI labels.

### Context file protection rule

Context files in `references/context/` are read-only for this skill.
Never modify, overwrite, or delete context files when running write-testrail-cases.
If a context file appears outdated, notify the user and suggest running build-app-context to refresh it.

---

## Scenario Analysis

Before generating cases, present:

```
I've read the story (refs: XXX-123) and the <area> context. Business rules touched: <rule numbers/short names>.

Here are the scenarios I plan to cover:

Happy path:
1. User can successfully [main action] with valid data → Critical Path

Business-rule verification:
2. [action] releases/creates/updates [entity] with [exact state] → Critical Path

UI verification:
3. [page/modal] shows all required elements on open → Extended

Capability boundaries:
4. User without [Capability Set] cannot [action] → Critical Path

Negative / edge cases:
5. [action] fails when [condition] → Extended

Does this coverage look complete? Any scenarios to add or remove before I write the cases?
```

Wait for the user's confirmation or corrections before proceeding.

### Journey vs atomic cases

Choose the case granularity to match the story type:

- **Lifecycle / workflow stories** (a process with checkpoints: request lifecycle with notices, order open→receive→pay, import job stages) → write **one journey case per flow variant**, walking through the whole lifecycle and verifying every checkpoint along the way (like the team's mediated-request notice cases: create → notice → transit → arrival → pickup → notice → cancel → notice in a single case). Flow variants (Page vs Hold, item-level vs title-level) become separate journey cases, not separate per-checkpoint cases.
- **Feature / element stories** (a new column, modal, validation, setting) → atomic cases per scenario as usual.

Never split one lifecycle into per-checkpoint stubs — an executor would have to rebuild the same preconditions N times, and intermediate state transitions would go unverified.

### Verify effects at their real destination

Assert the end effect where it actually lands, not at a convenient proxy:
- Notices → check the **mailbox** from preconditions: exact subject + body contains the configured item/title/patron tokens. The Circulation log "Notice sent" entry may be an additional check, never the only one.
- Exports → download and check the produced file, not only the log row.
- Finance effects → the transaction and budget values, not only a toast.

### Scenario Coverage Checklist

For every User Story, consider:
- [ ] Primary happy path (valid data, expected flow, correct end state)
- [ ] **Every Key Business Rule the story touches — verified by explicit state assertions**
- [ ] UI element verification (buttons, labels, columns, counts — especially for new pages)
- [ ] Edit and duplicate flows (where applicable)
- [ ] Delete flow including: Cancel button, confirm delete, verify removal from list
- [ ] Capability boundaries: restricted user cannot perform actions outside their Capability Sets — and the case also asserts what the restricted user still CAN see/do
- [ ] Negative cases: invalid input, wrong profile, empty files, referenced records blocking deletion
- [ ] Edge cases: repeated UUIDs, records referenced in multiple places, boundary values
- [ ] Status field changes (exact before/after values)
- [ ] Toast messages: exact text with placeholders — never just "success toast"
- [ ] Modal element verification: key elements are verified inline on first open; full modal inventory is used only when the modal itself is under test
- [ ] Interactive modal buttons (Swap, Recalculate): dedicated scenario verifying fields, errors, and button states update after clicking
- [ ] Multi-tenant / ECS behavior (only if applicable to the story)
- [ ] Drag and drop / reordering (if the story involves record order)
- [ ] Multi-tab behavior (only if the story explicitly covers concurrent editing — rare pattern, see end of Step Patterns)
- [ ] Inline edit flows: Save/Cancel appear inline, Save disabled until change made, row returns to read-only on Cancel
- [ ] Multi-select dropdowns: all options shown, dropdown stays open after selection, Save enables/disables correctly
- [ ] Search & filter pane: all accordions with correct initial expanded/collapsed state; Search/Reset buttons disabled by default
- [ ] Pagination: paginator appears when results exceed page limit; total count matches header
- [ ] Date range filters: From/To fields appear on accordion expand; results filter correctly
- [ ] Load/performance (if story involves bulk operations — mark as Extended)

---

## Test Case Structure

Every test case has these sections (in order):

**Metadata** — Type, Priority, Release, Test Group, References, and other classification fields.
**Preconditions** — numbered list: all users with their Capability Sets, required data setup with exact values, and starting system state.
**Steps** — actions with a concrete expected result for each step.

### Template

```
Title: [Actor/Subject] [verb] [object] [condition]

Type:               Other
Priority:           [Critical | High | Medium | Low — choose based on impact]
Release:            Umbrellaleaf
Test Group:         [Smoke | Critical Path | Extended — required]
User Journey:       No
Multi-Tenant:       No
Bug Created:        No
Unstable:           No
ECS Enabled:        No   [set to Yes only when the story explicitly tests ECS/cross-tenant behavior]
ECS Unsupported:    No   [fixed default — never ask]
Capabilities Ready: Yes
Execution Type:     Manual   [required]
Dev Team:           [Value from "Development Team" field in the User Story]
Customer Name:      [All | MOBIUS/GALILEO | LOC — only if the story targets a specific customer]
Labels:             AI   [always added to every case]
References:         [Jira ticket IDs, comma-separated, e.g. MODFIN-273, UIF-657]

Preconditions:
1. User A with following Capability Sets exists:
   - Data - [Module] [Resource] - [Action]
   - Procedural - [Module] [Resource] - [Action]
2. User B (admin user with all FOLIO Capability Sets) is logged in
3. [Required record with exact values, e.g. Fund A is Active; budget Fund A-FY-current: Allocated = 200.00, Encumbered = 50.00, Available = 150.00]
4. [More data as needed — one numbered entry per record/state so steps can reference "Preconditions #3"]
5. User B is on [Starting app/page]

Steps:
1. Action:   [verb] [object] on [location] — navigation/setup clicks may be grouped as a bullet list inside one step when they share a single verification point
   Expected: [Observable UI or system result — bullet list when 3+ distinct items]

2. Action:   [verb] [entity] from Preconditions #N
   Expected: [Column-by-column / field-by-field assertion with exact values]
```

---

## Title Format Rules

Use a plain descriptive sentence — no prefixes, no labels.

**Format:** `[Actor/Subject] [verb] [object] [condition]`

**Do's ✓**
- `User with Edit capability set can create locked mapping profile`
- `Mapping profile Status column shows Locked after lock checkbox is enabled`
- `Delete mapping profile modal shows all required elements`
- `Holdings export fails when submitted file contains invalid UUIDs`
- `Search filters mapping profiles by name and FOLIO record type`
- `User can create a multi-select custom field` ← always include actor ("User can...")
- `User can check out requested item in Central tenant` ← ECS case: no prefix needed, tenant context is in the title

**Don'ts ✗**
- ~~`Verify mapping profile creation`~~ — too vague, no subject or condition
- ~~`Create a text field custom field`~~ — missing actor; rewrite as `User can create a text field custom field`
- ~~`Verify that final custom field can be removed`~~ — don't start with "Verify that"
- ~~`Negative: Holdings export with invalid UUIDs`~~ — no prefixes
- ~~`ECS | Delete locked mapping profile`~~ — no pipe-style prefixes
- ~~`Load testing - Export 500k records`~~ — no prefixes
- ~~`Test that user can create profile`~~ — don't start with "Test that"

> **ECS title exception:** You may use `[ECS <Area>]` prefix only when the test is exclusively ECS-specific and the area label adds essential disambiguation — e.g. `[ECS Loans] User can check out requested item in Central tenant`. Use sparingly; prefer embedding the tenant context in the title sentence itself.

> **Note:** the Title is the one place actor naming ("User can...") is used. Steps below use imperative style instead — see Writing Guidelines.

---

## Writing Guidelines

> Write every test case as if it will be executed by a QA engineer who has never seen this feature before. Steps must be precise enough that any team member — Firebird, Spitfire, Vega, Volaris, Thunderjet — can execute the case without guessing. Same level of detail regardless of team or area.

### Preconditions

All environments are Eureka. Always use Capability Sets — never legacy permissions.

- **Number every precondition** (1., 2., 3., ...) so steps can reference them as "Preconditions #N". One record or state per entry. **The list must be flat**: each user, each data record, and the starting page are separate top-level numbered items. Sub-bullets are allowed only for listing Capability Sets under a user entry — never for nesting data records or login state under another item. Before finalizing, check that every "Preconditions #N" referenced in steps resolves to an actual top-level item N.
- List all required users with their exact Capability Sets, e.g.:
  ```
  Data - UI-Data-Export Settings - Edit
  Data - UI-Data-Export Settings Lock - Edit
  ```
- List required data with **exact values for everything a step will later assert**: monetary amounts, statuses, counts, relationships. If a step will verify `Available = 200.00`, the precondition must establish the starting `Available = 150.00 (Allocated 200.00 − Encumbered 50.00)`.
- List the starting system state (which app or page the user is on).
- Use named actors consistently: User A / User B. (Actor names live in Preconditions only — see Steps below for step phrasing.)
- **For ECS cases:** always specify which tenant each data record belongs to (Central or member tenant name), which service points are configured, and what affiliation the user starts with:
  ```
  1. Active Ledger exists in Central tenant for the current fiscal year
  2. Fund A (Allocated = 200.00) exists in member tenant (College), related to the Ledger above
  3. User B is logged in with affiliation set to Central tenant
  4. Item with barcode 12345 exists in member tenant, status Available
  5. Pickup service point SP-Central is configured in Central tenant
  ```

### Steps — Case Shape (match the golden examples)

1. **Entry**: grouped navigation step(s) from the app entry point, each with a real verification (pane opened, exact counts like "3 members selected", buttons with states).
2. **First-open context**: when the case lands on its target pane/modal for the first time, verify the key elements relevant to the scenario — columns, labels, button states, counts. A full element-by-element inventory step is only needed when the pane/modal itself is the subject under test.
3. **Business assertions**: per-row / per-field verification steps — the core of the case.
4. **Interaction + re-verification** (when the scenario involves changing state): perform the change, then re-assert the new exact state (new counts, rows appearing/disappearing).

Sizing: a typical case is **5–10 steps** (team median is 9). A case with 3 or fewer steps is a self-review failure unless the scenario is genuinely a single trivial assertion — if it feels too small, the navigation and context verification are probably missing, or the scenario should be merged with a sibling.

**Preconditions hold only data and state that exists before the test starts** (records, users, configuration, login, starting app). Any action the user performs in the UI during the test — selecting members, switching tabs, opening panes, applying filters — is a step with its own expected result, never a precondition. "User is on <page> with all 3 members selected" is wrong: member selection is a step (and per the golden examples, the selection modal itself gets verified).

### Steps — Business-Logic Verification (the most important rules)

- **Every case must verify the business rule outcome, not just the UI mechanics of triggering it.** The trigger flow (menus, modals, Submit) is compressed; the state verification is detailed.
- **Absolute values, never relative.** Write `Encumbered = 0.00`, `Available = 200.00 (restored to full allocation)` — never "increased by 50.00" or "decreased accordingly". The executor must be able to compare a number on screen with a number in the case.
- **Verify all entities the action touches**, per the context file. Example — closing a PO must assert: encumbrance transaction status, budget values, PO status and "Reason for closure" on the PO record, POL receipt/payment statuses.
- **Prefer explicit column-level verification for business-critical tables.** Never "transaction is displayed" for transaction or budget-value tables — assert exact values such as `Type = "Encumbrance"`, `Source = <PO number>`, `Amount = $50.00`, `Status = "Released"`. A concise summary assertion is acceptable for navigation/lookup tables where it still proves the intended behavior.
- **Reference preconditions by number** in steps: "the unlocked mapping profile from Preconditions #3".
- **Toast messages: exact text with placeholders**, e.g. `"<amount> was successfully allocated to the budget <Fund-FY>"`. Never "success toast is displayed". If the exact text is unknown and not in the context file or examples, write the most likely exact text and flag it: `(verify exact wording on first execution)`.

### Steps — Granularity and Format

- **Navigation/setup actions may be grouped into one step** as a bullet list when they share a single verification point (see examples.md, Example 1, step 1). Verification/assertion actions are never grouped — one assertion target per step.
- **Use imperative style in steps**: "Click ...", "Navigate to ...", "Select ...", "Open ...". Do not prefix steps with an actor name (no "User B clicks") — actors are defined once in Preconditions, not repeated in every step.
- Expected result must be a concrete, observable UI or system state.
- Use a bullet list when the expected result has **three or more distinct observable items**, or when each item needs separate reviewer attention. For one to two tightly related observations, a single-line expected result is fine.
- For modal dialogs, verify the elements relevant to the scenario inline with the trigger step. Add a dedicated full-inventory step only when the modal itself is the subject under test, or when validating a complex enabled/disabled state matrix.
- For list/table verifications, list the exact columns expected.
- When a modal has interactive buttons that change form state (Swap, Recalculate, Calculate), add a dedicated scenario for that button — fields, error messages, and button states must update correctly after clicking it.
- When a step has important caveats affecting execution, add a `NOTE:` line inside the expected result.
- **For ECS cases:** after every action in one tenant, add a verification step in the other tenant if the story requires cross-tenant consistency. Name the tenant explicitly in both action and expected result. Tenant switching is its own step with its own expected result.
- Cover scenario types in order: happy path → business-rule verification → edge cases → negative → capability boundaries.

**Don'ts ✗**
- Don't write vague expected results: "works correctly", "is successful", "confirming X is displayed"
- Don't write relative value assertions: "increased by", "reduced accordingly"
- Don't skip expected results for intermediate steps
- Don't bundle multiple user roles into one test case — one role per case
- Don't omit capability boundary scenarios when the story involves roles or restrictions
- Don't use legacy permission names — always use Capability Sets
- Don't combine UI element verification with action steps
- Don't group assertion steps — grouping is for navigation/setup clicks only
- Don't use `→` inside a single step to chain actions across verification points
- Don't use `|` as a title separator
- Don't invent UI labels, statuses, or toast texts that contradict the context file or examples

### Self-review gate (run before showing any case)

For each generated case, check:
- [ ] Case has a navigation/entry step, business assertion step(s), and (if state changes) a re-verification step? A 2–3 step case is a failure by default unless genuinely trivial.
- [ ] Are preconditions data/state only — no in-test UI actions hidden in them?
- [ ] Does at least one step assert the business-rule outcome with exact values? If every expected result could pass on a broken feature — rewrite.
- [ ] Are all touched entities from the context file verified?
- [ ] All numbers absolute? All toasts verbatim?
- [ ] Business-critical tables (transactions, budgets) verified column-by-column?
- [ ] Preconditions numbered, with starting values for everything asserted later?
- [ ] Steps reference "Preconditions #N" where data is used?
- [ ] Steps use imperative style, no actor prefix?
- [ ] Verification density comparable to references/examples.md?

---

## Step Patterns from the Backlog

> Common patterns first. Two rare patterns (multi-tab, DevTools/Network) are at the end of this section, marked accordingly — skip them unless the story explicitly requires that exact scenario.

**Grouped navigation (single verification point):**
```
1. Action:
   - Click "Consortium manager" app button in the header
   - Click "Select members" button
   - Check all members
   - Click "Save & close" button
   Expected:
   - "Consortium manager" app main page is opened including:
     - "Settings" pane with the settings list in alphabetical order
     - "3 members selected" text
     - "Select members" button (active)
```

**Navigating to a page:**
```
1. Action:   Navigate to Settings > Data export > Field mapping profiles
   Expected: "Field mapping profiles" pane is displayed with "New" button, search box, and table with profiles
```
> Always use `>` as the navigation separator: `Settings > Inventory > Call number browse`.

**Opening an Actions menu:**
```
2. Action:   Click "Actions" menu on the mapping profile view form
   Expected: Menu expands and displays the following options: Edit, Duplicate, Delete
```

**Confirming a modal:**
```
3. Action:   Click "Delete" button on "Delete mapping profile" modal
   Expected: Modal closes, toast message "Mapping profile <name> has been successfully deleted" is displayed, profile is removed from the list
```

**Verifying a transaction/table row (column-level):**
```
4. Action:   Navigate to Finance app > Fund A > Fund A-FY-current budget > "Transactions" accordion and open the encumbrance row for the PO from Preconditions #4
   Expected: Transaction details pane displays:
             - "Type" = "Encumbrance"
             - "Source" = <PO number> (hyperlink to the PO)
             - "Amount" = $50.00
             - "Status" = "Released"
             - "Initial encumbrance" = $50.00
             - "Expended" = $0.00
```

**Verifying budget values (absolute):**
```
5. Action:   Check the budget summary for Fund A-FY-current
   Expected: - "Allocated" = $200.00
             - "Encumbered" = $0.00
             - "Available" = $200.00 (restored to full allocation)
```

**Verifying table columns:**
```
6. Action:   Verify columns in the "Field mapping profiles" table
   Expected: Table includes the following columns: Name, FOLIO record type, Format, Updated, Updated by, Status
```

**File export flow:**
```
1. Action:   Click "or choose file" button on the Jobs pane and submit a .csv file with UUIDs
   Expected: "Select job profile to run the export" modal opens with list of job profiles, search box, and disabled "Search" button

2. Action:   Click "Default holdings export job profile"
   Expected: "Are you sure you want to run this job?" modal opens with dropdown list, "Cancel" button (enabled), "Run" button (disabled)

3. Action:   Select "Holdings" from the dropdown list
   Expected: "Run" button becomes enabled

4. Action:   Click "Run" button
   Expected: Job starts; progress bar is visible in "Running" section; after completion, "Logs" pane displays new row with .mrc file as hyperlink, "Completed" status, Total = 5, Exported = 5, Failed = 0
```

**Inline edit in table (pencil icon):**
```
1. Action:   Click the "Edit" (pencil) icon next to the "Call numbers (all)" row in the table
   Expected: "Call number types" column of that row switches to an enabled multi-select dropdown; "Cancel" button (enabled) and "Save" button (disabled) appear in the "Actions" column

2. Action:   Click "Cancel" button in the "Actions" column
   Expected: Row returns to read-only state; no changes are saved
```

**Multi-select dropdown verification:**
```
1. Action:   Click the multi-select dropdown in the "Call number types" column
   Expected: Dropdown expands and displays all available options in alphabetical order; each option has a checkbox; no options are pre-selected

2. Action:   Select options one by one from the multi-select dropdown
   Expected: Each selected option appears in the input field; dropdown remains open after each selection; "Save" button becomes enabled after at least one option is selected

3. Action:   Remove all selected options from the multi-select dropdown
   Expected: Input field is empty; "Save" button becomes disabled again
```

**Drag and drop (reordering):**
```
1. Action:   Hover over the drag handle (six-dots icon) next to the custom field record
   Expected: "Change custom field order" tooltip appears; cursor changes to grab

2. Action:   Drag the custom field record to a new position in the list
   Expected: Custom field moves to the new position; order is updated in the list
```

**Tenant switching (ECS cases):**
```
1. Action:   Switch affiliation to Central tenant via the service point menu (top right) > Switch active affiliation
   Expected: Active tenant changes to Central; page reloads showing Central tenant context
```

**Cross-tenant verification (ECS cases):**
```
1. Action:   Switch affiliation to member tenant and open Loan details page for Item 1 via Circulation log
   Expected: Loan details page opened in member tenant; renewal action displayed in the actions list; due date matches the due date from the Central tenant loan
```

**Barcode scanning — patron (Circulation):**
```
1. Action:   Open "Check out" app and enter patron barcode on the "Scan patron card" pane, then click "Enter"
   Expected: Patron scanned; patron name and details displayed on the left pane
```

**Barcode scanning — item (Circulation):**
```
2. Action:   Enter item barcode on the "Scan items" pane and click "Enter"
   Expected: Item scanned; loan created; item row appears in the scanned items list with status "Checked out"
```

**Accordion expansion:**
```
1. Action:   Expand "Loans" accordion on the user details page
   Expected: "Loans" accordion expands and displays "# open loans" and "# closed loans" hyperlinks

2. Action:   Click "# closed loans" hyperlink
   Expected: "Loans" page opens with "Closed loans" tab active; loan from Preconditions #3 is displayed in the list
```

**Search & filter pane verification:**
```
1. Action:   Click "View all" button in the "Logs" pane
   Expected: Page updates with "Search & filter" pane on the left and "Logs" main pane; "Search & filter" pane contains:
             - "ID" dropdown
             - Search box
             - "Search" button (disabled)
             - "Reset all" button (disabled)
             - "Errors in export" accordion (expanded)
             - "Started running" accordion (collapsed)
             - "Ended running" accordion (collapsed)
             - "Job profile" accordion (collapsed)
             - "User" accordion (collapsed)
```
> Always list all filter accordions with their initial expanded/collapsed state, and Search/Reset buttons with their initial enabled/disabled state.

**Pagination verification:**
```
1. Action:   Scroll to the bottom of the results table
   Expected: Paginator is displayed below the table; page navigation controls are visible; total records count matches the number shown in the header
```

**Date range filter (date picker):**
```
1. Action:   Expand "Started running" accordion in the "Search & filter" pane
   Expected: "Started running" accordion expands and displays "From" and "To" date/time fields

2. Action:   Fill in "From" and "To" date fields, then click "Apply"
   Expected: Results table shows only records within the specified date range; records count updates accordingly
```

> **Rare patterns below — use only when the story explicitly requires this exact scenario.**

**Multi-tab testing (only when the story explicitly tests concurrent tabs):**
```
1. Action:   Duplicate the current browser tab while the edit form is open
   Expected: Edit form opens in the second tab showing the same state as the first tab

2. Action:   Save changes in the first tab
   Expected: Changes saved successfully in the first tab

3. Action:   Switch to the second tab and attempt to save different changes
   Expected: [expected conflict/success behavior per story requirements]
```

**DevTools / Network verification (only when the story requires verifying API response or hidden fields):**
```
1. Action:   Open browser DevTools (F12) and navigate to the Network tab
   Expected: DevTools pane is open; Network tab is active and recording requests

2. Action:   Perform the action that triggers the relevant API call
   Expected: Network tab captures the /custom-fields request; response body contains [expected field/value]; UI does NOT display [hidden field]
```

---

## Test Group Rules

- **Smoke** — Core feature works at all. The single most critical happy path that would immediately break the feature if it failed. Typically 1 case per feature area.
- **Critical Path** — Essential functionality users depend on daily: create, edit, delete, key permissions and capability boundary checks, export/import flows, status transitions, business-rule verifications.
- **Extended** — Less frequent but important: search and filtering, UI element verification, page title checks, edge cases, negative cases, load/performance, complex multi-step workflows.

Pattern observed in backlog: most cases are Critical Path or Extended. Smoke is rare (1-2 per feature area).

---

## Metadata Fields Reference

> **Resolve IDs at runtime.** Dropdown fields (Type, Priority, Release, Test Group, Execution Type, Dev Team, Customer Name, Automation Scope/Team/For) take a **numeric option ID**, not the label string — sending a label returns `400 Field :<name> is not a valid natural number`. Look up the current IDs with `GET /index.php?/api/v2/get_priorities`, `get_case_types`, and `get_case_fields`. Checkbox fields take a JSON **boolean** (`true` / `false`). The option IDs below are a snapshot from `foliotest.testrail.io` and may change — always confirm via the API.
>
> **Required fields:** `custom_test_group` and `custom_automation_type` (labelled "Execution Type"). A case will not post without them.
>
> **Standing defaults (do not ask the user):** `ECS Unsupported = false` on every case, and **every case gets the "AI" label**. Set `ECS Enabled = true` only when the story explicitly tests cross-tenant / ECS behavior.

| Field | TestRail API key | Type | Default | Options / Notes (current IDs) |
|---|---|---|---|---|
| Title | `title` | string | — | Plain descriptive sentence; no prefixes ("Verify", "Negative:", "ECS \|", "Load testing -") |
| Type | `type_id` | dropdown (id) | `Other` | Resolve via `get_case_types`. Current: **Other=7** |
| Priority | `priority_id` | dropdown (id) | — | Resolve via `get_priorities`. Current: Low=1, Medium=2, High=3, Critical=4 |
| Release | `custom_release` | dropdown (id) | latest release | Current latest: **R2 2026 Umbrellaleaf=21**, R1 2026 Trillium=20, R1 2025 Sunflower=19 |
| Test Group | `custom_test_group` | dropdown (id) | — | **Required.** Smoke=1, Critical Path=2, Extended=3, Obsolete=4, Draft=5, Backend=6, Edge Cases=7 |
| Execution Type | `custom_automation_type` | dropdown (id) | `Manual` (2) | **Required.** Automated=1, Manual=2, Karate=3, Unit=4, Backend Component=5 (TestRail label is "Execution Type"; API key is `custom_automation_type`) |
| User Journey | `custom_user_journey` | checkbox (bool) | `false` | `true` / `false` |
| Multi-Tenant | `custom_multi_tenant` | checkbox (bool) | `false` | `true` / `false` |
| Bug Created | `custom_bug_created` | checkbox (bool) | `false` | `true` / `false` |
| Unstable | `custom_unstable` | checkbox (bool) | `false` | `true` / `false` |
| ECS Enabled | `custom_ecs_enabled` | checkbox (bool) | `false` | Set to `true` when the story explicitly tests ECS/cross-tenant behavior. Otherwise `false`. |
| ECS Unsupported | `custom_ecs_unsupported` | checkbox (bool) | `false` | **Always `false`. Never ask the user.** |
| Capabilities Ready | `custom_capabilities_ready` | checkbox (bool) | `true` | `true` / `false` |
| Dev Team | `custom_dev_team` | dropdown (id) | — | From "Development Team" in the story. e.g. Concorde=1, Firebird=3, Folijet=4, Spitfire=6, Thor=7, **Thunderjet=8**, Vega=9, Volaris=13, Citation=18, Eureka=21 (full list via `get_case_fields`) |
| Customer Name | `custom_customer_name` | dropdown (id) | — | Optional. All=1, MOBIUS/GALILEO=2, LOC=3 — set only when the story targets a specific customer |
| Automation Scope | `custom_automation_scope` | dropdown (id) | — | Optional; omit if N/A. Review by MQA=1, Review by PO=2, Automation Ready=3, Not an automation candidate=4, Mriya scope=5, Karate Approved=6, Karate Not Applicable=7, FE scope=8 (no "None" option) |
| Automated For | `custom_case_automated_in` | dropdown (id) | — | Optional; omit if N/A. Old releases=1, R2 2024 Ramsons=2, R1 2025 Sunflower=3, R2 2025 Trillium=4 |
| Automation Team | `custom_automation_team` | dropdown (id) | — | Optional; omit if N/A. TaaS=1, Mriya=2, FE team=3 (no "None" option) |
| References | `refs` | string | — | The story's own key(s) only — never linked bugs, subtasks, parent epics, or review tasks pulled in via enrichment |
| Labels | `labels` | array | `["AI"]` | **Always add the "AI" label to every case.** Pass label ID(s) — resolve via `get_labels/{project_id}` (on `foliotest.testrail.io`, "AI" = id **67**) — or the title string `"AI"`. |

---

## TestRail API Integration

### Credentials

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

### Jira MCP Integration

When the user provides a Jira ticket ID instead of pasting a User Story:

1. Use the Jira MCP tool to fetch the issue by ID
   - Extract: Summary, Description, Acceptance Criteria, Development Team, Fix Version
   - Use the issue key as `refs` value
   - Use Development Team field for `custom_dev_team`
2. If Jira MCP is not available — ask the user to paste the User Story manually
3. Proceed with the Mandatory Workflow as normal

### Optional: read existing cases from a TestRail section

If the user provides a Section ID for the area, fetch up to 20 existing cases as an *additional* style/content reference (the primary references are the context file and examples.md):

```
GET {TESTRAIL_URL}/index.php?/api/v2/get_cases/14&section_id={section_id}&limit=20
Authorization: Basic base64(TESTRAIL_USER:TESTRAIL_API_KEY)
```

Extract from `custom_preconds` and `custom_steps_separated`: exact UI labels, toast texts, precondition depth, step granularity. New cases must match the depth and format of the existing cases in this section. If no Section ID is provided, do not ask for one until the posting step.

### Posting preview

After generation and self-review, ask: _"Please provide the TestRail Section (folder) ID where the cases should be posted."_ Then show:

```
Ready to post 5 test cases to Section ID: XXXXX

1. User with Edit capability set can create unlocked mapping profile — Other / High / Critical Path
2. User with Edit capability set can edit unlocked mapping profile — Other / High / Critical Path
3. User with Edit capability set cannot delete mapping profile referenced in job profile — Other / High / Critical Path
4. Mapping profile "Status" column shows "Locked" after lock checkbox is enabled — Other / Medium / Extended
5. User with View-only capability set cannot see "New" or "Actions" buttons — Other / High / Critical Path

Confirm? (yes / no / edit)
```

Wait for explicit confirmation, then post.

### Add case request

```
POST /index.php?/api/v2/add_case/{section_id}
Content-Type: application/json
Authorization: Basic <base64(email:api_key)>
```

```json
{
  "title": "User with Edit capability set can delete unlocked mapping profile not referenced in job profile",
  "type_id": 7,
  "priority_id": 3,
  "refs": "MODFIN-273",
  "custom_preconds": "1. User B with following Capability Sets exists:\n  - Data - UI-Data-Export Settings - Edit\n2. User B is logged in\n3. Unlocked mapping profile NOT referenced in any job profile exists\n4. User B is on Settings > Data export > Field mapping profiles",
  "custom_steps_separated": [
    {
      "content": "Click on the row with the unlocked mapping profile from Preconditions #3",
      "expected": "Mapping profile view form is displayed; \"Lock profile\" checkbox is disabled, unchecked; \"Actions\" menu is enabled"
    },
    {
      "content": "Click \"Actions\" menu",
      "expected": "Menu expands and displays the following options: Edit, Duplicate, Delete"
    },
    {
      "content": "Click \"Delete\" option",
      "expected": "\"Delete mapping profile\" modal opens with: \"The mapping profile <name> will be deleted.\" text, \"Cancel\" button (enabled), \"Delete\" button (enabled, focused)"
    },
    {
      "content": "Click \"Cancel\" button",
      "expected": "\"Delete mapping profile\" modal closes; mapping profile view form is displayed"
    },
    {
      "content": "Click \"Actions\" menu > \"Delete\" > \"Delete\" in modal",
      "expected": "Modal closes; toast message \"Mapping profile <name> has been successfully deleted\" is displayed; \"Field mapping profiles\" pane shows list without deleted profile"
    }
  ],
  "custom_release": 21,
  "custom_test_group": 2,
  "custom_automation_type": 2,
  "custom_dev_team": 4,
  "custom_customer_name": 1,
  "custom_multi_tenant": false,
  "custom_user_journey": false,
  "custom_bug_created": false,
  "custom_unstable": false,
  "custom_ecs_enabled": false,
  "custom_ecs_unsupported": false,
  "custom_capabilities_ready": true,
  "labels": [67]
}
```

> The dropdown values above are **option IDs**, not labels. Resolve via `get_case_fields` / `get_priorities` / `get_case_types`. `custom_ecs_unsupported` is **always `false`**; `custom_ecs_enabled` is `true` only for ECS stories. `"labels": [67]` is the **"AI"** label, always added to every case.

### Success output

After posting all cases, report:
```
✅ Posted 5 test cases to Section 1042:
  C123456 — User with Edit capability set can create unlocked mapping profile
  ...
```

### Error handling

| HTTP status | Action |
|---|---|
| `401` | Credentials error — check `.env` or `~/.folio-credentials` |
| `400` | Show the full error body and identify which field caused it |
| `404` | Confirm the Section ID exists and is accessible |
| Any failure | Do not skip silently — report the failed case title and full error message |

---

## Fallback Output (no API access)

If posting via API fails entirely, output each case in this format:

```
---
Title:          [title]
Type:           Other
Priority:       [High | Medium | ...]
Release:        Umbrellaleaf
Test Group:     [Smoke | Critical Path | Extended]
Execution Type: Manual
Dev Team:       [from story]
References:     [jira_ids]

Preconditions:
1. User A with following Capability Sets exists:
   - [Capability Set 1]
2. User B (admin with all FOLIO Capability Sets) is logged in
3. [Required data with exact values]
4. User B is on [app/page]

Steps:
1. Action:   [step]
   Expected: [result]
---
```

Capability Sets format: `Data / Procedural / Settings / Module - <Module> <Resource> - <Action>` — see Preconditions in Writing Guidelines for a worked example.
For API field IDs: `GET /index.php?/api/v2/get_case_fields`

---

## Quick Reference Checklist

- [ ] Context file for the area was read; story mapped to Key Business Rules
- [ ] references/examples.md was read; verification density matches
- [ ] Title follows `[Actor] [verb] [object] [condition]` pattern and is unique
- [ ] All metadata fields filled; `Dev Team` from the story; `refs` contains ONLY the story's own key(s) — no linked bugs/subtasks/epics
- [ ] Preconditions numbered, Capability Sets only, exact starting values for everything asserted later
- [ ] Steps use imperative style, no actor prefix; reference "Preconditions #N"
- [ ] Business-rule outcome asserted with absolute values; all touched entities verified
- [ ] Business-critical tables verified column by column; toasts verbatim; modal checks match scenario focus
- [ ] No vague expected results ("works", "is correct", "is successful", "confirming")
- [ ] **ECS cases:** `ECS Enabled = true`; tenant named in every cross-tenant step
