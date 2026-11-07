---
area: inventory-browse
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO Inventory Browse — Business Logic Context

> Built: 2026-11-07 · Release: ui-inventory v13.0.0 at HEAD · Builder: build-app-context method, manual
> Sources: TestRail suite 21 sections 17147 "Call Number Browse" (55 cases) + 55325 "Browse configuration checks" (18), 17148 "Subject Browse" (64), 17888 "Contributors Browse" (44), 35111 "Instance classification browse" (51), Settings 55320 "Call number browse" (5) and 35321 "Classification browse" (7) — titles for all, full steps for C805650; GitHub folio-org/ui-inventory `translations/ui-inventory/en.json`; Jira UIIN, MSEARCH Done issues since 2025-11.
> Related contexts: `inventory.md` (records, search, move), `marc-authority.md` (authority browse — a different app), `marc-bib-quickmarc.md` (linking that drives the authorized indicator).

## What is Browse

`Inventory` → `Search | Browse` toggle → `Browse`. The left pane title is `Browse inventory` (subtitle `Enter search criteria to start browsing`); the empty results pane shows `Browse for results entering a query or choosing a filter.` Page title: `Inventory - {query} - Browse`. Browse lists index headings around the query (anchor in the middle, preceding results above), not instances; clicking a heading runs an instance search.

## Browse options (`Select a browse option`)

| Option (en.json) | Index | Filters (facets) |
|---|---|---|
| `Call numbers (all)` | Item effective call number (all types) | `Effective location (item)`, shared/held by in ECS |
| `Dewey Decimal classification`, `Library of Congress classification`, `Local`, `National Library of Medicine classification`, `Other scheme`, `Superintendent of Documents classification` | Item call numbers of that type, limited by Settings | same |
| `Classification (all)`, `Dewey Decimal classification`, `Library of Congress classification` | Instance classification | — |
| `Contributors` | Instance contributors | `Name type`, `Relator term` (only for this option) |
| `Subjects` | Instance subjects | `Subject source`, `Subject type` |

Contributors browse is offered on the Instance tab only, not on Holdings/Item (C353642). Switching browse options keeps the query and does not submit the form (C387486, C358148).

## Result list

| Option | Columns |
|---|---|
| Call numbers | `Call number`, `Title`, `Number of titles` (verify the full column set) |
| Classification | `Classification`, `Title`, `Contributors`, `Number of titles` (UIIN-3367/3368) |
| Contributors | `Contributor`, `Name type`, `Relator term`, `Number of titles` (en.json column keys; verify order) |
| Subjects | `Subject`, `Subject source`, `Subject type`, `Number of titles` (verify order) |

- An exact match is returned as its own row (C466323, C357531); no match shows a placeholder row with `would be here` (en.json `browseCallNumbers.missedMatch`; C347916, C350392). Highlight styling and anchor position — verify in env.
- The heading is a hyperlink (C374701…C374704). `Number of titles` = 1 opens the instance in the third pane; more than one opens the Search results with the query (C411505…C411507). The search uses `==` (exact) on the heading and, for contributors, also the name type (C358966, C357548).
- Hit count is not shown on browse lists (C358531, C356786).
- `Previous` / `Next` pagination; disabled on the first/last page; leaving the first/last page works (C468259…C468261).
- Browse results and filters persist when switching to Search and back, and after browser Back (C380402…C380405, C357033).
- `Reset all` returns focus to the search box and does not affect the Search pane (C422098, C422099, C398011).
- An authorized indicator (label — verify in env) is shown for contributors (100/110/111/700/710/711) and subjects (600/610/611/630/650/651/655) controlled by a MARC authority; linked and unlinked headings with the same text are separate rows (C375152…C375254, C375163).
- Contributors with the same name and name type but different authority IDs are separate rows; same authority ID — one row (C359595, C359596, C388531).

## Sorting and matching rules

