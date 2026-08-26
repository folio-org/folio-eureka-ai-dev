# FOLIO Circulation Log — Business Logic Context

> Built 2026-07-21 (browser-based). **Exact UI Texts confirmed against `folio-org/ui-circulation-log/translations/ui-circulation-log/en_US.json` (2026-07-21).** TestRail: suite 21 section 1539 "Circulation log" (+ subsection 25716 "Additional Loan Comments"). This is a small, single-purpose read-only audit app: it has no create/edit of its own — every row is produced by an action in another app (Check in, Check out, Requests, Loans, Fees/Fines, Users) and viewed/filtered here. Cases that assert "a notice/action was logged" should read the destination app's context file (check-in.md, check-out.md, requests.md, loans.md, fees-fines.md) for the triggering action, and this file for the exact log row shape and filter behavior.

---

## What is Circulation Log

The Circulation log app is a searchable, filterable audit trail of circulation events: every check-in, check-out, loan change, request status change, fee/fine action, and patron/manual block gets one row here. Staff use it to investigate "what happened to this item/patron" without digging through individual records. It is read-only — the only actions available are jumping to the related record (`Item details`, `User details`, `Loan details`, `Request details`, `Fee/fine details`, notice policy/template links).

---

## UI structure [confirmed]

- **Search & filter pane** (confirmed exact initial state, C1307995, 2025): `Reset all` button (starts disabled); `User barcode` input with `Patron look-up` below it; `Item barcode` input; `Description` input with its own `Apply` button; `Date` accordion **starts expanded** with `From`/`To` inputs + `Apply`; `Service point` dropdown; then accordions `Loan`, `Notice`, `Fee/fine`, `Request` — these **start collapsed**, each expanding to its own set of `Circ action` checkboxes (Item block/Manual block/Patron block ride along within the relevant accordion's checkbox set).
- **Results table columns**: `User barcode`, `Item barcode`, `Object`, `Circ action`, `Date`, `Service point`, `Source`, `Description`, and an `Action` column with a per-row ellipsis menu.
- **Pagination** (confirmed, C1307995, 2025): results page **100 rows at a time**; `Previous`/`Next` buttons at the bottom, with the current row range (e.g. `1-100`, `101-200`) shown between them. `Previous` starts disabled on the first page; `Next` disables when the last page has fewer than 100 rows. Clicking `Next` focuses the first row of the new page (offset advances by 100); running a **new search/filter resets the offset to 0** — a known past bug (UICIRCLOG-185: "Offset not being reset when performing search from 2+ page") makes this an explicit regression-guard scenario, not just a nice-to-have.
- **Per-row `Action` ellipsis menu** — options depend on the `Object`/`Circ action` of that row: `Item details`, `User details`, `Loan details`, `Request details`, `Fee/fine details`, `Notice policy` (notice-policy detail), `Live version of template` (for Notice rows).
- Reset: `Reset all` clears every filter. Filters persist across navigating away and back (returning from a detail page via the app icon lands back on the last filtered view).

---

## Exact UI Texts [confirmed against en_US.json]

### Circ action values (per Object)

| Object | Circ action values |
|---|---|
| Loan | `Checked out`, `Checked out through override`, `Checked in`, `Renewed`, `Renewed through override`, `Changed due date`, `Claimed returned`, `Declared lost`, `Aged to lost`, `Anonymized`, `Closed loan`, `Marked as missing`, `Created through override`, `Staff information only added`, `Patron info added`, `Staff info added`, `Patron info superseded` |
| Request | `Created`, `Cancelled`, `Moved`, `Queue position reordered`, `Request status changed`, `Recall requested`, `Expired`, `Pickup expired` |
| Fee/Fine | `Paid fully`, `Paid partially`, `Waived fully`, `Waived partially`, `Transferred fully`, `Transferred partially`, `Refunded fully`, `Refunded partially`, `Credited fully`, `Cancelled as error`, `Billed`, `Staff information only added` (confirmed C17047 — a fee/fine's own comments accordion has an independent "Staff info" concept from the Loan one; filtered via the `Fee/fine` accordion's own `Staff information only added` checkbox, not the `Loan` accordion's) |
| Patron Block | `Patron blocked from requesting` |
| Manual Block | `Created`, `Edited`, `Deleted` |
| Item Block | `Created`, `Edited`, `Deleted` |
| Notice | `Send`, `Send error` |

> `logEvent.action.Picked up for use at location` → `In use`, `logEvent.action.Held for use at location` → `Held` (reading-room / "for use at location" flows).

### Permissions [confirmed]

`Circulation log: All` (view + all actions), `Circulation log: View` (view only) — capability set names: `Data - UI-Circulation-Log - View` (curate exact Eureka name in env).

### Export

`Export results (CSV)` action; toasts: `Your Circulation log export has been requested. Please wait while the file is downloaded.` (request accepted), `Export job has been completed.` (success), `Export job has been failed.` (failure), `Something went wrong with export file request, please try again.` (request error).

---

## Common Verification Patterns

### Filter by identifier / action, then verify the row (confirmed pattern from cases C15484, C16978, C16980, C16982, C16997, C16999)

1. Perform the triggering action in its own app (e.g. check out an item) — note the item/user barcode.
2. Open Circulation log; filter by the relevant identifier (`Item barcode` / `User barcode` / `Description`) OR by expanding the matching `Object` accordion (e.g. `Loan`) and checking the specific `Circ action` checkbox.
3. Expected: the row appears with the correct `Circ action` value and all columns populated (`User barcode`, `Item barcode`, `Object`, `Circ action`, `Date`, `Service point`, `Source`, `Description`).
4. `Reset all`, then re-find the same row via a different filter (barcode instead of checkbox) — the team routinely verifies **both** the checkbox-filter path and the barcode-filter path reach the same row, not just one.

### Cover every destination link from the Actions column (team convention — same "every entry point" principle as fees-fines)

Real cases (C16975, C16979, C16981, C16995, C16998) don't stop at confirming the row exists — they also open **every applicable destination** from the per-row ellipsis menu, one at a time, and confirm the log view is preserved on return:
- `Item details` → item record loads; returning to the app shows the same filtered log.
- `User details` → user record loads; same return-state check.
- `Loan details` / `Request details` / `Fee/fine details` → same pattern for loan/request/fee-fine rows.
- Clicking the item barcode text directly (not the ellipsis) is a **separate** entry point to Item details and should be checked too (regression source: UIIN-2606, "Item barcode redirects to the broken page in circ log").

Which destinations are offered depends on the row's `Object` — don't assert `Loan details` on a Request row, etc.

### Date range filter (confirmed C16976)

`From`/`To` date pickers + `Apply`. Team's real sequence: apply `From=today` alone (today's events only) → add `To=yesterday` isn't meaningful, instead they widen `From=yesterday` (today AND yesterday's events) → then narrow to `To=yesterday` alone (only yesterday's events) → `Reset` via the `x` on the filter chip. Cover widen-then-narrow, not just one static range.

### Notice row navigation — full destination set [confirmed — C17092, C17093; resolves prior Known Gap]

A Notice row's Action ellipsis menu offers, in order: `Loan details`, `User details`, `Notice policy`, `Live version of template` — each opens its destination, and returning via the Circulation-log app icon restores the same filtered log view (same "every entry point" pattern as other Objects). The item-barcode text link (separate from the ellipsis) still opens Item details for the corresponding row. A sent notice is independently findable both by checking `Notice` accordion > `Send`, and by pasting the recipient's patron barcode into `User barcode` — both paths return the identical row.

### CSV Export — record-count parity and ECS tenant isolation [confirmed — C353955, C825329; resolves prior Known Gap]

- The exported file's row count (total lines minus 1 header row) always exactly matches BOTH the on-screen results counter AND the raw `totalRecords` value from the underlying `GET /circulation/logs?limit=0` API call — verified true across arbitrary filter combinations (date range, Loan checkbox, Service point multiselect, Fee/fine `Billed`, Notice `Send`) at real scale (~100,000 records).
- In an ECS/multi-tenant environment, an export requested from Tenant_1 is retrievable ONLY via Tenant_1's own Export Manager (`Circulation log` job type) and contains ONLY Tenant_1 data; Tenant_2's simultaneous export is completely separate with no cross-tenant data leakage.

### Permission tier — "Circulation log: View" hides Actions entirely [confirmed — C365625; refines existing permission note]

With only `Circulation log: View` (no `: All`): the results table's entire `Action` (ellipsis) column is MISSING from the table, not merely disabled — there are no hyperlinks anywhere in the results. The top-right `Actions` menu itself is still visible and clickable, but its one item, `Export results (CSV)`, is absent from the dropdown regardless of which filter accordion (Loan/Notice/Fee-fine/Request) is currently applied.

### Anonymization strips patron identity retroactively AND for later actions on the same item [confirmed — C449382, C449383]

Before anonymization, searching the log by patron barcode correctly finds all 3 rows of a check-out/check-in cycle (`Checked out`, `Closed loan`, `Checked in`) with the patron barcode populated. After running "Anonymize all loans" (Users app, Closed loans tab) on that closed loan: (a) those same historical rows, now only findable by ITEM barcode, show a blank/absent User barcode; (b) critically, a brand-new check-in performed on that same item AFTER anonymization ALSO logs without any user barcode — anonymization severs the loan-to-patron link going forward, not just for the frozen historical rows. Holds identically whether check-in happens at the item's home service point or a different one.

### Source field always reflects the ACTING user, not the original checkout clerk [confirmed — C407706, C1259771]

When User A checks an item out and User B later performs Change-due-date or Renew (from the Loans list, Users app, or Loan details), the Circulation log row for THAT action shows Source = User B, while the original `Checked out` row's Source correctly remains User A — each row's Source is independently the user who performed that specific action, confirmed identical between the Loan-details action table and the Circulation log's own Source column. The same holds for renewal actions performed cross-tenant in an ECS environment.

### Shared cancellation reason — exact Description format [confirmed — C1282808]

Cancelling a Request using a Consortium-Manager-created "Shared" cancellation reason logs a `Request` / `Cancelled` row whose Description contains literally `Reason for cancellation: {text}`, where `{text}` is the reason's **"Description (internal)"** field value specifically — not the reason's display Name. Holds for both item-level and title-level requests.

### Patron look-up and free-text filter interplay [confirmed — C958914]

Clicking "Patron look-up" opens a "Select User" modal; selecting a user auto-populates the `User barcode` field directly (not a hidden separate filter). All three free-text fields (`User barcode`, `Item barcode`, `Description`) are independently focusable/editable and each has its own "x" clear icon; clicking the `Description` field's `Apply` button submits whatever is currently entered across User barcode + Item barcode simultaneously, not just Description.

### "-" placeholder for barcode-less users [confirmed — C360554]

If the user associated with a logged circulation action has NO barcode assigned at all, the `User barcode` column displays a literal `-` rather than being blank or showing another identifier (name, ID, etc.).

### Description-column timestamps follow the tenant's configured time zone, in both the UI and the CSV export [confirmed — C770448]

Date/time values embedded in the `Description` column (e.g. a Changed-due-date row's `New due date: {…} (from {…})` text) render in the tenant's configured Language-and-localization time zone, not UTC — and this formatting is identical between the on-screen column and the exported CSV's Description field (same file/UI parity pattern as the record-count rule above).

---

## Key Business Rules for Test Cases

1. Circulation log has **no create/edit of its own** — every row is a side effect of an action performed elsewhere; a log-verification case's precondition is "perform action X in app Y", not a Circulation-log-native setup step. (cases)
2. Filtering works both by **free-text identifier** (barcode/description) and by **checkbox within an Object accordion** — real cases test the same event is findable via both paths. (cases — C16978, C16980, C16982)
3. The `Action` ellipsis menu's available options **depend on the row's Object** (Loan rows offer Loan/User/Item details; Request rows offer Request details; Fee/fine rows offer Fee/fine details, etc.) — don't assert options that don't apply to that object type. (cases)
4. Returning from a destination page via the Circulation log app icon **restores the last-applied filter/results**, not a blank search. (cases — C16979, C16981, C16995, C16998)
5. `Description` filter matches free text entered as "Additional information"/comments on the underlying action (e.g. Claimed returned reason, patron/staff info comment) — confirmed distinct from the Circ action itself. (cases — C15853)
6. Closed-loan rows' `Description` should NOT show an unrelated stale "Backdated to: ..." value carried over from a prior action — a specific regression guard the team checks. (cases — C16999 / MODAUD-176)
7. `Export results (CSV)` is async: a "requested" toast fires immediately, a separate completed/failed toast fires when the job finishes — do not assert file contents from the first toast alone. (github)
8. Item-barcode text link and the ellipsis-menu `Item details` option are two separate entry points to the same destination — both have shipped bugs independently (UIIN-2606) and both should be checked per this skill's "every entry point" rule (see SKILL.md Scenario Coverage Checklist). (cases)
9. Results page **100 rows per page** with `Previous`/`Next` pagination; a **new search/filter must reset the offset to page 1** — this has regressed before (UICIRCLOG-185) and is a real regression-guard scenario for any case touching search-then-paginate-then-search-again flows. (cases — C1307995, 2025)
10. A Notice row's destinations are exactly Loan/User/Notice-policy/Live-template details, reachable via the ellipsis, plus the separate item-barcode text link. (cases — C17092, C17093)
11. Exported CSV row counts (minus the header) always exactly match both the on-screen counter and the raw API `totalRecords`, and ECS exports are strictly per-tenant with no cross-tenant leakage. (cases — C353955, C825329)
12. `Circulation log: View` (without `: All`) removes the entire Action column from the table and hides `Export results (CSV)` from the Actions menu — it doesn't merely disable them. (cases — C365625)
13. Anonymizing a loan strips patron identity not only from that loan's existing historical rows but from ANY future log event on the same item that still references the anonymized loan. (cases — C449382, C449383)
14. Every log row's Source reflects whoever performed THAT specific action, never the original checkout clerk carried forward — Change-due-date/Renew rows always show the acting user. (cases — C407706, C1259771)
15. A cancelled request's Description surfaces the cancellation reason's "Description (internal)" text, not its display Name — true for Shared (ECS) reasons too. (cases — C1282808)
16. A user with no barcode logs as `-` in the User barcode column rather than blank. (cases — C360554)

---

## Capability Sets (Eureka)

- `Data - UI-Circulation-Log - View` — view/filter the log and follow destination links (curate exact name in env; legacy permission names are `Circulation log: All` / `Circulation log: View`).

---

## Authoring style (measured 2026-07-23)

Circulation Log: **`Other` ~82%** / Func ~18%, median **~5 steps**, `User Journey` ~8%. Cases perform a circulation action (check out/in, request, fee/fine, notice) then verify the resulting **log entry** — correct action name, date, user, item, and that clicking through opens the right record. Keep them compact and `Other`; the value is asserting the exact logged action value and its link target, not re-testing the action itself. Preconditions set up the action's prerequisites; the log assertion is the point.

---

## Known Gaps / Items to Verify

- [ ] Exact Eureka capability-set name(s) — only legacy Okapi permission display names (`Circulation log: All` / `Circulation log: View`) confirmed so far.
- [x] Notice-row navigation (`Notice policy`, `Live version of template` links) — **confirmed** (C17092, C17093): see "Notice row navigation" above.
- [x] CSV export record-count parity and ECS tenant isolation — **confirmed** (C353955, C825329): see "CSV Export" above. Exact column HEADER names still not pulled from a literal downloaded file sample — only content/count parity is confirmed, not the header row's exact text.
- [x] Pagination behavior — confirmed live (C1307995, 2025): 100 rows/page, Previous/Next, offset-reset-on-new-search regression guard. See "Pagination" above.
- [ ] The Actions "..." icon's border-less styling (C368490) is a minor visual-only assertion — not worth its own gap, noted here only so it isn't rediscovered as "new" next round.

> N≥10 audit round (2026-07-22): 14 cases read (C17092, C17093, C353955, C825329, C365625, C449382, C449383, C407706, C1282808, C958914, C1259771, C360554, C770448, C368490). Resolved both of the file's open Known Gaps (Notice-row navigation, CSV export record-count/isolation behavior). Surfaced additional previously undocumented rules: the View-permission tier's complete removal (not just disabling) of the Action column and CSV export option, anonymization's forward-looking effect on future log events for the same item, the Source column always reflecting the acting user rather than the original clerk, the Shared-cancellation-reason Description format, the barcode-less-user "-" placeholder, and tenant-timezone-aware Description timestamps matching between UI and CSV. Added 7 new Key Business Rules (10-16).
>
> Random spot-check (2026-07-22): picked one fresh uncited case at random (C17047) to sanity-check this file's "Match" verdict from the earlier self-assessment. Found a real, if narrow, mistake: the Circ-action table listed `Staff information only added` only under `Loan` — the real case shows it also independently exists under `Fee/Fine` (filtered via the Fee/fine accordion's own checkbox, populated by a fee/fine's own comments feature, separate from a loan's). Corrected the table rather than treating this as a new file miss.
