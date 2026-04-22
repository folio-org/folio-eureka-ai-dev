---
name: write-bug
description: Use when creating, writing, or refining a bug report for a FOLIO project. Produces structured bug tickets with a clear summary, preconditions, numbered steps to reproduce, expected vs. actual results, and supporting evidence (logs, stack traces, screenshots). Also use when asked to file a defect, triage an issue, or prepare a bug for Jira. Optionally interacts with the user to gather missing context and can create the ticket via the Jira MCP integration.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
---

# Write Bug (FOLIO)

A FOLIO bug report must be **reproducible, specific, and evidence-backed**. The reader
should be able to recreate the defect without guessing.

## Bug Structure

Every FOLIO bug must have these sections (in order). Sections marked _(optional)_
are omitted when they add no value.

1. **Summary** — One-line title on the Jira issue. Must name the affected area and
   the observable symptom. See [Summary Rules](#summary-rules).
2. **Overview / Context** _(recommended)_ — 1–3 sentences explaining the impact,
   origin (e.g. regression from TICKET-123), or business context. A majority of
   FOLIO bugs open with an "Overview:" section; include one unless the defect is
   truly self-evident from the summary.
3. **Preconditions** — Environment, data, roles, permissions, feature flags, or prior
   tickets required before the steps work. Each precondition must be independently
   verifiable.
4. **Steps to reproduce** — Numbered, atomic actions. One user action per step. No
   assumptions about prior navigation.
5. **Expected result** — What the system should do, referencing a source of truth
   (spec, acceptance criteria, prior behavior) when possible.
6. **Actual result** — What the system actually does. Quote error messages verbatim
   and include status codes/IDs where relevant.
7. **Additional information** _(optional but strongly recommended)_ — Stack traces,
   request/response payloads, query plans, log excerpts, screenshots, video, affected
   environment URLs, and reproducibility rate.

## Template

```markdown
## Overview

[1–3 sentences on impact, affected users, regression source, or related tickets.
Recommended for anything non-trivial — FOLIO bugs conventionally open with this.]

---

## Preconditions

1. [Environment / tenant / user role]
2. [Data state — e.g. "An Order in 'Open' status exists with one PO line"]
3. [Feature flag / configuration]

---

## Steps to reproduce

1. [Single user action]
2. [Single user action]
3. [Single user action]

---

## Expected result

- [Observable outcome #1]
- [Observable outcome #2, referencing spec/AC if applicable]

---

## Actual result

- [Observable outcome #1, including exact error text]
- [HTTP status / error code / record state]

---

## Additional information (optional)

**Reproducibility:** [Always / Intermittent (X of Y) / Once]
**Environment:** [folio-etesting-snapshot / folio-etesting-sprint / local]
**Module versions:** [mod-orders 13.0.5, ui-orders 9.1.2]
**Affected tickets / regression source:** [PROJECT-123]
**Workaround:** [Describe any workaround found, or "None" / omit if not applicable]
**Test Cases:** [TestRail IDs, e.g. C15189, C15190 — omit if not used by your team]

\`\`\`
[paste stack trace or log excerpt]
\`\`\`

**Attachments:** screenshots / HAR / video (attach to Jira)
```

## Summary Rules

A good summary passes the **"scan test"** — a triager can decide priority and
routing from the title alone.

### Format

```
[<Area/Component>] <symptom> when <trigger/condition>
```

The `[<Area>]` prefix is optional when the Jira project already narrows the area
(e.g., UIOR implies Orders UI).

### Do
- Name the observable symptom: "returns 500", "displays duplicate rows",
  "is not updated", "does not reflect the change".
- Include the trigger: "when moving holdings", "after paying invoice in foreign
  currency", "on tenant with >50k orders".
- Mention the environment only if the bug is environment-specific
  (e.g., "M-an dry-run |" prefix for env-specific issues).

### Don't
- Don't write vague titles: ❌ "Bug in orders", ❌ "Doesn't work".
- Don't prescribe a fix in the title: ❌ "Add null check in X".
- Don't over-qualify with implementation detail the triager won't know.

### Examples (from real FOLIO bugs)
- ✅ "Updating receiptDate does not update updatedDate in POL audit history"
- ✅ "Order expended amount is not converting the invoice currency"
- ❌ "POL bug"
- ❌ "Fix currency handling"

## Writing Guidelines

### Steps to reproduce
- **Start from a clean, logged-in state** or state it in Preconditions.
- **One action per step.** Split "Open the order and click Receive" into two.
- **Be literal.** Use the exact UI label or API path:
  `POST /orders/wrapper-pieces?query=...`.
- **Reference data by property, not ID.** "An Order in 'Open' status with
  Synchronized receiving workflow" beats "Order d4e7-...".
- **Stop at the point of failure.** Don't include post-failure exploration.

### Expected vs. Actual
- **Both must be observable by a tester**, not internal state. "No error is
  thrown" is weak; "Toast 'Order saved' appears and status = Open" is strong.
- **Quote errors verbatim**, including status code, error code, and message.
- **Diff expected and actual**. If a field is wrong, state both values.

### Evidence
- **Stack traces** → paste inside a fenced code block; Jira renders it as a
  scrollable `{code}` block.
- **Logs** → include timestamp, logger name, level, and correlation id.
- **SQL / query plans** → include for performance bugs.
- **Screenshots / video** → attach to Jira, reference by filename.
- **Reproducibility rate** matters for triage: always vs. intermittent
  (e.g., "3 of 10 attempts").

## Priority & Severity (FOLIO scale)

Use this matrix as a starting point; the triage team may re-assign.

| Priority | When to use |
|----------|-------------|
| **P1 — Critical** | Severe correctness or availability problems: data loss or corruption, security vulnerability, incorrect financial/calculation output, login/authentication broken, whole app or major workflow unusable, blocks release, or affects downstream processes across the system. |
| **P2 — Major** | Core workflow broken or produces wrong results, no reasonable workaround, affects many users. |
| **P3 — Normal** | Defect with a workaround, affects a specific flow or subset of users. |
| **P4 — Minor** | Cosmetic, typo, edge case with low impact. |
| **TBD** | Priority not yet assessed — acceptable when filing, expect triage. |

## User Interaction Flow

Before producing the final bug, check whether the user supplied the essentials.
If any of the following are missing or ambiguous, **ask the user using the
question tool** (batch related questions in one call):

1. **Target Jira project** (e.g., MODORDERS, UIOR, FOLIO). Required to draft
   summary prefix and determine Jira creation path.
2. **Environment** where the bug occurs (snapshot, bugfest, dry-run, local,
   specific tenant).
3. **Reproducibility** (always / intermittent / once-off). Drives triage.
4. **Steps to reproduce** if only a symptom was given.
5. **Expected behavior source** (spec, ticket, "previous release"). Needed when
   "expected" is subjective.
6. **Supporting evidence** — logs, stack trace, screenshots, HAR, recordings.
7. **Priority suggestion** if the user has context on impact.

Do **not** ask about sections the user can reasonably leave to triage
(fix versions, components, labels) unless they volunteer them.

### Optional: file the bug in Jira

After the user approves the draft, offer to create the ticket via
`mcp-atlassian_jira_create_issue`:
- Use the agreed project key and `issue_type: "Bug"`.
- Convert the Markdown draft to Jira markup (see
  [references/jira.md](references/jira.md)).
- Pass `priority`, `labels`, `components`, and `fixVersions` via
  `additional_fields` only when the user confirmed them.
- After creation, return the issue key and URL.

Before creating, **search for duplicates** with `mcp-atlassian_jira_search`
using keywords from the summary and show the top matches to the user.

## Best Practices

### Do ✓
1. One bug per ticket. Split compound defects.
2. Write preconditions so someone else can reach the starting state.
3. Quote errors verbatim, including codes and IDs.
4. State reproducibility rate for intermittent bugs.
5. Link regression source (the ticket that introduced it) when known.
6. Search for duplicates before filing.

### Don't ✗
1. Don't hypothesize a root cause in the summary or steps. Put hypotheses in
   a clearly labelled _Additional information_ note.
2. Don't mix multiple defects in one ticket.
3. Don't use vague verbs: "doesn't work", "is broken", "acts weird".
4. Don't paste secrets (tokens, real user emails, tenant credentials).
5. Don't include the proposed fix in the bug itself — that belongs in the PR
   or a linked story.
6. Don't skip the expected result — "it should work" is not testable.

## Quick Reference Checklist

- [ ] Summary identifies area + symptom + trigger
- [ ] Preconditions are independently verifiable
- [ ] Steps are numbered, atomic, and start from a defined state
- [ ] Expected result references a source of truth
- [ ] Actual result includes exact error text / status code
- [ ] Reproducibility rate is stated
- [ ] Environment and module versions are recorded
- [ ] Stack traces / logs / screenshots attached or inlined
- [ ] Workaround documented if one exists
- [ ] No PII, secrets, or real credentials
- [ ] Duplicate search performed before filing
- [ ] One defect per ticket

For section-by-section guidance, see [references/section-details.md](references/section-details.md).
For a complete example bug, see [references/example.md](references/example.md).
For Markdown → Jira markup conversion, see [references/jira.md](references/jira.md).
For common pitfalls with before/after rewrites, see [references/pitfalls.md](references/pitfalls.md).
