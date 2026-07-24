# FOLIO Finance App - Business Logic Context

> Generated/refreshed by the build-app-context workflow on 2026-06-18.
> **Manual enrichment on 2026-07-21** (browser-based). TestRail cases C186156/C380517/C648502 supplied the Transaction detail-pane fields, Budget structure, Rollover page/dialogs and rollover rules. The public GitHub translation file `folio-org/ui-finance/translations/ui-finance/en_US.json` supplied every exact toast, error, confirm-dialog and create-form field label. "Exact UI Texts" is now complete for Finance; see Known Gaps for the (minor) remaining metadata staleness.
> Sources used in the 2026-06-18 run:
> - TestRail subtree scoped from group_id=454 (sections: 12, cases: 249 total)
> - Focus releases requested: Umbrellaleaf, Trillium, Sunflower, Ramsons, 2023 Poppy (0 exact-label matches in this subtree)
> - Release labels observed in this subtree include: Trillium (16), Sunflower (28), Ramsons (56), Poppy (as "R2 2023 Poppy", 24)
> - GitHub: folio-org/ui-finance, folio-org/mod-finance-storage (9 files sampled)
> - Jira: FOLIO component "Finance" (0 Done stories, 0 Done bugs returned in this run)
> This file combines stable Finance domain rules with run evidence for test-writing decisions.

---

## What is Finance

The Finance app manages library budget structures, tracks spending, and controls who can access financial records. It is tightly integrated with Orders (encumbrances) and Invoices (payments). All financial activity flows through Finance transactions.

---

## Record Hierarchy

```
Fiscal Year
  └── Ledger  (linked to one or more Fiscal Years)
        └── Fund  (belongs to exactly one Ledger)
              └── Budget  (one per Fund per Fiscal Year)
                    └── Transactions (Allocation, Encumbrance, Pending payment, Payment, Transfer, Credit)

Group  (cross-Ledger grouping of Funds - for reporting/summary only)
```

---

## Fiscal Year

### Required fields
- Name - e.g. "Fiscal Year 2026"
- Code - must start with alpha prefix followed by a 4-digit number (e.g. FY2026); the alpha prefix determines the fiscal year series and must be consistent for rollover (e.g. FYA2026 -> FYA2027)
- Period Begin Date (UTC)
- Period End Date (UTC)

### Key rules
- A single tenant can have multiple fiscal year series running in parallel (e.g. FYA for academic library, FYG for government library on different calendar years)
- The "current" fiscal year is determined by whether today's date falls within the Period Begin-End range, not by a manual flag
- A ledger can be associated with multiple fiscal years (for rollover history)
- Budget currency is locked at fiscal year creation time - set to the tenant primary currency when the fiscal year record is created; if tenant currency changes later, existing budgets remain in the original currency
- Optional: Acquisition units, Description

---

## Ledger

### Required fields
- Name
- Code - user-created, unique
- Fiscal year one - the first fiscal year for this ledger
- Status - Active / Frozen / Inactive

### Key fields
| Field | Notes |
|---|---|
| Enforce all budget encumbrance limits | Checked by default; if checked: FOLIO rejects encumbrances that exceed available budget |
| Enforce all budget expenditure limits | Checked by default; if checked: FOLIO rejects expenditures that exceed available budget |
| Acquisition units | Controls who can view/edit this ledger |
| Description | Optional |

### Ledger status values
- Active - ongoing; funds and budgets can be transacted against
- Frozen - paused; no new transactions allowed
- Inactive - no longer in use

### Ledger detail view
Shows: associated Funds with current Budget values, Groups, summary totals per fiscal year.

### Exporting ledger funds and budgets
- Ledger detail view -> Actions -> Export -> downloads CSV of all funds and budgets for the ledger

### Rollover
Triggered from ledger Actions -> Rollover:
1. Creates new budgets for the next FY (configurable allocation carry-over)
2. Creates new encumbrances for open orders in the next FY
3. Optionally closes current budgets
4. Does not automatically advance the "current" FY - determined by FY period dates
- Requires Finance rollover execute capability set

---

## Group

### Required fields
- Name
- Code
- Status - Active / Frozen / Inactive

### Key characteristics
- Cross-ledger grouping of funds for summary/reporting
- Does not restrict transactions - reporting only
- A fund can belong to multiple groups
- Optional: Acquisition units, Description

---

## Fund

### Required fields
- Name
- Code - must be unique; alphanumeric recommended
- Ledger - exactly one; cannot be changed after creation
- Status - Active / Frozen / Inactive

