# FOLIO Orders App — Business Logic Context

> Generated/refreshed by the `build-app-context` skill on 2026-06-17.
> Sources: TestRail section subtree rooted at 105 (Orders): sections 105, 106, 122, 123, 11057, 17146, 23016, 29148, 39358
>          TestRail coverage: 708 cases total; 326 in focus releases (Umbrellaleaf, Trillium, Sunflower, Ramsons)
>          GitHub: folio-org/ui-orders, folio-org/mod-orders, docs at https://docs.folio.org/docs/acquisitions/orders/ and https://folio-org.atlassian.net/wiki/spaces/FOLIOtips/pages/5669035/Orders
>          Jira: Queries attempted for component/project prefixes (Orders, UIOR, MODORDERS) returned 0 done stories/bugs with current token scope
> Strings marked [confirmed] appear in both source materials and case corpus.
> Strings marked [from source] come from repo/docs references and must be verified in target env before strict assertion.
> Strings marked [from cases] come from TestRail patterns and weighted usage.

---

## What is Orders

The Orders app manages the full purchase order lifecycle: creating orders, opening them to vendors, receiving materials, and linking to Finance (encumbrances) and Inventory (instances, holdings, items).

---

## Record Hierarchy

```
Purchase Order (PO)
  └── Purchase Order Line (POL)  — one or more per PO
        └── Piece  — individual receiving units (in Receiving app)
```

---

## Purchase Order (PO)

### Order types
| Type | Description |
|---|---|
| **One-time** | Single purchase; order closes when fully received and paid |
| **Ongoing** | Recurring (e.g. subscription); does not auto-close |
| **Ongoing subscription** | Subscription with renewal dates and review periods |

### Workflow status (order lifecycle)
| Status | Description |
|---|---|
| **Pending** | Created but not yet sent to vendor; can be edited freely |
| **Open** | Sent to vendor; encumbrance created in Finance; limited editing |
| **Closed** | Fully received + paid, or manually closed; no new activity |

**Pending → Open**: triggered by user action (Actions → Open) or automatically on import
**Open → Closed**: automatically when all POLs are fully received + paid; or manually (Actions → Close)
**Closed → Open**: manually via Actions → Reopen
**Open → Pending**: manually via Actions → Unopen (releases encumbrances, allows full editing again)

### What happens when a PO is Opened
1. **Encumbrance** created in Finance for each POL fund distribution
2. **Date ordered** set to today
3. **Approval date** set to today (if not already approved)
4. **Inventory records created** based on POL "Create inventory" setting:
   - Attempts to match to existing Instance via Product ID
   - If match found: creates Holdings + Item on existing Instance
   - If no match: creates new Instance + Holdings + Item
5. **POL fields become restricted** (certain fields no longer editable without unopen)

### What happens when a PO is Closed
- Reason for closure is recorded (Complete, Cancelled, or custom reason)
- Encumbrances are released back to the budget
- No new POLs can be added

### Fields editable while Open (selected)
PO level: Vendor, Acquisition unit, Assigned to, Bill to, Ship to, Tags, Notes
POL level: Receiving note, Receipt status, Payment status, Fund distribution, Unit price, Quantity, Vendor reference number, URL, etc.
**NOT editable while Open** (require Unopen): Order type, Title, Acquisition method, Order format, Product ID

### Approval
Orders can require approval before opening (configurable in Settings → Orders). If approval is required:
- Order must be approved first (Actions → Approve) before it can be opened
- "Approved" flag visible on PO

---

## Purchase Order Line (POL)

### Order format (determines required fields)
| Format | Description |
|---|---|
| **Physical resource** | Physical material; requires physical details |
| **Electronic resource** | E-resource; requires e-resource details |
| **P/E mix** | Both physical and electronic |
| **Other** | Other format |

