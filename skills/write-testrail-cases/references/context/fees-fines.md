# FOLIO Fees/Fines — Business Logic Context

> Built 2026-07-21 (browser-based). Sources: TestRail suite 21 section 88 "Fees&Fines" and subsections (Pay 91, Waive 1533, Transfer 1534, Cancel 1530, Refund 1532, Manual 90, Overdue Fines 1141, Lost item fees 1531/1312, Bursar 11060, reports 16509/16510); Jira UIU/MODFEE stories. UI lives in `folio-org/ui-users` (fees/fines are part of the patron record). **Exact UI Texts confirmed against `ui-users/translations/ui-users/en_US.json` (2026-07-21)** — including corrections to several outdated case strings (see that section).

---

## What is Fees/Fines

Fees/Fines are monetary charges against a patron (library user) — either **manual** (staff-created, e.g. replacement card, damage) or **automatic** (system-created by circulation: overdue fines, lost item fees, lost item processing fees). Staff manage them from the patron's **Fees/Fines** accordion in the Users app: charge, pay, waive, refund, transfer, cancel (error), and view history. Settings that drive the feature live under `Settings > Users > Fee/fine`.

---

## Key Terms

| Term | Definition |
|---|---|
| Fee/fine owner | The library/desk that owns the charge; every charge, payment method, transfer account etc. is scoped to an owner. |
| Manual charge (Fee/fine type) | A staff-selectable charge type configured per owner (e.g. "Replacement card"). |
| Payment method | How a payment is recorded (Cash, Card, …), configured per owner. |
| Transfer account | External account a balance can be transferred to, configured per owner. |
| Waive reason / Refund reason | Controlled reasons required when waiving/refunding. |
| Fees/Fines History | The Open / Closed / All tabbed view of a patron's charges (a.k.a. "View all fees/fines"). |
| Balance | Remaining amount owed on a charge after payments/waivers/transfers. |
| Suspended (partially) | A closed fee/fine can still have refundable paid/transferred amounts. |

---

## Setup / Settings (Settings > Users > Fee/fine)

Configured before charging: **Owners** → then per owner: **Manual charges**, **Payment methods**, **Transfer accounts**, **Waive reasons**, **Refund reasons**, and **Comment required** (toggles requiring a comment for pay/waive/refund/transfer/cancel). Also relevant: **Overdue fine policy** and **Lost item fee policy** (in Settings > Circulation) drive automatic charges.

---

## Charge lifecycle

```
(Manual) staff clicks "Create fee/fine" → New fee/fine page → "Charge only" OR "Charge and pay"
(Automatic) circulation creates overdue fine / lost item fee / lost item processing fee

Open (balance > 0)
  ├─ Pay (full → Closed "Paid fully"; partial → stays Open, balance reduced)
  ├─ Waive (full/partial; requires Waive reason)
  ├─ Transfer (full/partial to a Transfer account)
  └─ Cancel as error (closes as "Cancelled as error")
Closed (balance = 0)
  └─ Refund (only if the charge had a Paid or Transferred amount) → refunds to patron
```

---

## UI structure

- **Users app → patron record → "Fees/fines" accordion**: closed accordion shows a count/total badge of outstanding fees/fines; expanded shows open count + amount and a **`View all fees/fines`** link.
- **Fees/Fines History** page: tabs `Open`, `Closed`, `All`; each row selectable via checkbox; row `Actions` (ellipsis) menu; page-level `Actions` menu.
- **Fee/Fine Details** page: opened by clicking a history row; shows the original charge plus an action table (Action date, Action, Amount, Balance, Fee/fine owner, Source, Comments).
- **New fee/fine** page: `Fee/fine owner` dropdown, `Fee/fine type` dropdown, amount, etc.; buttons `Charge only`, `Charge and pay`.

---

## Exact UI Texts