### Key fields
| Field | Notes |
|---|---|
| Currency | Pre-filled from the fiscal year currency; read-only after creation |
| Type | Optional category (e.g. Endowment, Restricted); used to group funds at rollover; funds without type grouped under "No fund type" at rollover |
| Acquisition units | Controls access; funds with restricted acquisition units are hidden from fund distribution dropdowns in Orders/Invoices for users outside those units |
| Group | Assign fund to one or more groups |
| Transfer from | Restrict which funds can transfer into this fund; blank = any fund allowed |
| Transfer to | Restrict which funds this fund can transfer to; blank = any fund allowed |
| External account number | Optional accounting system reference |
| Description | Optional |
| Donor information | Optional donor attribution |
| Locations | Optional location restrictions - limit fund use to specific library locations |
| Tags | Optional |

### Fund status
- Active - required for orders to be opened against this fund and for invoices to be paid
- Frozen - paused; no new transactions
- Inactive - no longer in use

---

## Budget

One budget per Fund per Fiscal Year.

### Required fields
- Name (auto-suggested from fund code + fiscal year code)
- Fiscal Year - selects which FY this budget covers

### Key fields
| Field | Notes |
|---|---|
| Allowable encumbrance (%) | Maximum percentage of allocation that can be encumbered; optional; if blank, no encumbrance limit beyond ledger setting |
| Allowable expenditure (%) | Maximum percentage of allocation that can be expended; optional |
| Status | Active / Planned / Closed |
| Expense classes | Add one or more expense classes to track spending by category within the budget |

### Budget financial buckets

| Bucket | Description | Formula |
|---|---|---|
| Allocated | Total money assigned to this budget | Sum of all Allocation transactions |
| Net transfers | Money moved in/out via Transfer transactions | Transfers in - Transfers out |
| Total funding | Allocated + Net transfers | Allocated + Net transfers |
| Encumbered | Reserved for open orders not yet invoiced | Sum of open Encumbrance transactions |
| Awaiting payment | Approved invoices not yet paid | Sum of Pending payment transactions |
| Expended | Paid invoices | Sum of Payment transactions |
| Unavailable | Encumbered + Awaiting payment + Expended | Sum of all committed/spent amounts |
| Over encumbered | Amount by which encumbrances exceed available | Only shows if ledger restrictions disabled |
| Over expended | Amount by which expenditures exceed available | Only shows if ledger restrictions disabled |
| Cash balance | Total funding - Expended | Remaining cash |
| Available | Total funding - Unavailable | Money not yet committed |

### Budget status values
- Active - current; accepts transactions
- Planned - future budget; not yet active for transactions
- Closed - no longer accepting transactions; typically set during fiscal year rollover

### Expense classes
- Optional sub-categories within a budget (e.g. Monographs, Serials, Electronic)
- Configured in Settings -> Finance -> Expense classes
- Applied on Order lines and Invoice lines during fund distribution
- Each fund can have multiple expense classes on a budget

---

## Allocation Transactions

Allocation adds money to a budget. Three allocation operations:

### Increase allocation
- Budget -> Actions -> Increase allocation
- Enter amount -> Save -> Allocation transaction created
- Requires allocation create capability set + view/edit fund and budget capability sets

### Decrease allocation
- Budget -> Actions -> Decrease allocation
- Reduces the allocated amount
- Cannot decrease below what is already committed (unavailable)

### Move allocation (between funds)
- Moves money from one fund budget to another fund budget
- Budget -> Actions -> Move allocation
- Both funds must be in the same ledger (or have transfer restrictions satisfied)

### Batch allocations
- Multiple funds can be allocated simultaneously:
  - Via UI - select multiple funds -> Actions -> Batch allocate -> enter amounts per fund
  - Via **allocation worksheet (CSV)** - download the worksheet, edit it, upload it back
- Batch allocation jobs are logged; logs can be viewed and deleted (separate capability sets: `Data - UI-Finance Fund-Update-Logs - View` / `- Delete`)

#### Allocation worksheet (CSV) — download & upload (confirmed C648502/C648514/C651511 etc.; refs UIF-525, UIF-526, MODFIN-391, MODFIN-421)

