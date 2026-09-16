---
name: document-feature
description: Use when the user asks to document an implemented feature, before or after its changes are committed, in the repository's existing documentation structure or under docs/features/ when none exists.
version: 0.6.0
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

Write where the repository already documents behavior. Before writing, look for an established
structure: `docs/features/` with `docs/features.md`, or another feature, behavior or API
documentation layout under `docs/`, `doc/`, or the README.

- **`docs/features/` already exists, or there is no established structure:** for each affected
  feature, write `docs/features/<feature_id>.md` (create directories if missing) and the
  `docs/features.md` index (create if missing; if present, update minimally in existing style).
- **Another structure is established:** update or add the matching document in that structure,
  following its file naming, headings, and index. Do not create `docs/features/` next to it. Use
  the section content below, adapted to that structure's headings.
- **Two structures are plausible:** ask one question, proposing the one you would use.

## Feature doc frontmatter

In the `docs/features/` layout, feature docs must include exactly these required frontmatter fields:

- `feature_id`: must equal the file name (without `.md`)
- `title`: human-readable Title Case
- `updated`: `YYYY-MM-DD` (use today)

Existing docs may have extra frontmatter keys; preserve them. Do not add new keys (for example, do not introduce `owners`).

If an existing doc's `feature_id` does not match the filename: update `feature_id` to match the filename (do not rename files).

## Documentation structure (fixed order; omit non-applicable sections)

In the `docs/features/` layout, each feature document lives at `docs/features/<feature_id>.md` using this template.

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

1. Resolve the base, first match wins:
   - a base the user or the calling workflow named (for example `release/2.x`);
   - the base of the branch's existing PR, or one stated in the active task context (`gh pr view --json baseRefName -q .baseRefName` is optional; skip it if `gh` is missing or finds no PR);
   - fallback only: `git symbolic-ref --short refs/remotes/origin/HEAD`, else `origin/master`, else `origin/main`.
   Prefer `origin/<name>` over a local branch and keep names with `/` whole. An `@{upstream}` that names another branch (not `origin/<current branch>`) is a base to confirm before the fallback. If you fell back and the branch, upstream, or task points to maintenance or release work, ask for the base. Then `MB=$(git merge-base <base> HEAD)`.
2. Collect the change candidate without committing, staging, stashing, or resetting anything:
   - Clean working tree (committed mode): `git diff <base>...HEAD --stat`, then the full diff.
   - Local changes (working-tree mode): `git diff $MB --stat`, then `git diff $MB` (final tracked content: committed, staged, and unstaged), plus `git ls-files --others --exclude-standard`; read untracked source files in full.
   - Document only changes that belong to the feature. Name files that look unrelated or pre-existing in your report instead of documenting them.
   - No commits since `MB` and a clean tree: report that there are no changes to document against `<base>`. This does not mean the base is wrong.
3. Determine whether changes are documentation/tests/formatting-only with no observable behavior change.
   - If yes: stop and report "No feature doc update needed".
4. Locate OpenAPI specs (do not assume one canonical location):
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

1. Use the documentation structure chosen under Outputs. Create `docs/features/` only when that is the chosen layout.
2. In the `docs/features/` layout: create/update `docs/features/<feature_id>.md` for each feature, set `updated` to today, and update/create `docs/features.md` minimally.
3. In another established layout: update or add the matching document and its index in that layout's existing style.

## Quick sanity checks

- Feature names reflect behavior (not caching/events/implementation).
- Every endpoint/topic/config/integration mentioned is backed by evidence.
- Sections are in fixed order; non-applicable sections are omitted.
- Docs were written in the repository's existing documentation structure, or in `docs/features/` only when none existed.
