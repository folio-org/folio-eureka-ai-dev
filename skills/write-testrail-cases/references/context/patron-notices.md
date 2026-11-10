# FOLIO Patron Notices — Business Logic Context

> Built: 2026-07-21 · Delta-refreshed: 2026-11-07 · Release: not recorded · Builder: build-app-context/manual — header normalized 2026-11-07, see area-map.md → Freshness

> Built 2026-07-21 (browser-based). **Exact UI Texts confirmed against `folio-org/ui-circulation/translations/ui-circulation/en_US.json` (2026-07-21).** TestRail: suite 21, parent section **328 "Patron notices"** with children **331 "Patron notices settings"** (notice-template AND notice-policy editor cases — e.g. UICIRC-1355 posted here 2026-08), **17059 "Loan patron notices"**, **17139 "Request notice triggers"**, **17145 "Fees/fines patron notices"**, **111082 "ECS patron notices"**. Two related settings live under `Settings > Circulation > Patron notices`: **Patron notice templates** (the message content) and **Patron notice policies** (which template fires on which event, and when). The runtime effect (a notice landing in the mailbox) is asserted in the circulation apps — see check-in.md / requests.md / loans.md.

---

## What is Patron Notices

Patron notices are automated messages (email or print) sent to patrons/requesters on circulation events. A **template** defines the Subject + Body with **tokens**; a **notice policy** binds templates to **triggering events** with a **timing** and **frequency**; a circulation rule assigns a notice policy to a patron-group × material-type × loan-type × location combination. So a real notice requires: a template + a notice policy referencing it + a circulation rule pointing at that policy + the triggering event occurring.

---

## Patron notice templates [confirmed]

`Settings > Circulation > Patron notice templates`. Fields: `Patron notice template name`, `Active`, `Description`, `Category`, `Email` (delivery), `Subject`, `Body`. New pane: `New patron notice template`; buttons `Save` / `Save new`; `Email or print` / `Print only`.

**Categories:** `Loan`, `Request`, `Manual fee/fine charge`, `Manual fee/fine action (pay, waive, refund, transfer or cancel/error)`, `Automated fee/fine charge`, `Automated fee/fine adjustment (refund or cancel)`.

**Token groups** (`Add token`): `Item`, `User`, `User Address`, `Request`, `Loan`, `Effective location`, `Fee/fine charge`, `Fee/fine action`, plus multiples `Multiple loans`, `Multiple requests`, `Multiple fee/fine actions`, `Multiple fee/fine charges`. Preview: `Preview of patron notice template` (view: `… - {name}`).

**Item-group tokens confirmed live (C692204, 2025, story CIRC-2260/UICIRC-1178 — 7 new item tokens added to the Email template):** `{{item.accessionNumber}}`, `{{item.administrativeNotes}}`, `{{item.datesOfPublication}}`, `{{item.editions}}`, `{{item.physicalDescriptions}}`, `{{item.instanceHrid}}`, `{{item.instanceHridImage}}`. Selecting a token in the `Add token` modal inserts it into the `Display` field of the Template content accordion; `Preview` then shows sample resolved values before save.

**Errors / guards:** `A patron notice with this name already exists`; delete guard `Cannot delete Patron notice template` / `This Patron notice template cannot be deleted, as it is in use by one or more records.`; `This is a predefined notice and cannot be deleted`; subject `Should not begin with a space`.

**Record metadata dropdown [confirmed — C411862]:** the template's Edit pane shows a `Record last updated: {Month/Day/Year time}` dropdown (labeled `Record created` on first save). Expanding it reveals two `Source` fields plus dates: `Record created` (date, frozen forever) with its own `Source` (the creating user's name, or `Unknown user` if migrated), and `Record last updated` with its own `Source` (the user who made the most recent edit). Editing ANY field (name, Active checkbox, Description, Category, etc.) and clicking `Save & close` updates `Record last updated` to the current date/time (tenant timezone) and its `Source` to the editing user's name — `Record created`/its `Source` never change after the initial save.

---

## Patron notice policies [confirmed]

