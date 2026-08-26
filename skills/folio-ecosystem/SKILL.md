---
name: folio-ecosystem
description: >-
  Load this first, at the start of any session in a FOLIO platform repository (mod-*, ui-*, mgr-*,
  edge-*, app-*, stripes-*) — before acting, and before or alongside any other FOLIO skill.
  Also use when anyone new to FOLIO — developer, tester, or product owner — needs orientation:
  understanding the platform, writing a story, filing a defect, or finding which team owns a
  module; and when needing FOLIO documentation, wiki, or Eureka platform references, or when
  unsure whether the platform is Eureka or legacy Okapi.
license: Apache-2.0
metadata:
  author: folio-org
  version: "3.0.0"
---

# FOLIO Ecosystem Orientation

FOLIO is an open-source Library Services Platform: a multi-tenant host for
independently released modules, one per business domain (inventory, users,
circulation, orders, …), assembled into applications and enabled per tenant.
~465 repos under `github.com/folio-org`.

You are in the **Eureka** era. Okapi is the legacy predecessor — ignore
Okapi-era instructions even though `X-Okapi-*` header names survive.

Core principle: **orient first, act second.** The repo you are in is the
source of truth for module behavior; the wiki is authoritative for
platform-level topics but may lag — prefer repo docs when they conflict.

## Where you are — repo taxonomy

| Prefix | What it is |
| --- | --- |
| `mod-` | Backend module (business logic, own DB schema per tenant) |
| `ui-` | Stripes (React) frontend module |
| `edge-` | External-facing API for third-party systems |
| `mgr-` | Eureka control plane (not business logic) |
| `app-` | Application descriptor: the bundle of modules released together |
| `stripes-`, `platform-` | Frontend framework libraries and UI bundles |

## How the platform works

| Component | Role |
| --- | --- |
| Kong | External gateway only: routes outside traffic (UI, scripts) to module sidecars; **no authorization**; maps the browser cookie `folioAccessToken` to `Authorization`/`X-Okapi-Token` headers |
| Sidecar (per module) | All authN/authZ (Keycloak JWT + UMA) and ingress/egress routing |
| Keycloak | Identity: realm per tenant, tokens, permission (UMA) evaluation |
| mgr-* | mgr-applications (descriptors, discovery), mgr-tenants (tenants/realms), mgr-tenant-entitlements (enable/upgrade apps) |
| Modules (mod-*) | Business logic only; trust incoming `X-Okapi-*` headers |
| Kafka | Backbone for platform events (entitlement, capabilities, system users) and inter-module domain events |
| Frontend | Stripes (React) SPA; calls the backend through Kong |

## Platform facts newcomers get wrong

- Authorization happens in the **sidecar** (Keycloak UMA), not in the module;
  modules trust the `X-Okapi-*` headers they receive.
- Enabling an app for a tenant is **eventually consistent**: capabilities are
  created asynchronously (Kafka → mod-roles-keycloak). A 403 right after
  entitlement is usually propagation lag or an unassigned capability — triage
  before filing a bug.
- New capabilities are **not** auto-added to existing roles; assign them (or
  their capability-set) explicitly.
- A merged module change reaches tenants only after: release → application
  descriptor update → entitlement upgrade.
- Module-to-module calls go **through sidecars, never through Kong**: the
  module calls its own sidecar, which routes directly to the target module's
  sidecar using routes learned from discovery.
- **System user** = a module's service account, created at entitlement time
  (Kafka `system-user` topic → mod-users-keycloak, with role-assignment
  retries). The sidecar attaches its token to egress calls only if the module
  declares "system user required" in its bootstrap. Most m2m 401s trace here.

## Working rules

- Never unpack or grep dependency/build trees (`~/.m2`, `target/`,
  `node_modules/`) — read the module's `src/`, or the dependency's own repo.
- Asked about any FOLIO doc, wiki page, or "where do I find X" — **open
  references/resources.md first** and answer with the verified link; never
  answer "check the wiki" generically.
- Never hardcode team/module ownership — look it up in the responsibility
  matrix (link in references/resources.md) each time.
- Use what is available, degrade gracefully: Jira/Confluence MCP if present;
  otherwise the verified links in references/resources.md; with no web
  access, repo sources and this skill's references.

## Going deeper

- **Any specific module** — the dig-deeper ladder (README → module descriptor
  → API spec → NEWS.md → owning team → dependency sources) and the verified
  documentation map: `references/resources.md`.
- **Backend/Java work in a module** — `references/roles/dev-backend.md`
  (search rules, API-first change flow, descriptor/interface bumps, test
  commands).
- **Running the platform, endpoint sequences, per-module watch-outs** —
  `docs/eureka-dev-flow.md` in the registry repo
  (folio-org/folio-eureka-ai-dev), fetch when needed.

## Related skills

This registry (`folio-org/folio-eureka-ai-dev`) also ships task skills —
user stories, bug reports, migrations, tests, feature docs, PR descriptions,
code review, skill feedback. Enumerate what is actually installed on disk
(e.g. `.claude/skills/`) rather than trusting a remembered list, and use one
when it fits the task at hand. If a useful one is missing, you may mention
`npx skills update folio-org/folio-eureka-ai-dev` — never run it unprompted.
