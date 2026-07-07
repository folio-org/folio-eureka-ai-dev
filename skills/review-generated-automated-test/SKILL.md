---
name: review-generated-automated-test
description: "Use this skill whenever performing a code review of Cypress E2E tests for the FOLIO Stripes framework. Triggers include: any mention of 'code review', 'review my test', 'review git diff', 'PR review', or 'check my Cypress test'. Also use when the user asks to analyze a git diff, validate test structure, check for interactor usage, verify tags/permissions/cleanup hooks, or produce a code review markdown report. Do NOT use for generating new tests from scratch, non-FOLIO projects, or general code review tasks unrelated to Cypress/FOLIO."
---

# FOLIO Stripes — Cypress E2E Code Review

## Overview

This skill produces structured code review reports for Cypress E2E tests written against the FOLIO Stripes framework. Reviews are output as a Markdown file named `<BRANCH_NAME_CODEREVIEW>.md`.

## Quick Reference

| Task | Command |
|------|---------|
| Get changed files | `git diff --name-only master` |
| Get full diff | `git --no-pager diff --no-prefix --unified=100000 --minimal origin/master...HEAD` |
| Output file | `<BRANCH_NAME_CODEREVIEW>.md` |

---

## Step-by-Step Workflow

### Step 1 — Gather the diff

Run both commands before reviewing anything. Never review partial diffs.

```bash
# 1. List changed files
git diff --name-only master

# 2. Get the complete diff (all changed files, full context)
git --no-pager diff --no-prefix --unified=100000 --minimal origin/master...HEAD
```

**Diff line prefix legend:**

| Prefix | Meaning |
|--------|---------|
| `+` | Line added |
| `-` | Line removed |
| ` ` (space) | Line unchanged |
| `@@` | Hunk header |

### Step 2 — Determine the branch name

Use the branch name as the output filename: `<BRANCH_NAME_CODEREVIEW>.md`.

### Step 3 — Review against all checklist items (below)

### Step 4 — Write the report using the required format (below)

---

## Review Checklist

Work through every item for every changed file before writing the report.

### 1. Fragment & Helper Reuse
- Are existing fragments, functions, and utilities being used rather than duplicated?
- Search `cypress/support/fragments/` for relevant page objects before flagging missing abstractions.
- Is logic that could live in a fragment written inline in the spec instead?

### 2. Interactors vs Raw Selectors
Prefer interactors from `@interactors/html` over raw Cypress selectors.

```javascript
// ✅ Preferred
cy.do(Button('Save').click());
cy.expect(TextField('Name').has({ value: 'test' }));

// ❌ Avoid when an interactor exists
cy.get('[data-testid="save-button"]').click();
```

Flag every raw selector that has a known interactor equivalent.

### 3. Describe Block Hierarchy
Must mirror the FOLIO module/feature hierarchy:

```javascript
describe('Module', () => {
  describe('Feature Area', () => {
    describe('Specific Function', () => {
      it('C##### Test name', { tags: [...] }, () => { ... });
    });
  });
});
```

Flag: missing levels, incorrect order, or hierarchy that doesn't match the test case path.

### 4. Tags
Every `it` block must have exactly 3 tag components:

```javascript
{ tags: ['extendedPath', 'spitfire', 'C627455'] }
```

| Position | Valid values |
|---|---|
| Test group | `smoke`, `criticalPath`, `extendedPath`; append `ECS` for consortia |
| Dev team | lowercase team name: `spitfire`, `thunderjet`, `eureka`, etc. |
| Test ID | `C######` exact identifier |

Flag: missing tags, wrong order, wrong group name, missing test ID.

### 5. Test Data Cleanup
- All entities **created in the test** must be deleted in `after()` via API.
- **Default / pre-existing entities must NOT be deleted**: service points, locations, material types, loan types, institutions, campuses, libraries, etc.
- Check that `after()` exists and covers every created entity.

### 6. Import Paths
- Verify all import paths are correct and consistent with the project structure.
- Flag relative paths that should be absolute (or vice versa per project convention).
- Flag imports of non-existent or renamed modules.

### 7. Forbidden Patterns
| Pattern | Rule |
|---|---|
| `cy.pause()` | Never allowed in committed code |
| `cy.wait(ms)` | Flag every usage; prefer fragment `waitLoading()` methods |
| Hardcoded test data without `getRandomPostfix()` | Flag — causes data conflicts in parallel runs |

