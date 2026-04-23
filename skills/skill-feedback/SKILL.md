---
name: skill-feedback
description: Use when a user has finished using one installed skill and wants to preserve actionable feedback about that skill while the session context is still fresh
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
---

# Skill Feedback

## Overview

Use this after a completed skill session.

**Core principle:** produce one `machine-prepared, user-validated` report about one skill, show the full draft, then submit or hand it off without surprises.

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
- No hidden fields in `v1`.
- Never auto-submit.
- Show the user the destination repo, issue title, and full body before submission.
- Infer conservatively. If context is unclear, use `unknown` or leave the field empty.
- Describe observed friction, not the user's emotions.
- Do not require FOLIO module classification.

## Quick Reference

| Step | Requirement |
|------|-------------|
| Target | One skill, one completed session |
| Contract | Use [references/report-template.md](references/report-template.md) for fields, enums, title, and body shape |
| Intake | One required question, one optional question when useful |
| Draft | Show all fields, inferred values, destination repo, title, and full body |
| Decision | `approve`, `edit`, or `cancel` |
| Submit | GitHub tool, then `gh`, then manual copy/paste |

If this repository includes a manual GitHub issue template, keep it aligned with [references/report-template.md](references/report-template.md). The skill must still work without that template.

## Workflow

1. Identify the target skill from the session.
2. If more than one candidate skill appears plausible, ask the user to confirm which skill the report is about.
3. Read the session and extract only low-risk, useful signals:
   - what the user was trying to do;
   - what artifact the session produced;
   - repeated corrections or reframing;
   - format problems, scope drift, or missing context;
   - likely `work_context` and optional `project_hint`.
4. Ask the user the minimum intake needed:
   - Required: `What should this skill improve first?`
   - Optional when useful: `What worked well?`
5. Draft the report using [references/report-template.md](references/report-template.md). Use [references/example-report.md](references/example-report.md) only as a style example.
6. Show the entire draft to the user, including:
   - all fields;
   - all inferred values;
   - the destination repo `folio-org/folio-eureka-ai-dev`;
   - the full issue title;
   - the full Markdown body.
7. Ask the user to choose one of:
   - `approve`
   - `edit`
   - `cancel`
8. If the user chooses `edit`, update the draft and show the full revised version again.
9. If the user chooses `cancel`, stop without creating an issue.
10. Only if the user chooses `approve`, submit using the first available path:
   - a GitHub issue creation tool for repo `folio-org/folio-eureka-ai-dev`;
   - write the approved body to `/tmp/skill-feedback.md`, then run `gh issue create --repo folio-org/folio-eureka-ai-dev --label skill-feedback --title "<title>" --body-file /tmp/skill-feedback.md`;
   - manual submission by handing the user the repo URL, final title, and final Markdown body.

## Drafting Rules

- Prefer explicit skill usage from the conversation.
- If the user named the skill directly, trust that.
- If the session suggests multiple skills, do not guess.
- Never merge feedback for multiple skills into one report.
- Summarize instead of copying large transcript chunks.
- Do not include secrets, tokens, private URLs, or unnecessary identifiers.
- Avoid long verbatim excerpts.
- Omit optional sections that add no value.

Good:

- `Work context: product-requirement`
- `Project hint: unknown`
- `Observed friction signals: repeated scope corrections`

Bad:

- `The user was frustrated`
- `The project was definitely mod-orders`
- `The prompt design is weak`

## FOLIO Handling

- `project_hint` may contain a FOLIO module, initiative, or area, or remain empty.
- Use FOLIO terminology only when it is visible in the session and useful for the report.
- Keep the report about the skill itself, even when the work happened in a FOLIO context.

## Common Mistakes

- Turning the intake into a survey instead of a short follow-up.
- Treating `project_hint` as required.
- Hiding inferred fields from the user.
- Submitting without re-showing the full draft after edits.
- Inferring emotions or intent from sparse evidence.
- Turning the report into a tuning plan.
- Copying raw transcript chunks into the issue body.

## Completion Check

Before creating the issue, verify all of these are true:

- the report is about one skill only;
- the user answered the required improvement question;
- the destination repo `folio-org/folio-eureka-ai-dev` was shown to the user;
- the full issue title and body were shown to the user;
- the user had a clear `approve`, `edit`, or `cancel` choice;
- the final version reflects any user edits;
- nothing hidden will be submitted.
