---
name: receiving-code-review
description: Use when receiving code review feedback on FOLIO module PRs — before implementing suggestions, especially if feedback seems unclear or technically questionable. Requires technical evaluation and verification, not performative agreement or blind implementation.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
  source: adapted from obra/superpowers (https://github.com/obra/superpowers)
---

# Receiving Code Review

## Overview

Code review requires technical evaluation, not emotional performance.

**Core principle:** Verify before implementing. Ask before assuming. Technical correctness over social comfort.

## The Response Pattern

```
WHEN receiving code review feedback on a FOLIO PR:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase and FOLIO conventions
4. EVALUATE: Technically sound for THIS module and THIS version?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## Forbidden Responses

**NEVER:**
- "You're absolutely right!" (performative, adds no value)
- "Great point!" (same)
- "Let me implement that now" (before understanding and verifying)

**INSTEAD:**
- Restate the technical requirement in your own words
- Ask clarifying questions if anything is unclear
- Push back with technical reasoning if the suggestion is wrong for this context
- Just fix it and show the change (actions > words)

## Handling Unclear Feedback

```
IF any item is unclear:
  STOP — do not implement anything yet
  ASK for clarification on ALL unclear items before starting

WHY: Items may be related. Partial understanding = wrong implementation.
```

**Example:**
```
Reviewer: "Fix issues 1-5"
You understand 1, 2, 4. Unclear on 3 and 5.

❌ WRONG: Implement 1, 2, 4 now; ask about 3 and 5 later
✅ RIGHT: "Understood items 1, 2, 4. Need clarification on 3 and 5 before proceeding."
```

## FOLIO-Specific Verification Checklist

Before implementing any review suggestion, check:

### API / Interface Changes
- Does the suggested change break the published FOLIO interface version?
- Does it require a major/minor interface version bump per [FOLIO versioning rules](https://dev.folio.org/guidelines/contributing)?
- Does it affect the ModuleDescriptor — and if so, is the descriptor updated?

### Keycloak / Auth
- Does the suggestion affect authentication or authorisation flows?
- Does it require changes to realm configuration or client scopes?
- Does it remain compatible with the tenant-scoped Keycloak realm model?

### Database / Liquibase
- Does the suggestion require a new Liquibase changeset?
- Is the changeset backward-compatible with existing tenant schemas?
- Does the suggestion affect multi-tenant schema isolation (`folio_{tenant}` prefix)?

### Eureka Service Discovery
- Does the suggestion affect module registration or Eureka metadata?
- Is it compatible with the current Eureka client configuration?

### Testing
- Does the suggested implementation have test coverage?
- Are existing tests still valid after the change?
- Does it require new integration test scenarios?

## Source-Specific Handling

### From the PR Author / Requester
- Implement after understanding the full scope
- Still ask if anything is unclear
- No performative agreement — skip to action or technical acknowledgment

### From External Reviewers
```
BEFORE implementing:
  1. Is the suggestion technically correct for this FOLIO version?
  2. Does it break existing functionality or interfaces?
  3. Is there a reason the current code works the way it does?
  4. Is it compatible across supported environments (local, CI, staging)?
  5. Does the reviewer have full context of the module's purpose?

IF suggestion seems wrong:
  Push back with technical reasoning and references (RFC, FOLIO dev guide, etc.)

IF can't easily verify:
  Say so: "I can't verify this without running the full integration suite. Should I proceed or investigate first?"

IF it conflicts with prior architectural decisions:
  Stop and discuss before implementing
```

## YAGNI Check for Suggested Features

```
IF reviewer suggests adding new functionality:
  Check: Is this feature called or required by any existing FOLIO interface?

  IF not referenced: Raise YAGNI concern — "This doesn't appear to be required by
    any current interface contract. Should we add it now or defer?"
  IF required: Implement properly with tests
```

## Implementation Order

```
FOR multi-item review feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     a. Blocking issues (build failures, interface breaks, security)
     b. Simple fixes (typos, imports, formatting)
     c. Complex fixes (logic changes, refactoring)
  3. Test each fix individually before moving to the next
  4. Verify no regressions (`mvn test` or `mvn verify`)
  5. Update PR description if scope changed
```

## When To Push Back

Push back when:
- Suggestion breaks a published FOLIO interface
- Reviewer lacks context of tenant-scoped multi-module architecture
- Violates YAGNI — adds unused functionality
- Technically incorrect for this Java/Spring Boot stack
- Creates backward-incompatible Liquibase changes
- Conflicts with established Eureka team architectural decisions

**How to push back:**
- Use technical reasoning, not defensiveness
- Reference FOLIO dev guidelines, RFCs, or existing patterns where relevant
- Ask specific questions
- Involve the team if architectural impact is unclear

## Acknowledging Correct Feedback

When feedback IS correct:
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch — [specific issue]. Fixed in [file:line]."
✅ [Just fix it and show the change]

❌ "You're absolutely right!"
❌ "Great catch, thanks!"
❌ Any expression of gratitude — actions speak louder
```

## GitHub Thread Replies

When replying to inline review comments on GitHub, reply in the comment thread directly — do NOT add a top-level PR comment.

```bash
# Resolve a thread after fixing
gh api repos/folio-org/<repo>/pulls/<pr>/comments/<id>/replies \
  -f body="Fixed in <commit-sha>: <brief description>"
```

## The Bottom Line

**External review feedback = suggestions to evaluate, not orders to follow.**

Verify. Question if needed. Then implement.

No performative agreement. Technical rigour always.
