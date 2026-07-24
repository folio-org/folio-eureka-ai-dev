# FOLIO Organizations — Business Logic Context

> Built 2026-07-21 (browser-based). **Exact UI Texts confirmed against `folio-org/ui-organizations/translations/ui-organizations/en_US.json` (2026-07-21).** TestRail: suite 21 section 107 "Organizations" (+ Settings 121, Interface details 201, Consortium 31406). UI repo `ui-organizations`; storage `mod-organizations-storage`.

---

## What is Organizations

The Organizations app holds records for **vendors** and other external parties (donors, access providers, licensors, material/access suppliers) that the acquisitions apps reference. An organization record carries contact info, contact people, interfaces (platform admin logins), agreements, vendor-specific settings (payment/claiming/intervals/tax), EDI **integration** configs (for automated order/invoice export), accounts, and banking information. Orders, Invoices, Receiving, Agreements and eUsage all link to organizations.

---

## Key Terms

| Term | Definition |
|---|---|
| Organization | The record; may be flagged `Vendor` and/or `Donor`. |
| Vendor | An organization the library buys from (orders/invoices reference it). |
| Interface | A platform/admin endpoint with URI + credentials (for e-resource stats etc.). |
| Integration (EDI) | Config for automated order/invoice export to the vendor (EDI over FTP/SFTP, scheduled). |
| Account | A vendor account number the library uses; must be unique within the org. |
| Accounting code | External accounting-system code (a.k.a. ERP code) used on invoice export. |

---

## Record structure — accordions

`Summary`, `Contact information`, `Contact people`, `Interface`, `Agreements`, `Vendor information`, `EDI information` / `Integration details`, `Accounts`, `Banking information`, `Privileged donor information`.

**Summary fields:** `Name`, `Code`, `Description`, `Accounting code`, `Default language`, `Alternative names` (`Alias`), `Organization status` (`Active` / `Inactive` / `Pending`), `Vendor` (Yes/No), `Donor`, `Type`.
**Vendor information:** `Payment method`, `Vendor currencies`, `Claiming interval`, `Discount percent`, `Expected activation interval`, `Expected invoice interval`, `Expected receipt interval`, `Renewal activation interval`, `Subscription interval`, `Tax`, `Tax ID`, `Tax percentage`, `Liable for VAT`, `Export to accounting`.
**Accounts:** `Name`, `Account number`, `Accounting code`, `Payment method`, `Account status`, `Library code`, `Library EDI code`.

---

## Exact UI Texts [all confirmed — ui-organizations en_US.json]

### Toasts
| Event | Text |
|---|---|
| Organization saved | `The Organization - "{organizationName}" has been successfully saved` |
| Organization deleted | `The organization {organizationName} was successfully deleted` |
| Contact saved / unassigned / deleted | `The contact was saved` / `The contact was unassigned` / `The contact was deleted` |
| Interface saved | `The interface was saved` |
| Integration saved / deleted / duplicated | `Integration was saved` / `The integration was successfully deleted` / `Integration {term} was successfully duplicated` |

### Create / delete / confirm modals
| Modal | Text |
|---|---|
| Create | `Create organization` (edit: `Edit - {name}`) |
| Delete organization | `Delete {organizationName}?` / `Delete organization?` → `Delete` |
| Vendor-data deletion warning | `Confirm vendor data deletion` / `Warning. All vendor information, vendor terms, EDI information, and accounts will be deleted from this record.` |
| Unassign contact/interface | `Unassign from organization` / `Are you sure you want to unassign the contact from this organization?` |
| Delete contact / interface | `Delete contact` / `Are you sure you want to delete the contact?`; `Delete interface` / `Are you sure you want to delete the interface?` |
| Delete integration | `Confirm integration deletion` / `Are you sure you want to delete the integration?` |
| Duplicate integration | `Duplicate integration config` / `Are you sure you want to duplicate the {term} integration config?` |

### Errors / validation
| Condition | Message |
|---|---|
| Org save (generic) | `Organization could not be saved` |
| Code duplicate | `Code is already in use` |
| Duplicate account numbers | `An organization can not have duplicate account numbers` (view banner: `An organization can not have duplicate account numbers. Before editing this organization in any way you will need to change or remove any duplicate account numbers`) |
| Credentials save | `Error while saving credentials` |
| No primary record | `No primary record selected` |