### Key POL sections
- **Item details**: Title, Contributor, Product ID (ISBN, ISSN, etc.), Publication date, Publisher, Edition
- **POL details**: Acquisition method, Order format, Receipt date, Receipt status, Payment status, Rush, Collection, Tags
- **Vendor**: Vendor account, Vendor reference number/type
- **Cost details**: Unit price, Quantity ordered, Currency, Discount, Additional cost, Total estimated price
- **Fund distribution**: Which fund(s) cover this line and in what percentage/amount; shows **Current encumbrance** value with hyperlink to the Finance transaction
- **Location**: Holding location(s) for the ordered item(s)
- **Physical resource details**: Material type, Create inventory setting, Material supplier
- **E-resources details**: Access provider, Activation status, Trial, URL
- **Donor information**: donors linked via "Add donors" modal

### Inventory interaction ("Create inventory" setting on POL)
| Setting | What is created on Open |
|---|---|
| Instance, holdings, item | Full hierarchy created |
| Instance, holdings | Instance + Holdings only |
| Instance only | Instance only |
| None | No Inventory records created |

### POL matching to Instance on Open
1. If a specific Instance was manually linked: uses that Instance (unless bib data was changed)
2. If bib data was changed after linking: creates new Instance
3. If no Instance linked: matches on Product ID (ISBN/ISSN) to find existing Instance
4. If multiple matches on Product ID: uses first match returned by Inventory API
5. If no match: creates new Instance (source = FOLIO)

### POL status fields
**Receipt status**: Pending / Awaiting Receipt / Partially Received / Fully Received / Receipt Not Required / Cancelled
**Payment status**: Pending / Awaiting Payment / Partially Paid / Fully Paid / Payment Not Required / Cancelled

### Auto-close logic
PO closes automatically (Reason: Complete) when ALL POLs have:
- Receiving: Fully Received or Receipt Not Required or Cancelled
- Payment: Fully Paid or Payment Not Required or Cancelled

---

## Acquisition Units in Orders

Orders (PO and POL) support Acquisition Units — same behavior as Finance:
- If an Acquisition Unit is assigned to an order, only users in that unit can view/edit it
- Users with "bypass acquisition unit" permission can access all orders
- Visible in search results list: "Acquisition unit" column

---

## Finance Integration

### On Open
- **Encumbrance** created for each POL fund distribution
- Reduces Available balance in the associated budget
- Encumbrance amount = estimated cost of the POL

### On Close / Cancel
- Encumbrances are **released** (funds return to Available)

### On Invoice approval
- **Pending payment** transaction created (linked to POL)
- Encumbrance reduced accordingly

### On Invoice payment
- **Payment** transaction created
- Pending payment resolved

### Restrict encumbrances (on Ledger)
- If enabled: FOLIO checks budget before creating encumbrance on Open; rejects if insufficient
- If disabled: Encumbrance created even if budget is overdrawn (shows overencumbered)

---

## Inventory Integration

### Items created on PO Open
- Item status set to **"On order"** when PO is opened
- Item status changes to **"In process"** when item is received (via Receiving app)
- After receiving and Check in: item status becomes **"Available"**

### Holdings location
- Determined by POL Location field
- If specified location's Holdings doesn't exist: new Holdings created on Open
- If Holdings already exists: item added to existing Holdings

---

## Settings → Orders

Key settings that affect Orders behavior:
- **Opening purchase orders**: require approval before opening (Yes/No)
- **Order number prefix/suffix**: configurable number format
- **PO lines limit**: maximum number of POLs per PO (default: 999)
- **Acquisition methods**: configurable list (e.g. Purchase, Approval, Gift, etc.)
- **Reasons for closure**: configurable list of closure reasons

---

## Search and Filters

### Order search filters
Status (Pending/Open/Closed), Approved, Acquisition unit, Assigned to, Date opened, Order type, Vendor, Tags, Reason for closure, Re-encumber, Subscription, Renewal date, Bill to, Ship to

### Order line search filters
Receipt status, Payment status, Acquisition unit, Acquisition method, Location, Fund code, Order format, Material type, Vendor, Tags, Source, Rush, Access provider, Expected receipt date, Date created/updated

---

## Actions Menu on Orders

