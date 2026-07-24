# FOLIO Mediated Requests — Business Logic Context

> Built 2026-07-21 (browser-based); **corrected 2026-07-21 same day** after re-verification found real 2025 TestRail coverage that was missed on first pass. **Exact UI Texts confirmed against `folio-org/ui-requests-mediated/translations/ui-requests-mediated/en_US.json`.** TestRail: suite 21 section 32570 "Mediated requests" (subsections 57628 "oLOAN", 61629 "Mediated request notices", 74667 "Mediated request patron blocks") — contains 15+ cases created in 2025 alone (releases Sunflower=19/Trillium=20); this is NOT a thin-coverage area, it was simply not pulled when this file was first built from GitHub translations only. Business rules below now include both translation-derived and live-case-confirmed content (marked accordingly).

---

## What is Mediated Requests

Mediated Requests lets library staff place and manage requests **on behalf of patrons** (a mediated / "secure" workflow, typically used with a **secure tenant** holding sensitive patrons). A staff-created request starts as **New - Awaiting confirmation** and must be reviewed and **confirmed** (which creates the real request in the Requests app) or **declined**. The app also drives the physical hand-off: **Confirm item arrival** and **Send item in transit** activities move the item toward the requester's pickup service point.

Jira/repo: `UIREQMED` / `MODREQMED`, `folio-org/ui-requests-mediated`.

---

## Key Terms

| Term | Definition |
|---|---|
| Mediated request | A request staff create for a patron that requires confirmation before becoming a real request. |
| Secure tenant | Tenant holding the mediated patrons/records the workflow protects. |
| Confirm | Approve a `New - Awaiting confirmation` mediated request → creates the actual request. |
| Decline | Reject a mediated request → `Closed - Declined`. |
| Confirm item arrival | Activity confirming the paged item has arrived for approval. |
| Send item in transit | Activity routing the item onward (e.g. to the pickup service point / to be checked out). |
| Interim service point | Service point used in the mediation/confirmation hand-off. |

---

## App structure — three activities

Filter pane `Select activity` switches between:
1. **Mediated requests** (`Mediated requests activities`) — the request list + New/Edit/Decline.
2. **Confirm item arrival** — `Scan items` pane to confirm arrivals.
3. **Send item in transit** — `Scan items` pane to route items onward.

---

## Status lifecycle [confirmed]

```
New - Awaiting confirmation
   ├─ Edit & confirm → (real request created) → Open - Not yet filled
   └─ Decline → Closed - Declined

Open - Not yet filled
   → Open - In transit for approval → Open - Item arrived
   → Open - In transit to be checked out
   → Open - Awaiting pickup  /  Open - Awaiting delivery
   → Closed - Filled   (or Closed - Cancelled)
```

Confirmed status values: `New - Awaiting confirmation`, `Open - Not yet filled`, `Open - In transit for approval`, `Open - Item arrived`, `Open - In transit to be checked out`, `Open - Awaiting pickup`, `Open - Awaiting delivery`, `Closed - Filled`, `Closed - Cancelled`, `Closed - Declined`.

---

## Exact UI Texts [all confirmed — ui-requests-mediated en_US.json]

### New / Edit mediated request form
- Pane titles: `New mediated request` / `Edit mediated request`.
- `Create title level request` checkbox.
- Accordions: `Title information`, `Item information`, `Requester information`, `Request information`.
- Inputs: `Instance HRID or UUID` (placeholder `Enter HRID or UUID`, lookup `Title look-up`); `Item barcode` (placeholder `Scan or enter item barcode`); `Requester barcode` (placeholder `Scan or enter requester barcode`, lookup `Requester look-up`).
- Request fields: `Request type` (`Select request type`; options `Page` / `Hold` / `Recall`), `Request status`, `Patron comments`, `Fulfillment preference` (`Hold Shelf` / `Delivery`), `Pickup service point` (`Select pickup service point`), `Delivery address`.
- Buttons: `Enter`, `Cancel`, `Confirm`.

