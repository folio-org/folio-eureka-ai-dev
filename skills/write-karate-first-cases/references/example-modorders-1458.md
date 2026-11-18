# Worked example: MODORDERS-1458

End-to-end run of this skill (November 2026). Result: TestRail C1621341, C1621342; PR folio-org/folio-integration-tests#2619.

## Phase 1 — Analysis

- Story MODORDERS-1458 "Do not overwrite approvalDate when opening an order" is test-only; the fix is MODORDERS-1456 (mod-orders PR #1332, commit `4f016d4`).
- Fix diff: `OrderValidationService.checkOrderApprovalRequired` used to call `setApprovedById(currentUser)` and `setApprovalDate(new Date())` on **every** transition to Open. Now `PurchaseOrderHelper.setOrderApprovalDetails` sets each field **only when it is null**.
- Trigger: any PUT that moves the order from Pending to Open. Not dependent on the `approvals.isApprovalRequired` setting.
- Existing coverage: no Karate feature asserts `approvalDate`; manual UI case C736774 was updated by the team for this story.
- Shared state: `approvals.isApprovalRequired` is tenant-wide and mod-orders caches it for 60 s; toggling it would break parallel open-order features. Not needed — the changed code runs without it.

| # | Scenario | Layer | Fails before fix because | Coverage | Target |
|---|---|---|---|---|---|
| 1 | Approval details from first opening survive unopen + open | Karate | second open overwrote both fields | none | new feature, Extended |
| 2 | Approval date set while Pending survives opening; approvedById filled | Karate | open overwrote approvalDate | none | same feature |

Scenario 2 also proves the per-field "only when null" logic: `approvalDate` is kept, `approvedById` (empty) is filled.

## Phase 2 — TestRail case (C1621342, as posted)

Plain business language: no endpoints, no status codes, no UI clicks. Capabilities are listed for people; the feature does not model them.

- Title: Approval date set on a pending order is not overwritten when the order is opened
- Section 105 (Orders), Type Functional, Priority Medium, Test Group Extended, Execution Type Karate, Automation Scope Karate Approved, Dev Team Thunderjet, refs `MODORDERS-1458,MODORDERS-1456`, label ai.

Preconditions (HTML):

```html
<ol>
<li>"Approval required" in Settings &gt; Orders &gt; Approvals is <strong>off</strong> (default). The behaviour does not depend on this setting.</li>
<li>User with the following capabilities/sets:<ul>
<li>data - UI-Orders Orders - view, create, edit</li>
<li>procedural - UI-Orders Order Approve - execute</li></ul></li>
<li>Records:<ul>
<li>Fund A with an active budget of $1,000.00</li>
<li>Order O: One-time, Pending, not approved, with one PO line paid from Fund A (100%)</li></ul></li>
</ol>
```

| # | Action | Expected |
|---|---|---|
| 1 | Approve Order O with approval date 15 January 2026, 10:00 UTC, leaving Approved by empty | Order O is saved |
| 2 | Check the approval details of Order O | Pending; Approved = yes; Approval date = 15 January 2026, 10:00 UTC (remember as D0); Approved by is empty |
| 3 | Open Order O | Order O is opened |
| 4 | Check the approval details of Order O | Open; Approved = yes; Approval date = D0, not the time of opening; Approved by is the user who opened the order |

The feature turns these steps into requests (`PUT /orders/composite-orders/{id}` with `approved`, `approvalDate`; `openOrder`; `GET` with `match`), keeping the step numbers as `# 1.` to `# 4.` comments.

## Phase 3 — Feature

`acquisitions/src/main/resources/thunderjet/mod-orders/features/open-order-approval-details-not-overwritten.feature`, registered at the end of `OrdersExtendedApiTest.FEATURES` and `mod-orders/orders.feature`.

```gherkin
# For MODORDERS-1458, https://foliotest.testrail.io/index.php?/cases/view/1621341, https://foliotest.testrail.io/index.php?/cases/view/1621342
Feature: Approval Details Are Not Overwritten When Opening An Order

  Background:
    * print karate.info.scenarioName
    * url baseUrl

    * callonce login testAdmin
    * def okapitokenAdmin = okapitoken
    * callonce login testUser
    * def okapitokenUser = okapitoken
    * def headersUser = { 'Content-Type': 'application/json', 'x-okapi-token': '#(okapitokenUser)', 'Accept': 'application/json', 'x-okapi-tenant': '#(testTenant)' }
    * def headersAdmin = { 'Content-Type': 'application/json', 'x-okapi-token': '#(okapitokenAdmin)', 'Accept': 'application/json', 'x-okapi-tenant': '#(testTenant)' }
    * configure headers = headersUser
    * configure retry = { count: 10, interval: 500 }

    * callonce variables

    * def fundId = call uuid
    * def budgetId = call uuid
    * configure headers = headersAdmin
    * def v = call createFund { id: '#(fundId)' }
    * def v = call createBudget { id: '#(budgetId)', fundId: '#(fundId)', allocated: 1000 }
    * configure headers = headersUser


  @C1621341
  @Positive
  Scenario: Approval Details Set On First Opening Are Kept After The Order Is Unopened And Opened Again
    * def orderId = call uuid
    * def poLineId = call uuid

    # 1. Create A Pending Order With One PO Line And No Approval Details
    * def v = call createOrder { id: '#(orderId)' }
    * def v = call createOrderLine { id: '#(poLineId)', orderId: '#(orderId)', fundId: '#(fundId)' }

    Given path 'orders/composite-orders', orderId
    When method GET
    Then status 200
    And match $.workflowStatus == 'Pending'
    And match $.approvalDate == '##null'
    And match $.approvedById == '##null'

    # 2. Open The Order
    * def v = call openOrder { orderId: '#(orderId)' }

    # 3. Approval Details Are Set On First Opening
    Given path 'orders/composite-orders', orderId
    And retry until response.workflowStatus == 'Open' && response.approvalDate != null && response.approvedById != null
    When method GET
    Then status 200
    * def initialApprovalDate = response.approvalDate
    * def initialApprovedById = response.approvedById

    # 4. Unopen The Order
    * def v = call unopenOrder { orderId: '#(orderId)', deleteHoldings: true }

    # 5. Approval Details Are Kept After Unopening
    Given path 'orders/composite-orders', orderId
    And retry until response.workflowStatus == 'Pending'
    When method GET
    Then status 200

    Given path 'orders/composite-orders', orderId
    When method GET
    Then status 200
    And match $.approvalDate == initialApprovalDate
    And match $.approvedById == initialApprovedById

    # 6. Open The Order Again
    * def v = call openOrder { orderId: '#(orderId)' }

    # 7. Approval Details Still Contain The Values From The First Opening
    Given path 'orders/composite-orders', orderId
    And retry until response.workflowStatus == 'Open'
    When method GET
    Then status 200

    Given path 'orders/composite-orders', orderId
    When method GET
    Then status 200
    And match $.approvalDate == initialApprovalDate
    And match $.approvedById == initialApprovedById


  @C1621342
  @Positive
  Scenario: Approval Date Set On A Pending Order Is Not Overwritten When The Order Is Opened
    * def orderId = call uuid
    * def poLineId = call uuid

    # Prerequisites: Pending Order With One PO Line
    * def v = call createOrder { id: '#(orderId)' }
    * def v = call createOrderLine { id: '#(poLineId)', orderId: '#(orderId)', fundId: '#(fundId)' }

    # 1. Approve The Order With An Explicit Approval Date
    Given path 'orders/composite-orders', orderId
    When method GET
    Then status 200
    * def order = response
    * set order.approved = true
    * set order.approvalDate = '2026-01-15T10:00:00.000+00:00'
    * remove order.approvedById
    * remove order.poLines

    Given path 'orders/composite-orders', orderId
    And request order
    When method PUT
    Then status 204

    # 2. Approval Date Is Stored And Approved By Is Empty
    Given path 'orders/composite-orders', orderId
    When method GET
    Then status 200
    And match $.workflowStatus == 'Pending'
    And match $.approved == true
    And match $.approvalDate contains '2026-01-15T10:00:00'
    And match $.approvedById == '##null'
    * def presetApprovalDate = response.approvalDate

    # 3. Open The Order
    * def v = call openOrder { orderId: '#(orderId)' }

    # 4. Approval Date Is Kept And Approved By Is Set To The Opening User
    Given path 'orders/composite-orders', orderId
    And retry until response.workflowStatus == 'Open'
    When method GET
    Then status 200

    Given path 'orders/composite-orders', orderId
    When method GET
    Then status 200
    And match $.approved == true
    And match $.approvalDate == presetApprovalDate
    And match $.approvedById == '#uuid'
```

## Phase 4 — PR notes that mattered

- Why both scenarios fail on the pre-fix code (one line each).
- Why the approval setting is not toggled (shared tenant, parallel runner, 60 s cache).
- What is unverified: mod-orders keeps a client-supplied `approvalDate` on PUT (schema allows it, not executed).
- "Not run locally — please run `sh ./runtests.sh acquisitions snapshot` or rely on CI."