- Call number browse is case-insensitive and ignores spaces for all sorting algorithms (MSEARCH-831/859, MSEARCH-1005, MSEARCH-1262; C594363, C594365, C1405529, C1405530).
- Classification browse is case-insensitive; `Classification (all)` sorts alphabetically, Dewey and LC use their own algorithms (C468241…C468258).
- Double quotes in a query, diacritics, backslash and a single-letter query are supported (UIIN-3537; C347915, C360948, C466294, C466296, C414511, C869994).
- A query containing `*` shows an error (C358151); contributor results error: `Error returning results. Please retry or revise your search.`
- Same call number with different copy numbers (enumeration) — separate rows; same call number in two holdings with different locations of one instance — handled per MSEARCH-992 (C651491, C651492, C692245).
- Call numbers with an invalid format for their type are still found (C451466…C451470). `fullCallNumber` includes prefix, suffix and item enumeration (C478253, C478256).

## Settings

| Page | Content | Toast |
|---|---|---|
| `Settings > Inventory > Call number browse` | One row per call number browse option; `Call number types` multi-select | `The call number browse type {term} was successfully updated` |
| `Settings > Inventory > Classification browse` | `Classification (all)`, Dewey, LC rows; `Classification identifier types` multi-select | `The Classification browse type {term} was successfully updated` |

Empty selection means "all types" (popover: `Please note that if no call number types are selected for a browse option, this option will display all call number types.`). Only selected types appear in that option's results (C627504…C627509, C468155…C468157). Deleting a local classification identifier type updates the config (C449381).

## Permissions

| Permission (ui-inventory package.json) | Display name |
|---|---|
| `ui-inventory.call-number-browse.view` | `Call number browse: View permissions` |
| `ui-inventory.subjects.view` | `Subject browse: View permissions` |
| `ui-inventory.settings.call-number-browse` | `Settings (Inventory): Configure call number browse` |
| `ui-inventory.settings.classification-browse` | `Settings (Inventory): Configure classification browse` |

Recent cases use `Inventory: All permissions` → `data - UI-Inventory - manage` in an Okapi/Eureka table (C805650). Browse-only users cannot edit records (C375064); without the browse permission the option is not offered (C374171, C451640). Eureka capability names for the browse-only permissions are not confirmed in cases — mark "verify".

## Key Business Rules for Test Cases

1. Browse shows headings, not records; assert the heading row, `Number of titles` and the anchor position, then the Search result after clicking (cases).
2. Each browse option is a separate case in the team corpus (all / Dewey / LC / …) — do not merge options into one case (cases).
3. Settings limit call number and classification browse options to the selected types; empty means all (en.json + cases).
4. Case, spaces and quotes do not change results (MSEARCH-1005, MSEARCH-1262, UIIN-3537).
5. Facets and query survive Search ↔ Browse switching and browser Back (cases).
6. Classification browse shows title and contributors (UIIN-3367/3368); contributors column is blank when the instance has none (C805650).
7. Recent bug areas: Classification browse 400 error (MSEARCH-1252), unindexed classifications (MSEARCH-1270), focus on a non-existent field (UIIN-3546).

## Authoring style (measured 2026-11-07)

Type `Functional` (sampled), Priority Medium. Step count and Test Group split were not measured across the sections; the sampled case C805650 has 2 steps, Critical Path. Preconditions: permissions table, test records with specific call numbers/classifications/subjects (often a MARC file imported with the default job profile), `"Browse" tab is selected in "Search|Browse" toggle`, the browse option selected. Steps are short (2–6), each with an example query value (`ex.: QL737.C22 E77 2025`) and the exact expected row content.

## Known Gaps / Items to Verify

- [ ] Eureka capability names for `Call number browse: View permissions` and `Subject browse: View permissions`.
- [ ] Exact column set for Call number browse results after 2026 changes — confirm in env.
- [ ] Authority browse in MARC authority app is out of scope here — use `marc-authority.md`.
