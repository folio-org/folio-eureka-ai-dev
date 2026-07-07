# FOLIO Finance App - Business Logic Context

> Generated/refreshed by the build-app-context workflow on 2026-06-18.
> Sources used in this refresh:
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
  - Via CSV upload - prepare CSV with fund codes and amounts -> upload
- Batch allocation jobs are logged; logs can be viewed and deleted

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

---

## Known Gaps / Items to Verify

- [ ] No exact Umbrellaleaf-labeled cases were returned from the group_id=454 subtree in this run
- [ ] Focus-release labels requested by user include "2023 Poppy" while this instance labels it as "R2 2023 Poppy"
- [ ] Jira search for component "Finance" returned 0 Done stories/bugs in this run; verify component naming conventions in the current Jira dataset
- [ ] Keep UI toast/modal assertions conservative unless confirmed directly in target environment, since this file prioritizes stable business rules over noisy text extraction
