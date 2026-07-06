# Eureka Developer Flow

A practical reference for the developer role working on FOLIO Eureka backend
modules: how the platform is brought up, which endpoints to call and in what
order, what the overall development loop looks like, how tests are structured,
and per-module watch-outs. Eureka is the official platform core; Okapi is
legacy and not covered. For platform orientation and other roles (QA, PO),
start from the `folio-ecosystem` skill.

## 1. Platform bring-up (local)

Use `eureka-platform-bootstrap` (`./start.sh`, Docker Compose). Startup order:

1. Infra: PostgreSQL, Kafka, Vault/secure store, Keycloak, Kong.
2. Managers: `mgr-applications`, `mgr-tenants`, `mgr-tenant-entitlements`.
3. Modules, each with its `folio-module-sidecar` next to it.

All API calls below go through Kong (default `http://localhost:8000`).
Manager APIs are authorized with a token from the Keycloak **master** realm;
tenant business APIs use a token from the tenant realm.

## 2. Canonical endpoint sequence (tenant bootstrap)

```
1. POST /applications                      # mgr-applications: register application descriptor
2. POST /modules/discovery                 # mgr-applications: where each module's sidecar lives
3. POST /tenants                           # mgr-tenants: creates tenant + Keycloak realm
4. POST /entitlements?async=true&tenantParameters=loadReference=true,loadSample=true
                                           # mgr-tenant-entitlements: enables the application
                                           # (creates Kong routes, Keycloak resources, calls
                                           #  each module's /_/tenant, publishes Kafka events)
5. GET  /entitlements/{tenantName}/applications   # verify entitlement completed
6. POST /users-keycloak/users              # create admin user
7. POST /authn/credentials                 # set password
8. POST /roles                             # create role
9. PUT  /roles/{id}/capability-sets        # assign capability sets (capabilities appear
                                           #  asynchronously after entitlement, via Kafka)
10. POST /roles/users                      # assign role to user
11. POST /authn/login  (or /authn/login-with-expiry)   # get token
12. Business calls via Kong with the token # e.g. GET /users-keycloak/users?query=...
```

Day-2 loop (new module version):

```
1. Release module → new descriptor + image
2. POST /modules/discovery (new version)          # mgr-applications
3. POST /applications (new application version)   # bumped module + interface versions
4. Entitlement upgrade via mgr-tenant-entitlements per tenant
5. Verify: GET /entitlements/{tenant}/applications; check flow stages on failure
```

Key background facts:

- Authorization is evaluated by the **sidecar** (Keycloak UMA,
  `{path}#{METHOD}` permission), not by the module. The module trusts
  `X-Okapi-*` headers it receives.
- `permissionsRequired` in the module descriptor become **capabilities**
  (mod-roles-keycloak) at entitlement time; a 403 right after entitlement
  usually means the capability is not yet assigned to the caller's role.
- Sidecars synchronize state via Kafka topics (discovery, entitlement,
  logout); many "it does not see my change" issues are cache/event timing.

## 3. The overall developer flow (beyond endpoints)

1. Ticket → branch (`JIRAKEY-###`).
2. Implement. API-first: change the OpenAPI spec, regenerate
   (`mvn clean generate-sources`), then controller → service.
3. DB change: Liquibase changelog (see the `liquibase-migration` skill).
4. Module descriptor: new routes/permissions in
   `descriptors/ModuleDescriptor-template.json`; **bump the provided
   interface version** (minor for additive).
5. Tests: unit + integration (section 4). `NEWS.md` entry with the ticket key.
6. Wrap-up: feature docs → PR description → self code review (see the
   `folio-ecosystem` skill flow: document-feature → write-pr-description →
   code-review).
7. After merge/release: application descriptor update + entitlement upgrade
   make the change reachable for tenants (day-2 loop above).

Frequent local commands: `mvn clean verify`, `mvn test -Dgroups=unit`,
`docker compose up --build -d`, and for application descriptors
`mvn folio-application-generator:generate|update`.

## 4. How tests look

Shared foundation: `applications-poc-tools/folio-backend-testing` provides
JUnit 5 extensions used across managers and Keycloak-aware modules:
`@EnablePostgres`, `@EnableKafka`, `@EnableWireMock`, `@EnableKeycloakTlsMode`,
`@KeycloakRealms(...)`, `@WireMockStub(...)` (Testcontainers under the hood).

