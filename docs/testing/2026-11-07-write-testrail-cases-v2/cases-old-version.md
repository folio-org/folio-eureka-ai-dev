# Generated test cases — write-testrail-cases v1

> Generated strictly according to the previous `SKILL.md` and its context files (`eholdings.md` built 2026-06-16, `users.md` / `loans.md` / `circulation-settings.md`, `orders.md`). The TestRail Section ID was not requested before posting (previous step 8). Enrichment: `eholdings.md` did not meet the step 1b triggers, so no enrichment ran; for Users/Loans the "Known gaps > 5" trigger fired and `translations/ui-users/en_US.json` was read (it contains no strings for the user-level anonymization preference).

---

## UIEH-1524 — Provider Record - Packages List MCL view - Add Access status type column

Scenario Analysis (v1): business rules touched — #13 (Tags/permissions controls in the Packages accordion); column chooser pattern "mirrors Titles accordion". Scenarios: 1) column in the column chooser, 2) column display, 3) persistence after navigation, 4) user without permissions.

---
Title:          Access status type column can be enabled in Provider Packages accordion column chooser
Type:           Functional
Priority:       High
Release:        Umbrellaleaf
Test Group:     Critical Path
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIEH-1524, MODKBEKBJ-839

Preconditions:
- Permissions (for Okapi env.):
  - Permission: eHoldings: Can view providers, packages, titles detail records
  For Eureka environment user with following capabilities/sets is logged in:
  - Settings - Module Eholdings Enabled - View
- Provider "EBSCO" exists with at least 2 selected packages; one package has Access status type "Access status type 1" assigned
- User is on eHoldings > Providers tab

Steps:
1. Action:   Search for Provider "EBSCO" and open the Provider record
   Expected: Provider detail record is displayed with "Packages" accordion expanded
2. Action:   Click "Actions" button in "Packages" accordion
   Expected: Actions menu expands with "Search by tags only", "Search by access status types only", "Sort options", "Selection status" and "Show columns" sections
3. Action:   Check "Show columns" section
   Expected: "Show columns" checkboxes are displayed; "Access status type" checkbox is present after "Package type" and is unchecked
4. Action:   Check "Access status type" checkbox
   Expected: "Access status type" column appears in the Packages list after "Package type" column
5. Action:   Check value of "Access status type" column for the package from Preconditions #2
   Expected: Column displays "Access status type 1"; other packages show an empty value

---
Title:          Access status type column selection is retained after navigating to Package record and back
Type:           Functional
Priority:       Medium
Release:        Umbrellaleaf
Test Group:     Extended
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIEH-1524

Preconditions:
- Permissions (for Okapi env.):
  - Permission: eHoldings: Can view providers, packages, titles detail records
  For Eureka environment user with following capabilities/sets is logged in:
  - Settings - Module Eholdings Enabled - View
- Provider "EBSCO" record is opened; "Access status type" column is enabled in "Packages" accordion

Steps:
1. Action:   Click any package row in "Packages" accordion
   Expected: Package detail record opens
2. Action:   Click "X" to close Package record
   Expected: Provider record is displayed; "Access status type" column is still shown in "Packages" accordion
3. Action:   Click "Actions" -> uncheck "Access status type"
   Expected: "Access status type" column disappears from the Packages list

---
Title:          Package name column cannot be hidden while Access status type column is toggled
Type:           Other
Priority:       Medium
Release:        Umbrellaleaf
Test Group:     Extended
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIEH-1524

Preconditions:
- Permissions (for Okapi env.):
  - Permission: eHoldings: Can view providers, packages, titles detail records
  For Eureka environment user with following capabilities/sets is logged in:
  - Settings - Module Eholdings Enabled - View
- Provider "EBSCO" record is opened

Steps:
1. Action:   Click "Actions" in "Packages" accordion
   Expected: "Show columns" section is displayed; "Package name" is not available to uncheck
2. Action:   Check "Access status type", then uncheck all other columns
   Expected: Packages list shows only "Package name" and "Access status type" columns

