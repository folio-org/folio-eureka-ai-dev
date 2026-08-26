# FOLIO quickMARC — MARC Bibliographic Editing — Business Logic Context

> Built 2026-07-21 (browser-based). **Exact UI Texts / validation errors confirmed against `folio-org/ui-quick-marc/translations/ui-quick-marc/en.json` (2026-07-21).** TestRail: suite 21 section 1285 "MARC" > 16715 "MARC Bibliographic" (subsections 23705 Create new MARC bib, 23706 Derive MARC bib, 24360 Edit MARC bib, each with Manual linking / Automated linking / Consortia sub-subsections, plus 27186 Optimistic locking, 39274 "API | MARC validation rules (bibliographic)", 58862 Version history). This file covers **MARC Bibliographic** editing only. MARC Holdings editing (section 16714) and MARC Authority (section 17151, already covered by `marc-authority.md`) share the same quickMARC editor shell and much of the same validation-error vocabulary, but have their own field-level rules — don't assume a Bib rule (e.g. exact 1XX/010 handling) transfers unchanged to Holdings.

---

## What is quickMARC (Bibliographic)

quickMARC is the in-browser MARC editor FOLIO uses for creating, deriving, and editing MARC Bibliographic records directly (tag/indicator/subfield grid), as an alternative to Data Import. It is opened from the **Inventory** app (`Actions > + New MARC bibliographic record`, `Actions > Derive new MARC bibliographic record`, `Actions > Edit MARC bibliographic record`) and saves back into Inventory as the source record behind an Instance. quickMARC also renders the record's fixed fields (**LDR**/Leader and **008**) as structured dropdowns/boxes rather than raw character positions, with inline validation.

---

## Key Terms

| Term | Definition |
|---|---|
| LDR (Leader) | 24 fixed character positions; quickMARC splits some into read-only groups and some into individual dropdowns/boxes (Status, Type, BLvl, Ctrl, ELvl, Desc, MultiLvl, etc.) |
| 008 field | Fixed-length control field; positions render as labeled dropdowns/boxes, several mandatory |
| Controlled field | A bib field (e.g. 1XX-derived heading fields) linked to and governed by a MARC Authority record — its content becomes read-only/restricted per the authority link |
| Manual linking | Staff explicitly links a bib field to an authority record via the linking UI |
| Automated linking | System auto-links bib fields to authority records based on matching rules (see `MARC bib and authority linking rules` corpus) |
| Derive | Create a new bib record starting from a copy of an existing one (`Actions > Derive new MARC bibliographic record`) |
| Optimistic locking | Save-conflict protection: saving a record that was changed/deleted elsewhere since it was opened is blocked |
| 999 field | System-managed field carrying `$s`/`$i` (SRS/Instance UUIDs); user-added 999 handling has changed across releases (see business rules) |

---

## UI structure [confirmed]

