# House Style by Area

> Two measurements feed this file:
> - **Corpus audit, 2026-07-23** — whole suite 21, per area (Type share, median steps, journey flag).
> - **Recent-manual sample, 2026-11-07** — 500 manual cases created 2026-03-02 … 2026-11-05 in suite 21 (293 written by people, 207 labelled `ai`). Rows marked **(Nov)** were re-measured on ≥13 human cases; where the two disagree, the Nov value is current.
>
> If the target section's recent cases (workflow step 4) disagree with this file, follow the section.

## Global defaults (human-written manual cases, Nov sample)

| Field | What people do | Default for a new case |
|---|---|---|
| Priority | Medium 83%, High 14%, Critical 2%, Low 1% | **Medium**. High only for the main daily workflow of the feature; Critical only if failure blocks a core library operation (check-in/out fulfillment, opening/paying an order, posting an invoice). |
| Test Group | Extended 70%, Critical Path 24%, Draft 4%, Obsolete 1%, Smoke <1% | **Extended**. Critical Path for the feature's core business-rule cases. Never Smoke for manual cases. |
| Steps | median 7 (p25 5, p75 11) | Area median below |
| User Journey | 5% | `false` unless the area uses it |
| Permissions in preconditions | capability sets in 86% of cases; Okapi + Eureka dual block in ~7% | Capability sets only, unless the section uses the dual block or a table |
| Preconditions markup | `<ul>` 32%, plain `<p>` 26%, `<ol>` 22%, `<p>1)` manual numbering 14%, table 3% — **varies by section** | `<ol>`; match the section when it consistently uses another form |
| Separators in steps | `>` for page paths; `->` (and legacy `=>`) for menu selection | `>` for paths, `->` for menus |

> **Calibration gap seen in the `ai`-labelled cases (Nov sample):** they set Priority High in 53% of cases (people: 14%), Critical Path in 41% (people: 24%), and have a median of 5 steps (people: 7). Stick to the defaults above and the area medians below.

## Per-area table

Type IDs: Functional = 6, Other = 7 (resolve at runtime via `get_case_types`).

| Area | Dominant Type | Median steps | Journey flag | Shape note |
|---|---|---|---|---|
| Orders **(Nov)** | Functional (100%) | 8 | 0% | Functional, mid-size; bundle workflow ACs; preconditions are often `<p>1)` manual numbering |
| Invoices **(Nov)** | Functional (100%) | 7 | ~0% | 1-step permission-denial cases are common; no `BFreviewed`; Eureka block as a plain paragraph after `<hr>` |
| Finance | Functional (94%) | 7 | ~2% | Exact money values |
| Organizations | Functional (85%) | 8 | ~15% | Journey flag sometimes used |
| Mediated Requests | Functional (94%) | 6 | ~0% | ECS by default |
| eHoldings **(Nov)** | Functional (96%) | 6 | **~44%** | Journey flag now frequent in new cases; title prefixes like `Package detail record:` |
| Inventory **(Nov)** | Functional (65%) | 6 | ~3% | Compact; per-variant (record type / OS) |
| Inventory import **(Nov)** | Functional (94%) | 4 | 0% | Short; `<ol>` preconditions |
| Inventory Browse **(Nov)** | Functional | not measured (sample: 2) | 0% | One case per browse option; example query value in each step |
| MARC Holdings **(Nov)** | Functional | not measured (sample: 7–14) | mostly No | Create and edit as separate cases; Okapi/Eureka permissions table |
| Receiving | Functional (99%) | 8 | ~0% | Piece flow + Inventory/Finance side effects |
| Data Import **(Nov)** | Other 52% / Func 30% / Acceptance 18% | 6 | ~2% | Matching-rule cases are short per variant; mostly `<ol>` preconditions |
| OAI-PMH **(Nov)** | Other (100%) | 8 | 0% | API/protocol assertions; title prefixes `ListRecords:` / `ListIdentifiers:` / `GetRecord \|` |
| Agreements **(Nov)** | Other (65%) | 10 | 0% | Larger cases than the July audit suggested |
| Loans | Other (85%) | 6 | ~0% | Short/atomic; Renewals sub-section: `BFreviewed`, titles "Renewal: [scenario]" / "Loan Policies: [topic]" |
| Fees&Fines | Other (79%) | **2–3** | ~1% | Very short atomic cases |
| Bulk Edit | Other (94%) | **14** | ~0% | Large multi-step cases |
| License | Other (98%) | 7–9 | ~3% | |
| Data Export | Other (93%) | 6–11 | ~0% | Few manual cases; sample the section |
| Lists | Other (65%) | 6 | ~0% | |
| Circulation Settings | Other (69%) | **3** | ~10% | Short; titles often "Settings - …" |
| Circulation Log | Other (82%) | 5–6 | ~8% | |
| Course Reserves | Other (61%) | **3** | ~0% | Short |
| Check-in | ~50/50 | 6 | **~18%** | Mostly Extended; all manual cases carry `BFreviewed`; titles "Check in [scenario]" |
| Check-out | Func 51% / Other 43% | 6 | ~6% | |
| Users | Func 52% / Other 46% | 6 | ~3% | High title variety; `BFreviewed` selective (match surrounding cases) |
| Requests | Func 53% / Other 45% | 5–7 | ~1% | `BFreviewed` required; titles "Check that…" / "Make sure that…" / "Validate that…"; permissions as a two-column table |
| Patron Notices | Other 53% / Func 40% | **12** | ~2% | Large cases |
| INN-Reach | — | 3–13 | — | Old cases use legacy permission names and many have group 4/5/7; sample recent cases (2025+) only |
| Open Access / Serials / Claiming / Export Manager | — | — | — | Few cases; sample the section before writing |
| Linked Data (Marigold) | — | — | — | Titles start with Jira keys in brackets: `[UILD-826] …`; many group 1 cases |

