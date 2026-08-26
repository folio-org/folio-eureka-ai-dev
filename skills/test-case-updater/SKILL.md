---
name: test-case-updater
description: >-
  Use when a phrase, term, or wording needs to be replaced across many existing TestRail
  test cases in a FOLIO module — a renamed UI label, a corrected term, a typo fix. Finds
  matching cases, previews every change, archives pre-release cases to a target section
  before editing them, and optionally appends a Jira reference. Also use to set metadata
  fields — priority, release, test group, automation type — across many cases at once.
  Works with any FOLIO module (Bulk Edit, Lists, Users, Data Export, and others). Do NOT
  use for writing new test cases (use write-testrail-cases) or for editing a single known
  case.
license: Apache-2.0
metadata:
  author: folio-org
  version: "3.0.0"
---

# TestRail Phrase Updater

> **Core principle:** never mutate TestRail before a rendered preview has been shown and explicitly confirmed. The preview is not optional and cannot be turned off.

## Overview

Replaces a phrase across existing test cases in one FOLIO module. Pre-release cases are first copied to an archive section so the old wording survives for historical releases, then the originals are updated in place. Current-release cases are updated in place only.

This skill performs the TestRail API calls directly. There is no script to run and no flag to set — the workflow below is the contract.

---

## When to Use

Use when:

- a UI label changed and many cases quote the old label;
- a term was corrected and the old term is spread across a section;
- a phrase must be updated *and* a Jira reference appended to the affected cases;
- pre-release wording must be preserved before current cases are edited;
- a metadata field must be set across many cases — priority, release, test group, automation type — either alongside a phrase replacement or on its own.

Do not use when:

- writing new test cases — use `write-testrail-cases`;
- editing one case whose ID is already known — edit it directly;
- the change requires human judgement per case rather than a uniform replacement.

---

## Hard Rules

- **Never mutate TestRail before the preview is confirmed.** No exceptions, no flags.
- **Never ask the user for credentials** — resolve them silently from the chain below.
- **Never treat a substring match as a match.** See Step 6 — this is the most common failure.
- **Never identify an existing copy by title.** Titles repeat across sections; use the `src:` stamp.
- **Never guess a bucket for a case with no release value.** Surface it and ask.
- **Never skip a failure silently.** Log the case ID and the full error, then continue.
- One module per run. Do not batch modules together.

---

## Mandatory Workflow (follow in this exact order)

### Step 1 — Detect the module

Infer the module from the request. If unclear, ask: *"Which FOLIO module (e.g. Bulk Edit, Lists, Users)?"*

### Step 2 — Load the module config

Read the config for the module from the Module Configs table below. If none exists, say so and offer to build one from [references/config-template.md](references/config-template.md). Do not invent section IDs.

Extract: source section IDs, target (archive) section ID, release threshold, `project_id`, `suite_id`.

### Step 3 — Gather search and replace inputs

Ask for:

- the phrase to find — plain text or regex;
- the replacement;
- an optional Jira reference to append (e.g. `UIBULKED-649`), or none;
- any metadata fields to set — priority, release, test group, automation type — or none;
- optionally, a release to stamp on the **archived copies**. Default is to keep whatever release the original had, which is usually what you want — the copy exists to record the wording as of that release.

At least one of *replacement* or *metadata change* must be given, otherwise there is nothing to do.

**Metadata-only runs** are allowed: leave the phrase empty and every case in the configured source sections is selected. State the resulting count plainly in the preview — this is a much wider blast radius than a phrase match, and it is the one path where a confirmation covers hundreds of cases at once.

Metadata values must be **numeric option IDs**, not labels. Resolve them with `get_case_fields` before the preview — see the Field reference table under TestRail API Integration.

### Step 4 — Read credentials

Resolve credentials using the chain in the Credentials section below. If they cannot be resolved, report which keys are missing and stop.

### Step 5 — Fetch all cases (paginated)

Fetch every case in each source section, following the pagination rule in Fetch cases below. ⚠️ Large sections are slow — process each page as it arrives rather than accumulating all pages first.

Also fetch the target section so already-archived cases can be detected in Step 7.

### Step 6 — Match, excluding already-replaced text

Search these fields on every case:

