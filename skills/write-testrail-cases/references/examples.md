# Golden Examples

> **Status: REAL cases, pulled from TestRail (project 14 "FOLIO Bug Fest", suite 21) on 2026-07-21.**
> `SKILL.md` step 2 requires reading this file as "golden cases from the team's TestRail" before generating anything. Until this file existed at all, every run of `write-testrail-cases` silently skipped this step. The three cases below are real, verbatim (HTML/inline-style noise stripped for readability), and were used to correct several rules in `SKILL.md` that didn't match how the team actually writes cases:
>
> 1. **No "User A / User B" naming.** No real case names an actor. Preconditions just say "User with following Capability Sets is logged in" or "Staff user with...". `SKILL.md` now defaults to a single unnamed user; named actors are reserved for cases that genuinely need two distinct roles.
> 2. **Preconditions are compact, not one-fact-per-line.** Real preconditions pack 2-3 related facts into a single numbered item ("Two Fiscal years exist. One has assigned AU.").
> 3. **`User Journey = Yes` for lifecycle/multi-outcome cases** (Example 3), tied to the journey shape — not left hardcoded to No.
> 4. **Value convention is area-specific:** concrete amounts in Finance/Orders/Invoices (Example 2), symbolic placeholders `S`/`<barcode>` in circulation (Example 3). Don't invent concrete values where the team writes placeholders.
> 5. **`refs` = whatever the case verifies** — often a Bug or Tech-Debt ticket, or several keys across projects; frequently no story at all.
> 6. **Expected results are terse, observable states.** Prose by default (bullets only for a true item-inventory), and — critically — **no rationale, no ticket-scope reasoning, no multi-sentence NOTE essays, no hedging about unshipped work**. Every real expected result below reads as *what the executor sees* (`Actions menu does NOT contain "Fee/fine details"`), never *why* or *which ticket requires it*. See the "Anti-pattern" section below for the exact failure mode to avoid.
>
> Refresh this file periodically by pulling a few recent (last 1-2 releases), Manual, Critical Path/Extended cases from well-maintained sections — see "How to populate this file for real" at the bottom.

---

## Example 1 — Compact preconditions, no named actor (Check in area)

