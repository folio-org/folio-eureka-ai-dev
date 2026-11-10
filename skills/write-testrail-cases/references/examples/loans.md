# Golden example — Loans

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** API-level case ([API] prefix) for renewal errors that cannot be reproduced in the UI: request, status code and exact error message per scenario.

### C1505018 — [API] Check error handling for loan renewal scenarios that cannot be reproduced on UI

Source: [C1505018](https://foliotest.testrail.io/index.php?/cases/view/1505018) · Type Functional · Priority Medium · Test Group Extended · refs UIU-3537,CIRC-2632

```
Preconditions:
One item has been checked out to the patron (applied loan policy allows renewals); created loan has never be renewed
Note patron and item barcodes, and any existing service point ID
User has "Postman" or similar tool

Steps:
1. Action:   Send the following API request:
             - Method: POST
             - Endpoint: {{host}}/circulation/renew-by-barcode
             Headers:
             - Content-Type = application/json
             - X-okapi-tenant = {{tenant name}}
             Body:
             {
             "userBarcode":"{{User barcode from Preconditions}}",
             "servicePointId":"{{SP from Preconditions}}"
             }
   Expected: 422 error appears:
             {
                 "errors": [
                     {
                         "message": "Renewal request must have an item barcode",
                         "parameters": [
                             {
                                 "key": "itemBarcode",
                                 "value": null
                             }
                         ],
                         "code": "RENEWAL_REQUEST_ITEM_BARCODE_REQUIRED"
                     }
                 ]
             }
2. Action:   Send the following API request:
             - Method: POST
             - Endpoint: {{host}}/circulation/renew-by-barcode
             Headers:
             - Content-Type = application/json
             - X-okapi-tenant = {{tenant name}}
             Body:
             {
             "itemBarcode":"{{Item barcode from Preconditions}}",
             "servicePointId":"{{SP from Preconditions}}"
             }
   Expected: 422 error appears:
             {
                 "errors": [
                     {
                         "message": "Renewal request must have a user barcode",
                         "parameters": [
                             {
                                 "key": "userBarcode",
                                 "value": null
                             }
                         ],
                         "code": "RENEWAL_REQUEST_USER_BARCODE_REQUIRED"
                     }
                 ]
             }
3. Action:   Send the following API request:
             - Method: POST
             - Endpoint: {{host}}/circulation/renew-by-barcode
             Headers:
             - Content-Type = application/json
             - X-okapi-tenant = {{tenant name}}
             Body:
             {
             "itemBarcode":"{{non-existent item barcode}}",
             "userBarcode":"{{User barcode from Preconditions}}",
             "servicePointId":"{{SP from Preconditions}}"
             }
   Expected: 422 error appears:
             {
                 "errors": [
                     {
                         "message": "No item with barcode {{barcode}} exists",
                         "parameters": [
                             {
                                 "key": "itemBarcode",
                                 "value": "non-existent"
                             }
                         ],
                         "code": "ITEM_BARCODE_NOT_FOUND"
                     }
                 ]
             }
4. Action:   Send the following API request:
             - Method: POST
             - Endpoint: {{host}}/circulation/renew-by-barcode
             Headers:
             - Content-Type = application/json
             - X-okapi-tenant = {{tenant name}}
             Body:
             {
             "itemBarcode":"{{Item barcode from Preconditions}}",
             "userBarcode":"{{non-existent user barcode}}",
             "servicePointId":"{{SP from Preconditions}}"
             }
   Expected: 422 error appears:
             {
                 "errors": [
                     {
                         "message": "Cannot renew item checked out to different user",
                         "parameters": [
                             {
                                 "key": "userBarcode",
                                 "value": "non-existent"
                             }
                         ],
                         "code": "ITEM_CHECKED_OUT_TO_DIFFERENT_USER"
                     }
                 ]
             }
5. Action:   Send the following API request:
             - Method: POST
             - Endpoint: {{host}}/circulation/renew-by-barcode
             Headers:
             - Content-Type = application/json
             - X-okapi-tenant = {{tenant name}}
             Body:
             {
               "userBarcode": "{{User barcode from Preconditions}}",
               "itemBarcode": "{{Item barcode from Preconditions}}",
               "servicePointId":"{{SP from Preconditions}}",
               "overrideBlocks": {
                 "patronBlock": {},
                 "renewalBlock":{},
                 "renewalDueDateRequiredBlock":{
                   "dueDate":"2026-09-30T12:53:00Z"
                 },
                 "comment": "test"
               }
             }
   Expected: 422 error appears:
             {
                 "errors": [
                     {
                         "message": "Override renewal does not match any of expected cases: item is not loanable, item is not renewable, reached number of renewals limit,renewal date falls outside of the date ranges in the loan policy, items cannot be renewed when there is an active recall request, item is Declared lost, item is Aged to lost, renewal would not change the due date, loan has reminder fees",
                         "parameters": [
                             {
                                 "key": "loanPolicyName",
                                 "value": "{{Loan policy name}}"
                             },
                             {
                                 "key": "loanPolicyId",
                                 "value": "{{Loan policy ID}}"
                             }
                         ],
                         "code": "OVERRIDE_RENEWAL_NOT_ALLOWED_FOR_CURRENT_LOAN"
                     }
                 ]
             }
6. Action:   - Login to Folio as admin user
             - Go to User from Preconditions details pane
             - Click "Actions" button
             - Select "Edit" option
             - Select "Inactive" option from "Status" dropdown
             - Click "Save & close" button
   Expected: Selected status is displayed on user details pane
7. Action:   Send the following API request:
             - Method: POST
             - Endpoint: {{host}}/circulation/renew-by-barcode
             Headers:
             - Content-Type = application/json
             - X-okapi-tenant = {{tenant name}}
             Body:
             {
             "itemBarcode":"{{Item barcode from Preconditions}}",
             "userBarcode":"{{User barcode from Preconditions}}",
             "servicePointId":"{{SP from Preconditions}}"
             }
   Expected: 422 error appears:
             {
                 "errors": [
                     {
                         "message": "Cannot renew loan when user is inactive or expired",
                         "parameters": [
                             {
                                 "key": "reason",
                                 "value": "User is inactive."
                             }
                         ],
                         "code": "USER_IS_INACTIVE_OR_EXPIRED"
                     }
                 ]
             }
8. Action:   - Go back to User from Preconditions details pane
             - Expand "Loans" accordion
             - Click "<X> open loans" hyperlink
   Expected: "Renewal count" has "0" value for the loan from Preconditions
```
