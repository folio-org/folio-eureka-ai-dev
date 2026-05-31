---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior in FOLIO modules, Keycloak integration, or Eureka infrastructure — before proposing any fixes. Enforces root-cause investigation over symptom patching.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
  source: adapted from obra/superpowers (https://github.com/obra/superpowers)
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue in the FOLIO/Eureka codebase:
- Test failures (unit, integration, API)
- Bugs in FOLIO modules or Eureka service discovery
- Unexpected behaviour in Keycloak authentication flows
- Performance problems in Spring Boot services
- Build failures (Maven, Docker, CI)
- Integration issues between FOLIO modules
- Liquibase migration errors

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- A "just one quick fix" seems obvious
- You've already tried multiple fixes that haven't worked
- The issue spans multiple FOLIO modules or service boundaries
- You don't fully understand the interaction between components

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - Read stack traces completely, including Spring framework layers
   - Note line numbers, file paths, error codes, HTTP status codes
   - For Keycloak issues, inspect the full OAuth2/OIDC error chain

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps (API call, UI action, background job)?
   - Does it happen every time or only under certain conditions?
   - If not reproducible → gather more data, don't guess

3. **Check Recent Changes**
   - What changed that could cause this?
   - `git diff`, recent commits, dependency version bumps
   - New Liquibase changesets, configuration changes, Keycloak realm updates
   - Environmental differences (local vs CI vs staging)

4. **Gather Evidence in Multi-Component FOLIO Systems**

   **FOLIO is a multi-module, multi-service system. ALWAYS instrument at each boundary:**

   ```
   For EACH component boundary (e.g. API Gateway → FOLIO Module → DB):
     - Log what data enters the component
     - Log what data exits the component
     - Verify tenant context propagation (X-Okapi-Tenant header)
     - Verify token validity and claims (X-Okapi-Token)
     - Check database connection pool and schema visibility

   Run once to gather evidence showing WHERE it breaks
   THEN analyse evidence to identify the failing component
   THEN investigate that specific component
   ```

   **Example (Eureka module authentication flow):**
   ```bash
   # Layer 1: Incoming request headers
   echo "=== Okapi headers ==="
   echo "Tenant: $X_OKAPI_TENANT"
   echo "Token present: ${X_OKAPI_TOKEN:+YES}${X_OKAPI_TOKEN:-NO}"

   # Layer 2: Keycloak token introspection
   curl -s -X POST \
     "$KEYCLOAK_URL/realms/$TENANT/protocol/openid-connect/token/introspect" \
     -d "token=$X_OKAPI_TOKEN&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET" \
     | jq '{active, exp, preferred_username}'

   # Layer 3: Module-level permissions check
   # Verify the folio_${tenant} schema is accessible
   psql -U $DB_USER -d $DB_NAME -c "SET search_path TO folio_${TENANT}; SELECT current_schema();"

   # Layer 4: Actual business logic
   # Check relevant table state
   psql -U $DB_USER -d $DB_NAME -c "SET search_path TO folio_${TENANT}; SELECT * FROM <table> LIMIT 5;"
   ```

   **This reveals:** Which layer fails (headers ✓, token ✓, schema ✗ → DB schema issue)

5. **Trace Data Flow**

   **WHEN error is deep in the call stack:**
   - Where does the bad value originate?
   - What called this with the bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom
   - In FOLIO: trace back through the module chain, not just within one service

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in the same or another FOLIO module
   - What works in a comparable module that's broken here?

2. **Compare Against References**
   - If implementing a FOLIO interface, read the interface definition completely
   - Don't skim — read every field, every constraint
   - Understand the expected behaviour before attempting a fix

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other FOLIO modules or Eureka services does this depend on?
   - What Keycloak realm configuration does it assume?
   - What Liquibase migration state does it require?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test the hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form a NEW hypothesis
   - DON'T stack more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help or research more

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Prefer a unit test or integration test using the existing FOLIO testing patterns
   - MUST exist before fixing

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved in the full module context?

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyse with new information
   - **If ≥ 3: STOP and question the architecture**
   - Don't attempt Fix #4 without discussing the design

5. **If 3+ Fixes Failed: Question Architecture**

   **Patterns indicating an architectural problem in FOLIO context:**
   - Each fix reveals new coupling between modules
   - Fixes require changes across multiple module boundaries
   - Each fix creates new failures in other modules

   **STOP and question fundamentals:**
   - Is this FOLIO interface implementation fundamentally sound?
   - Are we working around a known Eureka limitation?
   - Should we refactor the module contract vs. continue fixing symptoms?

   **Discuss with your team before attempting more fixes.**

## Red Flags — STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "It's probably a Keycloak config issue, let me just reset the realm"
- "I don't fully understand but this might work"
- "One more fix attempt" (when already tried 2+)
- Each fix reveals a new problem in a different module

**ALL of these mean: STOP. Return to Phase 1.**

## Common Rationalisations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple bugs have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write the test after confirming the fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |
