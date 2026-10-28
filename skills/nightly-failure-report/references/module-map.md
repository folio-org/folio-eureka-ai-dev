# API path to FOLIO module

Use this map to find which module repository serves a failing request. Clone it with `scripts/app_repo.py`.

| API path prefix | module repository |
|---|---|
| `orders`, `orders-storage` | mod-orders / mod-orders-storage |
| `invoice` | mod-invoice |
| `finance` | mod-finance |
| `eholdings` | mod-kb-ebsco-java |
| `circulation` | mod-circulation |
| `calendar` | mod-calendar |
| `data-export-spring` | mod-data-export-spring |
| `data-export` | mod-data-export |
| `specification-storage` | mod-record-specifications |
| `records-editor` | mod-quick-marc |
| `lists` | mod-lists |
| `query`, `entity-types` | mod-fqm-manager |
| `bulk-operations` | mod-bulk-operations |
| `users` | mod-users |
| `inventory`, `instance-storage`, `holdings-storage`, `item-storage` | mod-inventory / mod-inventory-storage |
| `search` | mod-search |
| `data-import`, `change-manager`, `mapping-rules` | mod-data-import / mod-source-record-manager |
| `remote-storage` | mod-remote-storage |
| `organizations` | mod-organizations / mod-organizations-storage |
| `linking-rules` | mod-entities-links |

UI apps live in `ui-<app>`, e.g. `ui-inventory`, `ui-users`.

If a path is not listed, search the `folio-org` GitHub organization for the path in a module's `descriptors/ModuleDescriptor-template.json`.