- **Download:** from a **Ledger view** → `Actions > Download allocation worksheet (CSV)` → **"Select fiscal year"** modal (`Fiscal year` dropdown, **newest FY selected by default**, `Cancel` / `Confirm`). Confirm shows toast `Please wait while the worksheet is generated. Your download will start automatically` and downloads a CSV.
- **Worksheet columns:** Fund columns are always populated — `Fiscal year`, `Fund name`, `Fund code`, `Fund UUID`, `Fund status`; Budget columns — `Budget name`, `Budget UUID`, `Budget status`, `Budget initial allocation`, `Budget current allocation`, … — are **blank when the fund has no budget for that FY** (that's how a budget gets *created* on upload).
- **Upload:** `Actions > Upload allocation worksheet (CSV)` **creates or updates budgets in batch** for the worksheet's fiscal year — works for both the **Current** and a **Future** fiscal year (C648514 / C651511). A blank budget row → budget created; a filled row → budget updated.
- **Upload validations (each its own negative case):** rejects a file that is not `.csv`, a worksheet with a **missing column**, a CSV that **doesn't correspond** to the generated worksheet, rows whose **fiscal years differ**, a **fund belonging to another Ledger**, and **invalid fund/budget status** values. Batch-allocation access is also capability-gated (a user without the capability can't reach the worksheet actions).

---

## Transfer Transactions

Transfers move money between two fund budgets.

### Creating a transfer
- From budget: Actions -> Transfer
- Specify: From fund (source), To fund (target), Amount, Fiscal year
- Transfer restrictions on funds (Transfer from/to fields) are enforced
- Requires transfer create capability set

### Transfer restrictions
- If a fund has Transfer from restrictions: only listed funds can transfer into it
- If a fund has Transfer to restrictions: only listed funds this fund can transfer to
- Blank fields = no restrictions

---

## Encumbrances

Created automatically by Orders when a PO is opened. Not manually creatable in Finance UI.

### Manually releasing an encumbrance
- Budget transaction log -> select encumbrance -> Release encumbrance
- Requires encumbrance manual release capability set
- Use case: vendor cancelled; free funds before invoice arrives

### Unreleasing an encumbrance
- Budget transaction log -> select released encumbrance -> Unrelease encumbrance
- Requires encumbrance unrelease capability set
- Use case: encumbrance released by mistake during invoice approval

---

## Transactions

All financial activity is recorded as immutable transactions. Transactions cannot be edited or deleted.

| Transaction type | Created by | Budget impact |
|---|---|---|
| Allocation | Finance app (manual) or Rollover | Allocated increases |
| Transfer | Finance app (manual) | Source Available decreases, Target Available increases |
| Encumbrance | Orders (on PO Open) | Encumbered increases, Available decreases |
| Pending payment | Invoices (on Approve) | Awaiting payment increases, Encumbered decreases |
| Payment | Invoices (on Pay) | Expended increases, Awaiting payment decreases |
| Credit | Invoices (credit invoice) | Available increases |
| Rollover transfer | Fiscal year rollover | Carries allocation/encumbrance to new FY |

### Viewing transactions
- Budget detail view -> Transactions accordion -> filter by type, date, amount
- Typical columns: Transaction date, Type, Amount, Source (Order/Invoice/Manual), Tags

---

## Acquisition Units

Acquisition units gate access to Finance records (same behavior as in Orders and Invoices).

### How they work
- Each Finance record (Fiscal Year, Ledger, Fund, Group) can have one or more Acquisition units assigned
- User must be a member of at least one assigned unit to view/edit the record
- Users with bypass acquisition unit capability can access all records
- Hidden from fund distribution: funds with acquisition unit restrictions are filtered out of fund selection dropdowns in Orders/Invoices for users outside those units

### Assign on create vs manage on edit
- Assign acquisition units to new record (Procedural execute) - only allows assigning units on create
- Manage acquisition units (Data manage) - allows changing unit assignment when editing existing records

---

## Recalculate Budget Totals

In case of data inconsistency (e.g. transactions deleted administratively):
- Budget -> Actions -> Recalculate budget totals
- Recomputes all bucket values from actual transactions
- Requires recalculation execute capability set

---

## Deleting Records

| Record | Can be deleted when... |
|---|---|
| Budget | Status is Planned or Closed; no transactions |
| Fund | No active budget with transactions; not referenced by open orders or unpaid invoices |
| Ledger | No active funds |
| Group | Always deletable (no transactional dependency) |
| Fiscal Year | Not referenced by any ledger |

---

## Rollover Fiscal Year

Triggered from a Ledger -> Actions -> Rollover.