### Form errors [confirmed]
| Condition | Message |
|---|---|
| No instance selected | `Please select an instance and hit enter` |
| No item selected | `Please select an item and hit enter` |
| Item barcode invalid | `Item with this barcode does not exist` |
| No requester | `Please fill out requester information to continue` |
| Requester barcode invalid | `User with this barcode does not exist` |
| Instance HRID/UUID invalid | `Title with this HRID or UUID does not exist` |

### Toasts [confirmed]
| Event | Text |
|---|---|
| Mediated request saved | `Mediated request has been successfully saved` |
| Request created (on confirm) | `Request has been successfully created for {requester}` |
| Save failed | `Mediated request cannot be successfully saved` |
| Create failed | `Request was not successfully created` |
| CSV report generating | `A CSV results report is being generated. This may take some time for larger result sets.` |

### List, details & actions [confirmed]
- List columns: `Mediated request date`, `Title`, `Item barcode`, `Effective call number string`, `Mediated request status`, `Requester`, `Requester barcode`. Action menu: `New mediated request`, `Export results (CSV)`.
- Details pane: `Mediated request details`; action menu `Edit & confirm`, `Decline`. Accordions: `Mediated request information`, `Requester information`, `Title information`, `Item information`. Fields: `Mediated request type`, `Mediated request status`, `Mediated request level` (`Item`/`Title`), `Confirmed request`, `Patron comments`; link `View details in Requests`.
- Decline modal: title `Confirm Mediated request decline`; message `<b>{title}</b> will be <b>declined</b>`; `Confirm` / `Back`.

### Search by UUID + CSV export (confirmed live, C844200, 2025)
The `Select activity` pane's search box accepts the **mediated request UUID** directly (not just barcode/name text), including exact and partial matches. `Reset all` clears the result table entirely (not just the filters). No-match message (exact team wording): `No results found for "{search value}". Please check your spelling and filters.` — this fires both for a *partial* UUID and for a value that matches nothing. `Actions > Export results (CSV)` downloads a CSV whose row count must equal the on-screen result count — a case should verify the file's row-for-row content, not just that a download happened.

### Three-tenant structure is the norm, not the exception (confirmed live, C692196, 2025)
A realistic mediated-request scenario typically spans **three** tenants at once, not just "a secure tenant": a **Central** tenant where `Settings > Circulation > General > Consortium title level requests (TLR) > Enable consortium title level requests (TLR)` must be turned on first; the **Secure** tenant (e.g. "University") where the mediated patron/requester lives and where staff work in the Mediated Requests app; and a **member** tenant (e.g. "College") holding the shared Instance/item actually being requested. Preconditions for a new case should name all three roles explicitly, not just "secure tenant" — and `ECS Enabled = true` is the norm for this app's cases, not an exception.

### Creating a request can go straight to Confirm (confirmed live, C692196, 2025)
The `New mediated request` form itself exposes a `Confirm` button (enabled once item + requester + request type + pickup service point are filled) — a staff user with confirm capability can create and confirm in one flow, landing directly on `Open - Not yet filled` without stopping at `New - Awaiting confirmation`. The two-step "create then separately Edit & confirm later" flow documented below is the path for a request created by staff **without** confirm capability (or deliberately saved for a second reviewer) — both paths are real and should be covered as distinct scenarios, not assumed to be the same case shape.

### Confirm item arrival / Send item in transit [confirmed]
- Panes `Confirm item arrival` / `Send item in transit`; `Scan items` main section; input placeholder `Scan or enter item barcode`; `Enter`; empty `No items have been entered yet`.
- Error modals: `Item not confirmed as arrived` / `No "Confirm item arrival" transaction could be found for this item`; `Item not sent in transit` / `No "Send item in transit" transaction could be found for this item`; `Close`.
- Confirm-item list columns: `Arrival date`, `In transit date`, `Title`, `Item barcode`, `Effective call number string`, `Mediated request status`, `Requester`, `Requester barcode`.