---

## UIU-3595 — Add an "Anonymize closed loans" option to user records

Scenario Analysis (v1): rules touched — loans.md #8 (anonymization), #17 (manual anonymization partial success); circulation-settings.md #10. Scenarios derived from the 7 story scenarios plus a capability boundary.

---
Title:          Anonymize closed loans radio buttons are displayed in Extended information when user-specific anonymization is allowed
Type:           Functional
Priority:       High
Release:        Umbrellaleaf
Test Group:     Critical Path
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIU-3595, UICIRC-1361

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Users: Can view, edit, and create users
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Users - Edit
- "Allow user specific anonymization settings for closed loans" is selected in Settings > Circulation > Loan anonymization
- Patron user exists
- User is on Users app

Steps:
1. Action:   Search for patron from Preconditions #3 and open user record
   Expected: User details pane is displayed
2. Action:   Expand "Extended information" accordion
   Expected: "Anonymize closed loans" field is displayed with value "According to library policy"
3. Action:   Click "Actions" -> "Edit"
   Expected: Edit user form opens
4. Action:   Expand "Extended information" accordion
   Expected: "Anonymize closed loans" radio button set is displayed with options "According to library policy" (selected), "As early as possible", "Never"
5. Action:   Select "Never" and click "Save & close"
   Expected: User record is saved; "Anonymize closed loans" = "Never" in Extended information

---
Title:          Anonymize closed loans option is hidden when user-specific anonymization is not allowed
Type:           Other
Priority:       Medium
Release:        Umbrellaleaf
Test Group:     Extended
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIU-3595

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Users: Can view, edit, and create users
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Users - Edit
- "Allow user specific anonymization settings for closed loans" is NOT selected in Settings > Circulation > Loan anonymization
- User is on patron record in Users app

Steps:
1. Action:   Expand "Extended information" accordion
   Expected: "Anonymize closed loans" field is not displayed
2. Action:   Click "Actions" -> "Edit" and expand "Extended information"
   Expected: "Anonymize closed loans" radio button set is not displayed

---
Title:          Closed loans of user with Never preference are not anonymized
Type:           Functional
Priority:       High
Release:        Umbrellaleaf
Test Group:     Critical Path
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIU-3595

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Users: Can view, edit, and create users; Check in: All permissions; Check out: All permissions
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Users - Edit
  - Procedural - UI-Checkin - Execute
  - Procedural - UI-Checkout - Execute
- Settings > Circulation > Loan anonymization: "Anonymize closed loans" = "Immediately after loan closes"; user-specific anonymization allowed
- Patron has "Anonymize closed loans" = "Never"
- Item with barcode <barcode> is checked out to the patron

Steps:
1. Action:   Check in item from Preconditions #4 in Check in app
   Expected: Item is checked in; status "Available"
2. Action:   Open patron record > "Loans" > "Closed loans"
   Expected: Loan for item from Preconditions #4 is displayed in Closed loans list and not anonymized

---
Title:          Closed loans of user with As early as possible preference are anonymized after the earliest duration
Type:           Functional
Priority:       High
Release:        Umbrellaleaf
Test Group:     Critical Path
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIU-3595

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Users: Can view, edit, and create users; Check in: All permissions
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Users - Edit
  - Procedural - UI-Checkin - Execute
- Settings > Circulation > Loan anonymization: "Anonymize closed loans" = "Never"; "If the user requests anonymization as early as possible, then anonymize closed loans" = "Immediately after loan closes"
- Patron has "Anonymize closed loans" = "As early as possible"
- Item <barcode> is checked out to the patron

Steps:
1. Action:   Check in item from Preconditions #4
   Expected: Item is checked in
2. Action:   Wait for the scheduled anonymization job and open patron record > "Loans" > "Closed loans"
   Expected: Loan is anonymized and no longer displayed in Closed loans

---

## UIOR-1497 — Add order filter status to Orders app