- Entry points from Inventory: `Actions > + New MARC bibliographic record` (create), `Actions > Derive new MARC bibliographic record` (derive, from an existing Instance's Actions menu), `Actions > Edit MARC bibliographic record` (edit, from an existing Instance/source-record view), `Actions > View source` (read-only MARC view).
- Pane header shows record `Status:` (`New` / `Current` / `In progress` / `Error`) and `Last updated: {date} {time}`.
- Each MARC field row: tag box, two indicator boxes, repeatable subfield ($x) rows; `+` (Add a new field) / delete (trash) icon per row.
- LDR is rendered as a mix of read-only grouped boxes (e.g. positions 00-04, 09-16, 20-23, filled with fixed defaults like `00000` / `a2200000` / `4500`) and individual dropdowns/boxes for the meaningful positions (`Status`(05), `Type`*(06), `BLvl`*(07), `Ctrl`(08), `ELvl`(17), `Desc`(18), `MultiLvl`(19)) — required positions show an asterisk on the label; hovering any LDR box shows its full descriptive name (e.g. "Record status", "Type of record", "Bibliographic level").
- 008 field positions similarly render as individual dropdowns; a position needing a valid selection is **highlighted in red** until a valid value is chosen.
- Save buttons: `Save & close`, `Save & keep editing`. Delete-fields confirm flow: modal `Delete fields`, body `By selecting <b>Continue with save</b>, then <b>{count} field(s)</b> will be deleted and this record will be updated. Are you sure you want to continue?`, buttons `Continue with save` / `Restore deleted field(s)`.

---

## Exact UI Texts — validation & save errors [confirmed against en.json]

### Record-shape / cardinality errors

| Condition | Message |
|---|---|
| LDR length wrong | `Record cannot be saved. The Leader must contain 24 characters, including null spaces.` |
| LDR forbidden position edited (bib) | `Record cannot be saved. Please check the Leader. Only positions 5, 6, 7, 8, 17, 18 and/or 19 can be edited in the Leader.` |
| LDR / 008 mismatch | `Record cannot be saved. The Leader and 008 do not match.` |
| Invalid position value | `Record cannot be saved. Please enter a valid {positions}. Valid values are listed at {link}` |
| Invalid 005 position 5 (bib) | `Record cannot be saved. Invalid value entered for position 5.` |
| Multiple 001 | `Record cannot be saved. Can only have one MARC 001.` |
| Multiple 010 | `Record cannot be saved with more than one 010 field` (confirmed live in case C380644 as inline `Fail: Field is non-repeatable.`) |
| 008 field missing | `Record cannot be saved without 008 field` |
| Multiple 008 | `Record cannot be saved with more than one 008 field` |
| 008 position invalid value | `Record cannot be saved. Field 008 contains an invalid value in "{name}" position.` |
| Fixed-field wrong length | `Invalid {name} field length, must be {length} characters.` (confirmed live: `Invalid Ctry field length, must be 3 characters.`) |
| Missing 1XX heading | `Record cannot be saved without 1XX field.` |
| Multiple 1XX | `Record cannot be saved. Cannot have multiple 1XXs` |
| Missing/multiple 245 | `Record cannot be saved without field 245.` / `Record cannot be saved with more than one field 245.` |
| 852 missing/multiple (holdings-shared) | `Record cannot be saved. An 852 is required.` / `Record cannot be saved. Can only have one MARC 852.` |
| MARC tag not 3 chars / non-digits | `Record cannot be saved. A MARC tag must contain three characters.` / `Invalid MARC tag. Please try again.` |
| Missing subfield value | `Missing a subfield value for a MARC tag` |
| One-subfield-only field violated | `<b>{fieldTag}</b> can only have one <b>{subField}</b>.` |

### Authority-linking-specific errors (bib side)

| Condition | Message |
|---|---|
| $9 on non-linkable field | `$9 is an invalid subfield for linkable bibliographic fields.` |
| Editing a controlled subfield | `A subfield(s) cannot be updated because it is controlled by an authority heading.` |
| Changing a saved controlled 1XX-derived field | `Cannot change the <b>saved MARC authority field {tag}</b> because it controls a bibliographic field(s). To change this 1XX, you must unlink all controlled bibliographic fields.` |

### Save-flow / concurrency errors

| Condition | Message |
|---|---|
| Generic save failure | `Record not saved: Communication problem with server. Please try again.` (confirmed live in C496193 as the message shown for an actually-invalid record shape, i.e. malformed records can surface as this generic error rather than a specific one) |
| Fixed-field length on save | `Record not saved. Please check the character length of the fixed fields.` |
| Optimistic-locking conflict | `This record has been deleted by another user. You can no longer edit this record, hit the cancel button to return to the previous page.` |
| Derive stale instance | `Instance cannot be updated. Deprecated instance version.` |
| Post-save processing note | `This record has successfully saved and is in process. Changes may not appear immediately.` (confirmed live as the exact save toast for a **shared/consortia** MARC bib edit — C405507; a case for a non-shared/local-tenant save should still confirm whether the same string or a shorter plain "Record ... saved" toast fires, this is not yet isolated) |
| Automated-linking success (per-field) | `Field <b>{tag1}, {tag2} and {tag3}</b> has been linked to MARC authority record(s).` (confirmed live, C388560 — lists only the tags that actually matched) |
| Automated-linking error (per-field, no `$0` match) | `Field <b>{tag}</b> must be set manually by selecting the link icon.` (confirmed live, C388560 — fires for a field lacking a matching `$0`/naturalId, directing the user to Manual linking instead) |
| Manual-linking success (single field, per-field link icon) | `Field {tag} has been linked to a MARC authority record.` (confirmed live, C365134 on the **Edit** flow — distinct wording from the Automated-linking multi-field toast above) |
| Warn-level errors present at save | `<b>Please scroll to view the entire record. Resolve issues as needed and save to revalidate the record.</b>{breakingLine}Warn errors: <b>{warnCount}</b>` (Warn does not block save — re-saving proceeds) |
| Fail-level errors present at save | Same lead sentence + `Fail errors: <b>{failCount}</b>{breakingLine}Record cannot be saved with a fail error.` (Fail blocks save) |

> **Warn vs Fail matters for case design:** a Warn-level validation issue lets the user save anyway (team convention: "ignore errors and Save again" — confirmed in cases C496208/C496193); a Fail-level issue hard-blocks save until corrected. Don't write a negative case that treats every inline error as save-blocking — check whether the specific rule is Warn or Fail.

---

## Capability Sets (Eureka) — dual-column convention confirmed live in corpus

Real cases (C496193, C503013, C496208) already show the team's two-column Okapi/Eureka table for this area:

| Permission name for Okapi env. | Capabilities/Sets for Eureka env. |
|---|---|
| Inventory: All permissions | `data - UI-Inventory - manage` |
| quickMARC: Create a new MARC bibliographic record | `data - UI-Quick-Marc Quick-Marc-Editor - create` |
| quickMARC: View MARC bibliographic record | `data - UI-Quick-Marc Quick-Marc-Editor - view` |
| quickMARC: View, edit MARC bibliographic record | `data - UI-Quick-Marc Quick-Marc-Editor - manage` |
| quickMARC: Derive new MARC bibliographic record | (derive-specific capability — curate exact Eureka name in env) |
| quickMARC: Can Link/unlink authority records to bib records | (linking-specific capability — curate exact Eureka name in env) |

A user without the create/edit/derive permission for the specific action must NOT see the corresponding `Actions` menu option at all (confirmed pattern, C422105) — the option is absent from the expanded menu, not present-but-disabled.

---

## Common Verification Patterns

### Create a new MARC bib record — first-open field inventory (confirmed pattern, C422104)

This is a genuine full-modal-inventory case (the pane itself is under test): verify `001` empty, `005` empty (tag editable), `008` tag-only initially, `999` empty, LDR groups exactly as documented (read-only 00-04/09-16/20-23 filled with fixed defaults; dropdowns 05/06*/07*/08/17/18/19 with the listed default values and hover tooltips), `245` with both indicators blank and an empty `$a`. Then verify Close (`x`) and `Cancel` both discard with no record created.

### Non-repeatable field validation (confirmed pattern, C380644, C496193)

1. Fill required fields (LDR Type/BLvl, 008 red-highlighted dropdowns, 245 $a) to make Save enabled.
2. Add a second instance of a non-repeatable field (010, 008, LDR, 1XX, 245...).
3. Expected: inline `Fail:` error naming the specific rule (e.g. "Field is non-repeatable.") and the pane stays open — save does NOT silently succeed or silently drop the duplicate.
4. Remove the duplicate, Save & close → success toast, record saved, then re-open via `Actions > View source`/Edit to confirm only the surviving field persisted.

### 008 fixed-field position validation (confirmed pattern, C503013)

Cover the position-by-position validation loop, not just one bad value: an invalid dropdown selection shows a **separate inline error per invalid position**; correcting one still leaves others flagged until all are valid; a wrong-length typed box (e.g. `Ctry` needing exactly 3 characters) gets its own length-specific error. Don't stop at the first error — real cases iterate until zero red-highlighted positions remain.

### System-managed field special handling (confirmed pattern, C380699 001/005, C496208 005, C380716 999)

`001` and `005` added by the user become **read-only** once the tag is typed (system fields cannot be user-authored); re-opening the saved record shows only the single system-generated field, any user-added duplicate having been superseded/removed. **999 handling is release-dependent**: before Trillium, all user-added 999s were stripped on save; from Trillium onward, only 999 fields with indicators `ff` are stripped while other indicator combinations (e.g. `12`) are preserved alongside the system-generated `999 ff $s {uuid} $i {uuid}` row — a case touching 999 must state which release behavior it targets.

### Delete-fields confirmation flow

Deleting one or more fields and then saving triggers the `Delete fields` modal (see UI structure) rather than an immediate silent delete — verify both `Continue with save` (fields deleted, record updated) and `Restore deleted field(s)` (fields restored, nothing saved) branches.

### Authority-linking gating (from github error strings — verify against a real linking case before asserting verbatim)

Editing/removing a subfield on a bib field that is controlled by a linked authority is blocked (`A subfield(s) cannot be updated because it is controlled by an authority heading.`); changing the bib's own saved 1XX-equivalent heading field that controls other fields requires unlinking first (`Cannot change the saved MARC authority field {tag}...`). Cover both the Manual linking and Automated linking sub-scenarios per the corpus's own section split (23705/24360's "Manual linking"/"Automated linking" subsections) — they exercise different trigger paths (explicit staff action vs. rule-based auto-match).

### LDR position 05 (Record status) drives Instance suppression flags — cross-entity effect (confirmed live, C1307997, 2025)
Changing **LDR position 05 to `d`** (Deleted) and saving doesn't just update the MARC record — it flips the underlying **Instance** record to `Set for deletion = true`, `Suppressed from discovery = true`, and `Staff suppressed = true`. Changing position 05 back to `c` (Corrected/current) reverts `Set for deletion` to `false`, but **`Suppressed from discovery` and `Staff suppressed` do NOT automatically revert** — they stay suppressed until explicitly unsuppressed on the Instance. A case exercising LDR position 05 must verify all three Instance flags after each change, not just the MARC field value, and must not assume "undo the LDR value" means "undo the suppression" (real regression: MODQM-509). This is the clearest example in this area of a bib-editing action whose real assertion target is a different entity (Inventory Instance), not the MARC record itself — apply the same "verify effects at their real destination" discipline used elsewhere in this skill.

### Optimistic locking (section 27186 — pull a dedicated case before writing new ones)

Two users/tabs open the same record; one saves first. Expected for the second: `This record has been deleted by another user. You can no longer edit this record, hit the cancel button to return to the previous page.` (message text is shared with the delete case, i.e. this exact wording fires even for a plain concurrent-edit conflict, not only an actual delete — don't over-interpret the string as proof of deletion in the case's own assertions).

### Derive — system-field carry-over rules (confirmed live, C387459 001, C496210 005, C499607 006/007, C503056 245, section 23706)

Deriving is NOT a blind copy of every field — system-managed fields follow different rules than ordinary content fields:

- **`001` and `005`**: even if the user manually adds a second `001` (or `005`) box and fills it with a value before saving, only **one** `001`/`005` field survives the save, holding the **system-generated** value — the manually-added duplicate is silently dropped, not flagged as an error. Re-opening the derived record via `Actions > Edit MARC bibliographic record` shows only the single system value. A case must assert "only one field, system value" after save, not "the user's typed value was rejected with an error."
- **`006`/`007`**: unlike 001/005, these are repeatable **and** user-authorable during derive — the user can add multiple 006/007 rows (each with its own type-character selection, e.g. `006-a`, `006-d`, `007-a`, `007-c`) and all of them persist after Save & close (confirmed C499607). Don't conflate the 006/007 repeatable-and-preserved rule with the 001/005 single-and-regenerated rule — they look similar (both "system" fixed fields) but behave oppositely.
- **`245`**: still hard-required on Derive exactly as on Create — deleting the `$a` subfield's value (leaving the empty box) or deleting the whole `$a` subfield blocks save with the **Fail**-tier flow: `Field 245 is required.` plus the standard `...Fail errors: 1 Record cannot be saved with a fail error.` banner (confirmed C503056). This is the same rule as row "Missing/multiple 245" above, now confirmed to also apply on the Derive pane, not only Create/Edit.
- **Local control fields (002, 004, 009)**: on Derive these carry over **as-is** and are treated leniently — unlike 1XX/245, they are valid both **without** any subfield indicator (raw value with no `$a`, e.g. `002 FOLIO23491`) and **with** one added by the user (`$a FOLIO23491`); either form saves successfully with the standard success toast, and re-opening via `View source` confirms whichever form was saved persists unchanged (confirmed live, C503160). Don't write a case asserting Local control fields require a subfield code to save — they don't.

### Manual linking — Create — exact modal & locked-box mechanics (confirmed live, C422126, section 24361)

1. Add a new field row (e.g. tag `700`), leave its `$a` subfield **empty** — a "Link to MARC authority record" icon appears to the right of the row as soon as the tag is a linkable type (no need to fill any subfield first).
2. Clicking the link icon opens the **Select MARC authority** modal: `Browse` is the default-selected toggle, and for a personal-name-type field (1XX/7XX `$a` personal name) the modal pre-selects the **Personal name** search-qualifier option automatically — don't write a case that assumes the user must manually pick the heading-type filter for a plain personal-name field.
3. Typing the target heading into the browse input and clicking `Search` surfaces the matching MARC Authority record highlighted in the results list; clicking the `Link` icon to its left (not a generic "Select" button) performs the link and closes the modal.
4. After linking, the field's box layout **splits** into a fixed pattern: first three boxes (tag + 2 indicators) become **locked**; the box holding the linked heading value (e.g. `$a Jackson, Peter, $d 1950-2022 ...`) becomes **locked**; any subfield the user had typed that is NOT part of the authority's own heading (e.g. a `$t` they added) stays **editable**; the `$0` box (authority record ID, e.g. `$0 3052044`) is **locked**; a trailing box remains editable for further free-text subfields. The row's icons change to just `Unlink from MARC authority record` and `View MARC authority record` (the original link icon disappears once linked).
5. `$9`/`$0` validation and the "controlled subfield can't be edited directly" error (see Exact UI Texts above) apply immediately to the newly-locked boxes.
6. **Confirmed identical on the Edit flow** (C365134, section 24363 — same locked-box breakdown, same modal, same "Personal name" preselection): the modal also supports a `Search` toggle (with a `Keyword` sub-option) as an alternative to the default `Browse` toggle — both are real, valid paths to the same result, don't assume Browse is the only route. The locked `$0` value's exact **format is not fixed**: it can be a bare authority `naturalId` number (e.g. `$0 3052044`, seen on Create) or a full authority URI (e.g. `$0 http://id.loc.gov/authorities/names/n2008001084`, seen on Edit) — the format follows whatever identifier scheme the linked Authority record's own `$0`/source-file configuration uses, not a fixed bib-side rule.

### Automated linking — Create — "Link headings" button mechanics (confirmed live, C388560, section 24362)

Automated linking is driven by two things, not just the button click: (1) each bib-field-tag's linking rule must have `autoLinkingEnabled: true` (configured via `PATCH /linking-rules/instance-authority/{id}`, readable via the same-named `GET`), and (2) the field's `$0` subfield value must **exactly match** an existing MARC Authority record's `naturalId`.

- Clicking `Link headings` processes ALL eligible fields in the record in one pass: fields whose `$0` matches an authority's `naturalId` get linked automatically; fields whose `$0` does NOT match any `naturalId` are left unlinked and separately flagged (see the per-field success/error toast strings above — both toasts can appear together after a single click, one per outcome group).
- **Non-controllable subfields already present on the field before linking (e.g. `$j`, `$2 fast`) are preserved** after auto-link.
- **Controllable subfields that duplicate the authority's own heading content (e.g. `$a`, `$d` on a field being auto-linked) are stripped/replaced** by the authority's heading after auto-link — don't write a case asserting the user's originally-typed `$a`/`$d` values survive verbatim once auto-linked; only the non-heading subfields survive as typed.
- The `Link headings` button itself stays enabled in the pane header for further passes after a partial-success run (i.e. it isn't a one-shot/disable-after-use control).

### Version history (MARC Bib) — pane & diff-modal structure (confirmed live, C663247 base pane, C692071 diff modal, section 58862)

- Entry point: a **clock icon** next to `Actions` on the record's `View source` (or Edit) pane — hovering it shows the tooltip `Version history`. Clicking it opens the Version history tab in the pane immediately to the right, with a loading indicator while it fetches.
- Pane header shows an exact version counter, e.g. `1 version` (singular) growing to `N versions` (plural) as more saves accumulate — assert the exact count, not just "some versions shown."
- Each version is a **Card**: `Updated date/time` (localized), a `Source` line, and a version label. Cards are ordered **newest-to-oldest, top-to-bottom**: the **bottom-most (oldest) card** is labeled **"Original Version"** (no `Changed` link — nothing precedes it to diff against); the **topmost (most recent) card** is labeled **"Current version"** (bold+italic) **and** additionally shows a `Changed` hyperlink; any **middle** card (neither newest nor oldest) shows only the `Changed` hyperlink with no version-label text. Don't write a case that only checks the oldest card's label and assumes every other card looks the same — the newest card carries its own distinct "Current version" label that the middle cards lack (confirmed live, C663247 single-version case + C692230/C692168 multi-version consortia cases).
- Clicking a later card's `Changed` hyperlink opens a **diff modal**: header repeats that card's `[Date], [Time]` and `Source` line, body is a table with columns `Action | Field | Changed from | Changed to` (e.g. a row `Added | 700 | - | 1\ $a Staceyann Chin $d 1972-`, another row for `Edited | LDR | ...`). Note the literal `\` blank-indicator character renders as visible **whitespace** in this table, not as a literal backslash glyph — don't assert the raw `\` character appears in the diff UI. The modal closes via either an `X` (top-left) or a `Close` button (bottom-right); both return focus to the Version history pane, not the underlying record pane.
- While the Version history pane is open, the record's own `Actions` button is **disabled**; closing the pane (`X` in its own header) re-enables `Actions` and returns focus/highlight to the `View source`/Edit pane.
- No `Load more` button is shown until enough versions exist to require pagination (not observed with a single version present).

### Consortia — shared MARC Bib edit propagation (confirmed live, C405507, section 27434)

- A user with edit permissions and an affiliation in a **Member** tenant CAN directly edit a MARC bib record that is **shared** from the Central tenant — the edit is made from the Member tenant's own quickMARC editor, not from Central.
- Save confirmation is the shared/consortia-specific toast: `This record has successfully saved and is in process. Changes may not appear immediately.` (see Exact UI Texts above) — the async "in process" wording is specific to this cross-tenant propagation path.
- After such an edit, the Instance's `Record last updated` accordion (`Administrative data`) shows the **actual editing user** (e.g. User A) as the `Source`, regardless of which tenant (Member vs Central) they were logged into when they made the edit.
- A second user affiliated only with a **different** Member tenant, viewing the same shared record from the **Central** tenant, sees the propagated change (title, field content, `Record last updated` source) — confirming the edit is a true single shared record, not a per-tenant copy.

### Consortia — Create: per-tenant validation rules & duplicate-LCCN check (confirmed live, C552462, C514877, section 27635)

- **MARC validation rules (required/repeatable field configuration) are per-tenant, not global**, even for a Shared record: Central and Member tenants can have deliberately **contradicting** rule sets (e.g. field `700` configured `required` on Central but not on Member). Creating a record **on a given tenant** is validated against **that tenant's own rule config** — a case must state which tenant's ruleset it's exercising and must not assume one shared/global rule set applies everywhere. Confirmed with the exact save-blocking error still following the standard pattern: `Field 700 is required.`
- **Duplicate-LCCN (010 `$a`) check on Shared record creation** is tenant/scope-aware and severity-differentiated: entering a `010 $a` value that matches an **existing Shared record's active LCCN** blocks save with the inline `Fail: 010 $a already exists.` error (hard block). Entering a value that instead matches an existing Shared record's **Canceled/cancelled LCCN** (the `$z`-style historical value) does **not** show that inline Fail error at all — only a `Warn`-tier toast appears, and save is NOT blocked. Don't write a duplicate-LCCN case without specifying whether the matched value is the active or the canceled LCCN — the two produce genuinely different save outcomes.

### Consortia — Version history: cross-tenant Source, permission-gated hyperlink, Shared-promotion reset (confirmed live, C692168, C692230, C692169, section 61630)

- When a Shared MARC bib record was updated by a user from a **different tenant** than the one currently viewing it, the `Source` field on that version's Card is rendered as a **hyperlink** (to the editing user's profile) if the viewing user holds permission to view users, and as **plain non-clickable text** if they don't — the displayed value is the same either way, only the clickability differs. A case for this area must check permission-gated clickability, not just Source content.
- **Promoting a Local record to Shared resets its Version history**: after `Actions > Share local instance > Share` (confirmation toast `Local instance [Instance title] has been successfully shared`), the Version history pane for the now-Shared record shows only **one** Card, regardless of how many local-tenant versions existed before the promotion — that single Card is labeled **"Shared"** (not "Original Version" and not "Current version"), with the usual `Source` hyperlink and date/time. Don't write a case asserting prior local edit history remains visible after promotion to Shared — it doesn't; a fresh single-Card history starts at the promotion point.

---

## Key Business Rules for Test Cases

1. Save-blocking (**Fail**) vs advisory (**Warn**) validation are distinct: Warn lets the user re-save as-is; Fail hard-blocks until the field is corrected. A negative case must specify which tier it's exercising. (github + cases)
2. LDR and 008 are structurally linked — an LDR/008 mismatch is its own dedicated Fail error, separate from either field's individual validation. (github)
3. Only specific LDR positions are editable for each record type (bib: 5,6,7,8,17,18,19); attempting to add/edit others is blocked with a record-type-specific message — do not reuse the bib wording for a Holdings or Authority case. (github)
4. `001`, `005`, and `999` are system-managed fields with special save-time handling (become read-only once tagged; user-added duplicates are superseded or stripped per current-release rules) — never write a case asserting a user can freely author these like ordinary fields. (cases — C380699, C496208, C380716)
5. Non-repeatable fields (010, 008, 1XX, 245, and others) are enforced with an explicit non-repeatable/multiple-field error, not a silent overwrite or silent duplicate. (cases — C380644, github)
6. A bib field controlled by a linked MARC Authority record has its subfields locked from direct edit; changing the bib's own linking-relevant heading requires unlinking all controlled fields first. (github — verify exact live behavior against a Manual/Automated linking case before asserting verbatim in a new case)
7. Missing the relevant quickMARC create/edit/derive capability hides the corresponding `Actions` menu option entirely — it is not shown-but-disabled. (cases — C422105)
8. Optimistic locking blocks saving a record that was changed/deleted by another user/session since it was opened, surfacing a dedicated conflict message rather than a generic save error. (github — pull section 27186 for a live confirmed case before writing new optimistic-locking cases)
9. Deriving a bib record from a stale/deprecated Instance version is blocked with its own message distinct from the generic save error. (github)
10. **LDR position 05 (Record status) has real cross-entity effect**: setting it to `d` (Deleted) flips the Instance's `Set for deletion`, `Suppressed from discovery`, and `Staff suppressed` flags to true; reverting to `c` only un-sets `Set for deletion` — the two suppression flags stay true until explicitly cleared on the Instance. Assert all three Instance flags, not just the LDR value. (cases — C1307997, 2025)
11. Every rule and message above is Bibliographic-specific by confirmation source — MARC Holdings and MARC Authority share the same editor shell and much of the same string vocabulary, but have field-specific rules of their own (e.g. Holdings' own required/repeatable-field set centers on 852, not 1XX/245) — read `marc-authority.md` for Authority-side rules and pull section 16714 directly before writing Holdings cases.
12. Derive treats `001`/`005` and `006`/`007` oppositely: a manually-added duplicate `001`/`005` is silently collapsed to the single system-generated value on save, while multiple `006`/`007` rows are genuinely repeatable and all persist. A derive case touching fixed fields must state which of these two behaviors it's testing — they are not interchangeable. (cases — C387459, C496210, C499607)
13. `245` is required on Derive exactly as on Create/Edit — an empty/missing `$a` blocks save with `Field 245 is required.` at Fail tier. (cases — C503056)
14. Manual linking (Create/Edit) locks a fixed subset of a linked field's boxes (tag+indicators, the authority-heading subfield, `$0`) while leaving non-heading subfields the user typed (e.g. `$t`) editable; the link action itself is via a per-field "Link to MARC authority record" icon → **Select MARC authority** modal (Browse toggle, auto-preselected heading-type filter for personal-name fields) → clicking the `Link` icon next to the highlighted result. (cases — C422126)
15. Automated linking (`Link headings` button) only auto-links a field whose `$0` value exactly matches an existing MARC Authority record's `naturalId`; non-matching fields are left for Manual linking and separately flagged in the error toast. Auto-linking preserves the field's pre-existing non-controllable subfields but strips/replaces controllable subfields with the authority's own heading content. Depends on the field's linking rule having `autoLinkingEnabled: true` (`/linking-rules/instance-authority` API). (cases — C388560)
16. Version history for a MARC Bib record opens via a clock icon (tooltip "Version history") next to `Actions`; the pane shows an exact `N version(s)` counter and one Card per version, ordered newest-to-oldest: the bottom/oldest Card = "Original Version" label, the top/newest Card = "Current version" label (bold+italic) plus a `Changed` link, and any middle Card = `Changed` link only. Each `Changed` link opens a diff modal with an `Action | Field | Changed from | Changed to` table. `Actions` is disabled while the pane is open. (cases — C663247, C692071, C692230, C692168)
17. A shared/consortia MARC Bib record can be edited directly from any affiliated Member tenant (not only Central); the save confirmation is the specific "...is in process. Changes may not appear immediately." toast, and the change (including `Record last updated` source = the actual editing user) propagates to every tenant's view of the same shared record. (cases — C405507)
18. MARC validation rules (required/repeatable field config) are per-tenant even under ECS — Central and Member tenants can hold contradicting rule sets, and a Create is validated against the rules of the tenant it's created on. A Shared-record duplicate-LCCN (`010 $a`) check hard-blocks (`Fail: 010 $a already exists.`) only against another Shared record's *active* LCCN; matching a *Canceled* LCCN is Warn-only and does not block save. (cases — C552462, C514877)
19. Promoting a Local MARC bib record to Shared resets its Version history to a single "Shared"-labeled Card — prior local-tenant version history is not carried forward into the Shared record's history view. Cross-tenant Source attribution in Version history is always shown, but is only a clickable hyperlink if the viewer holds view-users permission (otherwise same text, non-clickable). (cases — C692169, C692168, C692230)

---

## Authoring style (measured 2026-07-23)

MARC Bib / quickMARC: **`Func` ~79%** / Other ~21%, median ~8 steps, `User Journey` ~2% (~21% of cases are ≥15 steps — full edit/derive/link flows). Use `Functional`. Cases open quickMARC on a bib, edit LDR/008/controlled fields, derive a new record, link/unlink to authorities, and verify save + the Instance-side effect. Preconditions carry the source MARC bib (and any linkable authority). Longer cases walk edit→save→verify-Instance/linked-authority; field-validation and element checks stay compact.

---

## Known Gaps / Items to Verify

- [x] Fresh 2025-2026 TestRail coverage exists and was pulled on re-verification (2026-07-21) — sections 23705/23706/24360 have 30+ cases created since Jan 2025; see the LDR-position-05/Instance-suppression rule above (C1307997) as an example of real cross-entity content not derivable from GitHub translations alone. Pull more before generating cases for any specific quirky field.
- [x] Derive-specific field carry-over rules — resolved: 001/005 collapse to a single system value on save, 006/007 are genuinely repeatable and all persist, 245 stays hard-required, and Local control fields (002/004/009) carry over as-is with or without a subfield indicator (see "Derive — system-field carry-over rules" section, C503160).
- [x] Manual vs Automated linking exact step sequences and modal names — resolved for both Create AND Edit (C422126 Create, **C365134 Edit — blind-generate/diff validation round, 2026-07-22**: Edit-flow mechanics confirmed identical to Create — same modal, same locked-box breakdown, same "Personal name" preselection — plus two new confirmed nuances: the modal's `Search`/`Keyword` toggle as an alternate path to `Browse`, and the linked `$0` value's format varying between bare naturalId and full authority URI depending on the source Authority record's own identifier scheme).
- [x] Version history (section 58862) exact UI/behavior — resolved: pane structure, exact newest/middle/oldest Card labeling ("Current version" / plain `Changed` link / "Original Version"), and the diff-modal's `Action | Field | Changed from | Changed to` table are all now documented (C663247, C692071, C692230, C692168).
- [x] Consortia-specific bib editing behavior — resolved for Edit (Member-tenant direct edit, "...is in process..." toast, cross-tenant propagation — C405507), for Create (per-tenant-contradicting validation rules, Shared-record duplicate-LCCN Fail-vs-Warn severity split — C552462, C514877), and for Version history (permission-gated Source hyperlink across tenants, Version history reset to a single "Shared" Card on Local→Shared promotion — C692168, C692230, C692169).
- [ ] Manual/Automated linking mechanics have not been independently re-verified against a dedicated **Edit** (24363/24364) case — only Create (24361/24362) was directly read; treat Edit as "very likely identical" but not case-confirmed.
- [ ] Consortia **Derive** sub-flow (sections 26856/27639/28951) was not directly read — only Create (27635) and Edit (27434) consortia behavior are now case-confirmed.

> N≥10 audit round (2026-07-22): 14 cases read (C345388, C496231, C499607, C387459, C496210, C503056, C422126, C388560, C663247, C692071, C405507, C503160, C24361/24362/23706/58862/27434 section title surveys) — resolved 4 of 5 prior Known Gaps; added 6 new confirmed sections and Key Business Rules 12-17.
> Follow-up round (2026-07-22): 6 more cases read (C503160 full detail, C692168, C692230, C692169, C552462, C514877) — closed the 2 remaining residual items (Local-control-field derive behavior, Consortia Create/Version-history sub-flows); corrected the Version-history Card-labeling rule (newest = "Current version", not just oldest = "Original Version"); added Key Business Rules 18-19. Remaining open items are now narrow and specific (Edit-flow linking re-confirmation, Consortia Derive sub-flow) rather than whole unexplored areas.
