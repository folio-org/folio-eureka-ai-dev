---
area: inn-reach
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO INN-Reach Integration — Business Logic Context

> Built: 2026-11-07 · Release: R2 2026 Umbrellaleaf (ui-inn-reach v6.2.0 at HEAD) · Builder: build-app-context method, manual
> Sources: TestRail suite 21 section 16515 "INN-Reach Integration" and 13 subsections (≈150 cases; full content read for Transactions 17499 and Transactions search 17463, titles for the rest); GitHub folio-org/ui-inn-reach (translations/ui-inn-reach/en.json, package.json), folio-org/mod-inn-reach; Jira UIINREACH / MODINREACH Done issues since 2025-11.
> [confirmed] = en.json + TestRail agree · [source] = en.json only · [cases] = TestRail only.

## What is INN-Reach

INN-Reach is III's resource-sharing network (D2IR protocol). FOLIO acts as a **local server** connected to one or more **central servers**: it contributes bib/item records, lends its items to other agencies (owning site), and borrows items for its patrons (borrowing site). Staff work in the **INN-Reach** app (transactions + check-out to borrowing site) and in **Settings > INN-Reach** (connection, contribution, circulation mappings). Most state changes are driven by D2IR messages from the central server, so many cases need a sandbox central server or pre-created transactions (see FOLIJET wiki guides linked in case preconditions).

## Key Terms

| Term | Meaning |
|---|---|
| Central server | INN-Reach hub; configured in Settings > INN-Reach > Central server configuration (code, address, key/secret, local server code, local agency, FOLIO libraries, borrowed item loan type) |
| Local server / agency | FOLIO's identity on the central server; agencies map to FOLIO libraries/locations |
| Contribution | Sending FOLIO instances/items to the central catalog — initial (bulk, "Manage contribution") and ongoing (on create/update/move/delete) |
| Transaction | Record of one resource-sharing request. Types: **Item** (FOLIO owns the item, a remote patron requested it), **Patron** (FOLIO patron requests a remote item), **Local** (local patron, local item via central catalog) |
| ITEM_HOLD / PATRON_HOLD / LOCAL_HOLD | Initial statuses of Item / Patron / Local transactions |

## Transaction lifecycle (statuses seen in cases)

- **Item (owning site):** ITEM_HOLD → (Check out to borrowing site) ITEM_SHIPPED → ITEM_IN_TRANSIT / RECALL → FINAL_CHECKIN; cancel allowed in ITEM_HOLD and TRANSFER.
- **Patron (borrowing site):** PATRON_HOLD → ITEM_SHIPPED → (Receive item) ITEM_RECEIVED, or RECEIVE_UNANNOUNCED (Receive unshipped item, allowed in PATRON_HOLD / TRANSFER) → (Check out to patron) loan → return → FINAL_CHECKIN; Cancel hold allowed in PATRON_HOLD, ITEM_RECEIVED, RECEIVE_UNANNOUNCED.
- **Local:** LOCAL_HOLD → Check out to local patron / Transfer hold to another item (LOCAL_HOLD or TRANSFER only); RETURN_UNCIRCULATED when checked in after the local request is cancelled.
- RECALL: FINAL_CHECKIN must be handled when the loaned item is checked in, and IN_TRANSIT messages honored, even in RECALL (MODINREACH-575/576; C1385304, C1385310).
- Cancelling the FOLIO request cancels the INN-Reach transaction and vice versa (MODINREACH-562/563); CANCEL_REQUEST from the owning site sends a request-cancellation notice before temporary records are cleaned up (MODINREACH-574; C1395178).

## UI structure

