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
> ✅ Toasts, dialogs and error messages below were **confirmed verbatim against `folio-org/ui-invoice/translations/ui-invoice/en_US.json` on 2026-07-21** — every previously `[from source]` string matched the translation file exactly. `<b>…</b>` marks bold segments; `{placeholders}` interpolate at runtime.

### Toast Messages

| Event | Toast text | Source |
|---|---|---|
| Approve success | Invoice has been approved successfully | [confirmed] |
| Pay success | Invoice has been paid successfully | [confirmed] |
| Approve and pay success | Invoice has been approved and paid successfully | [confirmed] |
| Cancel success | Invoice has been cancelled successfully | [confirmed] |
| Invoice created | Invoice has been created | [confirmed] |
| Invoice saved | Invoice has been saved | [confirmed] |
| Invoice deleted | Invoice has been deleted | [confirmed] |
| Invoice duplicated | The invoice has been duplicated successfully | [confirmed] |
| Save duplicate warning | This appears to be a duplicate invoice | [confirmed] |
| Invoice line saved | Invoice line has been saved | [confirmed — C343209 + source] |
| Invoice line deleted | Invoice line has been deleted | [confirmed] |
| Invoice line relinked | Invoice line has been linked to POL {poLineNumber} | [confirmed] |
| Voucher save success | Voucher has been successfully saved | [confirmed] |
| Manual export started | Voucher export has been started successfully | [confirmed] |
| Manual export error | Vouchers were not exported | [confirmed] |
| Export results CSV started | Export has been started successfully | [confirmed] |

### Approve / Pay failure messages (negative-case gold — all [confirmed])

| Condition | Message text |
|---|---|
| Vendor has no accounting code | `Invoice can not be approved (paid), because the identified vendor must have an accounting code for this invoice to be exported to accounting` |
| Fund has no current budget | `Invoice cannot be approved because Fund <b>{fundCode}</b> has no current budget.` |
| Fund has no budget for FY | `Invoice cannot be approved because Fund <b>{fundCode}</b> has no current budget for fiscal year <b>{fiscalYear}</b>.` |
| Not enough money in fund | `One or more Fund distributions on this invoice can not be paid, because there is not enough money in <b>{fundCodes}</b>.` |
| Inactive expense class | `Invoice can not be <b>Approved</b> because expense class <b>{expenseClass}</b> is inactive.` |
| Fund distribution not 100% | `Fund distributions summary should be 100 % or equal to subtotal for every associated invoice lines` |
| Missing fund distribution | `At least one fund distribution should present for every associated invoice line` |
| Related order still Pending | `Invoice can not be approved. One or more of the related orders has a workflow status of "Pending". If desired, please open the related orders before approving this invoice.` |
| Vendor is inactive | `Vendor is inactive. Invoice cannot be approved or paid.` |
| Lock total mismatch | `Invoice cannot be approved. The Lock total amount of the invoice does not match the Calculated total amount of its invoice lines and adjustments.` |
| Multiple fiscal years | `Invoice cannot be approved because the funds used belong to multiple fiscal years` |
| Not acq-unit member | `Operation is not permitted because user is not a member of the specified acquisition unit` |
| Budget restricted encumbrance | `Fund distribution amount exceeds the allowable encumbrance amount in the <b>{fundCode}</b> fund.` |

### Modal / Dialog Titles

| Modal | Trigger | Source |
|---|---|---|
| Approve invoice | Actions > Approve | [confirmed] |
| Pay invoice | Actions > Pay | [confirmed] |
| Cancel invoice | Actions > Cancel | [from cases] |
| Approve & pay invoice | Actions > Approve & pay | [confirmed] |
| Save invoice | Duplicate detection on save | [confirmed] |
| Run manual export | Settings voucher export action | [from cases] |
| Select order lines | Add invoice line from PO lines — via `Add Line from POL` button in "Invoice lines" accordion | [confirmed — C2327] |
| Create vendor invoice line | `Actions > New blank line` in "Invoice lines" accordion (manual invoice line) | [confirmed — C2326, C343209] |
| Currency-mismatch confirmation | POL and invoice currency differ when adding line from POL | [confirmed — C2327] |