### Patron Notices for Mediated Requests [confirmed live — C692073, C692119; resolves prior Known Gap]

- Non-TLR mediated requests use the SAME notice mechanism as ordinary Requests: templates + a policy configured in the **Secure** tenant's own Settings > Circulation > Patron notice templates/policies (Category = Request), keyed to the identical triggering events (`Page request`, `Awaiting pickup`, `Cancel request`). Confirmed firing correctly across the full mediation lifecycle (create → Confirm item arrival → Send item in transit → Awaiting pickup → Cancel), even though the request physically spans Central/Member/Secure tenants.
- TLR mediated requests instead use the dedicated **"TLR Patron notice templates"** settings page (Secure tenant) with exactly two slots: **Confirmation notice** and **Cancellation notice** — this mirrors circulation-settings.md's TLR notice concept, now confirmed specifically for the Mediated-requests/Secure-tenant context.
- Cancelling the REAL circulation Request from ANY tenant's Requests app (not just Secure) still correctly fires the Secure tenant's configured Cancel/Cancellation-notice template — notice wiring stays anchored to the Secure tenant's policy regardless of where the cancel action itself was performed.

### Patron Blocks in Mediated Requests [confirmed live — C831971, C831973; resolves prior Known Gap]

- **"Requests" patron block** fires the standard `Patron blocked from requesting` popup the moment a blocked patron's barcode is entered (Enter) into "Requester barcode" on the New-mediated-request form — Override opens the same "Override patron block" modal (required Comment) used elsewhere; after Save & close, the New-request form remains open with all previously entered values retained, letting staff finish and save/confirm normally. Confirmed to work identically whether the requested instance is Shared (lives in a Member tenant) or Local (lives in the Secure tenant itself).
- **"Borrowing" patron block** fires when checking out the item once it arrives via the mediation workflow (Check out app) — same `Patron blocked from borrowing` popup → Override → Comment → checkout completes as `Checked out through override`.
- These are two INDEPENDENT gates: overriding the Requests block at creation time does NOT carry over to checkout — a Borrowing-blocked patron must be separately overridden again at the Check-out step even for the very same mediated-request journey.

---

## Secure Patron Data Masking [confirmed live — C627409, C856508; previously undocumented]

- Once a Mediated Request is confirmed, the resulting REAL circulation Requests visible in the **Central** and **Member** tenants display the requester under a fixed fake identity: name `Patron, Secure`, barcode of the exact form `securepatron_{uuid}` — the real patron's identity is never exposed outside the Secure tenant.
- On these masked Request-details pages (viewed from Central/Member), the entire `Actions` menu is suppressed — staff in those tenants cannot Cancel, Edit, or otherwise act on a secure-patron request at all; only Secure-tenant staff (or the mediated-request-origin flow) can act on it.
- The same masking applies inside the **Reorder queue** view: Requester/Requester-barcode columns show the masked values when viewed from Central/Member, but show the REAL name/barcode when viewed from inside the Secure tenant itself.
- **Known cross-tenant staleness (accepted, MODTLR-150)**: reordering a queue from Central correctly updates "Position in queue" consistently in the Member/Data tenant's own view, but the SAME queue viewed from the Secure tenant does NOT reflect the updated order — a reorder-queue case covering all three tenants should expect this specific lag, not treat it as a failure.

## "Congressional Loan" — Cross-Tenant Loan Lifecycle After Checkout [confirmed live — C812848, C825272; new terminology]