> ✅ Confirmed 2026-07-21 against `folio-org/ui-users/translations/ui-users/en_US.json` (fees/fines UI lives in ui-users). **Corrections applied:** several case-asserted strings were old/paraphrased — real modal title is `Pay fee/fine` (not "Pay Fee/Fine"), the amount field is `Payment amount` (not "Pay amount"), the staff field is `Staff information`, and the error strings are `Payment must be > 0` / `Pay amount exceeds the selected amount` (NOT "Amount must be positive" / "Requested amount exceeds remaining amount", which were 2020 mock text in the case). `{placeholders}` interpolate; `<b>…</b>` = bold.

### Success toast — ONE template for all actions [confirmed]

`The {feeFineType} fee/fine of {amount} has been successfully {paymentStatus} for {name}.`
where `{paymentStatus}` ∈ `paid` / `waived` / `refunded` / `transferred` (key `accounts.actions.calloutMessage`).

### Action modals [confirmed]

| Action | Modal title | Amount field | Method field | Summary verb (full / partial) |
|---|---|---|---|---|
| Pay | `Pay fee/fine` | `Payment amount` | `Payment method` | `Paying` / `Partially paying` |
| Waive | `Waive fee/fine` | `Waive amount` | `Waive reason` | `Waiving` / `Partially waive` |
| Transfer | `Transfer fee/fine` | `Transfer amount` | `Transfer Account` | `Transferring` / `Partially transfer` |
| Refund | `Refund fee/fine` | `Refund amount` | `Refund reason` | `Refunding` / `Partially refunding` |
| Cancel as error | `Confirm fee/fine cancellation` (`Back` / `Confirm`); body `<b>{amount}</b> {feeFineType} fee/fine will be <b>cancelled</b>` | — | — | — |

Pay modal also has: `Fee/fine owner desk` (`Select desk`), `Transaction information` (`Enter check #, etc.`), `Staff information`, `Notify patron`, `Cancel`. Page/menu action labels: `Pay fees/fines`, `Waive fees/fines`, `Transfer fees/fines`.

### Validation / Error messages [confirmed]

| Condition | Message |
|---|---|
| Pay amount ≤ 0 | `Payment must be > 0` |
| Pay amount > selected | `Pay amount exceeds the selected amount` |
| Waive amount ≤ 0 / > selected | `Waive amount must be > 0` / `Waive amount exceeds the selected amount` |
| Transfer amount ≤ 0 / > selected | `Transfer amount must be greater than zero` / `Transfer amount exceeds selected amount` |
| No payment method configured | `No Payment methods exist for Fee/fine owner` |
| No waive reasons | `No Waive reasons exist` |
| No transfer accounts | `No Transfer accounts exist for Fee/fine owner` |
| Comment required (owner setting) | `Additional information for staff is required` / `Comment must be provided` |
| Required field empty | `Please fill this field in to continue` |
| Mixed open+closed selected | Alert modal `Alert details` with `Deselect to continue`; deselect fully-paid rows then proceed |

> Note: whether a closed fee/fine disables the Pay control (greyed out, not an error) still holds from cases — that's UI state, not a string.

### Second "Confirm" step — every action has one [confirmed — C356793, C458; resolves prior Known Gap]

After the Pay/Waive/Refund/Transfer modal's primary button is clicked, a SECOND confirmation modal appears before the action actually commits:
- Pay → `Confirm fee/fine payment` → `Confirm` button closes it and returns to the Fees/fines page.
- Refund → `Confirm fee/fine refund` → same pattern.
- (Waive/Transfer follow the identical two-step pattern by naming convention: `Confirm fee/fine waiver` / `Confirm fee/fine transfer` — not independently re-verified this round, treat as high-confidence but unconfirmed-verbatim.)
- Cancel as error's own confirm step is the SAME modal as the initial one — `Confirm fee/fine cancellation` doubles as both trigger and confirm (no separate second modal for Cancel).

### Financial Transactions Detail Report & Cash Drawer Reconciliation Report — modal validation [confirmed — C343207, C343311, C343314, C343324]

