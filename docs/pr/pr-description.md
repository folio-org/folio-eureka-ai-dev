# PR Description Guide

A reference for writing consistent, reviewable pull request descriptions.

The canonical template is the target repository's own `.github/PULL_REQUEST_TEMPLATE.md`. There is no
single shared template: `mgr-tenants` and `mod-roles-keycloak` have no "Dependent module build
verification" item and split Breaking Changes into three sub-items, while `applications-poc-tools`
is the reverse. This guide defines what goes *into* the sections; the repository's template defines
which sections and which checklist items exist.

---

## Title

**Format:** `TICKET-KEY: <title>`

When the PR is opened through `gh`, the title goes in the title field and must **not** be repeated as
an `##` heading in the body. When the description is drafted as text for a human to paste, place it as
an H2 heading above the template sections.

Rules:
- Start with the Jira ticket key (`APPPOCTOOL-85:`, `KEYCLOAK-102:`, etc.).
- **Resolve the key from what the user said, then the branch name, then the commit messages.** If no
  key exists anywhere, ask once; if there is no ticket, write a plain semantic title describing what
  the branch does and omit the ticket link. Do not write `NOJIRA`, and do not emit a Jira URL for a
  key you inferred rather than read.
- **Write the title from the branch and the diff, not from Jira.** Looking the story title up is not
  required and not expected — no apology for lacking tracker access belongs in a PR description.
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
- **Write for a human, not for a diff viewer.** Each bullet should read as a plain sentence about what
  changed and why. The reviewer has the diff already; the bullet exists to explain it.
- **Name the code artifact when it helps the reviewer find the change.** Usually one per bullet — the
  class, or the schema/config file — is enough to anchor it. Do not stack every method, annotation,
  type parameter and exception into one bullet just because they appear in the diff, and do not leave
  a bullet unanchored ("in one shared utility") when naming the class would tell the reviewer exactly
  where to look.
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
- Defined the tenant contract in one shared interface.    ← which one? name it, so the reviewer
                                                             knows where to look
- Changed the type bound, added blank tenant handling, added concurrency, updated package-info files,
  bumped version, fixed README. ← one bullet for too many unrelated changes
- Changed `EnabledTenantMessageFilter<K, V>#filter(ConsumerRecord<K, V>)` to invoke
  `TenantAwareEvent#getTenant()`, guard the result with `StringUtils.isBlank`, emit a `WARN` through
  `log4j2`, and return `true` without calling `EntitlementService#isTenantEntitled`.
  ← reads as a transcript of the diff; say what it does and why instead
```

---

## Pre-Review Checklist

The checklist is copied from the repository's own `.github/PULL_REQUEST_TEMPLATE.md` — verbatim: same
items, same wording, same order, same indentation, same blockquote notes, same sub-items. Do not
reproduce a checklist from memory or from this guide; the items differ per repository. If a
repository has no template file, the description carries no checklist.

**The checklist is the author's signature.** Whoever opens the PR ticks the boxes. A drafted
description — and anything an assistant produces — leaves every box unticked. Ticking
*Self-reviewed Code*, *Change Notes* or *Testing* asserts that a human reviewed the code, updated
`NEWS.md` and ran the change; none of that is visible in a diff. Ticking a box and adding a prose
caveat underneath is the same defect with a disclaimer attached.

Do not tick, untick, reword, reorder, delete or add an item.

The template's **prose** sections are different: keep the heading, delete the template's instruction
line ("Explain why these changes are needed…"), and write real content in its place. Verbatim
reproduction applies to the checklist only.

---

## No tool attribution

The PR description must not mention Claude, Anthropic, Copilot, or any other AI tool, and must not end
with a "Generated with ..." or "Co-Authored-By" trailer. This applies however the description was
produced. The description is a statement about the change, not about how it was written.

Several coding agents append such a trailer by default — remove it before opening the PR.

---

## Opening the PR

Writing a PR description is a read-only task. Reading the repository, `git`, and `gh` are in scope;
builds, tests, linters, formatters, generators, migrations and CI workflows are not — a broken branch
is worth telling the author about, but not worth running a build to confirm.

Nothing in the description may claim what the diff does not show: no testing performed, no
verification run, no Jira title that was not read, no ticket link for a key that was inferred.

When the PR is actually opened rather than drafted:

- Base branch is always `master`.
- Verify the effective `gh` identity from the target repository first — repository-local setup such
  as `.envrc` exporting `GH_TOKEN` overrides the global account.
- Push only the current head branch, never another branch and never with `--force`, and push it when
  the branch has no upstream or has commits the remote does not.

---

## Complete example

Drafted output for a repository whose template is the `applications-poc-tools` variant. Another
repository's checklist will differ — this example is not a checklist to copy. Every box is unticked:
the author ticks them when opening the PR.

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

- [ ] **Self-reviewed Code** — Reviewed code for issues, unnecessary parts, and overall quality.
- [ ] **Change Notes** — NEWS.md updated with clear description and issue key.
- [ ] **Testing** — Confirmed changes were tested locally or on dev environment.
- [ ] **Dependent module build verification** — Ran manually when library changes impact downstream modules.
  > Actions → Verify Dependent Modules → Run workflow → select branch → Run.
- [ ] **Breaking Changes (if any)** — Handled if changes affect integration with other services.
- [ ] **New Properties / Environment Variables** — Updated README.md if new configs were added.
- [ ] **Environment Recreation Test (if needed)** — Verified that environment can be recreated successfully.
```