`Settings > Circulation > Patron notice policies`. Accordions: `General information`, `Loan notices - sent to borrower`, `Fee/fine notices`, `Request notices - sent to requester`. Fields: `Patron notice policy name`, `Description`, `Active`. Each notice row (`Add notice`, `Notice {counter}`): `Template`, `Format` (`Email`), `Frequency` (`One Time` / `Recurring`), `Triggering event` (`Send`), timing `Before` / `After` / `Upon/At` (+ `and every` for recurring).

### Triggering events [confirmed]

**Loan notices:** `Loan due date/time`, `Item renewed`, `Check in`, `Check out`, `Loan due date change`, `Item recalled`, `Item aged to lost`, `Hold request for item`.
**Request notices:** `Page request`, `Hold request`, `Recall request`, `Awaiting pickup`, `Hold shelf expiration`, `Request expiration`, `Cancel request`.
**Fee/fine notices:** `Overdue fine, returned`, `Overdue fine, renewed`, `Lost item fee(s) charged`, `Lost item returned - fee(s) adjusted`.

### Send-behaviour notes [confirmed]
- Real time: `Always sent when event is triggered.`
- Conditional: `Always sent when event is triggered and send conditions are met.`
- Postponed/bundled: `Always sent at the end of a session and loans are bundled into a single notice for each patron.`
- Long-term: `Send overnight with multiple loans/items by patron. Useful for long-term loans.`
- Short-term: `Send throughout the day without multiple loans/items. Useful for short-term loans.`

Delete guard: `Cannot delete patron notice` / `This notice policy cannot be deleted, as it is in use by one or more records.`

### Multiples radio options — "Lost item fee(s) charged" event only [confirmed — C385643]

Selecting Triggering event = `Lost item fee(s) charged` uniquely swaps the usual descriptive text for two mutually-exclusive REQUIRED radio buttons (not a dropdown): `Send overnight with multiple lost item fee charges by patron` / `Send throughout the day with one lost item fee charge per notice`. Neither is pre-selected; Save & close is blocked with `Please fill this in to continue` under both radios until one is chosen. Switching the Triggering event away and back to this option clears the radio selection again. Every OTHER triggering event instead shows the plain description text (e.g. `Always sent when event is triggered`) with no radio choice.

### Notice-card reordering controls — "Add notice above" / "Delete notice" [from UICIRC-1355, In Code Review 2026-08 — verify exact labels/tooltips on first execution]

Groundwork for reordering notice cards inside a policy (full drag & drop tracked separately in UICIRC-1372). Each `Notice {counter}` card in the `Loan notices`, `Request notices`, and `Fee/fine notices` accordions carries two per-card icon buttons in its header: a **plus** icon ("Add notice above") to the LEFT of the existing **trash** icon ("Delete notice"). Behavior derived from the story:
- **Plus / Add notice above** inserts a NEW empty notice card DIRECTLY ABOVE the card whose plus was clicked (contrast with the accordion-level `Add notice` button, which appends a card at the BOTTOM). After insertion the `Notice {counter}` labels renumber sequentially top-to-bottom, so an inserted card pushes the ones below it up by one.
- **Trash / Delete notice** removes that specific card; remaining cards renumber. Deleting the last remaining card returns the accordion to its empty state (no `Notice 1` card, only the `Add notice` button).
- The two icons appear on every notice card regardless of accordion and regardless of whether the card is fully filled in or still empty — i.e. present on brand-new (unsaved) policies too, not only on existing/saved ones.
- **View-only / no-edit capability:** whether these controls are hidden vs. merely disabled in read-only mode was NOT confirmed from the story — verify on execution.

> **Known gap — policy-level toasts unverified.** This file confirms *template* toasts (`A patron notice with this name already exists`, `Cannot delete Patron notice template`), but the verbatim success toast for saving/creating/updating/deleting a notice **policy** is not captured here. Do not assert an exact policy-save toast string from memory; verify wording on execution (expected pattern, unconfirmed: `The patron notice policy <name> was successfully updated`).

---