| Field | Notes |
|---|---|
| `title` | |
| `custom_preconds` | |
| `custom_steps_separated[].content` | Structured steps — the common case |
| `custom_steps_separated[].expected` | |
| `custom_steps` | **Legacy plain-text steps.** Rare but real — a match here is silently lost if not checked |
| `custom_expected` | Legacy expected result |

Report a per-field hit count so a legacy-field match is never invisible.

> **Match with word boundaries, not substrings.** A plain "contains" test is wrong whenever the search phrase is a prefix of its replacement — which is exactly the singular→plural case this skill is most often used for. Searching `Preview of record` as a substring matches `Preview of records`, so every already-corrected case re-matches on every run, inflating counts and producing no-op writes. Use `\bPreview of record\b`, which correctly fails against `records` because there is no word boundary before `s`.

Then subtract: exclude any case where the **replacement** already appears in the same field. Count these separately as *already correct* — they are not matches and must not be updated.

### Step 7 — Categorize by release

| `custom_release` | Bucket | Action |
|---|---|---|
| `>= threshold` | Current | Update in place |
| `< threshold` | Pre-release | Copy to archive section, then update the original |
| `null` | **Undetermined** | Do not guess — list separately in the preview and ask |

A pre-release case is **already archived** if any case in the target section carries `src:C<original_id>` in its `refs`. Do not compare titles.

> **Bucket on the original release value, before applying any release change.** If the run also sets `custom_release`, categorizing on the new value would reclassify cases mid-run — a case being moved from 19 to 21 must still be archived as pre-release, because the wording being preserved is the wording it had at release 19. Read the bucket first, write the new release second.

### Step 8 — Render the preview

Show exactly this shape, with real numbers and 3–5 real before/after samples:

```
Ready to update 82 cases in Bulk Edit - Items (section 19563)?

   61 pre-release (release < 20)  → copy to 65470, then update original
   21 current     (release >= 20) → update in place
    3 no release set              → NEEDS DECISION, excluded for now
   19 already contain "Preview of records" → skipped, not a match
    7 already archived (src: stamp found)  → copy skipped, original still updated

Sample 1 of 3 — C359006 (release 17, pre-release)
  title:   - Verify populating Item records in "Preview of record" matches
           + Verify populating Item records in "Preview of records" matches
  steps:   2 occurrences in custom_steps_separated
  refs:    + UIBULKED-649

Metadata applied to all 82 cases:
  custom_test_group:  3 (Extended) → 2 (Critical Path)
  custom_release:     unchanged

Confirm? (yes / no / edit)
```

Show the metadata block only when metadata changes were requested, and always resolve IDs to their labels in the preview — `2` alone is unreviewable, `2 (Critical Path)` is.

### Step 9 — Wait for explicit confirmation

Wait for `yes`. On `edit`, revise the inputs and re-render the full preview. On `no`, stop without writing. Never proceed on silence or ambiguity.

### Step 10 — Execute

Per case:

- **Pre-release** — copy to the archive section, append `src:C<original_id>` to the copy's `refs`, then update the original.
- **Current** — update in place. ⚠️ There is no archive copy for these, so the pre-edit wording survives only in TestRail's own case history. Recovering a bad replacement means reading history case by case.
- Replace the phrase in every field listed in Step 6.
- Set any requested metadata fields, sending numeric option IDs. Include them in the same `update_case` call as the phrase replacement — one write per case, not two.
- Append the Jira ref if given and not already present.
- Sanitize NBSP (` `) and control characters introduced by the replacement.

> **The copy and its stamp are two separate calls.** If the copy succeeds but the stamp fails, an unstamped copy exists and the next run will copy the case again. Do not treat such a case as archived — log the new case ID as needing a manual `src:` stamp and leave the original unmodified, so the pair can be completed by hand.

On a per-case failure, log it and continue. Do not abort the run.

### Step 11 — Report

Write a run log to `testrail-update-<module>-<YYYY-MM-DD>.md` containing:

- timestamp, module, search phrase, replacement, ref appended;
- the **original → copy ID map** for every archived case;
- per-case outcome (copied, updated, skipped with reason, or errored);
- totals: matched, pre-release, current, undetermined, copied, updated, skipped, errors;
- full error text for anything needing manual follow-up.

