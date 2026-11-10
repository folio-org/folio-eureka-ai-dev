# Golden example — Agreements

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Calculation case: fixed sample agreement and reporting period, report switched to Cost per Use, exact computed values asserted and the CSV export downloaded.

### C1301742 — Calculation: E-Journal with 2 orders, 1 invoice per order line, Cost per Use

Source: [C1301742](https://foliotest.testrail.io/index.php?/cases/view/1301742) · Type Other · Priority Medium · Test Group Extended · refs MODEUR-166

```
Preconditions:
- An agreement must be created in the agreements app
- An agreement line from the local KB is then linked to the agreement
- The 'usage data provider' data source must be created in the eUsage app, and COUNTER reports must be retrieved
- Titles from the COUNTER reports must be matched with titles from the local KB within the eUsage app
- The 'usage data provider' data source from eUsage must then be linked to the agreement in the Agreements app.
- An order with an order line must exist for the e-journal in the orders app
- An order with an order line must exist for the print magazine in the orders app
- An invoice with an invoice line must also exist for each of these orders
   - The start and end dates of the subscription, for which the invoice is issued must be entered on the invoice line
   - There must be usage statistics for the subscription period
- Both order lines (with invoice and invoice line) must be linked to the corresponding agreement line in the agreements app

Steps:
1. Action:   Go to the agreements app.
   Expected: The user is on the landing page for the agreements.
2. Action:   Search for the sample title labelled "Taylor & Francis - Sports Biomechanics (EJ)".
   Expected: The user is shown the details of the agreement.
3. Action:   Open the 'eUsage Reports' accordion.
   Expected: The user is shown a detailed view of the 'eUsage report' accordion.
4. Action:   Click 'Analyze Agreement'
   Expected: A bar chart showing the figures for 'use over time' for the past two years is shown to the user.
5. Action:   Adjust the start and end months to display January-December 2025.
   Expected: The usage figures for January-December 2025 are provided.
             When you hover your cursor over a bar, the number of views will appear in a black box.
             For example:
             Total Item Requests: 29
             Unique Item Requests: 17
6. Action:   Click 'Download CSV'.
   Expected: A CSV file containing the selected time period's usage statistics will be downloaded.
             The file contains the following information:
             - total item requests 2025
             - unique item requests 2025
7. Action:   Change the report to 'Cost per use'.
   Expected: The user will receive the 'Cost per use' figures for the period from January to December 2025.
             When you hover your cursor over a bar, the number of views will appear in a black box.
             Calculation method per scale/interval:
             - Invoice amount of both order lines / Total item requests = Cost per request (total)
             - Invoice amount of both order lines / Unique item requests = Cost per request (unique)
             For example:
             1.749,48 EUR (Invoice 1 (249,48 EUR) + Invoice 2 (1.500 EUR)) / 29 (Total item requests) = 60,33 EUR Cost per requests - total
             1.749,48 EUR (Invoice 1 (249,48 EUR) + Invoice 2 (1.500 EUR)) / 17 (Unique item requests) = 102,91 EUR Cost per requests - unique
8. Action:   Click 'Download CSV'
   Expected: A CSV file containing the selected time period's usage statistics will be downloaded.
             The file contains the following information:
             - paid amount
             - total item requests 2025
             - unique item requests 2025
             - cost per request - total
             - cost per request - unique
             - usage sorted by year of publication (0001 = the COUNTER report does not specify a publication year.)
```
