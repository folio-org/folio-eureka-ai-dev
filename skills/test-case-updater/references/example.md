# Example Run — Bulk Edit - Items

Use this only as a shape reference. The counts below are from a real run on 2026-06-30 and are not current.

## Inputs

| Input | Value |
|---|---|
| Module | Bulk Edit |
| Source section | `19563` (Bulk Edit - Items) |
| Target (archive) section | `65470` |
| Find | `\bPreview of record\b` |
| Replace | `Preview of records` |
| Ref to append | `UIBULKED-649` |
| Release threshold | `20` |

Note the word boundaries. Searching the bare substring `Preview of record` would also match `Preview of records`, so every already-corrected case would re-match on the next run — see the Anti-Patterns section in [../SKILL.md](../SKILL.md).

## What happened

1. Fetched section `19563` — 104 cases, returned in a single page (`_links.next` was null).
2. Fetched target section `65470` — 472 existing cases across **two pages**; the second request was required, `size` on the first page was 250.
3. Matched 82 cases on `\bPreview of record\b`; 19 already contained `Preview of records` and were excluded from the match count rather than counted as no-op updates.
4. Bucketed by `custom_release`: 61 pre-release (`< 20`), 21 current (`>= 20`), 0 with a null release.
5. Checked the target section for `src:C…` stamps — none found, so all 61 needed archiving.
6. Rendered the preview with three before/after samples and waited. Confirmed with `yes`.
7. Copied 61 pre-release cases via `copy_cases_to_section`, then stamped each copy's `refs` with `src:C<original_id>`.
8. Updated all 82 originals: phrase replaced in `title` and `custom_steps_separated`, `UIBULKED-649` appended to `refs`.
9. No errors.

## Log snippet

```
[2026-06-30 14:22:15] Run start — module=bulk-edit search=\bPreview of record\b
[2026-06-30 14:22:16] Source 19563: 104 cases (1 page)
[2026-06-30 14:22:19] Target 65470: 472 cases (2 pages)
[2026-06-30 14:22:19] Matched 82 | already correct 19 | pre-release 61 | current 21 | null release 0
[2026-06-30 14:22:19] Already archived (src: stamp): 0
[2026-06-30 14:22:20] Preview rendered — awaiting confirmation
[2026-06-30 14:22:44] Confirmed: yes
[2026-06-30 14:22:50] Copied 61 → C1395081-C1395141, stamped src:C<original>
[2026-06-30 14:23:10] Updated 82 originals
[2026-06-30 14:23:10] Errors: 0 — run complete
```

## Original → copy map

The run log must carry the full map. Abbreviated here:

| Original | Copy | Release |
|---|---|---|
| `C359006` | `C1395081` | 17 |
| `C359011` | `C1395082` | 16 |
| … | … | … |

This map, not title comparison, is what makes the next run safe.

## Re-running

Re-running the same inputs is safe:

- Cases already containing `Preview of records` are excluded at match time — they never enter the update set.
- Pre-release cases whose copy carries `src:C<original_id>` in the target section skip the copy step; the original is still updated if it still matches.
- Cases already carrying `UIBULKED-649` in `refs` skip the ref append.

Verified against live data on 2026-08-19, searching all six fields across section `19563`:

| Match method | Cases matched | Correct? |
|---|---|---|
| `\bPreview of record\b` (word boundary) | **0** | ✅ the 2026-06-30 run is complete, nothing left to do |
| `Preview of record` (naive substring) | **101** of 104 | ❌ every one already reads `Preview of records` |

A naive substring search would issue **101 no-op writes** to already-correct cases — and would do so on every subsequent run, forever. This is not an edge case; it is nearly the whole section. It is the single most important reason the matching rule in [../SKILL.md](../SKILL.md) is written the way it is.