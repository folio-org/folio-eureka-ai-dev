# Golden example — Circulation settings

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Settings form case: new option enabled on create, success toast verbatim, option toggled on edit and the persisted state re-verified (Automatic renewals).

### C1554460 — Settings - Create loan policy with "Automatic renewals" enabled

Source: [C1554460](https://foliotest.testrail.io/index.php?/cases/view/1554460) · Type Functional · Priority Medium · Test Group Critical Path · refs UICIRC-1387,UICIRC-1390,UICIRC-1399

```
Preconditions:
Authorized staff user with "data - UI-Circulation Settings Loan-Policies - manage" capability set is logged in

Steps:
1. Action:   - Go to Settings -> Circulation -> Loan policies
             - Click "New" button on "Loan policies" pane
   Expected: "New loan policy" form appears
2. Action:   Fill the following fields:
             - "Loan policy name" - enter any unique value
             - "Loanable" - enabled (checked)
             - "Loan profile" - rolling
             - "Loan period" - 5 days
             - "Closed library due date management" - Keep the current due date
             - "Renewable" - enabled (checked)
             - "Unlimited renewals" - enabled (checked)
             - "Renew from" - Current due date
   Expected: - Entered and selected values appear in appropriate fields
             - "Automatic renewals" label with unchecked checkbox appears below "Renewal period different from original loan" checkbox
3. Action:   Check "Automatic renewals" checkbox
   Expected: - "Automatic renewals" checkbox is checked
             - "Attempt first renewal" section appears below with “On due date” option selected by default
             - "Attempt additional retries for" section appears underneath radio buttons
4. Action:   Click "Save & close" button
   Expected: - Success toast message "The Loan policy <name> was successfully created." appears
             - Created loan policy details pane appears and contains entered and selected values from previous steps
             - "Renewals" accordion contains the following values:
                - Renewable - Yes
                - Unlimited renewals - Yes
                - Renew from - Current due date
                - Renewal period different from original loan - No
             -
                - Automatic renewals - Yes
                - Attempt first renewal - On due date
                - Attempt additional retries for - 0
5. Action:   - Click "Actions" button on just created loan policy details pane
             - Select "Edit" option
   Expected: - Edit form is displayed
             - "Automatic renewals" checkbox is active (checked)
6. Action:   Uncheck "Automatic renewals" checkbox
   Expected: - "Automatic renewals" checkbox became unchecked
             - "Attempt first renewal" and "Attempt additional retries for" options are not displayed
7. Action:   Click "Save & close" button
   Expected: - Success toast message "The Loan policy <name> was successfully created." appears
             - Edited loan policy details pane appears and does not contain "Automatic renewals" section
8. Action:   - Click "Actions" button on just created loan policy details pane
             - Select "Edit" option
   Expected: - Edit form is displayed
             - "Automatic renewals" checkbox is unchecked
9. Action:   - Check "Automatic renewals" checkbox
             - Populate "Attempt first renewal" with "5" value and "Attempt additional retries for" with "3" value
             - Uncheck "Automatic renewals" checkbox
   Expected: "Automatic renewals" checkbox is unchecked
10. Action:   Check "Automatic renewals" checkbox
   Expected: - "Automatic renewals" checkbox became active
             - "Attempt first renewal" and "Attempt additional retries for" populated with values entered in previous step
11. Action:   Click "Save & close" button
   Expected: - Success toast message "The Loan policy <name> was successfully created." appears
             - Edited loan policy details pane appears and contains "Automatic renewals" section with values entered in previous step
12. Action:   - Click "Actions" button on just created loan policy details pane
             - Select "Edit" option
             - Uncheck "Automatic renewals" checkbox
             - Click "Save & close" button
   Expected: - Success toast message "The Loan policy <name> was successfully created." appears
             - Edited loan policy details pane appears and does not contain "Automatic renewals" section
13. Action:   - Click "Actions" button on just created loan policy details pane
             - Select "Edit" option
             - Check "Automatic renewals" checkbox
   Expected: - "Automatic renewals" checkbox became active
             - "Attempt first renewal" and "Attempt additional retries for" are NOT populated
14. Action:   - Click "Cancel" button
             - Click "Close without saving" button in appeared popup
   Expected: Loan policy details pane appears and does not contain "Automatic renewals" section
```
