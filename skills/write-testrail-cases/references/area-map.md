# Area Detection and Context Files

Context files live in `references/context/`. Determine the area from (in priority order): **the apps and entities actually described in the story text**, the Development Team field, and only then the Jira project prefix as a hint. **If the story content contradicts the prefix mapping, trust the story content.** Confirm your detection in one line ("Story describes <X> — loading <file> context") rather than asking, unless detection is ambiguous — then ask.

**The story itself is the source of truth.** If the user's instructions contradict the story (e.g. "this is not an ECS story" while the story has an `ecs` label, mentions tenants/affiliations, or lives in a consortia module), do not silently follow either side — flag the conflict in one line and ask which to trust before generating. The same applies to ECS Enabled: derive it from the story's labels and text, not from assumptions.

| Area | Context file | Jira prefixes / keywords |
|---|---|---|
| Agreements | `references/context/agreements.md` | ERM, UIAG; "agreement", "agreement line", "SAS" |
| Bulk Edit | `references/context/bulk-edit.md` | UIBULKED, MODBULKOPS; "bulk edit", "identifier", "in-app", "commit changes", "preview of records matched", "errors accordion", "reason for error", "bulk edit profile", "query builder", "matched records", "suppress from discovery" |
| Check In | `references/context/check-in.md` | UICHKIN, CIRC; "check in", "return", "backdate" |
| Check Out | `references/context/check-out.md` | UICHKOUT, CIRC; "check out", "loan", "patron block" |
| Orders | `references/context/orders.md` | UIOR, MODORDERS; "purchase order", "POL", "PO line", "encumbrance", "fund distribution", "order template", "open order", "unopen", "reopen", "claiming", "donor information", "bindery active", "routing list", "acquisitions unit" |
| Invoices | `references/context/invoices.md` | UINV, MODINVOICE, MODINVOSTO; "invoice", "invoice line", "voucher", "approve invoice", "pay invoice", "cancel invoice", "pending payment", "lock total", "release encumbrance", "batch group", "adjustment", "pro rate", "export to accounting", "vendor invoice number", "approve and pay in one click", "update order status", "duplicate invoice" |
| Receiving | `references/context/receiving.md` | UIREC; "piece", "receive", "receiving title" |
| Finance | `references/context/finance.md` | UIF, MODFIN; "fund", "budget", "ledger", "fiscal year", "allocation", "encumbrance", "transfer", "rollover", "expense class", "acquisition unit" |
| Inventory | `references/context/inventory.md` | UIIN, MODINV; "instance", "holdings", "item" |
| Inventory Browse | `references/context/inventory-browse.md` | UIIN, MSEARCH; "browse", "call number browse", "subject browse", "contributor browse", "classification browse", "browse option", "Number of titles", "would be here" |
| Requests | `references/context/requests.md` | UIREQ; "request", "hold", "page", "recall", "pickup" |
| Mediated Requests | `references/context/mediated-requests.md` | UIREQMED, MODREQMED; "mediated request", "secure tenant", "secure request", "interim service point" |
| Users | `references/context/users.md` | UIU, MODUSERS; "patron", "user record", "custom fields", "proxy", "service points", "profile picture" |
| Fees/Fines | `references/context/fees-fines.md` | UIU, MODFEE, MODFEESFINES; "fee", "fine", "fee/fine", "charge", "pay", "waive", "refund", "transfer account", "manual charge", "overdue fine", "lost item fee", "fee/fine owner", "payment method", "bursar" |
| Loans | `references/context/loans.md` | UIU, CIRC; "loan", "loan details", "renew", "change due date", "declare lost", "declared lost", "claim returned", "claimed returned", "anonymization", "loan comments" |
| Organizations | `references/context/organizations.md` | UIORG, MODORGS; "organization", "vendor", "vendor record", "interface", "integration", "EDI", "account number", "accounting code", "contact people", "donor", "banking information" |
| Circulation Settings | `references/context/circulation-settings.md` | UICIRC, CIRCSET; "loan policy", "request policy", "overdue fine policy", "lost item fee policy", "circulation rules", "fixed due date schedule", "staff slips", "loan anonymization", "title level request", "TLR", "cancellation reasons", "closed library due date" |
| Patron Notices | `references/context/patron-notices.md` | UICIRC; "patron notice", "notice template", "notice policy", "triggering event", "loan notice", "request notice", "fee/fine notice", "notice token" |
| Circulation Log | `references/context/circulation-log.md` | UICIRCLOG, MODAUD; "circulation log", "circ log", "circ action", "log event", "logged" |
| Course Reserves | `references/context/course-reserves.md` | UICR, MODCOURSE; "course", "course reserve", "reserve item", "instructor", "crosslist", "cross-listed", "registrar id" |
| Data Import | `references/context/data-import.md` | UIDATIMP, MODDATAIMP, MODDICORE, MODSOURMAN, MODSOURCE, MODELINKS; "import", "job profile", "match profile", "action profile", "field mapping profile", "data import", "MARC import", "EDIFACT import", "LDR 05", "MARC Holdings", "file extension" |
| Data Export | `references/context/data-export.md` | UIDEXP, MDEXP; "export", "mapping profile", ".mrc" |
| MARC Authority | `references/context/marc-authority.md` | UIMARCAUTH, MODELINKS; "authority", "quickMARC" |
| MARC Bib (quickMARC) | `references/context/marc-bib-quickmarc.md` | UIQM, MODSOURCE; "quickMARC", "MARC bib", "MARC bibliographic", "LDR", "leader", "008 field", "derive", "controlled field", "linking authority" |
| MARC Holdings (quickMARC) | `references/context/marc-holdings.md` | UIQM, MODQM; "MARC holdings", "MARC holdings record", "852", "004", "Add MARC holdings record", "Edit in quickMARC" on a holdings record |
| eHoldings | `references/context/eholdings.md` | UIEH; "package", "title", "provider", "KB", "EBSCO" |
| Licenses | `references/context/licenses.md` | UILIC, MODLIC, ERM; "license", "amendment", "term", "core document", "supplementary document" |
| Lists | `references/context/lists.md` | UILISTS, MODLISTS, MODFQM; "list", "FQM", "query" |
| OAI-PMH | `references/context/oai-pmh.md` | MODOAIPMH; "harvest", "OAI" |
| Consortium Manager | `references/context/consortium-manager.md` | UICONSET (ui-consortia-settings), MODCON; "consortium", "ECS", "affiliation", "shared setting", "central tenant", "member tenant", "select members", "confirm share to all", "confirm member libraries", "authorization roles", "authorization policies", "data import logs", "data export logs" |
| INN-Reach | `references/context/inn-reach.md` | UIINREACH, MODINREACH; "INN-Reach", "central server", "D2IR", "contribution", "ITEM_HOLD", "PATRON_HOLD", "LOCAL_HOLD", "borrowing site", "owning site", "agency", "paging slip", "final check-in", "receive unshipped item" |
| Open Access | `references/context/open-access.md` | UIOA, MODOA; "open access", "OA", "publication request", "publication charge", "APC", "journal", "party", "correspondence", "checklist" |
| Serials Management | `references/context/serials-management.md` | UISER, MODSER; "serial", "publication pattern", "pattern template", "predicted piece", "piece set", "generate receiving pieces", "enumeration", "chronology", "omission", "combination" |
| Claiming | `references/context/claiming.md` | UICLAIM; "claim", "claiming", "send claim", "delay claim", "mark unreceivable", "late piece", "claim integration" |
| Export Manager | `references/context/export-manager.md` | UIEXPMGR, MODEXPS, MODEXPW; "export manager", "export job", "EDIFACT", ".edi", "resend", "rerun", "integration scheduling", "job deletion interval" |
| Linked Data Editor (Marigold) | `references/context/linked-data.md` | UILD, MODLD; "Marigold", "linked data", "LDE", "BIBFRAME", "Work", "Hub", "graph", "View MARC", "RDF", "profile settings", "LINKED_DATA" |
| Eureka platform (login, authorization, tenants) | `references/context/eureka.md` | EUREKA, KEYCLOAK, STCOR (stripes-core), UIROLES, MODROLESKC, UISAUTHCOM, UIPSELAPP, MODUSERSKC, MODLOGINKC, MGRENTITLE, MODSCHED, UID; "login", "log in", "logout", "session timeout", "idle session", "fixed-length session", "RTR", "refresh token", "Keycloak", "realm", "auth user", "Keycloak record", "promote user", "capability", "capability set", "authorization role", "authorization policy", "default role", "tenant", "entitlement", "application", "sidecar", "Kong", "password reset link", "SSO-only theme", "tenant selection screen" |
| DCB (Direct Consortia Borrowing) | `references/context/dcb.md` | Jira prefix not recorded in dcb.md — detect by keywords: "DCB", "direct consortia borrowing", "lending library", "borrowing library", "pickup library", "borrowing-pickup", "virtual item", "DCB transaction" |