### Rollover configuration options
- Rollover type: whether to roll over encumbrances (open orders) into new FY
- Allocation strategy: carry over full amount / carry over remaining amount / no carry over
- Close budgets: optionally close current FY budgets after rollover
- Fund types: rollover can be configured per fund type

### What rollover does
1. Creates new Budget records for each fund in the ledger for the new fiscal year
2. Creates new Encumbrance transactions in new budgets for each open PO with encumbrances in current year
3. Optionally closes current year budgets (status = Closed)
4. Generates a rollover log with results

### Rollover log
- Viewable after rollover: shows successes, errors, funds processed
- Accessible from: Ledger -> Rollover logs

---

## Exact UI Texts

> Use these verbatim in expected results. Never paraphrase.
> ✅ **Fully seeded on 2026-07-21.** Modal/transaction-pane/budget/rollover fields were mined from TestRail cases (C186156, C380517, C648502); all toast, error, dialog and form-field strings below were pulled verbatim from the public GitHub translation file `folio-org/ui-finance` → `translations/ui-finance/en_US.json`. These are the exact rendered strings — safe to assert directly. `{placeholders}` interpolate at runtime.

### Transaction detail pane — fields (the core Finance verification surface)

When a step opens a transaction (Encumbrance, Payment, Pending payment, Credit, Allocation, Transfer) from a budget's `View transactions`, the detail pane shows these fields — verify column-by-column with exact values [confirmed — C186156]:
`Transaction date`, `Fiscal year`, `Amount`, `Source` (e.g. the PO line, hyperlinked), `Type`, `From` (source fund), `To` (target fund), `Expense class`, `Tags`, `Initial encumbrance`, `Awaiting payment`, `Expended`, `Status`, `Description`.
Encumbrance `Status` values: `Unreleased`, `Released`, `Pending`.

### Budget page structure

- Fund pane accordions: `Current budget`, `Planned budget` (a rolled-over budget appears here named `<Fund code> - <FY code>`, e.g. "Fund A - FY #2"). [confirmed — C186156]
- Budget page accordions: `Budget summary` (Funding information table: Allocated, Net transfers, Total funding, Encumbered, Awaiting payment, Expended, Unavailable, Over encumbered/expended, Cash balance, Available), `Budget information` (contains `Status` field and the `View transactions` link), `Expense classes`.
- Budget `Status` values: `Active`, `Planned`, `Closed`.

### Modal / Dialog Fields & Titles

| Modal | Fields / elements | Source |
|---|---|---|
| Move allocation | `From` dropdown, `To` dropdown (pre-filled with the fund whose budget you opened), `Amount*` field, `Tags` dropdown, `Description` field, a **`Swap` button/icon that instantly swaps the `From`/`To` selections** (re-evaluates the negative-allocation validation live — swapping can flip `Confirm` from disabled to enabled or vice versa), `Cancel` button, `Confirm` button (blue, highlighted) | [confirmed — C380517, C825298] |
| Increase allocation / Decrease allocation | Opened from Budget → Actions; amount entry + Confirm | [from cases] |
| Transfer | `From` / `To` budget fields, Amount, Confirm | [from cases — C6650] |
| Unpaid invoices (during rollover) | message `FOLIO has found invoices that are not yet paid or canceled. If you are sure you want to continue with rollover click continue.` + `Continue` button | [confirmed — C186156] |
| Fiscal year rollover (confirm) | `Confirm` button; on success a toast + `Close & view ledger details` button appear | [confirmed — C186156] |

### Rollover page — fields (Ledger → Actions → Rollover)

Top-level: `Fiscal year` dropdown; `Enforce all budget encumbrance limits during rollover` checkbox (labelled `Enforce all budget encumbrance limits` before Ramsons); `Enforce all budget expenditure limits during rollover` (removed since Trillium); `Close all current budgets` checkbox. [confirmed — C186156]
`Rollover budgets` accordion: `Rollover allocation` checkbox, `Adjust allocation, %` field, `Rollover budget value` dropdown (option `None`), `Rollover value as` dropdown (e.g. `Transfer`), `Set allowances` checkbox, `Allowed encumbrance, %`, `Allowed expenditure, %`.
`Rollover encumbrances` accordion: `Ongoing encumbrances` toggle, `Ongoing-subscription encumbrances` toggle, `One-time encumbrances` toggle, each with a `Based on` dropdown (options `Expended`, `Initial encumbrance`) and an `Increase by, %` field.

### Validation / Error Messages (inline)