### Confirmation dialog messages (confirmed — GitHub translations)

| Dialog | Heading / message |
|---|---|
| Approve | `Approve invoice` / `Are you sure you want to approve invoice?` |
| Pay | `Pay invoice` / `Are you sure you want to pay invoice?` |
| Approve & pay | `Approve & pay invoice` / `Are you sure you want to approve and pay invoice?` |
| Cancel invoice | `Cancel invoice` / `Are you sure you want to cancel this invoice? Any related transactions against funds will be voided.` |
| Delete invoice | `Delete {vendorInvoiceNo}?` / `Are you sure you want to delete this invoice and all of its invoice lines? This will also delete any attached documents.` |
| Duplicate invoice | `Duplicate invoice?` / `Are you sure you want to create a duplicate of this invoice and all of its invoice lines?` |
| Add line from POL — currency differs | `Confirmation` / `You are adding one or more purchase order lines that are in a different currency than the one identified on this invoice. If you would still like to add these please click confirm. ...` |
| Add line from POL — vendor differs | `Confirmation` / `You are adding one or more purchase order lines that reference a different vendor than the one identified on this invoice. ...` |
| Update order status (cross-FY pay with release encumbrance) | `Update order status` / `You are processing this invoice against a previous fiscal year and "release encumbrance" equals true for one or more invoice lines. One or more related orders has a type of One-time. Please indicate how the payment status of these order lines should be updated?` — exact radio options: **No Change** (selected by default), Awaiting Payment, Partially Paid, Fully Paid, Cancelled. [from cases (C700852)] Selecting "No Change" leaves the linked POL's Payment status untouched even though the invoice itself completes Approve/Pay. |
| Duplicate invoice? | Actions > Duplicate on an invoice detail pane → `Duplicate` / `Cancel` buttons | [from cases (C514954, C514958, C1332438)] |

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

## Duplicate Invoice (Actions > Duplicate)

> Previously only cited via its toast string; this round confirms exact field-carry-over/reset behavior. [C514954, C514958, C1332438]

- Actions > Duplicate → confirmation modal (Duplicate/Cancel) → new invoice created with the **same vendor invoice number** and copies of all invoice lines/adjustments.
- Regardless of the SOURCE invoice's status (Open, Reviewed, Approved, Paid, Cancelled), the **duplicate is always created in "Open" status**, and all its invoice lines are duplicated as "Open" too.
- **Fiscal year is NOT copied**: if the current fiscal year (matching alpha-code family) cannot be resolved, it's left blank; otherwise the duplicate is auto-set to the CURRENT fiscal year, never the original invoice's (possibly past) fiscal year.
- Record metadata resets on the duplicate: "Resource created" = now, "Source" = the user performing the duplicate (not the original creator).
- A **Cancellation note** on a Cancelled source invoice is explicitly dropped — the field is not displayed on the duplicate AND is absent entirely from the `cancellationNote` field in the API response for the new invoice (confirmed via DevTools network inspection). [C1332438]
- Duplicated invoice lines keep their POL links and adjustments; the "Current encumbrance" hyperlink on a duplicated line references the NEW invoice's (current) fiscal year budget, not the original's.
- Duplicate is permission-gated (separate capability check) — a user lacking the relevant Invoice create/view permission cannot duplicate at all (Actions menu omits the option).

---

## Version History (Invoice / Invoice Line)

> Undocumented prior to this round. [C613165, C877080, C663321]

