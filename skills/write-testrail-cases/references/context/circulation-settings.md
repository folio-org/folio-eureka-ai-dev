# FOLIO Circulation Settings — Business Logic Context

> Built 2026-07-21 (browser-based). **Exact UI Texts confirmed against `folio-org/ui-circulation/translations/ui-circulation/en_US.json` (2026-07-21).** TestRail: suite 21 section 102 "Circulation" (+ Loan Policies 103, Rules 104, Floating collections 52794) and Permissions → Circulation 169. This file covers **Settings > Circulation**; the runtime circulation apps have their own files (check-in.md, check-out.md, loans.md, requests.md, fees-fines.md). Patron notice *templates and policies* are split into `patron-notices.md`.

---

## What is Circulation Settings

`Settings > Circulation` configures how circulation behaves: **policies** (loan, request, overdue fine, lost item fee, patron notice), **circulation rules** that map patron-group × material-type × loan-type × location → those policies, plus fixed due date schedules, staff slips, request cancellation reasons, title-level-request config, loan anonymization, and check-in/out "other settings". Everything the Check out / Check in / Requests / Loans / Fees-fines apps do at runtime is driven by these settings.

Settings groups (left nav): `General`, `Loans`, `Fee/fine`, `Patron notices`, `Requests`.

---

## Circulation rules (the mapping engine)

`Settings > Circulation > Circulation rules` — a text editor mapping **criteria** to **policies**. Criteria: `Patron groups`, `Material types`, `Loan types`, `Locations` (`Institution`/`Campus`/`Library`/`Location`), with `ANY`, `All`, `! (not)`. Policies assigned per rule: `Loan policies`, `Request policies`, `Patron notice policies`, `Overdue fine policies`, `Lost item fee policies`. A **fallback-policy** line matches everything; more specific rules win. Save toast: `Rules were successfully updated.`

### Exact editor grammar [confirmed — C651, C654, C401724; resolves prior Known Gap]

