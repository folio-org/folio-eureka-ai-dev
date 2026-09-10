---
name: skill-feedback
description: Use when a user wants to record feedback about one completed skill session while the session context is still available.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
---

# Skill Feedback

## Overview

Use this after a completed skill session.

**Core principle:** record what the user actually reported about one skill, show the exact artifact that will be published, and submit only that.

Feedback created by this skill always targets `folio-org/folio-eureka-ai-dev`.

## When to Use

Use when:

- a user wants to leave feedback on a skill they just used;
- the session is complete and still has enough context to summarize;
- the feedback is about skill quality, not a generic product or repository issue.

Do not use when:

- the user is still in the middle of using the skill;
- the report is really about an unrelated bug or repo problem;
- the conversation is about downstream tuning strategy.

## Hard Rules

- One report covers one skill and one completed session.
- Never auto-submit. Publish only after explicit approval of the displayed version.
- A positive or no-major-issues report is a complete, valid report.
- Infer conservatively. Omit optional fields you cannot support from the session.
- Describe observed friction, not the user's emotions.
- No secrets, tokens, or private internal URLs.
- Do not require FOLIO module classification.

## Quick Reference

| Step | Requirement |
|------|-------------|
| Target | One skill, one completed session |
| Contract | Use [references/report-template.md](references/report-template.md) for fields, enums, title, and body shape |
| Intake | Use the feedback the user already gave; at most one neutral question |
| Review | One preview of the exact publishable artifact |
| Decision | `approve`, `edit`, or `cancel` |
| Submit | Available GitHub issue tool, then configured `gh`, then manual |

If this repository includes a manual GitHub issue template, keep it aligned with [references/report-template.md](references/report-template.md). The skill must still work without that template.

## Workflow

1. Identify the target skill. A skill the user named explicitly wins over inference.
2. Ask which skill the report is about only when more than one candidate is genuinely plausible. Keep one skill per report.
3. Read the session and extract only low-risk, useful signals: what the user was trying to do, what the session produced, repeated corrections, format or scope problems.
4. Settle intake (see below).
5. Draft the report using [references/report-template.md](references/report-template.md). Use [references/example-report.md](references/example-report.md) only as a style example.
6. Show one publication preview and ask for a decision (see below).
7. On `edit`, revise and show the full updated preview again, then ask again.
8. On `cancel`, stop without creating an issue.
9. On approval, submit (see below).
10. After confirmed success, return the issue URL and a short confirmation. Do not repeat the approve/edit/cancel menu or re-print the whole report.

### Intake

Use feedback already supplied by the user. If their feedback is not yet clear, ask one neutral question: "What feedback would you like to record—what worked well, anything to improve, or no major issues?" A positive report does not require an improvement suggestion. Do not infer dissatisfaction from ordinary iteration or infer satisfaction from silence.

- `Nothing to improve` is valid positive or no-major-issues feedback, not a cancel.
- Explicit `cancel`, `do not record this`, or a withdrawal ends the workflow with no submission.
- Do not ask questions only to populate optional metadata.
- Do not offer the user a list of suspected problems without supporting context.

### One review artifact

Present one publication preview: repository (`folio-org/folio-eureka-ai-dev`), label (`skill-feedback`), the exact issue title, and the complete Markdown body. All agent-added content and inferred metadata must be visible in that preview. Do not add a separate "Draft fields" review. Ask once whether to approve, edit, or cancel the displayed version.

Clear natural-language agreement counts as approval; the user does not have to type the word `approve`. If the title, body, or any added field changes afterwards, show the full updated preview and get approval again. Moving an unchanged approved artifact between transport paths does not by itself need a second conversational approval; runtime permission prompts still apply.

### Submission

After approval, use an available GitHub issue-creation tool; if that path is unavailable or explicitly denied, try an already configured local `gh` CLI. Otherwise provide the approved artifact for manual submission. A timeout or missing response is not proof that creation failed: verify the outcome before attempting another write. Read [Submission](references/submission.md) before publishing.

## Drafting Rules

- Prefer explicit skill usage from the conversation.
- If the session suggests multiple skills, do not guess.
- Never merge feedback for multiple skills into one report.
- Summarize instead of copying large transcript chunks.
- Do not include secrets, tokens, private URLs, or unnecessary identifiers.
- Omit optional sections that add no value. Do not emit empty headings or `None` filler.

Good:

- `Work context: product-requirement`
- `Primary feedback type: no-major-issues`
- `Observed friction signals: repeated scope corrections`

Bad:

- `The user was frustrated`
- `The project was definitely mod-orders`
- An improvement paragraph invented so the section is not empty

## FOLIO Handling

- `project_hint` may contain a FOLIO module, initiative, or area, or be omitted.
- Use FOLIO terminology only when it is visible in the session and useful for the report.
- Keep the report about the skill itself, even when the work happened in a FOLIO context.

## Common Mistakes

- Pressing for a problem when the user reported that the skill worked.
- Turning the intake into a survey instead of a short follow-up.
- Reviewing draft fields separately from the artifact that will be published.
- Submitting without re-showing the full preview after edits.
- Writing a small approved body to a temporary file as a routine step.
- Retrying a write after an unclear outcome without verifying it first.
- Inferring emotions or intent from sparse evidence.
- Copying raw transcript chunks into the issue body.

## Completion Checklist

Before creating the issue, verify all of these are true:

- the target skill and the user's feedback intent are clear, and the report covers one skill only;
- no complaint and no positive outcome was invented;
- optional and removed metadata were not added automatically;
- the exact artifact to be published was shown: repository, label, title, and full body;
- the version the user approved is the current version;
- the submitted payload matches that approved version, or the manual/uncertain outcome was stated honestly;
- nothing hidden and nothing sensitive is included.
