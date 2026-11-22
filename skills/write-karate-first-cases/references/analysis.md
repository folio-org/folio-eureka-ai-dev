# Requirement analysis: coverage matrix, evidence and confidence

Phase 2 of the skill produces one matrix per story. It is shown to the user before any case is posted or any feature is written, and it is repeated (updated) in the run summary.

## Matrix columns

| Column | Content |
|---|---|
| ID | R1, R2, … — one row per requirement |
| Requirement | One acceptance criterion, one before/after line of the fix, or one Key Business Rule the change touches. Regression rows ("must not break") are requirements too |
| Source | Where the requirement comes from: `AC2`, `comment 14 Nov (PO)`, `fix diff PurchaseOrderHelper:88`, `unit test shouldKeepApprovalDate`, `context orders.md rule 7` |
| Evidence | `F` verified fact (read in code, contract, AC or an agreed comment), `I` inferred (from code structure or similar behaviour; must be confirmed), `A` assumption (no source; becomes an open question) |
| Decision | `Karate`, `Manual`, `Split`, `Covered`, `Extend` |
| Existing coverage | Feature + scenario + C-id for Covered/Extend; TestRail case for manual coverage that already exists |
| Pre-fix failure | `demonstrated` (the scenario was run against the pre-fix build and failed), `by diff` (the changed line is on the scenario's path and the old code produces a different asserted value — explain in one line), `unknown`. Never write a claim stronger than the evidence |
| Confidence | `H` all inputs F and the scenario reaches the changed code; `M` one input I; `L` any A, or the behaviour depends on environment/configuration the tests cannot control |
| QA review | `yes` when a trigger below applies |

## Decision rules

- **Karate**: the outcome is decidable through HTTP: the response, a follow-up GET, job or async state polled with `retry until`, data or events visible through another module's API.
- **Manual**: the outcome needs a person or a UI: rendering, labels, toasts, client-side validation, navigation, capability-based hiding, exact UI texts, downloaded files opened by a user, delivery to external systems (email, EDI/FTP, vendor portals), visual or usability judgement, behaviour the test environment cannot reproduce (say why).
- **Split**: the business rule is a Karate row; its UI part is a Manual row that references the Karate case instead of re-checking the rule.
- **Covered**: an existing scenario has the same precondition, the same trigger and asserts the same outcome. Cite it; generate nothing.
- **Extend**: an existing scenario has the same workflow but misses an assertion or a variant. Add to it (and to its TestRail case) instead of creating a new file or case.

A row may not be dropped. If nothing can verify it, it stays as a Manual row with the reason, or as an open question.

## What to consider per requirement

Positive path; the negative cases that the code actually distinguishes (validation branches, error codes in the diff); boundaries named in the code or the AC (zero, limits, empty lists); missing permission when the endpoint or the change checks one; invalid or incomplete data; status transitions in both directions; effects in other modules (finance, inventory, circulation, events). Add a row only when the code or the requirement makes the case different: no rows for implementation details that are not a contract.

## Mandatory human QA review (flag in the matrix and the run summary)

- Any row with confidence `L`, or any `A` evidence left unresolved.
- No implementation PR found; cases written from the story alone.
- The application context file is missing or stale and enrichment found little.
- A Manual or Split row exists for a UI change (QA owns UI verification).
- Permissions, security, data deletion, money (encumbrances, payments, fees) or tenant-wide settings are involved.
- Acceptance criteria and implementation disagree (contradiction found in Phase 2).
- An existing case would be changed (`update` decision) or an existing scenario extended.

## Contradictions and gaps

Before classifying, compare AC, comments, fix diff and unit tests. Record every disagreement as an open question `Qn` with both sources ("AC3 says 422, `ErrorCodes.java` returns 400 for this code"). Do not pick a side silently: the matrix row gets evidence `A` until the user or the PO answers. Missing AC for a code path in the diff becomes a row with source `fix diff` and evidence `F` for the behaviour, plus a question whether it is intended.

## Example (MODORDERS-1458)

| ID | Requirement | Source | Ev. | Decision | Existing coverage | Pre-fix failure | Conf. | QA review |
|---|---|---|---|---|---|---|---|---|
| R1 | Approval date and approver set at first opening stay after unopen + open | AC1; fix diff `setOrderApprovalDetails` | F | Karate | none | by diff: old code set both fields on every transition to Open | H | no |
| R2 | Approval date set while Pending is kept on opening; approver filled | fix diff (per-field null check) | F | Karate | none | by diff: old code overwrote approvalDate | H | no |
| R3 | Order details pane shows the initial approval date after reopen | AC2 | F | Covered | C736774 (manual, updated by the team) | — | H | no |
