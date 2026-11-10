---
area: marc-holdings
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO MARC Holdings (quickMARC) — Business Logic Context

> Built: 2026-11-07 · Release: ui-quick-marc v8.0.0 at HEAD · Builder: build-app-context method, manual
> Sources: TestRail suite 21 section 16714 "MARC > MARC Holdings" (28 cases) with sub-sections 39766 "Create MARC holdings" (39 cases) and 39767 "Edit MARC holdings" (43 cases) — titles for all, full steps for C350646, C983156, C1045403; GitHub folio-org/ui-quick-marc `translations/ui-quick-marc/en.json`; Jira UIQM, MODQM, MODINV Done issues since 2025-11.
> Related contexts: `marc-bib-quickmarc.md` (shared editor shell, bib-only rules), `inventory.md` (FOLIO holdings record, move, call numbers), `data-import.md` (importing MARC holdings files, section 17338), `consortium-manager.md` (ECS ownership).

## What is MARC Holdings

A holdings record whose source is MARC (`Source` = MARC) is edited in quickMARC, not in the FOLIO holdings form. The MARC holdings record (SRS) drives the FOLIO holdings record: 852 maps to location and call number fields, 004 links to the instance HRID. Some FOLIO-only fields (statistical code, administrative note, ILL policy, receiving history, tags, etc.) are edited in the FOLIO holdings form and must survive a quickMARC save (MODQM-505, MODINV-1323, C983156).

## Entry points

| Action | Where | Result |
|---|---|---|
| `Add MARC holdings record` | Instance detail (Source = MARC) → `Actions` | Pane `New MARC holdings record`, record status `New`, `Save & close` disabled until a change is made (UIQM-522) |
| `Edit in quickMARC` | Holdings detail (Source = MARC) → `Actions` | Pane `Edit MARC holdings - Location: {location} - [{callNumber}]` |
| `View source` | Holdings detail → `Actions` | MARC source view; `Edit` and `Print` from the source pane (UIIN-3012, UIQM-352) |
| Import | Data Import, job profile `Default - Create Holdings and SRS MARC Holdings` | Imported MARC holdings record (see `data-import.md`) |

MARC holdings can be created only for an instance with Source = MARC. Holdings with Source = MARC can be moved to another instance with Source = MARC or FOLIO (C345404, C345405).

## Editor behaviour (shared with bib, holdings-specific values)

