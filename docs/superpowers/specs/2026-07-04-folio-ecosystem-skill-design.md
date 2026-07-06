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
Platform-understanding content (architecture reference) is included by
operator decision, overriding the earlier TDD-based cut: strong models derive
it, but the skill also serves weaker agents and non-developer roles.

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
