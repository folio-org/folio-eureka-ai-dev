---
area: serials-management
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO Serials Management — Business Logic Context

> Built: 2026-11-07 · Release: R2 2026 Umbrellaleaf (ui-serials-management v2.2.0 at HEAD) · Builder: build-app-context method, manual
> Sources: TestRail suite 21 section 34766 "Serials Management" (Publication patterns 34767, Prediction pattern templates 111083, Predicted piece sets 34768 — 33 cases, titles only; most frequency-specific cases are Draft); GitHub folio-org/ui-serials-management (en.json, package.json); Jira UISER / MODSER Done issues since 2025-11.

## What is Serials Management

The **Serials** app links to a PO line (Orders) and defines a **publication pattern** (ruleset: recurrence/frequency, omissions, combinations, chronology and enumeration labels). From the pattern the user **generates predicted pieces** (a predicted piece set), then **generates receiving pieces** that appear in the Receiving app for the PO line's title. **Publication pattern templates** (model rulesets) can be created, copied, edited, deprecated and deleted.

## Workflow

Serial (linked to POL) → Publication pattern (Active / Deprecated; edit only while unused, otherwise "Copy and deprecate") → Generate predicted pieces (preview, "Follow on from the last piece in a previous set") → Predicted piece set ("Piece set generated", Date generated) → Generate receiving pieces (optionally with items) → pieces in Receiving.

## Permissions

| Okapi permission (package.json) | Eureka capability set |
|---|---|
| Serials: Search & view serials / Edit serials / Manage serials | not confirmed (verify) |
| Serials: Edit publication patterns | not confirmed |
| Serials: Manage publication pattern templates / View publication pattern templates | not confirmed |
| Serials: Search & view predicted pieces / Create predicted pieces / Delete predicted pieces | not confirmed |
| Settings (Serials): View / Manage pick lists and values | not confirmed |

## Existing cases (non-Draft)

C446129 Add simple publication pattern with chronology only (Smoke); C446130 … with chronology and enumeration; C1346385 … with combination piece; C619001 Edit existing unused publication pattern; C619002 Copy and deprecate a publication pattern; C1322911 Add prediction pattern template; C446151 Generate predicted pieces (Smoke); C451603 Generate receiving pieces from a predicted piece set (Smoke); C553044 Generate receiving pieces with items; C613211 Create simple combined pieces; C619003 Delete a predicted piece set. 20 frequency-specific cases (daily … triennial, omissions, combinations) are Draft.

## Key Business Rules for Test Cases

1. Receiving pieces are created only by explicit "Generate receiving pieces" — never automatically (UISER-241). Result message: "{count} receiving pieces were generated. Please check this total is as expected…" [source]; on failure "Error: No receiving pieces were generated." [source].
2. Omitted pieces must not produce predicted or receiving pieces (MODSER-46); omission and combination rules by Issue apply across multiple cycles (MODSER-151/152). (jira)
3. A used pattern cannot be edited in place — copy and deprecate (C619002). (cases)
4. Prediction works without a label template (MODSER-153, UISER-70). (jira)
5. "Follow on from the last piece in a previous set" continues enumeration correctly (MODSER-135). (jira)
6. ECS with central ordering: receiving pieces can be generated from a non-primary tenant (UISER-205). (jira)
7. Verify generated receiving pieces in the **Receiving app** (title, expected date, enumeration/chronology, display summary) — the effect's real destination.
8. Templates: create / copy / edit / delete (UISER-229/231/233/234); "Publication pattern template deleted: {name}" [source]; template visibility controlled by "View publication pattern templates" (UISER-232).

## Known Gaps / Items to Verify

- [ ] Eureka capability set names.
- [ ] Exact pattern-form labels — take from the string table below; no case content was read.

---

## Exact UI Texts

> From `folio-org/ui-serials-management` `translations/ui-serials-management/en.json` at HEAD (2026-11-07). `{x}` are placeholders; `<b>`/`<strong>` render bold. Use verbatim.

### Toast Messages

| Key | Text | Source |
|---|---|---|
| `refdata.deleteRefdataValue.confirmMessage` | <strong>{name}</strong> will be deleted. | [source] |
| `refdata.deleteRefdataValue.errorMessage` | <strong>Error: {label}</strong> was not deleted. {error} | [source] |
| `refdataCategory.deleteRefdataCategory.errorMessage` | <strong>Error</strong>: Pick list <strong>{label}</strong> was not deleted. | [source] |
| `serials.deleteSerial.confirmMessage` | Serial <strong>{serial}</strong> will be deleted | [source] |
| `serials.deleteSerial.error.hasPublicationPattern` | Serial was not deleted because it has one or more publication patterns. | [source] |
| `serials.deleteSerial.success` | Serial deleted: <strong>{serial}</strong> | [source] |
| `serials.deleteSerial.error.noDeleteSerialBackendError` | <strong>Serial was not deleted:</strong> {message} | [source] |
| `templates.deleteTemplate.confirmMessage` | Publication pattern template <strong>{name}</strong> will be deleted | [source] |
| `templates.deleteTemplate.success` | Publication pattern template deleted: <strong>{name}</strong> | [source] |
| `templates.deleteTemplate.error` | <strong>Publication pattern template was not deleted:</strong> {message} | [source] |
| `ruleset.confirmGeneration` | Confirm generation of overlapping piece sets | [source] |
| `pieceSets.generateReceivingErrorMessage` | <strong>Error:</strong> No receiving pieces were generated.  | [source] |
| `pieceSets.receivingPiecesAlreadyExistWarning` | Warning: Receiving pieces already exist for this predicted piece set. See {link} for more details. | [source] |
| `pieceSets.overlappingDates.warning` | Warning: A predicted piece set with the start date <strong>{startDate}</strong> already exists for the serial <strong>{serialName}</strong> | [source] |
| `pieceSets.deletePredictedPieceSet.confirmMessage` | Are you sure you wish to delete this predicted piece set? | [source] |
