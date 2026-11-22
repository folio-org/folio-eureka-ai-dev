# Lessons from reviews and runs

Knowledge learned after the skill produced tests. Read on every run; apply the entries whose scope matches the target project.

## How to add an entry

- One rule per entry. Before adding, search this file and `karate-standards.md`: if the rule is already there, add the new source to the existing entry instead.
- **Scope**: `U` (all teams) only when the rule follows from the Karate Coding Standards, from how Karate or the shared runners work, or from TestRail traceability; otherwise `T:<team>`.
- **Status**: `standard` (written in a team rules file or the wiki), `confirmed` (a reviewer or the team agreed it applies beyond one PR), `preference` (one reviewer's style; apply only in that team and do not enforce in the validator).
- **Rationale**: what goes wrong without the rule, in one line.
- A review comment about one story is fixed in that PR and not recorded.
- **Revalidated**: the date the entry was last checked against the team rules files and the wiki. When a rules file now states the rule, change status to `standard` and point to the file; when a source contradicts it, remove the entry.

| ID | Rule | Scope | Status | Rationale | Source | Revalidated |
|---|---|---|---|---|---|---|
| L1 | Data that scenarios change (funds, budgets, orders) is created inside each scenario with `call uuid`, not in `Background` with `callonce uuidN` | U | standard | Parallel scenarios share and corrupt the data (encumbrances mix) | Karate Coding Standards ("Do not repurpose the same identifiers"); validator finding on PR #2620 | 2026-11-22 |
| L2 | TestRail cases are written in business language; endpoints, status codes and payloads live only in the feature | U | confirmed | Cases are reviewed by QA and PO; technical detail hides the rule | Developer feedback (Thunderjet), Nov 2026 | 2026-11-22 |
| L3 | Capabilities appear in the TestRail case as Eureka capability sets; the feature does not create per-case users or permissions | U | confirmed | Project test users have fixed permissions; modelling them adds setup without value | Developer feedback (Thunderjet), Nov 2026 | 2026-11-22 |
| L4 | Read all of the team's rules files (`<project>/ai/`) and the Karate Coding Standards wiki before writing | U | confirmed | Rules overlap across modules (orders stories reach finance and invoices) | Developer feedback (Thunderjet), Nov 2026 | 2026-11-22 |
| L5 | Do not add a case or scenario for behaviour an existing scenario already asserts; extend or cite it | U | confirmed | Duplicates add runtime and maintenance, no coverage | Developer feedback (Thunderjet), Nov 2026 | 2026-11-22 |
| L6 | Discover folders, runners and registration style per project; never assume the acquisitions layout | U | confirmed | Projects use three registration styles | QA Manager decision, Nov 2026; repository survey | 2026-11-22 |
| L7 | Karate is the focus, not the limit: what Karate cannot verify becomes a full Manual case through write-testrail-cases; QA stays in the process | U | confirmed | Dropping non-API checks leaves UI behaviour untested | QA Manager decision, Nov 2026 | 2026-11-22 |
| L8 | Pass every documented reusable parameter explicitly instead of relying on a caller variable with the same name | U | confirmed | Works only by accident of Karate scope sharing; breaks on rename | `check-calls` finding (`openOrder { id: … }` in existing features), Nov 2026 | 2026-11-22 |
