# FOLIO Requests App — Business Logic Context

> Generated/refreshed by the build-app-context workflow on 2026-06-17.
> Sources:
> - TestRail section subtree rooted at section_id=96 (suite_id=21): sections 96, 343, 870, 1134, 1527, 2013, 17479, 29720, 93820, 34771
> - TestRail coverage: 162 cases total in subtree; 44 cases tagged to focus releases Umbrellaleaf, Trillium, Sunflower, Ramsons
> - GitHub signal scan: folio-org/ui-requests plus public repo metadata for requests-related modules
> - Jira/component signal was not refreshed in this run; rely on TestRail + docs-derived business rules below
> Strings marked [from cases] are mined from TestRail corpus.
> Strings marked [from source, verify in env] come from docs or limited source signal and should be validated in the target tenant UI before strict assertions.

---

## What is Requests

The Requests app allows library staff to create and manage patron requests for items. FOLIO supports item-level requests on a specific item and title-level requests on an instance, where the system selects the item that should satisfy the request.

Requests drive the retrieval, transit, hold shelf, delivery, and fulfillment workflows. The app also exposes queue management, request notices, CSV exports, and request-printing flows that are reflected in the existing TestRail corpus.

> **Identifier convention for this area:** write circulation cases with **symbolic placeholders the executor fills at run time** — `service point S` / `S1`, `<barcode>`, `<title>`, `<requester>` — not invented concrete values. Do NOT fabricate a specific barcode or a named service point; concrete values only when the exact value is itself under test.

---

## Key Terms

| Term | Definition |
|---|---|
| Item-level request | A request placed against a specific item record |
| Title-level request | A request placed against an instance; FOLIO chooses the filling item |
| Page request | Request used when an item is currently available |
| Hold request | Request used when an item is not currently available |
| Recall request | Urgent request for a not-available item; may shorten the current loan due date |
| Pickup service point | Service point where the patron collects the item |
| Retrieval service point | Service point associated with retrieving the requested item; recent focus-release coverage adds UI, filter, export, and ECS checks around this field |
| Hold shelf expiration date | Date after which an awaiting-pickup request becomes pickup expired |
| Request expiration date | Optional date after which an open not-yet-filled request becomes unfilled |
| Hold shelf clearance report | Report listing expired or cancelled hold-shelf requests whose items need re-shelving |
| Batch requesting | Patron services workflow for creating multiple requests in one operation |

---

## Record Hierarchy / Architecture

```text
Instance
└── Holdings
    └── Item
        └── Request queue
            ├── Item-level requests
            └── Title-level requests associated back to the instance

Related records and services:
- User / requester record
- Pickup service point
- Retrieval service point
- Request policy and circulation rules
- Check in / Check out / mod-patron / title-level request services
```

---

## Lifecycle / Workflow

```text
Open - Not yet filled
  -> Open - In transit
  -> Open - Awaiting pickup
  -> Closed - Filled

Open - Not yet filled
  -> Open - Awaiting delivery
  -> Closed - Filled

Open - Not yet filled
  -> Closed - Cancelled
  -> Closed - Unfilled

Open - Awaiting pickup
  -> Closed - Filled
  -> Closed - Cancelled
  -> Closed - Pickup expired
```

| Status | Description |
|---|---|
| Open - Not yet filled | Request exists and has not yet been routed to the next fulfillment stage |
| Open - In transit | Item has been checked in and is moving to the pickup service point |
| Open - Awaiting pickup | Item is on hold shelf at the pickup service point |
| Open - Awaiting delivery | Delivery request was closed at check in without immediate checkout |
| Closed - Filled | Patron received the item through hold shelf checkout or close-and-check-out delivery flow |
| Closed - Cancelled | Request was cancelled by staff or patron |
| Closed - Pickup expired | Hold shelf expiration passed before pickup |
| Closed - Unfilled | Request expiration passed while still open and not yet filled |

Important exception: Open - Awaiting pickup is governed by the hold shelf expiration date, not the request expiration date.

---

## Main Sections / UI Structure

### Panes

- Requests [from cases]
- Search & filter [from cases]
- Request details [from cases]
- Request Detail [from cases, verify in env]
- Notes [from cases]

### Accordions

