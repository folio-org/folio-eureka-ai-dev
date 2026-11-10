# Golden example — Invoices

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Budget restriction case with exact allocation, allowable expenditure/encumbrance percentages and exchange rate; asserts both the UI toast and the API error body (code + parameters).

### C1241224 — Check the expenditure restriction error messages when approving and editing an invoice with two fund distributions

Source: [C1241224](https://foliotest.testrail.io/index.php?/cases/view/1241224) · Type Functional · Priority Medium · Test Group Extended · refs MODINVOICE-631,UINV-623,FAT-29127

```
Preconditions:
1) "Primary currency (for currency symbol to display)" is set to **USD **in "Settings" -> "Tenant" -> "Language and localization"
2) "Set purchase order lines limit" is set to more than **2** in "Settings" -> "Orders" -> "Purchase order lines limit"
3) Active **Fiscal Year** (e.g. FYA2026) has been created, and its period includes the current date.
4) Active **Ledger** related to the created Fiscal year has been created. "Enforce all budget expenditure limits" option is **active**.
5) Active **Fund A **and **Fund B** related to the created Ledger with current budgets having **$100 **and **$150** money allocation have been created.
- "Allowable expenditure" limit is set to **100 %** value
- "Allowable encumbrance" limit is set to **110 %** value
6) An **Order #1** in "Open" status with **two **PO lines is created. "Fund distribution" is specified with** Fund A** in the _PO line #1_ total cost is **$50**. "Fund distribution" is specified with Fund B** in the _PO line #2_ total cost is **$50**.
7) An **Invoice #1** in "**Approved**" status and in **non-default **currency has been created based on the **Order #1** from Preconditions.
- "Use set exchange rate" checkbox is **active**
- "Set exchange rate" value is set to **2**
- "Fund distributions" in the invoice lines are specified with **Fund A **and **Fund B, **"Release encumbrance" in the invoice lines = **true**, invoice line amounts are equal to the POLs total.
8) An **Invoice #2** in "**Open**" status has been created based on the **Order #1** from Preconditions. "Fund distribution" is specified with **Fund A, **"Release encumbrance" in the invoice line = **true**, invoice line amount is equal to the POL total.
9) "Approve and pay in one click" option was set to **active **in "Settings" -> "Invoices" -> "Approvals"
10) Authorized user with following capabilities sets is logged in:
- data - UI-Orders Orders - view
- data - UI-Finance Fund-Budget - view
- data - UI-Invoice Invoice - edit
- procedural -  UI-Invoice Invoice Approve- execute
- procedural - UI-Invoice Invoice Pay - execute
11) A user is in "Invoice" app with the detail pane opened for the** Invoice #1** from Preconditions

Steps:
1. Action:   - Click "Actions" button on the "Vendor invoice number" pane
             - Select "Edit" option
   Expected: - "Edit vendor invoice number" page is displayed
             - "Set exchange rate" value is set to** 2**
2. Action:   - Open DevTools
             - Enter **3** in the "Set exchange rate" field
             - Click "Save&close" button
   Expected: - "Edit vendor invoice number" page is displayed
             - Error toast message "Fund distribution amount exceeds the allowable expenditure amount in the **[Fund A Code]** fund.
             - The response from PUT request to invoice/invoices returns the following 422 error:
             {
               "errors" : [ {
                 "message" : "Expenditure restriction does not allow this operation",
                 "code" : "budgetRestrictedExpendituresError",
                 "parameters" : [ {
                   "key" : "fundCode",
                   "value" : "fundCode"
                 }, {
                   "key" : "budgetId",
                   "value" : "69c4d0c8-8765-432f-aeb6-209f36cbe1f1"
                 }, {
                   "key" : "remaining",
                   "value" : "-50.0"
                 }, {
                   "key" : "allocated",
                   "value" : "100.0"
                 }, {
                   "key" : "netTransfers",
                   "value" : "0.0"
                 }, {
                   "key" : "allowableExpenditure",
                   "value" : "1.0"
                 }, {
                   "key" : "awaitingPayment",
                   "value" : "150.0"
                 }, {
                   "key" : "credited",
                   "value" : "0.0"
                 }, {
                   "key" : "expended",
                   "value" : "0.0"
                 } ]
               } ],
               "total_records" : 1
             }
3. Action:   - Close "Edit vendor invoice number" page
             - Navigate to the Invoice #2 from Preconditions
   Expected: - "Vendor invoice number" pane is displayed
             - "Status" is "Open"
4. Action:   - Open DevTools
             - Click "Actions" button
             - Select "Approve&Pay" option
             - Click "Submit" in the appeared modal
   Expected: - "Vendor invoice number" page is displayed
             - Error toast message "Fund distribution amount exceeds the allowable expenditure amount in the **[Fund A Code]** fund.
             - The response from PUT request to invoice/invoices returns the following 422 error:
             {
               "errors" : [ {
                 "message" : "Expenditure restriction does not allow this operation",
                 "code" : "budgetRestrictedExpendituresError",
                 "parameters" : [ {
                   "key" : "fundCode",
                   "value" : "
             {
               "errors" : [ {
                 "message" : "Expenditure restriction does not allow this operation",
                 "code" : "budgetRestrictedExpendituresError",
                 "parameters" : [ {
                   "key" : "fundCode",
                   "value" : "fa"
                 }, {
                   "key" : "budgetId",
                   "value" : "69c4d0c8-8765-432f-aeb6-209f36cbe1f1"
                 }, {
                   "key" : "remaining",
                   "value" : "-50.0"
                 }, {
                   "key" : "allocated",
                   "value" : "100.0"
                 }, {
                   "key" : "netTransfers",
                   "value" : "0.0"
                 }, {
                   "key" : "allowableExpenditure",
                   "value" : "1.0"
                 }, {
                   "key" : "awaitingPayment",
                   "value" : "150.0"
                 }, {
                   "key" : "credited",
                   "value" : "0.0"
                 }, {
                   "key" : "expended",
                   "value" : "0.0"
                 } ]
               } ],
               "total_records" : 1
             }
             "
                 }, {
                   "key" : "budgetId",
                   "value" : "69c4d0c8-8765-432f-aeb6-209f36cbe1f1"
                 }, {
                   "key" : "remaining",
                   "value" : "-50.0"
                 }, {
                   "key" : "allocated",
                   "value" : "100.0"
                 }, {
                   "key" : "netTransfers",
                   "value" : "0.0"
                 }, {
                   "key" : "allowableExpenditure",
                   "value" : "1.0"
                 }, {
                   "key" : "awaitingPayment",
                   "value" : "150.0"
                 }, {
                   "key" : "credited",
                   "value" : "0.0"
                 }, {
                   "key" : "expended",
                   "value" : "0.0"
                 } ]
               } ],
               "total_records" : 1
             }
5. Action:   - Click on the Invoice line #1 record in the "Invoice lines" accordion
             - Click on the **Fund A** in the "Fund distribution" accordion
             - Click on the record in the "Current budget" accordion
   Expected: - Current budget page is displayed
             - In the "Financial activity & overages" table:
             - "Encumbered" is $0.00**
             - "Awaiting payment" is $100.00**
6. Action:   Click "View transactions" link in the "Budget information" accordion
   Expected: - "Transactions" page is displayed for Fund A
             - There are only **three **transactions in the list:
                - "Pending payment" - **(**$100.00)**
                - "Encumbrance" - $0.00
                - "Allocation" - $100.00**
7. Action:   - Navigate to the Fund B details pane
             - Click on the record in the "Current budget" accordion
   Expected: - Current budget page is displayed
             - In the "Financial activity & overages" table:
             - "Encumbered" is $0.00**
             - "Awaiting payment" is $100.00**
8. Action:   Click "View transactions" link in the "Budget information" accordion
   Expected: - "Transactions" page is displayed for Fund B
             - There are only **three **transactions in the list:
                - "Pending payment" - **(**$100.00)**
                - "Encumbrance" - $0.00
                - "Allocation" - $150.00**
```
