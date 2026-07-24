# FOLIO Loans — Business Logic Context

> Built 2026-07-21 (browser-based). Sources: TestRail suite 21 section 97 "Loans" and subsections (Change due date 1287, Declare lost 1290, Claim returned 1294, Renewals 1540, Anonymization 1132, Additional Loan Comments 25717); Jira UIU/CIRC stories. UI lives in `folio-org/ui-users` (Loans list + Loan details page). Exact strings tagged `[from cases]` are the team's asserted wording; confirm/upgrade against `ui-users/translations/ui-users/en_US.json` next pass.

---

## What is Loans

A **loan** is created when an item is checked out to a patron and closed when the item is checked in (or the loan is resolved via lost/anonymized flows). Staff view and act on loans from the patron record: **Loans** accordion → Open loans / Closed loans list, and the per-loan **Loan details** page. Core staff actions on an open loan: **Renew**, **Change due date**, **Declare lost**, **Claim returned**. (Actual check-out/check-in happen in the Check out / Check in apps; this area is the ongoing management of existing loans.)

---

## Key Terms

| Term | Definition |
|---|---|
| Open loan | Active loan; item is out to the patron. |
| Closed loan | Returned/resolved loan. |
| Loan details | Per-loan page showing loan fields + an action history table. |
| Loan action | A row in the loan history (Checked out, Renewed, Due date changed, Declared lost, Claimed returned, Checked in, etc.). |
| Declared lost | Staff-marked lost status; triggers lost-item fee policy behaviour. |
| Claimed returned | Patron claims they returned it; loan stays open, overdue accrual pauses. |
| Override | Elevated action to bypass a block (e.g. renew a declared-lost item). |

---

## Loan details — structure

- **Buttons** (top): `Renew`, `Change due date`, `Declare lost`, `Claim returned` — each enabled/disabled by current item status (see rules).
- **Fields above the action table**: `Item status`, `Due date`, and status-specific stamps like `Lost:` (date/time declared lost).
- **Action table columns**: `Action date`, `Action`, `Due date`, `Item status`, `Source` (Lastname, firstname middlename of the staff user, linked to their profile), `Comments` (free text entered for the action).
- **Loans list (Open/Closed)**: rows selectable; **bulk action buttons** `Renew` and `Change due date` enable when a compatible loan is selected; per-row ellipsis action menu mirrors the buttons.

---

## Action lifecycles

```
Checked out
  ├─ Renew → new due date per loan policy (or Override & renew when blocked)
  ├─ Change due date → pick date/time → Save and close
  ├─ Declare lost → free-text reason → Confirm → Item status: Declared lost
  └─ Claim returned → free-text reason → Confirm → Item status: Claimed returned

Declared lost
  ├─ Renew: allowed (may require override) → returns item to Checked out, due date per policy
  ├─ Change due date: BLOCKED — "Failed to change due date: item is Declared lost"
  └─ Declare lost: button inactive

Claimed returned
  ├─ Renew / Change due date: BOTH inactive
  ├─ "Claim returned" button is replaced by a "Resolve claim" dropdown with two options:
  │    ├─ Declare lost → same Declare-lost modal/flow; Claimed-returned field resets to "-"; auto-creates a patron Note
  │    └─ Mark as missing → item status → Missing, loan CLOSES; Claimed-returned field resets to "-"; auto-creates a patron Note
  └─ Both resolution options are also reachable from the per-row ellipsis Action menu on the loans list, not just the loan-details dropdown.
```

---

## Exact UI Texts

> `[from cases]` = asserted verbatim in team TestRail cases. Confirm success-toasts/labels against `ui-users/en_US.json` next pass.

### Declare lost [from cases — C9191]
- Action-menu / button label: `Declare lost`
- Modal: free-text comment box + `Cancel` and `Confirm`.
- After confirm: `Item status` = `Declared lost`; field `Lost:` shows date/time; action-table row `Action` = `Declared lost`, `Due date` unchanged from prior row, `Comments` = entered text. `Declare lost` button becomes inactive.

### Change due date [from cases — C9192]
- Bulk modal lists selected loans; a declared-lost loan shows warning `Item is declared lost`.
- On Save with a declared-lost loan included: alert `Failed to change due date: item is Declared lost` (that loan is skipped; valid loans get the new due date).
- Buttons: `Save and close`, `Close`.

