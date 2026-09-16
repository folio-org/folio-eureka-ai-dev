# Workflow

## 1. Preflight

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

1. Use the documentation structure chosen under Outputs. Create `docs/features/` only when that is the chosen layout.
2. In the `docs/features/` layout: create/update `docs/features/<feature_id>.md` for each feature, set `updated` to today, and update/create `docs/features.md` minimally.
3. In another established layout: update or add the matching document and its index in that layout's existing style.
