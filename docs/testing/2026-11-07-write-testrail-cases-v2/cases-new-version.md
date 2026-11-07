# Generated test cases — write-testrail-cases v2

> Generated strictly according to the v2 `SKILL.md` and its references. Step 4 (target section sampling) was performed for eHoldings > Provider (section 125), Loans > Loans: Anonymization (section 1132) and Orders (November 2026 sample). The `## Changes since …` sections of the context files were read; enrichment used `en.json`.

**Section sampling results:**
- eHoldings > Provider: `<ol>` preconditions with a nested capability-set list; user line "User with following Capability Sets is logged in:"; capability `Settings - Module Eholdings Enabled - View`; Type mostly Other; titles are factual phrases ("Provider Packages accordion …").
- Loans: Anonymization: all cases carry the `BFreviewed` label; Type Other; recent cases use the Okapi + Eureka block (C422021), so the dual block is used; path "Settings > Circulation > Loan anonymization".
- Orders: `<p>1) …</p>` preconditions; user line "A user with the following capabilities/sets is logged in:"; capability `data - UI-Orders Orders - view`; Type Functional.

---

## UIEH-1524 — Provider Record - Packages List MCL view - Add Access status type column

```
I've read the story (refs: UIEH-1524, MODKBEKBJ-839), the eHoldings context (built 2026-06-16, delta 2026-11-07) and 6 recent cases from section 125.
Business rules touched: #13 (column/filter controls in Provider Packages accordion, Tags permission), Changes since → Provider > packages list columns (UIEH-1557).

Happy path / business rule:
1. Access status type column is offered in Show columns after Package type, unchecked by default, and shows the package's value when enabled → Critical Path
Regression:
2. Existing Provider Packages columns keep their default state and order after the new option is added → Extended
3. Access status type value in the column follows edits of the package's access status type (UIEH-1564 area) and deletion of the type in Settings → Extended
4. Column selection persists after opening a Package record and returning, and after editing the Provider (C1385308 pattern) → Extended
Capability boundary:
5. User without Tags capability still sees and can enable Access status type column (Tags checkbox absent, rule #13) → Extended

Open question (not in story, not in sources): is the column available in the Packages search results list (Packages tab) as well, or only in the Provider record? — assumed Provider record only.
```

---
Title:          Provider Packages accordion shows Access status type column after it is enabled in Show columns
Type:           Other
Priority:       High
Release:        R2 2026 Umbrellaleaf
Test Group:     Critical Path
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIEH-1524, MODKBEKBJ-839

Preconditions:
1. User with following Capability Sets is logged in:
   1. Settings - Module Eholdings Enabled - View
2. Access status type "AST-1" exists in Settings > eHoldings > Access status types
3. Provider "EBSCO" has selected package "Academic Search Complete" with Access status type = "AST-1" and selected package "Academic Search Premier" with no Access status type
4. User is on eHoldings > Providers tab

Steps:
1. Action:
   - Search for Provider "EBSCO"
   - Open the Provider record
   Expected: Provider detail record is opened with "Packages" accordion
2. Action:   Click "Actions" button in "Packages" accordion
   Expected: "Show columns" section lists, in this order:
   - Status
   - Titles selected
   - Total titles
   - Content type
   - Package custom coverage
   - Package type
   - Access status type (unchecked)
   - Tags
3. Action:   Check "Access status type" in "Show columns"
   Expected: "Access status type" column appears in the Packages list right after "Package type"
4. Action:   Find packages from Preconditions #3 in the Packages list
   Expected:
   - "Academic Search Complete": Access status type = "AST-1"
   - "Academic Search Premier": Access status type is empty

NOTE (source): column labels from `ui-eholdings/en.json` `packagesList.*`; "Package name" column is always shown and is not in Show columns (context rule). Check order of Show columns options on first execution — order is taken from the MCL column order, not confirmed by a case.

---
Title:          Existing Provider Packages columns keep default visibility after Access status type option is added
Type:           Other
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIEH-1524

Preconditions:
1. User with following Capability Sets is logged in:
   1. Settings - Module Eholdings Enabled - View
2. Provider "EBSCO" has at least 2 selected packages
3. Browser local storage is cleared (no saved column selection for the Provider Packages list)