- **Unit** (`@Tag("unit")`, surefire, `mvn test -Dgroups=unit`): Mockito with
  strict stubbing, no lenient mode, AAA structure — see the `unit-testing`
  skill.
- **Integration** (`*IT.java`, failsafe): extend the module's
  `BaseIntegrationTest` (e.g. `org.folio.roles.base.BaseIntegrationTest`,
  `org.folio.tm.base.BaseIntegrationTest`), which extends the shared
  `BaseBackendIntegrationTest` and stacks the annotations above +
  `@SpringBootTest` + `@AutoConfigureMockMvc` +
  `@DirtiesContext(AFTER_CLASS)`. Fixtures: SQL via `@Sql`, WireMock stubs as
  JSON files, Keycloak realm imports as JSON.
- Run a single IT class:
  `mvn failsafe:integration-test -Dit.test=**/<TestClassName>.java`
  (do not assume `mvn verify -Dit.test=...` narrows the suite).
- Caches are cleaned in `@BeforeEach` in base classes — when adding cached
  logic, mirror that or ITs will couple.

## 5. Per-module watch-outs

Areas where newcomers most often lose time. Sources: module `NEWS.md` and
public investigation docs; details evolve — treat these as pointers, not an
issue list.

**folio-module-sidecar**
- Intermittent `invalid_token` 401s in sidecar-to-sidecar UMA evaluation
  (documented investigation, 2026-02); system-token cache is invalidated on
  egress 401 with 503 + Retry-After (MODSIDECAR-178). Debugging usually starts
  from `RequestFilterService` DEBUG logs and the ingress filter chain.
- UMA permission checks migrated to response-mode=decision (MODSIDECAR-182);
  Keycloak error handling is sensitive to Keycloak version.
- Native (GraalVM) build breaks on missing reflection registration; routing of
  `multiple`-type interfaces and GET-with-body had dedicated fixes.
- Config is env-var driven; secure-store key uses `SECURE_STORE_ENV`, not
  `ENV` — a recurring misconfiguration.

**folio-keycloak**
- Performance and cache tuning is an ongoing theme (cache sizing/config via
  env vars, HA cluster join issues during deploys).
- Version upgrades ripple across the whole repo set (sidecar, managers,
  poc-tools) — verify admin-client permissions and token flows after any bump.

**mgr-tenants**
- Owns tenant + Keycloak realm lifecycle: realm session timeouts, lightweight
  tokens for clients, Kafka topic deletion on tenant delete. Startup failures
  are usually environment/secure-store/Keycloak connectivity, not code.
- Tenants with active entitlements cannot be deleted (MGRTENANT-17) — expected
  behavior, not a bug.

**mgr-tenant-entitlements**
- The hardest part is the module/application **dependency tree**: cross-app
  dependency validation (MGRENTITLE-113/118), optional dependencies, upgrade
  impact validation (MGRENTITLE-68). "Cannot entitle due to dependency issue"
  is a data/descriptor problem more often than a code problem.
- Entitlement runs as a staged flow (flow engine): on failure inspect flow
  stages; concurrent Kafka topic creation caused intermittent errors
  (MGRENTITLE-135); long-running flows need token refresh (MGRENTITLE-141).

**mod-roles-keycloak**
- Capability/permission mapping is the core complexity: duplicated
  capabilities by permission name, dedup/migration machinery, race condition
  leaving default loadable-role permissions without capabilities during tenant
  init (MODROLESKC-347). Kafka listener processes capability events —
  event-driven timing matters in tests.
- Keycloak record cleanup on role removal has had gaps (MODROLESKC-384) —
  check both DB and Keycloak state when debugging.

**mod-users-keycloak**
- Dual-write surface: FOLIO user store + Keycloak realm users must stay in
  sync (system users, `_self` endpoint). Most changes are integration-heavy —
  favor ITs with `@KeycloakRealms` fixtures.

**mod-scheduler**
- Two schemas: its own Liquibase changelog plus a separate Quartz changelog —
  do not mix them. Timer edge cases (missing/unspecified timer type) are a
  known review focus.