- Staff notes [from cases]
- Requester information [from cases, verify in env]
- Loan and availability [from cases, verify in env]
- Requests [from cases, verify in env]

### Key Navigation Paths

- Requests > Search & filter [from cases]
- Requests > Actions > New [from source, verify in env]
- Requests > Request details > Actions > Move request [from source, verify in env]
- Requests > Request details > Actions > Reorder queue [from source, verify in env]
- Requests > Actions > Export search results to CSV [from source, verify in env]
- Requests > Actions > Print pick slips [from source, verify in env]
- Requests > Actions > Print hold request search slips [from source, verify in env]

---

## Exact UI Texts

> Use these verbatim in expected results only after validating the target tenant when a string is marked verify in env.

### Modal / Dialog Titles

| Modal | Trigger | Source |
|---|---|---|
| Awaiting pickup for a request | Check in flow when item reaches hold shelf | [from cases] |
| Confirm request cancellation | Cancel an open request | [from cases] |
| Select item | Item/title selection workflows | [from cases] |
| Select request type | Request type resolution when multiple types are possible | [from cases] |
| Route for delivery request | Check in flow for delivery requests | [from cases] |
| New request | New request workflow | [from cases, verify in env] |
| Request not allowed | Blocked request workflow | [from cases, verify in env] |
| Are you sure? | Generic confirmation dialog | [from cases] |

### Button Labels (key actions)

Actions, Save & close, Save, Edit, Search, Reset all, New, Confirm, Cancel, Continue, Print [from cases]

### New Request form — fields (confirmed C542, C545)

`Item barcode` field, `Requester barcode*` field, `Request Type*` dropdown (options: `Page`, `Hold`, `Recall` — which appear depends on item status), `Fulfillment preference` (Hold shelf / Delivery), `Pickup service point*` dropdown. Request types offered depend on item status: an Available item offers `Page`; a checked-out item offers `Hold` / `Recall`.

**Requester lookup works even without a barcode (confirmed, C10956):** a patron with no barcode on their record must still be selectable and submittable as the requester via the `Requester` lookup (name/other identifier search), not just via the barcode field — this was a past regression (`UIREQ-444`/`UIREQ-849`, "Unable to select requester without barcode" / "Cannot submit a request with a user without barcode"). Include a barcode-less-patron scenario when testing request creation, don't assume every requester has one.

### Empty-field display convention: literal `-`, never blank (confirmed C680499)

Any field with no underlying data value renders as a literal `-` (dash), never an empty cell — confirmed consistently across multiple, otherwise-unrelated surfaces in one pass: the `Select item` modal's `Barcode` column (both from New-request title-level-item-selection and from `Move request`), the `Reorder queue` page's `Item barcode` and `Requester barcode` columns, and the main Requests results table's `Year`, `Item barcode`, `Effective call number string`, `Requester barcode`, and `Proxy` columns. When constructing test data specifically to exercise "missing field" display, create the item/user with only required fields and assert `-` in each of these locations rather than assuming an empty string or blank cell.

### Search & filter — filter accordions (confirmed C540, C541)

`Request type`, `Request status`, `Request level`, `Tags`, `Pickup service point`. Empty-result message: `No results found. Please check your filters.` `Reset all` clears all filters; filters persist across app navigation.

### Staff-slip token editing (confirmed C543, C544)

`Add token` modal (opened via the `{ }` icon in the Template content section); tokens land in the `Display` text field. Token syntax is `{{token.name}}`, e.g. `{{requester.firstName}}`, `{{requester.lastName}}`, `{{item.title}}`, `{{item.barcode}}`, `{{item.effectiveLocationSpecific}}`.

### Toast messages (confirmed — `ui-requests/en_US.json`, 2026-07-21)

| Event | Toast text |
|---|---|
| Request created | `Request has been successfully created for {requester}` |
| Request create failed | `This request was not placed successfully` |
| Request edited | `Request has been successfully edited for {requester}` |
| Request edit failed | `This request was not saved successfully` |
| Request duplicated | `Request has been successfully created for {requester}` |
| Request moved | `Request has been moved successfully` |
| Queue reordered | `Queue was successfully updated` |

### Request-not-allowed / validation errors (negative-case gold — confirmed)