Steps:
1. Action:   Open Provider "EBSCO" record
   Expected: Packages list shows the default columns: Status, Package name, Titles selected, Total titles, Content type, Package custom coverage, Package type, Tags; "Access status type" column is not shown
2. Action:   Click "Actions" in "Packages" accordion
   Expected: In "Show columns" all options except "Access status type" are checked
3. Action:   Uncheck "Package type", then check it again
   Expected: "Package type" column disappears and returns to the same position; "Access status type" stays hidden

---
Title:          Access status type column reflects package edits and access status type deletion
Type:           Functional
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIEH-1524, UIEH-1564

Preconditions:
1. User with following Capability Sets is logged in:
   1. Settings - Module Eholdings Enabled - View
   2. Data - UI-Eholdings Records - Edit
   3. Settings - UI-Eholdings Settings Access-Types - Manage
2. Access status types "AST-1" and "AST-2" exist; "AST-2" is not assigned to any record
3. Provider "EBSCO" has selected package "Academic Search Complete" with Access status type = "AST-1"
4. "Access status type" column is enabled in the Provider "EBSCO" Packages list

Steps:
1. Action:
   - Open package from Preconditions #3 from the Packages list
   - Click "Actions" -> "Edit"
   - Set Access status type = "AST-2"
   - Click "Save & close"
   Expected: Toast "Package saved. Note: A proxy or token update may take a few minutes and may require refreshing page." is displayed; Package record shows Access status type = "AST-2"
2. Action:   Close the Package record ("X")
   Expected: Provider "EBSCO" Packages list shows Access status type = "AST-2" for "Academic Search Complete"
3. Action:
   - Edit the package again and set Access status type = "AST-1", "Save & close"
   - Navigate to Settings > eHoldings > Access status types, delete unassigned "AST-2" (confirm in "Delete Access status type" modal)
   Expected: Toast "The access status type AST-2 has been deleted."
4. Action:   Return to Provider "EBSCO" Packages list
   Expected: "Academic Search Complete" shows Access status type = "AST-1"

---
Title:          Provider Packages Access status type column selection persists after opening a package and editing the provider
Type:           Other
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIEH-1524

Preconditions:
1. User with following Capability Sets is logged in:
   1. Settings - Module Eholdings Enabled - View
   2. Data - UI-Eholdings Records - Edit
2. Provider "EBSCO" record is opened; "Access status type" column is enabled in "Packages" accordion

Steps:
1. Action:   Open any package from the Packages list, then close it ("X")
   Expected: Provider record is shown; "Access status type" column is still displayed
2. Action:
   - Click "Actions" -> "Edit" on the Provider record
   - Change "Provider token" or proxy and click "Save & close"
   Expected: Toast "Updates saved. Note: A proxy update may take a few minutes and may require refreshing page."; "Access status type" column is still displayed in Packages list

---
Title:          User without tags capability can enable Access status type column in Provider Packages accordion
Type:           Other
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIEH-1524

Preconditions:
1. User with following Capability Sets is logged in (no tags capabilities):
   1. Settings - Module Eholdings Enabled - View
2. Provider "EBSCO" has a selected package with an Access status type assigned

Steps:
1. Action:   Open Provider "EBSCO" and click "Actions" in "Packages" accordion
   Expected:
   - "Access status type" option is present in "Show columns"
   - "Tags" option and "Search by tags only" are absent
2. Action:   Check "Access status type"
   Expected: Column is displayed with the assigned value

---

## UIU-3595 — Add an "Anonymize closed loans" option to user records