| Condition | Message text | Behaviour | Source |
|---|---|---|---|
| Move/allocate amount would drive total allocation negative | `Total allocation cannot be less than zero` | Red message below the `Amount` field; `Confirm` becomes **disabled** (no error toast — validation is inline, the action cannot be submitted) | [confirmed — C380517] |

> Note the interaction model: insufficient-funds is caught by **inline validation that disables Confirm**, NOT by an error toast after submitting. Do not write a "click Confirm → error toast" flow for this scenario.

### Button / Action Labels (key actions)

Actions, Increase allocation, Decrease allocation, Move allocation, Transfer, Confirm, Cancel, Continue, View transactions, Rollover, `Close & view ledger details`, Export (Ledger), Save & close. [from cases]

### Toast Messages

> All rows below are **[confirmed — GitHub `ui-finance/translations/ui-finance/en_US.json`, pulled 2026-07-21]**. `{placeholders}` are interpolated at runtime; `<b>` marks bold segments in the rendered toast.

| Event | Toast text |
|---|---|
| Increase allocation | `{amount} was successfully allocated to the budget <b>{budgetName}</b>.` |
| Decrease allocation | `Budget <b>{budgetName}</b> allocation was successfully decreased by {amount}.` |
| Move allocation | `{amount} was successfully allocated to the budget <b>{budgetName}</b>.` |
| Transfer | `{amount} was successfully transferred to the budget <b>{budgetName}</b>.` |
| Budget saved | `Budget <b>{name}</b> has been saved` |
| Budget created | `Budget <b>{name}</b> successfully <b>created</b> for fund <b>{fundName}</b>` |
| Fund saved | `Fund has been saved` |
| Fund deleted | `Fund has been deleted` |
| Ledger saved | `Ledger has been saved` |
| Ledger deleted | `Ledger has been deleted` |
| Group saved | `Group has been saved` |
| Group deleted | `Group has been deleted` |
| Fund added to group | `Fund(s) have been added to group` |
| Fiscal year saved | `Fiscal year has been saved` |
| Fiscal year deleted | `Fiscal year has been deleted` |
| Release encumbrance | `Encumbrance was released` |
| Unrelease encumbrance | `Encumbrance was unreleased` |
| Recalculate budget totals | `Budget totals have been updated based on current budget transactions` |
| Rollover complete | `Rollover is complete` (header `Rollover {fromYearCode} to {toYearCode}` on the Ledger name pane) |
| Batch allocations updated | `Allocations have been updated successfully.` |
| Batch budgets created | `Budgets have been created successfully.` |
| Export budget CSV started | `Export of <b>{name}</b> data has started` |
| Export budget CSV success | `<b>{name}</b> data was successfully exported to CSV` |

### Error / Validation Messages (confirmed — GitHub translations, 2026-07-21)

| Condition | Message text |
|---|---|
| Allocation/transfer would make total allocation negative | `Total allocation cannot be less than zero` (inline; disables Confirm) |
| Allocate more than source has | `{amount} was not successfully allocated to the budget <b>{toBudgetName}</b> because it exceeds the total allocation amount of <b>{fromBudgetName}</b>.` |
| Allocate more than source has, restrictions active | `{amount} was not successfully allocated to the budget <b>{toBudgetName}</b> because it exceeds the total allocation amount of <b>{fromBudgetName}</b> and ledger fund restrictions are active.` |
| Transfer more than Available | `Transfer was not successful. There is not enough money Available in the budget to complete this Transfer.` |
| Same-budget transfer/allocation | `Transfers and allocations can not be made from one budget to that same budget` |
| Transfer restriction (allow transfer to/from) blocks it | `This transaction cannot be made between these two Funds as the "allow transfer to or from" Fund setting on one or more of the Funds is too restrictive.` |
| Fund name duplicate on ledger | `This Fund name is already in use on the selected Ledger.` |
| Fund code duplicate | `This Fund code is already in use.` |
| Ledger name/code duplicate | `This Ledger name is already in use.` / `This Ledger code is already in use.` |
| Fiscal year code duplicate | `This Fiscal year code is already in use` |
| Fiscal year code format | `Fiscal year Code format must be an Alpha followed by a four digit numeric. Eg. ExampleFY2020` |
| Fiscal year period invalid | `Fiscal year has not been saved. Fiscal year period end date is earlier than start date` |
| Delete budget with transactions | `Budget can not be deleted, because it has transactions` |
| Delete budget with expense classes | `Unable to delete budget. You can not delete a budget that has been assigned one or more expense classes.` |
| Negative available (confirm modal) | heading `Negative available amount`; message `Completing this transaction will result in <b>{budgetName}</b> having a negative available amount. Are you sure you would like to complete this transaction?` |