- Once a mediated request completes checkout, the resulting loan is referred to in real cases as a **"congressional loan"** — a real loan whose patron/loan record lives in the Secure tenant but whose item physically resides (and is checked in/out) across Member/Central tenants too. Recognize this term when it appears in stories/cases for this area.
- **Declare lost** must be performed from the SECURE tenant's Loan details (where the real patron/loan lives); the SAME loan is then visible read-only from the Member ("data") and Central tenants' own Loan-details views, each showing `Declared lost` with its OWN tenant-specific Lost item fee policy NAME — the same cross-tenant loan can have differently-named lost-item-fee policies applied per tenant — but the `Declare lost` action itself is disabled everywhere except the Secure tenant.
- Checking in a declared-lost congressional loan typically requires **multiple check-in passes across different tenants** (e.g. Member/Data tenant → Secure tenant → Data tenant again) before the item finally reaches `Available`, with intermediate `In transit` states and confirmation popups at each hop — reflecting genuine multi-tenant physical routing, not a bug.
- **Claim returned** must likewise be actioned from the Secure tenant (where "Resolve claim" appears), but the "Found by library" CHECK-IN resolution can be performed from a different tenant's Check-in app. A known timing quirk (tracked as MCBFF-158, cited directly in the case) means the Secure tenant's own view of the loan may lag in showing it as closed immediately after a different tenant's check-in resolves it — expect (don't fail on) this specific lag when writing/running such a case.
- **Congressional-loan mechanics generalize beyond the first two sampled cases** (confirmed live, C895640, blind-generate/diff validation round, 2026-07-22): declaring a congressional loan lost with a **$0 Set-cost Lost item fee policy** auto-closes the loan immediately at the Declare-lost confirm step itself (`Closed loan` action + `Lost and paid` item status appear together in the SAME action, `Declare lost` button becomes disabled, `Fees/fines incurred` stays blank) — the exact same $0-auto-close pattern already documented in `loans.md` for ordinary loans is confirmed to generalize unchanged to the Secure-tenant congressional-loan case. **Central tenant has no record of oLOAN materials at all** — searching Central's own Circulation log for the item's barcode returns zero results, because the request/loan for oLOAN (congressional-loan) materials literally does not exist as a Central-tenant record, not merely a masked/hidden one. **Check-in of a declared-lost congressional item from a non-Secure tenant suppresses `Loan details` and `Patron details`** from that check-in result row's ellipsis actions menu — a third confirmed masking surface alongside the Requests-details Actions-menu suppression and the Reorder-queue masking already documented above.

## Additional Confirmed Edge Cases

- **Inactive-user confirm failure** [C825435]: attempting to `Confirm` a new mediated request for a patron who has since become Inactive fails with toast `Request was not successfully created`; the form stays open; after Cancel, searches in ALL THREE tenants (Secure/Member/Central) consistently show zero open requests for that item — no orphaned partial request is left anywhere in the consortium.
- **Proxy/Sponsor UI is deliberately hidden** [C624245]: scanning a user with an active proxy/sponsor relationship into "Requester barcode" during mediated-request CREATION does NOT trigger the normal "Who are you acting as?" modal seen in Requests/Check-out — the mediated request is always created directly for the scanned patron, with no proxy-substitution path offered in this app.
- **Deleted-Title edit error retains the stale value** [C594453]: if the Instance behind an existing `New - Awaiting confirmation` request is deleted after creation, opening `Edit & confirm` still shows the original (now-stale) HRID/UUID in the search box alongside the standard `Title with this HRID or UUID does not exist` error — the form surfaces the broken reference rather than silently clearing it.

---

## Capability Sets (Eureka) [confirmed live, C844200/C692196, 2025 — exact strings, no longer inferred]

| Action | Permission (Okapi display name) | Capability/Set (Eureka) |
|---|---|---|
| View | `Mediated requests: View` | `data — UI-Requests-Mediated — view` |
| All (manage) | `Mediated requests: All permissions` | `data — UI-Requests-Mediated — manage` |
| View, create, edit | `Mediated requests: View, create, edit` | `procedural — UI-Requests-Mediated Requests-Mediated View-Create-Edit — execute` |
| View, decline | `Mediated requests: View, decline` | `procedural — UI-Requests-Mediated Requests-Mediated View-Decline — execute` |
| View, confirm | `Mediated requests: View, confirm` | `procedural — UI-Requests-Mediated Requests-Mediated View-Confirm — execute` |
| Confirm item arrival | `Mediated requests: Confirm item arrival` | `procedural — UI-Requests-Mediated Requests-Mediated Confirm-Item-Arrival — execute` |
| Send item in transit | `Mediated requests: Send item in transit` | `procedural — UI-Requests-Mediated Requests-Mediated Send-Item-In-Transit — execute` |