### Integration (EDI) config — key fields
`Integration name`, `Description`, `Default integration`, `Integration type` (`Ordering` / `Claiming`), `Transmission method` (`File download` / `FTP`), EDI config (`Account numbers`, `Vendor EDI code`, `Vendor EDI type`, `Library EDI code`, `Library EDI type`, `EDI naming convention`, `Automate order export for acquisition methods`, expected messages `Orders`/`Invoices`), FTP details (`FTP mode`, `Server address`, `FTP connection mode` Active/Passive, `FTP port`, `Order directory`, `Invoice directory`), Scheduling (`Schedule EDI`, `Schedule period` Hourly/Daily/Weekly/Monthly, `Time`, `Day`).

### Settings [confirmed]
`Categories`, `Types` (with delete guards `This category/type cannot be deleted, as it is in use by one or more records.`), `Banking information` → `Account types` (`Account type must be unique.`), `Number generator options` (`Vendor code generator`; `Off` / `On, field editable` / `On, field not editable`).

---

## Capability Sets (Eureka) [confirmed permission display names]

| Action | Permission |
|---|---|
| View | `Organizations: View` |
| View, edit | `Organizations: View, edit` |
| View, edit, create | `Organizations: View, edit, create` |
| Delete | `Organizations: View, edit, delete` |
| View interface credentials | `Organizations: Interface usernames and passwords: view` |
| Manage interface credentials | `Organizations: Interface usernames and passwords: view, edit, create, delete` |
| Integration credentials | `Organizations: Integration usernames and passwords: view` / `…: view, edit` |
| Banking info | `Organizations: View banking information` … `… create and delete banking information` |
| Privileged donor info | `Organizations: can view privileged donor information` / `… create, edit, delete …` |
| Assign acq units | `Organizations: Assign acquisition units to new organization` |
| Manage acq units | `Organizations: Manage acquisition units` |
| Settings | `Settings (Organizations): View settings` / `… Can view and edit settings` |

---

## Common Verification Patterns

### Create a vendor
1. Actions → `New`/`Create organization`; fill `Name`, `Code`, set `Organization status`, check `Vendor` → `Save & close`.
2. Expected: toast `The Organization - "{name}" has been successfully saved`; record shows in list with the code; `Code is already in use` if the code collides.

### Add an interface with credentials
Interface accordion → `Add interface` (or find-interface plugin) → `Name`, `URI`, `Username`, `Password` → Save. Credentials view/edit gated by the interface-credentials capability; toggle `Show credentials` / `Hide credentials`.

### EDI integration for automated order export
Integration details → `Add integration` → `Integration type = Ordering`, EDI codes, FTP details, `Schedule EDI` period → Save (`Integration was saved`). This drives Export Manager order export.

### Verify a scheduled EDI export actually ran (confirmed pattern, C965832, 2025)
Don't stop at saving the integration's schedule — verify the export itself fires and lands: open an eligible Order (Actions → Open), wait for the scheduled time, then go to the **Export Manager** app → check the `Organizations` toggle on Search & Filter → filter `Integration type = Orders` → confirm a job in `Successful` status with start/end time matching the integration's schedule. A case that only checks "Integration was saved" without this step doesn't prove the export actually happens.

---

## "Save & Keep Editing" Button (Create/Edit Organization) [confirmed — C656329]

Same three-button pattern used across other acquisitions apps (Invoices, etc.): `Cancel` (always active), `Save & keep editing` (disabled until ≥1 field filled), `Save & close` (same enable condition). Save & keep editing runs the same mandatory-field validation without closing the screen; on success it shows a toast and, notably, **focus remains in the last-clicked field** (post UIORGS-449) rather than resetting to the top of the form.

## Version History (Organizations) [confirmed — C663330]

Same clock-icon / 4th-pane mechanic as Invoices (see invoices.md): most-recent-first cards, oldest = "Original version", newest = "Current version" + a "Changed" list of field/accordion names. Organizations-specific nuances:
- **"Privileged donor information" and "Agreements" accordions are NEVER shown in Version History, for any version card** — these stay hidden regardless of which historical version is selected (privacy/external-link exclusion, not a diff artifact).
- Each version accurately reflects that point in time's accordion CONTENTS, not just a highlighted diff: if Contact people/Interface entries were deleted in the latest edit, the current version's accordions literally show "The list contains no items", while the changed field name (e.g. "Interface", "Contact people", "Vendor") still appears in that card's "Changed" list.
- Checking the "Vendor" checkbox in an edit is tracked like any other field change — the checkbox itself is highlighted yellow on the details pane, and newly-revealed Vendor-only accordions (Vendor information, Vendor terms, Accounts) appear for that version.

