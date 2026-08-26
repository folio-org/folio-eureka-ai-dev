# FOLIO/Eureka Deep Dive — what an agent actually needs

| | |
| --- | --- |
| **Date** | 2026-08-26 |
| **Status** | Research complete; skill restructure proposed in Part 8, not yet applied |
| **Question** | What exactly can make a model aware of FOLIO, the Eureka platform, and its development lifecycle — for agentic development? |
| **Eval target** | **sonnet5-medium** — everything proposed here must be re-tested on it (docs/skill-test-scenarios.md) |
| **Sources** | 81 local repos under `~/EBSCO-FOLIO`; FOLIO wiki via Confluence MCP; dev.folio.org; folio-org on GitHub; the Okapi guide |

## How to read this

Findings are sorted twice, and both axes matter.

**By value to the skill** (does it earn context-window tokens?):

- **IN** — names a file, page, repo, or invariant an agent cannot see from the
  single repo it sits in, and that changes what it does.
- **DERIVABLE** — sonnet5-medium gets it from the repo it is in (README,
  descriptors, pom, tests). Out of the skill by the 2026-07-04 RED rule.
- **VOLATILE** — versions, ports, rosters, current release. Out; link the
  authority instead.

**By confidence** (may an agent assert it to a human?):

- **Verified** — traced to a primary source named inline: a file and line, a
  verbatim error string, a SQL view, a wiki page read through the API.
- **Likely** — reasoned from verified pieces but not traced end to end. Must be
  reported as a hypothesis, never as fact.

## Top findings

The ten that changed my picture of the platform, each verified as noted:

1. **A module declares its system user in one exact place** —
   `descriptors/ModuleDescriptor-template.json` → `metadata.user.type: "system"`
   with a `permissions` array. mgr-applications derives `systemUserRequired`
   from precisely that JSON path; the sidecar attaches a system-user token only
   when it is true. Missing field ⇒ m2m 401; missing entry in the array ⇒ m2m
   403. *(§3.5 — traced sidecar → mgr-applications → SQL view)*
2. **There are two m2m token mechanisms, not one.** Besides the system user, the
   sidecar can obtain a deliberately over-privileged **system JWT** via
   `client_credentials` and send it as `X-System-Token`. The skill's current
   single-mechanism bullet is wrong. *(§2.2, EUREKA-588)*
3. **Entitlement publishes four Kafka events, three of them conditional** —
   `<env>.<tenant>.{capability,scheduled-job,system-user}` and
   `<env>.entitlement`. No timers in the descriptor ⇒ no scheduled-job event; no
   `metadata.user` ⇒ no system-user event. *(§4 — verified in `KafkaEventUtils.java`)*
4. **"Entitlement finished" does not mean the platform is ready.** MTE marks the
   flow `FINISHED` when *its* stages end while consumers are still working; the
   tracking fix (EUREKA-732) is not implemented upstream. Verify capabilities
   directly, never flow status. *(§4 — code search with positive control)*
5. **Users are split in two**: Keycloak owns the AuthUser (username, password),
   mod-users owns the PersonUser (names, contact, patron data), and
   mod-users-keycloak routes between them. **Patrons have no Keycloak account at
   all** — only people who log in do. *(§2.1)*
6. **A capability is a Keycloak permission** (resource + scope) — the conceptual
   inverse of a FOLIO permission. A role is a policy evaluated at request time,
   not a stored grant, and capabilities can also be assigned to users directly,
   so the model is not pure RBAC. *(§2.1)*
7. **Interface compatibility: major must match exactly, minor must be at least
   as high.** Verified in Eureka's own `InterfaceComparisonUtils`, not merely in
   the legacy Okapi guide — this is the rule behind "additive ⇒ bump minor".
   *(§3.2)*