```
I've read the story (refs: UIU-3595; related UICIRC-1361), Users/Loans/Circulation settings contexts (delta 2026-11-07) and recent cases from Loans: Anonymization (1132).
Business rules touched: loans.md #8 (anonymization timing), #17 (manual anonymization partial success); circulation-settings.md #10 (fee/fine exception).

⚠️ Strings for the new controls are not in ui-users / ui-circulation en.json on master yet (story In Code Review). Labels below are taken from the story text and flagged (verify exact wording on first execution).
⚠️ Story text conflict: scenario 2 says the accordion "User-specific loan anonymization" is hidden, requirements say the radio set "Anonymize closed loans" in "Extended information" — assumed the radio set (requirements). Please confirm.

Happy path:
1. Radio set shown in view + edit when tenant allows it; default "According to library policy"; saving each option → Critical Path
Business rules (anonymization outcome, checked in Closed loans):
2. "Never" — closed loans stay with the user while tenant policy = Immediately → Critical Path
3. "As early as possible" — fee-free loans anonymized after duration X; loans with fees after Y when "Treat closed loans with associated fee/fines differently" is on → Critical Path (journey)
4. "As early as possible" with nothing set for the earliest duration → falls back to tenant policy → Extended
Regression:
5. "According to library policy" user follows tenant policy exactly as before the change → Extended
6. Manual "Anonymize all loans" for a user with "Never" — ⚠️ behaviour not defined in the story; not generated, question to PO
7. Editing other Extended information fields doesn't reset the preference; change appears in user Version history (UIU-3388) → Extended
Negative / settings:
8. Tenant setting disabled → radio set hidden in view and edit; existing "Never" preference is ignored and tenant policy applies → Extended
Capability boundary:
9. User with view-only Users capability sees the value but cannot change it → Extended
```

---
Title:          Anonymize closed loans preference is shown and saved in user Extended information when user-specific anonymization is allowed
Type:           Other
Priority:       High
Release:        R2 2026 Umbrellaleaf
Test Group:     Critical Path
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai, BFreviewed
References:     UIU-3595, UICIRC-1361

Preconditions:
1. User is logged in with permissions:
   - Users: Can view, edit, and create users
   For Eureka environments, use following capabilities/sets (type - resource - action):
   - data - UI-Users - edit
2. Settings > Circulation > Loan anonymization: user-specific loan anonymization is allowed (verify exact label on first execution — story: "Allow user specific anonymization settings for closed loans")
3. Patron user exists with no anonymization preference set
4. User is on Users app

Steps:
1. Action:   Search for the patron from Preconditions #3, open the record and expand "Extended information"
   Expected: "Anonymize closed loans" = "According to library policy"
2. Action:   Click "Actions" -> "Edit" and expand "Extended information"
   Expected: Radio set "Anonymize closed loans" with options "According to library policy" (selected), "As early as possible", "Never"
3. Action:   Select "As early as possible" and click "Save & close"
   Expected: User record is saved; "Anonymize closed loans" = "As early as possible" in Extended information
4. Action:   Edit again, select "Never", click "Save & close"
   Expected: "Anonymize closed loans" = "Never"
5. Action:   Edit again, select "According to library policy", click "Save & close"
   Expected: "Anonymize closed loans" = "According to library policy"

---
Title:          Closed loans of user with Never preference are not anonymized when tenant policy anonymizes immediately
Type:           Other
Priority:       High
Release:        R2 2026 Umbrellaleaf
Test Group:     Critical Path
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai, BFreviewed
References:     UIU-3595

Preconditions:
1. User is logged in with permissions:
   - Users: Can view, edit, and create users; Users: User loans view; Check out: All permissions; Check in: All permissions
   For Eureka environments, use following capabilities/sets (type - resource - action):
   - data - UI-Users - edit
   - data - UI-Users Loans - view
   - procedural - UI-Checkout Circulation - execute (verify name)
   - procedural - UI-Checkin Circulation - execute (verify name)
2. Settings > Circulation > Loan anonymization: "Anonymize closed loans" = "Immediately after loan closes"; user-specific loan anonymization allowed
3. Patron A: "Anonymize closed loans" = "Never"; Patron B: "According to library policy"
4. Item 1 (<barcode 1>) is checked out to Patron A; Item 2 (<barcode 2>) to Patron B; no fees/fines

Steps:
1. Action:   Check in Item 1 and Item 2 in Check in app
   Expected: Both items checked in; status "Available"
2. Action:   After the anonymization job runs, open Patron A > "Loans" > "Closed loans"
   Expected: Loan for Item 1 is listed with Patron A (not anonymized)
3. Action:   Open Patron B > "Loans" > "Closed loans"
   Expected: Loan for Item 2 is not listed (anonymized per tenant policy)

---
Title:          As early as possible preference anonymizes fee-free and fee/fine loans by their own durations
Type:           Other
Priority:       High
Release:        R2 2026 Umbrellaleaf
Test Group:     Critical Path
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai, BFreviewed
References:     UIU-3595, UICIRC-1361

