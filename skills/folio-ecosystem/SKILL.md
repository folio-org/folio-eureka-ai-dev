---
name: folio-ecosystem
description: >-
  Use when working in any FOLIO platform repository (mod-*, ui-*, mgr-*, edge-*, app-*, stripes-*) —
  starting a task in a module, planning or wrapping up a feature, deciding which team skill applies,
  or needing FOLIO documentation, wiki pages, Eureka platform references, or team/module ownership
  information. Also use when unsure whether the platform is Eureka or legacy Okapi.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
---

# FOLIO Ecosystem

## Overview

You are working in the FOLIO Library Services Platform ecosystem, Eureka era
(Kong gateway → module sidecar → module; Keycloak auth; mgr-* managers).
Okapi is the legacy predecessor — ignore Okapi-era instructions in older docs,
even though `X-Okapi-*` header names survive in Eureka.

Core principle: **do not guess what is already mapped.** Use the verified
resource map instead of guessing URLs, and drive the team's installed skills
proactively instead of waiting to be asked.

## Orchestrate team skills proactively

The FOLIO skill registry (`folio-org/folio-eureka-ai-dev`) covers the
development lifecycle. At the start of a task, enumerate the skills actually
installed on disk (e.g. `.claude/skills/`, `.agents/skills/`) — do not trust a
memorized list.

Invoke the matching skill at the right stage **without the user asking**:

| Stage reached | Invoke |
| --- | --- |
| Ticket/story needed | write-user-story / write-bug |
| Schema/DB change | liquibase-migration |
| Writing/reviewing Java tests | unit-testing |
| Feature implemented | document-feature |
| Preparing PR | write-pr-description |
| Before merge | code-review |
| A skill misbehaved or produced friction | skill-feedback |

Sequence for wrapping up a feature:
document-feature → write-pr-description → code-review, then skill-feedback if
any skill needs improvement. See references/dev-flow.md for details and
trigger examples.

## Find resources, don't guess them

Wiki URLs are frequently restructured; guessed links 404. Use
references/resources.md — a verified map of dev.folio.org, FOLIO wiki
(Eureka architecture, sidecar internals), GitHub, and community channels.

Module ownership questions ("which team owns mod-X?") have exactly one
authoritative source: the responsibility matrix linked in
references/resources.md. Never hardcode team↔module mappings — they change.

## Keep the registry fresh

Skills are installed via `npx skills add folio-org/folio-eureka-ai-dev` and
updated via `npx skills update folio-org/folio-eureka-ai-dev`. If an expected
skill is missing or this flow map disagrees with what is installed, **propose**
the update command to the user — never run it unprompted.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Guessing wiki URLs from memory | Use references/resources.md (legacy `/display/...` links 404) |
| Following Okapi-era docs | Eureka only; Okapi is legacy |
| Waiting for the user to request docs/PR text/review | Invoke lifecycle skills proactively per the table above |
| Hardcoding team/module ownership | Look up the responsibility matrix each time |
