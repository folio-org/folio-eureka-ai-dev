# write-testrail-cases: v1 vs v2 evaluation (2026-11-07)

## Summary

v2 produces materially better test cases than v1: full coverage of story scenarios, systematic regression coverage, UI strings taken from the current source, and metadata and formatting that match the target TestRail section. The main cost is volume (19 cases vs 12); part of the regression set can be consolidated. Three gaps found during the evaluation have been addressed in v2 (see "Follow-up changes").

## Scope and method

| Story | Area | Status at evaluation | Reason for selection |
|---|---|---|---|
| UIEH-1524 — Provider record: Access status type column in the Packages list | eHoldings | In Review | Area with the largest context delta |
| UIU-3595 — "Anonymize closed loans" option on user records | Users / Loans / Circulation settings | In Code Review | Cross-area story with time-based business rules |
| UIOR-1497 — Exported and Transmission method filters, Export date column | Orders | Blocked (UIORGS-477) | New filters plus regression of existing ones |

- Both versions were run under identical conditions, each strictly following its own `SKILL.md` and context files.
- Ground truth for UI strings: `en.json` on `master`, the feature branches `UIU-3595-loan-anonymization-preference` and `UICIRC-1361-opt-in-loan-anonymization`, and the six most recent cases in the target sections (125, 1132).
- Generated cases: `cases-old-version.md` (v1), `cases-new-version.md` (v2). Full change log: `changes.md`.

## Results

| Metric | v1 | v2 |
|---|---|---|
| Cases generated | 12 | 19 |
| Story scenarios covered (UIEH-1524 / UIU-3595 / UIOR-1497) | 3/3 · 4/7 · 7/7 | 3/3 · 7/7 · 7/7 |
| Regression cases | 1 | 8 |
| Open questions / conflicts raised to the user | 0 | 3 |
| Unflagged assumptions (capability set and permission names) | 4 | 0 (10 items flagged `verify`) |
| Preconditions format matches the target section | 0/3 | 3/3 |
| Type matches the target section | 1/3 | 3/3 |
| Priority distribution (High / Medium / Low) | 6 / 5 / 1 | 6 / 12 / 1 |
| `BFreviewed` label where the section requires it | No | Yes |
| Average steps per case | 3.2 | 3.2 |

## Key findings

**1. Current UI strings.** The Provider packages list columns (Status, Package name, Titles selected, Total titles, Content type, Package custom coverage, Package type, Access status type, Tags) exist only in `en.json` (`packagesList.*` keys added in October–November 2026). They are missing from `en_US.json`, which v1 used. v1 therefore wrote a generic assertion and relied on the Titles accordion pattern, whose columns differ.

**2. Regression coverage.** v2 added checks for: default visibility of existing columns; the column value after editing a package's access status type (area of bug UIEH-1564) and after deleting a type in Settings; persistence of the column selection after editing the provider; the existing Export date filter together with Reset all; CSV export from a filtered Order lines list; user version history. v1 covered only column persistence after navigation.

**3. Business-rule coverage.** For UIU-3595, v2 covered the fee/fine branch (separate duration), the fallback to the library policy, and a side-by-side check of two patrons ("Never" vs "According to library policy"). v1 missed 3 of the 7 story scenarios.

**4. Section conventions.** Section sampling produced the correct house style for each area: nested `<ol>` preconditions and `Settings - Module Eholdings Enabled - View` for eHoldings; the dual Okapi + Eureka block and `BFreviewed` for Loans: Anonymization; `<p>1)` numbering for Orders. v1 applied `<ul>` and a mandatory Okapi permission block everywhere, which recent eHoldings cases no longer use.

**5. Handling of ambiguity.** v2 raised the internal conflict in UIU-3595 (scenario 2 refers to a "User-specific loan anonymization" accordion, while the requirements describe a radio button set in "Extended information") and did not generate a case for undefined behaviour. v1 silently picked one interpretation.

## Issues found in both versions

- **Tenant setting label (UIU-3595).** The story uses "Allow user specific anonymization settings for closed loans"; the UICIRC-1361 branch uses a "User-specific loan anonymization" section with the option "Do not allow user-specific loan anonymization". v1 asserted the story text as fact; v2 flagged it for verification. The user-record labels ("Anonymize closed loans", "According to library policy", "As early as possible", "Never") match the UIU-3595 branch in both versions.
- **Case length.** Both versions averaged 3.2 steps against a section median of 6–8. The v2 self-review gate did not catch six two-step cases.
- **Capability set names** for Check in / Check out and fees/fines were inferred in both versions; v2 flagged them, v1 did not.

## Follow-up changes (included in v2)

1. **Feature-branch strings.** For stories that are not yet merged, enrichment reads `en.json` from the story's branch (`<STORY-KEY>-*`) when the strings are not on `master`.
2. **Case length gate.** A case shorter than half of the area median is merged into a sibling case with the same preconditions.
3. **Capability set names.** Taken from the context file, then recent cases in the target section, then the module's `package.json`; otherwise marked "capability set name not confirmed — verify". Names are never inferred.