- Rows: tag, two indicator boxes, content; row actions `+` (add field), move up/down, `Delete this field`. Deleted fields show a placeholder and can be restored (`Restore deleted field(s)` on the confirmation modal); a restored field returns to the same position (C359178).
- Buttons: `Cancel`, `Save & keep editing` (stays in the editor, keeps focus on the last edited field — UIQM-715), `Save & close`. `Esc` with unsaved changes opens the "Are you sure?" modal (C434155, C434156).
- Empty rows (no tag and no subfield value) are deleted on save (C423484, C423485). No field can be added below `999 ff` (C494043).
- All fields except LDR (and on create also 005, 999) can be moved and saved (C407734, C407738).
- 852 `$b` is filled through `Permanent location look-up` (modal with its own `Save and close`) or by typing a location code (C358990, C569545). Location codes with whitespace are supported (C805766).
- `$` in content is stored as the `{dollar}` code (C451564, C451565); backslash `\` is a valid character and shows in the detail view and browse (MODINV-1285, C877078, C877082).
- Create flow (2026, MODQM-490/491/497, UIQM-806): 003 is removed on save; 035 values are **not** normalized for holdings (C1045403). The edit flow keeps an added 003.
- 005 is system-managed: updated on every save (C417047); duplicate 001/005 added by the user are dropped, not rejected (C387462, C496215).
- Detail view after save: `Record last updated` → `Source` shows the editing user as `<last name>, <first name>`, or last name only when the first name is empty (C356850, C396368).

## Required and non-repeatable fields

| Field | Rule | Message (en.json) |
|---|---|---|
| LDR | Exactly one, 24 characters | `Record cannot be saved. The Leader must contain 24 characters, including null spaces.` |
| LDR positions | Only 05, 06, 17, 18 editable for holdings | `Record cannot be saved. Please check the Leader. Only positions 5, 6, 17, 18 can be edited in the Leader.` |
| LDR invalid value | Per-position valid values | `Record cannot be saved. Please enter a valid {positions}. Valid values are listed at {link}` |
| 001 | One; extra copies are dropped on save | `Record cannot be saved. Can only have one MARC 001.` (bib/authority wording; holdings drops duplicates) |
| 004 | Exactly one (instance HRID) | `Record cannot be saved. Can only have one MARC 004.` |
| 008 | Required, one, valid values (32 positions; imported records with fewer positions can still be edited — C387479) | `Record cannot be saved without 008 field` / `Record cannot be saved with more than one 008 field` / `Record cannot be saved. Field 008 contains an invalid value in "{name}" position.` |
| 852 | Required, exactly one, valid location in `$b`, single `$b` with no extra spaces | `Record cannot be saved. An 852 is required.` / `Record cannot be saved. Can only have one MARC 852.` / `852 $b contains an invalid Location code. Please try again.` |
| 999 ff | Several allowed on create (C503071) | — |
| Local control fields 002, 009 | Repeatable, with or without `$a` (UIQM-670) | — |
| MARC tag | 3 characters (MRSPECS-44) | Fail/warn summary toast: `Please scroll to view the entire record. Resolve issues as needed and save to revalidate the record.` + `Fail errors: {failCount}` / `Warn errors: {warnCount}` |

Error toasts appear before confirmation modals (C375206, C375187). Invalid LDR values in positions 07, 08, 10, 11, 19, 20–23 of an imported record are replaced with valid values on edit (C353984, C358155).

## Toasts

| Event | Text |
|---|---|
| Create in progress | `Creating record may take several seconds.` |
| Create success | `Record created.` |
| Create failed | `Unable to create record due to system error. Please try again or contact support.` |
| Create slow | `Creating this record is taking longer than expected. Please check back later if record is available or contact support.` |
| Edit saved | `This record has successfully saved and is in process. Changes may not appear immediately.` |
| Record deleted by another user | `This record has been deleted by another user. You can no longer edit this record, hit the cancel button to return to the previous page.` |
| Generic failure | `Record not saved: Communication problem with server. Please try again.` |

## Mapping to the FOLIO holdings record

- 852 → permanent location, call number, prefix, suffix, call number type (from the 852 first indicator — MODQM-506, C389500, C389503). Deleting the mapped 852 subfields clears the FOLIO call number fields (C375188).
- Changing holdings call number components updates the item's effective call number metadata; changing unrelated fields does not (C388510, C388511).
- FOLIO-only fields and tags are preserved after a quickMARC save — regression set from MODQM-505, MODQM-513 (number of items, receipt status — still open), MODINV-1323 (C983156).
- ECS: after `Update ownership` to another member tenant, the 852 `$b` location code must change to the new location (MODINV-1389, UIQM-834). Create/edit in ECS tenants regressed in Sunflower (MODINV-1327, MODINV-1330).

## Permissions (Okapi → Eureka, from team cases)

| Okapi permission | Eureka capability (type – resource – action) |
|---|---|
| `quickMARC: View MARC holdings record` | `data - UI-Quick-Marc Quick-Marc-Holdings-Editor - view` (verify — not seen in a case) |
| `quickMARC: View, edit MARC holdings record` | `data - UI-Quick-Marc Quick-Marc-Holdings-Editor - manage` |
| `quickMARC: Create a new MARC holdings record` | `data - UI-Quick-Marc Quick-Marc-Holdings-Editor - create` |
| `Inventory: View instances, holdings, and items` | `data - UI-Inventory Instance - view` |
| `Inventory: View, create, edit holdings` | `data - UI-Inventory Holdings - edit` |
| `Inventory: All permissions` | `data - UI-Inventory - manage` |

Recent cases use the two-column Okapi / Eureka table in preconditions (C1045403) or the Eureka list only (C983156).

## Key Business Rules for Test Cases

1. MARC holdings exist only under an instance with Source = MARC; the create action is absent for FOLIO-source instances (cases).
2. 852 is required and non-repeatable; 004 and 008 are non-repeatable; 008 is required (en.json + cases).
3. Only LDR positions 05, 06, 17, 18 are editable — do not reuse the bib list (5, 6, 7, 8, 17, 18, 19) or the authority list (5, 17, 18) (en.json).
4. Duplicate 001 and 005 are silently dropped on save; duplicate 004, 008, 852 or LDR block the save (cases).
5. Every save updates 005 and the `Record last updated` source user (cases).
6. A quickMARC save must not clear FOLIO-only holdings fields or tags (MODQM-505, MODINV-1323).
7. Call number type follows the 852 first indicator, including after edit (MODQM-506).
8. Optimistic locking: two users editing the same MARC holdings record — the second save shows the conflict banner; `Save & keep editing` follows the same rule (C353227, C353229, C360103).
9. Create and edit are separate sections (39766, 39767); the team writes the same validation as two cases, one per flow. Keep that split.

## Authoring style (measured 2026-11-07)

Type `Functional` in the create/edit sub-sections (type_id 6 in all 82 cases); the parent section 16714 has older cases of another type. Priority Medium dominates. Full-case sample (C350646, C983156, C1045403): 14, 7 and 8 steps; Test Group Critical Path for the core create journey, Extended for regression bugs. Step count was not measured across the section. Titles name the record in quotes: `"MARC Holdings"` / `"MARC holdings"`, often with the flow: `... when creating "MARC Holdings" record`. Data setup is a Data Import file with the default job profile, referenced in preconditions.

## Known Gaps / Items to Verify

- [ ] Eureka capability for view-only (`Quick-Marc-Holdings-Editor - view`) — not seen in a case.
- [ ] MODQM-513 (number of items, receipt status cleared after quickMARC save) is still In Refinement — expect failure until fixed.
- [ ] 008 is now a set of dropdowns for holdings (MODQM-519) — confirm control type before writing 008 steps.