A story can span two areas (e.g. closing an order affects Finance) — read both context files. Acquisitions chains: Serials Management → Receiving; Claiming → Receiving + Organizations + Export Manager; EDIFACT order export → Orders + Organizations + Export Manager. Inventory: MARC holdings → `marc-holdings.md` + `inventory.md` (+ `data-import.md` for imported records); browse stories → `inventory-browse.md` + `inventory.md`.

Login/session/authorization stories in an ECS environment span **Eureka platform** and **Consortium Manager** — read both.

> **Some areas are API/protocol-tested, not UI-tested.** OAI-PMH, and API-flagged cases in MARC validation (`API | ...` sections), assert HTTP requests and XML/JSON response fields rather than toasts, modals, and panes. For these, the same rigor applies but to a different surface: the "steps" are request URLs/params (e.g. `verb=ListRecords&metadataPrefix=marc21_withholdings&from=<date>`) and the "expected results" are response contents and exact field mappings (e.g. holdings → MARC `952` subfields), not UI strings. Don't force a UI navigation/toast shape onto these; follow the protocol/field-mapping detail in the context file. Execution Type may be `Karate` or `Backend Component` rather than `Manual` for such cases.

If a context file for the detected area does not exist, notify the user:
> "I don't have a context file for this area yet. I'll generate cases based on the User Story alone — results may be less accurate for domain-specific preconditions."