### Renew / Override [from cases — C9192]
- Renew of a declared-lost item fails with: `Item not renewed: item is Declared lost` + an `Override` control.
- `Override & renew` modal: for the blocked item the `New due date` column shows `New due date will be calculated automatically.`; requires a free-text comment; `override` confirms → item back to `Checked out`, due date per loan policy.

### Claim returned [confirmed verbatim — C10959, C10960]
- Modal text (single item): `{title} (Barcode: {barcode}) will be claimed returned.` + required "Additional information" text field; `Cancel` (active) / `Confirm` (inactive until text entered).
- On confirm: `Item status` = `Claimed returned`; loan-details top buttons change — `Claim returned` is replaced by a `Resolve claim` **dropdown**; `Renew` and `Change due date` both become inactive.
- Bulk Claim returned modal shows a table (Title, Due date, Requests, Barcode, Call number, Loan policy) per selected item, plus the same required Additional-information field; bulk button only activates once at least one eligible (Checked out or Declared lost) loan AND one other loan are both checked — a single already-Claimed-returned loan alone keeps it inactive.
- Patron record's open-loans count shows the count of claimed-returned items in parentheses alongside the total open-loan count.
- Resolvable later via: (a) Check in (`Found by library` / `Returned by patron`), or (b) the **Resolve claim** dropdown directly from Loan details — see below.

### Resolve claimed returned item [confirmed verbatim — C10960, previously undocumented]
- "Resolve claim" dropdown (replaces "Claim returned" button once item is Claimed returned) offers exactly two options: **Declare lost** and **Mark as missing**. Also available via the loans-list per-row ellipsis Action menu.
- **Declare lost** (from Resolve claim): modal `{title} (Barcode: {barcode}) will be declared lost.` + required Additional information + Cancel/Confirm. On confirm: `Item status` → `Declared lost`; `Fine incurred` updates per the lost item fee policy; `Claimed returned` field resets to `-`; `Lost` field populated with confirm date/time. Also auto-creates a patron **Note**: Note type `general note`, Note title `Claimed returned item marked declared lost`, Note details `Claimed returned item marked declared lost`.
- **Mark as missing** (from Resolve claim): modal `{title} (Barcode: {barcode}) will be marked Missing and patron will not be billed.` + required Additional information + Cancel/Confirm. On confirm: `Item status` → `Missing`; the loan **closes** (moves from Open to Closed loans list); ALL loan-details action buttons become inactive; `Claimed returned` field resets to `-`. Also auto-creates a patron Note: Note title `Claimed returned item marked missing`, Note details `Claimed returned item marked missing`.
- Both resolutions decrement the patron's "claimed returned" parenthetical count by one.

### Action values (loan history)
`Checked out`, `Renewed`, `Renewed through override`, `Due date changed`, `Declared lost`, `Claimed returned`, `Marked as missing`, `Loan closed`, `Checked in`, `Checked in (found by library)`, `Checked in (returned by patron)`.

### Renewal failure modal — exact structure [confirmed verbatim — C568, C569, C571, C6667]
- Common "Renew" failure modal: a failure count header, then a table of failed loans with columns Renewal status, Title, Item status, Due date, Requests, Barcode, Effective call number string, Loan policy, plus a `Close` button (and an `Override` button ONLY if the acting user has the renew-through-override permission/capability).
- Exact `Renewal status` failure strings (verbatim, use these in expected results — never paraphrase):
  - `Item not renewed: loan is not renewable`
  - `Item not renewed: loan at maximum renewal number`
  - `Item not renewed: renewal would not change the due date`
  - `Items with this loan policy cannot be renewed when there is an active, pending hold request` (loan-policy setting disallowing renewal under an active/pending hold)
