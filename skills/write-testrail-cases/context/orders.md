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
Orders can require approval before opening (configurable in Settings → Orders → General → Approvals → "Approval required to open orders"). If approval is required:
- Order must be approved first (Actions → Approve) before it can be opened
- "Approved" flag visible on PO
- **`Open` is absent from the Actions menu entirely until Approve has been clicked** — not just disabled/greyed; verify the menu's option list, not a disabled-state attribute (confirmed, C6533)
- Approving does not change Workflow status (order stays `Pending`); it only checks `Approved` and unlocks `Open`. Toast: `The Purchase order - {orderNumber} was successfully approved` (confirmed, C6533)

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
| Cancel | Open (requires `Orders: Cancel purchase orders` permission / `procedural - UI-Orders Order Cancel - execute`) |

**Cancel vs. Close (confirmed, C353546):** `Actions > Cancel` opens the same `Close - purchase order` overlay as a regular Close, but with `Reason` **pre-selected to `Cancelled`**. The resulting toast is identical to a normal close (`Order was closed`) and the order moves Open → Closed — but a **`Canceled` icon appears in the search results row** for that order, which a normal (non-Cancelled-reason) close does not show. Don't write "Cancel" and "Close" as the same scenario; the distinguishing assertion is the icon, not the toast.

---

## Exact UI Texts (from team test cases — use these verbatim)

> Toasts below confirmed verbatim against `folio-org/ui-orders/translations/ui-orders/en_US.json` (2026-07-21). `{orderNumber}`/`{lineNumber}` render as the record number; `<b>…</b>` = bold segment.

### Toast messages — PO
| Event | Toast text |
|---|---|
| PO opened | `The Purchase order - {orderNumber} has been successfully opened` |
| PO **closed** | `Order was closed` |
| PO unopened | `The Purchase order - {orderNumber} has been successfully unopened` |
| PO saved | `The Purchase order - {orderNumber} has been successfully saved` |
| PO reopened | `The Purchase order - {orderNumber} has been successfully reopened` |
| PO duplicated | `The purchase order was successfully duplicated` |
| PO duplicate failed | `The purchase order was not cloned` |
| PO deleted | `The purchase order {orderNumber} was successfully deleted` |

### Open-failure messages (validation on Open)
| Condition | Message |
|---|---|
| Open failed (generic) | `The Purchase order - {orderNumber} has not been opened` |
| Missing order status ref data | `Order can not be opened as the status of {value} is undefined` |
| Missing order type ref data | `Order can not be opened as the type of {value} is undefined` |
| Loan type not configured | `Order can not be opened as a loan type was not configured in ...` |
| Vendor not a vendor | `Order cannot be opened as the associated vendorId belongs to ...` |

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

### Location-restricted Funds (confirmed, C434140)
A Fund can have "Restrict use by location" checked with specific Locations added to it (Finance app, Fund's Locations accordion). Once such a Fund is selected in a POL's Fund distribution, the POL's own `Location` accordion "Name (code)" dropdown **narrows to only that fund's allowed locations** — don't test location selection on a restricted fund assuming the full location list is still offered; assert the dropdown is filtered.

### Vendor-currency default for new POL (confirmed, C440108)
When adding a POL, the `Currency` field in Cost details defaults to whatever the vendor Organization has in its own "Vendor currencies" (most recently used) — but if the vendor has **no** Vendor currencies configured, the field falls back to the **tenant's system default currency** (`Settings > Tenant > Language and localization`). A currency-default case must specify which of the two preconditions applies; they produce different expected values.

### Claiming interval inherited from Organization (confirmed, C423436)
`Claiming interval` on a new/edited POL is **read-only and pre-populated from the vendor Organization's own Claiming interval** as long as `Claiming active` is unchecked. Checking `Claiming active` makes the field editable and lets the user override the value; unchecking it again **clears the field** (does not revert to the Organization's value). Don't write a claiming-interval case that edits the field without first checking `Claiming active` — the field is inert until then.

### Unopen with "Synchronized order and receipt quantity" workflow (confirmed, C377037)
Unopening a POL on this receiving workflow presents a choice modal, not a plain confirmation: `Delete Holdings and items` vs `Delete items` (plus `Cancel`), warning that unreceived pieces with no current requests pending — and their "On order" items — will be deleted, and that Holdings with no other item references may also be deleted. The exact warning wording changed at Trillium to add the "with no current requests pending" qualifier — don't assert the pre-Trillium wording in current-release cases.

