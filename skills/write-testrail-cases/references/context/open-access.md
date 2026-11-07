---
area: open-access
generated_on: 2026-11-07
generator_version: manual (build-app-context method)
jira_status: ok
---

# FOLIO Open Access — Business Logic Context

> Built: 2026-11-07 · Release: R2 2026 Umbrellaleaf (ui-oa v3.2.0 at HEAD) · Builder: build-app-context method, manual
> Sources: TestRail suite 21 section 115129 "Open Access" (Journals 115130, People 115131, Requests 115132, Publication charges 117721, Checklists 117722 — 12 cases, all created 2026-06, Smoke group, titles only); GitHub folio-org/ui-oa (translations/ui-oa/en.json, package.json, README), folio-org/mod-oa; Jira UIOA Done issues since 2025-11.
> Coverage is thin: 12 smoke cases. Treat most strings as [source] and verify behaviour in the env before strict assertions.

## What is Open Access

The **Open access** app (ui-oa + mod-oa, ERM family) manages OA **publication requests** and related records: **Parties/People** (authors, corresponding authors), **Journals** (with OA status), **Publication charges** (APCs, with discounts, tax, invoicing through the Invoices app), **Correspondence**, **Checklists**, and publication statuses. Settings hold pick lists, checklist item definitions and defaults (e.g. tax rate).

## UI structure (from en.json + case titles)

- Main tabs/lists: Requests (publication requests), Parties/People, Journals.
- Publication request: Status, Status date, Status note, OA status, Publication status list ("Add publication status"), Journal, Parties, Charges, Correspondence (statuses Awaiting Reply / Response Needed / Closed), Checklist.
- Charge: Status, discount type, tax; "Create an invoice for a charge" links to Invoices (invoice line status Open).
- Search & filter: Charge status, Correspondence status, etc. (UIOA-260 fixed wrong filter values).

## Permissions

| Okapi permission (package.json) | Eureka capability set |
|---|---|
| Open Access Requests: Search & view all / Edit all / Manage all | not confirmed (verify in env) |
| Settings (Open Access): Manage all Open Access settings | not confirmed (verify in env) |

## Existing cases (all Smoke, created 2026-06)

- Journals: C1348712 Create Journal; C1348713 Search or filter for journals; C1348715 Display journal
- People: C1348717 Create Person; C1348718 Search or filter for people; C1348719 Display person
- Requests: C1373188 Create an article request; C1373195 Request accordion display; C1373196 Search or filter for a request
- Publication charges: C1373197 Add a publication charge; C1373198 Create an invoice for a charge
- Checklists: C1373199 Complete a checklist item for a request

## Key Business Rules for Test Cases

1. Creating a publication request shows the callout "Publication request {requestNumber} successfully created" [source].
2. Party / Journal creation callouts: "Party created: {name}", "Party updated: {name}", "Journal created: {title}" [source].
3. Adding a person to a request searches by family/given names, emails and ORCID (UIOA-252). (jira)
4. Charges: discount type must be submitted on update (UIOA-251); decimals with trailing zero are accepted in number fields (UIOA-258); default tax rate populated on first visit (UIOA-243). (jira — regression candidates)
5. Creating an invoice for a charge must produce an invoice/invoice line in the Invoices app — verify there, not only in OA (cross-app effect).

## Known Gaps / Items to Verify

- [ ] Request/charge status value lists — configured pick lists, env-specific.
- [ ] Eureka capability set names.
- [ ] No negative or capability-boundary cases exist yet.

---

## Exact UI Texts

> From `folio-org/ui-oa` `translations/ui-oa/en.json` at HEAD (2026-11-07). `{x}` are placeholders; `<b>`/`<strong>` render bold. Use verbatim.

### Toast Messages

| Key | Text | Source |
|---|---|---|
| `refdata.deleteRefdataValue.confirmMessage` | <strong>{name}</strong> will be deleted. | [source] |
| `refdata.deleteRefdataValue.errorMessage` | <strong>Error: {label}</strong> was not deleted. {error} | [source] |
| `settings.checklistItemDefinitions.deleteDefinition.confirmMessage` | Checklist item <strong>{label}</strong> will be <strong>deleted</strong> | [source] |
| `party.uniqueOrcIdError` | <strong>Error:</strong> Party was not saved. OrcId must be unique. A Party with OrcId {duplicateElement} already exists | [source] |
| `party.uniqueMainError` | <strong>Error:</strong> Party was not saved. Main email must be unique. A Party with the main email {duplicateElement} already exists | [source] |
| `party.creationSuccessCallout` | <strong>Party created:</strong> {createdParty} | [source] |
| `party.updatedSuccessCallout` | <strong>Party updated:</strong> {updatedParty} | [source] |
| `journal.creationError` | <strong>Error:</strong> Unable to create a new journal, please check the details and try again | [source] |
| `journal.creationSuccess` | <strong>Journal created:</strong> {journalTitle} | [source] |
| `publicationRequest.success.callout` | Publication request {requestNumber} successfully created | [source] |
| `charge.invoiceLine.newInvoiceLineConfirmMessage` | Select 'Submit' to go ahead. | [source] |