## Number Generator for Organization Code [confirmed — C700855; previously undocumented]

Settings > Organizations > Number generator options has three modes (already listed as a settings item, behavior not previously detailed):
- **Off**: no "Generate vendor code" button appears on either Create or Edit pages.
- **On, field not editable**: a "Generate vendor code" button appears under the Code field on Create (and Edit); clicking opens a "Vendor code generator" window to search/select a configured sequence, then generates the next number into Code — which subsequently **cannot be manually edited** (no prefix/suffix appending allowed).
- **On, field editable**: identical generation flow, but the generated value in Code CAN be manually edited afterward (e.g. to append a prefix/suffix).
- Requires: user has the `NumberGenerators` authorization role, and a sequence is defined under Settings > Service interaction > Number generator sequences for Generator "Organizations: Vendor code".
- Re-generating a new number on an already-saved organization (via Edit) works the same way and simply overwrites the previous Code value.

## Integration Create/Edit — Dynamic Field Requirements Matrix [confirmed — C688767, C825311, C434063; significantly expands prior "key fields" list]

The Create/Edit Integration form has interlocking conditional-required logic across three fields — **Integration type**, **Transmission method**, and **File format** — that is NOT simply "Ordering requires everything":

- Default state on Create: `Integration type = Claiming`, `Transmission method = File download`, `File format = CSV`; Account numbers optional; no EDI/FTP fields required; **Scheduling accordion is hidden entirely**.
- Selecting `Integration type = Ordering` forces (and locks/disables) `Transmission method = FTP` and `File format = EDI`, makes Account numbers + Vendor EDI code + Library EDI code + Server address + FTP port all REQUIRED, and reveals the **Scheduling** accordion (Schedule EDI unchecked by default). Switching back to Claiming unlocks Transmission method/File format again but preserves whatever value they currently hold and hides Scheduling again.
- Independent of Integration type, **File format alone drives EDI-code requiredness**: File format = EDI ⇒ Account numbers/Vendor EDI code/Library EDI code required; File format = CSV ⇒ all three become NOT required.
- Independent of both, **Transmission method alone drives FTP-field requiredness**: Transmission method = FTP ⇒ Server address/FTP port required; Transmission method = File download ⇒ NOT required.
- `Day` field (only shown when Schedule period = Monthly) validation: numeric, range 1–31 inclusive. Blank → `Required`; > 31 → `Value must be less than or equal to 31`; negative → `Value must be greater than or equal to 1`. Save & close is blocked while any such message is displayed. [C434063]
- **Duplicate integration**: modal `Duplicate integration config` (`Are you sure you want to duplicate the {term} integration config?`) → Cancel/Confirm → toast `Integration ({date, time AM/PM}) was successfully duplicated` → new record named exactly `Copy of ({date, time AM/PM})`, carrying over every field (including FTP credentials and Schedule settings) EXCEPT **Account numbers**, which is cleared and must be re-selected on the duplicate. [C688767]
- A background OAuth token-refresh call to `authn/refresh` can fire while the Create-integration form is still open (observed in DevTools Network tab); this does not interrupt or invalidate the in-progress form — Save & close still succeeds normally afterward. [C825311]

## Privileged Donor Contacts — Search Isolation [confirmed — C423630; previously undocumented]

A contact added via the "Privileged donor information" accordion's own "Add donor" > "New" flow is entirely invisible to the regular "Contact people" accordion's "Add contact" picker — searching that picker for the donor contact's name (or any other privileged-donor-only contact) returns `0 records found` / `No results found for "{query}". Please check your spelling and filters.` This is a hard search-index exclusion, not merely a permission-based hide, and holds even for a user who has full edit rights on both privileged-donor and contact-people data.

## Banking Information — Tenant-Level Kill Switch [confirmed — C423547; refines existing capability table]

