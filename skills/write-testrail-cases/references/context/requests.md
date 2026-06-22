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

### Frequently Observed Messages

| Condition | Message text | Source |
|---|---|---|
| CSV export requested | A CSV results report is being generated. This may take some time for larger result sets. Please be patient. | [from cases] |
| Request policy created | The Request policy ** was successfully created. | [from cases, verify in env] |

TestRail extraction for toast text in this area is noisy because several newer cases assert translation keys or API field values rather than rendered text. Prefer validating exact toast wording in the tenant before adding strict text assertions for new manual cases.

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

### Batch requesting verification

```text
Action:   Create multiple requests through Patron Services / edge-patron batch requesting.
Expected: Requests are created only up to the configured patron and item limits, and ECS / mediated variants respect their tenant-specific rules.
```

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

---

## Known Gaps and Verification Notes

- Focus-release slice is present, but Umbrellaleaf-tagged cases were not found in this subtree during this run; recent signal comes primarily from Trillium, Sunflower, and Ramsons.
- TestRail toast extraction for Requests is noisy because several cases assert translation tokens or backend field names instead of final rendered text. Verify toast wording in tenant before writing strict expected results.
- GitHub and Jira enrichment for this run was limited, so release-focused emphasis is derived mainly from TestRail titles and the stable docs workflow model.
- Circulation-settings capability names related to request-printing settings should be re-validated in Eureka before using them in new cases.