Preconditions:
1. User is logged in with permissions:
   - Users: Can view, edit, and create users; Users: User loans view; Users: Can create, edit and remove fees/fines; Check out: All permissions; Check in: All permissions
   For Eureka environments, use following capabilities/sets (type - resource - action):
   - data - UI-Users - edit
   - data - UI-Users Loans - view
   - data - UI-Users Feesfines Actions - manage (verify name)
2. Settings > Circulation > Loan anonymization:
   - "Anonymize closed loans" = "Never"
   - "If the user requests anonymization as early as possible, then anonymize closed loans" = "Immediately after loan closes"
   - "Treat closed loans with associated fee/fines differently" = on, "1 hour(s) after fee/fine closes" (Y)
3. Patron has "Anonymize closed loans" = "As early as possible"
4. Item 1 (<barcode 1>) and Item 2 (<barcode 2>) are checked out to the patron; Item 2 loan has a closed manual fee/fine

Steps:
1. Action:   Check in Item 1 and Item 2
   Expected: Both loans are closed
2. Action:   After the anonymization job runs, open patron > "Loans" > "Closed loans"
   Expected: Item 1 loan is not listed (anonymized immediately); Item 2 loan is still listed
3. Action:   After 1 hour (Y) and the next job run, reopen "Closed loans"
   Expected: Item 2 loan is no longer listed
4. Action:   Open Circulation log, filter by <barcode 2>
   Expected: Loan entries show the patron as anonymized (verify how anonymized loans are displayed on first execution)

---
Title:          As early as possible preference falls back to library policy when no earliest duration is configured
Type:           Other
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai, BFreviewed
References:     UIU-3595

Preconditions:
1. User is logged in with permissions as in the previous case (Users edit, loans view, check in/out)
2. Settings > Circulation > Loan anonymization: "Anonymize closed loans" = "Never"; earliest duration for "As early as possible" is not specified
3. Patron has "Anonymize closed loans" = "As early as possible"; Item (<barcode>) is checked out to the patron

Steps:
1. Action:   Check in the item and wait for the anonymization job
   Expected: Item is checked in
2. Action:   Open patron > "Loans" > "Closed loans"
   Expected: Loan is still listed (tenant policy "Never" applied as fallback)

---
Title:          Anonymize closed loans preference is hidden and ignored when user-specific anonymization is not allowed
Type:           Other
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai, BFreviewed
References:     UIU-3595

Preconditions:
1. User is logged in with permissions: Users: Can view, edit, and create users; Users: User loans view; Check in/Check out: All permissions
   For Eureka environments, use following capabilities/sets (type - resource - action):
   - data - UI-Users - edit
   - data - UI-Users Loans - view
2. Patron has "Anonymize closed loans" = "Never" (set while the tenant setting was allowed)
3. Settings > Circulation > Loan anonymization: user-specific loan anonymization switched off; "Anonymize closed loans" = "Immediately after loan closes"
4. Item (<barcode>) is checked out to the patron

Steps:
1. Action:   Open the patron record and expand "Extended information"
   Expected: "Anonymize closed loans" is not displayed
2. Action:   Click "Actions" -> "Edit", expand "Extended information"
   Expected: Radio set "Anonymize closed loans" is not displayed
3. Action:   Check in the item; after the anonymization job open "Closed loans"
   Expected: Loan is not listed — tenant policy applies, stored "Never" is ignored (verify with PO: story does not state this explicitly)

---
Title:          Changing anonymization preference keeps other Extended information values and is recorded in user version history
Type:           Other
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai, BFreviewed
References:     UIU-3595, UIU-3388

Preconditions:
1. User is logged in with permissions: Users: Can view, edit, and create users
   For Eureka environments, use following capabilities/sets (type - resource - action):
   - data - UI-Users - edit
2. User-specific loan anonymization is allowed; Version history is enabled in Settings > Users
3. Patron has Extended information filled: Date enrolled, Folio number, Preferred contact = Email, "Anonymize closed loans" = "According to library policy"

Steps:
1. Action:   Edit the patron, set "Anonymize closed loans" = "Never", click "Save & close"
   Expected: Extended information shows "Never"; Date enrolled, Folio number and Preferred contact are unchanged
2. Action:   Open "Version history" on the user record
   Expected: Latest entry shows the change of the anonymization preference by the current user (verify field label on first execution)

