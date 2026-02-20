# Workflow

## 1. Preflight

1. Compute the diff range:
   - Primary: `git diff master...HEAD --stat` and then the full diff.
   - If `master` is missing: automatically fallback to `main`, else to `origin/HEAD`.
2. Determine whether changes are documentation/tests/formatting-only with no observable behavior change.
   - If yes: stop and report "No feature doc update needed".
3. Locate OpenAPI specs (do not assume one canonical location):
   - Common: `src/main/resources/swagger/*.yml` / `*.yaml`
   - Also search under `src/main/resources/` for YAML containing `openapi:` or `swagger:`

## 2. Identify features (may be multiple)

1. Identify distinct observable behavior changes. If multiple independent behaviors are clearly changed, treat them as multiple features by default.
2. Infer a behavior-based `feature_id` for each feature.
3. Ask one question only if the boundary/name is truly ambiguous; propose a default split/name.

## 3. Identify entry points (spec-first)

For each feature:

1. REST:
   - If OpenAPI spec exists: treat it as source of truth for method/path/operation intent.
   - If spec is missing/incomplete: derive from Spring MVC / JAX-RS annotations and explicitly note that OpenAPI was not found/used.
2. Kafka:
   - Treat topics as contracts.
   - If a topic is referenced via `${property.key}`: document the property key (do not guess the resolved topic name).
3. Scheduled jobs/internal events:
   - Document only if they act as meaningful triggers for observable behavior.

## 4. Extract behavior details

For each feature, document only what is evidenced:

- Business rules and constraints (validation, invariants, authorization/visibility rules)
- Error behavior when externally visible (status codes, error payload shape if evidenced, retry/idempotency expectations)
- Cluster-relevant correctness concerns when they matter (idempotency, concurrency/locking, staleness windows)
- Database behavior only when it changes externally observable outcomes (e.g., new uniqueness constraints causing new validation failures)

## 5. Configuration (only when found)

1. Search for feature-relevant properties in `application.yml`/`application.properties`.
2. Document properties as `Variable | Purpose`.
3. If an env var mapping is explicit (e.g., `${ENV_VAR:...}`), document both the property and the env var.
4. If no configuration knobs are found: omit the `Configuration` section.

## 6. Dependencies and interactions (feature-relevant only)

Document external interactions only when relevant to the feature and evidenced.

- Outgoing REST calls to other modules:
  - Document as "Depends on: <module/system>" and include endpoint paths only if proven from code/spec.
- Kafka:
  - Prefer documenting topics and event contracts.
  - Avoid listing class/method names as part of the contract.

If no external interactions are found for the feature: omit the `Dependencies and interactions` section.

## 7. Write docs

1. Ensure `docs/features/` exists.
2. Create/update `docs/features/<feature_id>.md` for each feature.
3. Set `updated` to today.
4. Update/create `docs/features.md` minimally.
