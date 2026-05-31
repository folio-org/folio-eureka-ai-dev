---
name: writing-plans
description: Use when turning a chosen approach (from brainstorming or discussion) into a concrete, executable implementation plan for a FOLIO/Eureka feature or change. Produces step-by-step plans that are reviewable, assignable, and safe to hand off.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
  source: adapted from obra/superpowers (https://github.com/obra/superpowers)
---

# Writing Plans

## Overview

A plan converts a chosen approach into a sequence of concrete, verifiable steps.

**Core principle:** A plan is not done until every step has a clear completion criterion and a known risk.

**Violating the letter of this process is violating the spirit of planning.**

## The Iron Law

```
NO STEP WITHOUT A COMPLETION CRITERION
```

If you can't say "this step is done when X", the step is not ready to be executed.

## When to Use

Use after a technical decision has been made (ideally via the `brainstorming` skill) and you need to:
- Turn an architectural decision into concrete implementation tasks
- Plan a FOLIO module feature end-to-end (interface → implementation → tests → deployment)
- Prepare a Keycloak migration or realm configuration change
- Plan a Liquibase schema migration across tenant environments
- Define work breakdown for a sprint or GitHub milestone
- Create a checklist for a complex multi-module release
- Document the steps for onboarding a new module into Eureka

**Use this ESPECIALLY when:**
- The feature touches multiple FOLIO modules or services
- Steps must be done in a specific order (migrations before code, interfaces before implementations)
- The work will be split across multiple team members or sessions
- The change is risky and needs an explicit rollback plan
- The feature requires coordinated deployment across modules

## The Five Phases

### Phase 1: Anchor to the Decision

**Before writing any steps:**

1. **State the chosen approach in one sentence**
   - What are we building? For which FOLIO module(s)?
   - What problem does it solve?

2. **List the inputs**
   - What exists today that this plan builds on?
   - Which FOLIO interfaces, module versions, Keycloak realm state, DB schema state are assumed?

3. **List the outputs**
   - What will exist when the plan is complete?
   - What is the observable change from a user/operator perspective?

4. **Identify dependencies and ordering constraints**
   - What must be done before anything else? (e.g., Liquibase migration before code that uses the new column)
   - What can be done in parallel?
   - What depends on external teams, releases, or environment readiness?

### Phase 2: Draft the Steps

**Decompose the work into atomic steps:**

**Rules:**
- Each step must be completable in one focused session (ideally < 2 hours)
- Each step must have exactly one completion criterion
- Steps must be ordered: dependencies first, then their dependants
- No step should depend on a future step being partially done

**Step format:**
```
## Step N: [Action verb] + [Specific target]

**What:** [One sentence describing the concrete change]
**Why:** [One sentence — why this step is needed at this point in sequence]
**Completion criterion:** [Specific, verifiable condition — "tests pass", "migration applied in staging", "Okapi loads the descriptor without error"]
**Risk:** [What could go wrong and how to detect it]
**Rollback:** [How to undo this step if it causes problems]
```

**FOLIO-specific step categories (use as a checklist when drafting):**

```
□ Interface design
  - Define/update FOLIO interface in ModuleDescriptor.json
  - Version bump (patch / minor / major per RFC-0003)
  - Document breaking vs. non-breaking changes

□ API implementation
  - Implement endpoint(s) in the Spring Boot module
  - Wire Folio-Spring-Base annotations correctly
  - Handle tenant context (X-Okapi-Tenant propagation)

□ Database
  - Write Liquibase changeset (addColumn / createTable / createIndex)
  - Confirm changeset is backward-compatible
  - Test migration against existing tenant schemas

□ Keycloak / Auth
  - Define required permissions in ModuleDescriptor.json
  - Update realm configuration if new client scopes are needed
  - Verify token claims flow through to the module correctly

□ Testing
  - Unit tests for new business logic
  - Integration tests for new API endpoints (folio-spring-support patterns)
  - Contract/API tests if interface is published

□ Module descriptor
  - Validate JSON (jq check)
  - Confirm all requires/provides/permissionSets are correct
  - Test Okapi loads the updated descriptor without error

□ Documentation
  - Update CHANGELOG.md
  - Update API docs if interface changed
  - Note breaking changes for consuming modules

□ Deployment / Release
  - Docker image build and push
  - Update module registry version
  - Coordinate with dependent module teams if interface changed
  - Rollback plan documented
```

### Phase 3: Sequence and Dependencies

1. **Draw the dependency graph** (even informally)
   - Which steps MUST precede others?
   - Which steps can run in parallel?

2. **Apply the FOLIO ordering rules:**
   - Liquibase changesets before code that uses the new schema
   - Interface definition before implementation
   - ModuleDescriptor validation before deployment
   - Auth permissions defined before endpoints go live
   - Breaking interface changes coordinated with all consuming modules before release

3. **Mark parallel opportunities**
   - Steps that can be done independently (e.g., unit tests and documentation)
   - Flag them clearly so work can be split across team members

4. **Identify the critical path**
   - Which sequence of dependent steps is longest?
   - Which single step, if delayed, delays everything?

### Phase 4: Risk and Rollback

For each high-risk step, document:

```
Risk: [What could go wrong]
Detection: [How we'd know it went wrong]
Impact: [What breaks if this step fails]
Rollback: [Exact steps to undo]
Mitigation: [How to reduce the risk before attempting]
```

**High-risk categories in FOLIO context:**
- Liquibase migrations on production tenant schemas
- Breaking FOLIO interface changes affecting consuming modules
- Keycloak realm changes affecting active tenants
- Changes to Eureka module registration or metadata
- Multi-module coordinated releases

**Rollback completeness check:**
- Can every destructive step be undone?
- If a Liquibase migration cannot be rolled back, is there a compensating migration ready?
- Is there a feature flag or module version pin to revert to?

### Phase 5: Review the Plan

Before handing the plan off for execution, apply this checklist:

```
□ Every step has a completion criterion
□ Steps are in dependency order
□ No step depends on a future step being partially done
□ Each step is achievable in one focused session
□ High-risk steps have explicit rollback plans
□ Parallel opportunities are marked
□ Critical path is identified
□ FOLIO ordering rules applied (schema → code → descriptor → deploy)
□ Breaking changes documented and consuming modules notified
□ Plan is reviewable by a team member who wasn't in the design discussion
```

If any checkbox fails, revise before executing.

## Plan Output Format

When writing the final plan, use this structure:

```markdown
# Plan: [Feature or Change Name]

## Goal
[One sentence: what will exist when this plan is complete]

## Inputs / Assumptions
- [List current state assumptions]

## Steps

### Step 1: [Action + Target]
- **What:** ...
- **Why:** ...
- **Done when:** ...
- **Risk:** ...
- **Rollback:** ...

### Step 2: ...

(parallel steps grouped and labeled)

## Critical Path
[Sequence of steps on the critical path]

## Open Questions
[Anything that must be resolved before or during execution]
```

## Anti-Patterns

| Pattern | Problem |
|---------|----------|
| Steps with no completion criterion | Can't tell if a step is done — work expands indefinitely |
| "Then implement it" as a step | Too vague — decompose further |
| Skipping rollback planning | First sign of trouble becomes a fire |
| Ordering by convenience, not dependency | Downstream steps fail because upstream wasn't truly done |
| Plan written by one person, executed by another without review | Hidden assumptions cause failures at handoff |
| "We'll figure out testing later" | Testing is part of the plan, not an afterthought |
| Skipping the FOLIO ordering rules | Schema changes after code causes startup failures |

## Quick Reference

| Phase | Key Output | Done When |
|-------|-----------|----------|
| **1. Anchor** | Goal, inputs, outputs, constraints | Problem and scope are unambiguous |
| **2. Steps** | Atomic steps with completion criteria | Every step independently verifiable |
| **3. Sequence** | Ordered dependency graph, parallel paths | No hidden ordering assumptions |
| **4. Risk** | Rollback plan per high-risk step | No destructive step without undo path |
| **5. Review** | Checklist passed | Plan is hand-off ready |
