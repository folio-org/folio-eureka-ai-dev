# Step Patterns from the Backlog

> Common patterns first. Two rare patterns (multi-tab, DevTools/Network) are at the end of this section, marked accordingly — skip them unless the story explicitly requires that exact scenario.

**Grouped navigation (single verification point):**
```
1. Action:
   - Click "Consortium manager" app button in the header
   - Click "Select members" button
   - Check all members
   - Click "Save & close" button
   Expected:
   - "Consortium manager" app main page is opened including:
     - "Settings" pane with the settings list in alphabetical order
     - "3 members selected" text
     - "Select members" button (active)
```

**Navigating to a page:**
```
1. Action:   Navigate to Settings > Data export > Field mapping profiles
   Expected: "Field mapping profiles" pane is displayed with "New" button, search box, and table with profiles
```
> **Two navigation separators — use each in the right context:**
> - `>` — path navigation between pages/tabs: `Apps > Finance > Fund tab`, `Settings > Inventory > Call number browse`
> - `->` — selecting an item from a dropdown or Actions menu: `Click "Actions" button -> select "New"`, `Actions -> Select "Transfer"`
>
> Both appear in the same case. Use `>` when moving to a page; use `->` when selecting from a menu that appears in place.
>
> **Legacy:** older cases (releases ≤16) and some Users/Requests cases use `=>` for dropdown selection (e.g., `Click Actions menu => Select Edit`). When editing existing cases, preserve the separator already in use. When writing **new** cases, always use `->`.


**Opening an Actions menu:**
```
2. Action:   Click "Actions" menu on the mapping profile view form
   Expected: Menu expands and displays the following options: Edit, Duplicate, Delete
```

**Confirming a modal:**
```
3. Action:   Click "Delete" button on "Delete mapping profile" modal
   Expected: Modal closes, toast message "Mapping profile <name> has been successfully deleted" is displayed, profile is removed from the list
```

**Verifying a transaction/table row (column-level):**
```
4. Action:   Navigate to Finance app > Fund A > Fund A-FY-current budget > "Transactions" accordion and open the encumbrance row for the PO from Preconditions #4
   Expected: Transaction details pane displays:
             - "Type" = "Encumbrance"
             - "Source" = <PO number> (hyperlink to the PO)
             - "Amount" = $50.00
             - "Status" = "Released"
             - "Initial encumbrance" = $50.00
             - "Expended" = $0.00
```

**Verifying budget values (absolute):**
```
5. Action:   Check the budget summary for Fund A-FY-current
   Expected: - "Allocated" = $200.00
             - "Encumbered" = $0.00
             - "Available" = $200.00 (restored to full allocation)
```

**Verifying table columns:**
```
6. Action:   Verify columns in the "Field mapping profiles" table
   Expected: Table includes the following columns: Name, FOLIO record type, Format, Updated, Updated by, Status
```

**File export flow:**
```
1. Action:   Click "or choose file" button on the Jobs pane and submit a .csv file with UUIDs
   Expected: "Select job profile to run the export" modal opens with list of job profiles, search box, and disabled "Search" button

2. Action:   Click "Default holdings export job profile"
   Expected: "Are you sure you want to run this job?" modal opens with dropdown list, "Cancel" button (enabled), "Run" button (disabled)

3. Action:   Select "Holdings" from the dropdown list
   Expected: "Run" button becomes enabled

4. Action:   Click "Run" button
   Expected: Job starts; progress bar is visible in "Running" section; after completion, "Logs" pane displays new row with .mrc file as hyperlink, "Completed" status, Total = 5, Exported = 5, Failed = 0
```

**Inline edit in table (pencil icon):**
```
1. Action:   Click the "Edit" (pencil) icon next to the "Call numbers (all)" row in the table
   Expected: "Call number types" column of that row switches to an enabled multi-select dropdown; "Cancel" button (enabled) and "Save" button (disabled) appear in the "Actions" column

2. Action:   Click "Cancel" button in the "Actions" column
   Expected: Row returns to read-only state; no changes are saved
```

