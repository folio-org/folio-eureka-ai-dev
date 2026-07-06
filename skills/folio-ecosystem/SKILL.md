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
  version: "2.0.0"
---

# FOLIO Ecosystem Bootstrap

You are in the FOLIO Library Services Platform ecosystem, Eureka era:
microservice modules behind Kong (gateway) and per-module sidecars, Keycloak
auth, mgr-* managers, Kafka events. Okapi is the legacy predecessor — ignore
Okapi-era instructions even though `X-Okapi-*` header names survive.

Core principle: **initialize context first, act second, never guess what is
already mapped.** Follow the three phases in order.

## Phase 1 — Initialize context

1. Identify the user's role from the task (developer / tester / product
   owner); ask only if the task is ambiguous.
2. Identify the repo type from its name prefix and read its `README.md` /
   `docs/` — the repo is the source of truth for module behavior; the wiki is
   authoritative for platform-level topics but **may lag reality**, prefer
   repo docs when they conflict.
3. Note available integrations, degrade gracefully: Jira/Confluence MCP if
   present (tickets, wiki content unreadable by plain fetch); otherwise give
   the user verified links from references/resources.md. No web access — rely
   on repo sources and this skill's references.

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

Deeper platform/endpoint detail lives in `docs/eureka-dev-flow.md` (developer
role) — load it only when actually needed.

## Phase 2 — Route to the right skill

Enumerate the skills actually installed on disk (e.g. `.claude/skills/`,
`.agents/skills/`) — do not trust a memorized list. Invoke the matching skill
at the right stage **without the user asking**; prefer the specific skill over
improvising:

| Task signal | Skill |
| --- | --- |
| Story/requirements | write-user-story |
| Defect/unexpected behavior | write-bug (triage against platform facts first) |
| Schema/DB change | liquibase-migration |
| Writing/reviewing Java tests | unit-testing |
| Feature implemented | document-feature |
| Preparing a PR | write-pr-description |
| Before merge / review request | code-review |

If a needed skill is missing, say so and **propose**
`npx skills update folio-org/folio-eureka-ai-dev` — never run it unprompted.
See references/dev-flow.md for sequencing.

## Phase 3 — Close the session

When the task wraps up and any registry skill was used, offer once, briefly:
"Want me to record feedback on how the skills performed? (skill-feedback)".
Do not repeat the offer; skip it if no registry skill ran.

## Guardrails — avoid wasteful actions

- Never scan or unpack dependency/build trees: `~/.m2`, `target/`,
  `node_modules/`, Docker layers. Read the module's own `src/` and
  `descriptors/`; for library internals prefer the library's repo or link.
- Never guess wiki URLs (legacy `/display/...` links 404) — use
  references/resources.md.
- Never hardcode team/module ownership — look up the responsibility matrix
  (references/resources.md) each time.
- Load references and `docs/eureka-dev-flow.md` on demand, not upfront.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Following Okapi-era docs | Eureka only; Okapi is legacy |
| Trusting wiki over repo for module behavior | Repo README/docs win at module level |
| Waiting for the user to name a skill | Route proactively per Phase 2 |
| Grepping through .m2/target for answers | Sources, repos, or links only |