| Action | Available when |
|---|---|
| Edit | Pending or Open (limited fields) |
| Open | Pending (with at least 1 POL) |
| Unopen | Open |
| Close | Open |
| Reopen | Closed |
| Approve | Pending (if approval workflow enabled) |
| Duplicate | Any status |
| Delete | Pending only |
| Print | Any status |
| Add PO line | Pending only |
| View/Create invoice | Open or Closed |
| Update encumbrances | Open |

---

## Exact UI Texts (from team test cases — use these verbatim)

### Toast messages — PO
| Event | Toast text |
|---|---|
| PO opened | `The Purchase order - <PO number> has been successfully opened` |
| PO unopened | `The Purchase order - <PO number> has been successfully unopened` |
| PO saved | `The Purchase order - <PO number> has been successfully saved` |
| PO reopened | `The Purchase order - <PO number> has been successfully reopened` |
| PO duplicated | `The purchase order was successfully duplicated` |

### Toast messages — POL
| Event | Toast text |
|---|---|
| POL created | `The purchase order line was successfully created` |
| POL updated | `The purchase order line <POL number> was successfully updated` |
| POL deleted | `The purchase order line was successfully deleted` |

### Toast messages — related flows seen from Orders
| Event | Toast text |
|---|---|
| Export started (CSV) | `Export has been started successfully` |
| Piece saved / deleted / received (Receiving) | `The piece was successfully saved` / `…deleted` / `…received` |
| Invoice approved / paid / cancelled (Invoices) | `Invoice has been approved successfully` / `Invoice has been paid successfully` / `Invoice has been cancelled successfully` |

### Modal titles
| Modal | Trigger |
|---|---|
| `Open - purchase order` | Actions → Open (confirm with "Submit") |
| `Unopen - purchase order - <PO number>` | Actions → Unopen |
| `Close - purchase order` | Actions → Close (Reason for closure dropdown + Submit) |
| `Duplicate order?` | Actions → Duplicate |
| `Delete <name>?` / `Are you sure?` | Delete confirmations |
| `Select instance` | Linking POL to an Instance (Title look-up) |
| `Select locations` / `Select location` | POL Location field |
| `Select user` | Assigned to look-up |
| `Select order lines` | Adding related order lines (e.g. invoice creation) |
| `Confirm move` | Moving a POL to another PO |
| `Export settings` | Actions → Export results (CSV) |
| `Add donors` | Donor information accordion |
| `Update Expense Class` | Fund distribution expense class change |
| `Fiscal year rollover` | Finance rollover (cross-app) |

---

## UI Structure Inventory (panes and accordions)

### Panes
- `Orders` (search results) and `Order lines` (POL search results)
- `Search & filter` — left pane on both search modes
- `Purchase order - <PO number>` — PO detail pane
- `PO Line details - <POL number>` — POL detail pane
- `Encumbrance` — Finance transaction pane (opened from Current encumbrance link)
- `Transactions` — budget transactions list pane (Finance)
- `Version history` — change history pane on PO/POL (clock icon)

### PO detail pane accordions
`PO summary`, `PO lines`, `Ongoing order information` (Ongoing orders only), `Acquisition`, `Vendor`, `Related invoices`, `Users`

### POL detail pane accordions
`Item details`, `PO line details` / `POL details`, `Vendor`, `Cost details`, `Fund distribution`, `Location`, `Physical resource details` / `E-resources details`, `Donor information`, `Routing lists`, `Related invoice lines`, `Purchase order line` (in version history)

---

## Common Verification Patterns (copy these into expected results)

### Encumbrance verification via Current encumbrance link
The standard team pattern for verifying Finance effects from a POL:
```
Action:   Click "Current encumbrance" link in "Fund distribution" accordion on "PO Line details" pane
Expected: - User is redirected to "Finance" app
          - "Encumbrance" pane appears
          - "Source" field contains POL number <POL number>
          - Encumbrance "Amount" = <expected value>
          - Encumbrance "Status" = "Unreleased" (or "Released" after close/unopen/cancel)
          - "Initial encumbrance" = <expected value>
          - "Awaiting payment" = <expected value>
          - "Expended" = <expected value>
```
Encumbrance statuses used in assertions: **Unreleased** (active), **Released** (after Close/Unopen/POL payment status Cancelled).

