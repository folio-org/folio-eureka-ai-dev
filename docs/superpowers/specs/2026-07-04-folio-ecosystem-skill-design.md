# folio-ecosystem Skill — Design

Date: 2026-07-04
Status: approved (brainstorming session), implementation via writing-skills TDD
Amended 2026-07-04 after RED phase: scope narrowed — see "RED results and
narrowed scope" at the end.

## Goal

(Re-scoped 2026-07-06, operator decision — supersedes the narrowed scope below.)

An onboarding bootstrap for AI agents assisting **anyone starting to work with
FOLIO — developer, tester, or product owner**, in any team. The skill
initializes platform understanding (what FOLIO is, the Eureka core, where the
resources are) and guides the agent through a role-appropriate flow:

- developer → platform architecture, module conventions, dev lifecycle skills
  (tests, docs, PR, review), Eureka dev-flow reference;
- tester → bug reporting flow (write-bug), environment/platform orientation;
- product owner → story writing flow (write-user-story), wiki/ownership
  navigation (responsibility matrix).

The agent determines the user's role from the task context or asks.

Verification 2026-07-06: PO and QA role scenarios ran in a clean environment
against the existing skill — both passed (6/6 scenarios total across roles).
Consequence: no role-specific restructuring needed; role behavior emerges from
resources.md + the registry skills + model priors. Applied instead:
(a) description broadened with role-trigger vocabulary (onboarding, story,
defect, ownership); (b) a compact "Platform facts newcomers get wrong" section
(sidecar-side authorization, eventual-consistency 403 after entitlement,
capabilities not auto-added to roles, release→descriptor→entitlement path)
replaces the originally planned full architecture.md — the facts tests showed
to be load-bearing, without duplicating model priors or creating a rot-prone
architecture retelling.

## Problem

Agents in FOLIO module repos today:

1. Do not know the platform: Eureka request path (Kong → sidecar → module),
   mgr-* managers, Keycloak, Kafka — and make wrong assumptions about how a
   module is embedded in the platform.
2. Do not know FOLIO conventions: module descriptors, interfaces, tenant API,
   folio-spring-base, repo taxonomy — they write "generic Java" instead of
   "FOLIO module".
3. Do not know where to look: wiki, dev.folio.org, team/module ownership.
4. Do not use the registry skills (code-review, unit-testing, liquibase-migration,
   write-pr-description, document-feature, write-user-story, write-bug,
   skill-feedback) unless the user invokes them manually.

## Decisions

- **Delivery mechanism:** a skill in this registry with a broad trigger
  ("any development work in a FOLIO module"), installed via
  `npx skills add folio-org/folio-eureka-ai-dev`. The description line itself
  acts as an ambient "you are in FOLIO" beacon at agent startup.
- **Granularity:** one skill `folio-ecosystem` with `references/`
  (progressive disclosure), not several skills.
- **Scope:** Eureka-era only. Okapi is mentioned in one line as legacy
  predecessor so agents are not confused by older docs. Depth is backend/Java
  (profile of the rest of the registry); UI/Stripes covered as orientation only.
- **Team-agnostic:** content must serve any FOLIO developer. Team/module
  ownership is volatile — never hardcoded; the skill points to the wiki
  responsibility matrix and dev.folio.org instead.
- **Orchestration:** SKILL.md carries a lifecycle flow map
  (stage → registry skill) and instructs the agent to invoke registry skills
  proactively at the right stage, without the user asking:
  story/bug → write-user-story / write-bug; DB change → liquibase-migration;
  tests → unit-testing; feature docs → document-feature; PR →
  write-pr-description; review → code-review; skill misbehaved → skill-feedback.
- **No description duplication:** canonical skill descriptions live in each
  skill's frontmatter. The flow map lists only name, position in flow, and 1–2
  trigger-phrase examples. The agent is instructed to enumerate installed
  skills from disk rather than trust a hardcoded list.
- **Feedback:** no new skill; the existing `skill-feedback` is wired in as the
  terminal step when a registry skill performs badly.
- **Freshness:** SKILL.md documents `npx skills update
  folio-org/folio-eureka-ai-dev`; on catalog/flow-map mismatch the agent
  proposes the update to the user, never runs it unprompted.

## Structure

```
skills/folio-ecosystem/
├── SKILL.md                    # trigger + compact core: what FOLIO/Eureka is,
│                               # behavior rules, lifecycle flow map, freshness
└── references/
    ├── architecture.md         # Eureka: Kong → sidecar → module, mgr-*, Keycloak, Kafka
    ├── module-conventions.md   # repo taxonomy, backend module anatomy, descriptors,
    │                           # tenant API, folio-spring-base
    ├── resources.md            # curated map: dev.folio.org, wiki spaces,
    │                           # team↔module responsibility matrix, community
    └── dev-flow.md             # dev lifecycle and skill-orchestration rules
```

## Testing (writing-skills TDD)

- RED: baseline subagent scenarios without the skill — platform knowledge
  (request path/auth context), conventions (DB migration planning),
  orchestration (wrap-up after feature). Document failures verbatim.
- GREEN: write skill addressing observed failures; re-run scenarios with the
  skill present.
- REFACTOR: counter new rationalizations, CSO check on description, token
  budget check.

## Risks

- Broad trigger may not fire in every agent; mitigated by the description
  beacon and (optionally, later) a one-line AGENTS.md pointer.