- A clock ("Version history") icon appears top-right of the invoice detail pane (and separately for invoice lines). Clicking opens a 4th pane listing every saved version as a card, **most recent first**, each titled with a date/time in `MM/DD/YYYY, HH:MM AM` format.
- While the Version history pane is open: the underlying invoice's "Actions" button is hidden, and the Version-history/Tags icons on the invoice pane itself become disabled (can't stack panes).
- Selecting a card highlights every field that changed IN that version, in **yellow**, directly on the invoice detail pane behind it.
- The oldest card is labeled "Original version" (no changed-field list); the newest is labeled "Current version" plus a "Changed" section listing every changed field name.
- If a referenced record (e.g. the vendor Organization) is later deleted, older versions still resolve it as "Record deleted" in the Vendor details accordion, and re-opening the live invoice shows an error toast `Failed to load invoice data`.
- Adjustment-related field changes (Total adjustments, Calculated total amount, Description, Value, Pro rate, Relation to total) and currency/exchange-rate changes are tracked and highlighted like any other field.
- Approving an invoice creates its own version entry with Status, Approval date, Approved by, Voucher number, and Exchange rate all listed as changed.

---

## "Save & Keep Editing" Button (Create Invoice / Create Invoice Line)

> New UI mechanic, not previously documented. [C663268]

- Both the standalone "Create vendor invoice" screen and "Create vendor invoice line" screen show three buttons in order: **Cancel** (always active), **Save & keep editing** (disabled until at least one field is filled), **Save & close** (same enable condition, styled as the primary blue button).
- Clicking "Save & keep editing" with missing mandatory fields shows the same inline red "Required!" validation as Save & close, without closing the screen.
- On a successful "Save & keep editing", a success toast appears, the screen stays open, and both Save buttons return to a disabled state until further edits are made.
- Cancelling with unsaved changes prompts a "Close without saving" confirmation; declining preserves the create screen, confirming discards the in-progress edits.
- **"Save & keep editing" is NOT displayed** when creating an invoice via the Orders app's Actions > "New invoice" flow (order-based invoice creation) — only the two standalone create-from-scratch flows offer it.

---

## Batch Group Credentials — Permission Tiers (Settings > Invoices)

> [C422074] plus adjacent cases in the same TestRail cluster (422071, 422073) confirm three distinct permission tiers.

- Settings > Invoices pane layout: **General** section (Approvals, Adjustments) + **Vouchers** section (Batch groups, Batch group configuration, Voucher number).
- Three permission tiers gate "Batch group configuration" specifically:
  1. `Settings (Invoices): View settings` — can view the settings pane but NOT batch group credentials at all.
  2. `Settings (Invoices): Batch group usernames and passwords: view` — can view+edit general invoice settings, but batch group username/password fields are visible-only (not editable).
  3. `Settings (Invoices): Batch group usernames and passwords: view and edit` — full edit access to Batch group configuration fields (Batch group, Location type, Upload location, Port, Directory, Format, Username, Password) plus an active "Show credentials" button that reveals the plaintext Username/Password.
- This is a deliberately separate, more restrictive permission from general Invoice-settings access — a useful negative-case axis (view-only vs edit-without-credentials vs full-credentials).

---

## Adjustment Fund Distribution — Strict Pro-Rate Coupling

> Refines/extends Key Business Rule 11. [C825250, C889747]

- An adjustment's **fund distribution is only meaningful/visible when "Pro rate" = "Not prorated"**. The moment "Pro rate" is switched to ANY other value (By line / By amount / By quantity), the adjustment's fund distribution is immediately hidden from the UI and stripped from the saved record — the API payload's `adjustments[].fundDistributions` becomes an empty array `[]`, confirmed on both PUT (editing an existing adjustment) and POST (creating a new one).
- This holds even if the Fund ID dropdown was left blank — switching Pro rate away from "Not prorated" clears it either way, and switching back to "Not prorated" does not restore a previously-cleared fund selection (user must re-pick the fund).
- Test design implication: any adjustment case that toggles Pro rate should assert both the UI (fund-distribution controls disappear) and the API response body (`fundDistributions: []`) for full coverage.

---

## Exchange Rate — Zero-Decimal Currency Display (JPY)

> [C1322894]