### Cost change while Open
Editing POL cost while the PO is Open immediately updates the encumbrance:
```
Expected: - Toast message "The purchase order line <POL number> was successfully updated" appears
          - "Current encumbrance" field in "Fund distribution" accordion contains <new value>
```

### Version history (confirmed C369046, C369047, C375995, C410833, C916261, C927735, C476746, C423660)

Entry point: a clock-icon `Version history` icon at the top-right of both the `Purchase order` details pane and the `PO Line details` pane (independent version histories for PO vs. each POL). Clicking it opens a 4th pane.

- **Pane header**: a version-count label (`1 version`, `2 versions`, etc.) below the pane title.
- **Cards are sorted most-recent-first.** Each card's title link shows the change date/time in `MM/DD/YYYY, HH:MM AM` format plus a small clock/"View this version" icon.
- **Three-way card labeling** (mirrors the same pattern documented in marc-bib-quickmarc.md's Version history):
  - **Newest card**: labeled `Current version`, shows `Source` (the user who made the change) and a `Changed` list of the fields that changed in that edit.
  - **Oldest card**: labeled `Original version`, shows NO `Changed` list — instead the underlying detail pane displays `Created by` / `Created on` (creator + creation timestamp).
  - **Middle cards**: show `Source` + a `Changed` list only — no `Current version`/`Original version` label at all.
  - **A record with only ONE version ever (never edited)** collapses newest and oldest into a single card that shows BOTH `Current version` AND `Original version` labels together, with no values/Source/Changed list under either (confirmed C410833) — don't assume these two labels are mutually exclusive.
- **Clicking a card highlights it grey** and highlights that version's changed fields in **yellow** on the underlying detail pane; while any historical card is selected, the `PO lines` and `Related invoices` accordions are hidden from the PO pane (they reappear once the Version history pane is closed via its `X` button).
- **A "no-op" save produces NO card at all** — if an edit is saved without actually changing any field value, no version-history entry appears (confirmed C375995); don't expect every Save & close click to add a card.
- **Lifecycle actions (Open, Close order, Reopen, checkbox toggles like `Manual`) each produce their own version card**, exactly like a field edit — a status/workflow transition is not exempt from version tracking.
- **`Show all` / `Show less` toggle appears only once a single version's `Changed` list exceeds 12 fields** — exactly 12 changed fields does NOT show the toggle; 13+ does. Clicking `Show all` reveals every changed field and flips the button to `Show less`.
- **Internal/backend-only field names are always filtered out of the `Changed` list**, even when they technically changed — confirmed for `nextPolNumber` (PO-level) and `searchLocationIds[]` (POL-level, appears when a cross-tenant Location edit is made — see ECS section below). Don't expect these raw field names to leak into the UI diff.
- **ECS**: editing a POL's Location to point at a different tenant shows `Affiliation` as a changed field in the `Changed` list and highlights it yellow on the detail pane, same as any other field (confirmed C476746).

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

## ECS / Consortia — Cross-Tenant Location Lookup via "Affiliation" Dropdown (confirmed C468189, C471514, C471515, C471516, C471517, C473256, C473257, C473258, C473259)

**This is a canonical, cross-app mechanic** — the identical UI and rules also apply in Receiving (see receiving.md's ECS section) and Invoices' "Add line from POL" modal (see invoices.md's ECS section); this file is the reference copy.

**Prerequisite:** `Settings > Consortium manager > Central ordering > "Allow user to select locations from other affiliations for central orders"` must be checked in the Central tenant. Without it, none of the below is available.

- On the Orders app's `Order lines` search (or the equivalent Location facet anywhere this pattern is reused), expanding the `Location` facet and clicking its `Location look-up` link opens a `Select locations` modal. When the prerequisite setting is on, this modal shows an **`Affiliation` dropdown** (defaulting to the current/Central tenant name) above the location list.
- Selecting a different tenant in the `Affiliation` dropdown re-scopes the location list in that modal to **that tenant's own locations only**. Checking a location and clicking `Save` adds it to the active `Location` filter, and PO lines using that location (created in whichever tenant it belongs to) are returned in the results — this is how a Central-tenant user finds order lines that reference a Member tenant's location (or a Member tenant's holding — same mechanic, confirmed C471515).
- **The `Affiliation` dropdown is Central-tenant-only** (confirmed C471516, and mirrored in Receiving): logging into a Member tenant and opening the same `Location look-up` modal shows NO `Affiliation` dropdown at all — only that Member tenant's own locations are available, with no cross-tenant lookup option.
- **The dropdown lists every tenant in the consortium, not just the tenants the logged-in user has an affiliation to** (confirmed C471517) — a user with affiliations only in Central + Member 1 still sees Member 2 (and any other member tenant) listed and selectable in the `Affiliation` dropdown. Don't write a test assuming the dropdown is scoped to the user's own assigned affiliations; it isn't.
- Clicking the `x` icon next to the active `Location` filter chip clears the filter and the results pane, independent of which affiliation/tenant was used to build that filter.

### A user cannot Open/Save a POL referencing a tenant they lack affiliation to (confirmed C468203)

If a PO line's Location was set (by another user, or before the current user's affiliations changed) to a tenant the current user does NOT have an affiliation to, both `Actions > Open` on the order and `Save & close` on an edit of that POL are blocked with the exact toast: `POL could not be saved. This record has location affiliations that your user does not have. These affiliations must be removed or the operation must be performed by a user that has the same affiliations as the record.`

- On `Open`, the order simply stays `Pending` and the error is shown — no partial state change.
- On `Edit`, `Save & close` is initially disabled (the mismatched Location field renders with its `Affiliation` and `Name (code)` sub-fields visible but read-only-effective); changing an unrelated field (e.g. Physical unit price) DOES enable the button, but clicking it still fails with the same toast and the Edit page stays open — the only fix is to remove the offending location line entirely (trash-can icon) and add a replacement the user does have affiliation to. Once that's done, both Save and the subsequent Open succeed normally.
- This is a genuinely different gate from the `Affiliation` dropdown/Location-lookup mechanic above — that one is about *finding* cross-tenant records; this one is about *acting* on a POL that already references a tenant outside the current user's own affiliations.

## Multi-Year Prepayment / "Payment terms" accordion (UIOR-1528 + UIOR-1530 + MODORDERS-1428)

A POL-level feature for tracking known future payments across multiple fiscal years (e.g. splitting a subscription across 2 FYs). Gated by a **`Multi-year payment`** checkbox in the **Ongoing order information** accordion (UIOR-1528); the **`Payment terms`** accordion (UIOR-1530) sits **below Fund distribution** and is inactive/collapsed until the checkbox is on.

**Payment terms accordion contents (when active):** `Total price` (numeric); `Remaining amount to be distributed` (= Total price − funds distributed in the FY cards); `Prepayment term` (integer, **default 2, not directly editable** — grows/shrinks via Add fiscal year / trash can); `Starting fiscal year` (dropdown, tooltip "Fiscal years must have been created for each year of prepayment"); **2 fund-distribution cards** initially (header `Fiscal year N (FY20xx)`); an `Add fiscal year` button under the bottom card; `Add fund distribution` inside each card (fields Fund ID / Value / Type currency|% with **Currency default** / Amount / trash-can Action). Info icon next to the accordion reads: `To enable the fields in the Payment terms accordion, select Multi-year payment in the Ongoing order information accordion`.

**Exact validation messages:** prepayment term 0/negative/non-integer → `Value must be a positive integer`; fund-distribution totals ≠ total → `The percentage or amount(s) should equal 100% of the total` (shown under Remaining amount, blocks Save); missing FY for the term duration → `Please ensure all fiscal years have been created for the duration of the prepayment term` (older wording seen live: `Please ensure all fiscal years have been created for the duration of the prepayment term`). `Add fiscal year` is ACTIVE only while the next sequential FY exists; only the LAST card gets a trash can (none when just 2 cards). **No encumbrance** is created for the POL when Payment terms is filled but the regular Fund distribution accordion is empty.

> **How the team tests this feature (real cases C1385639 / C1395029 / C1404901 / C1404902, Type = Functional, Test Group = Critical Path, refs = `UIOR-1528, UIOR-1530, MODORDERS-1428`):** NOT one atomic case per acceptance criterion — **4 large journey cases** that each weave many ACs into one realistic flow. Reproduce this shape for any multi-year-prepayment story:
> - **Create + edit an order with a 2-year prepayment spanning a fiscal-year rollover** (36 steps): build previous+current FY (no future FY), Ledger, Funds with budgets, an Ongoing Pending order; add a POL, hit the red-highlighted Payment-terms validation, see `Starting fiscal year` exclude the previous FY, get the "all fiscal years must be created" error at term=1, uncheck Multi-year → accordion collapses → save; then edit and run the FY rollover and re-verify.
> - **Create an order from a template that has a 3-year prepayment preconfigured** (28 steps) — verify the template carries the Multi-year settings into the new order.
> - **Multi-year prepayment NOT available for one-time orders** (11 steps) — the UIOR-1528 gating: the checkbox/feature is absent for one-time orders.
> - **Behavior when a new fiscal year begins** (19 steps) — over-time dynamic behavior.
>
> These "rollover", "from template", "one-time gating", and "new FY begins" journeys are **inferred from domain knowledge, not spelled out in the UIOR-1530 acceptance criteria** — propose them proactively in Scenario Analysis (see SKILL.md "Journey vs atomic cases"). Atomic per-AC cases give clean traceability but are not what the team ships for this kind of feature.

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
20. **Cancelling one POL in a multi-line order does NOT affect the other POLs** — only the cancelled line's linked item flips to `Order closed` (others linked to un-cancelled lines stay `On order`), only the cancelled line's Payment/Receipt status become `Cancelled` (others are untouched), and only the cancelled line's encumbrance is Released to 0.00 (others remain Unreleased at full amount). A case for POL cancellation on a multi-line order must assert the *other* lines are unaffected, not just that the cancelled one changed. (cases — C367963)
21. **Renewal date and Renewal interval are never required** to Open, Unopen, Close, or Reopen an Ongoing order — don't write a case that blocks any of those four transitions on missing renewal fields; that validation does not exist. (cases — C353627)
22. **Fund distribution totals must equal exactly 100%** (or exactly the total cost, if using Amount instead of Percent) before a POL can be saved — the UI shows a running `Remaining amount to be distributed: ${x}` figure above the Fund ID field and a blocking message `The percentage or amount(s) should be equal 100% of the total` below the accordion; `Save & close` is rejected (with the PO line left unsaved) until the distributed total matches exactly, even by a cent. (cases — C359009)
23. **The cross-tenant `Affiliation` dropdown (Location look-up modal) only appears in the Central tenant and lists ALL consortium tenants regardless of the user's own assigned affiliations** — see the dedicated ECS section above for the full mechanic; this same rule is reused verbatim in Receiving and Invoices. (cases — C468189, C471516, C471517)
24. **Version-history cards use three distinct labels, not a simple newest/oldest split** — newest = `Current version` + Changed list, oldest = `Original version` + no Changed list (Created by/on instead), middle cards = Changed list only, and a never-edited record's single card shows BOTH labels together with no values. (cases — C369046, C410833)
25. **A save that changes nothing produces no version-history card at all**, but every lifecycle transition (Open/Close/Reopen, even a checkbox toggle like `Manual`) DOES produce its own card, same as a field edit. (cases — C375995, C369046)
26. **A user without affiliation to a POL's referenced tenant cannot Open the order or Save an edit to that POL** — exact toast: `POL could not be saved. This record has location affiliations that your user does not have...`; the only fix is removing/replacing the offending Location line. (cases — C468203)

---

## Known Gaps / Items to Verify

> Verify these in environment before writing strict assertions.

- [ ] Requested TestRail `group_id=1389` maps to OAI-PMH in this tenant, not Orders; Orders context here was built from the Orders subtree rooted at section 105.
- [ ] Jira story/bug distillation for Orders could not be completed because project/component queries returned 0 with current API token visibility.
- [ ] Capability set strings extracted from raw TestRail HTML include noisy legacy/formatting variants; use the curated `Required Capability Sets (Eureka)` table above as the canonical source for new cases.

> ECS/Consortia enrichment round (2026-07-22, per self-assessment report priority #2): this file previously had zero ECS/Consortia content — the systemic gap flagged in the self-assessment. Added the "Cross-Tenant Location Lookup" section and Key Business Rule 23 from 9 real cases (C468189, C471514, C471515, C471516, C471517, C473256, C473257, C473258, C473259). This is the canonical write-up; receiving.md and invoices.md cross-reference it rather than duplicating the full mechanic.
>
> Version history + further Consortia round (2026-07-22, per self-assessment report priority #5): the old Version history entry was a single unsourced sentence. Read 8 cases from the same section-105 subtree — C369046, C369047, C375995, C410833, C916261, C927735, C476746, C423660 — and rewrote it as a full section with the three-way card-labeling scheme (matching the pattern already documented in marc-bib-quickmarc.md), the no-op-save/lifecycle-transition rules, the >12-fields Show all/less threshold, and the BE-only-field filtering rule. Also read 2 more cases from the 107-case "Consortium (Orders)" subtree (C468203 plus a supporting read of C422252) and added the "user without matching affiliation can't Open/Save a POL" gate with its exact error toast — a different mechanic from the Location-lookup dropdown already documented, easy to conflate. Added Key Business Rules 24-26. ~85 of the 107 Consortium (Orders) cases remain unread (mostly template-creation and item-status-propagation variants); lower priority since the core mechanics are now covered.