Both reports are triggered from Users app > Actions menu (gated by their own dedicated permissions — Cash Drawer Reconciliation requires `Users: Can create and download Cash drawer reconciliation report`, absent from the Actions menu entirely without it).

| Condition | Message |
|---|---|
| Start date blank, End date also blank | `"Start date" is required` |
| Start date blank, End date filled | `"Start date" is required if "End date" entered` |
| End date < Start date | `"End date" must be greater than or equal to "Start date"` |
| Fee/fine owner not selected (Financial Transactions Detail report) | `"Fee/fine owner" is required` |
| Service point not selected (Cash Drawer Reconciliation report) | `"Service point" is required` |

- Both modals: `Save & close` only activates once all validation passes; `Cancel`/`X` returns to User search results.
- Cash Drawer Reconciliation: selecting a Service point populates a "Sources" dropdown with every user associated with that service point, defaulting to the logged-in user if they themselves are associated with the selected SP.
- Financial Transactions Detail report's exported file title line (confirmed exact format): `Financial Transactions Detail Report for {Fee/Fine Owner}, Service Point(s) {SP1, SP2, ...} - {Start date} to {End date}` — owner is always singular (only one owner per report), Service Point(s) can be zero-to-many, End date defaults to system date if left blank.

### Settings labels (Settings > Users > Fee/fine) [confirmed]

`Fee/fine: Manual charges` (columns `Fee/fine type`, `Default amount`, `Charge notice`, `Action notice`; also `Default charge notice` / `Default action notice`; empty: `There are no Fee/fine: Manual charges`); `Fee/fine: Payment methods` (`Payment method`, `Refund method allowed`; empty: `There are no Fee/fine: Payment methods`). Manual-charge validation: `Default Amount must be numeric`, `Default Amount must be positive`, `Fee/fine type exists`. Delete guard: `Fee/fine Type cannot be deleted when used by one or more user accounts` (modal `Delete Fee/Fine Type?`).

---

## Capability Sets (Eureka)

Curated from precondition patterns (confirm exact names in env):
- `Data - UI-Users Feesfines - View` (view fees/fines)
- `Data - UI-Users Feesfines - Create/Edit` (charge, pay, waive, transfer, cancel)
- `Procedural - UI-Users Feefine Refund - Execute` (refund)
- Settings: `Settings - UI-Users Feefines - Manage` (owners, manual charges, payment methods, transfer accounts, waive/refund reasons)
- Cross-app often required: `Data - UI-Users - View` (view user profile), `Data - UI-Inventory Instance - View` (for lost item context).

> Legacy permission names commonly seen in older cases: "Users: View fees/fines", "Users: Create, edit, and delete fees/fines", "Settings (Users): Can create, edit and view fee/fine settings". Prefer capability sets for new cases; keep both if the section's existing cases use the two-column table.

---

## Common Verification Patterns

### Charge a manual fee/fine
Preconditions: an Owner + Manual charge (+ Payment method for "Charge and pay") in Settings > Users > Fee/fine; an active patron.
1. On the patron record expand `Fees/fines` → click `Create fee/fine`.
2. Select `Fee/fine owner` and `Fee/fine type`, enter amount → click `Charge only`.
3. Expected: charge appears in `Open` tab with the exact amount; the accordion badge count/total increases by the charge.

### Partial pay
Note the balance; Pay with `Pay amount` < balance → charge stays `Open`, balance = original − pay amount; Fee/Fine Details shows `Action = Paid partially`, `Amount = <pay amount>`, `Balance = <new balance>`.

### Fee/Fine Details page survives reload and direct URL access (confirmed pattern, C808511, 2025)
Open a Fee/Fine Details page, then (a) refresh the browser and (b) copy/paste the same URL into a new navigation — both must reload the same details page correctly with the URL unchanged, not crash. This is a real regression class (UIU-3428: page crashed when visited directly via URL) — worth a dedicated case whenever a story touches this page's routing/deep-linking, not just its content.

