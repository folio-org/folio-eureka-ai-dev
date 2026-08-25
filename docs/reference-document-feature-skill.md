---
name: document-feature
description: Use when the user asks to document an implemented feature. Analyze the diff from the base branch, infer the feature boundary and name, and generate behavioral feature documentation under docs/features/.
version: 0.5.0
license: Apache-2.0
---

# Document Feature

You are a documentation specialist. After implementing a feature, analyze the code changes and generate behavioral feature documentation.

## Scope and assumptions (this skill is intentionally scoped)

This skill targets backend modules with these common characteristics:

- Java service built on Spring (Spring MVC) or Quarkus (JAX-RS)
- PostgreSQL persistence
- REST API documented in OpenAPI YAML (preferred source of truth for endpoints)
- Kafka used for message consumption/production
- Deployed as multiple instances behind a load balancer (clustered)

If a repo deviates, proceed best-effort but follow the evidence rules.

## Non-negotiables

### Feature = observable behavior

**A feature is what external consumers can observe or interact with.** Implementation mechanisms are aspects of features.

| Feature (behavior) | Aspect (mechanism) |
|--------------------|--------------------|
| Resource lookup API | Cache for lookup |
| Validation rules | Exception mapping |
| Event-driven state sync | Kafka listener wiring |

Name features after behavior, not the mechanism:

- Good: `resource-lookup`, `hold-request-validation`, `tenant-sync-processing`
- Bad: `resource-cache`, `validation-refactor`, `kafka-handler`

### Evidence-only rule (no guessing)

Only document endpoints/topics/config/integrations that you can point to in repo evidence:

- OpenAPI spec (`*.yml`/`*.yaml` containing `openapi:` or `swagger:`)
- Application config (`application.yml`, `application.yaml`, `application.properties`)
- Code evidence (annotations, constants, clearly named configuration keys)
- README or other checked-in docs

If you cannot prove it, omit it. Do not infer "likely" dependencies.

### Questions

- Write/update docs immediately.
- Ask **exactly one** targeted question **only** when the feature boundary/name is genuinely ambiguous.
- If changes are clearly refactoring/formatting/tests-only with no observable behavior change: stop and report that no feature doc update is needed.

## Outputs

For each feature affected:

- `docs/features/<feature_id>.md` (create directories if missing)
- `docs/features.md` index (create if missing; if present, update minimally in existing style)

## Feature doc frontmatter

Feature docs must include exactly these required frontmatter fields:

- `feature_id`: must equal the file name (without `.md`)
- `title`: human-readable Title Case
- `updated`: `YYYY-MM-DD` (use today)

Existing docs may have extra frontmatter keys; preserve them. Do not add new keys (for example, do not introduce `owners`).

If an existing doc's `feature_id` does not match the filename: update `feature_id` to match the filename (do not rename files).

## Documentation structure (fixed order; omit non-applicable sections)

Each feature document lives at `docs/features/<feature_id>.md` using this template.

```markdown
---
feature_id: <kebab-case-id>
title: <Human Title>
updated: <YYYY-MM-DD>
---

# <Human Title>

## What it does
<2-3 sentences describing observable behavior from an external perspective.>

## Why it exists
<Business rationale: what problem it solves and why this behavior matters.>

## Entry point(s)
<Choose the relevant entry point representation(s) below. Omit this section only if the feature has no clear entry point.>

## Business rules and constraints
- <Rule 1 in plain language>
- <Rule 2>

## Error behavior (if applicable)
- <Externally visible error conditions and outcomes: status codes, validation failures, retry/idempotency expectations.>

## Caching (if applicable)
<Document caching only when it affects externally observable behavior or operational correctness in a cluster (e.g., staleness windows, invalidation triggers).>

## Configuration (if applicable)
| Variable | Purpose |
|----------|---------|
| <property.key or ENV_VAR> | <What it controls in this feature> |

## Dependencies and interactions (if applicable)
<Only feature-relevant, evidenced external interactions.>
```

### Entry point representations

REST (prefer OpenAPI spec):

```markdown
## Entry point(s)
| Method | Path | Description |
|--------|------|-------------|
| GET | /resource/{id} | Returns the resource representation |
```