For any area not in this table, sample its section and match what you see.

## Titles

Default shape: an **imperative or factual verb phrase** — `[Verb] [object] [condition]`, or `[Subject] [state] [condition]` for UI checks.

✓ `Check in multipiece items` · `Re-open order after making edits` · `Holdings export fails when submitted file contains invalid UUIDs` · `Mapping profile Status column shows Locked after lock checkbox is enabled` · `User cannot save new match profile when …` (capability/validation cases)

✗ `Verify mapping profile creation` (vague) · `Test that user can create profile` · `Negative: …` · `Load testing - …` · `NOT implemented yet | …` (status marker)

**Prefixes** — use a prefix only if it already appears in the target section (seen in the Nov sample): `[LoC]`, `[ECS <Area>]`, `ECS |`, `Consortia |`, `Calculation:`, `ListRecords:`, `ListIdentifiers:`, `GetRecord |`, `Renewal:`, `Package detail record:`, `Postman |`, `[API]`. Never invent a new prefix.

**"Verify that…" / "Check that…"** — ~5% of recent human titles. Use them only in sections where they are the norm (Requests, some Users subsections); elsewhere, rewrite as a verb phrase.

Titles must be unique within the section.

## Section-specific formats (confirmed)

- **Requests:** permissions as a two-column HTML table:
  ```html
  <table><thead><tr>
    <th>Permission name for Okapi env.</th>
    <th>Capabilities/Sets for Eureka env. (type/table - resource - action)</th>
  </tr></thead><tbody>
    <tr><td>Requests: All permissions</td><td>data - UI-Requests - manage</td></tr>
  </tbody></table>
  ```
- **Invoices:** Eureka block as a plain paragraph after `<hr>`:
  ```html
  <hr>
  <p>For Eureka environments, use the following capability sets:<br>data - UI-Invoice Invoice - create</p>
  ```
- **Orders:** preconditions frequently written as `<p>1) …</p><p>2) …</p>`; the user line reads "A user with the following capabilities/sets is logged in:" followed by a capability list.
- **ECS cases:** tenant names in `<strong>` (`<strong>Central</strong>`, `<strong>Member</strong>`); every data record says which tenant it lives in.

## Labels

- `ai` (id **67** on foliotest.testrail.io) — on every generated case.
- `BFreviewed` (id 62) — only in sections where the surrounding cases carry it (Requests, Renewals, Check In confirmed).
- `fe_reviewed`, `CBS2FOLIO`, `eusage-reports` exist — never add them on your own.