### Confirm / Delete dialogs (confirmed — GitHub translations)

| Dialog | Heading / message |
|---|---|
| Delete fund | `Delete fund` / `Are you sure you want to delete fund?` |
| Delete ledger | `Delete ledger` / `Are you sure you want to delete ledger?` |
| Delete group | `Delete group` / `Are you sure you want to delete group?` |
| Delete budget | `Delete budget` / `Are you sure you want to delete budget?` |
| Delete fiscal year | `Delete fiscal year` / `Are you sure you want to delete Fiscal year` |
| Release encumbrance | `Release encumbrance` / `Are you sure you want to release this encumbrance? Any remaining amount will be added back to the budget.` |
| Unrelease encumbrance | `Unrelease encumbrance` / `Are you sure you want to unrelease this encumbrance? Any remaining amount will be encumbered against the budget.` |
| Rollover confirm | `Fiscal year rollover` / `Ledger <b>{ledgerName}</b> for <b>{currentFYCode}</b> will be rolled over to <b>{chosenFYCode}</b>. ... This process may take several minutes to complete and cannot be undone.` |
| Save fund (duplicate name) | `Save fund` / `Warning: You are about to add a fund with the same name as an existing fund. Would you like to complete this action?` |

### Create-form titles & field labels (confirmed — GitHub translations)

- Form titles: `Create fund`, `Create ledger`, `Create fiscal year`, `Create group` (edit variants: `Edit fund`/`Edit ledger`/`Edit fiscal year`/`Edit group`).
- **Fund** fields (Fund information): `Name`, `Code`, `Ledger`, `Status`, `Currency`, `Type`, `Group`, `Acquisition units`, `Transfer from`, `Transfer to`, `External account`, `Description`, `Donor information`, `Restrict use by location`, `Locations`. Statuses: `Active`, `Frozen`, `Inactive`.
- **Ledger** fields (Ledger information): `Name`, `Code`, `Status`, `Fiscal year one`, `Description`. Also `Current fiscal year`. Statuses: `Active`, `Frozen`, `Inactive`.
- **Fiscal year** fields: `Name`, `Code`, `Period Begin Date (UTC)`, `Period End Date (UTC)`, `Description`.
- **Group** fields (Group information): `Name`, `Code`, `Fiscal year`, `Status`, `Description`. Statuses: `Active`, `Frozen`, `Inactive`.

---

## Capability Sets (Eureka)

| Action | Capability Set |
|---|---|
| View fiscal years | Data - UI-Finance Fiscal-Year - View |
| Create/edit fiscal years | Data - UI-Finance Fiscal-Year - Create/Edit |
| Delete fiscal years | Data - UI-Finance Fiscal-Year - Delete |
| View ledgers | Data - UI-Finance Ledger - View |
| Create/edit ledgers | Data - UI-Finance Ledger - Create/Edit |
| Delete ledgers | Data - UI-Finance Ledger - Delete |
| View groups | Data - UI-Finance Group - View |
| Create/edit groups | Data - UI-Finance Group - Create/Edit |
| Delete groups | Data - UI-Finance Group - Delete |
| View funds and budgets | Data - UI-Finance Fund-Budget - View |
| Create/edit funds and budgets | Data - UI-Finance Fund-Budget - Create/Edit |
| Delete funds and budgets | Data - UI-Finance Fund-Budget - Delete |
| Create allocations | Data - UI-Finance Allocations - Create |
| Create transfers | Data - UI-Finance Transfers - Create |
| Execute fiscal year rollover | Procedural - UI-Finance Ledger Rollover - Execute |
| Manually release encumbrance | Procedural - UI-Finance Encumbrance Release-Manually - Execute |
| Unrelease encumbrance | Procedural - UI-Finance Encumbrance Unrelease - Execute |
| Recalculate budget totals | Procedural - UI-Finance Fund-Budget Recalculate-Totals - Execute |
| Export finance records | Procedural - UI-Finance - Execute |
| Assign acquisition units to new record | Procedural - UI-Finance Acq Unit Assignment - Execute |
| Manage acquisition units on existing record | Data - UI-Finance Acq Unit Assignment - Manage |
| View batch allocation logs | Data - UI-Finance Fund-Update-Logs - View |
| Delete batch allocation logs | Data - UI-Finance Fund-Update-Logs - Delete |

