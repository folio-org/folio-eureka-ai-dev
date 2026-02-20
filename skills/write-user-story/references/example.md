# Complete Example User Story

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
1. System shall identify timer descriptors disabled for >90 days
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

### Manual Testing

**Scenario 1: Verify soft deletion**
1. Create test timers with disabled_date set to 95 days ago
2. Set cleanup retention period to 1 minute (for faster testing)
3. Manually trigger cleanup job or wait for schedule
4. Query database to verify soft deletions (deletion_date populated)
5. Confirm timers are still queryable during grace period

**Scenario 2: Verify permanent deletion after grace period**
1. Set timers with deletion_date older than grace period
2. Trigger cleanup job
3. Verify timers are permanently deleted
4. Verify associated Quartz jobs are unscheduled
5. Check logs for deletion count

**Scenario 3: Verify recently disabled timers are unaffected**
1. Create timers disabled 30 days ago
2. Run cleanup job
3. Confirm those timers have no deletion_date set

---

## Additional Notes

**Monitoring:**
- Add dashboard alerts if cleanup job fails
- Track metric: timers_deleted_per_day (watch for anomalies)

**Risks:**
- If retention period too short, may delete timers still needed
- Consider adding restoration endpoint in future story

## Related Links
- Database schema: src/main/resources/changelog/changes/v1.0/
- Quartz job configuration: JobSchedulingService.java
```
