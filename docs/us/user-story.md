# User Story Writing Guide

> **Current skill contract:** For section selection, acceptance-criteria granularity, verification guidance, templates, examples, and completion checklists, follow [write-user-story](../../skills/write-user-story/SKILL.md) and its references. The corresponding material below is retained as historical reference, not as an additional set of requirements.

This guide provides a structured approach to writing clear, actionable user stories that effectively communicate requirements to development teams.

## Table of Contents
1. [User Story Structure](#user-story-structure)
2. [Writing Guidelines](#writing-guidelines)
3. [Section Details](#section-details)
4. [Best Practices](#best-practices)
5. [Common Pitfalls](#common-pitfalls)
6. [Template](#template)

---

## User Story Structure

A well-written user story should include the following sections:

### 1. Purpose/Overview
**What it is:** A concise summary of what the story aims to achieve and why it matters.

**Should include:**
- High-level description of the feature or change
- Business context and motivation
- User persona or target audience (when applicable)
- Link to related stories, epics, or documentation

**Optional sub-section:**
- **Technical Details/Technical Approach**: High-level technical strategy, architecture decisions, or implementation notes (avoid deep implementation details unless necessary for understanding)

### 2. Requirements/Scope
**What it is:** Detailed functional and non-functional requirements that define what needs to be built.

**Functional Requirements should include:**
- Specific functionality to be implemented
- Input/output expectations
- Business rules and constraints
- Edge cases and error scenarios
- Integration points with other systems

**Non-Functional Requirements should include (when significant):**
- Performance requirements (only if they have measurable impact or specific targets)
- Security considerations (only if there are specific security requirements)
- Data integrity requirements
- Scalability requirements (if applicable)

**Omit non-functional requirements when:**
- Performance impact is negligible (e.g., adding a few fields to a response)
- No specific performance targets are needed
- Standard security practices are sufficient

**Out of Scope section:**
- Include ONLY when there's genuine ambiguity about scope
- List items that might reasonably be expected but are explicitly NOT included
- Omit if there are no valuable scope clarifications
- Don't include obvious future enhancements or unrelated features

**Formatting tips:**
- Use numbered or bulleted lists for clarity
- Group related requirements together
- Be specific and measurable where possible

### 3. Acceptance Criteria
**What it is:** Clear, testable conditions that must be met for the story to be considered complete.

**Should include:**
- Specific scenarios in Given-When-Then format (recommended)
- Expected behaviors for different user actions
- Error handling expectations
- Validation rules
- UI/UX expectations (if applicable)

**Format example:**
```
- Given [initial context/state]
  When [action/event occurs]
  Then [expected outcome]
```

### 4. Testing Guidance
**What it is:** High-level guidance for manual testing and verification.

**Should include:**
- Manual testing scenarios with step-by-step instructions
- Key user workflows to verify
- Edge cases to manually test
- Expected outcomes for each scenario

**Should NOT include:**
- Detailed unit test specifications (belongs in implementation plan)
- Integration test code examples (belongs in implementation plan)
- Test data setup details (belongs in implementation plan)
- Auto-generated documentation verification (e.g., OpenAPI docs)

**Note:** Keep testing guidance focused on manual verification. Detailed test specifications, test code examples, and test data belong in the implementation plan or technical documentation, not in the user story.

---

## Writing Guidelines

### Standard User Story Format

While not always required in the description, consider starting with the classic user story format:

```
As a [user persona/role]
I want [goal/desire]
So that [benefit/value]
```

**Example:**
```
As a system administrator
I want to configure automatic cleanup of old job logs
So that disk space is managed efficiently without manual intervention
```

### INVEST Principles

Good user stories should be:

- **I**ndependent: Can be developed and delivered separately
- **N**egotiable: Details can be discussed and refined
- **V**aluable: Delivers clear value to users or the system
- **E**stimable: Team can reasonably estimate the effort
- **S**mall: Can be completed within a single sprint
- **T**estable: Clear criteria for verification

### Characteristics of Quality User Stories

**Clear and Specific**
- Avoid vague language like "enhance," "improve," or "optimize" without specifics
- Define measurable outcomes where possible

**User-Focused**
- Written from the perspective of who benefits
- Emphasizes outcomes over implementation

**Appropriately Sized**
- Large stories should be epics, broken into smaller stories
- Very small stories might be tasks, not stories

**Actionable**
- Development team can start work immediately
- All necessary context is provided or linked

---

## Section Details

### Purpose/Overview - Deep Dive

**Good Purpose/Overview:**
```
This story implements automated retry logic for failed Kafka message processing.
Currently, when a Kafka event fails to process (e.g., due to temporary database
unavailability), the message is lost, requiring manual intervention.

This feature will add configurable retry with exponential backoff, improving
system resilience and reducing operational burden.

Related: PROJ-123 (Kafka Infrastructure Epic)
```

**Technical Details/Approach sub-section example:**
```
Technical Approach:
- Use Spring Retry with @Retryable annotation
- Configure retry policy via application properties
- Implement exponential backoff with jitter
- Add Dead Letter Queue (DLQ) for permanently failed messages
- Store retry attempts in message headers
```

### Requirements/Scope - Deep Dive

**Structure your requirements logically:**

**Functional Requirements:**
1. System shall retry failed Kafka message processing up to N times (configurable)
2. Retry intervals shall use exponential backoff (1s, 2s, 4s, 8s, etc.)
3. After max retries exceeded, message shall be sent to Dead Letter Queue
4. Each retry attempt shall be logged with timestamp and error details

**Non-Functional Requirements:**
1. Retry logic shall not block other message processing
2. Configuration shall be externalized (environment variables or properties)
3. System shall emit metrics for retry attempts and failures

**Out of Scope:**
- Manual retry triggering via UI
- Historical retry analytics dashboard

### Acceptance Criteria - Deep Dive

**Use Given-When-Then format for clarity:**

```
AC1: Successful retry after temporary failure
- Given a Kafka message fails to process due to database timeout
  When the message is retried
  And the database becomes available
  Then the message is processed successfully
  And no further retries occur

AC2: Dead Letter Queue after max retries
- Given a Kafka message that consistently fails processing
  When max retry attempts are exceeded
  Then the message is sent to the Dead Letter Queue
  And an error is logged with all retry details
  And processing continues with next message

AC3: Configurable retry behavior
- Given retry configuration is set to 5 attempts
  When the system starts
  Then the retry policy uses exactly 5 attempts
  And uses exponential backoff as configured
```

**Alternative format (checklist style):**
```
- [ ] System retries failed messages automatically
- [ ] Retry count is configurable via environment variable
- [ ] Exponential backoff is applied between retries
- [ ] Messages exceeding max retries go to DLQ
- [ ] All retry attempts are logged
- [ ] Metrics are emitted for monitoring
```

### Testing Guidance - Deep Dive

**Focus on manual testing scenarios that verify the feature works as expected:**

**Manual Testing Scenario Example:**
1. Start application with retry enabled
2. Temporarily stop database container
3. Send test message to Kafka topic
4. Verify retry attempts in logs
5. Restart database
6. Verify successful processing after retry

**What to INCLUDE in Testing Guidance:**
- Manual testing scenarios with clear steps
- Key user workflows to verify
- Edge cases and error scenarios to test manually
- Expected outcomes for each scenario
- System integration points to verify

**What to EXCLUDE from Testing Guidance:**
- Unit test specifications (e.g., "Test retry logic with mocked dependencies")
- Integration test code examples or detailed setup
- Test data fixtures and setup scripts
- Verification of auto-generated documentation (e.g., checking OpenAPI HTML output)
- Detailed test framework configuration

**Rationale:** Unit and integration test details belong in the implementation plan or technical documentation. User stories should focus on what needs to be verified, not how to write the tests.

---

## Best Practices

### Do's ✓

1. **Write from user perspective** - Focus on value delivered, not technical implementation
2. **Keep stories small** - Aim for completion within one sprint
3. **Include all necessary context** - Link to designs, APIs, related stories
4. **Make acceptance criteria testable** - Avoid subjective criteria
5. **Collaborate** - Review stories with developers, testers, and stakeholders
6. **Update as needed** - Stories can evolve during refinement
7. **Use consistent terminology** - Follow project glossary and domain language
8. **Include error scenarios** - Don't just focus on happy path
9. **Consider edge cases** - Boundary conditions, null values, empty states
10. **Link dependencies** - Identify blocking or related stories

### Don'ts ✗

1. **Don't write technical tasks as stories** - "Refactor UserService class" is a task, not a story
2. **Don't be vague** - Avoid "improve performance" without metrics
3. **Don't skip acceptance criteria** - These are essential for done definition
4. **Don't over-specify implementation** - Allow developers flexibility
5. **Don't make stories too large** - Break down into smaller, deliverable pieces
6. **Don't add non-functional requirements unless significant** - Only include performance, security, etc. when they have measurable impact or specific requirements
7. **Don't ignore existing patterns** - Follow established conventions in the codebase
8. **Don't write in isolation** - Collaborate with the team
9. **Don't leave out error handling** - Specify behavior when things go wrong
10. **Don't include test implementation details** - Focus on manual testing; unit/integration test specs belong in implementation plans
11. **Don't add "Out of Scope" unless necessary** - Only include when there's genuine ambiguity

---

## Common Pitfalls

### Pitfall 1: Technical Task Disguised as User Story
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
- Update documentation

Note: This is a technical enabler story, not user-facing.
```

### Pitfall 2: Vague Acceptance Criteria
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

- Given a user enters search term
  When clicking "Search"
  Then results appear within 3 seconds
  And user can filter, sort, and export results
```

### Pitfall 3: Missing Error Scenarios
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

### Pitfall 4: Solution Specified Too Early
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
- Performance: Profile retrieval shall be under 100ms (p95)

Technical Approach:
Consider Redis or in-memory cache. Coordinate with infrastructure team
on availability and operations requirements.
```

### Pitfall 5: Including Unnecessary Sections or Details
**Bad:**
```
Non-Functional Requirements:
1. Performance: Audit field updates are very fast (negligible overhead)
2. Backward Compatibility: API is backward compatible

Out of Scope:
- Full audit history table
- Audit export API
- User name resolution

Testing Guidance:
Unit Testing:
- Mock FolioExecutionContext
- Test entity extends AuditableEntity
- Verify getters and setters work

Test Data:
UUID USER_A = "11111111-1111-1111-1111-111111111111"
UUID USER_B = "22222222-2222-2222-2222-222222222222"
```

**Better:**
```
Non-Functional Requirements:
1. Data Integrity: created_date shall have NOT NULL constraint

(No "Out of Scope" section - none of the items clarify genuine ambiguity)

Testing Guidance:
Manual Testing Scenario 1: Create and Update Timer
1. POST /scheduler/timers with valid descriptor
2. Verify response includes audit fields with your user ID
3. Authenticate as different user and PUT to update
4. Verify createdBy unchanged, updatedBy shows new user

(No unit test specs, test data, or auto-generated doc verification)
```

**Rationale:**
- Performance section removed when impact is negligible
- Out of Scope removed when items don't clarify genuine ambiguity
- Backward compatibility removed when feature is additive by nature
- Unit test specifications moved to implementation plan
- Test data details moved to implementation plan
- Focus on what needs manual verification, not how to write tests

---

## Template

```markdown
## Purpose/Overview

[Provide high-level description of what this story achieves and why it's important.
Include business context, user persona, and links to related work.]

### Technical Details/Technical Approach (Optional)

[Include architectural decisions, implementation strategy, or technical constraints
that inform the approach but don't over-specify implementation.]

---

## Requirements/Scope

### Functional Requirements
1. [Specific functionality to implement]
2. [Input/output expectations]
3. [Business rules and constraints]

### Non-Functional Requirements (only if significant)
1. [Data integrity requirements]
2. [Performance requirements - only if measurable impact]
3. [Security considerations - only if specific requirements exist]

### Out of Scope (only if needed for clarity)
- [Include ONLY if there's genuine ambiguity about scope]
- [Omit this section if there are no valuable scope clarifications]

---

## Acceptance Criteria

**AC1: [Scenario name]**
- Given [initial context]
  When [action occurs]
  Then [expected outcome]

**AC2: [Scenario name]**
- Given [initial context]
  When [action occurs]
  Then [expected outcome]

**AC3: [Error handling scenario]**
- Given [error condition]
  When [action occurs]
  Then [expected error behavior]

---

## Testing Guidance

### Manual Testing

**Scenario 1: [Primary user workflow]**
1. [Step-by-step instructions]
2. [Expected outcomes]

**Scenario 2: [Edge case or alternate workflow]**
1. [Step-by-step instructions]
2. [Expected outcomes]

**Scenario 3: [Error handling or system integration]**
1. [Step-by-step instructions]
2. [Expected outcomes]

**Note:** Do not include unit test specifications, integration test code examples, test data details, or verification of auto-generated documentation. These belong in the implementation plan or technical documentation.

---

## Additional Notes

[Any other relevant information, risks, dependencies, or considerations]

## Related Links
- [Link to design documents]
- [Link to API specifications]
- [Link to related stories]
```

---

## Quick Reference Checklist

Before marking a user story as "Ready for Development," ensure:

- [ ] Purpose clearly explains the value and context
- [ ] Requirements are specific and measurable
- [ ] Acceptance criteria are testable and unambiguous
- [ ] Error scenarios and edge cases are covered
- [ ] Testing guidance is provided
- [ ] Dependencies are identified and linked
- [ ] Story is sized appropriately (completable in one sprint)
- [ ] Technical approach is outlined (if needed) but not over-specified
- [ ] Non-functional requirements are included (if applicable)
- [ ] The story has been reviewed by relevant stakeholders

---

## Example User Story

Here's a complete example following this guide:

```markdown
## Purpose/Overview

Implement automatic cleanup of expired timer descriptors to prevent database
bloat and improve query performance. Currently, disabled or expired timers
remain in the database indefinitely, consuming storage and slowing down queries.

This feature will add a scheduled job that removes timer descriptors that have
been disabled for more than 90 days, keeping the database lean and performant.

Target users: System administrators and database operations
Related: MODSCHED-45 (Database Optimization Epic)

### Technical Approach

- Add new Quartz job scheduled to run daily at 2 AM
- Use soft delete pattern to mark timers for deletion
- Actual deletion occurs after grace period expires
- Emit metrics for monitoring cleanup operations

---

## Requirements/Scope

### Functional Requirements
1. System shall identify timer descriptors that have been disabled for >90 days
2. System shall soft-delete identified timers (set deletion_date timestamp)
3. System shall permanently delete timers after 30-day grace period
4. Grace period allows recovery if timer was disabled accidentally
5. Cleanup job shall run daily at 2:00 AM (configurable)
6. System shall log all cleanup operations with timer IDs and counts

### Non-Functional Requirements
1. Cleanup operation shall not lock database tables for >5 seconds
2. Cleanup shall process max 1000 timers per batch to prevent memory issues
3. Configuration shall be externalized (cron schedule, retention period)

### Out of Scope
- Manual cleanup UI for administrators (future story)
- Cleanup of Quartz job history tables
- Archival of deleted timers to separate storage

---

## Acceptance Criteria

**AC1: Disabled timers soft-deleted after 90 days**
- Given timer descriptors that have been disabled for 95 days
  When cleanup job executes
  Then those timers are marked with deletion_date
  And they remain queryable for 30 more days
  And audit log records the soft deletion

**AC2: Soft-deleted timers permanently removed after grace period**
- Given timers with deletion_date older than 30 days
  When cleanup job executes
  Then those timers are permanently deleted from database
  And associated Quartz jobs are unscheduled
  And deletion count is logged

**AC3: Recently disabled timers not affected**
- Given timer descriptors disabled less than 90 days ago
  When cleanup job executes
  Then those timers are not marked for deletion
  And they continue to function normally

**AC4: Cleanup job runs on schedule**
- Given cleanup job is configured to run daily at 2 AM
  When system reaches 2:00 AM
  Then cleanup job executes automatically
  And completion status is logged
  And metrics are emitted (timers_deleted, execution_time)

**AC5: Batch processing prevents memory issues**
- Given 5000 timers eligible for cleanup
  When cleanup job executes
  Then timers are processed in batches of 1000
  And each batch is committed separately
  And process completes without out-of-memory errors

---

## Testing Guidance

### Unit Testing
- Test timer age calculation logic
- Test soft delete marking
- Test permanent deletion after grace period
- Test batch processing with various batch sizes
- Mock Quartz scheduler interactions

### Integration Testing
- Test with real PostgreSQL database (Testcontainers)
- Create timers with various disabled dates
- Execute cleanup job and verify correct deletions
- Verify Quartz jobs are properly unscheduled
- Test with large dataset (10,000+ timers) for performance

### Manual Testing
1. Create test timers with disabled_date set to various dates
2. Set cleanup retention period to 1 minute (for faster testing)
3. Manually trigger cleanup job via endpoint (if available) or wait for schedule
4. Query database to verify soft deletions
5. Wait for grace period to expire
6. Verify permanent deletions and Quartz job removal
7. Check logs for cleanup operation details
8. Verify metrics in monitoring dashboard

### Test Data Setup
```sql
-- Create test timers with various disabled dates
INSERT INTO timer_descriptor (id, enabled, disabled_date, ...)
VALUES
  ('uuid1', false, NOW() - INTERVAL '95 days', ...),  -- Should be soft-deleted
  ('uuid2', false, NOW() - INTERVAL '130 days', ...), -- Should be soft-deleted
  ('uuid3', false, NOW() - INTERVAL '30 days', ...),  -- Should remain
  ('uuid4', true, NULL, ...);                          -- Active, should remain
```

---

## Additional Notes

**Performance Considerations:**
- Cleanup runs during off-peak hours to minimize impact
- Batching prevents transaction log bloat
- Indexes on disabled_date and deletion_date required for performance

**Monitoring:**
- Add dashboard alerts if cleanup job fails
- Track metric: timers_deleted_per_day (watch for anomalies)

**Risks:**
- If retention period too short, may delete timers still needed
- Consider adding restoration endpoint in future story

## Related Links
- Database schema: src/main/resources/changelog/changes/v1.0/
- Quartz job configuration: JobSchedulingService.java
- Monitoring dashboard: [link to Grafana]
```

---

## Summary

Writing effective user stories is a skill that improves with practice. The key is to balance clarity with flexibility, provide enough detail for implementation without over-specifying, and always keep the user's needs at the center.

Remember:
- **Purpose/Overview** answers "What and why?"
- **Requirements/Scope** answers "What exactly needs to be built?"
- **Acceptance Criteria** answers "How do we know it's done?"
- **Testing Guidance** answers "How do we verify it works manually?"

**Keep it focused:**
- Omit non-functional requirements when they're not significant
- Skip "Out of Scope" unless there's genuine ambiguity
- Keep testing guidance to manual scenarios only
- Don't include unit/integration test specifications (those belong in implementation plans)
- Don't include test data details or auto-generated documentation verification

**The goal:** A user story should clearly communicate requirements and acceptance criteria without becoming an implementation specification or test plan. Technical implementation details belong in separate technical documentation.

Use this guide as a starting point, and adapt it to your team's needs and preferences.

---

## Converting to JIRA Format

When creating user stories in JIRA, you'll need to convert Markdown formatting to JIRA markup syntax:

**Headers:**
- `# Header` → `h1. Header`
- `## Subheader` → `h2. Subheader`

**Text Formatting:**
- `**bold**` → `*bold*`
- `*italic*` → `_italic_`
- `` `code` `` → `{{code}}`

**Lists:**
- `- item` → `* item` (unordered)
- `1. item` → `# item` (ordered)
- Nested lists use `**` for second level, `***` for third level

**Code Blocks:**
- ` ```language` → `{code:language}...{code}`
- ` ```json` → `{code:json}...{code}`

**Special Characters:**
- Escape curly braces in URLs: `{id}` → `\{id\}`
- Escape square brackets if needed

**Horizontal Rules:**
- `---` → `----` (four dashes in JIRA)

**Example Conversion:**

Markdown:
```markdown
## Requirements
**Functional Requirements:**
- System shall store `audit_date` field
- API returns timestamps in ISO 8601 format
```

JIRA:
```
h2. Requirements
*Functional Requirements:*
* System shall store {{audit_date}} field
* API returns timestamps in ISO 8601 format
```
