# Common Pitfalls

## Pitfall 1: Technical Task With No Stated Value

**Bad:**
```
As a developer, I want to upgrade Spring Boot to version 3.2
So that we use the latest framework
```

**Better:**
```
Purpose: Upgrade Spring Boot from 3.0 to 3.2 to address critical security
vulnerabilities (CVE-2024-XXXX) and enable new features needed for upcoming work.

Requirements:
- Upgrade Spring Boot dependency to 3.2.x
- Update all affected dependencies
- Verify all tests pass

Note: This is a technical enabler story, not user-facing.
```

Why: the problem was never that the work is technical — technical enablers are legitimate stories. The problem is a hollow persona wrapper standing in for the actual outcome and its value. State the outcome directly; do not invent an end-user persona for work that has none.

## Pitfall 2: Vague Acceptance Criteria

**Bad:**
```
- System performs well
- UI looks good
- Users can complete the task
```

**Better:**
```
- Given 1000 concurrent users
  When searching for records
  Then results return in under 2 seconds (p95)

- Given the search results page
  When viewport is 320px wide (mobile)
  Then all content is readable without horizontal scroll
```

## Pitfall 3: Missing Error Scenarios

**Bad:**
```
Requirements:
- User can upload CSV file
- System imports data from CSV
```

**Better:**
```
Requirements:
- User can upload CSV file (max 10MB)
- System validates CSV format and column headers
- System imports valid data from CSV
- System reports validation errors for:
  - Invalid file format (not CSV)
  - Missing required columns
  - Data type mismatches
  - Duplicate records
  - File too large (>10MB)
- User can download error report for failed imports
```

## Pitfall 4: Solution Specified Too Early

**Bad:**
```
Requirements:
- Implement Redis cache using Lettuce client
- Cache keys must follow pattern: "user:{id}:profile"
- Set TTL to 3600 seconds
```

**Better:**
```
Requirements:
- System shall cache user profile data to reduce database load
- Cache shall expire after reasonable time to ensure data freshness
- Cache invalidation shall occur when profile is updated

Technical Approach:
Consider Redis or in-memory cache. Coordinate with infrastructure team.
```

**Important limit:** this pitfall is about inventing an implementation the user never chose. If the user or the team has agreed a technical constraint — a specific timeout value, a required protocol, a mandated library — keep it in Requirements. Do not strip an agreed constraint just because it looks like implementation detail.

## Pitfall 5: Including Unnecessary Sections or Details

**Bad:**
```
Non-Functional Requirements:
1. Performance: Audit field updates are very fast (negligible overhead)
2. Backward Compatibility: API is backward compatible

Out of Scope:
- Full audit history table
- Audit export API

Testing Guidance:
Unit Testing:
- Mock FolioExecutionContext
- Test entity extends AuditableEntity

Test Data:
UUID USER_A = "11111111-1111-1111-1111-111111111111"
```

**Better:**
```
Non-Functional Requirements:
1. Data Integrity: created_date shall have NOT NULL constraint

(No "Out of Scope" — none of the items clarify genuine ambiguity)

Testing Guidance:
Manual Testing Scenario 1: Create and Update Timer
1. POST /scheduler/timers with valid descriptor
2. Verify response includes audit fields with your user ID
3. Authenticate as different user and PUT to update
4. Verify createdBy unchanged, updatedBy shows new user
```

The manual API walkthrough above suits an API change. It is not the required shape for a library change or for discovery work — see the verification table in the main skill.

**Rules:**
- Remove performance NFRs when impact is negligible
- Remove Out of Scope when items don't clarify genuine ambiguity
- Remove unsupported boilerplate compatibility notes; keep a compatibility requirement that is significant or was explicitly stated, in Requirements
- Naming the level of automated verification is fine ("covered by contract tests"); detailed unit test specifications, mock setup, and fixtures belong in the implementation plan
- Move test data details to the implementation plan

## Pitfall 6: Runtime Tests Forced Onto a Decision Ticket

**Bad:**
```
Purpose: Decide the circuit-breaker policy for mod-scheduler.

Acceptance Criteria
- Given the circuit breaker is configured
  When the downstream service fails repeatedly
  Then the breaker opens

Testing Guidance
Manual Testing: deploy the change and take the downstream service offline.

Additional Notes
The chosen policy must not let a retry run longer than the timer interval.
```

**Better:**
```
Purpose: Decide the circuit-breaker policy for mod-scheduler so implementation
tickets can be written against an agreed policy.

Requirements/Scope
1. Compare the candidate circuit-breaker options against the agreed criteria
2. Record the trade-offs and the constraints that apply, including that a retry
   must not run longer than the timer interval
3. Record one recommendation with its reasoning
4. Obtain Product Owner and backend lead review

Acceptance Criteria
- [ ] Options compared with trade-offs recorded
- [ ] Recommendation stated with reasoning
- [ ] Constraints recorded, including the retry-vs-interval limit
- [ ] Product Owner and backend lead have signed off
```

Why: nothing runs yet, so there is nothing to test at runtime. The binding constraint also moved out of Additional Notes into Requirements and into a checkable criterion.

## Pitfall 7: Dropping an Out of Scope Boundary That Does Help

Out of Scope is not banned — it is conditional. Keep it when it excludes a reading of *this* request that a reader could plausibly assume.

**Useful:**
```
Purpose: Add bulk renewal to the loans UI.

Out of Scope
- Integrating a new third-party renewal API (renewals use the existing service)
```

Why: bulk renewal could reasonably be read as including a new external integration, and the user ruled that out explicitly. Contrast this with adding "Quartz history cleanup" to a timer-deletion story — nobody would have read that into the request.
