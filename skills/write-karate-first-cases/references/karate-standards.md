# Karate standards for folio-integration-tests

The rules below combine four sources. Read the originals when a rule is unclear or a case is not covered here.

| Source | What it gives | Link |
|---|---|---|
| Team rules files (Thunderjet) | Authoritative, current rules for acquisitions features. Win over everything below | `acquisitions/ai/ACQ_ORDERS_SYSTEM_PROMPT.md`, `acquisitions/ai/ACQ_CROSS_MODULES_SYSTEM_PROMPT.md` |
| Karate Coding Standards & Best Practices (FOLIJET wiki) | The baseline style guide all teams refer to | https://folio-org.atlassian.net/wiki/spaces/FOLIJET/pages/114098928 |
| FAT-13426 and FAT-20199, "Update Karate tests" (1) and (2) | How the team rewrote old tests to the standard: before/after examples of almost every rule | PRs #1359, #1482, #2259, #2465 in folio-org/folio-integration-tests |
| PR #2426, "Reduced redundancy in acquisitions JUnit tests" | Current runner structure: one `FEATURES` array per runner class | https://github.com/folio-org/folio-integration-tests/pull/2426 |

Where the sources disagree, the newer team rule wins. Known differences:

- **Step markers.** The wiki page (2024) asks for numbered `* print 'N. …'` lines. The current team rules forbid them: use `# N. …` comments, and keep `* print karate.info.scenarioName` in `Background` as the only print.
- **Runners.** The wiki shows one JUnit `@Test` method per feature. Since PR #2426 a runner holds a `FEATURES` string array and runs it with `runFeatures(...)`; registering a feature means adding one string to that array.

## 1. One workflow per scenario, scenarios independent

- A scenario is a complete business workflow: prepare data, trigger, verify. Do not split dependent steps into separate scenarios (`Scenario: Create finances`, `Scenario: Create an order`, `Scenario: Open the order`). That pattern needs `@parallel=false` and was removed everywhere by FAT-13426 / FAT-20199.
- Every scenario must pass when run alone, in any order, and twice in a row on the same tenant ("can I run it over and over again?").
- Never add `@parallel=false` to a new feature. It is tolerated only in `init-*.feature` and in old features that cannot be fixed yet.
- A feature holds a few closely related scenarios. Split large features by business rule instead of growing one file.

## 2. Unique data in every scenario

- IDs: `* def orderId = call uuid` inside the scenario. Never `callonce uuidN` or IDs in `Background` for data that scenarios change.
- Unique codes and names as well as IDs: fiscal year codes, fund codes and series must not collide between parallel scenarios. Use `* def series = call random_string` and build codes from it (`code: '#(series + "0001")'`), as in the parallel fix for `partial-rollover.feature` (PR #2465).
- Do not reuse the global fund or budget for a scenario that changes their amounts or status; create its own fund and budget (another test may run a rollover that changes the global ones).

## 3. Reusable features

- Before writing a request, check whether a reusable already does it. All acquisitions reusables are loaded in `acquisitions/src/main/resources/karate-config.js`; call them by key (`call createOrder { … }`).
- Do not `read('classpath:…/reusable/x.feature')` a reusable that `karate-config.js` already loads (FAT-20199 requirement).
- If a reusable lacks one parameter you need, add it as an optional parameter (`karate.get('param', default)`) and document it in the `# parameters:` header, instead of copying the request into the feature (FAT-13426: `paymentStatus` and `receiptStatus` added to `create-order-line.feature`). Mention the change in the PR.
- A new reusable: `@ignore` on the first line, a `# parameters:` header listing every parameter with its default, a descriptive verb-noun name, and a key in `karate-config.js` next to the related keys.
- Prefix calls with `def v =` when the result is not used: `* def v = call openOrder { orderId: '#(orderId)' }`. Exceptions where the output is used: `call login`, `callonce variables`.
- Quote embedded expressions in call arguments: `{ id: '#(fundId)' }`, not `{ id: #(fundId) }`.

## 4. Data preparation with tables, not Scenario Outline

- Use a Karate `table` and call the reusable once per row: `* def v = call createOrderLine statusTable`. Scenario Outline runs each example as a separate scenario, cannot share prepared data and does not combine with reusables.

```gherkin
* table statusTable
  | id      | paymentStatus          | receiptStatus          |
  | poLine1 | 'Awaiting Payment'     | 'Partially Received'   |
  | poLine2 | 'Payment Not Required' | 'Awaiting Receipt'     |
* def v = call createOrderLine statusTable
```

## 5. Waiting and assertions

- Wait for async processing with `retry until` on the state you expect. Use `call pause` only when there is no state to poll (the wiki: "add a retry rather than pausing"). Put every condition of the wait in the `retry until` expression; assert other fields in a separate request block after it.
- Assert on business fields, not only on the status code.
- Collections have no guaranteed order: use `match response.items[*].field contains value`, `contains any`, `contains only`. Never assert `items[0]` unless the API sorts by contract.
- Objects can gain fields: use `match obj contains { … }` rather than `==` on a whole object, unless the test is about the exact shape.
- Use `$` right after a request (`And match $.workflowStatus == 'Open'`).

## 6. Readability

- The scenario reads like a technical product owner wrote it: numbered `# N.` comments, one action per block, reusable calls instead of raw payloads.
- Large JSON bodies go to files under `samples/` and are loaded with `read()`.
- Keep global variables to `variables.feature`; prefer local `def`.
- Tags: `@Positive` / `@Negative` on every scenario (plus `@C<id>` first, see the skill).
- File names: kebab-case, short (≤ 80 characters with `.feature`), naming the rule, not the implementation.

## 7. Runners and registration after PR #2426

- Runner classes hold `private static final String[] FEATURES = { … }` and two entry points (`runFeatures` for the shared pool, `runFeaturesSeparately` for `test.mode=no-shared-pool`). Register a feature by appending its name to the array of exactly one runner.
- Do not add JUnit `@Test` methods, enums or new runner classes for a single feature.
- A feature name appears in one runner only, across the whole project. Registering it in two runners runs it twice and duplicates its TestRail results.
- The Test Group of the TestRail case decides the runner: Critical Path, Extended or the default runner of the module.

## 8. Before you add a scenario: is it already covered?

Old tests were rewritten, merged and renamed during FAT-13426 / FAT-20199, so a rule can live in a feature whose name does not mention it. Search by behaviour, not by file name:

1. `grep -rln` the endpoint, the changed field, the error code and the state transition (for example `workflowStatus = 'Open'` after `unopenOrder`) across the team folder, including `cross-modules/`.
2. Read the scenarios you find. Same trigger, same precondition, same asserted outcome means covered: cite it and do not write a new scenario.
3. Same workflow but a missing assertion or a missing variant: add the assertion or a scenario to that feature rather than a new file.
4. Check TestRail for Karate cases with the same `refs` or the same outcome; a covered rule keeps its existing C-id.