- When the tenant's primary/target currency is JPY (a zero-decimal currency), the UI's "Calculated total amount (Exchanged)" field displays as a whole number with no decimal places (e.g. `¥16717`), matching real-world yen formatting.
- However, the underlying `GET /finance/calculate-exchange` API call always returns its `amount` with an explicit `.0` decimal suffix regardless of target currency (e.g. `16717.0`) — the zero-decimal formatting is a UI-layer presentation choice only, not an API contract difference. This holds for both provider-calculated rates and manually-entered "Use set exchange rate" values.

---

## Fiscal Year Auto-Resolution Rules

> [C396373, C700852]

- Leaving "Fiscal year" blank when creating an invoice is allowed; on save, FOLIO auto-populates it with the CURRENT fiscal year whose alpha-code family matches the invoice date — the user never sees "undefined" persist.
- Once a Fiscal year value exists on a saved invoice (even an auto-populated one), the Edit page's "Fiscal year" dropdown **no longer offers a blank/undefined option** — a fiscal year must be explicitly (re)selected going forward; there's no way back to "undefined" once set.
- Approving/paying an invoice against a FISCAL YEAR THAT IS NOT the ledger's current one correctly posts Pending payment / Payment transactions against the ORIGINAL (past) fiscal year's budget, not the currently active rolled-over budget — verified by checking the resulting transaction's own "Fiscal year" field and the past-FY budget's transaction list directly.
- The "Update order status" modal's per-line "Status" (Released/Unreleased) on the resulting Encumbrance transaction can differ per invoice line depending on whether that line's PO line payment status was actually updated ("No Change" selection leaves an Unreleased/stale linkage on that specific line while other, fully-processed lines correctly show "Released").

---

## ECS / Multi-Tenant Notes

Invoices subtree for this run includes ECS coverage (7 ECS-enabled cases), including Consortium (Invoices) section content. Primary behavior remains same as non-ECS invoice lifecycle, with additional tenant/capability gating in consortial contexts.

**Canonical mechanic documented in orders.md** ("Cross-Tenant Location Lookup via 'Affiliation' Dropdown") — Invoices reuses the identical UI, but nested one level deeper: inside an invoice's `Invoice lines` accordion, `Actions > Add line from POL` opens a `Select order lines` modal that has its own `Location` facet with the same `Location look-up` > `Select locations` > `Affiliation` dropdown pattern (confirmed C471510).