**Multi-select dropdown verification:**
```
1. Action:   Click the multi-select dropdown in the "Call number types" column
   Expected: Dropdown expands and displays all available options in alphabetical order; each option has a checkbox; no options are pre-selected

2. Action:   Select options one by one from the multi-select dropdown
   Expected: Each selected option appears in the input field; dropdown remains open after each selection; "Save" button becomes enabled after at least one option is selected

3. Action:   Remove all selected options from the multi-select dropdown
   Expected: Input field is empty; "Save" button becomes disabled again
```

**Drag and drop (reordering):**
```
1. Action:   Hover over the drag handle (six-dots icon) next to the custom field record
   Expected: "Change custom field order" tooltip appears; cursor changes to grab

2. Action:   Drag the custom field record to a new position in the list
   Expected: Custom field moves to the new position; order is updated in the list
```

**Tenant switching (ECS cases):**
```
1. Action:   Switch affiliation to Central tenant via the service point menu (top right) > Switch active affiliation
   Expected: Active tenant changes to Central; page reloads showing Central tenant context
```

**Cross-tenant verification (ECS cases):**
```
1. Action:   Switch affiliation to member tenant and open Loan details page for Item 1 via Circulation log
   Expected: Loan details page opened in member tenant; renewal action displayed in the actions list; due date matches the due date from the Central tenant loan
```

**Barcode scanning — patron (Circulation):**
```
1. Action:   Open "Check out" app and enter patron barcode on the "Scan patron card" pane, then click "Enter"
   Expected: Patron scanned; patron name and details displayed on the left pane
```

**Barcode scanning — item (Circulation):**
```
2. Action:   Enter item barcode on the "Scan items" pane and click "Enter"
   Expected: Item scanned; loan created; item row appears in the scanned items list with status "Checked out"
```

**Accordion expansion:**
```
1. Action:   Expand "Loans" accordion on the user details page
   Expected: "Loans" accordion expands and displays "# open loans" and "# closed loans" hyperlinks

2. Action:   Click "# closed loans" hyperlink
   Expected: "Loans" page opens with "Closed loans" tab active; loan from Preconditions #3 is displayed in the list
```

**Search & filter pane verification:**
```
1. Action:   Click "View all" button in the "Logs" pane
   Expected: Page updates with "Search & filter" pane on the left and "Logs" main pane; "Search & filter" pane contains:
             - "ID" dropdown
             - Search box
             - "Search" button (disabled)
             - "Reset all" button (disabled)
             - "Errors in export" accordion (expanded)
             - "Started running" accordion (collapsed)
             - "Ended running" accordion (collapsed)
             - "Job profile" accordion (collapsed)
             - "User" accordion (collapsed)
```
> Always list all filter accordions with their initial expanded/collapsed state, and Search/Reset buttons with their initial enabled/disabled state.

**Pagination verification:**
```
1. Action:   Scroll to the bottom of the results table
   Expected: Paginator is displayed below the table; page navigation controls are visible; total records count matches the number shown in the header
```

**Date range filter (date picker):**
```
1. Action:   Expand "Started running" accordion in the "Search & filter" pane
   Expected: "Started running" accordion expands and displays "From" and "To" date/time fields

2. Action:   Fill in "From" and "To" date fields, then click "Apply"
   Expected: Results table shows only records within the specified date range; records count updates accordingly
```

> **Rare patterns below — use only when the story explicitly requires this exact scenario.**

**Multi-tab testing (only when the story explicitly tests concurrent tabs):**
```
1. Action:   Duplicate the current browser tab while the edit form is open
   Expected: Edit form opens in the second tab showing the same state as the first tab

2. Action:   Save changes in the first tab
   Expected: Changes saved successfully in the first tab

3. Action:   Switch to the second tab and attempt to save different changes
   Expected: [expected conflict/success behavior per story requirements]
```

**DevTools / Network verification (only when the story requires verifying API response or hidden fields):**
```
1. Action:   Open browser DevTools (F12) and navigate to the Network tab
   Expected: DevTools pane is open; Network tab is active and recording requests

2. Action:   Perform the action that triggers the relevant API call
   Expected: Network tab captures the /custom-fields request; response body contains [expected field/value]; UI does NOT display [hidden field]
```

---