### Refund gating (business rule)
`Refund` is active ONLY when the patron has a **paid or transferred** amount. A never-paid open charge → `Refund` inactive. After a full refund → `Refund` becomes inactive for that charge.

### Cover every entry point for each action (team convention)
The team verifies each fee/fine action (Pay/Waive/Refund/Transfer) from **all** entry points, not just one:
- `Actions` menu on the **Open** tab and on the **All** tab of Fees/Fines History,
- the per-row **ellipsis** (`…`) menu,
- the **Fee/Fine Details** page `Actions` menu.
Also cover selection permutations: no row selected → button greyed out; a **closed** fee/fine selected → button greyed out; a mix of open+closed → alert to `Deselect to continue`; **multiple** open fees/fines selected → summary counts and the amount is **split across the selected fees/fines** (equal split, with rounding, e.g. 50.00 across 3 → 16.66 + 16.67 + 16.67). A single "core flow" case is not enough — Scenario Analysis for a fee/fine action should enumerate these entry points and the single-vs-multiple / open-vs-closed matrix.

---

## Lost Item Fee Refund Mechanics on Return/Renew [confirmed — C11031, C11032, C15201; resolves prior Known Gap]

> Applies identically whether the item's status is **Declared lost** or **Aged to lost** — both are resolved by either checking the item in OR successfully renewing it (renew typically requires an override since the item shows as lost).

- Checking in (or renewing) a lost item whose Lost item fee / Lost item processing fee was only **partially** paid/transferred/waived (not fully closed as "Lost and paid") triggers a `Check in aged to lost item` confirmation modal (Cancel/Confirm) — this single modal name is used for both Declared-lost and Aged-to-lost resolution paths.
- On Confirm, each fee/fine is resolved component-by-component:
  - Any **paid** amount is reversed as TWO separate transactions: a `Credit` then a `Refund`, both for the same amount (not one combined reversal transaction).
  - Any **transferred** amount is reversed the same way — Credit then Refund — but credited back to the transfer account rather than the patron.
  - Any remaining **outstanding** (never paid/transferred) balance is written off with fee/fine action `Cancelled item returned` — this is a cancellation, not a refund; nothing is "returned" to anyone since it was never collected.
  - **Waived** amounts are NOT reversed at all — a waiver is a permanent write-off and stays waived even after the item is found/returned.
  - Net effect: balance drops to 0.00 and the fee/fine closes.
- Exact fee/fine action-history strings: `Credited/Refunded fully - Lost item found` (for the paid/transferred reversal) and `Cancelled item returned` (for the outstanding-balance write-off).
- The **Lost item processing fee**'s fate on return/renew is governed by a SEPARATE lost-item-policy toggle, "If lost item returned or renewed, remove lost item processing fee": if **Yes**, the processing fee closes using the identical Credit/Refund/Cancel mechanics above; if **No**, the processing fee fee/fine is left completely untouched — it stays Open with no changes.
- If the lost item fee was already FULLY paid before check-in/renewal (item status already `Lost and paid`), this reversal flow does not apply — that's a distinct scenario (a separate CSV/status-verification case) outside this mechanic's scope.

## Aged to Lost — Process Exclusions and Recall-Specific Interval [confirmed — C15198, C196743; previously undocumented]

- **Claimed returned items are permanently excluded from the aged-to-lost background process** — even once such a loan is well past the aged-to-lost overdue threshold, the job skips it entirely; no lost item fees are ever billed for a Claimed-returned loan unless/until it's explicitly resolved back to Declared-lost via the Resolve-claim dropdown (see loans.md).
- The Lost item fee policy defines **two independent aging tracks**: the regular "Items aged to lost after overdue" / "Patron billed after aged to lost" pair, and a SEPARATE "Recalled items aged to lost after overdue" / "Patron billed for recall after aged to lost" pair used only for items with an active recall. A recalled item ages to lost strictly on its own (typically much shorter) interval, independent of the non-recalled timing.
- Leaving either pair of fields blank disables aging-to-lost for that specific category only — e.g. blank regular-track fields with populated recall-track fields means only recalled items will ever age to lost, non-recalled overdue items never will (and vice versa).

