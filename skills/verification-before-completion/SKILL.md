---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing in any FOLIO module — before committing, pushing, or creating PRs. Requires running actual verification commands and confirming their output before making any success claims. Evidence before assertions, always.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
  source: adapted from obra/superpowers (https://github.com/obra/superpowers)
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures in FOLIO Context

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Unit tests pass | `mvn test` output: 0 failures | Previous run, "should pass" |
| Integration tests pass | `mvn verify -Pintegration` output: 0 failures | Unit tests passing |
| Build succeeds | `mvn clean package` exit 0 | Tests passing, logs look good |
| Liquibase migration applied | Migration script executed + schema confirmed in DB | Script file present |
| Bug fixed | Test reproducing original symptom passes | Code changed, assumed fixed |
| Keycloak config applied | Realm export matches expected JSON | Config file updated |
| API contract met | Module descriptor loaded by Okapi without error | Interface declared in descriptor |
| Agent completed | VCS diff shows actual changes | Agent reports "success" |
| Requirements met | Line-by-line checklist against acceptance criteria | Tests passing |

## FOLIO-Specific Verification Commands

```bash
# Unit tests
mvn test

# Full build with integration tests
mvn clean verify

# Specific module test
mvn test -pl <module-name> -am

# Check Liquibase migration status
mvn liquibase:status -Dliquibase.url=$DB_URL

# Validate module descriptor syntax
jq . src/main/resources/ModuleDescriptor.json > /dev/null && echo "Valid JSON" || echo "INVALID"

# Lint check
mvn checkstyle:check

# Verify Docker image builds
docker build -t test-image . && echo "Build OK" || echo "Build FAILED"
```

## Red Flags — STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Done!", "Fixed!", "All good!")
- About to commit/push/create a PR without running tests
- Trusting agent success reports
- Relying on partial verification (e.g., unit tests only when integration tests are relevant)
- Thinking "just this once"

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Unit tests passed" | Unit tests ≠ integration tests |
| "Agent said success" | Verify independently |
| "The build is slow" | Slow build ≠ skip verification |
| "Partial check is enough" | Partial proves nothing |

## Key Patterns

**Tests:**
```
✅ [Run `mvn test`] [See: BUILD SUCCESS, 0 failures] → "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Build:**
```
✅ [Run `mvn clean package`] [See: BUILD SUCCESS, exit 0] → "Build passes"
❌ "Tests passed" (compilation errors can still exist)
```

**Liquibase migration:**
```
✅ [Run migration] [Query schema] [Confirm table/column exists] → "Migration applied"
❌ "I added the changeset" (without confirming it ran)
```

**Module descriptor:**
```
✅ [Validate JSON] [Check interface version matches dependency] → "Descriptor is valid"
❌ "I updated the version number"
```

**Agent delegation:**
```
✅ Agent reports success → Check `git diff` → Verify actual changes → Report real state
❌ Trust agent report
```

## When To Apply

**ALWAYS before:**
- ANY success or completion claim
- Committing, pushing, or creating a PR
- Marking a JIRA ticket as done
- Moving to the next task
- Delegating follow-up to another agent

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