- **Positive flow** (confirmed C471510): with the Central-tenant prerequisite setting on (`Settings > Consortium manager > Central ordering`), a Central-tenant user in `Add line from POL`'s Location facet can select a Member tenant in the `Affiliation` dropdown (default: Central), see only that tenant's own locations, check one, and the corresponding PO line (created against a Member tenant's location) is returned in the `Select order lines` modal's results — letting a Central-tenant invoice pull in a line ordered under a Member tenant's location.
- The "Location" facet's "Affiliation" dropdown (used to search POLs by location across tenants when adding an invoice line "from POL") is **Central-tenant-only** — from a Member tenant, the same "Add line from POL" > Location facet > location look-up modal does NOT show an Affiliation dropdown at all; only the Central tenant's own local locations are searchable directly. [C471512]
- Per orders.md's fuller mechanic (also true here, not yet separately case-confirmed in Invoices but confirmed identically in Orders/Receiving): the dropdown, when present, lists ALL consortium tenants regardless of the user's own assigned affiliations.
- Paying an invoice whose linked POL was created in a Member tenant, performed directly from that Member tenant (not Central), follows the exact same Pay flow, encumbrance-release, and voucher-status transitions as a non-ECS invoice — no special cross-tenant Pay restriction exists once the user has Member-tenant Invoice/Finance/Orders capabilities. [C610245]

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
17. Duplicating an invoice always resets status to Open and fiscal year to current/blank, and never carries over the original invoice's status, cancellation note, or fiscal year — only vendor invoice number, lines, and adjustments transfer. (cases)
18. Version history tracks every save on both Invoice and Invoice line, highlighting changed fields in yellow and correctly labeling the oldest/newest cards as Original/Current version. (cases)
19. "Save & keep editing" is available on both standalone create screens (invoice, invoice line) but not on the order-triggered "New invoice" flow. (cases)
20. Batch group username/password access is gated by a permission tier strictly separate from general Invoice-settings view/edit access. (cases)
21. An adjustment's fund distribution is only retained while Pro rate = Not prorated; switching to any other Pro rate value strips fund distribution from both UI and the persisted API record. (cases)
22. Zero-decimal currencies (e.g. JPY) are displayed without decimals in Calculated total (Exchanged) even though the underlying exchange-calculation API always returns an explicit decimal value. (cases)
23. An invoice's fiscal year auto-resolves to the current FY if left blank at creation, and cannot be reverted to blank once set. (cases)
24. Approve/Pay transactions always post against the fiscal year the invoice/PO is actually scoped to, even when that FY is no longer the ledger's current one after a rollover. (cases)
25. The "Add line from POL" modal's `Location` facet `Affiliation` dropdown is the same canonical cross-tenant lookup mechanic as Orders/Receiving — Central-tenant-only, positive flow confirmed C471510. (cases — C471510, C471512)

---

## Authoring style (measured 2026-07-23)

Invoices is strongly **`Functional` (~95%)**, median ~8 steps, `User Journey` ~1% (`No`) — an acquisitions-family shape like Orders/Finance. Cases build the money context in **Preconditions** with exact values (Fund + Budget in an active Fiscal Year, an Open PO/POL to link, a Vendor/Organization, batch group, currency) and then walk the approve/pay/cancel/duplicate flow, **verifying the Finance side at its real destination** — the Pending payment / Payment / Credit transactions and the budget's Encumbered/Expended/Available values column-by-column, not just an invoice toast. Adjustment-calculation cases spell out the exact resulting `Total adjustments` / `Calculated total amount` numbers. Match this: exact monetary preconditions, `Functional` type, one coherent flow per case, Finance-transaction verification.

---

## Known Gaps / Items to Verify

- [ ] Umbrellaleaf-tagged cases are not present in this subtree (release option exists but no matching cases in this run).
- [ ] Jira extraction for Invoices returned zero Done stories/bugs for all attempted filters; business-rule dating is therefore TestRail/GitHub-led in this refresh.
- [ ] Some extracted capability strings in old cases include HTML artifacts (for example trailing </li>); use normalized values from table above when writing new cases.
- [x] ~~Consortium (Invoices) ECS signals exist but are sparse (7 ECS-enabled cases); verify tenant-specific edge behavior~~ — 2026-07-22 enrichment round confirmed the positive cross-tenant-lookup flow (C471510) alongside the already-documented negative/gating case (C471512); see the expanded ECS section above. The "all tenants regardless of affiliation" nuance is confirmed in Orders/Receiving but not yet separately re-verified with an Invoices-specific case — low priority since the underlying modal component is shared.
- [ ] Whether a duplicated invoice's fiscal year can ever resolve to something OTHER than "current FY or blank" (e.g. if invoice date itself is edited pre-save) was not tested in the sampled cases.

> N≥10 audit round (2026-07-22): 14 cases read (C514954, C514958, C1332438, C613165, C663268, C422074, C471512, C610245, C396373, C700852, C1322894, C825250, C889747, C934328). Added entirely new sections: Duplicate Invoice (field carry-over/reset rules), Version History (Invoice/Invoice line), "Save & keep editing" button mechanic, Batch group credentials permission tiers, strict Pro-rate↔fund-distribution coupling for adjustments, JPY zero-decimal display vs API contract, and fiscal-year auto-resolution/no-revert-to-blank rules. Added 8 new Key Business Rules (17-24) and enriched the "Update order status" modal row with its exact radio-option list and the Central-only ECS Affiliation-dropdown scoping.
