---
area: linked-data
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO Linked Data Editor (Marigold) — Business Logic Context

> Built: 2026-11-07 · Release: R2 2026 Umbrellaleaf (ui-linked-data v2.0.4 at HEAD) · Builder: build-app-context method, manual
> Sources: TestRail suite 21 section 26752 "Marigold" (LDE Editor, Bibframe API, Search, Accessibility, Integration, Accesses, RDF Import/Export, Profiles, Hubs, LD Authority — ~230 cases, titles); sections "Linked Data", "Marva Editor", "LD Authority"; GitHub folio-org/ui-linked-data (en.json, README); Jira UILD / MODLD Done issues since 2026-05.
> Case titles start with the Jira keys in brackets, e.g. "[UILD-826] PERSON - Authority profile, create/edit page" — follow that convention in this area.

## What is the Linked Data Editor

**Marigold** (UI module ui-linked-data, wrapped by ui-ld-folio-wrapper; backend mod-linked-data) is a BIBFRAME editor over a linked-data **graph**. Resources: **Work**, **Instance**, **Hub**, **Authority** (Person, Family, Organization, Meeting, Jurisdiction, Place, Temporal, Topic, Form). Instances created in Marigold become Inventory instances with source **LINKED_DATA**; MARC is derived from the graph ("View MARC"), and MARC bib/authority records can be transformed into the graph.

## UI structure

- Search page with tabs (Resources / Hubs / Authority): basic search, Advanced search (AND/OR/NOT, exact phrase, LCCN/ISBN), results set, Work preview, "Actions" for Work/Instance.
- Edit pages for Work / Instance / Hub / Authority: "Save & close", "Save & keep editing", Duplicate (titles marked "(DUPLICATE WORK)" etc.), "View MARC", "Export instance RDF file", unsaved changes modal ("Unsaved changes" / "Would you like to save your changes before proceeding?").
- Authority assignment: "Assign authority", sources "Local Marigold Authority" / "Local MARC Authority", uncontrolled-authority warning icon and modal "Uncontrolled authorities warning".
- Profiles: resource profiles (Work/Instance), "Set as my default", "Manage profile settings" with multiple named settings per profile (name must be unique), drag & drop components.
- Import: "Import resources" / "Import hubs" via JSON file or URL; import log downloaded.
- Inventory integration: "Edit in Linked data editor" in Inventory Actions (permission-gated), read-only preview for MARC-sourced instances with "Continue".

## Key Business Rules for Test Cases

1. Save toasts: "Resource created. Expect a short delay before resource is visible in FOLIO." / "Resource updated. Expect a short delay before changes are visible in FOLIO." [source] — verify the instance in Inventory after the delay (UILD-858 bug: instance created via Marigold unsearchable).
2. Main title is required: "Please add the main title in order to save."; each series needs a title [source].
3. LCCN: validated against Structure A/B when status is current/empty; duplicates with status current/empty are rejected; whitespace normalization applied (MODLD-582/583/586).
4. Assigning an authority of an unsupported type or unmapped MARC authority shows a specific error [source]; uncontrolled authorities show a warning on save (UILD-448/451/495).
5. Graph ↔ MARC mappings are tested field by field (008, 020, 040, 1XX/6XX/7XX, 130/240/630 hubs, 300, 502, 773/787) via "View MARC" — assert exact MARC fields/subfields.
6. Profile settings: several settings per profile, unique names, switching settings during editing asks to save first (MODLD-1040, UILD-780/848).
7. Standalone Authority create/edit pages per authority type; Name is required (UILD-826, MODLD-1082/1083/1107).
8. Access: without LDE permissions Inventory hides "Edit in Linked data editor"; Overlay and Set for deletion removed for LINKED_DATA instances (C503137, C566511). Marigold administrator role (C1292045).

## Permissions

ui-linked-data declares no permission sets itself; access is via the FOLIO wrapper/Inventory capabilities and a Marigold administrator role — verify names in the env.

---

## Exact UI Texts

> From `folio-org/ui-linked-data` `translations/ui-linked-data/en.json` at HEAD (2026-11-07). `{x}` are placeholders; `<b>`/`<strong>` render bold. Use verbatim.

### Toast Messages

