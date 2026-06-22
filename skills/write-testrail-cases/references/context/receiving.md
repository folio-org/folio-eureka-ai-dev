# FOLIO Receiving App — Business Logic Context

> Generated/refreshed by the build-app-context workflow on 2026-06-17.
> Sources:
> - TestRail section subtree rooted at section_id=17995 (suite_id=21): sections 17995, 17996, 36735
> - TestRail coverage: 244 cases total in subtree; 0 cases tagged to focus releases (Umbrellaleaf, Trillium, Sunflower, Ramsons)
> - GitHub signal scan: folio-org/ui-receiving (labels/callouts/permission usage snippets)
> - Jira signal scan: project=FOLIO component=Receiving and project=UIREC (Done stories/bugs: 0 with current token scope)
> Strings marked [from cases] are mined from TestRail corpus.
> Strings marked [from source, verify in env] come from source scan and should be validated in target tenant UI before strict assertions.

---

## What is Receiving

The Receiving app confirms that materials ordered through the Orders app have been physically delivered to the library. It manages pieces (individual receiving units) tied to a Purchase Order Line (POL). Receiving is possible only for Open or Closed orders.

---

## Key Terms

| Term | Definition |
|---|---|
| Receiving title | The title of ordered material; can have one or more pieces |
| Piece | A single receivable unit under a receiving title |
| Package | A PO representing multiple titles; titles must be added before receive |
| Receive | Confirm piece delivery |
| Unreceive | Move received piece back to Expected |
| Unreceivable | Mark a piece that cannot be received |

---

## Piece Lifecycle

Expected -> Received
Expected -> Unreceivable
Received -> Expected (via Unreceive)

---

## Receiving Workflow

### Quick receive
1. In Expected accordion, select piece checkbox.
2. Click Quick receive.
3. Piece moves to Received immediately.

### Receive with detail form
1. Open piece from Expected accordion.
2. Edit piece/item fields as needed.
3. Click Receive.
4. Piece moves to Received.

### Must acknowledge receiving note
If POL has this flag enabled, receiving is blocked until user confirms Continue in dialog.

### Receive side effects
1. Piece status changes to Received.
2. If Create item is enabled, Inventory item status is In process.
3. POL receipt status recalculates (Partially Received or Fully Received).
4. PO can auto-close when all POLs are fully received and fully paid.

### Unreceive side effects
1. Piece moves back to Expected.
2. If item was created on receive, item is removed and lifecycle state is reversed.
3. POL receipt status recalculates.

---

## Inventory Integration

| Create item on piece | On Receive | On Unreceive |
|---|---|---|
| Yes | Item created with status In process | Created item removed; piece returns to Expected |
| No | No item created | Piece returns to Expected only |

Check in is a separate workflow: after receive, Check in app transitions item from In process to Available (or Awaiting pickup if request exists).

---

## Package POL Rules

- Package POL cannot be received directly.
- Titles must be added first (Orders Add package title or Receiving New action).
- Each added title is then receivable independently.

---

## Exact UI Signals (TestRail-mined)

### Toast messages
- The piece was successfully saved [from cases]
- Receiving successful [from cases]
- The piece was successfully deleted [from cases]
- The piece was successfully received [from cases]
- Item (barcode) created successfully [from cases]

### Modal and dialog titles
- Select order lines [from cases]
- Delete Holdings [from cases]
- Send claim [from cases]
- Select locations [from cases]
- Delete piece [from cases]
- Select user [from cases]
- Add piece [from cases]
- Select Organization [from cases]
- Delay piece [from cases]
- Are you sure? [from cases]
- Select instance [from cases]

### Pane titles
- Receiving [from cases]
- Search & filter [from cases]
- Search results [from cases]
- Title name [from cases]
- PO Line details [from cases]

### Accordion names
- Expected [from cases]
- Received [from cases]
- Unreceivable [from cases]
- Item details [from cases]
- Title information [from cases]
- POL details [from cases]
- Bound items [from cases]
- Routing lists [from cases]

### Frequent button labels
- Actions [from cases]
- Receive [from cases]
- Quick receive [from cases]
- Add piece [from cases]
- Save & close [from cases]
- Save [from cases]
- Cancel [from cases]
- Edit [from cases]
- Confirm [from cases]
- Unreceivable [from cases]

---

## Capability Sets (Eureka)

Curated receiving capabilities for test preconditions:

- Data - UI-Receiving - View
- Data - UI-Receiving - Create
- Data - UI-Receiving - Edit
- Data - UI-Receiving - Delete
- Procedural - UI-Receiving - Execute
- Data - UI-Receiving Acq-Units Assignment - Manage
- Procedural - UI-Receiving Acq-Units Assignment - Execute

Frequently co-required in cross-app flows:

- Data - UI-Orders Orders - View [from cases]
- Data - UI-Inventory Instance - View [from cases]

---

## Common Verification Patterns (from cases)

1. Title details verification pattern
- Open receiving title.
- Verify Expected and Received accordion state/counts.
- Add or receive piece.
- Re-verify movement between Expected and Received accordions plus status value.

2. Order linkage verification pattern
- From title details, open POL number link.
- Verify Orders app opens correct PO line.
- Verify receipt status update after receive/unreceive action.

3. Claiming state verification pattern
- Validate piece state labels in Expected/Received (for example Expected, Late, Claim delayed).
- Trigger claim action.
- Verify claim-related status text and piece placement.

---

## Search and Filters

Main search covers title, POL number, package name, vendor reference number.

Key filters used in receiving tests:
- Order status (Open, Closed, Pending)
- Receiving status (Expected, Received, Unreceivable)
- Order type, order format
- Location, vendor, material type
- Expected receipt date, received date, receipt due
- Acquisition unit, rush, bindery active

Important: Pending orders are not receivable.

---

## Key Business Rules for Test Cases

1. Receiving is available only for Open or Closed orders.
2. Piece lifecycle is Expected -> Received and reversible via Unreceive.
3. Must acknowledge receiving note blocks receive until Continue is confirmed.
4. Create item on receive sets item status to In process.
5. Unreceive reverses receive-side inventory effects.
6. Package POLs cannot be received directly.
7. POL receipt status recalculates automatically (Partially/Fully Received).
8. Auto-close can trigger from Receiving when receiving and payment completion conditions are met.
9. Quick receive skips detail form; Receive flow supports field edits first.
10. Check in is a separate step after receiving.
11. Claiming requires claiming to be active on the title.
12. Acquisition units on receiving titles follow order/acq-unit governance.

---

## Known Gaps and Verification Notes

- Focus release slice requested by user (Umbrellaleaf, Trillium, Sunflower, Ramsons) returned 0 tagged cases in this TestRail subtree. Context above therefore relies on full subtree corpus (244 cases) plus source/docs.
- Jira done stories/bugs for component/prefix queries returned 0 with current token scope.
- Some mined capability and status strings were noisy due free-text preconditions; this file keeps a curated capability set list for reliable precondition authoring.
- Before strict string matching in new manual tests, verify toast/modal wording in the target environment.