### 8. Code Duplication & Reusability
- Is logic copy-pasted from another test that could be extracted to a fragment?
- Are `before()`/`after()` hooks unnecessarily duplicated across `it` blocks?

### 9. Naming Conventions
- Test data: `AT_C######_Description_${randomPostfix}`
- Fragment methods: verb-noun camelCase (`verifyRecordExists`, `fillName`, `openForm`)
- Spec files: lowercase hyphenated (`call-number-browse.cy.js`)
- Variables: descriptive camelCase, no single-letter names outside loops

### 10. Parallel Run Safety
- Test data must be unique per run (use `getRandomPostfix()`).
- No shared mutable state between `it` blocks.
- No reliance on test execution order.

---

## Report Format

Output a Markdown file with this exact structure:

````markdown
# Code Review for ${feature_description}

Brief overview: purpose of the change, relevant context, files involved.

# Suggestions

## ${emoji} ${Summary of suggestion}
* **Priority**: ${🔥 / ⚠️ / 🟡 / 🟢}
* **File**: `relative/path/to/file.cy.js`
* **Details**: Clear explanation of the issue and why it matters.
* **Example** (if applicable): what the current code does wrong.
* **Suggested Change** (if applicable):
```javascript
// improved code here
```

## (next suggestion...)

# Summary
High-level recap: overall quality, top issues to fix, positive highlights.
````

---

## Priority Levels

| Emoji | Level | When to use |
|---|---|---|
| 🔥 | Critical | Breaks tests, causes false positives/negatives, data leaks between runs |
| ⚠️ | High | Violates required standards (missing tags, missing cleanup, `cy.pause()`) |
| 🟡 | Medium | Code quality issues, raw selectors with interactor equivalents, duplicated logic |
| 🟢 | Low | Naming, style, minor readability improvements |

## Suggestion Type Emojis

| Emoji | Code | When to use |
|---|---|---|
| 🔧 | `:wrench:` | Change required — concern or refactor worth addressing |
| ❓ | `:question:` | Genuine question requiring a response with sufficient context |
| ⛏️ | `:pick:` | Nitpick — no action required; stylistic or formatting |
| ♻️ | `:recycle:` | Refactor suggestion — actionable, not a nitpick |
| 💭 | `:thought_balloon:` | Concern, alternative solution, or walkthrough for understanding |
| 👍 | `:+1:` | Genuine praise for something well thought out — use sparingly |
| 📝 | `:memo:` | Explanatory note or relevant context; no action needed |
| 🌱 | `:seedling:` | Observation with future implications; not a change request |

---

## Example Suggestion Blocks

### Raw selector instead of interactor
```markdown
## ♻️ Replace raw selector with interactor
* **Priority**: 🟡
* **File**: `cypress/e2e/inventory/settings/call-number-browse.cy.js`
* **Details**: A raw Cypress selector is used where a built-in interactor exists. Raw selectors are brittle and couple tests to DOM implementation details.
* **Example**: `cy.get('[data-testid="save-button"]').click();`
* **Suggested Change**:
```javascript
cy.do(Button('Save').click());
```
```

### Missing cleanup in after()
```markdown
## 🔧 Created entity not deleted in after() hook
* **Priority**: ⚠️
* **File**: `cypress/e2e/orders/order-lines.cy.js`
* **Details**: `testData.organization` is created via API in `before()` but never deleted in `after()`. This pollutes the environment and can cause failures in subsequent runs.
* **Suggested Change**:
```javascript
after(() => {
  cy.getAdminToken().then(() => {
    Organizations.deleteOrganizationViaApi(testData.organization.id);
  });
});
```
```

### cy.pause() present
```markdown
## 🔧 Remove cy.pause() before merging
* **Priority**: 🔥
* **File**: `cypress/e2e/inventory/items/item-create.cy.js`
* **Details**: `cy.pause()` halts test execution and must never be committed. This will cause CI runs to hang indefinitely.
```

---

## Critical Rules

- **Always run both git commands** before starting the review — never review from memory or partial context.
- **Never flag suppressed warnings** (`#pragma warning disable` equivalents) — assume they are intentional.
- **Address TODO comments** found in the diff — include them as suggestions.
- **Do not overwhelm** — prioritize 🔥 and ⚠️ items; group related 🟡/🟢 items where possible.
- **Always include file paths** in every suggestion.
- **Output file name**: `<BRANCH_NAME_CODEREVIEW>.md` — derive branch name from git context.