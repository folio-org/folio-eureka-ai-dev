# FOLIO Invoices App - Business Logic Context

> Generated/refreshed by the build-app-context workflow on 2026-06-18.
> Sources:
> - TestRail section subtree under group_id=329 scoped to Invoices roots (sections: 329, 1289, 37957; 276 cases total).
> - Focus releases requested: Umbrellaleaf, Trillium, Sunflower, Ramsons, 2023 Poppy (175 matching cases; no Umbrellaleaf-tagged cases found in this subtree).
> - GitHub: folio-org/ui-invoice, folio-org/mod-invoice, folio-org/mod-invoice-storage (4 files read in this run).
> - Jira: FOLIO component "Invoices" and fallback project scans (0 Done stories, 0 Done bugs returned in this run).
> Strings marked [confirmed] appear in both GitHub source and TestRail signals.
> Strings marked [from source] come from GitHub source only.
> Strings marked [from cases] come from TestRail case corpus.

---

## What is Invoices

The Invoices app manages payments and credits for materials acquired by the library. An invoice records what is owed to a vendor, contains invoice lines (individual items being paid), and goes through an Approve → Pay workflow that drives Finance transactions.

Invoices behavior is tightly integrated with Orders and Finance. Approval and payment actions create and transition Finance transactions, update budget balances, and update linked POL payment status.

---

## Key Terms

| Term | Definition |
|---|---|
| Invoice | The header record representing a payable (or credit) document for a vendor. |
| Invoice line | A payable line item, often linked to a POL, with fund distribution and optional adjustments. |
| Voucher | Payment-request document generated on approval and used in export/accounting flows. |
| Pending payment | Finance transaction type created during Approve, before payment is finalized. |
| Payment transaction | Finance transaction type created during Pay, moving cost into Expended. |
| Lock total | Control requiring calculated invoice total to match a user-entered locked amount before Approve. |
| Release encumbrance | Option on line/payment flow controlling whether encumbrance releases on Approve vs Pay. |

---

## Invoice Lifecycle (Status)

```
Open / Reviewed → Approved → Paid
Open / Reviewed → Cancelled
Paid → Cancelled (only with special capability)
```

| Status | Description |
|---|---|
| **Open** | Default status on creation; editable |
| **Reviewed** | Optionally set before approval; still editable |
| **Approved** | Approved for payment; creates Pending payment transactions in Finance; editing is restricted |
| **Paid** | Payment confirmed; Payment transactions created in Finance; encumbrances released |
| **Cancelled** | Invoice voided; all transactions reversed |

---

## Record Hierarchy / Architecture

Invoices
- Invoice list and search
  - Invoice header
    - Invoice lines
      - Fund distributions
      - Line adjustments
    - Invoice-level adjustments
    - Voucher information
- Related integrations
  - Orders (POL/PO payment status)
  - Finance (pending payment, payment, credit/reversal)

---

## Invoice Header Fields

### Required fields
- **Invoice date** — vendor invoice date
- **Status** — Open (default) or Reviewed; can approve/pay from either
- **Batch group** — groups invoices for voucher export

### Key header fields
- **Vendor invoice number** — must be unique per vendor + date combination (duplicate check on save)
- **Vendor** — must be an active vendor organization; non-vendor org can be selected but Approve will fail
- **Fiscal year** — defaults to current FY; only editable by users with the `Invoice: Pay invoices in a different fiscal year` capability
- **Acquisition units** — controls access same as Orders/Finance
- **Payment due** — due date for payment
- **Lock total / Lock total amount** — when Lock total is checked, all invoice lines + adjustments must equal the locked amount before Approve is allowed
- **Export to accounting** — sends voucher to external financial system
- **Payment method** — Cash, Credit card, EFT, Deposit account, Physical check, Bank draft, Internal transfer, Other

### Calculated totals (system-generated, read-only)
- **Sub-total** — sum of all invoice line sub-totals
- **Total adjustments** — sum of all adjustments (invoice-level + line-level), excluding "Separate from" adjustments
- **Calculated total amount** — Sub-total + Total adjustments; if negative → credit transaction

---

## Invoice Lines

