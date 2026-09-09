---
name: write-user-story
description: Use when creating or refining a user story, technical enabler, or discovery/policy ticket, defining acceptance criteria, or preparing scoped work for development or a decision.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
---

# Write User Story

## User Story Structure

Every story has three core sections, in order: Purpose/Overview, Requirements/Scope, and Acceptance Criteria. Choose supporting sections from the actual deliverable, not from the template. Determine the work type from the request and available context; ask a focused question only when an unresolved distinction would materially change the story.

Purpose/Overview states the outcome and its value. Requirements/Scope contains the capabilities, contracts, deliverables, and binding constraints. Acceptance Criteria states the smallest sufficient set of distinct, verifiable completion conditions. Technical enablers and discovery/policy work do not require an invented end-user persona.

## Template

This skeleton is the whole story unless a supporting section earns its place.

```markdown
## Purpose/Overview

[Outcome, value, and relevant context.]

## Requirements/Scope

1. [Required capability, contract, or deliverable, including binding constraints.]

## Acceptance Criteria

[Distinct verifiable completion conditions.
Use Given-When-Then for behavior or a concise checklist for contracts/deliverables.]
```

## Acceptance Criteria

Use Given-When-Then for observable behavior. Use a concise verifiable checklist when it expresses a technical contract or decision deliverable more clearly. Each criterion covers a distinct completion condition grounded in the agreed scope. Cover material error and boundary behavior without expanding every configuration field or implementation step into a separate scenario.

There is no fixed maximum or minimum number of criteria. Do not drop important conditions for the sake of brevity, and do not turn acceptance criteria into a detailed test plan.

## Task-Appropriate Verification

| Work/result | Required behavior |
|---|---|
| User-facing/runtime change | Add `Testing Guidance` when it gives a useful way to verify beyond the acceptance criteria. For a real UI workflow, `Manual Testing` with short steps and expected results is appropriate. |
| Backend/API/library change | Add `Testing Guidance` with `Controlled Verification` when useful: API/contract checks, a local harness, stubs, or controlled failure conditions. Naming the level of automated verification is fine without writing the tests. Do not require breaking a shared or production deployment, or waiting for a real outage of an external service. |
| Pure discovery/policy/decision work | Do not add runtime `Testing Guidance`. Verify the concrete decision artifacts, comparison/trade-offs, recommendation, constraints, and the agreed review through Requirements and acceptance criteria. Do not write `Testing Guidance: N/A`. |
| Mixed work | Verify each part that was actually requested in the way that fits it. The word "policy" alone does not remove testing for a runtime change that was genuinely requested. |

Keep test code, mock configuration, fixture scripts, detailed harness setup, and implementation-plan-level test cases out of the story. This limits detail; it does not forbid naming automated or contract verification.

## Conditional Sections

Add a section only when its condition holds.

- **Out of Scope** — only for a plausible alternative reading of *this* request that must be excluded, or a useful boundary the user stated explicitly. Neighbouring investigation topics, obvious future enhancements, and unrelated features are not reasons to add exclusions.
- **Non-Functional Requirements** — keep specific, significant security, compatibility, concurrency, integrity, or performance constraints. Do not add generic wishes for template completeness.
- **Additional Notes** — relevant non-binding context only, not a duplicate of the main sections. A commitment that affects correctness or acceptance belongs in Requirements, and in acceptance criteria when it is verifiable — not only in Notes.
- **Technical Approach** — optional high-level context. Do not invent an implementation. Do not delete an agreed technical constraint merely because it is technical.
- **Related Links** — an inline reference or a compact section. Every link kept has a clear role: dependency, prior behavior, parent scope, specification, or evidence. Do not list every neighbouring Jira key, and do not invent relationships.

Example: if a story must account for a retry duration that can exceed the timer interval, that belongs in Requirements and in the verifiable result — not hidden in Additional Notes. Keep the conditions of the request at hand; do not introduce a general timer or retry policy.

## Writing Guidelines

### Persona format (when a user role applies)
```
As a [user persona/role]
I want [goal/desire]
So that [benefit/value]
```

Use this when a real user role is involved. For a technical enabler or a decision ticket, state the outcome and its value directly instead of inventing a persona.

### INVEST Principles
- **I**ndependent — deliverable separately
- **N**egotiable — details can be refined
- **V**aluable — delivers clear value
- **E**stimable — team can estimate effort
- **S**mall — completable within one sprint
- **T**estable — clear verification criteria

## Best Practices

### Do's ✓
1. Explain the value and the outcome, whoever the beneficiary is
2. Make acceptance criteria specific and verifiable
3. Cover material error scenarios and boundaries
4. Keep binding constraints in Requirements
5. Use consistent domain terminology
6. Explain what each linked ticket contributes

### Don'ts ✗
1. Don't invent an end-user persona for technical or decision work
2. Don't be vague — "improve performance" needs metrics
3. Don't skip acceptance criteria
4. Don't add sections the deliverable does not need
5. Don't add "Out of Scope" for neighbouring topics that were never in scope
6. Don't put test code, fixtures, or detailed test setup in the story
7. Don't over-specify implementation — leave the "how" to developers
8. Don't leave a binding constraint in Additional Notes

## Quick Reference Checklist

- [ ] Purpose clearly explains the value and context
- [ ] The chosen sections match the actual deliverable
- [ ] Requirements are specific, and every binding constraint is there
- [ ] Acceptance criteria are distinct, verifiable, and match the result type
- [ ] Material error and boundary conditions are covered
- [ ] Verification fits the work type, or is correctly absent for decision work
- [ ] Each optional section present is doing real work
- [ ] Each linked ticket's relationship is explained
- [ ] Story is sized for one sprint
- [ ] Technical approach is outlined only if needed, and not over-specified
- [ ] Non-functional requirements included only if significant

A missing optional section is not a defect.

For deep-dive guidance on each section, see [references/section-details.md](references/section-details.md).
For common pitfalls with before/after examples, see [references/pitfalls.md](references/pitfalls.md).
For a complete example story, see [references/example.md](references/example.md).
For JIRA markup conversion, see [references/jira.md](references/jira.md).
