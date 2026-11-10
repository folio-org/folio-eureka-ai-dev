# Golden example — Orders

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Lifecycle journey across Unopen → Open → Cancel → Reopen with absolute PO summary values and a column-by-column encumbrance check after every transition; financial preconditions set up through invoices with exact amounts.

### C1348668 — Encumbrance is unreleased after un-opening, reopening, and cancelling the order with related Cancelled and Paid invoices

Source: [C1348668](https://foliotest.testrail.io/index.php?/cases/view/1348668) · Type Functional · Priority Medium · Test Group Extended · refs MODORDERS-1449,MODINVOICE-628

```
Preconditions:
1) Active **Fund A** with the current budgets having $1000 money allocation has been created.
2) An **One-time** order in "Open" status with one PO line is created. "Fund distribution" is specified with **Fund A**, total cost is **$10**. "Receiving workflow" is "Synchronized order and receipt quantity".
3) An **Invoice #1** in "Open" status has been created based on the Order from Preconditions. "Fund distribution" is specified with **Fund A**, "Release encumbrance" in the invoice line = **true**, invoice line amount is **$4.00**.
4) **Invoice #1** was approved and then paid
5) An Invoice #2** in "Open" status has been created based on the Order from Preconditions. "Fund distribution" is specified with **Fund A**, "Release encumbrance" in the invoice line = **false**, invoice line amount is **$3.00**.
6) Invoice #2** was approved and then paid
7) Invoice #1 **was cancelled
8) Authorized user with following capabilities sets is logged in:
- data - UI-Orders Orders - edit
- procedural - UI-Orders Order Cancel - execute
- procedural - UI-Orders Order Reopen - execute
- procedural - UI-Orders Order Unopen - execute
- data - UI-Finance Fund-Budget - view
9) A user is in "Orders" app with the search result for the Order from Preconditions

Steps:
1. Action:   Click on the Order number from Preconditions
   Expected: - "Purchase order" details pane is displayed
             - "Workflow status" is "Open"
             - "PO summary" accordion contains the following data:
                - "Total estimated price" - $10.00
                - "Total encumbered" - **$7.00**
                - "Total expended" - **$3.00**
                - "Total credited" - $0.00
2. Action:   - Click "Actions" button
             - Select "Unopen" option
             - Click "Delete items" button in the appeared modal
   Expected: - "Purchase order" details pane is displayed
             - Toast message "The Purchase order - _number _has been successfully unopened" appears
             - "Workflow status" is "Pending"
             - "PO summary" accordion contains the following data:
                - "Total estimated price" - $10.00
                - "Total expended" -** $3.00**
                - "Total credited" - $0.00
3. Action:   - Click "Actions" button
             - Select "Open" option
             - Click "Submit" button in the appeared modal
   Expected: - "Purchase order" details pane is displayed
             - Toast message "The Purchase order - _number _has been successfully opened" appears
             - "Workflow status" is "Open"
             - "PO summary" accordion contains the following data:
                - "Total estimated price" - $10.00
                - "Total encumbered" - **$7.00**
                - "Total expended" - **$3.00**
                - "Total credited" - $0.00
4. Action:   - Click on the PO line record in the "PO lines" accordion
             - Click on the **$7.00** "Current encumbrance" hyperlink
   Expected: "Encumbrance" pane contains the following fields:
             - "Transaction date" - date and time when the order was opened
             - "Fiscal year" - FY from Preconditions
             - "Amount" - (**$7.00)**
             - "Source" - PO line number (link)
             - "Type" - Encumbrance
             - "From" - **Fund A** from Preconditions
             - "To" - blank
             - "Expense class" - blank
             - "Tags" - blank
             - "Initial encumbrance" = $10.00
             - "Awaiting payment" = $0.00
             - "Expended" - $3.00
             - "Status" = **Unreleased**
             - "Description" = blank
5. Action:   - Navigate back to the order from Preconditions
             - Click "Actions" button
             - Select "Cancel" option
             - Click "Submit" button in the appeared modal
   Expected: - "Purchase order" details pane is displayed
             - Toast message "Order was closed" appears
             - "Workflow status" is "Open"
             - "PO summary" accordion contains the following data:
                - "Total estimated price" - $10.00
                - "Total encumbered" - **$0.00**
                - "Total expended" - **$3.00**
                - "Total credited" - $0.00
6. Action:   - Click on the PO line record in the "PO lines" accordion
             - Click on the **$0.00** "Current encumbrance" hyperlink
   Expected: "Encumbrance" pane contains the following fields:
             - "Transaction date" - date and time when the order was opened
             - "Fiscal year" - FY from Preconditions
             - "Amount" - **$0.00**
             - "Source" - PO line number (link)
             - "Type" - Encumbrance
             - "From" - **Fund A** from Preconditions
             - "To" - blank
             - "Expense class" - blank
             - "Tags" - blank
             - "Initial encumbrance" = $10.00
             - "Awaiting payment" = $0.00
             - "Expended" - $3.00
             - "Status" = **Released**
             - "Description" = blank
7. Action:   - Navigate back to the order from Preconditions
             - Click "Actions" button
             - Select "Reopen" option
   Expected: - "Purchase order" details pane is displayed
             - Toast message "The Purchase order - _number _has been successfully reopened" appears
             - "Workflow status" is "Open"
             - "PO summary" accordion contains the following data:
                - "Total estimated price" - $10.00
                - "Total encumbered" - **$7.00**
                - "Total expended" -** $3.00**
                - "Total credited" - $0.00
8. Action:   - Click on the PO line record in the "PO lines" accordion
             - Click on the **$7.00** "Current encumbrance" hyperlink
   Expected: "Encumbrance" pane contains the following fields:
             - "Transaction date" - date and time when the order was opened
             - "Fiscal year" - FY from Preconditions
             - "Amount" - (**$7.00)**
             - "Source" - PO line number (link)
             - "Type" - Encumbrance
             - "From" - **Fund A** from Preconditions
             - "To" - blank
             - "Expense class" - blank
             - "Tags" - blank
             - "Initial encumbrance" = $10.00
             - "Awaiting payment" = $0.00
             - "Expended" - $3.00
             - "Status" = **Unreleased**
             - "Description" = blank
```