> Not generated (v2 rule: new cases are never set to Draft; undefined behaviour is raised as a question instead): **"Manual Anonymize all loans for user with Never preference"** — neither UIU-3595 nor UICIRC-1361 states whether "Never" blocks manual anonymization. The question is listed in the Scenario Analysis above.

---
Title:          User with view-only Users capability sees but cannot change anonymization preference
Type:           Other
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai, BFreviewed
References:     UIU-3595

Preconditions:
1. User is logged in with permissions: Users: Can view user profile
   For Eureka environments, use following capabilities/sets (type - resource - action):
   - data - UI-Users - view
2. User-specific loan anonymization is allowed; Patron has "Anonymize closed loans" = "As early as possible"

Steps:
1. Action:   Open the patron record, expand "Extended information"
   Expected: "Anonymize closed loans" = "As early as possible" is displayed read-only
2. Action:   Check "Actions" menu
   Expected: "Edit" is absent

---

## UIOR-1497 — Add order filter status to Orders app

```
I've read the story (refs: UIOR-1497; requires MODORDSTOR-526 — transmission method propagated to POLs; blocked by UIORGS-477), the Orders context (delta 2026-11-07) and the Orders section norms.
Story status: Blocked — cases depend on UIORGS-477 (email integration method) for the "Email" option data.

Happy path:
1. Accordions placement + options → Extended
Business rules:
2. Exported Yes / No / both / none → Critical Path
3. Transmission method single + multiple → Critical Path
4. Export date column rightmost, sortable asc/desc → Extended
Regression:
5. Existing Export date filter (date range + validation) unchanged and combinable with Exported / Transmission method; Reset all clears the new filters → Extended
6. Orders toggle (PO level) is not affected — new accordions only on Order lines → Extended
7. Export results (CSV) from a filtered Order lines list contains only the filtered POLs → Extended
Localization:
8. German labels → Extended
```

---
Title:          Exported and Transmission method accordions are placed around Export date on Order lines pane
Type:           Functional
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIOR-1497

Preconditions:
<p>1) A user with the following capabilities/sets is logged in:</p>
<ul><li>data - UI-Orders Orders - view</li></ul>
<p>2) User is on Orders app</p>

Steps:
1. Action:   Click "Order lines" toggle on "Search & filter" pane
   Expected: "Order lines" toggle is active
2. Action:   Check filter accordions around "Export date"
   Expected: "Exported" accordion is directly above "Export date"; "Transmission method" accordion is directly below "Export date"
3. Action:   Expand "Exported" and "Transmission method"
   Expected:
   - Exported: "Yes", "No" (unchecked)
   - Transmission method: "Email", "FTP", "File download" (unchecked)
4. Action:   Click "Orders" toggle
   Expected: "Exported" and "Transmission method" accordions are not displayed on the Orders pane (verify: story covers Order lines only)

---
Title:          Order lines are filtered by Exported status, both or no options return all lines
Type:           Functional
Priority:       High
Release:        R2 2026 Umbrellaleaf
Test Group:     Critical Path
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIOR-1497, MODORDSTOR-526

Preconditions:
<p>1) A user with the following capabilities/sets is logged in:</p>
<ul><li>data - UI-Orders Orders - view</li></ul>
<p>2) Open order PO-1 with POL-1 exported via EDIFACT FTP integration (Export date is populated)</p>
<p>3) Open order PO-2 with POL-2, Automatic export disabled (not exported)</p>
<p>4) User is on Orders app > Order lines with search query "*"</p>

Steps:
1. Action:   Check "Yes" in "Exported"
   Expected: POL-1 is listed, POL-2 is not; all listed lines have Export date populated
2. Action:   Uncheck "Yes", check "No"
   Expected: POL-2 is listed, POL-1 is not; listed lines have empty Export date
3. Action:   Check "Yes" as well (both selected)
   Expected: Both POL-1 and POL-2 are listed; record count equals the count with no Exported filter
4. Action:   Uncheck both
   Expected: Both POL-1 and POL-2 are listed

---
Title:          Order lines are filtered by single and multiple Transmission methods
Type:           Functional
Priority:       High
Release:        R2 2026 Umbrellaleaf
Test Group:     Critical Path
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIOR-1497, MODORDSTOR-526, UIORGS-477

