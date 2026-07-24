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

## Exact UI Texts

> Use these verbatim in expected results. Never paraphrase.
> All strings below are [from cases] (mined from TestRail, not cross-checked against GitHub translations) — none are yet [confirmed] by a second source. Verify wording in the target environment before treating any single string as fixed, and prefer running `build-app-context` with GitHub access enabled for this repo to upgrade these to [confirmed].

> ✅ Toasts/errors below confirmed verbatim against `folio-org/ui-receiving/translations/ui-receiving/en_US.json` (2026-07-21). `<b>…</b>` = bold; `{enumeration}`/`{title}` interpolate.

### Toast messages
- `The piece was successfully saved` [confirmed — `piece.actions.savePiece.success`]
- `Receiving successful` (title receive) / `Unreceiving successful` [confirmed]
- `The piece <b>{enumeration}</b> was successfully deleted` [confirmed]
- `The piece <b>{enumeration}</b> was successfully received` [confirmed]
- `The piece <b>{enumeration}</b> was successfully unreceived` [confirmed]
- `Pieces expect successful` [confirmed]
- `The title <b>{title}</b> has been successfully added for <b>PO line {poLineNumber}</b>` [confirmed — C423486 + source]
- `The sequence of the piece was successfully changed from <b>{old}</b> to <b>{new}</b>` [confirmed]

### Edit piece form — "Save & close" dropdown actions

> ⚠️ **Version drift.** The Ramsons-era case C423537 listed the Expected-piece dropdown as `Save and create another / Quick receive / Delay claim / Send claim / Unreceivable / Delete`. In **current master** the confirmed action buttons are `Save and create another`, `Quick receive`, `Expect`, `Unreceive`, `Mark late`, `Delete` (keys `piece.action.button.*`) — i.e. `Delay claim`→ effectively `Mark late`, and `Unreceivable` is no longer a dropdown label (`Expect`/`Unreceive` toggle status instead). Assert against the release under test: use the case wording for older releases, the source wording for Trillium/Umbrellaleaf. Claiming is triggered via the `Send claim` flow (`piece.sendClaim.*`), which shows a "generate a claim job… Continue?" confirmation.

### Title information accordion — claiming fields (confirmed C423486)

