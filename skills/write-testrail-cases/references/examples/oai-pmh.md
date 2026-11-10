# Golden example — OAI-PMH

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Mixed API + UI case: Postman requests alternate with browser actions, and record presence in the response is asserted before and after the Inventory edit and the record-source setting change.

### C1347157 — ListRecords: Verify that edited via "Inventory" LINKED_DATA instance is retrieved in response (marc21)

Source: [C1347157](https://foliotest.testrail.io/index.php?/cases/view/1347157) · Type Other · Priority Medium · Test Group Extended · refs MODOAIPMH-600

```
Preconditions:
1) From API-client app: To run OAI-PMH request, please, use edge User
2) From Browser:
Authorized user with the following capability sets:
- UI-Linked-Data - data/manage
- UI-Inventory - data/manage
- UI-Oai-Pmh Settings - settings/edit
3) User has experience of using the FOLIO API. You can see documentation by the link: https://wiki.folio.org/display/FOLIOtips/Working+with+FOLIO+APIs
Base URL User can find: "Settings" => "OAI=PMH" => "GENERAL" => "BASE URL" base URL included to the request is located between "http://" and "/oai", for example: folio.org
4) User has "Postman" app (or any similar API-client, will use to send request to interact with FOLIO's API)
5) Record source is set to **"Source record storage"** on the "Settings" => "OAI-PMH" => "Behavior" => "Record source"
"Suppressed records processing" is set to "Transfer suppressed records with discovery flag value" on the "Settings" => "OAI-PMH" => "Behavior" => "Suppressed records processing"
6) At least one **not suppressed from discovery** Instance with electronic access** populated with source LINKED_DATA **that was updated in the past, not in the current date** is present on the environment
NOTE: For testing on environment where there is no Instance updated in the past but only on current date use UTCdatetime in the requests "from=TZ&until=TZ"
- Date should be in the format: yyyy-mm-dd (for example: 2023-01-24)
- Time should be in the format: hh:mm:ss (for example: 05:35:00)
- Time should be in UTC time zone
- "From"  and "until" define a time period when Instance was not updated
7) User is on the "Inventory" app with opened Instance detailed view from Preconditions 6

Steps:
1. Action:   **From "Postman" app:**
             Send the "GET" request to the endpoint with following parameters:
             {{edge-url}}/oai/records?verb=ListRecords&metadataPrefix=marc21&from=<current date>&until=<current date>&apiKey={{apiKey}}
             - <current date> in the format: yyyy-mm-dd (for example: 2023-01-24)
   Expected: - The request is sent from "Postman" app
             - The successful response is obtained
2. Action:   Verify that obtained response doesn't include Instance with source LINKED_DATA from Preconditions
   Expected: - The response doesn't include Instance with source LINKED_DATA from Preconditions
             NOTE: search for the record in response by Instance UUID
3. Action:   **From the browser tab:**
             - Click "Actions" > "Edit instance"
             - Check "Suppress from discovery" checkbox
             - Click "Save & close" button
   Expected: - Instance detailed view is displayed
             - Instance is marked suppressed from discovery
             NOTE: Instance UUID could be found in the URL after view/<UUID>
4. Action:   **From "Postman" app:**
             Send the "GET" request to the endpoint with following parameters:
             {{edge-url}}/oai/records?verb=ListRecords&metadataPrefix=marc21&from=<current date>&until=<current date>&apiKey={{apiKey}}
             - <current date> in the format: yyyy-mm-dd (for example: 2023-01-24)
   Expected: - SRS record that is associated with the LINKED_DATA Instance is present in response
             - 999 ff field includes subfields "i", "s", "l", "t"
             - subfield $i contains UUID of associated instance record
             - subfield $s contains UUID of associated SRS record
             - subfield $l contains UUID of associated Linked_Data record
             - In 999 field subfield "t" value is 1
             - 856 field includes information about electronic access
             - In 856 field subfield "t" value is 1
5. Action:   **From the browser tab:**
             - Go to "Settings" => "OAI-PMH" => "Behavior" => "Record source"
             - Set record source to "Inventory"
             - Click "Save" button
   Expected: - Record source is set to **"Inventory"** on OAI-PMH settings
6. Action:   **From "Postman" app:**
             Send the "GET" request to the endpoint with following parameters:
             {{edge-url}}/oai/records?verb=ListRecords&metadataPrefix=marc21&from=<current date>&until=<current date>&apiKey={{apiKey}}
             - <current date> in the format: yyyy-mm-dd (for example: 2023-01-24)
   Expected: - SRS record that is associated with the LINKED_DATA Instance is present in response
             - 999 ff field includes subfields "i", "s", "l", "t"
             - subfield $i contains UUID of associated instance record
             - subfield $s contains UUID of associated SRS record
             - subfield $l contains UUID of associated Linked_Data record
             - In 999 field subfield "t" value is 1
             - 856 field includes information about electronic access
             - In 856 field subfield "t" value is 1
7. Action:   **From the browser tab:**
             - Go to "Settings" => "OAI-PMH" => "Behavior" => "Record source"
             - Set record source to "Source record storage and Inventory"
             - Click "Save" button
   Expected: - Record source is set to **"Source record storage and Inventory"** on OAI-PMH settings
8. Action:   **From "Postman" app:**
             Send the "GET" request to the endpoint with following parameters:
             {{edge-url}}/oai/records?verb=ListRecords&metadataPrefix=marc21&from=<current date>&until=<current date>&apiKey={{apiKey}}
             - <current date> in the format: yyyy-mm-dd (for example: 2023-01-24)
   Expected: - SRS record that is associated with the LINKED_DATA Instance is present in response
             - 999 ff field includes subfields "i", "s", "l", "t"
             - subfield $i contains UUID of associated instance record
             - subfield $s contains UUID of associated SRS record
             - subfield $l contains UUID of associated Linked_Data record
             - In 999 field subfield "t" value is 1
             - 856 field includes information about electronic access
             - In 856 field subfield "t" value is 1
```