### Status pair verification on POL after PO state change
After Open/Reopen, assert both statuses on the POL:
```
Expected: - Payment status is changed to "Awaiting Payment"
          - Receipt status is changed to "Awaiting Receipt"
```
After cancelling a POL (Payment status / Receipt status → "Cancelled"), the related encumbrance is Released and "Current encumbrance" shows 0.00.

### Cost change while Open
Editing POL cost while the PO is Open immediately updates the encumbrance:
```
Expected: - Toast message "The purchase order line <POL number> was successfully updated" appears
          - "Current encumbrance" field in "Fund distribution" accordion contains <new value>
```

### Version history
PO and POL keep version history (Version history pane); cases for edit flows may assert that a new version entry appears after save.

---

## Required Capability Sets (Eureka)

| Action | Capability Set |
|---|---|
| View orders | `Data - UI-Orders - View` |
| Create/Edit orders | `Data - UI-Orders - Create`, `Edit` |
| Delete orders | `Data - UI-Orders - Delete` |
| Open/Close/Reopen orders | `Procedural - UI-Orders Open - Execute` |
| Approve orders | `Procedural - UI-Orders Approve - Execute` |
| Manage acquisition units | `Procedural - UI-Orders Acquisition Units Assign - Execute` |
| View order lines | `Data - UI-Orders Order Lines - View` |
| Create/Edit order lines | `Data - UI-Orders Order Lines - Create`, `Edit` |

---

## Key Business Rules for Test Cases

1. **Cannot open PO without at least one POL** — Actions → Open is disabled until a POL is added
2. **Opening creates encumbrance** — Finance budget Available is reduced immediately on Open; verify via the Current encumbrance link pattern
3. **Unopen releases encumbrance** — Available returns to budget; Encumbrance status → Released
4. **Certain fields locked while Open** — Order type, Title, Acquisition method, Order format require Unopen to edit
5. **Auto-close requires all POLs complete** — one partially received POL prevents auto-close
6. **Pending orders can be deleted** — Open and Closed orders cannot be deleted via UI
7. **POL matching uses Product ID** — if no Product ID, a new Instance is always created on Open
8. **Changed bib data on POL triggers new Instance** — even if Instance was manually linked
9. **Item status "On order"** — set when PO is opened; changed to "In process" on receipt
10. **Acquisition units gate access** — same as Finance; user must be in the assigned unit
11. **Approval setting is configurable** — some tenants require approval before opening; others don't
12. **Cannot add POLs to Open order** — must Unopen first to add new POLs
13. **Finance budget restrictions apply** — if Ledger has "Restrict encumbrances" = true, Open fails if budget insufficient
14. **One-time orders auto-close** — when fully received + paid; Ongoing orders do not auto-close
15. **Editing POL cost while Open updates the encumbrance immediately** — Current encumbrance reflects the new value after save
16. **Cancelling a POL releases its encumbrance** — Payment/Receipt status → Cancelled; encumbrance Released; Current encumbrance = 0.00
17. **Reopen restores Awaiting Payment / Awaiting Receipt** on POLs and re-establishes the encumbrance link
18. **Moving a POL between POs uses the "Confirm move" modal** — encumbrance follows the POL
19. **PO/POL keep Version history** — edits produce new version entries viewable in the Version history pane

---

## Known Gaps / Items to Verify

> Verify these in environment before writing strict assertions.

- [ ] Requested TestRail `group_id=1389` maps to OAI-PMH in this tenant, not Orders; Orders context here was built from the Orders subtree rooted at section 105.
- [ ] Jira story/bug distillation for Orders could not be completed because project/component queries returned 0 with current API token visibility.
- [ ] Capability set strings extracted from raw TestRail HTML include noisy legacy/formatting variants; use the curated `Required Capability Sets (Eureka)` table above as the canonical source for new cases.