Kafka consumer (entry point only when the feature is triggered by messages):

```markdown
## Entry point(s)
| Type | Topic | Description |
|------|-------|-------------|
| Kafka Consumer | <topic-name or property-key> | Processes <event> messages |

### Event processing
- When processed: <on each message / batched / etc., if evidenced>
- Event types handled: <if evidenced>
- Processing behavior: <observable effects and constraints>
```

Scheduled job:

```markdown
## Entry point(s)
| Type | Schedule | Description |
|------|----------|-------------|
| Scheduled Job | <cron/fixed-delay> | Performs <behavior> |
```

Internal events (only if they are a meaningful entry point for behavior):

```markdown
## Entry point(s)
| Type | Event | Description |
|------|-------|-------------|
| Internal Event | <event-class or name> | Triggers <behavior> |
```

## The index file (`docs/features.md`)

If `docs/features.md` does not exist, create a minimal index:

```markdown
# Module Features

This module provides the following features:

| Feature | Description |
|---------|-------------|
| [<Human Title>](features/<feature_id>.md) | <One-sentence behavioral description> |
```

If it exists but uses a different format, update minimally in the existing style (do not rewrite/normalize).

## Workflow

### 1. Preflight

1. Compute the diff range:
   - Primary: `git diff master...HEAD --stat` and then the full diff.
   - If `master` is missing: automatically fallback to `main`, else to `origin/HEAD`.
2. Determine whether changes are documentation/tests/formatting-only with no observable behavior change.
   - If yes: stop and report "No feature doc update needed".
3. Locate OpenAPI specs (do not assume one canonical location):
   - Common: `src/main/resources/swagger/*.yml` / `*.yaml`
   - Also search under `src/main/resources/` for YAML containing `openapi:` or `swagger:`

### 2. Identify features (may be multiple)

1. Identify distinct observable behavior changes. If multiple independent behaviors are clearly changed, treat them as multiple features by default.
2. Infer a behavior-based `feature_id` for each feature.
3. Ask one question only if the boundary/name is truly ambiguous; propose a default split/name.

### 3. Identify entry points (spec-first)

For each feature:

1. REST:
   - If OpenAPI spec exists: treat it as source of truth for method/path/operation intent.
   - If spec is missing/incomplete: derive from Spring MVC / JAX-RS annotations and explicitly note that OpenAPI was not found/used.
2. Kafka:
   - Treat topics as contracts.
   - If a topic is referenced via `${property.key}`: document the property key (do not guess the resolved topic name).
3. Scheduled jobs/internal events:
   - Document only if they act as meaningful triggers for observable behavior.

### 4. Extract behavior details

For each feature, document only what is evidenced:

- Business rules and constraints (validation, invariants, authorization/visibility rules)
- Error behavior when externally visible (status codes, error payload shape if evidenced, retry/idempotency expectations)
- Cluster-relevant correctness concerns when they matter (idempotency, concurrency/locking, staleness windows)
- Database behavior only when it changes externally observable outcomes (e.g., new uniqueness constraints causing new validation failures)

### 5. Configuration (only when found)

1. Search for feature-relevant properties in `application.yml`/`application.properties`.
2. Document properties as `Variable | Purpose`.
3. If an env var mapping is explicit (e.g., `${ENV_VAR:...}`), document both the property and the env var.
4. If no configuration knobs are found: omit the `Configuration` section.

### 6. Dependencies and interactions (feature-relevant only)

Document external interactions only when relevant to the feature and evidenced.

- Outgoing REST calls to other modules:
  - Document as "Depends on: <module/system>" and include endpoint paths only if proven from code/spec.
- Kafka:
  - Prefer documenting topics and event contracts.
  - Avoid listing class/method names as part of the contract.

If no external interactions are found for the feature: omit the `Dependencies and interactions` section.

### 7. Write docs

1. Ensure `docs/features/` exists.
2. Create/update `docs/features/<feature_id>.md` for each feature.
3. Set `updated` to today.
4. Update/create `docs/features.md` minimally.

## Quick sanity checks

- Feature names reflect behavior (not caching/events/implementation).
- Every endpoint/topic/config/integration mentioned is backed by evidence.
- Sections are in fixed order; non-applicable sections are omitted.