Each invoice line represents one item being paid. Lines are linked to POLs.

### Invoice line key fields
- **Description** — what is being paid for
- **Invoice line number** — auto-generated
- **Sub-total** — cost of this line before adjustments
- **Quantity** — number of units
- **Comment** — internal note
- **Fund distribution** — which fund(s) pay for this line and in what amount/percentage
- **Expense class** — sub-category within a fund
- **Linked POL** — purchase order line this invoice line is paying for (optional but common)
- **Adjustments** — line-level adjustments (tax, shipping, etc.)
- **Accounting code** — from vendor record, required if Export to accounting is on
- **Release encumbrance** — checkbox; when checked, the encumbrance on the linked POL is released when the invoice is approved (vs. when it's paid)

### Linking an invoice line to a POL
- User clicks "Add fund distribution from POL" or links via POL number
- Fund distribution from the POL is automatically pre-filled on the invoice line
- Linking updates the POL's Payment status when the invoice is approved/paid

---

## Adjustments

Adjustments are additional charges on top of the material cost (e.g. shipping, tax). Can be at invoice level or invoice line level.

### Adjustment fields
- **Description** — required
- **Value + Type** — amount (or percentage) of the adjustment; negative value = credit
- **Pro rate** — how the adjustment is distributed across invoice lines:
  - **By line** — equal share per line regardless of amount or quantity
  - **By amount** — proportional to each line's subtotal
  - **By quantity** — proportional to each line's quantity
  - **Not prorated** — applied at invoice level; requires specifying a fund
- **Relation to total**:
  - **In addition to** — added on top of subtotal; increases total
  - **Included in** — already bundled in subtotal; reduces material cost component
  - **Separate from** — NOT included in calculated total; reported but not paid via this invoice
- **Export to accounting** — include in voucher export

### Preset adjustments
Configured in Settings → Invoices → Adjustments. Can be marked "Always show" to appear on every invoice automatically.

---

## Approve Flow

### What triggers Approve
User action: Actions → Approve

### What Approve requires
- Invoice status is Open or Reviewed
- Vendor is an active vendor organization (not just any org)
- If Lock total is enabled: sum of lines + adjustments must equal lock total amount
- Budget must have sufficient funds (if Restrict expenditures is on the ledger)

### What happens on Approve
1. Invoice status → **Approved**
2. **Pending payment** transaction created in Finance for each fund distribution on each invoice line and invoice-level not-prorated adjustment
3. Budget **Awaiting payment** increases; **Encumbered** decreases proportionally (if linked to POL)
4. **Approval date** set to today's date
5. **Approved by** field populated with approving user's name
6. A **Voucher** is generated (for accounting export purposes)
7. POL **Payment status** updates to **Awaiting Payment** (for linked lines)

---

## Pay Flow

### What triggers Pay
User action: Actions → Pay

### What happens on Pay
1. Invoice status → **Paid**
2. **Payment** transactions created in Finance for each fund distribution
3. Budget **Expended** increases; **Awaiting payment** decreases
4. Remaining **Encumbrance** on linked POLs is released (unless "Release encumbrance" was already checked at Approve step)
5. POL **Payment status** updates to **Fully Paid** (for fully paid lines) or **Partially Paid**
6. If all POLs on the linked PO are now Fully Received + Fully Paid → PO auto-closes

---

## Cancel Flow

### What triggers Cancel
User action: Actions → Cancel

### What happens on Cancel
- All Finance transactions are **reversed** (credits applied back to budgets)
- Invoice status → **Cancelled**
- POL payment status reverts

### Cancelling a Paid invoice
- Requires the `Invoice: Cancel invoices` capability
- All payment transactions are reversed in Finance

---

## Voucher

A voucher is a payment request document generated when an invoice is Approved.

### Voucher fields
- **Voucher number** — system-generated
- **Voucher date** — date voucher was generated (= approval date)
- **Status** — Awaiting payment / Paid
- **Batch group** — inherited from invoice
- **Disbursement number** — can be entered manually after payment is processed externally
- **Disbursement date** — date external payment was made

### Voucher export
- Actions → Export vouchers → downloads XML or JSON for external financial system
- Export includes all invoices in the selected batch group within the specified date range
- Only invoices with "Export to accounting" checked are included

---

## Duplicate Invoice Detection

When saving a new invoice:
- If vendor + vendor invoice number + invoice date matches an existing invoice → popup warning: "This appears to be a duplicate invoice"
- User can choose to proceed (Submit) or cancel

---

## Finance Integration Summary

| Invoice action | Finance transaction created | Budget impact |
|---|---|---|
| Approve | Pending payment | Awaiting payment ↑, Encumbered ↓ |
| Pay | Payment | Expended ↑, Awaiting payment ↓ |
| Cancel (Approved) | Reversal of pending payment | Awaiting payment ↓ |
| Cancel (Paid) | Credit | Expended ↓ |
| Negative total (credit invoice) | Credit | Available ↑ |

---

## Main Sections / UI Structure

### Panes
- Invoices [from source]
- Invoice details [from source]
- Voucher information [from source]
- Invoice line details [from source]

### Accordions
- Adjustments [from source]
- Voucher lines [from source]

### Key Navigation Paths
- Apps > Invoices
- Invoices > Actions > Approve
- Invoices > Actions > Pay
- Invoices > Actions > Cancel
- Invoices > Actions > Export vouchers
- Settings > Invoices > Adjustments
- Settings > Invoices > Vouchers
- Settings > Invoices > Approvals

---

## Exact UI Texts

> Use these verbatim in expected results. Never paraphrase.

### Toast Messages

| Event | Toast text | Source |
|---|---|---|
| Approve success | Invoice has been approved successfully | [from source] |
| Pay success | Invoice has been paid successfully | [from source] |
| Approve and pay success | Invoice has been approved and paid successfully | [from source] |
| Save duplicate warning | This appears to be a duplicate invoice | [confirmed] |
| Voucher save success | Voucher has been successfully saved | [from source] |
| Manual export error | Vouchers were not exported | [from source] |
| Accounting code validation | Invoice can not be approved (paid), because the identified vendor must have an accounting code for this invoice to be exported to accounting | [from source] |

### Modal / Dialog Titles

| Modal | Trigger | Source |
|---|---|---|
| Approve invoice | Actions > Approve | [confirmed] |
| Pay invoice | Actions > Pay | [confirmed] |
| Cancel invoice | Actions > Cancel | [from cases] |
| Approve & pay invoice | Actions > Approve & pay | [confirmed] |
| Save invoice | Duplicate detection on save | [confirmed] |
| Run manual export | Settings voucher export action | [from cases] |
| Select order lines | Add invoice line from PO lines | [from cases] |

### Button Labels (key actions)

Actions, Submit, Save and close, Save, Cancel, Continue, Add adjustment, Add fund distribution, Run manual export, Confirm, Delete, View voucher.

### Error / Warning Messages

| Condition | Message text | Source |
|---|---|---|
| Approve failed | Invoice was not approved | [from source] |
| Pay failed | Invoice was not paid | [from source] |
| Approve/pay failed | Invoice was not approved/paid | [from source] |
| Invoice load failure | Failed to load invoice data | [from source] |
| Budget restriction | One or more Fund distributions on this invoice can not be paid, because there is not enough money in <b>{fundCodes}</b>. | [from source] |
| Missing fund distribution | At least one fund distribution should present for every associated invoice line | [from source] |
| Duplicate detection warning | This appears to be a duplicate invoice | [confirmed] |

---

## Status Values

### Invoice workflow status

Open, Reviewed, Approved, Paid, Cancelled.

### Voucher export status

Pending, Generated, Uploaded, Error.

### POL payment status (integration)

Awaiting Payment, Fully Paid, Partially Paid.

---

## Capability Sets (Eureka)

| Action | Capability Set |
|---|---|
| View invoices | `Data - UI-Invoice Invoice - View` |
| Create invoices | `Data - UI-Invoice Invoice - Create` |
| Edit invoices | `Data - UI-Invoice Invoice - Edit` |
| Delete invoices | `Data - UI-Invoice Invoice - Delete` |
| Approve invoices | `Procedural - UI-Invoice Invoice Approve - Execute` |
| Pay invoices | `Procedural - UI-Invoice Invoice Pay - Execute` |
| Cancel invoices | `Procedural - UI-Invoice Invoice Cancel - Execute` |
| Pay in different fiscal year | `Procedural - UI-Invoice Invoice Pay-Different-Fy - Execute` |
| Export vouchers | `Procedural - UI-Invoice Voucher Export - Execute` |
| Download batch file | `Procedural - UI-Invoice BatchVoucher - Execute` |
| Edit batch export credentials | `Data - UI-Invoice Batchvoucher Exportconfigs Credentials - Edit` |
| Assign acquisition units | `Procedural - UI-Invoice Acq Unit Assignment - Execute` |
| Manage acquisition units | `Data - UI-Invoice Acq Unit Assignment - Manage` |
| Export search results | `Procedural - UI-Invoice Export CSV - Execute` |

---

## Common Verification Patterns

### Approve creates pending payment

```
Action:   Click Actions > Approve and confirm in Approve invoice modal.
Expected: Invoice status changes to Approved; approval metadata is populated; pending payment transactions are created in Finance.
```

### Pay creates payment and relieves awaiting payment

```
Action:   Click Actions > Pay and confirm in Pay invoice modal.
Expected: Invoice status changes to Paid; payment transactions are created; budget Expended increases and Awaiting payment decreases.
```

### Duplicate detection on save

```
Action:   Save an invoice with existing vendor + vendor invoice number + invoice date combination.
Expected: Save invoice dialog appears with warning This appears to be a duplicate invoice; user can submit or cancel.
```

---

## ECS / Multi-Tenant Notes

Invoices subtree for this run includes ECS coverage (7 ECS-enabled cases), including Consortium (Invoices) section content. Primary behavior remains same as non-ECS invoice lifecycle, with additional tenant/capability gating in consortial contexts.

---

## Key Business Rules for Test Cases

1. Default invoice workflow status on creation is Open and invoice is editable after save. (cases + source)
2. Approval is allowed from both Open and Reviewed statuses; Reviewed is optional, not mandatory. (cases + source)
3. Vendor must be a valid active vendor organization for successful approval. (cases)
4. Duplicate detection is enforced on vendor + vendor invoice number + invoice date and requires explicit user decision to proceed. (cases + source)
5. Lock total prevents approval when calculated totals do not match lock total amount. (cases)
6. Approve creates pending payment transactions and moves budget amounts into Awaiting payment. (cases + source)
7. Pay creates payment transactions and moves budget amounts into Expended while decreasing Awaiting payment. (cases + source)
8. Cancel reverses prior finance effect (pending payment or payment) according to invoice state, and paid-invoice cancel requires cancel capability. (cases)
9. Negative calculated total posts credit behavior in Finance (increasing available budget). (cases)
10. Separate from adjustments are not included in invoice calculated total and not paid via invoice total flow. (cases)
11. Not prorated adjustments require explicit fund distribution at adjustment level. (cases)
12. Release encumbrance option controls whether release occurs at Approve instead of Pay for linked lines. (cases)
13. Voucher is generated at approval and carries voucher metadata used in export/accounting workflows. (cases + source)
14. Export to accounting controls voucher inclusion in batch export. (cases + source)
15. Accounting code is required for approval/payment when export-to-accounting behavior is active. (cases + source)
16. POL payment status progression is driven by invoice transitions (Awaiting Payment at Approve, Fully/Partially Paid at Pay). (cases)

---

## Known Gaps / Items to Verify

- [ ] Umbrellaleaf-tagged cases are not present in this subtree (release option exists but no matching cases in this run).
- [ ] Jira extraction for Invoices returned zero Done stories/bugs for all attempted filters; business-rule dating is therefore TestRail/GitHub-led in this refresh.
- [ ] Some extracted capability strings in old cases include HTML artifacts (for example trailing </li>); use normalized values from table above when writing new cases.
- [ ] Consortium (Invoices) ECS signals exist but are sparse (7 ECS-enabled cases); verify tenant-specific edge behavior in environment before relying on narrow ECS assumptions.
