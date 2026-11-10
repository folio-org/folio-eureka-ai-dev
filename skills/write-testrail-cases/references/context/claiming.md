---
area: claiming
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO Claiming — Business Logic Context

> Built: 2026-11-07 · Release: R2 2026 Umbrellaleaf (ui-claims v3.0.0 at HEAD) · Builder: build-app-context method, manual
> Sources: TestRail suite 21 section 57331 "Claiming" (11 cases, titles); GitHub folio-org/ui-claims (translations/ui-claims/en.json — complete, 55 keys; package.json); Jira UICLAIM Done issues since 2025-11. Related contexts: `receiving.md` (pieces, Late status), `organizations.md` (claim integrations), `export-manager.md` (claim jobs).

## What is Claiming

The **Claiming** app lists receiving **pieces in "Late" status** across POs and lets staff act on them in bulk: **Send claim** (generates a claim export job per vendor integration, visible in Export manager), **Delay claim**, **Mark unreceivable**, and **Group by organization**. Claims go out through the organization's **claim integration** (Organizations > Integration details, integration type Claiming).

## UI structure (en.json)

- Search by: Keyword, Title (Receiving titles), Package (POL Package name), Product ID, PO number, POL number, Vendor reference number.
- Results columns: Expected date, Organization code, Organization name, Title, Display summary, Chronology, Enumeration, POL number, Status, Pieces to claim; row checkboxes + "Select all claims".
- Filters: Vendor, Order type, Material type, Order format, Location, Receiving status, Rush, Received date, Expected receipt date, Receipt due, Created/Updated by and date (Piece and Title), Ship to.
- Actions: Group by organization, Send claim, Delay claim, Mark unreceivable.

## Permissions

| Okapi permission | Eureka capability set |
|---|---|
| Claims: View claims | `data - UI-Claims Claiming - view` [cases] |
| Claim actions also need Receiving edit; viewing pieces needs Receiving view (C692165, C692167) | `data - UI-Receiving - edit` / `view` [cases] |

## Key Business Rules for Test Cases

1. Only pieces with status **Late** are processed; otherwise "Cannot find pieces with "Late" status to process." [source].
2. Send claim: confirmation "Claim {count} piece(s)?"; success "Claims are currently being processed. Please check Export manager for job status." [source]; one export job per organization integration — verify jobs in Export manager (C692111, C692126, C648508, C1322902, C692237).
3. Organization without a claim integration: "Unable to generate claims for {orgCodes} because no claim integrations exist." [source].
4. Mark unreceivable: modal "Mark unreceivable" / "Mark {count} piece(s) unreceivable?" → "Claims are successfully marked unreceivable" [source]; piece status changes in Receiving.
5. Delay claim → "Claims are successfully delayed." [source]; piece claim/expected dates change in Receiving.
6. Capability boundaries: without Receiving view the list is not visible; without Receiving edit claim actions are unavailable (C692165, C692167).
7. ECS: claim for a piece on a central-tenant POL with a member-tenant location (C692233).
8. The `claimingActive` filter was removed from Claims search (UICLAIM-29) — do not assert it.

## Existing cases

C692111, C692126, C648508, C1322902 (send claim, 1–2 integrations / orgs); C692165, C692167 (capabilities); C663254 (keyboard shortcuts); C692237 (consecutive runs in Export manager); C692233 (ECS); C1045993 (localization); C1322904 (unreceivable, delay, group by vendor with filters).

---

## Exact UI Texts

> From `folio-org/ui-claims` `translations/ui-claims/en.json` at HEAD (2026-11-07). `{x}` are placeholders; `<b>`/`<strong>` render bold. Use verbatim.

### Toast Messages

| Key | Text | Source |
|---|---|---|
| `claiming.delayClaim.success.message` | Claims are successfully delayed. | [source] |
| `claiming.delayClaim.error.message` | Failure on delay claims. | [source] |
| `claiming.sendClaim.modal.message` | Claim <b>{count, number}</b> {count, plural, one {piece} other {pieces}}? | [source] |
| `claiming.sendClaim.success.message` | Claims are currently being processed. Please check Export manager for job status. | [source] |
| `claiming.sendClaim.error.message` | Failure on send claims. | [source] |
| `claiming.markUnreceivable.modal.heading` | Mark unreceivable | [source] |
| `claiming.markUnreceivable.modal.message` | Mark <b>{count, number}</b> {count, plural, one {piece} other {pieces}} unreceivable? | [source] |
| `claiming.markUnreceivable.success.message` | Claims are successfully marked unreceivable | [source] |
| `claiming.markUnreceivable.error.message` | Failure on mark unreceivable | [source] |
| `error.code.cannotFindPiecesWithLatestStatusToProcess` | Cannot find pieces with "Late" status to process. | [source] |
| `error.code.unableToGenerateClaimsForOrgNoIntegrationDetails` | Unable to generate claims for <b>{orgCodes}</b> because no claim integrations exist. | [source] |