| Condition | Message text |
|---|---|
| Only checked-out can be recalled | `Only checked out items can be recalled` |
| Only checked-out can be held | `Only checked out items can be held` |
| Hold not allowed for patron+title | `Hold requests are not allowed for this patron and title combination` |
| No request type available (title) | `None available for this title and patron combination` |
| No request type available (item) | `None available for this item and patron combination` — appears **inline under the `Request type` dropdown**, not as a toast; confirmed triggers include item statuses `Withdrawn`, `Declared lost`, `Claimed returned`, and `Lost and paid` (verify each individually — C9193, C10931) |
| Requester already has item on loan | `This requester already has this item on loan` |
| Requester already has loan for one of instance's items | `This requester already has a loan for one of the instance's items` |
| Requester already has open request for item | `This requester already has an open request for this item` |
| Requester already has open request for instance | `This requester already has an open request for this instance` |
| SP is not a pickup location | `Service point is not a Pickup location` |
| Hold-shelf needs pickup SP | `Hold shelf fulfillment requests require a Pickup service point` |
| Request already closed | `Error: The Request has already been closed.` |
| User cannot be proxy for self | `User cannot be proxy for themselves` |
| Item barcode not found | `Item with this barcode does not exist` |
| User barcode not found | `User with this barcode does not exist` |
| Instance HRID/UUID not found | `Instance with this HRID or UUID does not exist` |
| Requester is Inactive | Toast `This request was not placed successfully`; modal `Request not allowed` body `Inactive users cannot make requests.`, `Close` button (confirmed: both `Close` and the `X` icon dismiss it; neither creates the request) — applies to Page, Hold, and Recall alike (C1385311/C1385312, item- and title-level) |

### Cancel-request modal (confirmed, incl. field-gating detail from C3533)

`Confirm request cancellation` heading; body `<b>{title}</b> will be <b>cancelled</b>`; fields `Reason for cancellation`, `Notify patron`, `Additional information for patron`. Blocked-request modal: heading `Patron blocked from requesting`, `Reason for block`, `View block details`, `Request not allowed`.

**Patron-block override on request creation — confirmed details (C170385):** the modal shows at most **3 blocks** even if the patron has more. Closing the modal (without overriding) does NOT let the request save — clicking `Save & close` again re-triggers the same block modal; only `Override` clears the gate. **There is no comment field on this override** (unlike Check-out/Renewal override, which requires a comment) — the team's own case notes this as a deliberate current asymmetry ("future development planned to add a comment during override"). Don't write a case that expects a required-comment step here; that belongs to check-out.md/loans.md's override patterns, not this one.

**Field-gating logic (confirmed, C3533):** `Reason for cancellation` options come from `Settings > Circulation > Request cancellation reasons`. Once **any** reason is selected, the `Additional information for patron` free-text field appears — but it's only **required** when the reason is `Other`; for every other reason it's optional. `Confirm` stays disabled only when reason = `Other` and the text field is empty; for any other reason `Confirm` is enabled as soon as a reason is picked. `Back` closes the modal without cancelling. Don't write a case that requires text for every reason, or that never shows the field for non-Other reasons — both are wrong.

### Patron comments on a request (confirmed, C199704–C199708 family — previously undocumented)

`Patron comments` is a free-text field on the `New request` form, fillable at creation time only — once the request is saved, re-opening it via `Actions > Edit` shows the same field but **uneditable** (write-once from the UI). Real coverage of this feature spans five distinct surfaces the team tests separately — treat each as its own scenario, not one combined case:
1. **Creation**: field appears on `New request`, accepts any text, persists on save (C199704).
2. **CSV export**: patron comment column is included in the Requests CSV export (C199705).
3. **Hold shelf clearance report**: patron comment appears in that report's row for the request (C199706).
4. **Staff slip token**: the token is `request.patronComments` (Settings > Circulation > Staff slips > token picker `{}`) and must be configured and verified separately in **all three** applicable templates — `Hold`, `Pick Slip`, and `Request Delivery` — each triggered by a different check-in flow (Hold: "Awaiting pickup for a request" modal → print slip; Pick Slip: Requests app "Print pick slips for `<service point>`"; Request Delivery: "Route for delivery request" modal → print slip). Don't test only one slip type and assume the others work the same way (C199707).
5. **Check-in "Awaiting pickup for a request" modal**: when checking in the item, the modal shown at that point displays the patron comment associated with the request (C199708) — this is a cross-app effect landing in Check In, verify it there per this skill's "verify effects at their real destination" rule.

### Move request / reorder queue (confirmed)

`Move request` action opens the `Select item` modal, which must list **every requestable/available item on the Instance** — this was a past regression when an Instance has **more than 10 holdings**: pagination/limit bugs caused some requestable items to be silently missing from the list (`UIREQ-929`). When testing Move Request on a multi-holdings Instance, use 10+ holdings and assert the full item set appears, not just that the modal opens (C388490). `Select request type`; second-position message `Requests cannot be moved above page requests, even when fulfillment has not begun. This request will be moved to position 2 in the request queue.` Reorder confirm: `Move to position 2` / `Requests cannot be displaced from position 1 when fulfillment has begun.`

> `No results found. Please check your filters.` (empty filter results) is a shared stripes component string, confirmed from cases C540/C541.

---

## Status Values

### Request status

Open - Not yet filled, Open - In transit, Open - Awaiting pickup, Open - Awaiting delivery, Closed - Filled, Closed - Cancelled, Closed - Pickup expired, Closed - Unfilled

### Request type

Page, Hold, Recall

---

## Capability Sets (Eureka)

Curated capability set list for Requests authoring:

| Action | Capability Set |
|---|---|
| View requests | `Data - UI-Requests - View` |
| View and create requests | `Data - UI-Requests - Create` |
| View, edit, and cancel requests | `Data - UI-Requests - Edit` |
| All request functions | `Data - UI-Requests - Manage` |
| Move request to another item | `Procedural - UI-Requests MoveRequest - Execute` |
| Reorder queue | `Procedural - UI-Requests ReorderQueue - Execute` |
| Title look-up while creating title-level requests | `Data - UI-Inventory Instance - View` |

Observed older cases also reference circulation settings permissions around print-hold-requests and search-slip settings. Where those settings are part of the scenario, verify the current Eureka capability-set names in tenant before using them verbatim.

---

## Common Verification Patterns

### Request status transition verification

```text
Action:   Complete the request workflow step that moves the request forward.
Expected: Request details show the exact updated Request status value and the item status reflects the same fulfillment stage.
```

### Retrieval service point list-column verification

```text
Action:   Add the Retrieval service point column or apply the Retrieval service point filter in the Requests result list.
Expected: The result list displays the Retrieval service point value correctly for item- and title-level requests, and filtering/sorting/export use the same value consistently.
```

### Request export verification

```text
Action:   Run Actions > Export search results to CSV from a filtered Requests result set.
Expected: The generated CSV contains the visible request data plus additional request/item fields, including Retrieval service point when that column is part of the tested release scope.
```

### Delivery-route verification at check in

```text
Action:   Check in an item with Delivery fulfillment and choose one of the Route for delivery request dialog options.
Expected: Close and check out changes the request to Closed - Filled; Close changes the request to Open - Awaiting delivery.
```

### Batch / multi-item requesting — API (confirmed C1292036, C1301731; refs MODPATRON-253, MODREQMED-161)

Batch (a.k.a. multi-item) requesting is an **edge-patron API flow**, not a UI screen — cases are Postman-style: method / URL / headers / body, and the expected result is the response code + body fields. Steps and preconditions are written as bulleted API blocks.

- **Create a batch request:** `POST {{host}}/patron/account/{userId}/instance/{instanceId}/batch-request`, header `X-Okapi-Tenant = {tenantId}`, body:
  ```json
  { "patronComments": "...", "requests": [ { "itemId": "...", "pickUpLocationId": "..." }, { "itemId": "...", "pickUpLocationId": "..." } ] }
  ```
  A successful response returns each request line; in a Secure tenant each line carries `"mediatedRequestStatus": "Pending"` (batch requests placed in the Secure tenant are mediated). Retrieve a patron's batch requests via `GET {{host}}/patron/account/{userId}` with the batch include parameter.
- **Max items per batch is a configurable setting**, per Member tenant, via `POST /settings/entries` (create, 201) / `PUT /settings/entries/{settingId}` (update, 204): `{ "scope": "mod-requests-mediated.manage", "key": "multiItemBatchRequestItemsValidation", "value": { "maxAllowedItemsCount": N } }`. A batch exceeding `maxAllowedItemsCount` is rejected; raising the value then re-sending the same batch succeeds — so a limit case sets the value low, exceeds it, then raises it and retries.
- **Preconditions pattern for these ECS batch cases:** `Allow title level requests` checked in Central + Member + Secure, `Enable consortium title level requests (TLR)` checked in Central with no tenants in `Exclude tenants`; a Shared instance created in Central with a Holding in a Member tenant; ≥2 items whose material/loan types are shared. ECS variants repeat the call swapping the `userId` in the path and the `X-Okapi-Tenant` header for Member / Secure tenants.
- Related: `Create Mediated batch request for Secure patron via edge-patron` (C1250456) and `Create non-ECS batch requests via edge-patron` (C1322897) are the mediated and non-ECS variants of the same POST flow.

---

## ECS / Multi-Tenant Notes

Requests subtree section 96 includes ECS-specific focus-release coverage. Recent Sunflower and Trillium cases cover:

- Retrieval service point column behavior for local, ECS, and mediated item/title-level requests [from cases]
- Batch ECS request creation and mediated secure-patron batch request creation via edge-patron [from cases]

When writing ECS requests tests, specify:

- Central tenant versus member tenant ownership of the requester and item
- Starting affiliation and any affiliation switch step
- Whether the flow is local, ECS, mediated, or secure-patron mediated

---

## Release-Focused Signals

Focus-release coverage in section 96 is concentrated in these areas:

1. Retrieval service point UI, filtering, sorting, export, and ECS visibility checks in Ramsons and Sunflower.
2. Requests CSV export edge cases and deleted-requester behavior in Trillium.
3. Batch requesting, patron settings, maximum item limits, and edge-patron API flows in Trillium.
4. Same-patron requests for different items on the same instance, request-policy editing, and request search by normalized ISBN in Ramsons.

This means new manual cases for Requests should give extra attention to retrieval service point behavior, batch requesting, patron-services API coverage, and ECS-mediated variants before adding more legacy core-flow coverage.

---

## Key Business Rules for Test Cases

1. Request type options depend on current item status and circulation rules; not every item can offer Hold, Page, and Recall at once. (docs + cases)
2. Page requests are for available items, Hold requests are for unavailable items, and Recall requests are urgent requests that may shorten the current borrower's due date. (docs)
3. Request expiration date is optional; if it is set and the request remains Open - Not yet filled past that date, the request becomes Closed - Unfilled. (docs)
4. Open - Awaiting pickup ignores the request expiration date and closes only when the hold shelf expiration date passes. (docs)
5. Only open requests can be edited or cancelled; closed requests do not allow those actions. (docs)
6. Cancelling a Page request with no remaining queue returns the item to Available. (docs)
7. Cancelling a request while it is In transit or Awaiting pickup closes the request, but the item status does not change until the item is checked in. (docs)
8. A duplicate request cannot be saved for the same requester and the same item; at least one of those values must change. Recent Ramsons coverage confirms the allowed variant where the same patron requests different items on the same instance. (docs + cases)
9. Moving a request to a loaned target item on the same instance can trigger recall behavior and due-date changes for the current borrower. (docs)
10. Title-level requests require newly added items to be checked in before they can satisfy an existing open title-level request. (docs)
11. Title-level requesting cannot be disabled while open title-level requests exist. (docs)
12. Title-level requests are not supported for multi-volume sets; item-level requests must be used instead. (docs)
13. Delivery fulfillment requires delivery to be enabled on the patron record and a valid delivery address to exist. (docs)
14. Hold shelf clearance report must include cancelled-awaiting-pickup and pickup-expired items that need to be re-shelved. (docs + cases)
15. Page requests cannot be moved above other Page requests during queue reordering. (docs)
16. Reorder queue and Move request are separate capabilities and must be tested independently. (docs)
17. Title look-up for title-level request creation requires inventory instance view capability. (docs)
18. Pickup notices are sent at the end of the check-in session rather than immediately when the item reaches the hold shelf. (docs)
19. Cancellation reason Other requires additional information. (docs)
20. Retrieval service point is now a meaningful verification surface across list columns, filters, sorting, CSV export, printing, and ECS visibility. (cases)
21. Requests export must still succeed when prior printed-request data or deleted-requester data creates edge conditions. (cases)
22. Batch requesting obeys patron settings and multi-item request limits, including ECS and non-ECS edge-patron flows. (cases)
23. Patron-services API flows exist for item-level hold creation, title-level hold creation, cancellation, allowed-service-points resolution, and related request workflows; use API-focused manual cases only when the story explicitly targets those endpoints. (cases)
24. **A `Closed - Cancelled` (or any Closed-*) request has no Edit control anywhere in the UI, but the view still shows every field fully populated** — verify both: the absent edit affordance AND that the closed record's data is still intact/readable, not just one or the other. (cases — C3533)
25. Cancelling a request while `Awaiting pickup` doesn't resolve the item's status immediately — the item stays as-is until the next **check-in**, at which point it resolves per normal queue logic (`Available` if no other requests and the check-in service point matches the item's effective location; `In transit` if it must route elsewhere for reshelving or the next request; `Awaiting pickup` if another request needs the hold shelf). A cancel-while-awaiting-pickup case should include this follow-up check-in step and assert the resulting status, not stop at the cancel toast. (cases — C3533)
26. **An Inactive patron cannot have any new request placed for them** — Page, Hold, and Recall are all blocked identically (`Request not allowed` / `Inactive users cannot make requests.`), for both item- and title-level requests; verify no request record is created after the blocked attempt. (cases — C1385311, C1385312)
27. **Certain item statuses block new request creation outright** (see "No request type available (item)" in the errors table above) — `Withdrawn`, `Declared lost`, `Claimed returned`, and `Lost and paid` all produce the inline `None available for this item and patron combination` message under `Request type` rather than letting the request form proceed; verify each status individually rather than assuming they behave the same as `Checked out`/`Available`. (cases — C9193, C10931)
28. **A recall's due-date truncation and "Item recalled" notice fire only once per loan, on the *first* recall.** When a checked-out item with **zero** existing recalls gets a new recall request: the loan's due date is truncated per the loan policy's recall rules, and the "Item recalled" loan notice is sent to the current borrower — but the "Recall request" *request*-notice is deliberately **not** sent (it's a creation receipt, already implied covered). When a recall request **already exists** in the queue and another recall request is moved onto that same item (e.g. via reordering), the due date must **not** be truncated again and neither notice fires a second time. A recall-notice case must distinguish "first recall on this loan" from "additional recall on an already-recalled loan" — they have different expected outcomes, not the same one twice. (cases — C2368)
29. **Any field with no data renders as a literal `-`, never blank**, across Select-item modals, Reorder-queue, and the main results table — see the dedicated note above. (cases — C680499)
30. **Batch/multi-item requesting is an edge-patron API feature** with a per-Member-tenant configurable item cap (`multiItemBatchRequestItemsValidation` / `maxAllowedItemsCount`) and Secure-tenant mediation (`mediatedRequestStatus: Pending`); write these as Postman-style API cases, not UI flows. (cases — C1292036, C1301731; refs MODPATRON-253, MODREQMED-161)

---

## Authoring style (measured 2026-07-23)

Requests cases split ~53% `Functional` / 45% `Other` (pick per scenario; API/edge-patron flows tend `Functional`), median ~5 steps, `User Journey` flag ~1% (leave `No`). Core UI request flows are compact atomic cases; batch/edge-patron and ECS/mediated flows are API cases with method/URL/header/body blocks. Preconditions group related facts per numbered item (TLR settings in one item, shared-instance+holding in another).

---

## Known Gaps and Verification Notes

- Focus-release slice is present, but Umbrellaleaf-tagged cases were not found in this subtree during this run; recent signal comes primarily from Trillium, Sunflower, and Ramsons.
- TestRail toast extraction for Requests is noisy because several cases assert translation tokens or backend field names instead of final rendered text. Verify toast wording in tenant before writing strict expected results.
- GitHub and Jira enrichment for this run was limited, so release-focused emphasis is derived mainly from TestRail titles and the stable docs workflow model.
- Circulation-settings capability names related to request-printing settings should be re-validated in Eureka before using them in new cases.

> Random spot-check (2026-07-22): picked one fresh uncited case at random (C680499) — no prior rule existed for empty-field display, so this was a genuine blind spot rather than a re-confirmation. Added the dedicated note and Key Business Rule 29.