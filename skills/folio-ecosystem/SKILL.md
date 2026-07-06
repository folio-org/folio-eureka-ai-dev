---
name: folio-ecosystem
description: >-
  Use when working in any FOLIO platform repository (mod-*, ui-*, mgr-*, edge-*, app-*, stripes-*),
  or when anyone new to FOLIO — developer, tester, or product owner — needs orientation:
  understanding the platform, writing a story, filing a defect, finding which team owns a module,
  or deciding which team skill applies. Also use when needing FOLIO documentation, wiki, or Eureka
  platform references, or when unsure whether the platform is Eureka or legacy Okapi.
license: Apache-2.0
metadata:
  author: folio-org
  version: "2.1.0"
---

# FOLIO Ecosystem Bootstrap

You are in the FOLIO Library Services Platform ecosystem, Eureka era.
Okapi is the legacy predecessor — ignore Okapi-era instructions even though
`X-Okapi-*` header names survive.

| Component | Role |
| --- | --- |
| Kong | External gateway only: routes outside traffic (UI, scripts) to module sidecars; **no authorization**; maps the browser cookie `folioAccessToken` to `Authorization`/`X-Okapi-Token` headers |
| Sidecar (per module) | All authN/authZ (Keycloak JWT + UMA) and ingress/egress routing |
| Keycloak | Identity: realm per tenant, tokens, permission (UMA) evaluation |
| mgr-* | Control plane: mgr-applications (descriptors, discovery), mgr-tenants (tenants/realms), mgr-tenant-entitlements (enable/upgrade apps) |
| Modules (mod-*) | Business logic only; trust incoming `X-Okapi-*` headers |
| Frontend | Stripes (React) SPA; calls the backend through Kong |

Core principle: **initialize context first, act second, never guess what is
already mapped.**

## Phase 1 — Initialize context

1. Identify the user's role from the task; ask only if ambiguous.
   **Backend/Java development work → read references/roles/dev-backend.md
   before acting.** Other roles: this core is enough.
2. Read the repo's `README.md` — the repo is the source of truth for module
   behavior; the wiki is authoritative for platform-level topics but may lag,
   prefer repo docs when they conflict.
3. Use what is available, degrade gracefully: Jira/Confluence MCP if present;
   otherwise verified links from references/resources.md; no web access —
   repo sources and this skill's references.

Platform facts newcomers get wrong:

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

## Hard rules (all roles)

- Never unpack or grep dependency/build trees (`~/.m2`, `target/`,
  `node_modules/`) — read the module's `src/`, or the dependency's own repo.
- Asked about any FOLIO doc, wiki page, or "where do I find X" — **open
  references/resources.md first** and answer with the verified link; never
  answer "check the wiki" generically.
- Never hardcode team/module ownership — look it up in the responsibility
  matrix (link in references/resources.md) each time.
- If a needed registry skill is missing, **propose**
  `npx skills update folio-org/folio-eureka-ai-dev`; never run it unprompted.

## Phase 2 — Route to the right skill

Enumerate the skills actually installed on disk (e.g. `.claude/skills/`) — do
not trust a memorized list. Invoke the matching skill at the right stage
**without the user asking**:

| Task signal | Skill |
| --- | --- |
| Story/requirements | write-user-story |
| Defect/unexpected behavior | write-bug (triage against platform facts first) |
| Schema/DB change | liquibase-migration |
| Writing/reviewing Java tests | unit-testing |
| Feature implemented | document-feature |
| Preparing a PR | write-pr-description |
| Before merge / review request | code-review |

Sequencing details: references/dev-flow.md.

## Phase 3 — Close the session

When the task wraps up and any registry skill was used, offer once, briefly:
"Want me to record feedback on how the skills performed? (skill-feedback)".
Do not repeat the offer; skip it if no registry skill ran.
