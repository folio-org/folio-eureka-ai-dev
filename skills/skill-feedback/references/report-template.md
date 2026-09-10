# Skill Feedback Report Template

Use this file as the portable report contract for `skill-feedback`.

This file is intentionally independent from any repository-local `.github/ISSUE_TEMPLATE` layout. A repository may provide a matching GitHub issue template, but this template must remain usable even when the skill is installed on its own.

Default destination repo for reports created by this skill:

- `folio-org/folio-eureka-ai-dev`

## Issue Title

```text
[skill-feedback] {skill_name} | {primary_feedback_type}
```

## Fields

### Required

- `skill_name`
- `primary_feedback_type`
- `validated_session_summary`

### Conditional

- `what_should_improve_first` — include when the user reported a problem or a suggestion. It is enough to describe the needed improvement or the observed problem clearly; the user does not have to propose a technical solution.

### Optional

- `work_context`
- `project_hint`
- `what_worked_well`
- `observed_friction_signals`

## Allowed Enums

### `primary_feedback_type`

- `incorrect-or-misleading-output`
- `missing-domain-context`
- `poor-structure-or-format`
- `process-friction`
- `unclear-guidance`
- `no-major-issues`
- `other`

Use `no-major-issues` for explicitly positive or no-major-issues feedback with no specific corrective request. When feedback is mixed, use the matching problem category and, if useful, add `What Worked Well`.

### `work_context`

- `frontend`
- `backend`
- `product-requirement`
- `bug-investigation`
- `documentation`
- `ops-infrastructure`
- `cross-functional`
- `unknown`

Do not fill `work_context` with `unknown` automatically. Unknown optional fields are normally omitted.

## Markdown Body

Section order:

1. `# Skill Feedback Report`
2. `## Metadata` — Skill and Primary feedback type, then only the optional Work context / Project hint values that are actually useful.
3. `## What Should Improve First` — conditional.
4. `## What Worked Well` — optional.
5. `## Validated Session Summary` — required.
6. `## Observed Friction Signals` — optional, observable relevant facts only.

```md
# Skill Feedback Report

## Metadata
- Skill: `{skill_name}`
- Primary feedback type: `{primary_feedback_type}`

## What Should Improve First
{what_should_improve_first}

## Validated Session Summary
{validated_session_summary}
```

A positive or no-major-issues report is complete with metadata and a substantive session summary. `What Worked Well` may be added, but do not invent specific strengths to fill the section.

## Omission Rules

- Omit any conditional or optional section that has no useful content.
- Do not emit empty headings, placeholders, boilerplate `None`, or an invented improvement paragraph.
- Use `unknown` only when it adds value over omitting the field.
- Do not paste large raw transcript excerpts.
- Do not include secrets, tokens, or private internal URLs.
- Do not edit older issues to match this contract.