8. **ECS vs non-ECS is a first-order split the skill says nothing about.**
   Cross-tenant requests are off by default (`ALLOW_CROSS_TENANT_REQUESTS:false`,
   verified in the sidecar's `application.properties:59`); impersonation exists
   for consortia; FOLIO tests ECS and non-ECS as separate environments. *(§5)*
9. **Several repos an agent cannot guess exist carry hard invariants** — notably
   `folio-permissions-mappings` (deleting a mapping breaks the system; correct
   via the descriptor `replaces` mechanism) and `mod-okapi-facade` (read-only
   Okapi compatibility, writing new code against it is discouraged). *(§1.1)*
10. **Eureka is the shipped default, not an experiment** — the Okapi → Eureka
    migration completed with **Sunflower (R1 2026, released 2026-03-17)**. A
    model with a stale prior will say otherwise. *(§3.3)*

## Contents

- Part 1 — Local workspace corpus: repos, prior art, cross-repo conventions
- Part 2 — FOLIO wiki: platform overview, sidecar internals
- Part 3 — Development lifecycle: contribution, versioning, release, tooling
- Part 4 — Entitlement's asynchronous tail, verified against code
- Part 5 — ECS (consortia) vs non-ECS
- Part 6 — Two negative findings about the resource map itself
- Part 7 — Other sources worth registering (not yet mined)
- Part 8 — What this means for the skill (the proposal)

## Freshness caveats

Local checkouts range 2026-05-04 … 2026-06-22 and `mgr-tenant-entitlements` sits
on a feature branch; upstream claims were re-checked against `origin/master` and
GitHub code search where they mattered. Wiki pages carry no reliable edit dates
in the API response, so treat wiki-only facts as weaker than code-verified ones.

---

## Part 1 — Local workspace corpus (81 repos under ~/EBSCO-FOLIO)

The single richest source, and the one no public doc replaces: it shows which
repos exist and how they relate. Most of these are absent from the current
`resources.md`.

### 1.1 Repos an agent cannot guess exist

| Repo | What it is | Bucket |
| --- | --- | --- |
| `mod-okapi-facade` | Read-only partial Okapi API impl over the mgr-* components, for legacy code that still calls Okapi endpoints. Writing new code against it is explicitly discouraged; intended to be removed eventually. | **IN** — explains "why does this module call /_/proxy/..." in Eureka |
| `folio-permissions-mappings` | Single `mappings-overrides.json`: permissions that cannot be auto-converted to capabilities; consumed by mod-roles-keycloak. **Never remove entries** (breaking); corrections go through the module descriptor `replaces` mechanism. | **IN** — hard invariant, unguessable |
| `folio-flow-engine` | Generic staged flow executor (parallel/sequential stages, per-stage state) used by mgr-tenant-entitlements — the reason entitlement failures are reported as *stages*. | **IN** — explains entitlement failure reports |
| `folio-secure-store-proxy` (FSSP) | Quarkus proxy centralizing secret access (AWS SSM / Vault) for modules and sidecars; mTLS. | **IN** — third secret-store option next to SSM/Vault |
| `folio-module-descriptor-validator` | Maven plugin validating `ModuleDescriptor-template.json` against FOLIO conventions; integrable in any module build. | **IN** — a checkable gate for descriptor edits |
| `folio-application-generator` | Maven plugin generating/updating application descriptors (`mvn folio-application-generator:generate|update`). | **IN** |
| `application-descriptors`, `app-*` repos | Application descriptors: which modules ship together (`app-platform-minimal`, `app-platform-complete`, `app-edge-complete`, `app-consortia*`). | **IN** — the release unit above a module |
| `folio-keycloak-plugins` | FOLIO's Keycloak SPI plugins; version tracks the Keycloak major.minor it is built against. | **IN** |
| `folio-integration-tests` | Karate-based cross-module API test suite, daily Jenkins run. | **IN** — where platform-level regressions live |
| `folio-module-descriptor-mcp` | MCP server for querying/analyzing module descriptors. | **IN** (agentic tooling) |
| `eureka-setup` / `eureka-platform-bootstrap` | Two local-environment paths: Eureka CLI, and Compose-based `app-platform-minimal` bootstrap. | **IN** |
| `mod-settings` | Key-value settings store replacing mod-configuration; permission naming is `mod-settings.{global,users}.{read,write}.<scope>`. | DERIVABLE per-module, but the *replacement of mod-configuration* is IN |

### 1.2 Prior art: module-level AGENTS.md files

28 repos in **this workspace** already carry `AGENTS.md`/`CLAUDE.md` (~1850
lines total). That ratio is a property of this machine, not of FOLIO — a fresh
clone elsewhere may have none — but the files themselves are the team's own
answer to "what must an agent be told about this module", and so the best
available ground truth for what belongs in a skill vs what belongs in a repo
file. Reviewed below.

Reviewed: `mgr-tenant-entitlements`, `folio-module-sidecar`, `mod-roles-keycloak`.
They are 100–300 lines each of build commands, package maps, test conventions,
and pitfalls. **Conclusion: the skill must not duplicate them.** Their existence
is itself the finding — the right instruction is "if the repo has AGENTS.md /
CLAUDE.md, read it before anything else; it outranks this skill for that module."

Cross-repo conventions that recur in all three (so they are platform, not module,
facts):

| Convention | Detail | Bucket |
| --- | --- | --- |
| Test tags | `@UnitTest` / `@IntegrationTest`; unit `*Test.java`, integration `*IT.java` extending a `BaseIntegrationTest` | **IN** — same everywhere, saves rediscovery |
| Checkstyle | `folio-java-checkstyle`, **max method length 23 lines**, fails the build on warnings; `-Dcheckstyle.skip=true` while iterating | **IN** — identical in sidecar and mgr-tenant-entitlements |
| API-first | OpenAPI YAML in `src/main/resources/swagger.api/` → `mvn generate-sources`; controllers implement generated interfaces; **never edit `target/generated-sources`** | **IN** |
| Coverage gate | JaCoCo 80% instruction minimum, `-Pcoverage` | **IN** |
| Kafka topics | prefixed with the `ENV` variable (logical deployment name) | **IN** — explains "topic not found" confusion |
| Secret store | `SECRET_STORE_TYPE`: Ephemeral / AWS-SSM / Vault / **FSSP** | **IN** |
| Java/Spring | Java 21; Spring Boot 4 for managers/modules, Quarkus 3.x for sidecar + FSSP | VOLATILE-ish — state the split, not the versions |

### 1.3 Sidecar internals worth knowing at platform level

Ingress filter chain with orders (from `IngressFilterOrder`), i.e. the exact
sequence a request survives before the module sees it:

```
90  RequestValidation
100 SelfRequest            (sidecar-to-sidecar bypasses auth)
110 KeycloakSystemJwt
120 KeycloakJwt            (parse Bearer)
130 KeycloakTenant         (token tenant == x-okapi-tenant)
140 Tenant                 (is the tenant enabled?)
150 KeycloakImpersonation
160 KeycloakAuthorization  (RPT / UMA evaluation)
170 SidecarSignature
171 DesiredPermissions
```

**IN (condensed)** — the triage value is the *ordering*: a 401 dies at 110–130,
a 403 at 160, and neither ever reaches the module. That single sentence is worth
more than the full list.

Egress: `ServiceTokenProvider` (module's own service token) vs
`SystemUserTokenProvider` (system-user token) in `service/token/`; discovery
lookup then forward to the **target module's sidecar**.

### 1.4 mgr-tenant-entitlements: why entitlement failures look the way they do

Built on `folio-flow-engine`: Entitle / Upgrade / Revoke / **Desired-State**
flows, composed of retryable stages with finalizers that run on both success
and failure. Consequences an agent should know:

- entitlement errors surface as **a failed stage name**, not a stack trace —
  ask for the stage;
- stages must be idempotent because they are retried;
- module installation is parallel (`FLOW_ENGINE_MODULE_INSTALLER_THREADS`);
- there is an interface-integrity validator across applications — most
  "cannot entitle" errors are unsatisfied interface dependencies.

**IN** — unguessable from a module repo, and it is the #1 platform failure mode.

### 1.5 mod-roles-keycloak: the authorization data plane

- **Dual-write**: every mutation goes to Postgres *and* Keycloak, with
  compensating rollback on failure.
- Capability events arrive over Kafka and **retry indefinitely at 1s** by
  default — a stuck capability is a poison-message symptom, not a lost event.
- Legacy FOLIO permissions → capabilities migration is asynchronous.
- Permissions that cannot be auto-mapped live in `folio-permissions-mappings`
  (`mappings-overrides.json`); corrections go through the module descriptor
  `replaces` mechanism, never by deleting a mapping.

**IN** — completes the 403-triage story that the current skill only half tells.

---

## Part 2 — FOLIO wiki (read via Confluence API; plain fetch returns chrome)

### 2.1 Eureka Platform Overview (PLATFORM/193134643)

The single best conceptual source. Findings the current skill does **not** carry:

| Finding | Why it matters | Bucket |
| --- | --- | --- |
| **AuthUser vs PersonUser split.** Keycloak owns username/userId/password (AuthUser); mod-users owns names, emails, patron metadata (PersonUser). `mod-users-keycloak` wraps mod-users + mod-users-bl and routes each concern to the right side. | Explains why user work touches two stores, and why "create a user" is two operations | **IN** |
| **Patrons have no Keycloak AuthUser** — only users who actually log in (staff) get one. | Directly changes how a user-related story/defect is written | **IN** |
| **Capability = Keycloak Permission** (Resource + Scope), the *conceptual inverse* of a FOLIO permission: a capability effectively has users (via user/role policies), rather than a user having permissions. Roles are native Keycloak objects tied to Role Policies, evaluated at authorization time — role membership is not a permanent grant. | The mental model that makes the whole roles/capabilities API make sense | **IN** |
| Eureka is **not pure RBAC** — capabilities can be assigned directly to users. | Prevents wrong assumptions in stories/tests | **IN** |
| **Late-binding platform**: a tenant's authN/Z infrastructure is only created when an application is entitled for it. | The root cause behind the eventual-consistency 403 the skill already mentions | **IN** |
| Kong objects: Application Manager creates a Kong **Service** per application; the Entitlement Manager adds the **Routes**, tagged with `X-Okapi-Tenant` per tenant. | Precise mapping for "where did my route come from" | **IN** |
| On Eureka, **mod-login and mod-login-saml are not used**; Keycloak renders a themed login screen. mod-login-keycloak exists for interface backward-compatibility. | Stops agents editing/So citing dead modules | **IN** |
| Backward compatibility is a *primary requirement*: unmodified FOLIO modules must run on Eureka, and modules stay agnostic to security enforcement. | Frames every "should the module check permissions?" question | **IN** |
| Passwords are not migrated from classic FOLIO — they must be reset. | Migration stories/defects | IN (narrow) |

### 2.2 folio-module-sidecar deep dive (FOLIJET/509149215)

Deep, mostly reference-grade. The parts with triage value:

- **Bootstrap**: sidecar calls `GET /modules/{moduleId}` (mgr-applications, for ingress+egress
  routing entries), `GET /entitlements/modules/{moduleId}` (mgr-tenant-entitlements),
  then `GET /tenants?query=id==(...)` (mgr-tenants). A tenant missing from that
  cache is rejected with the literal error
  **`400 Bad Request Application is not enabled for tenant: {tenantName}`**.
  **IN** — error-string → cause mapping is the highest-value kind of fact.
- **Two m2m token mechanisms, not one.** The skill currently only knows the
  system user. The other: a **system JWT** obtained by the sidecar via
  `client_credentials` on a tenant-specific service client
  (`KC_SERVICE_CLIENT_ID`, secret in the secure store), sent as `X-System-Token`,
  used as the fallback when a module declares no system user or the user's JWT
  lacks the permission. **IN — corrects an oversimplification in the skill.**
- **Signing-key rotation trap**: if a JWT carries an unknown `kid` and a forced
  JWKS refresh happened less than `KC_FORCED_JWKS_REFRESH_INTERVAL` (default
  1 hour) ago, the sidecar **rejects** the request rather than refetching. A real
  cause of sporadic 401s after a Keycloak key rotation. **IN**
- Authorization result is cached per
  `{permission}#{tenantId}#{userId}#{sessionId}#{expiry}`; logout invalidates via
  the `session_state` claim. Explains "I assigned the capability and it still
  fails / it still works after revoke". **IN**
- Unmatched egress can be forwarded to Kong
  (`SIDECAR_FORWARD_UNKNOWN_REQUESTS`, default destination Kong). **IN (narrow)**
- Impersonation uses Keycloak token-exchange, for consortia/cross-tenant.
  `ALLOW_CROSS_TENANT_REQUESTS` gates tenant/JWT-issuer matching. **IN (narrow)**
- Module descriptor semantics that drive filter skips: `interfaceType: system`,
  the `_timer` interface, `_tenant` v1.0/1.1/2.0 (tenant-install requests bypass
  the enabled-tenant check — otherwise entitlement could never bootstrap).
  **IN (narrow)** — genuinely unguessable.
- `SIDECAR_MODULE_PATH_PREFIX_STRATEGY`: `PROXY` / `STRIP` / `NONE`. DERIVABLE
  from the sidecar README; **out** unless working in the sidecar.
- Sizing formulas, CPU reservations, memory math: **VOLATILE** — out.

---

## Part 3 — Development lifecycle (dev.folio.org + primary sources)

The genuinely missing half of the current skill: it describes the platform but
not how work moves through it.

### 3.1 Contribution flow (dev.folio.org/guidelines/contributing/)

- **GitHub Flow**: master is always releasable; work in feature branches, merge
  by PR. Branch name carries the Jira key + description: `MODFOO-123-short-desc`.
- Commit messages: imperative mood, ≤50-char subject, blank line, body explains
  **why**; include the Jira key.
- PR: must build in CI first; title carries the Jira key; **merge without
  squashing** — FOLIO deliberately preserves commit history and attribution.
- Breaking API change ⇒ **major** version increment.

**IN** — house conventions, not derivable, and directly shape branch/commit/PR work.

### 3.2 Interface versioning — the exact rule (okapi/doc/guide.md:535)

> the major version number must match **exactly**, and the minor version must be
> **at least** as high as required.

Requiring `3.2` accepts `3.2`, `3.4`; rejects `2.2`, `4.7`, `3.1`.

**Verified for Eureka, not just Okapi**: `InterfaceComparisonUtils.isCompatible`
in `applications-poc-tools/folio-backend-common` implements exactly this —
different interface id or different major ⇒ `Integer.MAX_VALUE` (incompatible);
provided minor higher ⇒ `2`, lower ⇒ `-2`; compatible iff the result is in
`[0, 2]`. This is the code mgr-* uses for interface-integrity validation at
entitlement time.

**IN** — this one sentence is the entire reason "additive change ⇒ bump minor"
and the reason a major bump breaks every consumer. The current skill states the
conclusion without the rule.

### 3.3 Release train (dev.folio.org/guides/regular-releases/)

- Roughly **quarterly**, flower-named alphabetically: quesnelia → ramsons →
  sunflower → trillium.
- **Sunflower (R1 2026, released 2026-03-17) is the release that completed the
  Okapi → Eureka architecture migration.** Trillium (R2 2026) followed
  2026-07-14. → *Eureka is not "new" any more; it is the shipped default.*
- Module cut-off dates per release, tracked in spreadsheets pinned in Slack
  `#folio-releases`; hold feature branches that miss the cut-off.
- After the cut-off: master continues, long-lived `bX.Y` branches carry bug
  fixes for patch releases.

**IN** for the naming scheme + Sunflower/Eureka fact (an agent with an older
prior will call Eureka experimental). **VOLATILE** for "current release" — point
at the release calendar instead.

### 3.4 Module release mechanics (dev.folio.org/guidelines/release-procedures/)

Tags `vX.Y.Z`; temporary release branch `tmp-release-X.Y.Z`; bugfix branches
`bX.Y`. Maven: `mvn -DautoVersionSubmodules=true release:clean release:prepare`,
then Jenkins deploys. `NEWS.md` gets concise entries with issue numbers.
Platform branches: `master` (released), `snapshot` (unreleased), `R2-2024`-style
release branches.

**IN (condensed)** — mostly release-manager work; the agent-relevant slice is
the branch/tag naming and "NEWS.md entry with the Jira key".

### 3.5 The system-user declaration — resolved to the exact field

Traced through primary sources (sidecar → mgr-applications → SQL view):

```json
// descriptors/ModuleDescriptor-template.json
"metadata": {
  "user": { "type": "system", "permissions": ["users.collection.get", "..."] }
}
```

`mgr-applications` derives `systemUserRequired` with exactly
`descriptor @> '{"metadata":{"user":{"type":"system"}}}'`
(`changelog/changes/v3.0.0/sys-user-required-to-module-bootstrap.xml`), serves it
in the module bootstrap, and the sidecar's `SystemUserTokenProvider` attaches the
token only when that flag is true. Confirmed present in mod-bulk-operations,
mod-circulation-bff, mod-consortia-keycloak, mod-entities-links, mod-orders,
mod-roles-keycloak, mod-tlr, mod-erm-usage-harvester.

**IN — highest-value single fact found.** It converts the skill's vague "declares
system user required in its bootstrap" into a file, a JSON path, and a check the
agent can actually run. The `permissions` array is what the system user is
granted — a missing entry there is the second most common m2m 403.

### 3.6 Agentic tooling that already exists in this ecosystem

| Tool | Use |
| --- | --- |
| `folio-module-descriptor-mcp` | MCP server for querying/analyzing module descriptors |
| `folio-module-descriptor-validator` | Maven plugin — validates a descriptor against FOLIO conventions; a real verification gate after descriptor edits |
| `folio-application-generator` | `mvn folio-application-generator:generate|update` for application descriptors |
| `folio-integration-tests` | Karate cross-module API suite, daily Jenkins run — where platform regressions actually show up |
| `eureka-platform-bootstrap` / `eureka-setup` | Two ways to get a local Eureka running (Compose bootstrap; Eureka CLI) |
| Jira/Confluence MCP | Already assumed by the skill; the wiki pages that matter are unreadable by plain fetch, so the MCP is not optional for doc lookups |

**IN** — "what can I actually run to check my work" is exactly what an agentic
dev flow needs and none of it is currently in the skill.

---

## Part 4 — Entitlement's asynchronous tail, verified against code

Source: wiki EUREKA-732 (FOLIJET/941096985) + EUREKA-695, cross-checked against
the local `mgr-tenant-entitlements` checkout (2026-05-13).

**The four Kafka events mgr-tenant-entitlements publishes during entitlement**
(verified in `integration/kafka/KafkaEventUtils.java` and
`EntitlementEventPublisher.java` — topic prefix is `<env>.<tenant>.`):

| Topic | Consumer | Sent when | Payload |
| --- | --- | --- | --- |
| `<env>.<tenant>.capability` | mod-roles-keycloak | always | permissions + endpoints → capabilities |
| `<env>.<tenant>.scheduled-job` | mod-scheduler | only if the descriptor declares timers | routing entries with cron schedule |
| `<env>.<tenant>.system-user` | mod-users-keycloak | only if the descriptor declares `metadata.user.type: system` | system user name + permission list |
| `<env>.entitlement` | sidecars | always | `ENTITLE` / `REVOKE`, moduleId, tenant |

**The verified invariant:** the entitlement flow is marked `FINISHED` by
`FinishedFlowFinalizer` when *MTE's* stages complete — the downstream consumers
(capabilities, system user, timers) are still working. The wiki page EUREKA-732
exists precisely to fix this (adding `AWAITING_COMPLETION`, an
`async_entitlement_task` table and an `entitlement_task_results` ack topic);
**neither `AWAITING_COMPLETION` nor `async_entitlement_task` exists upstream**:
absent from the local checkout, absent from `origin/master`, and a GitHub code
search across `folio-org/mgr-tenant-entitlements` (default branch, 2026-08-26)
returns 0 hits for both. Positive control: the same query for
`FinishedFlowFinalizer` (a class the EUREKA-732 page names) returns 15 — so the
search is indexing this repo and the two zeros are true negatives. The gap is
still open. (The advice survives either way: verify capabilities directly rather
than flow status, whether or not the tracking fix lands.)

**IN — this is the mechanism behind the skill's existing "eventually consistent"
bullet.** Saying *why* (MTE finishes before mod-roles-keycloak has consumed the
capability event) is what turns a rule into something the agent can reason with.
Two corollaries worth stating:

- "entitlement succeeded" ≠ "capabilities exist". Verify capabilities, not flow
  status.
- No system-user event is sent at all when the descriptor lacks
  `metadata.user`, so a missing system user is a *descriptor* bug, not a Kafka
  delivery problem.

Also found (EUREKA-588 spike): the sidecar's system token is deliberately
**over-privileged** ("System JWT has access to all endpoints"), and scoping it to
declared module permissions is active work. Useful when reasoning about why an
m2m call unexpectedly succeeds.

Freshness caveat for anything code-verified here: local checkouts are
2026-05-04 … 2026-06-22, and `mgr-tenant-entitlements` sits on a feature branch.

---

## Part 5 — ECS (consortia) vs non-ECS: the split the skill ignores

Fragments were scattered across every source; consolidated here because "is this
ECS?" changes how a story, a defect, and a test are written — and the current
skill says nothing about it.

- **ECS = Enhanced Consortia Support**: a consortium of tenants (one central +
  member tenants), not a single tenant. FOLIO ships and tests ECS and non-ECS as
  **separate environments** — Bug Fest runs both variants per release (FTC space).
- Eureka's consortial pieces: `mod-consortia-keycloak` (the Eureka replacement
  for `mod-consortia`; provides `consortia`, requires `user-tenants`,
  `users-keycloak`, and the whole roles/capabilities set), plus the
  `app-consortia` / `app-consortia-manager` application descriptors.
- **Cross-tenant requests are off by default**: the sidecar reads
  `sidecar.cross-tenant.enabled=${ALLOW_CROSS_TENANT_REQUESTS:false}` (verified in
  `folio-module-sidecar/src/main/resources/application.properties:59`). With it
  off, the sidecar enforces that `X-Okapi-Tenant` matches the JWT issuer tenant.
- **Impersonation** (KeycloakImpersonationFilter, Keycloak token-exchange) exists
  specifically to serve consortia/cross-tenant flows: the sidecar looks the user
  up in mod-users-keycloak and swaps in an impersonated token.
- `SINGLE_TENANT_UX` (mod-users-keycloak + mod-consortia-keycloak) enables
  unified login for member-tenant users. **Wiki-sourced (FOLIJET/906297394),
  not found in the local 2026-05-04 checkout** — verify before relying on it.
- Realm-per-tenant means a consortium is N Keycloak realms; "a lot of tenants ⇒
  a lot of realms" is the background for the lightweight-access-token work
  (EUREKA-704).

**IN** — belongs in `platform-map.md` as its own section. For a QA/PO audience it
is a first-order question; for a developer it decides whether cross-tenant
behavior is even reachable in the environment under test.

---

## Part 6 — Two negative findings about the resource map itself

Both are load-bearing for the skill's own hard rules, so they are recorded rather
than discarded:

1. **The responsibility matrix (REL/5210256) did not return.** Fetched via the
   Confluence MCP, it ran past 15 minutes without completing — the page is very
   large. The skill currently instructs the agent to consult it *every time* for
   module ownership. If it cannot be retrieved in a normal turn, that rule is
   unusable as written and needs a fallback (ask the user, or use the smaller
   application-level table REL/884605011).
2. **`[Eureka] CI Flow` (FOLIJET/873398308) is diagram-only** — the page body is
   a single intro sentence; all content lives in images the API returns as
   attachments. It cannot answer a CI question via MCP text retrieval. Record the
   link, do not promise the content.

## Part 7 — Other sources worth registering (not yet mined)

| Source | Value |
| --- | --- |
| `[Eureka] CI Flow` (FOLIJET/873398308) | Eureka CI/CD pipeline architecture — **diagram-only, see Part 6**; link it, do not quote it |
| `FOLIO Eureka Applications` (REL/884605011) | application → team → PO → dev lead → first release. The **application**-level counterpart to the module responsibility matrix |
| `Release Guide (Eureka application)` (SPITFIRE/885162874) | app release via the `release-preparation.yml` GH workflow, `R1-2026`-style branches |
| `How to Include a New Eureka Application in Snapshot Environment Builds` (FOLIJET/848035875) | how an app reaches snapshot envs |
| Bug Fest pages (FTC space), ECS and non-ECS variants | QA environments; note ECS (consortia) vs non-ECS is a first-class split |
| `Run migration for existing users for unified login` (FOLIJET/906297394) | `SINGLE_TENANT_UX` flag in mod-users-keycloak + mod-consortia-keycloak |
| `Common Utility Functions in Eureka Karate` (FOLIJET/901873689) | how Karate tests bootstrap tenants/users — the platform test idiom |
| dev.folio.org `/guides/spring-way/` | the FOLIO Spring-way module framework guide |
| `EUREKA-588` spike (FOLIJET/995131397) | m2m calls scoped to declared module permissions — why today's system token is over-privileged |
| `EUREKA-704` (FOLIJET/887324704) | lightweight access tokens; realm-per-tenant scaling pain |
| folio.org release calendar + `Flower Release Names` (REL) | the authority for "which release is current" — link, never inline |
| `DR-000041 Eureka Adoption` (TC/860061701) | the decision record behind Eureka becoming the platform |

---

## Part 8 — What this means for the skill

### 8.1 The shape problem

The dive produced far more IN-bucket material than a SKILL.md can hold, and the
target model is **sonnet5-medium**, where a bloated body costs compliance. So the
answer is not "add it to SKILL.md" — it is progressive disclosure:

```
SKILL.md            ~500 words: what FOLIO is, where you are, the handful of
                    facts that change your FIRST action, and a router
                    TRADE (decide now, not at write time): the "How the platform
                    works" component table moves OUT to platform-map.md, leaving
                    one line of topology in the body. It is the piece the
                    2026-07-04 RED already found derivable, and it is what pays
                    for the six additions in 8.2. Without this the body lands
                    past 1000 words on a model that punishes exactly that.
references/
  platform-map.md   NEW — component + repo map, incl. the repos an agent cannot
                    guess exist (mod-okapi-facade, folio-permissions-mappings,
                    folio-flow-engine, FSSP, app-*, validator/generator/MCP)
  triage.md         NEW — symptom → cause → where to look. The highest-value
                    artifact this dive can produce
  lifecycle.md      NEW — branch/commit/PR conventions, interface version rule,
                    descriptor edits, NEWS.md, release train, how a merged change
                    reaches a tenant
  resources.md      extend — app-level matrix (REL/884605011), release calendar,
                    Eureka CI flow page
  roles/dev-backend.md  keep
```

### 8.2 Content that must reach SKILL.md itself (first-action changing)

1. **Read the repo's `AGENTS.md`/`CLAUDE.md` first if present** — where such a
   file exists it is far deeper than any skill can be and outranks it for that
   module. (Note: the 28-of-81 hit rate in *this* workspace is a property of this
   machine, not of FOLIO — a fresh clone may have none, so the instruction must
   stay conditional. This is also the opposite direction from the mechanism the
   2026-07-06 amendment rejected: that was *writing* skill pointers into module
   repos; this is only *reading* whatever the repo already provides.)
2. The AuthUser/PersonUser split and "patrons have no Keycloak account".
3. Capability = Keycloak permission (resource+scope); role membership is a
   policy evaluated at request time, not a stored grant; direct
   user↔capability assignment exists.
4. Late binding + the async tail: entitlement returns before capabilities exist.
5. The two m2m token mechanisms (system user via `metadata.user`, system JWT
   fallback) — replacing the current single, slightly wrong bullet.
6. Eureka is the shipped default since **Sunflower (R1 2026)**, not an
   experiment — counters a stale prior.
7. **The ownership rule needs a fallback chain.** Today it says "look it up in
   the responsibility matrix each time" — and that page did not return in 15+
   minutes (Part 6), making the rule unexecutable as written. Replace with:
   application-level table (REL/884605011, small enough to return) → module
   matrix (REL/5210256) if it responds → ask the user. Never a bare "check the
   matrix".

### 8.3 Content that must NOT go in

- Component-by-component architecture retelling (2026-07-04 RED: derivable).
- Sidecar env vars, prefix strategies, memory/CPU sizing (README-derivable,
  volatile).
- Per-module package maps and build commands (that is what repo AGENTS.md is for).
- Team rosters, current release numbers, ports, versions → link the authority.

### 8.4 Draft triage table (the core of references/triage.md)

**Verified** — each row traces to a primary source named in the last column.

| Symptom | Cause | Source |
| --- | --- | --- |
| `400 Application is not enabled for tenant: X` | sidecar's tenant cache lacks the tenant — entitlement never completed, or the sidecar booted before it | verbatim error string, sidecar wiki FOLIJET/509149215 |
| 403 right after entitlement | the capability event has not been consumed yet, or the capability is not assigned to the caller's role | `KafkaEventUtils.CAPABILITIES_TOPIC`; MTE finalizer behavior |
| "entitlement finished" but nothing works | MTE marks the flow `FINISHED` when *its* stages end; downstream consumers are still working. Verify capabilities/system user directly, never flow status | EUREKA-732 + code check (fix not implemented upstream) |
| m2m 401 | the module declares no system user, so the sidecar attaches no system-user token | `metadata.user.type: system` → `system_user_required` SQL view → `SystemUserTokenProvider` |
| sporadic 401 after a Keycloak restart / key rotation | JWT carries an unknown `kid` and a forced JWKS refresh already happened within `KC_FORCED_JWKS_REFRESH_INTERVAL` (default 1h) → request rejected rather than refetched | sidecar wiki, "Signing Key Rotation" |
| capability/role change appears not to take effect | the sidecar caches the authorization decision per `{permission}#{tenant}#{user}#{session}#{expiry}` until token expiry | sidecar wiki, KeycloakAuthorizationFilter |
| scheduled job never fires | no `scheduled-job` event was published — the descriptor declares no timers | EUREKA-732 table ("Mandatory: No") |
| 401 on a request that never reached the module | died in the ingress chain at KeycloakSystemJwt/KeycloakJwt/KeycloakTenant | `IngressFilterOrder` |
| 403 on a request that never reached the module | died at KeycloakAuthorization (UMA/RPT evaluation) | `IngressFilterOrder` |

**Likely — reasoned, not traced end-to-end. Mark as hypotheses when reporting.**

| Symptom | Suspected cause | What would confirm it |
| --- | --- | --- |
| 403 that never resolves, even after role assignment | the permission has no automatic capability mapping | look for it in `folio-permissions-mappings/mappings-overrides.json`; fix via the descriptor `replaces` mechanism, never by deleting a mapping |
| m2m 403 with a system user present | the needed permission is missing from `metadata.user.permissions` | compare the failing endpoint's `permissionsRequired` against that array |

Every row is sourced above and unguessable from a single module repo. This table
is the single most useful thing the dive produced for agentic development.

### 8.5 Eval note

Everything above must be re-tested on **sonnet5-medium** per
docs/skill-test-scenarios.md before release. The existing A/B numbers were
measured on a different (unstated, likely stronger) model, so the current
description is *unvalidated on the target model*, not proven.