- `Override & renew` modal: date/time pickers are required UNLESS the system can auto-calculate the new due date, in which case the "New due date" column shows `Due date will be calculated automatically` (or, when a date IS required, `Select due date above` as the placeholder in that column) — plus a table (same columns as above, plus Renewal count) and a REQUIRED free-text "Additional information" field; `Cancel` / `Override` (inactive until required fields are filled).
- On successful override, the loan action-history row logs `Action: Renewed through override`, `Source` = the overriding staff user, `Comments` = the override justification text entered.
- A loan policy field can allow renewal even under an active pending hold request, optionally applying a distinct "Alternate loan period at renewal" (different from the loan's normal renewal period) specifically for that scenario. [C6667]

### Override patron block on renewal [confirmed — C170386]
- Attempting to renew a blocked patron's loan opens a modal titled `Patron blocked from renewing` with a `Reason for block:` line, and buttons `Override`, `Close`, `View block details`. If more than three blocks exist on the patron, only the first three are shown.
- Clicking `Override` opens a second modal requiring a free-text comment; `Save & close` completes the override, the renewal proceeds, and the comment is saved directly onto the loan record (same Comments mechanism as other loan actions).

### Recall due-date recalculation rules [confirmed — C466157, C466158, C466159; previously undocumented]
> When an active Recall request is placed against a Checked-out item, the loan's due date is recalculated per the interaction of two Loan Policy fields: **Recall return interval** and **Minimum guaranteed loan period for recalled items**. Let `recallDueDate` = today + Recall return interval, `minGuaranteedDate` = checkout date + Minimum guaranteed loan period.
- If `recallDueDate` is AFTER the loan's current due date → due date is **unchanged**. [C466157]
- If `recallDueDate` is BEFORE the current due date but AFTER `minGuaranteedDate` → due date becomes `recallDueDate` itself. [C466158]
- If `recallDueDate` is BEFORE the current due date AND BEFORE `minGuaranteedDate` → due date becomes `minGuaranteedDate` (the minimum guaranteed period always wins over an even-earlier recall interval). [C466159]
- In all cases the recalculation happens automatically upon Recall request creation — no explicit staff action on the loan itself is required to trigger it.

### Manual anonymization (Closed loans) [confirmed verbatim — C9217, C422021; resolves prior Known Gap]
- "Anonymize all loans" button lives on the patron's Closed loans tab.
- Confirmation modal text (verbatim): `All loans for this user will be anonymized. The loans will no longer appear in the user's closed loans. Anonymizing loans cannot be reversed.` Buttons: `Cancel` / `Confirm`.
- On Confirm: closed loans with NO associated fees/fines are anonymized and disappear from the Closed loans view immediately. Closed loans that DO have an associated fee/fine (open or closed) are **skipped** — they remain visible and unanonymized — and an error/warning message appears: `x loan(s) had associated fees/fines and could not be anonymized` (x = count of skipped loans). This is a partial-success operation, not all-or-nothing.

### Additional Loan Comments (patron info / staff info) [confirmed — C397378, C397379; resolves prior citation gap]
- Reachable from the Check-out app's per-loan ellipsis Action menu right after checkout: `add patron info` and `add staff info` options, each gated by its own distinct permission (`Users: Users loans: add patron information` / `...add staff information`).
- Entering text and clicking `Save & close` shows a green success toast and the text appears at the TOP of the "Comments" column on the Loan details action table.
- Both comment types can also be added later (not just at checkout) via `New patron info` / `New staff info` buttons directly on the Loan details page.
- Adding a NEW comment of the same type does not overwrite the prior one — instead the prior comment's row is marked **"superseded"** in the Action column, preserving a full stacked history of every comment ever added to that loan.

### Close declared-lost loan with $0 lost-fee [confirmed — C10948]
- When the applicable Lost item fee policy has: item-charge set-cost = $0.00, "Charge lost item processing fee if declared lost by patron" = No, and a short "close the loan after" interval configured, declaring an item lost (by staff, not system-aged) auto-**closes** the loan once that interval elapses.
- Resulting item status is `Lost and paid` (not merely `Declared lost`); `Fine incurred` does NOT increase; TWO new action-table rows appear stacked: `Loan closed` (top, Comments = `-`) then `Declared lost` (below, Comments = the staff-entered lost reason) — both sharing the same (pre-existing) due date.

---

## Capability Sets (Eureka)

Curated from precondition prose (verify exact names in env):
- `Data - UI-Users Loans - View` (view loans)
- `Data - UI-Users Loans - Manage` (renew, change due date)
- `Procedural - UI-Users Loans Declare-Lost - Execute`
- `Procedural - UI-Users Loans Claim-Returned - Execute`
- `Procedural - UI-Users Loans Renew-Override - Execute` (override renew)
- `Data - UI-Users Loans Anonymize - Execute` (anonymization)

> Legacy permission names seen in older cases: "Users: User loans view", "Users: User loans view, change due date, renew", "Loans: declare lost", "Loans: renew through override". Prefer capability sets for new cases; keep the two-column table if the section's cases use it.

---

## Common Verification Patterns

### Declare lost (Cancel then confirm)
1. Open loan action menu on a Checked out item → `Declare lost` present → click.
2. Modal with free-text + `Cancel`/`Confirm`; click `Cancel` → item status unchanged.
3. Re-open, enter text, `Confirm` → item status `Declared lost`; verify Loan details fields + action-table row column-by-column (Action = `Declared lost`, Comments = entered text, Source = staff name linked).

### Status gates the action buttons
Assert exact enabled/disabled matrix per item status — e.g. once `Declared lost`: `Renew` active, `Change due date` + `Declare lost` inactive; the bulk `Change due date` button stays inactive until a Checked-out loan is also selected.

### Change due date with a mixed selection
Select one Checked out + one Declared lost loan → bulk `Change due date` → declared-lost row warns `Item is declared lost`; on Save the checked-out loan gets the new due date, the declared-lost loan alerts `Failed to change due date: item is Declared lost`.

### Bulk renew-override sends one API request per loan (confirmed pattern, C1347104, 2025)
Selecting many loans (e.g. 10+ aged-to-lost loans) and confirming `Override & renew` does **not** batch into a single request — DevTools shows requests fired **one by one, sequentially**. This is load-bearing for any case touching optimistic-locking/concurrency bugs in bulk renewal (real regression: UIU-3561, bulk renewals causing user-summary update errors) — a case asserting "bulk renew succeeds" should also assert per-loan due date/status update, not just an aggregate success count.

### Automated patron block clears when its triggering condition is resolved (confirmed pattern, C1347104)
An automated patron block (e.g. `Maximum number of lost items` exceeded) shows on the patron record as a red exclamation mark on the `Patron blocks` accordion with the block listed in its table. After the triggering condition is resolved (e.g. all aged-to-lost loans successfully renewed back to `Checked out`), the accordion **collapses with no blocks listed** — verify this end state explicitly, not just that the renewal action itself succeeded.

---

## Key Business Rules for Test Cases

1. Loan actions are gated by item status: `Change due date` and `Declare lost` are unavailable for a Declared-lost loan; `Renew` remains available (may require override). (cases — C9192)
2. `Declare lost` requires a free-text comment; the comment is stored in the loan action row's `Comments`. (cases — C9191)
3. Declaring lost stamps `Item status = Declared lost` and a `Lost:` date/time, and disables the `Declare lost` button thereafter. (cases — C9191)
4. Renewing a declared-lost item is blocked (`Item not renewed: item is Declared lost`) unless overridden; override recalculates the due date per loan policy and returns the item to `Checked out`. (cases — C9192)
5. Change-due-date on a batch skips ineligible loans with a per-row failure alert rather than failing the whole batch. (cases — C9192)
6. Claimed returned keeps the loan open and pauses overdue fine progression until resolved at check in. (cases — Claim returned subsection + check-in.md)
7. Loan action `Source` records the staff user (Lastname, firstname middlename) linked to their profile. (cases — C9191)
8. Loan anonymization removes the link between the loan and patron after the loan closes (configured in Settings > Circulation > Loan anonymization); anonymized loans no longer show patron identity. (cases — Anonymization subsection)
9. Renewals honour the loan policy's renewal limits/period; over-limit renewals fail with a policy message and may be overridable. (cases — Renewals subsection)
10. Additional loan comments (patron/staff info) can be added to a loan and are searchable in the Circulation log. (cases — Additional Loan Comments subsection)
11. Bulk renew/override on multiple selected loans fires **one API request per loan sequentially**, not a single batched request — relevant to any concurrency/optimistic-locking scenario on bulk actions. (cases — C1347104, 2025)
12. An automated patron block tied to loan state (e.g. max lost items) clears (accordion collapses, no blocks listed) once the underlying condition is resolved (e.g. the blocking loans are renewed/returned) — verify the block's disappearance as its own assertion, not just the triggering action's success. (cases — C1347104, 2025)
13. Claimed-returned loans replace the "Claim returned" button with a "Resolve claim" dropdown (Declare lost / Mark as missing); resolving via either option resets the Claimed-returned field to "-" and auto-creates a patron Note documenting the resolution. (cases — C10960)
14. Mark-as-missing from Resolve-claim closes the loan and deactivates all loan-details buttons; Declare-lost from Resolve-claim keeps the loan open under the standard Declared-lost lifecycle. (cases — C10960)
15. Renewal failures always present the exact `Item not renewed: {reason}` phrasing in a per-loan table; an Override button only appears for users holding the renew-through-override capability, and a loan-policy setting can specifically forbid renewal while an active/pending hold request exists. (cases — C568, C569, C571, C6667)
16. A recall's effect on due date is governed by comparing (today + Recall return interval) against both the current due date and (checkout date + Minimum guaranteed loan period): the later of an unchanged due date, the recall date itself, or the minimum-guaranteed date always wins, protecting the patron's guaranteed minimum loan period. (cases — C466157, C466158, C466159)
17. Manual anonymization of closed loans is a partial-success operation: loans with associated fees/fines are always skipped and reported by count, even when other selected loans anonymize successfully. (cases — C9217, C422021)
18. Patron-info and staff-info loan comments are additive/superseding, never overwritten — each new comment of the same type marks the prior one "superseded" while preserving it in the action history. (cases — C397378, C397379)
19. A lost item fee policy with $0 set-cost and "charge if declared lost by patron" = No can auto-close a declared-lost loan after its configured interval, stamping the loan `Lost and paid` with two stacked action rows (Loan closed, Declared lost) rather than leaving it open in Declared-lost status. (cases — C10948)
20. **A backdated check-in (see check-in.md's Backdate feature) makes the closed loan's own `Return date` and `Check in service point` fields reflect the BACKDATED date/time and the service point used at check-in** — but the loan's Action-history table's top row `Action Date` column still shows the actual SYSTEM date/time the check-in was performed. Don't conflate these two timestamps in a single assertion: `Return date` is the business-effective (possibly backdated) value, `Action Date` is the real audit-trail time. (cases — C584)

---

## Authoring style (measured 2026-07-23)

Loans skews **`Other` (~85%, 59/69)** with only ~15% `Functional` — the most Other-heavy of the circulation apps — median ~6 steps, `User Journey` ~0% (`No`). Reason: most Loans cases verify the **loan-details / closed-loan display and single actions** (change due date, renew, declare lost, claim returned, anonymization, additional comments) as compact checks rather than end-to-end lending journeys — those live in Check-out/Check-in. Use `Other` for loan-detail/display and single-action cases; reserve `Functional` for behavior that computes state (recall due-date recalculation, bulk renew/override effects). Preconditions carry the loan setup with symbolic identifiers (`<barcode>`, service point `S`, loan policy with the relevant intervals) — don't invent concrete values; keep the flow to the one action under test and assert the resulting loan/due-date/status.

---

## Known Gaps / Items to Verify

- [ ] Success-toast exact wording for renew / change-due-date — still not confirmed against `ui-users/en_US.json` (Claim-returned/Resolve-claim/Anonymization modal texts ARE now confirmed verbatim, see above).
- [ ] Capability-set names inferred from prose — verify exact Eureka strings in env.
- [ ] The third recall due-date case (C466158: recall date before current due date but after min-guaranteed date → due date = recall date) was cited by title only in the original gap list; now fully documented above alongside its siblings C466157/C466159.
- [ ] Interaction between Additional Loan Comments and the Circulation log (whether "superseded" comments remain individually searchable) was not directly re-verified this round.

> N≥10 audit round (2026-07-22): 14 cases read (C9217, C422021, C10959, C10960, C568, C569, C571, C397378, C397379, C466157, C466159, C10948, C170386, C6667). Resolved every open Known Gap from the prior build: pulled verbatim Claim-returned/Resolve-claim/Anonymization modal text, exact Renewal failure-reason strings, and full Additional-Loan-Comments behavior. Surfaced two entirely new, previously undocumented features/rules: the "Resolve claim" dropdown (Declare lost / Mark as missing) for Claimed-returned loans, and the full Recall due-date recalculation algorithm (Recall return interval vs. Minimum guaranteed loan period). Added 7 new Key Business Rules (13-19).
>
> Random spot-check (2026-07-22): picked one fresh uncited case at random (C584) to sanity-check this file's "Mostly match" verdict. Found a genuine cross-file gap — check-in.md thoroughly documents the backdate feature's effect on the Check-in app's own UI (Scanned Items "Time returned" column), but loans.md never mentioned the resulting loan-record-side effect: the closed loan's `Return date`/`Check in service point` fields take the backdated values while the Action-history `Action Date` column stays on system time. Added Key Business Rule 20 with a cross-reference to check-in.md.