- **INN-Reach app** — "Select activity" dropdown at the top of Search & filter: **INN-Reach transactions** | **Check out to borrowing site**.
  - Transactions list columns: Transaction time, Transaction type, Item title (Agency code), Patron name (Agency code), Transaction status (INN-Reach). Title/Patron columns are sortable since R21 (C1385302).
  - Search by: Item barcode, Patron barcode, Item ID, Item title, Patron ID, Patron name, Tracking ID. Filters: Transaction type, Transaction status, Central server, Patron agency, Item agency, INN-Reach patron type, INN-Reach item type.
  - Transaction detail (third pane): Transaction summary, Patron information, Item information accordions; Actions menu depends on type + status (Receive item, Receive unshipped item, Check out to patron, Cancel hold, Final check-in, Transfer hold to another item, Check out to local patron, Recall item, Return item, Check out to borrowing site).
  - Pane Actions: CSV reports — Owning site overdue report, Requested too long report, Returned too long report, Owning site paged too long report, In-transit too long report (each opens a modal with a "Minimum days …" field).
  - Check out to borrowing site: barcode entry → loan row with "..." menu: Loan detail, Change due date, INN-Reach transaction detail.
- **Settings > INN-Reach** — General: Central server configuration, INN-Reach locations; Record contribution: Contribution criteria, FOLIO to INN-Reach locations, Circulation status mapping (contribution options), Material to item type mapping, Bib transformation options, Manage contribution (Current contribution / history); Circulation mappings: Agency to FOLIO location, Central item type, Central patron type, FOLIO circulation user for INN-Reach patron type, Patron agency, INN-Reach recall user, Visible patron ID, INN-Reach paging slip templates, Pickup locations.
- All settings forms use the standard unsaved-changes modal: "Are you sure?" / "There are unsaved changes" / "Keep editing" / "Close without saving" [confirmed].

## Permissions

| Okapi permission (package.json) | Eureka capability set |
|---|---|
| INN-Reach App: All permissions | `data - UI-Inn-Reach App - manage` [cases, C1543961] |
| Settings (inn-reach): All INN-Reach settings: Read-only / Read, edit / CRUD | settings-type capability sets — names not confirmed in cases (verify) |

Most transaction cases also need Check out, Inventory view and Users loans view capabilities (preconditions of C353659/C353939).

## Key Business Rules for Test Cases

1. Every transaction action is enabled only for specific type+status combinations; each action has a negative case asserting it is inactive in other statuses (C350948, C350953, C350956, C350961, C353620, C353591). (cases)
2. Receiving a shipped item requires the item to have a barcode; an already received item cannot be received again (C353221, C350968, C353525). (cases)
3. Receive unshipped item asks for a barcode; if it already exists on another FOLIO item the barcode is augmented and the toast "The barcode associated with the transaction has been updated" appears (C350910). (cases + source)
4. Final check-in is allowed in ITEM_RECEIVED, RECEIVE_UNANNOUNCED and ITEM_IN_TRANSIT (with open loan); repeating it is blocked (C353568–C353615). (cases)
5. Check out to borrowing site on an ITEM_HOLD item creates a FOLIO loan, sets the transaction to ITEM_SHIPPED and the item to Checked out (C357006). (cases)
6. Change due date from the borrowing-site loan menu behaves like Users > Change due date, incl. "New due date is in the past" warning and loan history action "Due date changed" (C353953–C353970). (cases)
7. Contribution criteria: excluded locations and three statistical-code fields (contribute but suppress / exclude / system-owned); a code chosen in one field is not selectable in another (C345363). (cases)
8. Material to item type mapping and FOLIO to INN-Reach locations require a mapping for every row before Save is enabled (C345364, C345365). (cases)
9. Bib transformation: "Strip fields and subfields" can be saved without "Modify MARC 001 field for contributed records" (C350720). (cases)
10. Central server secrets are obfuscated after save; generating a new local key pair preserves the local server key (C350755, UIINREACH-272). (cases + jira)
11. Ongoing contribution: item create/update/delete, bulk edit, moving holdings/items between instances must be reflected in the central catalog (de-/re-contribute on move) (C503082–C506653, MODINREACH-512). (cases + jira)
12. Pickup locations: with local pickup disabled, the request uses the patron's default pickup service point; without a default SP no request is generated (C357039, C357046, C357048). (cases)
13. Paging slip templates: per central server, token list, preview, print, images can be saved (C356767–C1538597, MODINREACH-518). (cases + jira)
14. Owning site overdue report CSV columns: INN-Reach Patron ID, INN-Reach Patron name, Item's Effective Location, Item call number, Item Barcode, Item Title, Patron Agency, Loan Due Date; due date follows loan renewals/changes (C1543961, UIINREACH-289). (cases + source)