| Key | Text | Source |
|---|---|---|
| `ld.errorFetching` | Error fetching data | [source] |
| `ld.errorLoadingResource` | Error loading resource | [source] |
| `ld.errorLoadingProfiles` | Error loading profiles | [source] |
| `ld.errorLoadingProfileSettings` | Error loading profile settings | [source] |
| `ld.errorApplyingProfileSettings` | Error applying profile settings | [source] |
| `ld.confirmCloseRd` | Do you really want to close the resource description? All unsaved changes will be lost. | [source] |
| `ld.confirmDeleteRd` | Do you really want to delete the resource description? | [source] |
| `ld.rdSaveSuccess` | Resource created. Expect a short delay before resource is visible in FOLIO. | [source] |
| `ld.rdUpdateSuccess` | Resource updated. Expect a short delay before changes are visible in FOLIO. | [source] |
| `ld.rdDeleted` | Resource description deleted | [source] |
| `ld.errorFetchingExternalResourceForPreview` | Error fetching external resource for preview | [source] |
| `ld.errorFetchingExternalResourceForEditing` | Error fetching external resource for editing | [source] |
| `ld.errorMakingApiRequest` | Error making API request | [source] |
| `ld.errorAssigningAuthority` | Error assigning authority | [source] |
| `ld.errorAssigningAuthority.not_valid_for_target` | Please select an authority with a resource type matching the edited authority field (e.g. LCNAF authority for the Creator field) | [source] |
| `ld.errorAssigningAuthority.unsupported_marc` | The selected authority isn't mapped to Linked Data, and can't be assigned yet. This is temporary, since MARC mapping is in progress. | [source] |
| `ld.errorImportingHub` | Error importing hub. Please try again. | [source] |
| `ld.modal.uncontrolledAuthoritiesWarning.title` | Uncontrolled authorities warning | [source] |
| `ld.modal.uncontrolledAuthoritiesWarning.body` | This description includes one or more uncontrolled authorities.  Do you want to save changes? | [source] |
| `ld.required_primary_main_title` | Please add the main title in order to save. | [source] |
| `ld.failed_dependency` | Unable to verify if LCCN is duplicated. | [source] |
| `ld.importFileTypeError` | You are unable to upload that file type. Please try again. | [source] |
| `ld.importFileSizeError` | Your file is too large. Please try again. | [source] |
| `ld.importFileEmptyError` | Your file is empty. Please provide a file with JSON contents. | [source] |
| `ld.importNoResourcesWarning` | Import ran successfully but no resources were imported. Review the import log or check for appropriate resource types. | [source] |
| `ld.importNoUrlError` | No URL was provided. Please try again with a URL. | [source] |
| `ld.importFileSuccess` | Your file was successfully imported and an import log file downloaded. | [source] |
| `ld.importSuccessful` | Import successful | [source] |
| `ld.importFileFailure` | Your file was unable to be imported. Please check the import log downloaded to your browser for more details. | [source] |
| `ld.importFailed` | Import failed | [source] |
| `ld.modal.chooseResourceProfile.typeProfile` | {type} profile | [source] |
| `ld.modal.chooseResourceProfile.subtitle` | Choose a resource profile to get started. | [source] |
| `ld.modal.chooseResourceProfile.setAsDefault` | Set as my default | [source] |
| `ld.modal.chooseResourceProfile.workProfile` | Work profile | [source] |
| `ld.modal.chooseResourceProfile.instanceProfile` | Instance profile | [source] |
| `ld.modal.chooseResourceProfile.setDefaultWorkProfile` | My default work profile | [source] |
| `ld.modal.chooseResourceProfile.setDefaultInstanceProfile` | My default instance profile | [source] |
| `ld.modal.chooseResourceProfile.warningTitle` | Warning: You might lose information in the following fields: | [source] |
| `ld.error.profileSaveAsPreferred` | Error setting up preferred profile | [source] |
| `ld.error.profileChange` | Error changing recording profile | [source] |
| `ld.modal.chooseProfileWarning.title` | Unable to change profile | [source] |
| `ld.modal.chooseProfileWarning.message` | You must save any changes before changing the profile. | [source] |
| `ld.required_series_title` | Please add a title to each series in order to save. | [source] |
| `ld.requiredAnnotation` | required | [source] |
| `ld.error.saveProfileSettings` | Error saving profile settings | [source] |
| `ld.error.profileSettingsNameNotBlank` | Profile settings name should not be blank, please provide a name | [source] |
| `ld.error.updatePreferredProfileSettings` | Error updating preferred profile settings | [source] |