---

## Key Business Rules for Test Cases

1. Budget values are read-only and derived from transactions; they cannot be directly edited
2. Budget currency is locked at fiscal year creation; tenant currency changes do not retroactively alter existing budgets
3. Fund belongs to exactly one ledger and cannot be reassigned after creation
4. Ledger enforce encumbrance/expenditure limits are checked by default; if enabled, overdraw transactions are blocked
5. Acquisition units gate access and hide restricted funds from Orders/Invoices distribution dropdowns
6. Fund must be Active for orders to open and invoices to pay
7. Groups are reporting-only and do not affect transaction processing
8. Current fiscal year is date-driven, and rollover does not manually set current FY
9. Transactions are immutable; corrections require recalculate or compensating transactions
10. One budget per fund per fiscal year
11. Closed budgets block new transactions
12. Fund type drives rollover grouping; untyped funds fall under "No fund type"
13. Budget allowable encumbrance/expenditure percentages can impose additional limits
14. Transfer restrictions are directional and enforced on both incoming and outgoing paths
15. Assign vs Manage acquisition unit capability sets are distinct and independently required
16. Rollover requires a dedicated procedural capability set
17. Release and Unrelease encumbrance are separate procedural capability sets
18. Batch allocation log deletion capability set is separate from viewing logs
19. Fund code uniqueness is global across ledgers
20. Expense classes are optional but transaction-visible and used for spending analysis
21. **Rollover creates a `Planned budget` for each fund in the new FY** and (if `Close all current budgets` is set) moves the source budgets to `Closed`; encumbrances roll per the Rollover encumbrances toggles. Rolled encumbrances land as `Unreleased` in the new-FY budget; the closed-FY copy reflects the pre-rollover end state. (cases — C186156)
22. **Rollover is blocked-with-warning by unpaid invoices** — the `Unpaid invoices` dialog appears and requires explicit `Continue` before the rollover confirm. (cases — C186156)
23. **A fiscal year series is identified by its alpha code prefix** (e.g. `FYA2025` → alpha `FYA`); rollover requires the next FY to share the same alpha. (cases — C186156)
24. **A ledger can only be rolled over once from a given source fiscal year.** After Ledger rolls FY-A → FY-B, attempting a second rollover from the ledger's (now-current) FY-B to a further FY-C does not error on FY-C being invalid — it errors because the ledger *already has a completed rollover on record*: `"{ledgerName} was already rolled over from the {fromYearCode} fiscal year to the {toYearCode} fiscal year"`, and the second rollover does not run. Test this as its own scenario (rollover once → succeed; immediately rollover again → blocked with this exact message), not just "rollover succeeds." (cases — C360956)
25. **"Move allocation" and "Transfer" enforce negative-available differently** — Move allocation is a **hard block**: if the amount would drive total allocation negative, `Confirm` is disabled with the inline message `Total allocation cannot be less than zero` and the action cannot be submitted at all. Transfer, by contrast, **allows** a resulting negative available balance but requires an extra confirmation step: clicking `Confirm` first opens a `Negative available amount` dialog (`Completing this transfer will result in <budgetName> having a negative available amount. Are you sure you would like to complete this transaction?`); only a second `Confirm` on that dialog commits it. Don't write these two actions as having the same negative-balance behavior — one is blocked outright, the other is allowed-with-warning. (cases — C374166, C374183)
26. **Remaining allowed encumbrance is computed, not just compared to a flat cap**: `remaining allowed encumbrances = (allocated + netTransfers) × allowableEncumbered% − (encumbered + awaitingPayment + expended)`. When a PO's requested encumbrance would exceed this remaining figure (with "Enforce all budget encumbrance limits" active on the Ledger), Opening the order fails with the toast `One or more fund distributions on this order can not be encumbered, because there is not enough money in [{Fund name}].` — order stays `Pending`, the POL's Current encumbrance shows `-`, and no encumbrance transaction is created for that order at all (verify via Fund > Actions > View transactions for current budget). This is the Orders-side symptom of a Finance-side limit; when writing an Orders test for this, cross-check the encumbrance math against this formula rather than guessing a round-number threshold. (cases — C449364)
27. **"Available" (and similarly negative budget figures) render in parentheses, not with a minus sign**, since Ramsons — e.g. `($500.00)` for a budget that is $500 over. Pre-Ramsons cases/screenshots show a leading `-` instead; don't assert the old format against a current-release environment. (cases — C374183, C496145)
28. **A Fund's "Restrict use by location" checkbox blocks Save & close on its own, with no separate confirm step.** Checking it expands a `Locations` accordion showing `Locations must be assigned` while empty; attempting to Save & close with the checkbox checked and zero locations added leaves the user on the Create/Edit page with that warning still showing — it does not throw a toast or navigate away. Unchecking the box removes the requirement immediately (accordion disappears, Save & close proceeds normally). Test both the blocked-save path and the unchecked-passthrough path, not just "restricted funds require locations" as a single assertion. (cases — C423530)
29. **Rollover based on "Expended" promotes the Planned budget to Active and folds the old Current budget's allocation into it** — after rollover, the old FY's budget becomes `Closed`; the new FY's Planned budget becomes `Active`, with `Initial allocation` = the Planned budget's own pre-set allocation, `Increase in allocation` = the old Current budget's allocated amount, and `Total allocated` = the sum of both. Additionally, any **paid-invoice amount that exceeded the old POL's fund-distribution value** rolls forward as a new `Unreleased` encumbrance in the new fiscal year, sourced to the same PO number, with `Initial encumbrance` = that paid amount and `Awaiting payment`/`Expended` reset to $0.00. Don't test "Planned → Active" and "encumbrance carries the overage" as unrelated facts; they're two sides of the same rollover-with-Expended-basis behavior. (cases — C359186)
30. **With `Rollover allocation` OFF and `Rollover budget value` = `None`, the new FY's Planned budget still gets created and set `Active` — just entirely zeroed out**: `Initial allocation`, `Increase/Decrease in allocation`, `Total allocated`, `Net transfers`, `Unavailable`, and `Available` all read `$0.00`/`0`. This refines Rule 21 — "a Planned budget is created for each fund" doesn't by itself imply it carries any money forward; the specific combination of toggles determines whether it's a real starting balance or an empty shell. (cases — C376609)