- Flow map needs a touch when a new skill enters the registry; mitigated by
  dynamic on-disk discovery instruction.
- External wiki/dev.folio.org links can rot; resources.md is a curated map,
  not content — links verified at authoring time.

## RED results and narrowed scope (amendment, 2026-07-04)

Four baseline scenarios ran without the skill (three in the maintainer's
workspace, one in an isolated single-repo clone with no workspace context, no
web, no installed skills). All four passed: a strong agent derived the Eureka
request path, module conventions, descriptor/interface-bump steps, entitlement
rollout, and pre-PR process from model priors plus in-repo evidence
(README, descriptors, PR template). Teaching platform architecture and module
conventions therefore has no demonstrated failing test and was cut.

What agents demonstrably cannot derive: verified documentation URLs (research
hit a dead legacy wiki link and a page unreadable via plain fetch) and the
discipline of proactively sequencing registry skills.

Shipped scope: `SKILL.md` + `references/resources.md` (verified resource map)
+ `references/dev-flow.md` (lifecycle orchestration rules).
`references/architecture.md` and `references/module-conventions.md` were
dropped; research drafts are preserved outside the repo if ever needed.

## Trigger/value test round (amendment, 2026-07-06)

All prior scenario tests told the agent skills were installed. This round
tested natural triggering: clean mod-users-keycloak clone, registry skills in
`.claude/skills`, headless Claude Code 2.1.201, prompts never mentioning
skills. Scenarios and stand recipe persisted in docs/skill-test-scenarios.md.

Findings:

- **Value confirmed** (forced-load A/B, m2m-401 defect scenario): with
  folio-ecosystem loaded, 3/3 reports attributed the 401 to the sidecar
  (system-user egress token / bootstrap declaration) and redirected ownership
  away from the target module's team; without it, 3/3 reports gave a generic
  token-timing hypothesis addressed to the wrong team.
- **Natural triggering failed on the defect scenario**: write-bug's more
  specific description intercepted 3/3; folio-ecosystem co-triggered 0/3, so
  its platform facts never loaded. On the pure platform-triage scenario it
  triggered 2/3 (the miss answered correctly from model priors — harmless).

Rejected fixes (operator decisions): back-references from other registry
skills to folio-ecosystem (skill may be absent on a given system; unwanted
coupling) and AGENTS.md pointers in module repos (files vary or don't exist;
distribution is skills-only — the agentskills.io spec is cross-tool).

Applied fix (v2.2.0): description-only CSO change — opening rewritten to
"Load this first, at the start of any session in a FOLIO platform
repository… before or alongside any other FOLIO skill". A/B against a
narrower "always load before triaging any defect" variant, N=5 each: both
reached 5/5 co-trigger with correct substance; the primacy wording won as it
generalizes to interception by any specific skill, not just write-bug.
Regression on the platform-triage scenario: 3/3 (baseline 2/3). Skill body
untouched.

## Re-scope to orientation-only (amendment, 2026-08-26, v3.0.0)

Operator decision. Reference point: superpowers' `using-superpowers` skill,
which bootstraps context but *mandates* invoking the framework's own skills
("if there is even a 1% chance a skill might apply, you MUST invoke it").
We deliberately do not want that pressure in this registry.

Removed from the skill:

- Phase 2 skill routing — the stage→skill table with "invoke the matching
  skill at the right stage **without the user asking**".
- `references/dev-flow.md` in full (orchestration table, "Reaching a stage IS
  the trigger", proactivity rules). Its only non-orchestration content, the
  wrap-up sequence, now lives inline in `roles/dev-backend.md`.
- Phase 3 — the end-of-session `skill-feedback` offer. `skill-feedback` is
  still documented in docs/skill-engineering.md as a maintainer practice.

Added instead — the skill now answers "what is FOLIO, where am I, what are
the principles, where do I get more context":

- what FOLIO is (one paragraph) and the repo prefix taxonomy;
- Kafka added to the component table;
- a **"Digging into a specific module" ladder** in `references/resources.md`:
  README → module descriptor → API spec → NEWS.md → targeted `src/` search →
  dependency sources by `pom.xml` version → responsibility matrix → `ui-*`
  `okapiInterfaces`/`permissionSets`; plus where cross-repo detail lives
  (sidecar wiki page, docs/eureka-dev-flow.md, owning team's Jira/space);
- a "Going deeper" section in SKILL.md pointing at the three deeper sources;
- a non-imperative "Related skills" paragraph: the registry ships task
  skills, enumerate them from disk, use one if it fits.

Evidence note: the 2026-07-04 RED cut generic architecture/conventions
content because baselines derived it unaided. The added context is therefore
biased toward what later tested load-bearing — verified links and non-obvious
invariants — plus navigation guidance, which is by construction non-derivable
(it names files and pages, not concepts).

**Description deliberately untouched** except for dropping the routing
parenthetical. Its primacy wording ("Load this first… before or alongside any
other FOLIO skill") is the outcome of the 2026-07-06 N=5 A/B (co-trigger
0/3 → 5/5, platform-triage 2/3 → 3/3) and must not be softened to match the
gentler body; loading early and forcing other skills are different mechanisms.

Regression suite unchanged (docs/skill-test-scenarios.md): scenarios A and B
test triggering and platform-fact value, neither of which this re-scope
touches. Re-run both before releasing v3.0.0.