## Patron Notice Template Duplication [confirmed — C396392; previously undocumented]

Actions > Duplicate on an existing template redirects to the "New patron notice template" page, pre-filled with the source's Description and Category and with "Active" checked by default. The Name field is pre-filled with the SOURCE name and immediately shows `A patron notice with this name already exists`, blocking Save & close until renamed to something unique. Before saving, the duplicate-in-progress's own "Record Last update" accordion shows Source = "Unknown user" (this is expected pre-save UI state, not a bug — real usernames display normally once the duplicate is actually saved).

## `loan.additionalInfo` Token — Always Resolves to the Latest Comment [confirmed — C414969]

When a loan has multiple patron/staff comments (see loans.md's "Additional Loan Comments" — new comments mark prior ones "superseded"), the `{{loan.additionalInfo}}` token in ANY notice template — whether the notice is triggered manually/immediately (e.g. Loan due date change) or automatically later (e.g. Loan due date/time reached) — always resolves to only the MOST RECENT, non-superseded comment. Superseded comments are never concatenated or otherwise included in the rendered token value.

## Proxy / Sponsor Notification Routing [confirmed — C784435, C784436, C784437, C784438; previously undocumented]

A proxy relationship record (linking a Sponsor and their Proxy) carries its own "Notifications sent to" field with two mutually exclusive options: **Proxy** or **Sponsor**. This single per-relationship setting governs the delivery target for EVERY notice type — both Loan notices (Check out, Check in, etc.) and Request notices (Page request, Awaiting pickup, Cancel request, Hold request, etc.) triggered by activity performed "acting as proxy for" that sponsor:
- Set to **Proxy**: every such notice is delivered ONLY to the Proxy's mailbox; the Sponsor receives nothing.
- Set to **Sponsor**: every such notice is delivered ONLY to the Sponsor's mailbox; the Proxy receives nothing.
- There is no per-template or per-policy override — the routing is entirely determined by this one relationship-level field, consistently across all notice categories.

## Anonymized Loans — No Circulation-Log Error on Notice Send [confirmed — C729196]

If a notice's timing (e.g. an "After" due-date notice) is still pending when the underlying loan gets anonymized before the notice fires, the eventual attempt to send that notice does NOT produce a "Send error" entry in the Circulation log's Notice-type events for that patron — the notice engine handles the now-anonymized/unlinked loan gracefully rather than surfacing a visible error.

## Overdue-Fine Notice Bundling — Precise Scope [confirmed — C397372, C397373, C397380; refines Key Business Rule 5]

Multiple SEPARATE overdue-fine charges (e.g. from two different items resolved together in one Check-in or Users-app bulk-action session) bundle into a SINGLE notice email via the template's `{{#feeCharges}}...{{/feeCharges}}` loop, as long as they share the SAME triggering-event type — both "Overdue fine, returned" or both "Overdue fine, renewed". This bundling works identically for both "Send = After" and "Send = Upon/At" timing.
- **Critical boundary**: bundling never crosses event-type lines. If one item is renewed ("Overdue fine, renewed") and a different item is separately returned ("Overdue fine, returned") within the same session/timeframe for the same patron, TWO SEPARATE emails are sent — one per triggering-event type — even though both derive from the same notice policy and patron. Test design for bundling must therefore always specify same-vs-different trigger type as a distinct axis, not just "multiple fees, one notice."

## Fee Amount Token — Always 2 Decimal Places [confirmed — C357041]

`{{feeCharge.amount}}` and `{{feeCharge.remainingAmount}}` always render with exactly two decimal places, even when the second digit is a trailing zero (e.g. `110.90`, never `110.9` or `111`). This formatting is identical between the Loan-details "Fees/fines incurred" UI field and the actual rendered notice email body — both share the same 2-decimal rule.

## `item.displaySummary` Token [confirmed — C449392]

Listed in the Add-token modal immediately BEFORE `item.enumeration`. Preview shows a realistic combined enumeration/chronology/volume sample, e.g. `no.1-2v. 121948-1962 (Board)` — a concrete example of the token's resolved format, useful when writing expected-result text for cases that exercise it.

## Awaiting-Pickup Notices Are Scoped Per-Request [confirmed — C400642]

When a title-level-request-enabled item is checked in and becomes "Awaiting pickup" for a specific requester, only THAT requester receives the Awaiting-pickup notice. Repeating the exact same flow for a second item/requester pair (same notice policy, same circulation rule) produces an entirely independent second notice to the second requester — notices are never deduplicated or merged across different requesters, even under identical policy/rule configuration.

---

## Capability Sets (Eureka) [confirmed permission display names]

`Settings (Circulation): Can create, edit and remove patron notice templates` / `… Can view patron notice templates`; `… Can create, edit and remove notice policies` / `… Can view notice policies`.

---

## Key Business Rules for Test Cases

1. A notice is produced only when **all four** exist: an active template, a notice policy that references it for the event, a circulation rule assigning that policy to the item/patron combination, and the triggering event occurring. (github + requests.md/check-in.md)
2. Template **category constrains** which token groups and which notice-policy section can use it (a `Request` template only in request notices, etc.). (github)
3. Notice policies split by recipient: **loan notices → borrower**, **request notices → requester**, plus fee/fine notices. (github)
4. Timing is `Before` / `Upon/At` / `After` the event; recurring notices add `and every {interval}`. (github)
5. **Check-in/Check-out receipt notices bundle** multiple loans/items into one notice per patron per session (sent at session end). Reminder/overdue for long-term loans can bundle overnight; short-term cannot. (github + check-in.md pickup-notice-at-session-end rule)
6. Templates/policies **in use cannot be deleted**; predefined templates cannot be deleted at all. (github)
7. Verify a notice's real effect **at the mailbox** — exact Subject + Body with the configured tokens resolved — not only the "Notice sent" circulation-log entry (see write-testrail-cases "verify effects at their real destination"). (skill + notices subsections)
8. TLR patron notices (Confirmation/Cancellation/Expiration) are selected under Title level requests (TLR) settings, separate from per-policy request notices. (github + circulation-settings.md)
9. Patron notice templates can be duplicated via Actions > Duplicate, which pre-fills Description/Category but always requires a renamed, unique template name before it can save. (cases — C396392)
10. The `loan.additionalInfo` token always resolves to the single most recent (non-superseded) loan comment, never a concatenation of comment history. (cases — C414969)
11. Proxy/Sponsor notice routing is a single per-relationship setting ("Notifications sent to" = Proxy or Sponsor) that applies uniformly to every Loan and Request notice for that relationship — never overridden per template or policy. (cases — C784435, C784436, C784437, C784438)
12. Overdue-fine notice bundling only merges charges that share the identical triggering-event type (both "returned" or both "renewed"); different event types for the same patron in the same window always produce separate emails. (cases — C397372, C397373, C397380)
13. Fee-amount tokens always render with exactly two decimal places, matching the same formatting used in the Loan-details "Fees/fines incurred" field. (cases — C357041)
14. Anonymizing a loan before its pending notice fires does not produce a Circulation-log "Send error" — the notice engine handles it silently. (cases — C729196)

---

## Authoring style (measured 2026-07-23)

Patron Notices: mixed **`Other` ~53% / `Func` ~40%**, median **~12 steps** (large — among the biggest), `User Journey` ~2%. Template/policy configuration cases lean `Other`; end-to-end "configure notice → trigger event → notice lands in mailbox with resolved tokens" cases lean `Func` and run long. Verify the notice at its real destination (the mailbox: exact subject + body with resolved item/user/loan tokens), not only the Circulation-log "Notice sent" entry. Preconditions carry the template + policy + circulation-rule + triggering setup; the flow walks event→delivery.

---

## Known Gaps / Items to Verify

- [x] Item-group token strings — confirmed live (C692204, 2025): see "Item-group tokens confirmed live" above. Other groups (`User`, `Loan`, `Request`, `Fee/fine charge`/`action`) still need their exact `{{…}}` names captured the same way (requests.md has confirmed request/staff-slip tokens for the Requests app's own slips, which is a different token set from these Patron Notice templates). This round confirmed `item.displaySummary` and `feeCharge.amount`/`feeCharge.remainingAmount` (2-decimal rule) specifically.
- [x] TestRail Patron notices cases (sec 328 subsections) — **pulled this round** (14 cases): realistic notice-setup preconditions, bundling scope, proxy/sponsor routing, and template duplication are now documented above with cited case IDs.
- [ ] Exact Eureka capability-set strings — permission display names confirmed; verify capability-set form in env.
- [ ] Whether the Proxy/Sponsor notice-routing setting has any per-template or per-policy override path in newer releases was not tested — the sampled cases show it as a single relationship-level switch with no override.

> N≥10 audit round (2026-07-22): 14 cases read (C396392, C414969, C784435, C784436, C784437, C784438, C729196, C397372, C397373, C397380, C357041, C385643, C449392, C400642). Resolved the file's main open Known Gap by pulling directly from TestRail section 328 and its subsections. Surfaced several previously undocumented rules: Patron Notice Template Duplication, Proxy/Sponsor notification routing (a single relationship-level switch governing all notice types), the exact scope-boundary of overdue-fine notice bundling (same-event-type only), the always-latest-comment behavior of `loan.additionalInfo`, the 2-decimal-place rule for fee tokens, and the "Lost item fee(s) charged" event's unique dual-radio Multiples UI. Added 6 new Key Business Rules (9-14).

> Random spot-check (2026-07-23): picked one fresh uncited case at random from section 328 (C411862) — found the template Edit pane's `Record last updated`/`Record created` metadata dropdown (with per-field `Source`/timestamp) was entirely undocumented. Added a new subsection under "Patron notice templates".


---

## Changes since 2026-07-21 (delta refresh 2026-11-07)

> Delta, not a rebuild: sections above reflect the original build. Where this section contradicts them, **this section wins**.
> Sources: GitHub folio-org/ui-circulation (translations/ui-circulation/en.json, HEAD v12.0.0); Jira folio-org.atlassian.net Done issues resolved since 2026-07-21; TestRail suite 21 cases created since 2026-07-21.

### What changed
- Notice templates: **Notice format** dropdown (Email / Text message); text message limited to 160 characters; Subject enabled only for Email; Body enabled after a format is chosen (UICIRC-1353). String "Email or print" removed — do not assert it.
- Notice policies: notices can be reordered by **drag & drop**; "Add notice above", "Delete notice" (UICIRC-1355/1372).
- Bugs to regress: hold shelf expiration notice sent twice (CIRC-2664); notice after aged to lost (CIRC-2679); item/title missing for ECS and mediated requests (CIRC-2639).

### UI strings changed since 2026-07-21 [source — en.json, 2026-11-07]

> `en.json` is the source of truth; `en_US.json` is a Lokalise copy that can lag behind. `<b>`/`<strong>` render as bold; `{x}` are placeholders.

**New strings**

| Key | Text |
|---|---|
| `settings.patronNotices.patronNoticeContent` | Patron notice content |
| `settings.patronNotices.textMessage` | Text message |
| `settings.patronNotices.noticeFormat` | Notice format |
| `settings.patronNotices.selectNoticeFormat` | Select notice format |
| `settings.patronNotices.noticeFormat.infoPopover` | If text message is selected, it has a maximum limit of 160 characters, including spaces, numbers, and symbols. If more than 160 characters are used, multiple text messages will be sent. |
| `settings.patronNotices.subject.infoPopover` | To enable the <strong>Subject</strong> field, select <strong>Email</strong> in the <strong>Notice format</strong> drop-down list. |
| `settings.patronNotices.body.infoPopover` | To enable the <strong>Body</strong> field, select an option in the <strong>Notice format</strong> drop-down list. |
| `settings.noticePolicy.addNoticeAbove` | Add notice above |
| `settings.noticePolicy.deleteNotice` | Delete notice |
| `settings.noticePolicy.dragAndDrop` | Drag & drop |
| `settings.noticePolicy.notices.textMessage` | Text message |

**Removed strings — do not assert**

| Key | Text |
|---|---|
| `settings.patronNotices.emailOrPrint` | Email or print |

### Jira — Done since build (circulation: check-in / check-out / circulation-settings / patron-notices / requests / mediated / circulation-log (CIRC, UICIRC, UICHKIN, UICHKOUT, UIREQ, UIREQMED, MODREQMED, UICIRCLOG, MODAUD) since 2026-07-21)

- UICIRC-1351 / 1387 / 1390 Story — "Automatic renewals" section on Loan policy form and page (settings + validation)
- UICIRC-1355 / 1372 Story — Reordering of patron notice policies (drag & drop)
- UICIRC-1353 Story — Shortened tokens in patron notices for text messages
- UICHKIN-515 / CIRC-2685 Story — [PoC] In-house use option in Check in (inHouseUse persisted on check-in-by-barcode)
- UICHKIN-510 Story — Check in modals: default focus on the action button, not "X"
- CIRC-2130 Story — Both Set cost and Actual cost fees/fines closed when item returned
- CIRC-2705/2706/2707 Bug — America/Vancouver time zone: due date cut-off by patron expiration; releases for Sunflower/Trillium (see Vancouver incident)
- CIRC-2664 Bug — Hold shelf expiration notice sent twice; CIRC-2679 notice not sent after aged to lost; CIRC-2639 item/title missing in email notices for ECS and mediated requests
- CIRC-2697 Bug — [LoC] batch requests duplicated queue positions; CIRC-2538 ECS pick slips printed from wrong SP; CIRC-2629 extra "Aged to lost" action (ECS); CIRC-2673 declare lost 500
- CIRC-2496 Bug — staff slip preview name always "Transit"
- MODAUD-324 Bug — fee/fine actions missing from Circulation log; MODAUD-323 circ logs not appearing; MODAUD-326 preferred contact changes missing in user version history
- (2026-06-16..07-21) UIREQ-1365 Bug — Requests app crashes opening a request with erased data; CIRC-2497 Bug — staff slip name missing in due date receipt; UICHKOUT-1012 Bug — all custom fields shown at Check out with default Other settings; UICIRC-1354 staff slips localisation; UICIRC-1316 Save button state for "Patron id(s) for checkout scanning"
- (no other Done issues found for UIREQ / UIREQMED / MODREQMED / UICHKOUT / UICIRCLOG in this window)

### TestRail — cases created since 2026-07-21: 24 (10 manual, 14 automated/Karate)

- C1538651 Postman \| item.shortTitle with missing, blank, or absent token in template — refs MODTEMPENG-137
- C1538650 Postman \| Render item.shortTitle alongside item.title in one template — refs MODTEMPENG-137
- C1538649 Postman \| Render item.shortTitle token with titles of varying length — refs MODTEMPENG-137
- C1504508 User without notice policy edit permission cannot modify the Formats settings pane — refs CIRC-2661,UICIRC-149,UXPROD-1532
- C1504507 Formats enabled in the Formats settings pane control which options appear in the patron record "Preferred notification method" field — refs CIRC-2661,UICIRC-149,UXPROD-1532
- C1504506 Formats enabled in the Formats settings pane are the only options available in the patron notice policy "Format" dropdown — refs CIRC-2661,UICIRC-149,UXPROD-1532
- C1504505 "Formats" pane appears in Settings > Circulation > Patron notices and displays correct elements — refs CIRC-2661,UICIRC-149,UXPROD-1532
- C1504504 Two notice rows with identical Template, Triggering event, Send, and Frequency but different Formats send in patron's preferred format; email is the fallback when no preference is set — refs CIRC-2661,UICIRC-149,UXPROD-1532
- C1504503 Notice with Format set to "User preference" is delivered in the patron's preferred format; fallback to email applies when patron has no preferred format set — refs CIRC-2661,UICIRC-149,UXPROD-1532
- C1504502 Notice with Format set to "Print" is delivered via print regardless of patron's preferred notification method — refs CIRC-2661,UICIRC-149,UXPROD-1532