> Real cases test each permission/capability **separately** (C844200 precondition note: "best to test each permission separately") — a capability-boundary scenario set for this app should cover each row individually, not just "manage" vs "view".

---

## Key Business Rules for Test Cases

1. A mediated request is created by staff for a patron and starts as **`New - Awaiting confirmation`** — it is NOT a real request until confirmed. (github)
2. **Edit & confirm** creates the actual request (`Request has been successfully created for {requester}` toast) and links it — details show `Confirmed request` and a `View details in Requests` link. (github)
3. **Decline** closes the mediated request as `Closed - Declined` after the `Confirm Mediated request decline` modal. (github)
4. Request type offered (`Page`/`Hold`/`Recall`) and fulfillment (`Hold Shelf`/`Delivery`) follow the same rules as normal Requests; a title-level request uses the `Create title level request` checkbox. (github + requests.md)
5. The **Confirm item arrival** and **Send item in transit** activities require a matching transaction for the scanned item, else the error modal appears (`No "…" transaction could be found for this item`). (github)
6. Mediated request statuses extend the normal request lifecycle with mediation-specific states (`Open - In transit for approval`, `Open - Item arrived`, `Open - In transit to be checked out`). (github)
7. Separate capability sets gate create/edit vs confirm vs decline vs the two item activities — a user may see mediated requests but lack confirm/decline. Confirmed concretely: a user with ONLY `Mediated requests: View, decline` opens a `New - Awaiting confirmation` request's details and the `Actions` menu shows exactly one option, `Decline` — no `Edit & confirm` (that requires the separate View-create-edit or View-confirm capability). Each of the 7 capability rows in the table above gates its own Actions-menu entry independently; don't assume "decline visible" implies "confirm visible" or vice versa. (github + cases — C523647)
8. Notes: staff notes can be attached to a mediated request (`New staff note` / `Staff notes`). (github)
9. A realistic scenario spans **three tenants** (Central config + Secure requester tenant + member-tenant shared item) with `Enable consortium title level requests (TLR)` active in Central as a precondition — this app is ECS-by-default, not ECS-as-a-special-case. (cases — C692196, 2025)
10. The `New mediated request` form can go straight to `Confirm` in one flow (landing on `Open - Not yet filled` directly) when the creating staff user has confirm capability — the separate "create, then later Edit & confirm" path is for staff without that capability or a deliberate two-reviewer flow. Both are real, cover both. (cases — C692196, 2025)
11. The result list search accepts the mediated request **UUID** (exact or partial) in addition to text fields, and supports CSV export whose row count must match the on-screen result count. (cases — C844200, 2025)
12. Cancelling the confirmed circulation Request cascades one-way to close the originating Mediated Request as `Closed - Cancelled` too — for both Item-level and Title-level requests. (cases — C630441)
13. Requester identity is masked outside the Secure tenant (`Patron, Secure` / `securepatron_{uuid}`), and the Actions menu is fully suppressed on masked Request-details pages viewed from Central/Member. (cases — C627409, C856508)
14. A confirmed mediated request's post-checkout loan ("congressional loan") permits Declare-lost/Claim-returned actions only from the Secure tenant, while Member/Central tenants get a read-only mirrored view with the action disabled; resolution can require multiple cross-tenant check-in passes. A $0 Set-cost Lost item fee policy auto-closes the congressional loan at Declare-lost confirm itself (same rule as ordinary loans in `loans.md`), and Central tenant has literally NO record of the request/loan at all — not just a masked view. Checking in a declared-lost congressional item from outside the Secure tenant also suppresses `Loan details`/`Patron details` on that check-in row's actions menu. (cases — C812848, C825272, C895640)
15. Requests and Borrowing patron blocks are independent gates in the mediated-request flow — overriding one does not carry over to the other, even for the same patron/item journey. (cases — C831971, C831973)
16. Proxy/Sponsor substitution is never offered during mediated-request creation, regardless of whether the scanned patron has an active proxy relationship. (cases — C624245)

