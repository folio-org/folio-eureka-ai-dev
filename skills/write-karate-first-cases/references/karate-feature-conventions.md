# Karate feature conventions

Skeleton of a new feature and the mapping from a TestRail case to a scenario. When the owning team has rules files (`<project>/ai/`), they win on every point they cover.

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

The rules, with their scope (all teams or one team), are in `karate-standards.md`. Copy login and headers from an exemplar feature of the target folder; the skeleton shows the acquisitions style.

## Mapping a TestRail Karate case to a scenario

| TestRail | Feature |
|---|---|
| Case title | `Scenario:` name (Title Case) |
| Case ID | `@C<id>` tag + header URL |
| Preconditions → records | `# Prerequisites:` block of reusable calls |
| Preconditions → capabilities | Not modelled: the project's test users have a fixed permission set (init feature). If the scenario fails for a missing permission, add it to the init feature and say so in the PR |
| Step N action | `# N.` comment + request or reusable call |
| Step N expected status | `Then status <code>` |
| Step N expected fields | `And match` lines (or `retry until` + separate GET for async) |
| `remember as D1` | `* def d1 = response.<field>` |