`Claiming active` checkbox and `Claiming interval` field. `Claiming interval` is inactive/empty while `Claiming active` is unchecked; checking `Claiming active` activates the interval field (default value inherited from the vendor organization's `Claiming interval` in its `Vendor information` accordion). When claiming is turned off, `Claiming interval` shows `-`.

### Confirm dialogs & error messages (confirmed — ui-receiving)

| Trigger | Text |
|---|---|
| Unreceive confirm | `Unreceiving piece` / `Are you sure you want to unreceive piece? It will return to a status of Expected and any associated item will be set as On-Order.` |
| Delete piece confirm | `Delete piece` / `Are you sure you want to delete piece?` |
| Receive against closed order | `Order closed` / `The order linked to this Title is closed. Are you sure you want to receive this piece(s)?` |
| Title already exists | `The title {title} for PO line {poLineNumber} already exists` |
| Piece already received | `The piece record is already received` |
| Barcode not unique | `Barcode must be unique, piece and item data could not be updated.` |
| Create item not allowed | `Create item for piece format is not allowed. Please check "create inventory" value in the purchase order line` |
| Create piece on pending order | `Creating piece for pending order is not possible. Please open order` |
| Delete last synchronized piece | `The piece was not deleted because you cannot delete all pieces when ordering and receiving quantity are synchronized.` |
| Acq-unit restriction | `Action is restricted by acquisition unit. User is not assigned to the specified acquisitions unit.` |
| Fund distribution amounts (not %) | `Pieces can not be added to or deleted from this Title until all the Fund distributions on the related purchase order line are converted from amounts to percentages.` |

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

## Claiming / Late Status Timing Rules (confirmed — C436495, C436793, C436794)

> Requires POL `Claiming active` checked + `Claiming interval` (days) set. The backend batch job `POST /orders-storage/claiming/process` (run manually via Postman in these cases, otherwise scheduled) is what actually evaluates and flips statuses — a piece won't move to `Late` just because a date passed if this job hasn't run.

- **Late via Claiming interval**: a piece in `Expected` whose `Expected receipt date` + `Claiming interval` (days) has passed, once the claiming batch job runs, becomes `Late`. The related PO Line's Receipt status is unaffected (`Awaiting Receipt` for one-time orders still shows correctly), and the related Inventory Item stays in status `On order`.
- **Late via "Send claim" (Claim sent) expiry**: a piece manually set to `Claim sent` with a future "send claim" date becomes `Late` once that date passes and the batch job runs — same end state (Item stays `On order`), even though the piece got there via the claim-sent path rather than the plain expected-date path. PO Line receipt status for an ongoing order shows `Ongoing` (not `Awaiting Receipt`) in this scenario.
- **"Delay claim" wins over Claiming interval**: if a piece has an active `Delay claim` date that has passed, the piece becomes `Late` **even if the underlying `Claiming interval` (days since expected receipt) has NOT yet separately expired**. Don't assume Claiming interval must expire first — a manually-set Delay claim date is an independent, and higher-precedence, trigger for `Late`.
- In all three of these Late-transition scenarios, the associated Inventory Item's status remains `On order` — Late is purely a Receiving/piece-level status, it does not itself change Inventory item state.

## Binding Pieces (Bind pieces / Bound items) — entirely new feature area, confirmed C476838, C476880

> Requires the POL's `Bindery active` = Yes. Available from the `Received` accordion's Actions menu ("Bind pieces"), for both one-time and ongoing orders, package and non-package.

- **Only `Received` pieces are eligible for binding** — pieces in `Expected` or `Unreceivable` status (even with the `Bind` checkbox unchecked) are simply not listed in the Bind page's piece table at all; likewise a piece with `Bound` already active is excluded. Don't expect a validation error for these — they're silently filtered out of the candidate list.
- Bind page ("{POL number} - {Title name}") layout: item-record fields (`Barcode`, `Call number`, `Material type*`, `Permanent loan type*`, `Permanent location*`) at the top, a multi-select table of eligible received pieces below (columns: select-all checkbox, Display summary, Enumeration, Chronology, Copy number, Accession number, Barcode, Status, Call number), then `Cancel` (always active) / `Bind` (disabled until Barcode + Material type + Permanent loan type + Permanent location are all filled AND at least one piece is selected).
- On successful Bind: toast `Item ({barcode}) created successfully`; the bound pieces disappear from `Received` (only reappear there if the "Bound" filter checkbox is applied) and instead surface as a single new record in the `Bound items` accordion. Each bound original piece keeps its `Bound` checkbox checked when reopened via Edit; the FIRST piece bound into that item shows Item status `-` in its Item details accordion, while subsequently-bound pieces show `Unavailable` (i.e. only the newly-created bound item itself is `In process`; the original items/holdings of the other bound pieces become `Unavailable`, not deleted).
- `Bound pieces data` accordion (on the bound Item's own detail record) lists every piece bound into it: Barcode (links back to the original piece's item, when one exists), Display summary, Chronology, Copy number, Enumeration, Expected receipt date, and a per-row `X` (remove) button. Removing shows an `Are you sure?` confirmation: `Remove this piece from the bound item?` / `Cancel` / `Remove`.
- After binding, both the new bound-item holding location AND the original pieces' original holding locations remain visible under the Instance's Holdings list — binding does not delete or merge holdings.

## Abandoned Holdings (confirmed — C503243, C503244)

> "Abandoned holding" = a Holdings record left with zero pieces/items associated with it after an edit or deletion. FOLIO's receiving flows proactively manage (or ask about) these rather than leaving orphaned Holdings silently in Inventory.

- **Deleting the only piece tied to a holdings record that has no other pieces/items DOES automatically delete that now-empty holdings record** — no confirmation prompt for this specific path; verify by checking the Instance's Holdings count in Inventory before/after (it drops by one silently). (C503243)
- **Changing a piece's holding during Edit** (Select holdings dropdown → pick a different existing holding → Save & close), when doing so would abandon the *previous* holdings record, triggers the `Delete Holdings` popup: title-less modal with body `This piece is connected to records in inventory. After this edit there will be no other pieces OR items connected to the related Holdings record(s). After making this change would you like FOLIO to delete the Holdings record(s)?`, buttons `Cancel` / `Keep Holdings` / `Delete Holdings` (both action buttons highlighted blue/active). Choosing `Keep Holdings` preserves the now-empty holdings record — Inventory shows both the old (empty) and new holdings under the Instance. (C503244)
- This same `Delete Holdings` popup and Keep/Delete choice also appears mid-flow during full-screen batch receiving when a holding-swap would abandon a holding (see Batch Receiving below) — it is not exclusive to the single-piece Edit form.

## Batch Receiving on the Full-Screen "Receive" View (confirmed, C813585)

> Triggered from `Expected` accordion's Actions → `Receive` when there are many expected pieces (accordion itself paginates 30/page in the regular title view).

- Selecting `Receive` first opens a `Select expected date range` modal (`Start date` / `End date` date pickers, both **required** — leaving either blank and clicking Receive shows red `Required!` under the empty one). A date range with zero matching pieces opens the full-screen view with `The list contains no items` rather than blocking the action.
- The full-screen view loads/paginates in **batches of 50** pieces at a time, sorted by `Expected receipt date`, with a subheader showing progress like `50 of 112 receiving pieces · {startDate} - {endDate}`. Actions per batch: fill in fields per-row (Display summary, Barcode, Display on holding, etc.), optionally create a new holding inline (`Create new holding` link) or pick an existing one per piece, then click `Receive & load more` to commit the current batch and load the next 50 (button becomes `Receive` with no "load more" once the final batch is showing).
- If committing a batch would abandon a holding (e.g. a piece's holding is being swapped and the old one would end up empty), the same `Delete Holdings` popup from the single-piece flow appears mid-batch-commit — choosing `Delete Holdings` proceeds with cleanup and the next batch loads automatically after.
- **A holding newly created for one piece in a batch is NOT offered in the holding-selection dropdown for other pieces in that same batch** — each per-row "create new holding" is scoped to its own row, not shared/reusable within the batch, even though they're all being committed together.
- Final commit (last remaining pieces, "Receive" not "Receive & load more") returns to the Title details pane with a `Receiving successful` toast; the `Received` accordion count updates and any newly created holdings appear under the Instance with their received pieces already in `In process` status.

## Number Generators for Barcode / Accession Number / Call Number (confirmed, C700856)

> Configured in `Settings > Orders > General > Number generator options`, per field (Barcode, Accession number, Call number), each independently set to `Off` / `On, field not editable` / `On, field editable`. Sequences themselves are defined in `Settings > Service interaction > Number generator sequences`. Requires the `NumberGenerators` authorization role.

- When a field's mode is `On` (either variant), a `Generate numbers` icon appears next to it on both the single-piece Edit form (Item details accordion) and per-row in the Actions column of the full-screen batch `Receive` table; clicking it opens a `Generate numbers` picker where the user selects which sequence to draw from for Barcode/Accession number/Call number and generates the next value(s) in one action.
- **`On, field not editable`**: after generation, the field's content cannot be hand-edited at all (attempting to append/change text has no effect, or Save & close silently keeps the generated value).
- **`On, field editable`**: after generation, the user CAN manually add a prefix/suffix or otherwise edit the generated value before saving, and that edit persists through Receive and into the Item record.
- **`Off`**: the `Generate numbers` icon is not shown at all on the Edit form, and the entire Actions column (which would otherwise host the icon) is absent from the full-screen batch Receive table.
- A dedicated checkbox `Use the same generated number for accession number and call number` (available when Accession number and Call number are both in a generating mode) forces both fields to receive the identical generated value from one "Accession and call number" sequence selection — if Call number is independently set to `On, field editable` while Accession number is `On, field not editable`, only Call number can subsequently be hand-edited even though both started with the same generated value.
- Generated (and any subsequently hand-edited) values carry through correctly into the Received accordion's table and into the bound/received Item record — verify both the Receiving-app Received table AND the Edit-piece view after receiving, not just one.

## Piece ↔ Item Field Synchronization (confirmed, C959222 and related C432301-C432304)

- Fields `Display summary`, `Copy number`, `Enumeration`, `Chronology`, `Barcode`, `Call number`, `Accession number` exist on BOTH the Piece record (Piece details accordion, pre-receive) and the linked Item record (post-receive) — but **after a piece has been received, editing these fields on the Piece side (Piece details accordion) no longer updates the Item**, and editing them on the Item side (via Inventory or the piece's "Item details" accordion) is reflected back into the piece's "Item details" accordion display but NOT into the "Piece details" accordion fields. Treat "Piece details" as a frozen historical snapshot and "Item details" (on the same Edit piece form) as the live mirror of the actual Item record once receiving has occurred.
- This one-way-mirror behavior holds even across an Unreceive — unreceiving a piece moves it back to `Expected` but does not resync "Piece details" from the Item; only "Item details" reflects the live Item state.
- Clearing a field on the Item side clears it in the piece's "Item details" mirror too (this is a live link, not a one-time copy) — but never touches "Piece details".

---

## ECS / Consortia — Cross-Tenant Location Lookup and "Active affiliation default" (confirmed C468235-family, C471514, C471515, C471516, C471517, C473256, C473257, C473258, C473259, C511231)

**Canonical mechanic documented in orders.md** ("Cross-Tenant Location Lookup via 'Affiliation' Dropdown") — Receiving reuses the identical `Location` facet > `Location look-up` > `Select locations` modal with its `Affiliation` dropdown, in **two separate surfaces**:

1. The Receiving app's main `Search & filter` pane `Location` facet.
2. The `POL number look-up` modal (used when adding/looking up a POL to receive against) — same `Affiliation` dropdown, same rules, confirmed as a fully separate case family (C473256-C473259).

Both surfaces confirm the same three core rules from orders.md: Central-tenant-only dropdown presence (C471516/C473258), all-tenants-listed-regardless-of-user-affiliation (C471517), and Location-or-Holding from a Member tenant both resolve correctly (C471514/C471515, C473256/C473257).

### A second, distinct ECS mechanic: "Active affiliation default" (confirmed C511231)

Independent of the Location-lookup pattern above, `Settings > Orders > Network ordering > Central ordering > "Active affiliation default"` is a **per-Member-tenant** setting. When selected, it changes what the Receiving app's top-level `Search & filter` pane looks like for that Member tenant:

- The pane shows a **segmented control** between the user's active-affiliation tenant name and the Central tenant name, with the active-affiliation segment selected by default (not Central).
- The `Vendor` accordion's `Organization look-up` modal, while the active-affiliation segment is selected, returns **only that Member tenant's own organizations** — no `Affiliation` dropdown appears in this modal (unlike the Location-lookup modal above, which always has one from Central). Selecting an organization then returns only that tenant's own Titles/POLs, not the Central tenant's.
- This is a **different UI paradigm** (app-level segmented toggle vs. a per-facet `Affiliation` dropdown) gating a **different filter** (Organization vs. Location) — don't conflate the two mechanics when writing a test; check which setting/precondition the scenario actually requires.

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
13. **Delay claim date takes precedence over Claiming interval expiry for the Late transition** — a piece goes Late as soon as its Delay claim date passes, independent of whether the underlying Claiming interval has separately expired. (cases — C436794)
14. **Only Received pieces are eligible for Bind pieces** — Expected/Unreceivable pieces (and already-Bound pieces) never appear in the Bind page's candidate list. (cases — C476838, C476880)
15. **Deleting a piece that leaves its holding with zero remaining pieces/items auto-deletes that holding, no confirmation** — but changing a piece's holding assignment mid-edit (when it would abandon the old holding) DOES prompt a Keep/Delete Holdings choice. (cases — C503243, C503244)
16. **Full-screen batch Receive commits in pages of 50**, driven by an explicit Start/End expected-date-range selection; per-batch holding creation is scoped to that batch's own rows only. (cases — C813585)
17. **Post-receive, Piece-side fields are a frozen snapshot; Item-side fields are the live mirror** — edits to the Piece details accordion after receiving do not propagate to the Item, and vice versa edits to the Item record only update the piece's Item details accordion, never Piece details. (cases — C959222)
18. **Two independent ECS/consortia mechanics exist and must not be conflated**: the cross-tenant `Affiliation` dropdown inside the `Location` facet's look-up modal (Central-tenant-only, lists all tenants) versus the per-Member-tenant `Active affiliation default` setting (an app-level Central/Member segmented toggle gating the `Vendor`/Organization facet instead). See the dedicated ECS section above. (cases — C471516, C471517, C511231)
19. **Adding a piece with `Create item`/`Create holdings` is gated by the order's encumbrance/budget, not just by receiving state** — when `Enforce all budget encumbrance limits` is active and creating the item would exceed the encumbrance limit, OR when the linked Fund's budget is **not Active**, saving the piece fails with the error toast **`The piece was not saved.`** and **no Holdings/Item is created** (the Expected accordion is unchanged). Conversely, deleting such a piece must also not leave a stray holdings/item behind. A create-on-receive case should state the budget state and encumbrance-limit setting in preconditions, because they change whether the Inventory records are created at all. (cases — C1250459, C1250460; refs MODORDERS-1415)
20. **A POL's receiving workflow (Synchronized vs Independent order-and-receipt quantity) changes piece/holdings behavior** — with the *synchronized* workflow you cannot delete the last piece (`The piece was not deleted because you cannot delete all pieces when ordering and receiving quantity are synchronized.`); an *independent*-workflow POL allows piece/holdings operations the synchronized one blocks (e.g. "delete only holding not related to PO line"). State the POL's workflow in preconditions for any piece-delete / holdings-abandonment case. (cases — C1273175, C1273162)

---

## Authoring style (measured 2026-07-23)

Receiving is almost **purely `Functional` (~99.6%, 243/244)**, median ~8 steps, `User Journey` ~0% (`No`). Cases walk a real piece flow (`Title > Expected/Received accordion > Actions > Add piece / Receive / Edit piece / Delete`) and verify Inventory + (often) Finance side effects — because create-on-receive touches Holdings/Item creation and encumbrance. Preconditions carry the acquisition setup (Open PO with an ongoing/one-time POL, its receiving workflow Synchronized/Independent, the linked Fund/budget state) and any Number-generator / claiming settings. Set `Type = Functional`; keep the flow single and verify the created/deleted Holdings/Item and, where budget-gated, the `The piece was not saved.` outcome.

---

## Known Gaps and Verification Notes

- Focus release slice requested by user (Umbrellaleaf, Trillium, Sunflower, Ramsons) returned 0 tagged cases in this TestRail subtree. Context above therefore relies on full subtree corpus (244 cases) plus source/docs.
- Jira done stories/bugs for component/prefix queries returned 0 with current token scope.
- Some mined capability and status strings were noisy due free-text preconditions; this file keeps a curated capability set list for reliable precondition authoring.
- Before strict string matching in new manual tests, verify toast/modal wording in the target environment.
- [ ] Sequence-number generation for predicted piece sets (C844201/C844209/C844210) was located but not yet read this round — revisit for the Serials-integration piece-generation angle.

> N≥10 audit round (2026-07-21): 10 cases read — C436495, C436793, C436794, C476838, C476880, C503243, C503244, C813585, C700856, C959222. This was the first round to surface entirely new feature areas not previously in this file: Bind pieces/Bound items, abandoned-holdings handling, Late-status timing precedence rules, full-screen batch receiving (50-at-a-time), and Number Generators for Barcode/Accession/Call number. All added above as dedicated sections plus Key Business Rules 13-17.
>
> ECS/Consortia enrichment round (2026-07-22, per self-assessment report priority #2): this file previously had zero ECS/Consortia content despite section 36735 ("Consortium (Receiving)") holding 104+ cases. Read 10 cases from that subtree — C471514, C471515, C471516, C471517, C473256, C473257, C473258, C473259, C511231, plus title-scan of the C468235 family — surfacing two distinct mechanics (Location-lookup Affiliation dropdown, reused from orders.md; and the separate "Active affiliation default" segmented-toggle setting). Added the ECS section and Key Business Rule 18. The remaining ~94 cases in section 36735 (piece/title-level ECS behaviors, not filter/search UI) are still unaudited — a candidate for a future round if deeper ECS piece-lifecycle coverage is wanted.
