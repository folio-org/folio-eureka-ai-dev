---
area: export-manager
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO Export Manager (+ EDIFACT order export) — Business Logic Context

> Built: 2026-11-07 · Release: R2 2026 Umbrellaleaf (ui-export-manager v5.1.0 at HEAD) · Builder: build-app-context method, manual
> Sources: TestRail suite 21 section 11061 "Export Manager" + Export Orders in EDIFACT format 17492, Orders Export to a Vendor 17493, Settings 72797 (~70 cases, titles); GitHub folio-org/ui-export-manager (en.json — complete, 60 keys; package.json); Jira UIEXPMGR / MODEXPS Done issues since 2025-11. Related: `orders.md` (automatic export, acquisition method), `organizations.md` (integration details, scheduling), `claiming.md`.

## What is Export Manager

The **Export manager** app lists **export jobs** produced by other apps and schedulers: Circulation log, Bursar, eHoldings, Authority control (MARC authority headings updates, Failed updates: Linked bibliographic fields), Orders (EDI / CSV) and Claims. Tabs: **All** and **Organizations** (EDIFACT order / claim exports per vendor integration). Jobs can be downloaded; organization jobs can be **resent** (same file) or **rerun**.

## Job model (en.json)

- Status: Scheduled, In progress, Successful, Failed.
- Job types (list): Circulation log, Bursar, eHoldings, Authority control, Orders (EDI), Orders (CSV); detail types incl. "EDIFACT orders export", "MARC authority headings updates", "Failed updates: Linked bibliographic fields".
- Fields: Job ID, Status, Job type, Output type, Description, Source, Start time, End time, Error details, Organization, Export method, Sent to, File name, Integration type (Orders / Claims).
- Settings: "Job deletion intervals (days)" per job type.

## EDIFACT order export rules (from cases)

1. A POL is exported only if the PO is not Manual, the POL has **Automatic export** enabled, and the POL acquisition method matches the integration's acquisition methods (C350395–C350404, C350604).
2. Opening an order whose POLs map to more than one vendor account for export shows an alert (C350410, C350434).
3. Two integrations of one organization cannot share an account number (C350552; see UIORGS-481 warning).
4. Scheduling: Hourly / Daily / Weekly / Monthly; export time is the time chosen in the UI; disabled scheduler stops jobs (C350595–C423529, C359161).
5. Download / resend the exact ".edi" file, including Failed jobs and files older than one day (C365604, C365605, C368040).
6. Jobs are deleted automatically after the configured deletion interval, per tenant in ECS (C784505, C813001, C813000).
7. EDIFACT message: UNH and UNT reference numbers match (C430228); currency different from default is exported (C523775).

## Permissions

| Okapi permission (package.json) | Notes |
|---|---|
| Export manager: View | sees jobs, cannot download (C405555) |
| Export manager: Download and resend files | |
| Export manager: All | eHoldings and Authority control downloads need additional capabilities (UIEXPMGR-132/135, C1263891) |
| Settings (Export manager): Can view only settings / Can view and edit settings | deletion intervals read-only for view-only (C813000) |

Eureka capability set names — not confirmed in cases read (verify).

## Key Business Rules for Test Cases

1. Landing page stays empty until a filter is selected (C380489).
2. Download/rerun/resend toasts: "Your file upload has started successfully.", "Export job {name} was successfully rerun.", errors "Your file download was failed." / "Your file upload was failed." / "Export job {name} rerun was failed." [source].
3. Default integration with SFTP can be saved without vendor account numbers (bug MODEXPS-322 fixed). (jira)
4. Claims jobs appear on the Organizations tab with Integration type = Claims (see `claiming.md`).

---

## Exact UI Texts

> From `folio-org/ui-export-manager` `translations/ui-export-manager/en.json` at HEAD (2026-11-07). `{x}` are placeholders; `<b>`/`<strong>` render bold. Use verbatim.

### Toast Messages

| Key | Text | Source |
|---|---|---|
| `exportJob.errorDetails` | Error details | [source] |
| `exportJob.status.SUCCESSFUL` | Successful | [source] |
| `exportJob.status.FAILED` | Failed | [source] |
| `exportJob.details.type.FAILED_LINKED_BIB_UPDATES` | Failed updates: Linked bibliographic fields | [source] |
| `exportJob.details.action.download.error` | Your file download was failed. | [source] |
| `exportJob.details.action.rerun.error` | Export job <b>{name}</b> rerun was failed. | [source] |
| `exportJob.details.action.resend.error` | Your file upload was failed. | [source] |
| `exportJob.details.action.resend.success` | Your file upload has started successfully. | [source] |
| `exportJob.details.action.rerun.success` | Export job <b>{name}</b> was successfully rerun. | [source] |
| `settings.jobs.update.success` | {count, plural, one {Deletion interval for <b>{entities}</b> was successfully updated} other {Deletion intervals for <b>{entities}</b> were successfully updated}}. | [source] |
| `settings.jobs.update.error` | {count, plural, one {Deletion interval for <b>{entities}</b> was not updated} other {Deletion intervals for <b>{entities}</b> were not updated}}. | [source] |