---

## Key Business Rules for Test Cases

1. Every charge, payment method, transfer account, waive/refund reason is scoped to a **Fee/fine owner**; owner setup is a precondition for any charge. (cases)
2. A fee/fine can be **paid, waived, or transferred** fully or partially; partial actions reduce the balance and keep the charge `Open`. (cases)
3. **Refund is only available for fees/fines that were paid or transferred** — not for never-paid open charges; refunding again after a full refund is blocked. (cases — C15188)
4. `Pay`/`Refund` controls are disabled (greyed out), not error-toasted, when the selection is invalid (closed charge, no payment method, nothing selected). (cases — C459)
5. Pay amount must be positive and must not exceed the selected/remaining amount. (cases — C459)
6. Paying multiple fees/fines with one amount splits it smallest-first (fully pay the smallest, then next, leaving the largest possibly partial). (cases — C459 sc.15)
7. Automatic charges (overdue fine, lost item fee, lost item processing fee) are created by circulation per the overdue/lost-item policies; returning/renewing an aged-to-lost item can trigger refunds/adjustments. (cases — Fees&Fines subsections)
8. `Notify patron` defaults to checked when the owner has a default action notice; staff can uncheck. (cases — C459)
9. Fees/Fines History has `Open` / `Closed` / `All` tabs; the `Pay` action is absent on `Closed` (only `Refund` applies there). (cases)
10. Bursar transfer and financial reports (Financial Transactions Detail, Cash Drawer Reconciliation) export closed-period fee/fine activity. (cases — Bursar / reports subsections)
11. Every Pay/Waive/Refund/Transfer action requires a SECOND "Confirm fee/fine {action}" modal after the initial action modal before it actually commits. (cases — C356793, C458)
12. Cancel as error ("Error" action) is greyed out/unavailable the moment a fee/fine has ANY partial (or full) pay/waive/transfer against it — but a fee/fine that was fully paid and THEN fully refunded becomes eligible for Cancel-as-error again, since the refund resets its state back to a clean unpaid balance. (cases — C17157, C356793)
13. When a fee/fine owner/type has no default or type-specific action notice configured, the Pay/Waive/etc. modal omits the "Notify patron" checkbox and "Additional information for patron" field entirely (not merely leaves them unchecked/empty). (cases — C6643)
14. Resolving a lost item (Declared lost OR Aged to lost) via check-in or renewal reverses paid/transferred amounts as paired Credit+Refund transactions, cancels any never-collected outstanding balance outright, and never touches already-waived amounts — governed additionally by the lost-item-policy's own "remove lost item processing fee on return/renew" toggle for the processing-fee component specifically. (cases — C11031, C11032, C15201)
15. Claimed-returned loans are permanently excluded from the automatic aged-to-lost billing process, and recalled items age to lost on their own independently configured interval separate from non-recalled items. (cases — C15198, C196743)
16. **Reminder fees are a graduated overdue-escalation mechanism configured inside an Overdue fine policy** (see the Reminder Fees section below), created by an overnight process on a per-sequence interval; they stop once the item is returned, can block or allow renewal per policy, and re-start a new first reminder if an unreturned overdue item is renewed. (cases — Reminder Fees subsection)

---

## Reminder Fees (confirmed — Reminder Fees subsection; refs CIRC-1527/1528/1599, CIRCSTORE-414/452, MODAUD-165)

A graduated overdue-fee escalation. **Configured inside an Overdue fine policy**, not a separate settings page: `Settings > Circulation > Fee/fine > Overdue fine policies`, in a dedicated **"Reminder fees"** section (independent of the overdue-fine entries — a policy can have reminder fees with no overdue fines).

