# Feedback Skill Design

Date: 2026-04-22
Status: Drafted after brainstorming approval

## Goal

Design a manually invoked `feedback skill` for this repository of FOLIO-oriented skills.

The skill is used after a user finishes working with a specific skill, for example `write-user-story`. Its job is to produce a useful, low-friction, user-validated feedback report about that skill and publish it to GitHub Issues in a consistent format.

The primary goal is to collect improvement signals about the skill itself, even when the user population is small and informal feedback would otherwise be lost.

## Scope

The `feedback skill` must:

- run as a manual, post-session workflow;
- determine which skill the report is about;
- analyze the current session and infer only useful, low-risk context;
- ask the user a very short feedback intake;
- generate a full draft report;
- show the complete draft to the user before submission;
- allow the user to edit, approve, or cancel;
- create one GitHub Issue after explicit user approval.

## Non-Goals

This version does not:

- auto-run at the end of every session;
- decide how feedback should be triaged weekly;
- decide how skills should be tuned from the collected feedback;
- run evaluations, dashboards, or analytics pipelines;
- require module-level or workflow-level tagging in FOLIO;
- collect reporter role as a required signal.

## Design Principles

- Feedback is collected per skill, not per FOLIO module.
- The user must see the entire issue draft before submission.
- No hidden fields are allowed in `v1`.
- Structured fields should be normalized enough for aggregation, but the intake must remain short.
- Inference must stay conservative. If context is unclear, use `unknown` or leave the field empty.
- The report should capture observed friction, not guess the user's emotions.

## User Flow

1. The user manually invokes `feedback skill` after using another skill.
2. The skill identifies the target skill from the session history.
3. If the target skill is ambiguous, the skill asks the user to confirm it.
4. The skill analyzes the current session and prepares a draft understanding of:
   - likely skill used;
   - likely work context;
   - possible project hint;
   - likely feedback type;
   - observed friction signals;
   - a concise session summary.
5. The skill asks the user for a short feedback intake.
6. The skill assembles a complete GitHub Issue draft.
7. The user reviews the full draft and chooses one of:
   - `approve`
   - `edit`
   - `cancel`
8. Only `approve` creates the GitHub Issue.

## User Intake

### Required question

`What should this skill improve first?`

### Optional question

`What worked well?`

No additional required questions are part of `v1`.

## Inferred Context

The skill may infer the following fields from the session:

- `skill_name`
- `primary_feedback_type`
- `work_context`
- `project_hint`
- `validated_session_summary`
- `observed_friction_signals`
- `skill_fit_assessment`

All inferred fields must be visible to the user in the final draft and may be edited or cleared before submission.

## Report Schema

### Required fields

- `skill_name`
- `primary_feedback_type`
- `what_should_improve_first`
- `validated_session_summary`

### Optional fields

- `work_context`
- `project_hint`
- `what_worked_well`
- `observed_friction_signals`
- `skill_fit_assessment`

### Fixed field

- `report_type = machine-prepared, user-validated`

## Normalized Enums

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

## Field Semantics

- `skill_name`: the skill the report is about; inferred first, then confirmed or corrected by the user.
- `primary_feedback_type`: the dominant category of the reported problem; may be corrected by the user.
- `work_context`: a normalized description of the type of work the skill was used for; may remain `unknown`.
- `project_hint`: short optional free text inferred from the session or added by the user; may be empty.
- `what_should_improve_first`: the main human feedback signal; required.
- `what_worked_well`: optional positive signal.
- `validated_session_summary`: a concise, user-visible summary of what happened in the session.
- `observed_friction_signals`: short bullets describing repeated corrections, scope drift, wrong format, or similar evidence.
- `skill_fit_assessment`: a cautious machine judgment on whether the skill appears to have been used for an intended kind of task.

## Draft Generation Rules

The skill must:

- rely on observed behavior from the session;
- avoid psychologizing the user;
- avoid confident claims without evidence;
- use short summaries instead of long copied conversation excerpts;
- avoid including secrets, tokens, sensitive internal URLs, or unnecessary identifiers;
- keep any uncertain field as `unknown` or empty.

Good examples:

- `Work context: product-requirement`
- `Project hint: unknown`
- `Observed friction signals: repeated scope corrections`

Bad examples:

- `The user was frustrated with the skill`
- `The project was clearly mod-orders`
- `The skill failed because its prompt is weak`

## GitHub Issue Format

### Title

`[skill-feedback] {skill_name} | {primary_feedback_type}`

Example:

`[skill-feedback] write-user-story | missing-domain-context`

### Labels

Minimum label set:

- `skill-feedback`

Optional future label if the repository adopts a stable taxonomy:

- `skill:{skill_name}`

### Body

The issue body should follow this structure:

```md
# Skill Feedback Report

## Metadata
- Skill: `write-user-story`
- Primary feedback type: `missing-domain-context`
- Work context: `product-requirement`
- Project hint: `unknown`
- Skill fit assessment: `expected`
- Report type: `machine-prepared, user-validated`

## What Should Improve First
The skill should ask sharper scoping questions before drafting the final artifact.

## What Worked Well
The overall structure of the output was useful and easy to refine.

## Validated Session Summary
The skill was used to draft a user-story-like artifact. The result was usable, but the session required repeated corrections around scope and domain framing.

## Observed Friction Signals
- Repeated scope corrections
- Output mixed requirements with implementation detail
```

If an optional section has no useful content, it may be omitted from the final issue body.

## FOLIO-Specific Handling

This skill operates in a repository of FOLIO-oriented skills, but the feedback report is still centered on the skill itself.

Rules:

- Do not require the user to classify the report by FOLIO module.
- Allow `project_hint` to contain a FOLIO area, module, initiative, or remain empty.
- Allow `work_context` to describe the kind of work even when the exact FOLIO target is unclear.
- Use FOLIO context only when it is visible in the session and useful for interpreting the report.

## Required Review Gate

Before creating the GitHub Issue, the skill must show the user:

- all normalized fields;
- all inferred fields;
- the full issue title;
- the full Markdown issue body.

No content may be submitted if it was not shown to the user in the final draft.

## Success Criteria

The design is successful if `feedback skill` can:

- create one consistent report per skill session;
- keep the user intake very short;
- produce a report that is detailed enough to review later;
- avoid hidden metadata or surprising submission behavior;
- allow the user to fully validate the report before publication.

## Out of Scope Follow-Up

Later work may define:

- weekly review process;
- label taxonomy beyond `skill-feedback`;
- dashboards or aggregation scripts;
- how the collected reports should influence skill revisions.