Scenario Analysis (v1): rules — orders.md search & filter; story scenarios 1–7 plus localization.

---
Title:          Exported and Transmission method filter accordions are displayed around Export date on Order lines pane
Type:           Functional
Priority:       Medium
Release:        Umbrellaleaf
Test Group:     Extended
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIOR-1497

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Orders: Can view Orders and Order lines
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Orders Orders - View
- User is on Orders app

Steps:
1. Action:   Click "Order lines" toggle on "Search & filter" pane
   Expected: "Order lines" toggle is active
2. Action:   Check filter accordions on "Search & filter" pane
   Expected: "Exported" accordion is displayed above "Export date"; "Transmission method" accordion is displayed below "Export date"
3. Action:   Expand "Exported" accordion
   Expected: "Yes" and "No" checkboxes are displayed, both unchecked
4. Action:   Expand "Transmission method" accordion
   Expected: "Email", "FTP", "File download" checkboxes are displayed, all unchecked

---
Title:          Filter order lines by Exported status
Type:           Functional
Priority:       High
Release:        Umbrellaleaf
Test Group:     Critical Path
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIOR-1497

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Orders: Can view Orders and Order lines
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Orders Orders - View
- POL 1 has been exported; POL 2 has not been exported
- User is on Orders app > Order lines

Steps:
1. Action:   Enter "*" in search box and click "Search"
   Expected: Order lines are displayed including POL 1 and POL 2
2. Action:   Check "Yes" in "Exported" accordion
   Expected: Only exported order lines are listed; POL 1 is displayed, POL 2 is not
3. Action:   Uncheck "Yes", check "No"
   Expected: Only not exported order lines are listed; POL 2 is displayed, POL 1 is not
4. Action:   Check both "Yes" and "No"
   Expected: All order lines are listed
5. Action:   Uncheck both
   Expected: All order lines are listed

---
Title:          Filter order lines by Transmission method
Type:           Functional
Priority:       High
Release:        Umbrellaleaf
Test Group:     Critical Path
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIOR-1497

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Orders: Can view Orders and Order lines
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Orders Orders - View
- POLs exported via Email, FTP and File download exist
- User is on Orders app > Order lines with "*" search results

Steps:
1. Action:   Check "Email" in "Transmission method" accordion
   Expected: Only order lines with transmission method Email are listed
2. Action:   Additionally check "FTP"
   Expected: Order lines with Email or FTP are listed
3. Action:   Uncheck all and check "File download"
   Expected: Only order lines with File download are listed

---
Title:          Export date column is displayed and sortable on Order lines pane
Type:           Functional
Priority:       Medium
Release:        Umbrellaleaf
Test Group:     Extended
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIOR-1497

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Orders: Can view Orders and Order lines
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Orders Orders - View
- At least 3 exported POLs with different export dates exist
- User is on Orders app > Order lines

Steps:
1. Action:   Search "*"
   Expected: Results table has "Export date" as the rightmost column
2. Action:   Click "Export date" header
   Expected: Rows sorted by export date ascending
3. Action:   Click "Export date" header again
   Expected: Rows sorted by export date descending

---
Title:          Exported, Transmission method and Export date labels are localized in German
Type:           Other
Priority:       Low
Release:        Umbrellaleaf
Test Group:     Extended
Execution Type: Manual
Dev Team:       <Development Team field of the story>
Labels:         AI
References:     UIOR-1497

Preconditions:
- Permissions (for Okapi env.):
  - Permission: Orders: Can view Orders and Order lines
  For Eureka environment user with following capabilities/sets is logged in:
  - Data - UI-Orders Orders - View
- User locale is set to German (Deutsch)
- User is on Orders app > Order lines

Steps:
1. Action:   Check filter accordions on "Search & filter" pane
   Expected: Accordions "Exportiert" (options "Ja", "Nein") and "Übertragungsmethode" (options "E-Mail", "FTP", "Dateidownload") are displayed
2. Action:   Search "*" and check results table header
   Expected: Rightmost column is "Exportdatum"
