# Skill Feedback Report Template

Use this file as the portable report contract for `skill-feedback`.

This file is intentionally independent from any repository-local `.github/ISSUE_TEMPLATE` layout. A repository may provide a matching GitHub issue template, but this template must remain usable even when the skill is installed on its own.

Default destination repo for reports created by this skill:

- `folio-org/folio-eureka-ai-dev`

## Issue Title

```text
[skill-feedback] {skill_name} | {primary_feedback_type}
```

## Required Fields

- `skill_name`
- `primary_feedback_type`
- `what_should_improve_first`
- `validated_session_summary`
- `report_type = machine-prepared, user-validated`

## Optional Fields

- `work_context`
- `project_hint`
- `what_worked_well`
- `observed_friction_signals`
- `skill_fit_assessment`

## Allowed Enums

### `primary_feedback_type`

- `incorrect-or-misleading-output`
- `missing-domain-context`
- `poor-structure-or-format`
- `process-friction`
- `unclear-guidance`
- `other`

### `work_context`

- `frontend`
- `backend`
- `product-requirement`
- `bug-investigation`
- `documentation`
- `ops-infrastructure`
- `cross-functional`
- `unknown`

### `skill_fit_assessment`

- `expected`
- `borderline`
- `likely-misfit`
- `unknown`

## Markdown Body

```md
# Skill Feedback Report

## Metadata
- Skill: `{skill_name}`
- Primary feedback type: `{primary_feedback_type}`
- Work context: `{work_context}`
- Project hint: `{project_hint}`
- Skill fit assessment: `{skill_fit_assessment}`
- Report type: `machine-prepared, user-validated`

## What Should Improve First
{what_should_improve_first}

## What Worked Well
{what_worked_well}

## Validated Session Summary
{validated_session_summary}

## Observed Friction Signals
- {observed_friction_signal_1}
- {observed_friction_signal_2}
```

## Omission Rules

- Omit any optional section that has no useful content.
- Use `unknown` only when it adds value over an empty field.
- Do not paste large raw transcript excerpts.
- Do not include secrets, tokens, or private internal URLs.
