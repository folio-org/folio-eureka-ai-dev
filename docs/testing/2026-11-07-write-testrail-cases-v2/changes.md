# write-testrail-cases v2 — change log (2026-11-07)

This release consolidates the team-calibrated version of the skill (calibration up to 2026-08-06) with `master` (`a64bd3c`, including #41 of 2026-09-11), re-validates the defaults against current TestRail data, and refreshes all context files.

## Data behind the defaults

Sample: 500 manual cases in suite 21 created between 2026-03-02 and 2026-11-05 (raw `custom_preconds` / `custom_steps_separated`); 293 written by QA engineers, 207 labelled `ai`.

| Topic | Finding | Decision |
|---|---|---|
| Preconditions markup (`<ul>` vs `<ol>`) | `<ul>` 32%, plain `<p>` 26%, `<ol>` 22%, `<p>1)` 14%, table 3%; varies by section (Orders: `<p>1)`, Data Import: `<ol>`) | Follow the target section; default `<ol>` (supports "Preconditions #N", consistent with `examples.md`) |
| Okapi + Eureka permissions block | Capability sets in 86% of cases; dual block in ~7% | Capability sets only by default; dual block where the section uses it |
| Navigation separators | `->` 166, `=>` 71, `>` 103 occurrences | `>` for page paths, `->` for menu selection |
| Priority | Medium 83%, High 14% (AI-generated cases: High 53%) | Default Medium, with explicit criteria for High and Critical |
| Test Group | Extended 70%, Critical Path 24% (AI-generated cases: Critical Path 41%) | Default Extended; Obsolete, Draft, Backend and Edge Cases are never set on new cases |
| Case length | Median 7 steps (p25 5, p75 11); AI-generated cases median 5 | Per-area medians; cases shorter than half the median are merged |
| Title prefixes | `ECS \|`, `Consortia \|`, `Calculation:`, `ListRecords:`, `[LoC]`, `Package detail record:`, `[API]`, `Renewal:` | A prefix is used only if the target section already uses it |
| Label | Label title is lowercase `ai` (id 67) | Applied consistently |

## Skill structure

`SKILL.md` reduced from 78 KB / 936 lines to about 14 KB (workflow, scenario analysis, self-review gate). Detailed rules moved to `references/`, each read at the step that needs it:

- `area-map.md` — area detection table, context file rules, freshness rule
- `house-style.md` — per-area conventions, global defaults, titles, section formats, labels
- `writing-rules.md` — case template, preconditions, steps
- `step-patterns.md` — reusable step patterns
- `testrail-api.md` — metadata IDs, HTML markup (based on #41), API usage, fallback output

## New behaviour

- **Evidence-only rule:** every UI string and business rule must trace to a source read during the run, or carry a verification flag.
- **Target section sampling:** the 10 most recent cases of the target section are read before generation; their conventions override the defaults. The Section ID is requested early (optional).
- **Mandatory regression scenarios** for every changed business rule.
- **Enrichment from `en.json`** (instead of `en_US.json`, a Lokalise copy that lags behind), including the story's feature branch when the story is not yet merged.
- **Capability set names** are taken from the context file, recent section cases or the module's `package.json`; otherwise they are explicitly marked as unconfirmed.
- **Context freshness:** every context file carries a `Built / Delta-refreshed` header; files older than 90 days or built for an older release trigger enrichment and a warning.
- Verification checks for record types (instance / holdings / item, task / job), link targets, and UI data provided by the backend.

## Resolved inconsistencies

- Template, API example and fallback output used three different preconditions formats; now a single rule, with the API example in valid HTML.
- "Do not use legacy permission names" conflicted with the mandatory Okapi block; resolved.
- "Verify that…" titles were both prohibited and required (Requests); now allowed only where the section uses them.
- Test Group 4 was described as "permission assignment tests"; it is Obsolete.
- Type and Release were hard-coded in the template; now resolved per area and at runtime.
- Conflicting sizing rules for 1-step and 2–3-step cases replaced by one rule.
- Multi-line expected results sent as `\n- …` collapsed in TestRail; now encoded as `<ul><li>`.

## Context files

- **30 existing files — delta refresh.** Each file ends with a `## Changes since <build date>` section that takes precedence over older content: summary of changes (each item tied to a Jira key or commit), UI strings added / changed / removed since the build date (from the `en.json` diff; removed strings marked "do not assert"), Jira stories and bugs closed since the build date, and TestRail cases created since the build date (890 new cases in suite 21 since 2026-06-12). Largest changes: eHoldings package record and visibility, Orders payment terms and email templates, Users SMS contact and role selection, Lists search and MARC querying, Inventory custom links and number generators, Data Import deletion of MARC authority records, Bulk Edit deletion of user records, Circulation automatic renewals and text-message notices.
- **6 new areas:** `inn-reach.md`, `open-access.md`, `serials-management.md`, `claiming.md`, `export-manager.md`, `linked-data.md` (Marigold), built with the `build-app-context` method.
- `dcb.md`: a stray code fence that broke rendering of half the file was removed.
- `invoices.md`, `requests.md`, `users.md`: the 2026-08-06 date reflected a partial refresh only; the delta was calculated from the original June build.

## build-app-context

- Translations read from `en.json` only.
- `Built` header line added to the output template.
- Delta format documented for lightweight refreshes.
- Jira access table re-checked: ERM, UIEH / MODKBEKBJ and UIMARCAUTH / MODELINKS are accessible.

## Known limitations

- Coverage remains limited for Open Access (12 smoke cases), Serials Management and Claiming. Capability set names for INN-Reach settings, Open Access, Serials Management and Export Manager are not confirmed by any existing case and are flagged in the respective files.
- Delta sections are additive. A full `build-app-context` rebuild of the most active areas (eHoldings, Orders, Lists, Inventory) would merge them into the main sections.

## Evaluation

See `comparison.md` in this folder (v1 vs v2 on UIEH-1524, UIU-3595, UIOR-1497).