When Settings > Organizations > Banking information > "Enable banking information" is **unchecked** at the tenant level, the "Banking information" accordion is completely absent from BOTH the View and Edit pages for every user — including a user holding every individual Organizations banking permission (view, view+edit, create, delete, all of them). The tenant setting is a hard kill switch; per-user banking permissions are irrelevant while it's off.

## Bank Account Type — Delete Guard [confirmed — C590820]

Deleting an Account type (Settings > Organizations > Account types) that's currently referenced by ANY organization's Banking information record is blocked by a second, non-dismissible-looking popup after the initial confirm: first `Delete account type` (`The account type will be deleted.` Cancel/Delete), then on Delete a SEPARATE `Cannot delete account type` popup appears — `Unable to delete. Account type is in use by one or more organizations.` with only an `Okay` button — the type is NOT deleted.

## Vendor / Donor Toggle — Side Effects [confirmed — C730, C421981; refines Key Business Rule 1]

- Checking "Vendor" in Edit mode immediately (pre-save) reveals Vendor information / Vendor terms / Accounts accordions and activates Save & close; after the save completes, an **Integration details** accordion also appears — Integration details is Vendor-gated exactly like the other three, not shown separately.
- The "Donor" checkbox is disabled (non-interactive) on the View pane for a non-donor organization — it can only be toggled from Edit mode.
- Unchecking "Donor" and saving immediately drops that organization from any active "Is donor = Yes" search-filter result set — the facet re-evaluates live rather than showing stale membership.

## "Add Contacts" / "Add Donors" Picker — Pagination & Bulk Selection [confirmed — C359169, C422163]

Both pickers (Contact people's "Add contact" and Fund's Donor-information "Add donor", and by extension any similar plugin-search picker in this app) share one pagination/selection pattern:
- 50 records per page; the header "Select all" checkbox selects only the CURRENT page's up-to-50 rows, not every matching record across all pages.
- The running "Total selected" counter persists correctly across Next/Previous navigation — selections made on an earlier page remain selected (and their checkboxes show as checked again) when paging back to them.
- Deselecting a single record while "Select all" was active flips the page-level "Select all" checkbox back to unchecked, without altering any other already-selected record.
- The picker's `Save` button only activates once at least one record is selected, regardless of which page is currently displayed.

---

## Key Business Rules for Test Cases

1. An organization is only a **vendor** when the `Vendor` flag is set — only vendors are selectable in Orders/Invoices vendor fields. (github + orders/invoices)
2. **Organization code must be unique** — duplicate code blocks save with `Code is already in use`. (github)
3. **Account numbers must be unique within an organization**; a record with duplicate accounts is locked from editing until fixed. (github)
4. Deleting a vendor's data (or the org) triggers the `Confirm vendor data deletion` warning — vendor info, terms, EDI info, and accounts are all removed. (github)
5. Interface and integration **credentials are separately permissioned** from the org record; a user may view an org but not its usernames/passwords. (github)
6. The vendor's `Claiming interval` seeds the Receiving title's claiming interval; expected receipt/invoice/activation intervals drive acquisitions expectations. (github + receiving.md/orders.md)
7. EDI integration config (type Ordering/Claiming, FTP, schedule) enables automated order/invoice export via Export Manager. (github)
8. Contacts and interfaces can be **assigned/unassigned** (shared) vs **deleted**; unassign removes the link, delete removes the record. (github)
9. Acquisition units gate org access the same way as other acq records (assign on create vs manage on edit are distinct capabilities). (github)
10. `Donor` organizations feed the donor-information fields used on order lines; privileged donor info is separately permissioned. (github + orders.md)
11. **EDI integration `Schedule EDI` Time is a tenant-timezone display value, but is transmitted/stored as UTC.** Changing `Settings > Tenant > Language and localization > Time zone` changes how the same stored schedule reads in the Integration's `Time` field, while the backend response (`/data-export-spring/configs/`) always shows `scheduleParameters.timeZone: "UTC"` with `scheduleTime`/`schedulingDate` in UTC. A timezone-sensitive case must check both the UI display value (changes with tenant timezone) and the API/DB value (always UTC) — checking only one proves nothing about the other. (cases — C965832, 2025)
12. A scheduled EDI export's real effect is a job row in **Export Manager** (`Organizations` toggle, `Integration type` filter), not just the saved Integration config — verify the job actually ran and succeeded, per this skill's "verify effects at their real destination" rule. (cases — C965832)
13. Integration required-field logic is driven independently by File format (EDI vs CSV → EDI-code requiredness) and Transmission method (FTP vs File download → FTP-field requiredness); Integration type = Ordering merely locks both to their EDI/FTP combination and reveals Scheduling — it isn't itself the source of the requiredness rules. (cases — C688767)
14. Duplicating an Integration carries over every field including FTP credentials and Schedule settings EXCEPT Account numbers, which is always cleared on the copy. (cases — C688767)
15. Privileged donor contacts are fully excluded from the general Contact-people search index, not merely hidden by permission — they cannot be found by any user via the standard Add-contact picker. (cases — C423630)
16. The tenant-level "Enable banking information" setting is a hard kill switch: when off, the Banking information accordion disappears for every user regardless of their individual banking permissions. (cases — C423547)
17. Bank Account types in use by any organization's Banking information cannot be deleted — a second blocking popup (`Cannot delete account type`) appears even after the initial delete confirmation is accepted. (cases — C590820)
18. Version History for an Organization never displays the Privileged donor information or Agreements accordions for any version, and otherwise reflects each version's true point-in-time accordion contents (e.g. showing "The list contains no items" where applicable) rather than a pure diff overlay. (cases — C663330)
19. "Add contact"/"Add donor" pickers paginate at 50 records; bulk selection state (including the running "Total selected" count) persists correctly across Next/Previous navigation, and "Select all" only ever applies to the currently displayed page. (cases — C359169, C422163)
20. The **"Date created"** search facet's `From`/`To` range is evaluated against the record's actual creation timestamp in the **tenant's configured timezone**, not UTC or the browser's local time — an org created just before local midnight falls in "yesterday", one created just after falls in "today", even though both timestamps may be close together in UTC. A timezone-boundary test for this facet must set a non-default tenant timezone and create records straddling that timezone's midnight, per the same UTC-vs-tenant-timezone caution already noted for EDI scheduling (Rule 11). (cases — C466130)