- **Attribute (criteria) prefix letters**, before the `:`: `g` Patron groups, `m` Material types, `t` Loan types, `a` Institutions, `b` Campuses, `c` Libraries, `s` Locations. Typing at a new line auto-suggests these letters; selecting one then shows a value-picker populated from that attribute's actual configured records.
- **Policy prefix letters**, after the `:`, one per policy type in the SAME line: `l` Loan policy, `r` Request policy, `n` Patron notice policy, `o` Overdue fine policy, `i` Lost item fee policy — e.g. `m DVD : l one-hour r allow-all n send-no-notices o overdue-fine-policy i lost-item-fee-policy`. Typing `:` after a selected attribute value shows the policy-TYPE dropdown (Loan/Request/Patron notice/Overdue fine/Lost item fee policies); selecting a type then shows the actual configured policies of that type.
- **A rule is incomplete unless ALL FIVE policy types are present on that line.** Attempting to Save an incomplete rule shows: `Must contain one of each policy type, missing type [next expected policy type from drop down list]` — the message names the specific missing type.
- Other malformed syntax (missing comma between multiple criteria values, missing policies, incorrect line indentation, a criteria conjunction missing its `+` sign) all block Save with an error message.
- **Comments**: lines starting with `#` are supported and are matched by the editor's own "filter rules" search field. The filter treats special characters LITERALLY, not as regex — `*`, `?`, `\`, and `[` were each confirmed to correctly filter to only the comment line containing that exact literal character.
- On successful Save, a "Last updated" stamp (date + updating user's name) appears top-left of the rules editor pane, alongside the `Rules were successfully updated.` toast.

---

## Policies

### Loan policy [confirmed]
Accordions `General information`, `Loans`, `Renewals`. Key fields: `Loan policy name`, `Description`, `Loanable`, `Loan profile` (`Fixed` / `Rolling`), `Loan period`, `Fixed due date schedule`, `Closed library due date management` (short-term: `Keep the current due date/time` / `Move to the end of the current service point hours` / `Move to the beginning of the next open service point hours`; long-term: `Keep the current due date` / `Move to the end of the previous open day` / `Move to the end of the next open day`), `Grace period`, `Item limit`, `Hold shelf expiration period`, `For use at location`. Renewals: `Renewable`, `Unlimited renewals`, `Number of renewals allowed`, `Renew from` (`System date` / `Current due date`), `Renewal period different from original loan`, alternate periods for existing requests / renewals. Delete guard: `Cannot delete Loan policy` / `This policy cannot be deleted, as it is in use by one or more records.`

### Request policy [confirmed]
`Request policy name`, `Description`, `Request types allowed` (Page/Hold/Recall), pickup: `Allow all pickup service points` / `Allow some pickup service points` (`Please select at least one service point`). Errors: `A request policy with this name already exists`. Delete guard: `Request policy cannot be deleted` / `This request policy is used by circulation rules and it cannot be deleted`.

### Overdue fine policy [confirmed]
`Overdue fine policy name`, `Overdue fine` (amount `per` interval), `Count closed days/hours/minutes`, `Maximum overdue fine`, `Forgive overdue fine if item renewed`, `Overdue recall fine`, `Ignore grace periods for recalls`, `Maximum recall overdue fine`. Plus **Reminder fees** (sequence, interval, frequency, fee, notice method/template, `Clear patron block when paid`, `Allow renewal of items with reminder fee(s)`). Validation e.g. `Maximum overdue fine must be greater than or equal to Overdue fine`.

### Lost item fee policy [confirmed]
`Lost item fee policy name`, `Items aged to lost after overdue`, `Patron billed after aged to lost`, `Charge amount for item` (`Actual cost` / `Set cost`), `Lost item processing fee` (+ charge-if-declared-by-patron / aged-by-system), `Replacement allowed`, `Replacement processing fee`, `If lost item returned or renewed …`, `No fees/fines shall be refunded if a lost item is returned more than … late`, recall variants (`Recalled items aged to lost after overdue`). Many cross-field validations.

### Fixed due date schedules [confirmed]
`Fixed due date schedule name`, `Description`, schedule rows `Date from`/`Date to`/`Due date`. Validations: `Date range {n1} cannot overlap with date range {n2}`, `To date must be after from date`, `Due date must be on or after to date`, `At least one schedule must be entered`. Delete guard: `Schedule cannot be deleted when used by one or more loan policies.`

---

## Closed Library Due Date Management — Exact Resulting Due Date [confirmed — C829892, C844248; expands prior field-only listing]

Verified directly via the resulting Loan-details "Due date" field (not just the setting's existence):
- **Short-term** loan, option = `Move to the end of the current service point hours`, calculated due date falls during the service point's CLOSED hours ⇒ due date is truncated EARLIER to the END TIME of the current (checkout) day's open hours — the loan is effectively shortened to fit within that day, not pushed to a later day.
- **Long-term** loan, option = `Move to the end of the previous open day`, calculated due date falls on a day the service point is closed ⇒ due date moves BACKWARD to 11:59 PM of the closest PRIOR day the service point was open.
- **Short-term** loan, option = `Move to the beginning of the next open service point hours`, calculated due date falls during CLOSED hours ⇒ confirmed directly (previously only inferred by symmetry): due date pushes LATER to the start of the next open period. If the policy's `Opening time offset` field is also set (e.g. `1 minute`), that offset is ADDED on top of the next-open start time — a policy with offset = 1 minute and next-open-hours starting 11:00 AM produces due date 11:01 AM, not 11:00 AM exactly. Don't treat "beginning of next open hours" as offset-free; the offset field independently shifts the result and must be included in the expected-value calculation. (cases — C831956)
- The "end of the next open day" (long-term) symmetric option is still not independently re-fetched — continue treating that one specifically as a high-confidence inference pending direct verification.

## Floating Collections [previously undocumented — C605980, C605981]

A Location can be flagged "Floating enabled" and tied to one or more specific service points.
- Checking in an item at a service point whose CURRENT location has floating enabled: item status → `Available`, and BOTH the item's Temporary location AND Effective location update to that check-in service point's floating-enabled location — the item "floats" to wherever it was returned instead of needing to transit home.
- Checking in the same kind of item at a service point that has NO location with floating enabled: item status → `In transit` instead, and Temporary/Effective location remain UNCHANGED (still the original floating location).
- **An open request on the item overrides floating entirely** (confirmed live, C605982 — blind-generate/diff validation round, 2026-07-22): checking in a floating-enabled item at a floating-enabled-location service point, when an open item-/title-level request with a DIFFERENT pickup service point exists, produces item status `In transit to {pickup SP}` — NOT `Available` — and BOTH Temporary and Effective location stay UNCHANGED at the item's pre-check-in location (no floating relocation happens at all). Request fulfillment takes priority over floating outright; a case exercising floating must always state whether an open request exists, since its presence changes the outcome from "floats to check-in location" to "routes to pickup location, no relocation."

## "For Use At Location" (Reading-Room Circulation) [previously undocumented beyond a bare field name — C870003, C869999, C1307935, C916267]

A full feature for items that circulate only within the library (e.g. reading-room use), distinct from a normal checkout.

**Setup** (three linked configs):
1. A Loan policy with the `For use at location` checkbox ticked (Loans section) — requires a `Hold shelf expiration period` (days/weeks/months) to be filled in.
2. A dedicated Loan type created in Inventory settings (e.g. named "For use at location").
3. A Circulation rule mapping that Loan type (and/or a dedicated patron group) to the For-use-at-location Loan policy — same `l`/`r`/`n`/`o`/`i` syntax as any other rule.

**Per-service-point default**: Settings > Tenant > Service points > Edit > `Default check-in action for use at location` dropdown. This default is NOT sticky at the app level — navigating away from Check-in and back always redisplays the service point's configured default, even if a different value was temporarily selected in the current Check-in session.

**Check-in behavior** depends on the service point's configured default:
- If default = a specific action (e.g. "Keep on hold shelf"), that action applies silently on check-in.
- If default = **"Ask for action"**: scanning a checked-out For-use-at-location item pops a confirmation modal titled `For use at location` with body `Item {title} ({material type}) (Barcode: {barcode}) is for use at location at {service point}.` and exactly three buttons: `Cancel`, `Close loan and return item`, `Keep on hold shelf`.
  - `Cancel`: aborts, nothing changes, item remains checked out/In use.
  - `Keep on hold shelf`: the loan stays OPEN (not closed); circ action becomes `Held`; Check-in results show Status = "Checked out" and "For use at location" column = "Keep on hold shelf".
  - `Close loan and return item`: the loan CLOSES; item status → `Available`; "For use at location" column = "Close loan and return item".

**Circ-action lifecycle**: a For-use-at-location item's own two special circ actions are **`In use`** (checked out, actively in use) and **`Held`** (checked back in but kept on the hold shelf rather than fully returned) — cross-references circulation-log.md's already-confirmed translation-key mapping (`Picked up for use at location` → `In use`, `Held for use at location` → `Held`). The Users app's Loans accordion surfaces these as sub-counts alongside the overall open-loan count, e.g. `2 open loans` / `Use at location` / `Held: 1` / `In use: 1`, and the Open-loans table's own "Use at location" column shows `In use in {service point}` or `Held in {service point} until {date time}`.

---

## Other Settings [confirmed]

- **Check out scanning**: `Patron id(s) for checkout scanning` (`Barcode`, `External system ID`, `FOLIO record number (ID)`, `Username`); `Users custom fields to display at Check out`.
- `Enable audio alerts` (+ `Select audio-alerts theme`: Classico/Moderna/Futura).
- `Automatically end check in and check out session after period of inactivity` (`Timeout duration` minutes).
- `Perform wildcard lookup of items by barcode in circulation apps (Check in, Check out)` — enables the Select item wildcard modal in check-in/out.
- **Request management**: recalls (`Recall return interval`, `Minimum guaranteed loan period for recalled items`, `Allow recalls to extend due dates for overdue loans`), holds (`Alternate loan period at checkout for items with an active, pending hold request`, `Allow renewal of items with an active, pending hold request`).
- **Loan anonymization** (`Anonymize closed loans` never/interval; `Treat closed loans with associated fee/fines differently`; per-payment-method exceptions).
- **Staff slips** (`Staff slip name`, `Template content`, tokens for Item/Borrower/Request/Requester/Staff slip/Effective location; `Hold`, `Transit`, etc.; `Maintained as raw HTML?`).
- **Request cancellation reasons** (`Cancel reason`, `Description (internal)`, `Description (public)`).
- **Title level requests (TLR)**: `Allow title level requests`, `"Create title level request" selected by default`, notice templates (Confirmation/Cancellation/Expiration), `Fail to create title level hold when request is blocked by circulation rule`; guard `Cannot change "Allow title level requests"` / `… in use by one or more requests`. **Consortium TLR**: `Enable consortium title level requests (TLR)`.
- **Print hold requests** / **View print details** (Pick slips) toggles.

---

## Capability Sets (Eureka) [confirmed permission display names]

`Settings (Circulation): Can view all circulation settings`, and per-area create/edit/remove + view pairs, e.g.:
`… Can create, edit and remove loan policies` / `… Can view loan policies`; likewise `notice policies`, `patron notice templates`, `request policies`, `overdue fine policies`, `lost item fee policies`, `fixed due date schedules`, `staff slips`, `cancellation reasons`, `other settings`, `circulation rules` (view: `View circulation rules`), `loan history` (view/edit), `Title level request view`/`edit`.

---

## Key Business Rules for Test Cases

1. **Circulation rules resolve policies by most-specific match**; a fallback rule matches everything. The applied loan/overdue/lost-item/notice/request policy for a checkout is whatever the rules select for that patron-group × material-type × loan-type × location. (github + check-out.md)
2. A policy **in use by a circulation rule cannot be deleted** — each policy type shows a distinct "cannot be deleted, in use" guard. (github)
3. Loan `Loan profile` = Fixed uses a fixed due date schedule; = Rolling uses a period; `Closed library due date management` shifts due dates around closed hours/days. (github)
4. `Item limit` on a loan policy caps checkouts for the matched combination — over-limit checkout is blocked (see check-out.md item-limit messages). (github + check-out.md)
5. Overdue fine policy accrues `Overdue fine` per interval up to `Maximum overdue fine`; recalls can use separate recall-fine settings; reminder fees add a scheduled escalation. (github)
6. Lost item fee policy drives automatic charges (aged-to-lost, lost item fee, processing fee) and their refund/adjustment on return/renew/replace — the source of fees-fines automatic charges. (github + fees-fines.md)
7. Request policy `Request types allowed` gates which of Page/Hold/Recall a patron may place for the matched combination; pickup service points can be restricted. (github + requests.md)
8. Enabling `Allow title level requests` cannot be turned off while TLRs exist; Consortium TLR requires base TLR enabled first. (github)
9. `Perform wildcard lookup …` and session-timeout are tenant-wide check-in/out behaviours set here, not per policy. (github + check-in.md)
10. Loan anonymization timing (immediately/interval after close, with fee/fine exceptions) is configured here and executed by a scheduled process. (github + loans.md)
11. A circulation rule line is valid only when it contains exactly one criteria expression plus all five policy-type letters (`l r n o i`); missing any policy type blocks Save with a message naming the specific missing type. (cases — C651, C654)
12. The rules editor's "filter rules" search treats special characters as literal text, not regex, including inside `#`-prefixed comment lines. (cases — C401724)
13. Closed Library Due Date Management options that reference "current"/"previous" move the due date EARLIER (truncating the loan), while options referencing "next" move it LATER — verify the exact direction per option name rather than assuming a single universal behavior. (cases — C829892, C844248)
14. Floating collections update an item's Temporary AND Effective location to the check-in service point only when that service point's current location has floating enabled; otherwise the item goes `In transit` with location unchanged. **An open request on the item overrides this outright** — the item routes `In transit to {pickup SP}` with location left unchanged, regardless of whether the check-in service point's location has floating enabled. (cases — C605980, C605981, C605982)
15. "For use at location" items introduce a distinct two-state lifecycle (`In use` while checked out, `Held` when kept on the hold shelf after check-in) that is separate from ordinary Checked out/Available status, governed by a per-service-point default check-in action (including an interactive "Ask for action" mode with its own 3-button modal). (cases — C870003, C869999, C1307935, C916267)

---

## Authoring style (measured 2026-07-23)

Circulation Settings: **`Other` ~69%** / Func ~31%, median **~3 steps** (short), `User Journey` ~10%. Most cases are compact settings-config checks (loan/request/overdue/lost-item policies, circulation rules, fixed due date schedules, staff slips, TLR, cancellation reasons). Use `Other` for pure config/display; `Functional` where the setting drives a computed runtime effect verified downstream (e.g. closed-library due-date recalculation). Heavy circulation-rule setup lives in Preconditions; steps stay short. Some cases carry `User Journey = Yes` when a setting is exercised through a Check-out/Check-in outcome.

---

## Known Gaps / Items to Verify

- [x] TestRail Circulation cases (sec 102/103/104, plus Floating collections 52794 and For-use-at-location 72019) — **pulled this round** (14 cases): rules-editor grammar, Closed-library-due-date exact mechanics, Floating Collections, and the full For-use-at-location feature are now documented above.
- [ ] Exact Eureka capability-set strings — permission display names confirmed; verify capability-set form in env.
- [x] Circulation-rules **editor grammar** — **confirmed** (C651, C654, C401724): see "Exact editor grammar" above for the full `g/m/t/a/b/c/s` criteria and `l/r/n/o/i` policy letter mapping, incomplete-rule error text, and literal-character filter behavior.
- [x] The "beginning of the next open service point hours" (short-term) Closed-Library-Due-Date option — **confirmed** (C831956, random spot-check 2026-07-23): pushes due date LATER as predicted, PLUS revealed the `Opening time offset` field adds on top of the next-open start time. The long-term "end of the next open day" counterpart remains an unverified symmetry-based inference.
- [x] Whether Floating collections behavior changes when active requests exist on the item/instance — **resolved** (C605982, blind-generate/diff validation round, 2026-07-22): an open request overrides floating outright, see "Floating Collections" section above.

> N≥10 audit round (2026-07-22): 14 cases read (C651, C654, C196833, C196834, C401724, C605980, C605981, C829892, C844248, C870003, C869999, C1307935, C916267, C9293). Resolved both open Known Gaps (TestRail cases pulled; rules-editor grammar fully captured with exact letter codes and error text). Surfaced two entirely new, previously undocumented feature areas: Floating Collections and "For Use At Location" (reading-room circulation) with its full setup chain, per-service-point default check-in action, the 3-button "Ask for action" modal, and the In-use/Held lifecycle. Also expanded Closed Library Due Date Management from a bare field list to exact resulting-due-date mechanics for two of its four option combinations. Added 5 new Key Business Rules (11-15).
> Blind-generate/diff validation round (2026-07-22): predicted (before reading) that an open request would override floating and route the item to the pickup SP without relocating it — confirmed exactly against C605982. Closed the file's last open Known Gap.

> Random spot-check (2026-07-23): picked one fresh uncited case at random from section 102/103/104's 42-case tree (C831956) — confirmed the previously-inferred "beginning of next open hours" due-date direction AND found the undocumented `Opening time offset` field, which adds to that calculated due date.