The ID map is what makes a rerun safe — preserve it.

---

## Module Configs

| Module | Config file | Status |
|---|---|---|
| Bulk Edit | [references/config-bulk-edit.md](references/config-bulk-edit.md) | Complete |
| Any other module | — | Create from [references/config-template.md](references/config-template.md) |

A worked run is in [references/example.md](references/example.md).

---

## TestRail API Integration

### Credentials

Read credentials using this fallback chain (try in order, stop at first hit):

1. `.env` file in the repository root — parse KEY=VALUE pairs
2. `~/.folio-credentials` — legacy local file
3. Environment variables — for CI/Codespaces

Keys to read:
```
TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_API_KEY
```

Never ask the user for credentials — try all three silently. If all three fail — report which keys are missing and stop.

All requests use `Authorization: Basic base64(TESTRAIL_USER:TESTRAIL_API_KEY)`.

### Fetch cases

```
GET {TESTRAIL_URL}/index.php?/api/v2/get_cases/{project_id}&suite_id={suite_id}&section_id={section_id}&limit=250&offset=0
Authorization: Basic base64(TESTRAIL_USER:TESTRAIL_API_KEY)
```

The response envelope is `{offset, limit, size, _links: {next, prev}, cases: [...]}`. **Paginate (increment offset by 250) until `_links.next` is null.** `size` is the count on the current page, not the total — never treat a single response as complete.

⚠️ Paged reads can fail intermittently. Observed on 2026-08-19 while the instance was slow: 6–9s per page, the same request returning `504` on one attempt and `200` on the next, and occasional connection drops with no status at all. Treat these as transient, whatever the cause:

- Retry the same `offset` up to 3× with 2s/4s/8s backoff. Treat a connection drop like a `504`, and never read an empty body as an empty page.
- If a page still fails, **stop and report the last good `offset`.** Never continue past a gap — a missing page shrinks the match set and the run reports success having never seen those cases.
- Keep `limit=250`. Page size does not affect reliability — `limit=100` and `limit=250` both succeeded 5/5 at comparable speed — so lowering it only adds round-trips.

### Copy a pre-release case

```
POST {TESTRAIL_URL}/index.php?/api/v2/copy_cases_to_section/{target_section_id}
Content-Type: application/json
Authorization: Basic base64(TESTRAIL_USER:TESTRAIL_API_KEY)
```

```json
{ "case_ids": [359006] }
```

This preserves custom fields, structured steps, labels and refs server-side — do not reconstruct them by hand. The response carries the new case IDs; record them in the run log immediately, then stamp each copy:

```
POST {TESTRAIL_URL}/index.php?/api/v2/update_case/{new_case_id}
```
```json
{ "refs": "UIBULKED-119,UIBULKED-162,src:C359006" }
```

`refs` is a comma-separated string. The `src:` prefix namespaces the stamp so it is distinguishable from Jira keys and greppable on rerun.

If a release override for archived copies was requested in Step 3, send it in this same call rather than adding a third write:

```json
{ "refs": "UIBULKED-119,UIBULKED-162,src:C359006", "custom_release": 19 }
```

Omit `custom_release` to keep the release the copy inherited from the original — the usual case, since the copy's purpose is to record the wording as of that release.

> **Fallback only if `copy_cases_to_section` is unavailable:** `get_case` then `add_case`, explicitly carrying `title`, `type_id`, `priority_id`, `refs`, `labels`, `custom_preconds`, `custom_steps_separated`, `custom_steps`, `custom_expected`, `custom_release`, `custom_test_group`, `custom_automation_type`, `custom_dev_team`, `custom_case_automated_in`. Omitting any of these silently drops data.

### Update a case

```
POST {TESTRAIL_URL}/index.php?/api/v2/update_case/{case_id}
Content-Type: application/json
Authorization: Basic base64(TESTRAIL_USER:TESTRAIL_API_KEY)
```

```json
{
  "title": "Verify populating Item records in \"Preview of records\" matches",
  "custom_preconds": "1. User is on Bulk edit pane\n2. Item records are uploaded",
  "custom_steps_separated": [
    {
      "content": "Click \"Preview of records\" accordion",
      "expected": "Accordion expands; first 10 records are displayed"
    }
  ],
  "refs": "UIBULKED-119,UIBULKED-649"
}
```

