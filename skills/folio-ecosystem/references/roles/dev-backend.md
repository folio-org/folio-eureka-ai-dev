# Backend Developer Rules (Java/Eureka modules)

Load this when doing backend development work in a FOLIO module. Deep
endpoint/platform reference: `docs/eureka-dev-flow.md` in the registry repo
(fetchable from folio-org/folio-eureka-ai-dev) — load only when needed.

## Finding code

- Targeted search only (symbol/keyword in `src/main/java`, `src/test/java`,
  `descriptors/`, `src/main/resources`); no open-ended directory dumps.
- Never read `target/`, generated sources, or unpacked jars. Library
  internals (folio-spring-support, applications-poc-tools): read the exact
  dependency version from `pom.xml`, then that repo/tag on GitHub, or ask the
  user to run `mvn dependency:sources`.

## Making changes

- API-first: change the OpenAPI spec (`src/main/resources/swagger.api/`),
  run `mvn clean generate-sources`, then controller → service.
- New/changed routes: update `descriptors/ModuleDescriptor-template.json`
  (handler + permissions) and **bump the provided interface version**
  (minor for additive changes).
- DB changes: the `liquibase-migration` skill covers the conventions if it is
  installed; mod-scheduler note — its Quartz changelog is separate, do not mix.
- Add a `NEWS.md` entry with the Jira key.

## Tests

- Unit: `@Tag("unit")`, Mockito strict stubbing (details in the
  `unit-testing` skill). Run: `mvn test -Dgroups=unit`.
- Integration: `*IT.java` extending the module's `BaseIntegrationTest`
  (shared extensions: `@EnablePostgres`, `@EnableKafka`, `@EnableWireMock`,
  `@KeycloakRealms`, `@WireMockStub` from folio-backend-testing).
- Single IT class: `mvn failsafe:integration-test -Dit.test=**/<Class>.java`
  — do not assume `mvn verify -Dit.test=...` narrows the suite.
- Base classes clean caches in `@BeforeEach` — mirror this for new cached
  logic.

## Wrap-up

Verify the build and tests before calling the work done. The usual next steps
— feature docs, PR description, review — have registry skills
(`document-feature`, `write-pr-description`, `code-review`); use them if they
are installed and the stage applies. Do not commit or push unless asked.
