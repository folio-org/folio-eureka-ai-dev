# Karate feature conventions

Apply these when the owning team has no rules file. When it has one (for example `acquisitions/ai/ACQ_ORDERS_SYSTEM_PROMPT.md`), the team file wins on every point it covers.

## Skeleton

```gherkin
# For MODXXX-123, https://foliotest.testrail.io/index.php?/cases/view/1234567
Feature: <Business Outcome In Title Case>

  Background:
    * print karate.info.scenarioName
    * url baseUrl

    # Copy login and headers from a neighbouring feature in the same folder
    * callonce login testAdmin
    * def okapitokenAdmin = okapitoken
    * callonce login testUser
    * def okapitokenUser = okapitoken
    * def headersUser = { 'Content-Type': 'application/json', 'x-okapi-token': '#(okapitokenUser)', 'Accept': 'application/json', 'x-okapi-tenant': '#(testTenant)' }
    * def headersAdmin = { 'Content-Type': 'application/json', 'x-okapi-token': '#(okapitokenAdmin)', 'Accept': 'application/json', 'x-okapi-tenant': '#(testTenant)' }
    * configure headers = headersUser
    * configure retry = { count: 10, interval: 500 }

    * callonce variables


  @C1234567
  @Positive
  Scenario: <TestRail Case Title In Title Case>
    * def entityId = call uuid

    # Prerequisites: <Records The Case Creates>
    * def v = call createSomething { id: '#(entityId)' }

    # 1. <TestRail Step 1 In Title Case>
    Given path 'module/entities', entityId
    When method GET
    Then status 200
    And match $.status == 'Pending'

    # 2. <Trigger Step>
    * def v = call doTransition { id: '#(entityId)' }

    # 3. <Resulting State>
    Given path 'module/entities', entityId
    And retry until response.status == 'Done'
    When method GET
    Then status 200

    Given path 'module/entities', entityId
    When method GET
    Then status 200
    And match $.someField == expectedValue
```

## Rules

| Topic | Rule |
|---|---|
| Header | `# For <JIRA-KEY>, <TestRail case URL>[, <URL>]` — first line of the file |
| Tags | `@C<id>` alone on the first tag line, then `@Positive` or `@Negative`. Exactly one `@C` per scenario. No `@T` tags |
| Names | Feature, scenario names and comments in Title Case. Scenario name = TestRail case title |
| Steps | `# N. …` comments, numbered to match TestRail steps; `# Prerequisites: …` for setup. No `* print` inside scenarios |
| IDs | `call uuid` inside each scenario. Background-level IDs only for data that every scenario may share safely |
| Parallelism | Scenarios must run in parallel. Never add `@parallel=false` to a new feature |
| Reusables | Call by `karate-config.js` key (`call createOrder { … }`), parameters from the reusable's `# parameters:` header |
| Waiting | `retry until <all conditions>` only after async triggers. Do not mix `retry until` and `match` in one request block — wait first, then GET again and `match` |
| Assertions | `match $.field == value` right after the request. Presence markers: `'##null'` absent-or-null, `'#notnull'`, `'#uuid'`, `'#string'`, `'#[1]'` array of size 1 |
| Captured values | `* def initialValue = response.field`, compare later with `match $.field == initialValue` |
| Headers | `configure headers = headersAdmin` before admin-only calls, back to `headersUser` after; never as the last line of a scenario |
| Body changes | GET → `* def body = response` → `* set body.field = …` / `* remove body.field` → PUT |
| Amounts | TestRail amounts in brackets `($10.00)` are positive values in the API (`amount == 10.00`) |
| File name | kebab-case, ≤ 80 characters including `.feature` |

## Mapping a TestRail Karate case to a scenario

| TestRail | Feature |
|---|---|
| Case title | `Scenario:` name (Title Case) |
| Case ID | `@C<id>` tag + header URL |
| Preconditions → records | `# Prerequisites:` block of reusable calls |
| Preconditions → permissions | Already granted in the module's `init-*.feature`; if missing, add them there (and say so in the PR) |
| Step N action | `# N.` comment + request or reusable call |
| Step N expected status | `Then status <code>` |
| Step N expected fields | `And match` lines (or `retry until` + separate GET for async) |
| `remember as D1` | `* def d1 = response.<field>` |