Send only the fields being changed. `update_case` replaces the whole value of each field it receives, so `custom_steps_separated` must be sent complete, not as a partial array.

### Field reference

Verified on `foliotest.testrail.io`, project `14`:

| Field | Type | Option IDs |
|---|---|---|
| `custom_release` | dropdown | `21` R2 2026 Umbrellaleaf · `20` R1 2026 Trillium · `19` R1 2025 Sunflower · `18` R2 2024 Ramsons · `17` R1 2024 Quesnelia · `16` R2 2023 Poppy · descending to `1` Q1 2019 |
| `custom_test_group` | dropdown | `1` Smoke · `2` Critical Path · `3` Extended · `4` Obsolete · `5` Draft · `6` Backend · `7` Edge Cases |
| `refs` | string | Comma-separated |

> **Resolve IDs at runtime.** Dropdown fields take a numeric option ID, not the label — sending a label returns `400 Field :<name> is not a valid natural number`. Confirm current IDs with `GET /index.php?/api/v2/get_case_fields` before relying on the table above.

### Success output

```
✅ Updated 82 cases in Bulk Edit - Items:
  61 archived to 65470 (C1395081–C1395141)
  82 originals updated, UIBULKED-649 appended
  19 skipped (already correct)
   0 errors
Run log: testrail-update-bulk-edit-2026-08-19.md
```

### Error handling

| HTTP status | Action |
|---|---|
| `401` | Credentials error — check `.env` or `~/.folio-credentials` |
| `400` | Show the full error body and identify which field caused it |
| `403` | Insufficient permission or a locked run/milestone — log the case ID and skip |
| `404` | Confirm the section ID exists and is accessible |
| `429` | Back off 2s and retry up to 3×; then log and continue to the next case |
| `504` | Transient, often just instance load — retry the same request 3× with 2s/4s/8s backoff |
| No status returned | Connection dropped. Treat as `504` and retry; never read an empty body as an empty page |
| Timeout | Resume from the last successful `offset`; do not restart the run |
| Any failure | Do not skip silently — report the case ID and full error message |

---

## Anti-Patterns to Avoid

**Substring matching** — re-matches already-corrected cases forever when the search phrase is a prefix of its replacement. Use word boundaries.

**Identifying an archived copy by title** — titles repeat across sections, so this both skips copies that were never made and re-copies ones that were. Use the `src:C<id>` stamp.

**Bucketing a `null` release as pre-release** — `null < 20` is not a meaningful comparison. Surface it and ask.

**Searching only `custom_steps_separated`** — a phrase living in legacy `custom_steps` is silently missed and the run reports success.

**Treating one `get_cases` response as complete** — `size` is the page count. Without pagination, a 472-case archive section reads as 250 and duplicate copies get created.

**Sending a partial `custom_steps_separated`** — `update_case` replaces the whole field, so a partial array deletes steps.

**Reporting totals without the original → copy ID map** — the next run has no way to tell what was already archived.

---

## Fallback Output (no API access)

If the API is unreachable, emit the intended changes as a table the user can apply by hand, then stop:

```
| Case | Field | Current | Proposed |
|---|---|---|---|
| C359006 | title | Preview of record matches | Preview of records matches |
| C359006 | refs  | UIBULKED-119 | UIBULKED-119,UIBULKED-649 |
```

Do not claim success. State plainly that nothing was written.

---

## Completion Check

Before reporting a run complete, verify all of these are true:

- [ ] The preview was rendered and explicitly confirmed before any write.
- [ ] Match detection used word boundaries, and already-correct cases were excluded from the match count.
- [ ] All six searchable fields were checked, including legacy `custom_steps` and `custom_expected`.
- [ ] Every source section was fully paginated to `_links.next == null`.
- [ ] No case with a `null` release was silently bucketed.
- [ ] Every archived copy carries a `src:C<original_id>` stamp.
- [ ] The run log records the original → copy ID map.
- [ ] Every failure appears in the log with its case ID and full error text.
- [ ] Rerunning the same inputs would report the completed work as skipped.