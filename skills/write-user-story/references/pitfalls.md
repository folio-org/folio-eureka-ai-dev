# Common Pitfalls

## Pitfall 1: Technical Task Disguised as User Story

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

**Rules:**
- Remove performance NFRs when impact is negligible
- Remove Out of Scope when items don't clarify genuine ambiguity
- Remove backward compatibility notes when feature is purely additive
- Move unit test specs to the implementation plan
- Move test data details to the implementation plan
