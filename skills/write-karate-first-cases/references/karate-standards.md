# Karate standards for folio-integration-tests

Every rule has a **scope**: `U` applies to all teams (Karate Coding Standards, or a property of Karate and the shared runners); `T:<team>` comes from one team's rules files and applies only in that team's projects. A `T` rule is a good default elsewhere, never a reason to fail a feature of another team.

## Sources and precedence

| # | Source | Why this rank |
|---|---|---|
| 1 | The owning team's rules files: `<project>/ai/*.md` (today only `acquisitions/ai/`: `ACQ_ORDERS_SYSTEM_PROMPT.md`, `ACQ_CROSS_MODULES_SYSTEM_PROMPT.md`, `prompt/PROMPT_TEMPLATES.md`) | Written by the team for AI-generated tests, maintained in the repo next to the tests, most recent (last change Nov 2026) |
| 2 | FOLIJET wiki *Karate Coding Standards & Best Practices* (https://folio-org.atlassian.net/wiki/spaces/FOLIJET/pages/114098928) | The shared baseline all teams refer to; last updated June 2024, so specific points are superseded by rank 1 |
| 3 | What the repository does now: the 2 best exemplar features of the target folder (`karate-context.py exemplars`) and the registration style (`karate-context.py profile`) | Shows conventions nobody wrote down (login, headers, folder layout) |
| 4 | Reference refactorings: FAT-13426 (PRs #1359, #1482), FAT-20199 (PRs #2259, #2465), runner structure PR #2426 | Before/after examples of rank 2 applied at scale (acquisitions) |
| 5 | This file and `lessons.md` | Digest; when it disagrees with 1–3, they win and this file is corrected |

Known differences between rank 1 and rank 2:
- Step markers: the wiki asks for numbered `* print 'N. …'`; the acquisitions rules forbid them and use `# N. …` comments. Use the team's choice; for teams without rules files, `# N.` comments are the skill's default because they map 1:1 to TestRail steps.
- Runners: the wiki shows one `@Test` per feature; acquisitions moved to a `FEATURES` array (PR #2426). Follow the project's current style.

## Rules

| Area | Rule | Scope |
|---|---|---|
| Scenario design | One scenario = one complete workflow (prepare, trigger, verify). Never split dependent steps into separate scenarios; that pattern needs `@parallel=false` | U |
| Scenario design | A scenario passes alone, in any order, and twice in a row on the same tenant | U |
| Scenario design | Do not add `@parallel=false` to a new feature (wiki: avoid; acquisitions rules forbid it). If a team serialises on purpose because of tenant-wide state, the PR says why | U (error only where team rules forbid it) |
| Scenario design | Keep features focused; split by business rule instead of growing one file | U |
| Test data | IDs with `call uuid` inside the scenario; no `callonce uuidN` or Background IDs for data scenarios change | U |
| Test data | Codes and names that must be unique (fiscal year series, fund codes) built from `call random_string`, not literals (PR #2465) | U |
| Test data | Do not change shared global records (global fund, budget, tenant settings) in a parallel scenario; create own records | U |
| Test data | Large JSON bodies in `samples/` files loaded with `read()` | U |
| Test data | Global variables only in the project's variables/global features; prefer local `def` | U |
| Reusables | Use an existing reusable before writing a request; check `karate-context.py reusables` | U |
| Reusables | Load them the way the project does: by `karate-config.js` key where it is there, else as neighbouring features do | U |
| Reusables | Do not `read()` a reusable that `karate-config.js` already loads (FAT-20199) | U |
| Reusables | Missing parameter: add it to the reusable as optional (`karate.get('x', default)`) and document it in `# parameters:`; never copy the request into the feature | U |
| Reusables | New reusable: `@ignore`, `# parameters:` header with defaults, verb-noun name, registered next to related keys | U |
| Reusables | `* def v = call …` when the result is unused; no prefix for `call login` / `callonce variables` whose output is used | U |
| Reusables | Quote embedded expressions in call arguments: `{ id: '#(fundId)' }` | U |
| Data preparation | Several similar records: a Karate `table` passed to one reusable call, not `Scenario Outline` | U |
| Waiting | Poll async state with `retry until`; `call pause` only when there is no state to poll | U |
| Waiting | All conditions of a wait inside the `retry until` expression; assert other fields in a separate request block | T:acquisitions |
| Assertions | Assert business fields with exact or captured values, not only status codes | U |
| Assertions | Collections have no guaranteed order: `[*]` with `contains`, `contains any`, `contains only` | U |
| Assertions | Objects may gain fields: `match obj contains { … }` unless the exact shape is the contract | U |
| Assertions | Negative cases: exact status, error code and a follow-up GET proving nothing changed | U |
| Assertions | `$` instead of `response` right after a request | T:acquisitions |
| Structure | `* print karate.info.scenarioName` first in `Background` | U |
| Structure | `# N.` comments mapped to TestRail steps; no `* print 'N. …'` | T:acquisitions (skill default elsewhere) |
| Structure | Header `# For <JIRA-KEY>, <TestRail case URLs>`; one `@C<id>` per scenario, then `@Positive` / `@Negative` | Skill (traceability) |
| Users | `headersUser` for the module under test, `headersAdmin` for setup in other modules; never end a scenario with `configure headers` | T:acquisitions |
| Users | Users and headers exactly as the folder's features use them; no per-case users | U |
| Naming | kebab-case feature files, ≤ 80 characters with `.feature` (longer names break Karate reports) | T:acquisitions (warning elsewhere) |
| Naming | Feature, scenario names and step comments in Title Case | T:acquisitions |
| Registration | Register the way the project does (see below); a feature runs from exactly one runner or root feature | U |

## Registration styles

`karate-context.py profile <project>` shows the style. Never introduce a second style in a project.

| Style | Example projects | How a feature is registered |
|---|---|---|
| `FEATURES` array (PR #2426) | acquisitions, data-import | Append the name to the array of one runner; no new `@Test` methods, enums or runner classes |
| One `@Test` per feature | mod-calendar, mod-users | Add a `@Test` method calling `runFeatureTest("<name>")`, shaped like its neighbours |
| Root feature | mod-circulation | Add `* call read('…/<name>.feature')` to the root feature (`root.feature`, `root-extended.feature`) the runner executes |
| `@Test` per feature with `feature("classpath:…").run()` | data-import (`DataImportExtendedApiTest`, `DataImportCriticalPathApiTest`) | Add a `@Test` method running the feature by path, like its neighbours |
| `enum Feature` + `@Test` per feature (before PR #2426) | older acquisitions runners | Add an enum entry and a `@Test` method; do not convert the class to the array style in a test PR |
| Array + root feature | acquisitions | Both: array entry and a `Scenario` calling the feature at the end of the module root feature |

Where the project has per-group runners (Critical Path, Extended), the TestRail Test Group decides the runner. Append only; never reorder.

## Is it already covered?

Tests are rewritten, merged and renamed over time (acquisitions: FAT-13426 / FAT-20199), so a rule can live in a feature whose name does not mention it. Search by behaviour:

1. `karate-context.py coverage <projects> --endpoint "<METHOD> <path>" --field <field> --code <error-code> --reusable <key>` over every project the story touches. Reusable calls are expanded, so a scenario that opens an order through `openOrder` counts as a PUT on `orders/composite-orders`.
2. Open each hit and compare precondition, trigger and asserted outcome. Same three: covered. Same workflow, missing assertion or variant: extend.
3. Check TestRail for cases with the same `refs` or outcome (write-testrail-cases, step 4b).
