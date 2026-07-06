# Skill Test Scenarios (regression suite)

Clean-environment scenarios for benchmarking registry skills, primarily
`folio-ecosystem` triggering and value. Method: docs/skill-engineering.md
(N≥5 runs per variant, LLM behavior is stochastic).

## Test stand

```bash
STAND=$(mktemp -d)/mod-users-keycloak
git clone --depth 1 <mod-users-keycloak> "$STAND"        # any FOLIO module repo works
mkdir -p "$STAND/.claude/skills"
cp -R <this-repo>/skills/. "$STAND/.claude/skills/"
```

The stand must contain no workspace-level CLAUDE.md/AGENTS.md that mentions
skills. Prompts must never mention skills — that is the point of the test.

## Running (headless Claude Code)

```bash
cd "$STAND"
claude -p "<scenario prompt>" --output-format stream-json --verbose --max-turns 12 > run.jsonl
```

Detect skill invocations in the transcript:

```bash
grep -o '"name":"Skill","input":{"skill":"[^"]*"' run.jsonl
```

## Scenario A — platform triage (403 after entitlement)

Prompt:

> We just enabled the users application for a new tenant, but a user who has
> the correct role still gets 403 on GET /users-keycloak/users right after
> enablement. Where would you start triaging this?

Grading:
- Trigger: `folio-ecosystem` invoked without being named.
- Substance: answer names asynchronous capability propagation
  (Kafka → mod-roles-keycloak) and capability↔role assignment as first
  hypotheses, before suspecting module code.

Baseline 2026-07-06 (Claude Code 2.1.201): trigger 2/3; the miss still
answered correctly from model priors — outcome not harmed.

## Scenario B — defect report (intermittent m2m 401)

Prompt:

> POST /users-keycloak/users intermittently returns 401 when called from
> another module. I need to report this as a defect to the owning team -
> draft the report for me.

Grading:
- Co-trigger: `folio-ecosystem` invoked in addition to `write-bug`.
- Substance (the value test): the report attributes the 401 to the sidecar
  layer (module handler never ran), names the system-user egress token /
  "system user required" bootstrap declaration as the primary hypothesis,
  and does NOT route the bug to the target module's team by default.

Baseline 2026-07-06: `write-bug` intercepts 3/3; `folio-ecosystem`
co-trigger 0/3; all baseline reports gave a generic token-timing hypothesis
addressed to the wrong team. With the skill force-loaded: 3/3 correct
cause and ownership — the skill adds value whenever it loads.

## When to re-run

- After any edit to `folio-ecosystem` description or platform facts.
- After a major model or Claude Code upgrade.
- Before releasing a registry version consumed via `npx skills add/update`.
