# Section Details — Deep Dive

## Purpose/Overview

**What it is:** A concise summary of what the story aims to achieve and why it matters.

**Should include:**
- High-level description of the feature or change
- Business context and motivation
- User persona or target audience **when a real user role applies** — omit it for technical enablers and decision work rather than inventing one
- Links to related stories, epics, or documentation **when they carry context**, each with its relationship stated

**Good example:**
```
This story implements automated retry logic for failed Kafka message processing.
Currently, when a Kafka event fails to process (e.g., due to temporary database
unavailability), the message is lost, requiring manual intervention.

This feature will add configurable retry with exponential backoff, improving
system resilience and reducing operational burden.

Parent scope: PROJ-123 (Kafka Infrastructure Epic) defines the retry budget this
story must stay within.
```

Note how the link says what PROJ-123 contributes. A bare list of neighbouring keys adds nothing.

**Technical Details/Approach sub-section example** — these are illustrative choices that were agreed in that particular story, not defaults to copy into other stories:
```
Technical Approach:
- Use Spring Retry with @Retryable annotation
- Configure retry policy via application properties
- Implement exponential backoff with jitter
- Add Dead Letter Queue (DLQ) for permanently failed messages
```

## Requirements/Scope

This section carries **all binding constraints**. If a constraint affects correctness or acceptance, it belongs here — not in Additional Notes.

**Functional Requirements:**
1. System shall retry failed Kafka message processing up to N times (configurable)
2. Retry intervals shall use exponential backoff (1s, 2s, 4s, 8s, etc.)
3. After max retries exceeded, message shall be sent to Dead Letter Queue
4. Each retry attempt shall be logged with timestamp and error details

**Non-Functional Requirements (only if significant):**
1. Retry logic shall not block other message processing
2. Configuration shall be externalized (environment variables or properties)

**Omit non-functional requirements when:**
- Performance impact is negligible
- No specific performance targets are needed
- Standard security practices are sufficient

**Out of Scope:**
- Include ONLY when a plausible alternative reading of this request must be excluded, or the user drew the boundary explicitly
- Omit for neighbouring topics that were never in scope

## Acceptance Criteria

Each criterion covers a **distinct completion condition**. Do not expand every configuration field or implementation step into its own scenario, and do not collapse genuinely different outcomes into one.

**Use Given-When-Then for observable behavior:**

```
AC1: Successful retry after temporary failure
- Given a Kafka message fails to process due to database timeout
- When the message is retried
- And the database becomes available
- Then the message is processed successfully
- And no further retries occur

AC2: Dead Letter Queue after max retries
- Given a Kafka message that consistently fails processing
- When max retry attempts are exceeded
- Then the message is sent to the Dead Letter Queue
- And an error is logged with all retry details

AC3: Configurable retry behavior
- Given retry configuration is set to 5 attempts
- When the system starts
- Then the retry policy uses exactly 5 attempts
```

**Alternative checklist format** — clearer for a technical contract or a decision deliverable:
```
- [ ] System retries failed messages automatically
- [ ] Retry count is configurable via environment variable
- [ ] Messages exceeding max retries go to DLQ
- [ ] All retry attempts are logged
```

## Testing Guidance

Match verification to the work type. See the table in the main skill.

### User-facing / runtime change → Manual Testing

Short steps with expected results, for a workflow a tester can actually run.

**Manual Testing Scenario Example** (run against a disposable local or test environment — never by disrupting a shared or production deployment):
1. Start application with retry enabled
2. Temporarily stop the local database container
3. Send test message to Kafka topic
4. Verify retry attempts in logs
5. Restart the local database container
6. Verify successful processing after retry

### Backend / API / library change → Controlled Verification

Verify the contract under conditions you can create locally. Name the level of automated verification if useful; do not write the tests here.

**Example — library timeout behavior:**
```
Controlled Verification:
- Point the client at a local endpoint that accepts the TCP connection but never
  responds, and confirm the read timeout fires at the configured value.
- Point the client at an unroutable address and confirm the connect timeout fires
  at its own configured value.
- Confirm each case surfaces its own externally observable timeout exception, and
  that the existing retry logic still sees it.
```

No shared Keycloak outage is required, and no test code belongs in the story.

### Pure discovery / policy / decision work → no runtime Testing Guidance

Do not add a runtime section, and do not write `Testing Guidance: N/A`. Completion is verified through the Requirements and acceptance criteria instead.

**Example — policy/discovery completion:**
```
Acceptance Criteria
- [ ] Candidate options are compared against the agreed criteria, with trade-offs recorded
- [ ] One recommendation is stated with its reasoning
- [ ] Constraints and rejected options are recorded with the reason for rejection
- [ ] Product Owner and backend lead have reviewed and signed off on the recommendation
```

**Exclude from every variant:**
- Unit test specifications
- Integration test code examples or detailed setup
- Test data fixtures and setup scripts
- Verification of auto-generated documentation
