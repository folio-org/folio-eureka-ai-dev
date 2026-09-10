# Example Skill Feedback Reports

Both examples below are illustrative only. Do not copy their facts into real reports.

## Example 1 — reported friction

### Issue Title

```text
[skill-feedback] write-user-story | process-friction
```

### Issue Body

```md
# Skill Feedback Report

## Metadata
- Skill: `write-user-story`
- Primary feedback type: `process-friction`
- Work context: `product-requirement`

## What Should Improve First
The skill should ask one or two scope questions before drafting when the input is broad. The first draft moved too quickly into a full story and required manual correction around boundaries and acceptance criteria.

## What Worked Well
The final structure was useful after refinement.

## Validated Session Summary
The skill was used to draft a user story. The session produced a usable artifact, but the user had to correct scope framing and remove implementation-level details from the acceptance criteria.

## Observed Friction Signals
- Repeated scope corrections
- Acceptance criteria mixed expected behavior with implementation detail
- Initial draft assumed details that were not present in the prompt
```

## Example 2 — no major issues

The user reported that the scope and acceptance criteria were usable without corrections. There is no reported problem, so `What Should Improve First` and `Observed Friction Signals` are omitted rather than filled with invented content.

### Issue Title

```text
[skill-feedback] write-user-story | no-major-issues
```

### Issue Body

```md
# Skill Feedback Report

## Metadata
- Skill: `write-user-story`
- Primary feedback type: `no-major-issues`
- Work context: `product-requirement`

## Validated Session Summary
The skill was used to draft a user story for a configurable page-size limit. The user confirmed that the scope and acceptance criteria were usable as produced and made no corrections before using the artifact.
```