Source: [C1263908](https://foliotest.testrail.io/index.php?/cases/view/1263908) — "Check in items with and without fee/fines within one session", section 115 (Check in), Release Trillium, Extended, Manual, Dev Team Vega, refs a single Bug (not a Story — this case exists to cover a specific bug fix).

```
Title: Check in items with and without fee/fines within one session

Type:               Other
Priority:           Medium
Release:            Trillium
Test Group:         Extended
User Journey:       No
Multi-Tenant:       No
Bug Created:        Yes
Unstable:           No
ECS Enabled:        No
ECS Unsupported:    No
Capabilities Ready: Yes
Execution Type:     Manual
Dev Team:           Vega
Labels:             AI
References:         UICHKIN-485

Preconditions:
1. At least one Owner and one Manual charge type have been created in Settings > Users
2. Three items have been checked out to the patron; fee/fine is owed for two of them
3. Staff user with an assigned service point is logged in with capability set: Data - UI-Checkin - manage

Steps:
1. Action:   Enter barcode of the item with fee/fine owed (e.g. Item #1)
   Expected: Item is checked in successfully; new record appears on "Scanned Items" page; "Time returned" column contains the actual time the item was checked in and the "(fees/fines owed)" label; item status changes to "Available" or "In transit" (depends on selected service point and item effective location)

2. Action:   Enter barcode of the item without fee/fine owed (e.g. Item #2)
   Expected: Item is checked in successfully; new record appears on "Scanned Items" page; "Time returned" column contains only the actual time (no fee/fine label); item status changes to "Available" or "In transit"

3. Action:   Enter barcode of the item with fee/fine owed (e.g. Item #3)
   Expected: Item is checked in successfully; new record appears on "Scanned Items" page; "Time returned" column contains the actual time and the "(fees/fines owed)" label; item status changes to "Available" or "In transit"

4. Action:   Click the ellipsis "..." actions menu on the record for the item without fee/fine
   Expected: Actions menu appears and does NOT contain "Fee/fine details" option

5. Action:   Click the ellipsis "..." actions menu on the record for the item with fee/fine
   Expected: Actions menu appears and contains "Fee/fine details" option
```

**Why this is the bar:** 3 preconditions, not 6 — related facts (three items checked out, two with fee/fine) share one line instead of being split into separate numbered items. No "User A"/"User B" — just "staff user", singular, because the scenario only needs one role. `refs` is a single Bug ID because this case exists specifically to cover that bug's fix, not a story. Every expected result names the exact column/label/menu-item affected — nothing says "works correctly".

---

## Example 2 — Journey case across multiple apps, multi-ref (Acquisition Units area)

Source: [C1385303](https://foliotest.testrail.io/index.php?/cases/view/1385303) — "Filter by Acquisition unit across acquisition modules", section 873 (Acquisition Units), Release Umbrellaleaf, Extended, Manual, Dev Team Thunderjet.

```
Title: Filter by Acquisition unit across acquisition modules

Type:               Other
Priority:           Medium
Release:            Umbrellaleaf
Test Group:         Extended
User Journey:       No
Multi-Tenant:       No
Bug Created:        No
Unstable:           No
ECS Enabled:        No
ECS Unsupported:    No
Capabilities Ready: Yes
Execution Type:     Manual
Dev Team:           Thunderjet
Labels:             AI
References:         UIOR-1519, UISACQCOMP-300, UIREC-504, MODORDSTOR-407, UICLAIM-31, MODORDERS-1464

Preconditions:
1. Acquisition unit (AU) with "View" option unchecked has been created in Settings > Acquisition units; admin user is assigned to it
2. Two Fiscal years exist. One has the AU assigned.
3. Two Ledgers exist. One has the AU assigned.
4. Two Groups exist. One has the AU assigned.
5. Two Funds exist. One has the AU assigned.
6. Two Organizations exist. One has the AU assigned.
7. Two Orders in "Open" status exist. One has the AU assigned. Its PO line has "Claiming active" checked and "Create inventory" = "Instance, holdings, item".
8. Two Invoices exist. One has the AU assigned.
9. User is logged in with the following Capability Sets: Data - UI-Claims Claiming - View, Data - UI-Finance Fiscal-Year - View, Data - UI-Finance Fund-Budget - View, Data - UI-Finance Group - View, Data - UI-Finance Ledger - View, Data - UI-Invoice Invoice - View, Data - UI-Orders Orders - View, Data - UI-Organizations - View, Data - UI-Receiving - View
10. User is in the Finance app with the "Fiscal year" toggle selected on the Search & filter pane

Steps:
1. Action:   Select the AU from Preconditions #1 in the "Acquisition unit" filter
   Expected: Fiscal year with the AU assigned is returned in the search result

2. Action:   Select "No acquisition unit" option in the "Acquisition unit" filter
   Expected: Fiscal year without the AU assigned is returned in the search result

3. Action:   Click "Ledger" toggle, then select the AU in the "Acquisition unit" filter
   Expected: Ledger with the AU assigned is returned in the search result

4. Action:   Select "No acquisition unit" option in the "Acquisition unit" filter
   Expected: Ledger without the AU assigned is returned in the search result

5. Action:   Click "Group" toggle, then select the AU in the "Acquisition unit" filter
   Expected: Group with the AU assigned is returned in the search result

6. Action:   Select "No acquisition unit" option in the "Acquisition unit" filter
   Expected: Group without the AU assigned is returned in the search result

7. Action:   Click "Fund" toggle, then select the AU in the "Acquisition unit" filter
   Expected: Fund with the AU assigned is returned in the search result

8. Action:   Select "No acquisition unit" option in the "Acquisition unit" filter
   Expected: Fund without the AU assigned is returned in the search result

9. Action:
   - Navigate to "Organizations" app
   - Select the AU in the "Acquisition unit" filter
   - Select "No acquisition unit" option
   Expected:
   - Organization with the AU assigned is returned in the search result
   - Organization without the AU assigned is returned in the search result

10. Action:
    - Navigate to "Orders" app, select "Orders" toggle
    - Click "Reset all" button (if active)
    - Select the AU, then select "No acquisition unit" option
    Expected:
    - Order with the AU assigned is returned in the search result
    - Order without the AU assigned is returned in the search result

11. Action:
    - Select "Order lines" toggle, click "Reset all" (if active)
    - Select the AU, then select "No acquisition unit" option
    Expected:
    - PO line with the AU assigned is returned in the search result
    - PO line without the AU assigned is returned in the search result

12. Action:
    - Navigate to "Receiving" app, click "Reset all" (if active)
    - Select the AU, then select "No acquisition unit" option
    Expected:
    - PO line with the AU assigned is returned in the search result
    - PO line without the AU assigned is returned in the search result

13. Action:
    - Navigate to "Claiming" app, click "Reset all" (if active)
    - Select the AU, then select "No acquisition unit" option
    Expected:
    - PO line with the AU assigned is returned in the search result
    - PO line without the AU assigned is returned in the search result

14. Action:
    - Navigate to "Invoices" app, click "Reset all" (if active)
    - Select the AU, then select "No acquisition unit" option
    Expected:
    - Invoice with the AU assigned is returned in the search result
    - Invoice without the AU assigned is returned in the search result
```

**Why this is the bar:** 14 steps because the scenario genuinely spans 7 modules (Finance × 4, Organizations, Orders × 2, Receiving, Claiming, Invoices) — a real journey case, not padding. Preconditions group multiple related facts per line ("Two Fiscal years exist. One has the AU assigned.") instead of splitting counts and assignment into separate items. `refs` lists all 6 related Jira keys across 5 different projects (deduplicated from the source, which had one repeated) — this case exists to verify a cross-module CQL index change, so every touched module's ticket is relevant, not just one "story key". Every step follows the same two-state pattern (with AU / without AU) so the reviewer can scan for the one that's missing.

---

## Example 3 — User Journey case, symbolic placeholders, bug-driven (Check in area)

Source: [C7148](https://foliotest.testrail.io/index.php?/cases/view/7148) — "Check In: item with at least one open request", section 115 (Check in), `User Journey = Yes`, Priority Critical, refs a Bug + a Tech-Debt automation ticket (no story). One case covers BOTH fulfillment outcomes plus slip reprints.

```
Title: Check In: item with at least one open request

Type:               Other
Priority:           Critical
Release:            Umbrellaleaf
Test Group:         Critical Path
User Journey:       Yes
Multi-Tenant:       No
Bug Created:        No
Unstable:           No
ECS Enabled:        No
ECS Unsupported:    No
Capabilities Ready: Yes
Execution Type:     Manual
Dev Team:           Vega
Labels:             AI
References:         CIRC-1719, FAT-1218

Preconditions:
1. User with Check In capability and permission to view requests, with service points S and S1 assigned
2. Item with at least one open request; the top request has pickup service point S

Steps:
1. Action:   Select service point S1 for the user
   Expected: <Service point S1> shows in the upper right corner

2. Action:   Check in the item (top request pickup = S) at service point S1
   Expected: Modal appears: "Route <title> (<material type>) (Barcode: <barcode>) to <Service point S>." "Print slip" is checked by default

3. Action:   Close the modal
   Expected: Browser print dialog appears with preview of the transit slip

4. Action:   Close the print dialog
   Expected: Item is shown on the check in screen; status shows as "In transit"

5. Action:   Open the action menu (ellipsis)
   Expected: "Print transit slip" and "View request details" are shown

6. Action:   Click "View request details"
   Expected: Request details for the top request on the item record are shown

7. Action:   Navigate back to Check In, re-open the action menu, click "Print transit slip"
   Expected: Browser print dialog reopens with transit slip preview

8. Action:   Close the print dialog, switch the user's service point to S, scan the item
   Expected: Modal appears: "Place <title> (<material type>) (Barcode: <barcode>) on Hold Shelf at <Service point S> for request." "Print slip" is checked by default

9. Action:   Close the modal
   Expected: Browser print dialog appears with preview of the hold slip

10. Action:  Close the print dialog
    Expected: Item is shown on the check in screen; status shows as "Awaiting pickup"

11. Action:  Open the action menu (ellipsis)
    Expected: "Print hold slip" and "View request details" are shown

12. Action:  Click "View request details"
    Expected: Request details for the top request on the item record are shown

13. Action:  Navigate back to Check In, re-open the action menu, click "Print hold slip"
    Expected: Browser print dialog appears with hold slip preview
```

**Why this is the bar (and what a naive generation gets wrong):** a terse title — "item with at least one open request" — hides a **journey**. The team does NOT write an atomic "check in at pickup SP → Awaiting pickup" case; they walk *both* outcomes (In transit at a non-pickup SP, then Awaiting pickup after switching to the pickup SP) plus slip reprints, in one case flagged `User Journey = Yes`. Note the conventions a first-pass AI case tends to violate: (a) **symbolic placeholders** `S` / `S1` / `<barcode>` / `<title>`, never invented values like `SP-A`/`12345`; (b) **prose expected results** — "Modal appears: ... Print slip is checked by default." is one sentence, not a 3-bullet list; (c) **`refs` = a Bug + a Tech-Debt ticket, no story**; (d) **Priority Critical** because check-in fulfillment is a core daily path. (Real-world footnote: the raw case ends with a junk step "Saving this test - test step - ignore PDW" — dropped here. Always strip such noise when curating examples.)

---

## Anti-pattern — bloated expected results (what NOT to do)

> These are **real AI-generated expected results** (MARC Authority "Default - Delete" profile cases, section test_ai) that a reviewer rejected. Study them as the failure mode to avoid — then copy the terse rewrites.

**❌ BAD — expected result padded with ticket rationale and hedging:**

```
Step: Click "Actions" on the Action profile detail pane
Expected: No "Duplicate", "Edit", or "Delete" options are available. NOTE: UIDATIMP-1768
(which specifically disallows Duplicate for this profile) is still Open as of this case's
authoring — if "Duplicate" IS present/enabled, treat it as a known tracked gap, not a new defect
```

```
Step: Click "Actions" on the Match profile detail pane
Expected: Both "Edit" and "Duplicate" are available/enabled; "Delete" is absent or disabled —
this contrasts explicitly with the Job profile (duplicate-only, verified in step 2) and the
Action profile (fully locked, verified in step 4)
```

**✅ GOOD — same checks, terse and observable:**

```
Step: Click "Actions" on the Action profile detail pane
Expected: Actions menu has no Duplicate, Edit, or Delete options

Step: Click "Actions" on the Match profile detail pane
Expected: Actions menu shows Edit and Duplicate (enabled); no Delete option
```

**What went wrong, precisely:**
- **Ticket-scope reasoning in the Expected field** ("UIDATIMP-1768 … is still Open … treat it as a known tracked gap") — that belongs in the story/PR discussion, never in a test step. An executor needs *what to observe*, not *why*.
- **Cross-step justification** ("this contrasts explicitly with the Job profile … verified in step 4") — a reviewer reads the steps in order; don't narrate the comparison inside a result.
- **Hedging about unshipped work** ("IF listed / IF NOT listed", "if Duplicate IS present, treat as…") — don't build a case around behavior that isn't shipped, and don't turn the Expected field into a decision tree. If the behavior is unresolved, either omit that step or write a single terse `NOTE:` sentence.
- **Multi-sentence `NOTE:` essays** — a NOTE is one short caveat sentence, max. If it needs a paragraph, the assertion itself is wrong or speculative.

Rule of thumb: if an expected result contains a Jira key, the word "gap"/"defect", "IF"/"unless", or more than ~2 sentences, it's over-written — cut it to the observable state.

### Second failure mode — the semicolon field-list run-on

Same case family, a different reviewer rejection: a detail-view verification crammed into one line with semicolons.

**❌ BAD:**

```
Step: Click the profile row to open its detail view
Expected: Detail view shows Name = "Default - Delete MARC Authority records"; Description =
"This action profile is used to delete MARC authority records. This action profile cannot be
duplicated, edited, or deleted."; Action = "Delete"; FOLIO record type = "Authority"; linked
Field mapping profile = "Default - Delete MARC Authority records"
```

**✅ GOOD — lead-in line + one field per bullet:**

```
Step: Click the profile row to open its detail view
Expected: Action profile detail view shows:
- Name = "Default - Delete MARC Authority records"
- Description = "This action profile is used to delete MARC authority records. This action
  profile cannot be duplicated, edited, or deleted."
- Action = "Delete"
- FOLIO record type = "Authority"
- Linked Field mapping profile = "Default - Delete MARC Authority records"
```

Trigger to watch for: **named fields joined by semicolons.** 2+ `field = value` pairs — or even one whose value is a full sentence (like a Description) — is an inventory → bullets. A toast plus one resulting state may stay prose with a semicolon (see golden Example 1, which chains short observations readably); the smell is a *list of named fields* crammed onto one line, e.g. `Name = "…"; Description = "…"; Action = "Delete"`.

### Third failure mode — nested preconditions

Preconditions must be **flat**: each user, each data record, and the starting page/state are separate top-level numbered items. Do NOT nest the starting-state (or a data record) as a sub-bullet under another item.

**❌ BAD** (starting page nested under the capability set):
```
2. User with following Capability Sets is logged in:
   - Settings - UI-Data-Import Settings - Manage
     - User is on Settings > Data import > Action profiles
```

**✅ GOOD** (starting page is its own numbered item; sub-bullets only list capability sets):
```
2. User with following Capability Sets is logged in:
   - Settings - UI-Data-Import Settings - Manage
3. User is on Settings > Data import > Action profiles
```

---

## How to populate this file for real

Once TestRail credentials are available (see `SKILL.md` → Credentials), pull real cases from 2–3 of the team's best-maintained sections and refresh the examples above. Note: direct API calls to `foliotest.testrail.io` may be blocked by your network/sandbox egress rules — if so, open the case in a browser where you're already logged in and hit the same API path directly (e.g. `https://foliotest.testrail.io/index.php?/api/v2/get_case/{id}`); TestRail accepts the existing session cookie, no API key needed in that context.

```
GET {TESTRAIL_URL}/index.php?/api/v2/get_cases/14&suite_id=21&section_id={section_id}&limit=20
GET {TESTRAIL_URL}/index.php?/api/v2/get_case/{case_id}
```

Pick sections/cases that:
- have been updated within the last 1–2 releases (recent, not legacy style — old cases often use the single `custom_steps` field instead of `custom_steps_separated`, and read very differently),
- are `custom_automation_type = 2` (Manual) — automated-style cases are terser and skip UI-verification detail,
- come from an area with a healthy context file (10+ Key Business Rules, an `Exact UI Texts` section with `[confirmed]` strings — see `references/context/`).

**Strip HTML aggressively before using real case content.** Real `custom_preconds`/`custom_steps_separated` fields are full of copy-paste noise from Confluence/Word — huge inline `style="..."` blobs, `data-pasted="true"` attributes, stray `&nbsp;`. Strip all tags and attributes down to plain text (keep `<strong>`/`<em>` emphasis as `**bold**`/`*italic*` if you want, or drop it) before reformatting into this file's template shape. This same stripping step is what `build-app-context`'s Phase 1.3 extraction needs to do more aggressively — several context files came up with zero extracted toast/modal strings, which is very likely this noise breaking the extraction regexes rather than a genuine absence of signal.

For each case, add a one-line "Why this is the bar" note explaining what makes it a good example (step count, what's grouped vs. atomic, how absolute values are asserted, refs practice, etc.) — that note is what actually teaches the model verification depth, not just the raw case text.

Aim for 4–6 examples covering: a bug-driven regression case, a capability-boundary case, a journey/lifecycle case spanning multiple apps, and an ECS cross-tenant case, since those are the shapes `write-testrail-cases` has to reproduce most often.
