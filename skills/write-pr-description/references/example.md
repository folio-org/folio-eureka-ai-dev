# Worked example

Drafted output for a repository whose template is the `applications-poc-tools` variant. Another
repository's checklist will differ — this example is not a checklist to copy; the checklist always
comes from the target repository's own template file (Step 3 of the skill). Every box is unticked:
the author ticks them when opening the PR.

```markdown
## APPPOCTOOL-85: Generalize Kafka consumer tenant filter to support custom event types

### **Purpose**
Extends the Kafka consumer library to allow tenant-aware filtering for any message type, not just
`ResourceEvent`. Adds per-listener concurrency configuration and a blank-tenant guard in the filter.
Jira: [APPPOCTOOL-85](https://folio-org.atlassian.net/browse/APPPOCTOOL-85)

### **Approach**
A new `TenantAwareEvent` interface extracts the tenant contract from `ResourceEvent`, allowing
`EnabledTenantMessageFilter` to be parameterized over any custom event type. A blank-tenant guard
is added to the filter to short-circuit entitlement checks for malformed messages, and a
`concurrency` property is introduced to `KafkaListenerProperties` for tuning concurrent consumer
threads per listener.

**Implementation details:**

- Introduced `TenantAwareEvent` marker interface with a single `@Nullable getTenant()` method;
  `ResourceEvent<T>` now implements it, preserving backward compatibility for existing consumers.
- Changed `EnabledTenantMessageFilter<K, V>` type bound from `V extends ResourceEvent<?>` to
  `V extends TenantAwareEvent`, so any custom event class can be filtered without inheriting from
  `ResourceEvent`.
- Added a blank-tenant guard at the start of `EnabledTenantMessageFilter#filter`: if `getTenant()`
  returns `null` or blank the record is accepted immediately and a `WARN` log entry is emitted,
  avoiding an unnecessary entitlement service call.
- Added `concurrency` field (default `1`) to `KafkaListenerProperties`; lets consumers declare the
  number of concurrent threads per listener directly in `application.kafka.consumer.listener.<name>`.

---

### **Pre-Review Checklist**

- [ ] **Self-reviewed Code** — Reviewed code for issues, unnecessary parts, and overall quality.
- [ ] **Change Notes** — NEWS.md updated with clear description and issue key.
- [ ] **Testing** — Confirmed changes were tested locally or on dev environment.
- [ ] **Dependent module build verification** — Ran manually when library changes impact downstream modules.
  > Actions → Verify Dependent Modules → Run workflow → select branch → Run.
- [ ] **Breaking Changes (if any)** — Handled if changes affect integration with other services.
- [ ] **New Properties / Environment Variables** — Updated README.md if new configs were added.
- [ ] **Environment Recreation Test (if needed)** — Verified that environment can be recreated successfully.
```