## Known Gaps / Items to Verify

- [ ] Eureka capability set names for the settings permissions — not present in any case read.
- [ ] Generic success toasts in settings cases say only "Successful toast message appears" — use the exact texts from the table below.
- [ ] Many old cases have Test Group 4/5/7 (Obsolete/Draft/Edge) — do not copy their metadata.

---

## Exact UI Texts

> From `folio-org/ui-inn-reach` `translations/ui-inn-reach/en.json` at HEAD (2026-11-07). `{x}` are placeholders; `<b>`/`<strong>` render bold. Use verbatim.

### Toast Messages

| Key | Text | Source |
|---|---|---|
| `validate.required` | Required | [source] |
| `modal.heading.areYouSure` | Are you sure? | [source] |
| `modal.message.unsavedChanges` | There are unsaved changes | [source] |
| `modal.confirmLabel.keepEditing` | Keep editing | [source] |
| `modal.cancelLabel.closeWithoutSaving` | Close without saving | [source] |
| `settings.central-server-configuration.callout.connectionProblem.get` | Unable to get data due to a module error. Please try again. If a problem persists please contact your system administrator | [source] |
| `settings.central-server-configuration.callout.deleted` | Central server configuration was successfully deleted | [source] |
| `settings.central-server-configuration.callout.failedToDelete.delete` | Failed to delete a central server configuration | [source] |
| `settings.central-server-configuration.callout.connectionProblem.delete` | Unable to delete due to a module error. Please try again. If a problem persists please contact your system administrator | [source] |
| `settings.central-server-configuration.callout.connectionProblem.post` | Unable to create data due to a module error. Please try again. If a problem persists please contact your system administrator | [source] |
| `settings.central-server-configuration.callout.connectionProblem.put` | Unable to updated data due to a module error. Please try again. If a problem persists please contact your system administrator | [source] |
| `settings.central-server-configuration.callout.invalidData` | Invalid central server data | [source] |
| `settings.central-server-configuration.callout.notUnique` | Some of the values entered must be unique | [source] |
| `settings.central-server-configuration.create.success` | Central Server configuration created successfully | [source] |
| `settings.central-server-configuration.update.success` | Central Server configuration updated successfully | [source] |
| `settings.central-server-configuration.edit.modal-heading.updateLocalServerKeyConfirmation` | Update Local Server Key Confirmation | [source] |
| `settings.central-server-configuration.edit.modal-message.updateLocalServerKeypair` | You have updated the Local Server Key/Secret pair. INN-Reach circulation functions will be interrupted until this information is updated by the Central Server administrator. Click “Confirm” to save your changes and download a JSON file with the new key and secret values. | [source] |
| `settings.central-server-configuration.edit.modal-button.confirm` | Confirm | [source] |
| `settings.confirmDeleteModal.central-server-configuration.heading` | Confirm deletion of central server configuration | [source] |
| `settings.confirmDeleteModal.central-server-configuration.message` | Central server configuration {name} will be removed. | [confirmed] |
| `settings.confirmDeleteModal.central-server-configuration.confirm` | Delete | [source] |
| `settings.confirmDeleteModal.central-server-configuration.cancel` | Cancel | [source] |
| `settings.contribution-criteria.create.success` | Contribution Criteria settings created successfully | [source] |
| `settings.contribution-criteria.update.success` | Contribution Criteria settings updated successfully | [source] |
| `settings.folio-to-inn-reach-locations.create-edit.create.success` | FOLIO to INN-Reach locations settings created successfully | [source] |
| `settings.folio-to-inn-reach-locations.create-edit.update.success` | FOLIO to INN-Reach locations settings updated successfully | [source] |
| `settings.contribution-options.create.success` | Circulation status mapping settings created successfully | [source] |
| `settings.contribution-options.update.success` | Circulation status mapping settings updated successfully | [source] |
| `settings.material-type-mapping.update.success` | Material type mappings updated successfully | [source] |
| `settings.agency-to-folio-locations.callout.connection-problem.put` | There was a problem and your update was not saved: {message}, status code {code} | [source] |
| `settings.agency-to-folio-locations.create.success` | The INN-Reach Agency to FOLIO Location Mapping for {name} has been created successfully | [source] |
| `settings.agency-to-folio-locations.update.success` | The INN-Reach Agency to FOLIO Location Mapping for {name} has been updated successfully | [source] |
| `settings.bib-transformation.create.success` | Bib transformation options created successfully | [source] |
| `settings.bib-transformation.update.success` | Bib transformation options updated successfully | [source] |
| `settings.bib-transformation.callout.connection-problem.post` | There was a problem and your creation was not saved: {message}, status code {code} | [source] |
| `settings.manage-contribution.initaiate.failed` | Initiate contribution failed | [source] |
| `settings.manage-contribution.initaiate.success` | Contribution successfully initiated | [source] |
| `settings.manage-contribution.cancel.failed` | Cancel contribution failed | [source] |
| `settings.manage-contribution.cancel.success` | Contribution canceled successfully | [source] |
| `settings.manage-contribution.item-mapping-type-status.invalid` | Invalid | [source] |
| `settings.manage-contribution.label.error` | Error | [source] |
| `settings.central-item-type.create.success` | Central item type settings created successfully | [source] |
| `settings.central-item-type.update.success` | Central item type settings updated successfully | [source] |
| `settings.central-patron-type.create.success` | Central patron type settings created successfully | [source] |
| `settings.central-patron-type.update.success` | Central patron type settings updated successfully | [source] |
| `settings.patron-agency.create.success` | Patron agency settings created successfully | [source] |
| `settings.patron-agency.update.success` | Patron agency settings updated successfully | [source] |
| `settings.inn-reach-recall-user.create.success` | INN-Reach recall user settings created successfully | [source] |
| `settings.inn-reach-recall-user.update.success` | INN-Reach recall user settings updated successfully | [source] |
| `settings.visible-patron-id.create.success` | Visible patron id settings created successfully | [source] |
| `settings.visible-patron-id.update.success` | Visible patron id settings updated successfully | [source] |
| `settings.paging-slip-template.preview-modal-header` | Preview of INN-Reach Paging Slip | [source] |
| `settings.paging-slip-template.create.success` | INN-Reach paging slip template settings created successfully | [source] |
| `settings.paging-slip-template.update.success` | INN-Reach paging slip template settings updated successfully | [source] |
| `settings.pickup-locations.update.success` | Local pickup locations updated successfully | [source] |
| `shipped-items.modal.no-transaction.heading` | No matching INN-Reach transaction found for this item | [source] |
| `shipped-items.modal.barcode-augmented.heading` | The barcode for this item already exists in FOLIO | [confirmed] |
| `shipped-items.modal.hold.heading` | Awaiting pickup for a request | [confirmed] |
| `shipped-items.modal.hold.comment` | <strong>Patron comments:</strong> {comment} | [source] |
| `shipped-items.modal.hold.message` | Place <strong>{title} ({materialType})</strong> (Barcode: {barcode}) on Hold Shelf at <strong>{pickupServicePoint}</strong> for request. | [source] |
| `shipped-items.modal.transit.heading` | In transit | [confirmed] |
| `shipped-items.modal.transit.message` | Route <strong>{title} ({materialType})</strong> (Barcode: {barcode}) to <strong>{servicePoint}</strong>. | [source] |
| `shipped-items.modal.message.no-transaction` | This item may not have been checked out by the owning site. Please locate the transaction for this item using the search "INN-Reach transactions" function on the landing page and perform a "Receive unshipped item" action. | [source] |
| `shipped-items.modal.message.barcode-augmented` | The agency code for this item has been appended to the barcode. You will need to use this updated barcode to perform circulation actions on this transaction | [confirmed] |
| `shipped-items.modal.button.close` | Close | [source] |
| `shipped-items.callout.connection-problem.put.receive-shipped-item` | There was a problem receiving the item | [confirmed] |
| `check-out-borrowing-site.modal.message` | No INN-Reach transaction could be found for this item. | [source] |
| `check-out-borrowing-site.callout.connection-problem.post.check-out-borrowing-site` | There was a problem checking out the item | [source] |
| `check-out-borrowing-site.callout.success.post.check-out-borrowing-site` | Item has been successfully checked out | [confirmed] |
| `unshipped-item.modal.title` | Receive unshipped item | [confirmed] |
| `unshipped-item.callout.connection-problem.post.receive-unshipped-item` | There was an error updating the barcode for the transaction | [confirmed] |
| `unshipped-item.callout.success.post.receive-unshipped-item` | The barcode associated with the transaction has been updated | [confirmed] |
| `receive-item.callout.success.post.receive-item` | Item has been successfully received | [confirmed] |
| `recall-item.callout.connection-problem.post.recall-item` | There was a problem recalling the item | [source] |
| `recall-item.callout.success.post.recall-item` | Item has been successfully recalled | [source] |
| `reports.callout.export-in-progress` | Export in progress | [source] |
| `reports.callout.no-items-found` | No items found. | [source] |
| `reports.modal.title.owning-site-overdue-report` | Owning site overdue report | [source] |
| `reports.modal.title.requested-too-long-report` | Requested too long report | [confirmed] |
| `reports.modal.title.returned-too-long-report` | Returned too long report | [source] |
| `reports.modal.title.paged-too-long-report` | Owning site paged too long report | [source] |
| `reports.modal.title.in-transit-too-long-report` | In-transit too long report | [source] |
| `reports.modal.field.minimum-days-overdue` | Minimum days overdue | [source] |
| `reports.modal.field.minimum-days-requested` | Minimum days requested | [confirmed] |
| `reports.modal.field.minimum-days-returned` | Minimum days returned | [source] |
| `reports.modal.field.minimum-days-paged` | Minimum days paged | [source] |
| `reports.modal.field.minimum-days-shipped` | Minimum days shipped | [source] |
| `reports.modal.button.save-and-close` | Save & close | [source] |
| `loan.callout.connection-problem.get.loan` | There was a problem loading the loan | [source] |
| `cancel-hold.callout.connection-problem.get.cancellation-reasons` | Could not retrieve cancellation reasons! | [source] |
| `cancel-hold.callout.connection-problem.post.cancel-hold` | There was a problem canceling the item | [confirmed] |
| `cancel-hold.callout.success.post.cancel-hold` | Item has been successfully canceled | [confirmed] |
| `return-patron-hold-item.callout.success.post.return-patron-hold-item` | Item has been successfully returned | [source] |
| `return-patron-hold-item.callout.connection-problem.post.return-patron-hold-item` | There was a problem returning the item | [source] |
| `final-check-in-item-hold.callout.success.post.final-check-in-item-hold` | Item has been successfully checked in | [confirmed] |
| `final-check-in-item-hold.callout.connection-problem.post.final-check-in-item-hold` | There was a problem checking in the item | [source] |
| `transfer-hold.modal.label` | Select item | [source] |
| `transfer-hold.modal.title` | Other items in {title} | [source] |
| `transfer-hold.modal.result-count` | {count, number} {count, plural, one {Record found} other {Records found}} | [source] |
| `transfer-hold.modal.column.barcode` | Barcode | [source] |
| `transfer-hold.modal.column.item-status` | Item status | [confirmed] |
| `transfer-hold.modal.column.request-queue` | Request queue | [source] |
| `transfer-hold.modal.column.location` | Location | [source] |
| `transfer-hold.modal.column.material-type` | Material type | [confirmed] |
| `transfer-hold.modal.column.loan-type` | Loan type | [confirmed] |
| `transfer-hold.modal.list-of-items.notFound` | No items found | [source] |
| `transfer-hold.callout.success.post.transfer-hold` | Item has been successfully transferred | [source] |
| `transfer-hold.callout.connection-problem.post.transfer-hold` | There was a problem transferring the item | [source] |
| `remove-hold.callout.success.post.remove-hold` | Hold has been successfully removed | [confirmed] |
| `remove-hold.callout.connection-problem.post.remove-hold` | There was a problem removing the hold | [source] |
| `paging-slips.callout.connection-problem.get.pagingSlip` | There was a problem loading the paging slips | [source] |
| `paging-slips-template.callout.connection-problem.get.pagingSlipTemplate` | There was a problem loading the paging slip templates | [source] |
