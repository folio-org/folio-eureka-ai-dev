# Golden example — Data Import

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Import edge case: a MARC bib with empty 008/00-05 is imported with the default job profile; the job log status, the created Instance, View source and the subsequent MARC edit are each verified.

### C1332477 — Import MARC bib record with empty positions 00-05 of 008 MARC field

Source: [C1332477](https://foliotest.testrail.io/index.php?/cases/view/1332477) · Type Functional · Priority Medium · Test Group Extended · refs MODQM-515,FAT-27419

```
Preconditions:
- Authorized user with following capabilities
   - Data-UI-Data-Import-Manage
   - Data-UI-Inventory-Manage
   - data - UI-Quick-Marc Quick-Marc-Editor - manage
- User have .mrc file with record which contains blanks (whitespaces) in 00-05 positions of 008 field

Steps:
1. Action:   Go to the "Data import" app-> Click on the "or choose files" button -> Select file from the precondition -> click on the "Open" button
   Expected: The selected file is loaded and the user is redirected to the "Job profiles" page
2. Action:   Select the "Default - Create instance and SRS MARC Bib" job profile (created by system) -> Click on the "Actions" button-> Select "Run" > Click on the "Run" button at the displayed modal
   Expected: Once the import is confirmed, the user is redirected to the "Data Import" landing page
3. Action:   After the import is completed, click on the file name at the top of the log list
   Expected: - Job has status "Completed" and no errors
             - The user is redirected to the "Log details" page
             - Instance and SRS MARC have status "Created"
4. Action:   Click on the "Created" hotlink for the "Instance" column
   Expected: The user is redirected to the "Inventory" app and displays the Instance details
5. Action:   Click on "Actions" - "View source"
   Expected: - View source of the underlying MARC record is opened
             - 008 field contains blanks in 00-05 positions:
              | 008 |       m20172019nyua     6    000 1 eng d
6. Action:   Click on "Actions" - "Edit MARC bibliographic record"
   Expected: - Edit MARC bib record is opened
             - There are no invalid values in "008" field
             - Following values display in "008" field:
                - DtSt = m
                - Date 1 = 2017
                - Date 2 = 2019
                - Ctry = nyu
                - Ills = a
7. Action:   Update any MARC field, ex.: 245
   Expected: - Some field is updated
             - "Save & close" button is enabled
8. Action:   Click on "Save & close" button
   Expected: - Record is saved
             - User is on detail view pane of Instance record
9. Action:   Click on "Actions" - "View source"
   Expected: - View source of the underlying MARC record is opened
             - 008 field contains today day value in 00-05 positions:
              | 008 | 260507m20172019nyua     6    000 1 eng d
10. Action:   Click on "Actions" - "Edit MARC bibliographic record"
   Expected: - Edit MARC bib record is opened
             - There are no invalid values in "008" field
             - Following values display in "008" field:
                - DtSt = m
                - Date 1 = 2017
                - Date 2 = 2019
                - Ctry = nyu
                - Ills = a
```
