# Golden example — eHoldings

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Column chooser persistence: state is re-verified after switching records and returning — the pattern to reuse for any Show columns story (e.g. Provider packages list).

### C1282793 — Package detail record: Data column selection is retained after switching between records and panes

Source: [C1282793](https://foliotest.testrail.io/index.php?/cases/view/1282793) · Type Functional · Priority Medium · Test Group Extended · refs UIEH-1455,UIEH-1488

```
Preconditions:
- Authorized user with following permissions/capabilities
 |  | Permission name for Okapi env. | Capabilities/Sets for Eureka env. (type/table - resource - action)
 | eHoldings: Can view providers, packages, titles detail records | settings - Module Eholdings Enabled - view
 | eHoldings: Can edit providers, packages, titles detail records
 | data - UI-Eholdings Records - edit
- For test you need to find "Package" record (you can use this package "Academic Search Premier" ("19-160").
   - which has more than 100 titles
- User is on the detail view pane of "Package" record from precondition, ex: "Academic Search Premier"

Steps:
1. Action:   Scroll down to the "Titles" accordion
   Expected: The expanded "Titles" accordion contains following:
             - Table with all Titles related to current Package which has following columns:
                - "Status" - Selected or Not selected
                - "Title" - wrapped
                - "Managed coverage"
                - "Custom coverage" - with date ranges displayed in 1 line (if there are many)
                - "Managed embargo period"
                - "Custom embargo period"
                - "Publication type"
                - "Access status type"
                - "Tags"
2. Action:   Click on "Actions" button and Uncheck some options in "Show columns" section of "Actions" menu
   Expected: Only columns selected in the "Show columns" options are displayed in the expanded "Titles" accordion.
3. Action:   Click on any "Title" (aka "Resource") in expanded "Titles" accordion
   Expected: "Package+Title" (aka "Resource") record is opened
4. Action:   Close opened "Package+Title" (aka "Resource") record
   Expected: - User is redirected back to the "Package" record
             - Columns selected in "Show columns" are retained in the "Titles" accordion.
5. Action:   Click on Provider link in "Package information" accordion
   Expected: "Provider" record is opened
6. Action:   Close opened "Provider" record
   Expected: - User is redirected back to the "Package" record
             - Columns selected in "Show columns" are retained in the "Titles" accordion.
7. Action:   Update "Package" record:
             - Click on the "Actions" -> "Edit"
             - Update any field
             - Click on the "Save & close" button
   Expected: - User is redirected back to the "Package" record
             - Columns selected in "Show columns" are retained in the "Titles" accordion.
8. Action:   Update any "Package+Title" (aka "Resource") record:
             - Click on any selected "Title" (aka "Resource") in expanded "Titles" accordion
             - Click on the "Actions" -> "Edit"
             - Update any field
             - Click on the "Save & close" button
             - Close opened "Package+Title" (aka "Resource") record
   Expected: - User is redirected back to the "Package" record
             - Columns selected in "Show columns" are retained in the "Titles" accordion.
9. Action:   Update "Provider" record:
             - Click on Provider link in "Package information" accordion
             - Click on the "Actions" -> "Edit"
             - Update any field
             - Click on the "Save & close" button
             - Close opened Provider record
   Expected: - User is redirected back to the "Package" record
             - Columns selected in "Show columns" are retained in the "Titles" accordion.
```