---

## Authoring style (measured 2026-07-23)

Mediated Requests: strongly **`Func` ~94%**, median ~6 steps, `User Journey` ~0%. ECS-by-default — cases assume a Secure requester tenant + Central config, and mix UI flows with edge-patron **API** blocks (batch/mediated creation). Use `Functional`. Preconditions carry the three-tenant setup (Central TLR config + Secure tenant + Member shared item) and the capability set under test; steps walk create → confirm/decline → status, or the API request/response. Capability-boundary cases test each of the 7 capability sets individually (see the capability table).

---

## Known Gaps / Items to Verify

- [x] TestRail case coverage — **corrected**: section 32570 + subsections have substantial 2025 coverage (15+ cases just in the top section); pull more as new scenarios are needed, but do not assume thin coverage going forward.
- [x] Exact Eureka capability-set strings — **confirmed live** (C844200, C692196, 2025), see Capability Sets table above.
- [x] Secure-tenant / ECS setup specifics — **confirmed live** (C692196, 2025): Central (TLR setting) + Secure (requester + app) + member tenant (shared item), see "Three-tenant structure" above.
- [x] Mediated request notices (section 61629) and Mediated request patron blocks (section 74667) — **pulled and confirmed this round** (C692073, C692119, C831971, C831973): see "Patron Notices for Mediated Requests" and "Patron Blocks in Mediated Requests" above.
- [x] The "congressional loan" terminology and cross-tenant Declare-lost mechanics — **generalization confirmed** (C895640, blind-generate/diff validation round, 2026-07-22): a 3rd oLOAN-subsection (57628) case, sampled independently, matched the predicted $0-auto-close behavior exactly and surfaced two new confirmed nuances (Central has zero oLOAN records, not just a masked view; Check-in row actions menu is also masking-suppressed). 7 more oLOAN-tagged cases remain unpulled in section 57628 (renewal-policy-change, claim-returned variants, CSV export) — pull them before writing cases for those specific sub-scenarios.
- [ ] MODTLR-150 (Secure-tenant queue-reorder staleness) and MCBFF-158 (Secure-tenant closed-loan display lag) are both cited as accepted/known limitations in currently-live cases — re-verify they're still open before relying on them, since either could be fixed in a future release and turn the "expected" lag into an actual regression.

> N≥10 audit round (2026-07-22): 14 cases read (C692073, C692119, C831971, C831973, C624245, C630441, C627409, C812848, C825435, C825272, C594453, C651539, C856508, C692201). Resolved the file's last open Known Gap by pulling both the Mediated request notices (61629) and Mediated request patron blocks (74667) subsections. Surfaced substantial new previously undocumented content: Secure-patron-data masking (exact placeholder format + Actions-menu suppression + two accepted cross-tenant staleness quirks), the "congressional loan" terminology and its cross-tenant Declare-lost/Claim-returned lifecycle, the one-way cancel cascade from real Request to Mediated Request, the two-independent-gates nature of Requests vs Borrowing patron blocks, hidden proxy/sponsor UI, and the inactive-user confirm-failure cleanup guarantee. Added 5 new Key Business Rules (12-16).
> Blind-generate/diff validation round (2026-07-22): predicted (before reading) that a $0 Set-cost policy would auto-close a congressional loan the same way it does an ordinary loan per `loans.md` — confirmed exactly against C895640, which also surfaced 2 new masking nuances (Central has zero oLOAN records; check-in row actions menu suppression). Closed the file's last real open Known Gap (congressional-loan generalization); the two remaining items are external-ticket-status re-checks, not undocumented behavior.
