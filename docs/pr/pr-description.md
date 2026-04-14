# PR Description Guide

A reference for writing consistent, reviewable pull request descriptions in this repository.
The canonical template is [PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md).

---

## Title

Place the PR title as an H2 heading **above** the template sections.

**Format:** `TICKET-KEY: <title>`

Rules:
- Start with the Jira ticket key (`APPPOCTOOL-85:`, `KEYCLOAK-102:`, etc.).
- **Copy the title verbatim from the Jira user story title.** Only when explicitly told otherwise
  should the title be formed from the purpose of the changes instead.
- Use sentence case; do not end with a period.
- Keep it under ~80 characters.

**Good**
```
## APPPOCTOOL-85: Generalize Kafka consumer tenant filter to support custom event types
```

**Avoid**
```
## Fix stuff and update tests        ← no ticket key, vague
## APPPOCTOOL-85                     ← key only, no description
## Updated the filter class to now use a new interface instead of the old one  ← too long, passive
```

---

## Purpose

One or two sentences answering:
1. **Why** are these changes needed?
2. A user story reference in the format `US: [TICKET-KEY](url)`.

```
Extends the Kafka consumer library to allow tenant-aware filtering for any message type,
not just `ResourceEvent`. Adds per-listener concurrency configuration and a blank-tenant
guard in the filter.
US: [APPPOCTOOL-85](https://folio-org.atlassian.net/browse/APPPOCTOOL-85)
```

Do not describe *how* the change is implemented here — that belongs in Approach.

---

## Approach

Two parts, always in this order:

### 1. Summary (2–3 sentences)

A high-level technical narrative. A reader should understand the main idea without reading any code.
Focus on what was introduced or changed and why the chosen design makes sense.

```
A new `TenantAwareEvent` interface extracts the tenant contract from `ResourceEvent`, allowing
`EnabledTenantMessageFilter` to be parameterized over any custom event type. A blank-tenant guard
is added to the filter to short-circuit entitlement checks for malformed messages, and a
`concurrency` property is introduced to `KafkaListenerProperties` for tuning concurrent consumer
threads per listener.
```

### 2. Implementation details (bullet list)

Each bullet covers one concrete, self-contained change.

Rules:
- **One bullet per logical change** — a new class, a changed contract, a new config property, etc.
- **Up to 2 sentences per bullet.** First sentence: what was done. Optional second sentence: why,
  or a notable consequence (e.g. backward-compatibility note).
- **No test changes** — do not list added/updated tests unless the PR is exclusively about testing.
- **No documentation changes** — do not list README or Javadoc updates unless the PR is
  exclusively about documentation.
- Use backticks for class names, method names, property keys, and values.
- Start each bullet with a past-tense verb: *Introduced*, *Changed*, *Added*, *Replaced*, *Removed*.

**Good**
```markdown
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
```

**Avoid**
```markdown
- Updated unit tests for EnabledTenantMessageFilter.      ← test changes, omit
- Fixed Javadoc in TenantAwareEvent.                      ← doc change, omit
- Made some improvements to the filter class.             ← vague, no specifics
- Changed the type bound, added blank tenant handling, added concurrency, updated package-info files,
  bumped version, fixed README. ← one bullet for too many unrelated changes
```

---

## Pre-Review Checklist

Keep the checklist exactly as it appears in the template. Before submitting, tick every item that
applies to the PR:

| Item | When to tick |
|---|---|
| **Self-reviewed Code** | Always |
| **Change Notes** | Always — add an entry to `NEWS.md` |
| **Testing** | Always — local run or dev-env verification |
| **Dependent module build verification** | When a shared library changes its public API |
| **Breaking Changes** | When an interface, configuration key, or serialized format changes incompatibly |
| **New Properties / Environment Variables** | When `application.kafka.*` or similar config keys are added |
| **Environment Recreation Test** | When infrastructure or startup configuration changes |

Leave unchecked items unchecked — do not delete them.

---

## Complete example

```markdown
## APPPOCTOOL-85: Generalize Kafka consumer tenant filter to support custom event types

### **Purpose**
Extends the Kafka consumer library to allow tenant-aware filtering for any message type, not just
`ResourceEvent`. Adds per-listener concurrency configuration and a blank-tenant guard in the filter.
US: [APPPOCTOOL-85](https://folio-org.atlassian.net/browse/APPPOCTOOL-85)

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

- [x] **Self-reviewed Code** — Reviewed code for issues, unnecessary parts, and overall quality.
- [x] **Change Notes** — NEWS.md updated with clear description and issue key.
- [x] **Testing** — Confirmed changes were tested locally or on dev environment.
- [ ] **Dependent module build verification** — Ran manually when library changes impact downstream modules.
  > Actions → Verify Dependent Modules → Run workflow → select branch → Run.
- [x] **Breaking Changes (if any)** — Handled if changes affect integration with other services.
- [x] **New Properties / Environment Variables** — Updated README.md if new configs were added.
- [ ] **Environment Recreation Test (if needed)** — Verified that environment can be recreated successfully.
```