---

## Authoring style (measured 2026-07-23)

Finance is strongly **`Functional` (~94%)**, median ~7 steps, `User Journey` ~2% (`No`). Cases live and die on **exact monetary values**: preconditions establish the full hierarchy (Fiscal year with today in its period, active Ledger, Fund with a current Budget and specific `Allocated`/`Encumbered`/`Available`) and steps verify budget buckets **absolutely, bucket-by-bucket** (`Initial allocation`, `Increase in allocation`, `Total allocated`, `Net transfers`, `Encumbered`, `Awaiting payment`, `Expended`, `Unavailable`, `Available`), plus the underlying Transaction rows (Type/Source/Amount/Status). Multi-fiscal-year features (rollover, batch-allocation worksheet, future-FY budgets) require the previous+current(+future) FY with an identical letter part as preconditions. `refs` frequently span sibling FE/BE tickets (e.g. `UIF-525, UIF-526, MODFIN-391, MODFIN-421`). Match this: concrete amounts, `Functional` type, column-level budget/transaction verification.

---

## Known Gaps / Items to Verify

- [ ] No exact Umbrellaleaf-labeled cases were returned from the group_id=454 subtree in this run
- [ ] Focus-release labels requested by user include "2023 Poppy" while this instance labels it as "R2 2023 Poppy"
- [ ] Jira search for component "Finance" returned 0 Done stories/bugs in this run; verify component naming conventions in the current Jira dataset
- [ ] Keep UI toast/modal assertions conservative unless confirmed directly in target environment, since this file prioritizes stable business rules over noisy text extraction
- [x] "Exact UI Texts" is now complete: Transaction detail pane, Budget page structure, all modals, the full Rollover page/dialogs (from TestRail C186156/C380517/C648502) **plus** every toast, error, confirm-dialog and create-form field label pulled verbatim from `ui-finance/translations/ui-finance/en_US.json` on 2026-07-21. No known UI-string gaps remain for Finance.
- [ ] Only the automated `build-app-context` **run metadata** at the top is stale (0 Jira issues, 9 GitHub files) — the content has since been enriched manually. A fresh full run would also pull `mod-finance-storage` API schemas and Jira acceptance criteria, but is no longer needed to write accurate Finance cases.

> Random spot-check (2026-07-22): picked one fresh uncited case at random from the "Fiscal Year Rollover" subsection (C376609) — a large, detailed rollover scenario. The general "Planned budget is created" rule already existed (21) but didn't cover the specific zeroed-out outcome when Rollover allocation is off and Rollover budget value is None. Added Rule 30 as a refinement rather than a new top-level fact.