- Click **"Add reminder fee"** to add a sequence row; each row = one reminder in the escalation. Per-row fields:
  - **Interval** (a number) + a **days/weeks** frequency dropdown — how long after the item goes overdue the reminder fee is created (the 1st row) / after the previous reminder (subsequent rows).
  - **Amount** — the fee charged for that reminder.
  - **Notice method** dropdown (e.g. mail/email) and a **Notice template** (a Patron notice template, e.g. `ODIN_1st reminder`, `ODIN_2nd reminder`), plus a print option.
- **Reminders are generated by an overnight process**, in sequence (1st reminder, then 2nd, …). Testing these end-to-end genuinely spans several days of overnight runs (real cases warn "this test needs five days").
- **Returning the item stops further reminders** — no reminder fees are billed after the item is checked in following the first reminder. (C411799)
- Policy option **"Allow renewal of items with reminder fee(s)"** gates whether an item that already has reminder fee(s) can be renewed. (C451528)
- **Renewing an unreturned overdue item resets the escalation** — a new first reminder fee is created after renewal if the item still isn't returned. (C451530)
- **Closed days shift the reminder schedule** — both regular closed days and closed-on-short-notice days affect when the next reminder fires. (C451535, C451537)
- Mandatory-field validation: saving a reminder-fee sequence with missing mandatory fields is blocked. (C411797)

---

## Authoring style (measured 2026-07-23)

Fees&Fines has the **shortest cases in the project — median ~2 steps** (many are 1–3 steps), `Type` **Other ~79%** (Functional ~20%), `User Journey` ~1% (`No`). The team keeps the heavy setup (patron group, circulation rule, fee/fine owner, policies, a checked-out overdue item) in **Preconditions**, then writes a **very short Steps block** that performs the one action (often a multi-click sequence compressed into a single step with bulleted sub-lines) and asserts one outcome. Don't pad these with navigation ceremony — match the corpus: rich preconditions, 1–3 tight steps, `Other` type. (Exception: Reminder-fee and lost-item lifecycle cases run longer because they walk an overnight/multi-day process.)

---

## Known Gaps / Items to Verify

- [x] Action success-toast + modal/error/settings strings — **confirmed** against `ui-users/en_US.json` (2026-07-21); corrected the outdated case strings.
- [x] Confirm-Pay/Refund step exact heading — **confirmed**: `Confirm fee/fine payment` / `Confirm fee/fine refund` (Waive/Transfer equivalents inferred by naming convention, not independently re-verified).
- [x] Automatic lost-item-fee refund/adjustment rules on return/renew of aged-to-lost/declared-lost items — **confirmed** with exact action-history strings and the paired Credit+Refund transaction mechanic; see new "Lost Item Fee Refund Mechanics" section above.
- [ ] The Owners / Transfer accounts / Waive reasons / Refund reasons / Comment-required settings **column** labels are still not individually confirmed — a few settings sub-pages weren't in the grep sample; verify in env or a targeted ui-users pass.
- [ ] Capability-set names above are inferred from precondition prose — verify exact Eureka capability strings in env.
- [ ] Waive/Transfer's second-confirm modal titles (`Confirm fee/fine waiver` / `Confirm fee/fine transfer`) are inferred by pattern from the confirmed Pay/Refund titles, not independently pulled from a case this round.

> N≥10 audit round (2026-07-22): 14 cases read (C11031, C11032, C15201, C15198, C196743, C356793, C17157, C343311, C343314, C343324, C343207, C400625, C458, C6643). Resolved three of four prior Known Gaps: the second "Confirm" modal step, the full lost-item-fee refund/reversal mechanics (Declared lost + Aged to lost, both via return and renew), and the Cash Drawer Reconciliation / Financial Transactions Detail report validation strings and title format. Surfaced two previously undocumented rules: Claimed-returned loans are excluded from aged-to-lost entirely, and recalled items age to lost on a separate configurable interval. Added 5 new Key Business Rules (11-15).