---

## Authoring style (measured 2026-07-23)

Organizations: **`Func` ~85%** / Other ~15%, median ~8 steps, `User Journey` ~15% (one of the higher journey-flag areas). Cases are record-CRUD and accordion management (summary, contacts, interfaces, integrations/EDI, accounts, banking, privileged donor) plus Settings. Use `Functional`. Journey-flagged cases walk a multi-accordion setup or an integration→Export-Manager effect. Verify effects at their real destination (a scheduled EDI export = a job row in Export Manager, not just the saved config). Preconditions carry the org record with the relevant accordion populated and any tenant-level kill-switch settings.

---

## Known Gaps / Items to Verify

- [x] TestRail section 107 cases pulled this round (14 cases) for realistic precondition depth/style — organization delete, Save & keep editing, Version history, Number generator, Integration dynamic-requirements matrix, privileged-donor search isolation, banking kill-switch, account-type delete guard, Vendor/Donor toggle side effects, and picker pagination are now all documented above with exact strings.
- [ ] Exact Eureka capability-set strings (`UI-Organizations …`) — permission display names confirmed; verify the capability-set form in env.
- [ ] Interface find-plugin vs inline-create exact flow labels (`find-interface plugin` vs `Add interface`) — verify which the target release uses.
- [ ] Whether "Save & keep editing" is available on Edit (not just Create) was implied by C656335's title but not independently re-verified this round — cross-check against the Invoices/other-areas pattern where it IS available on both.

> N≥10 audit round (2026-07-22): 14 cases read (C613152, C656329, C663330, C700855, C688767, C825311, C434063, C423630, C423547, C590820, C730, C421981, C359169, C422163). This was the file's first pull directly from TestRail section 107 (previously GitHub-translation-only) — resolved that Known Gap. Surfaced entirely new/previously undocumented features: Version History, Number Generator for Organization Code, the Integration form's dynamic required-field matrix (File format vs Transmission method vs Integration type, independently), Privileged-donor contact search isolation, the Banking-information tenant kill switch, the Account-type delete guard, and the Add-contact/Add-donor picker's cross-page bulk-selection mechanic. Added 8 new Key Business Rules (12-19).

> Random spot-check (2026-07-23): picked one fresh uncited case at random from section 107 (C466130) — found the "Date created" facet's timezone-aware midnight-boundary behavior was undocumented. Added Key Business Rule 20.