Preconditions:
<p>1) A user with the following capabilities/sets is logged in:</p>
<ul><li>data - UI-Orders Orders - view</li></ul>
<p>2) Exported POLs exist with transmission methods: POL-E — Email, POL-F — FTP, POL-D — File download</p>
<p>3) User is on Orders app > Order lines with search query "*"</p>

Steps:
1. Action:   Check "Email" in "Transmission method"
   Expected: POL-E is listed; POL-F and POL-D are not
2. Action:   Check "FTP" as well
   Expected: POL-E and POL-F are listed; POL-D is not
3. Action:   Uncheck "Email" and "FTP", check "File download"
   Expected: Only POL-D is listed
4. Action:   Check "Yes" in "Exported" with "File download" selected
   Expected: POL-D is listed (filters combine with AND)

---
Title:          Export date column is the rightmost Order lines column and sorts ascending and descending
Type:           Functional
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIOR-1497

Preconditions:
<p>1) A user with the following capabilities/sets is logged in:</p>
<ul><li>data - UI-Orders Orders - view</li></ul>
<p>2) POL-1, POL-2, POL-3 are exported on different dates (D1 &lt; D2 &lt; D3); POL-4 is not exported</p>
<p>3) User is on Orders app > Order lines with search query "*"</p>

Steps:
1. Action:   Check the results table header
   Expected: "Export date" is the rightmost column
2. Action:   Click "Export date" header
   Expected: Rows ordered POL-1 (D1), POL-2 (D2), POL-3 (D3); POL-4 with empty date at the end (verify empty-value position on first execution)
3. Action:   Click "Export date" header again
   Expected: Rows ordered POL-3, POL-2, POL-1

---
Title:          Existing Export date filter works with new Exported and Transmission method filters and Reset all clears them
Type:           Functional
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIOR-1497

Preconditions:
<p>1) A user with the following capabilities/sets is logged in:</p>
<ul><li>data - UI-Orders Orders - view</li></ul>
<p>2) POL-1 exported via FTP on D1; POL-2 exported via FTP on D3 (D3 = D1 + 10 days)</p>
<p>3) User is on Orders app > Order lines with search query "*"</p>

Steps:
1. Action:   Expand "Export date", set From = D1, To = D1 + 1 day, click "Apply"
   Expected: POL-1 is listed, POL-2 is not
2. Action:   Set From later than To and click "Apply"
   Expected: Existing date-range validation message is shown (unchanged behaviour)
3. Action:   Restore a valid range D1..D3, check "Yes" in "Exported" and "FTP" in "Transmission method"
   Expected: POL-1 and POL-2 are listed
4. Action:   Click "Reset all"
   Expected: Export date, Exported and Transmission method filters are cleared; list returns to the empty pre-search state

---
Title:          Export results (CSV) from filtered Order lines contains only lines matching Exported and Transmission method filters
Type:           Functional
Priority:       Medium
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIOR-1497

Preconditions:
<p>1) A user with the following capabilities/sets is logged in:</p>
<ul><li>data - UI-Orders Orders - view</li><li>procedural - UI-Orders Order Export CSV - execute</li></ul>
<p>2) POL-E exported via Email, POL-F via FTP, POL-N not exported</p>
<p>3) User is on Orders app > Order lines with search query "*"</p>

Steps:
1. Action:   Check "Yes" in "Exported" and "Email" in "Transmission method"
   Expected: Only POL-E is listed
2. Action:
   - Click "Actions" -> "Export results (CSV)"
   - Keep "All" for PO and POL fields, click "Export"
   Expected: Toast "Export has been started successfully"; .csv file is downloaded
3. Action:   Open the .csv file
   Expected: File contains only POL-E row

---
Title:          Exported, Transmission method and Export date labels are displayed in German
Type:           Other
Priority:       Low
Release:        R2 2026 Umbrellaleaf
Test Group:     Extended
User Journey:   No
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         ai
References:     UIOR-1497

Preconditions:
<p>1) A user with the following capabilities/sets is logged in:</p>
<ul><li>data - UI-Orders Orders - view</li></ul>
<p>2) Tenant/user locale = German (Deutsch)</p>
<p>3) User is on Orders app > Order lines</p>

Steps:
1. Action:   Check filter accordions
   Expected: "Exportiert" (Ja / Nein) and "Übertragungsmethode" (E-Mail / FTP / Dateidownload)
2. Action:   Search "*" and check the rightmost column header
   Expected: "Exportdatum"
