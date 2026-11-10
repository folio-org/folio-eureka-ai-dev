# Golden example — Data Export

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Capability-gated settings case: the capability set is part of the title; create/edit flow with exact field values and locked-profile behaviour.

### C1046003 — User with "Settings - UI-Data-Export Settings Lock - Edit" capability set is able to edit locked mapping profile

Source: [C1046003](https://foliotest.testrail.io/index.php?/cases/view/1046003) · Type Other · Priority Medium · Test Group Critical Path · refs MDEXP-894,UIDEXP-414,FAT-25249

```
Preconditions:
1) Authorized user with the following capability sets is logged in:
- UI-Data-Export Settings Lock - settings/edit
2) At least two mapping profiles (not default) are present on the environment as specified below:
- unlocked mapping profile not referenced in job profile
- locked mapping profile referenced in job profile
3) User is on the "Settings" > "Data export" > "Field mapping profiles" page

Steps:
1. Action:   Select existing mapping profile from Preconditions:
             - **unlocked** mapping profile not referenced in job profile
   Expected: - The mapping profile view form is displayed
             - "Lock profile" checkbox is disabled, unchecked
             - "Actions" menu is enable
2. Action:   Click "Actions" menu button
   Expected: Menu is expanded and the following options are displayed:
             - Edit
             - Duplicate
             - Delete
3. Action:   Click on Actions menu => Edit option
   Expected: - Field mapping profile form opens in edit mode
             - "**Lock profile**" checkbox is enabled, unchecked
             - "Save & close" button is disabled
             - "Cancel" button is enabled
             - "X" button is enabled
             NOTE: HTML page title is "Data export settings - <Name of the profile> - FOLIO"
4. Action:   - Check "Lock profile" checkbox
             - Click "Save & close" button
   Expected: - The changes are saved
             - The edit form closes
             - The list of the existing mapping profiles displays with the callout "The field mapping profile <profile name> has been successfully saved"
5. Action:   Verify row with edited mapping profile in "Field mapping profiles" table
   Expected: Appropriate values are populated in the columns for edited mapping profile:
             - "Name" displays mapping profile name
             - "FOLIO record type" displays record type
             - "Format" displays "MARC"
             - "Updated" displays localized date
             - "Updated by" displays user name in format <first name> <last name>
             - "Status" is **Locked**
6. Action:   Click on the row with edited mapping profile
   Expected: - Detailed view of field mapping profile opens
             - The changes in "Name", "Description" and "Transformations" are saved correctly
             - "Lock profile" checkbox is **checked**, disabled
7. Action:   Close Mapping profile view page
             Select existing mapping profile from Preconditions:
             - **locked **mapping profile referenced in job profile
   Expected: - The mapping profile view form is displayed
             - "Lock profile" checkbox is **disabled, checked**
             - "Actions" menu is enabled
8. Action:   Click "Actions" menu button
   Expected: Menu is expanded and the following options are displayed:
             - Edit
             - Duplicate
9. Action:   - Click on Actions menu => Edit option
   Expected: - Field mapping profile form opens in edit mode
             - "**Lock profile**" checkbox is enabled, checked
             - "Save & close" button is disabled
             - "Cancel" button is enabled
             - "X" button is enabled
             NOTE: HTML page title is "Data export settings - <Name of the profile> - FOLIO"
10. Action:   - Uncheck "Lock profile" checkbox
             - Make any other changes on the mapping profile
             - Click "Save & close" button
   Expected: - The changes are saved
             - The edit form closes
             - The list of the existing mapping profiles displays with the callout "The field mapping profile <profile name> has been successfully saved"
11. Action:   Verify row with edited mapping profile in "Field mapping profiles" table
   Expected: Appropriate values are populated in the columns for edited mapping profile:
             - "Name" displays mapping profile name
             - "FOLIO record type" displays record type
             - "Format" displays "MARC"
             - "Updated" displays localized date
             - "Updated by" displays user name in format <first name> <last name>
             - "Status" is **empty**
12. Action:   Click on the row with edited mapping profile
   Expected: - Detailed view of field mapping profile opens
             - The changes in "Name", "Description" and "Transformations" are saved correctly
             - "Lock profile" checkbox is **unchecked**, disabled
```