### How to use the context file

- **Key Business Rules section is the scenario source.** For each rule the story touches, decide: does this story change the rule, depend on it, or risk breaking it? Touched rules become scenarios.
- Use the domain model to write realistic preconditions: which records must exist, in what status, with what values (e.g. an encumbrance requires a Fund, a Budget in an active Fiscal Year, an Open PO with a POL fund distribution).
- Use documented side effects to build verification steps: if the context file says an action touches N entities (e.g. PO Close → encumbrance released, budget Available restored, PO status + reason for closure, POL statuses), the case verifies ALL of them.
- Use exact terminology from the context file (statuses, field names, transaction types) — never invent UI labels.

### Context file protection rule

Context files in `references/context/` are read-only for this skill.
Never modify, overwrite, or delete context files when running write-testrail-cases.
If a context file appears outdated, notify the user and suggest running build-app-context to refresh it.

---

### Freshness

Every context file must start with a header in this shape (`build-app-context` writes it; fix it by hand if missing):

```
> Built: YYYY-MM-DD · Delta-refreshed: YYYY-MM-DD · Release: <release the sources reflect, e.g. R2 2026 Umbrellaleaf> · Builder: build-app-context | manual
> Sources: TestRail sections <ids>; GitHub <repos/files>; Jira <projects/JQL>
```

Treat the file as **stale** when the newer of `Built` and `Delta-refreshed` is older than 90 days, or when the story's Fix Version is a newer release than the header's Release.

A delta refresh appends a `## Changes since <date>` section at the end of the file (What changed, UI strings changed, Jira Done issues, new TestRail cases). **Read it first: where it contradicts the sections above, it wins.** Strings listed under "Removed strings — do not assert" must never appear in expected results. For a stale file:
- run Lightweight Context Enrichment (SKILL.md) for the story;
- tell the user in Scenario Analysis: `⚠️ <area>.md was built <date> for <release>; consider running build-app-context`;
- treat its Exact UI Texts as `[verify]` unless enrichment re-confirmed them.

String provenance tags used inside context files: `[confirmed]` (source + cases agree), `[from source — file, date]`, `[from cases]`, `[from KB]`, `[verify]`. Assert `[confirmed]` / `[from source]` strings verbatim; add the verify flag to the others.
