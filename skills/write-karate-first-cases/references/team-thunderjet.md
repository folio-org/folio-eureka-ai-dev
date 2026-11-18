# Thunderjet (acquisitions) in folio-integration-tests

Snapshot of `folio-org/folio-integration-tests` master, November 2026. Re-check the runner classes before relying on this table.

## Rules files (authoritative)

| File | Use for |
|---|---|
| `acquisitions/ai/ACQ_ORDERS_SYSTEM_PROMPT.md` | mod-orders, consortia, edge-orders |
| `acquisitions/ai/ACQ_CROSS_MODULES_SYSTEM_PROMPT.md` | cross-modules (orders ↔ finance ↔ invoices) |
| `acquisitions/ai/prompt/PROMPT_TEMPLATES.md` | The team's own "mirror TestRail case C…" prompt |

## Folders, runners, root features

Base: `acquisitions/src/main/resources/thunderjet/`, runners in `acquisitions/src/test/java/org/folio/`.

| Folder | Runners (by Test Group) | Root feature |
|---|---|---|
| `mod-orders/features/` | `OrdersCriticalPathApiTest`, `OrdersExtendedApiTest`, `OrdersApiTest` | `mod-orders/orders.feature` |
| `cross-modules/features/` | `CrossModulesCriticalPathApiTest`, `CrossModulesExtendedApiTest`, `CrossModulesApiTest` | `cross-modules/cross-modules.feature` |
| `mod-finance/features/` | `FinanceApiTest` | `mod-finance/finance.feature` |
| `mod-invoice/features/` | `InvoicesExtendedApiTest`, `InvoicesApiTest` | `mod-invoice/invoice.feature` |
| `mod-organizations/features/` | `OrganizationsApiTest` | `mod-organizations/organizations.feature` |
| `consortia/` | `ConsortiaOrdersApiTest` | `consortia/consortia-orders.feature` |
| `edge-orders/features/` | `EdgeOrdersApiTest` | `edge-orders/edge-orders.feature` |
| `mod-gobi/features/` | `GobiExtendedApiTest`, `GobiApiTest` | `mod-gobi/gobi.feature` |
| `mod-mosaic/features/` | `MosaicApiTest` | `mod-mosaic/mosaic.feature` |
| `mod-ebsconet/features/` | `EbsconetApiTest` | `mod-ebsconet/ebsconet.feature` |
| `mod-data-export-spring/features/` | `DataExportSpringExtendedApiTest`, `DataExportSpringApiTest` | `mod-data-export-spring/data-export-spring.feature` |

Registration = file name appended to the end of the runner's `FEATURES` array **and** a `Scenario` appended to the root feature. Runners share one tenant per class (`SharedOrdersTenant`, `SharedCrossModulesTenant`, …) and run features in parallel (`THREAD_COUNT = 4`).

## Users and permissions
- `headersUser` for mod-orders, mod-orders-storage and inventory; `headersAdmin` for everything else (finance setup, settings).
- Permissions for both users are defined in the module's `init-*.feature` (for orders: `mod-orders/init-orders.feature`, includes `orders.item.approve`, `orders.item.unopen`, `orders.item.reopen`).

## Reusable features
All registered in `acquisitions/src/main/resources/karate-config.js` (≈ 90 keys). Most used: `createFund`, `createBudget`, `createOrder`, `createOrderLine`, `openOrder`, `unopenOrder`, `closeOrder`, `createInvoice`, `createInvoiceLine`, `approveInvoice`, `payInvoice`, `variables` (global fiscal year, ledger, vendor, locations, material types). Read the `# parameters:` header of the reusable before calling it — for example `createOrder` accepts only `id, vendor?, orderType?, ongoing?, reEncumber?, acqUnitIds?`; anything else (such as `approved`) needs a GET → set → PUT.

## Pitfalls seen in practice
- **Tenant-wide order settings** (`/orders-storage/settings`, e.g. `approvals.isApprovalRequired`) affect every parallel feature in the runner and are cached by mod-orders for 60 s (bypass header `x-okapi-bypass-cache: true`). Avoid toggling them; find a path to the changed code that does not need them.
- TestRail amounts in brackets are positive in the API.
- Feature file names over ~90 characters break Karate HTML reports.
- `@parallel=false` is reserved for `init-*.feature`; do not use it in new features.
- Many reusable features use `karate.get('<param>', <default>)`; omitted parameters silently take defaults (One-Time order, global vendor, 1 physical copy at the default location).
