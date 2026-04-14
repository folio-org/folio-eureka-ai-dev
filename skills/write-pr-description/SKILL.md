---
name: write-pr-description
description: >-
  Use when writing, generating, or drafting a pull request description. Always use this skill
  when the user asks to "write a PR description", "create a PR", "draft a pull request",
  "generate PR text", or similar. Produces a complete, structured PR description following
  the team's conventions: ticket-key title, Purpose, Approach with implementation details,
  and a Pre-Review Checklist.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
---

# Write PR Description

You are a senior software engineer writing a pull request description for this repository.
Follow the conventions in this skill exactly.

## Step 1 — Collect context

Run these commands in order.

Get the current branch name:

```bash
git --no-pager rev-parse --abbrev-ref HEAD
```

Get the list of changed files:

```bash
git --no-pager diff --name-only master
```

Get the full diff:

```bash
git --no-pager diff --no-prefix --unified=100000 --minimal origin/master...HEAD
```

Get the commit log for this branch:

```bash
git --no-pager log --oneline origin/master..HEAD
```

Read all output before proceeding. If the diff for a specific file is needed:

```bash
git --no-pager diff --no-prefix --unified=100000 --minimal origin/master...HEAD -- <file>
```

If the user has not provided the Jira ticket key, ask for it before writing the description.

## Step 2 — Write the PR description

Produce a single markdown document using the structure below. Follow every rule in each section.

---

### Title

Format: `## TICKET-KEY: <title>`

Rules:
- Start with the Jira ticket key (e.g. `APPPOCTOOL-85:`).
- Copy the title verbatim from the Jira user story title. Only use the purpose of changes when explicitly told so.
- Sentence case; no trailing period.
- Keep under ~80 characters.

**Good:** `## APPPOCTOOL-85: Generalize Kafka consumer tenant filter to support custom event types`

**Avoid:**
- No ticket key or vague title
- Ticket key only with no description
- Passive voice or overly long titles

---

### Purpose

One or two sentences answering:
1. **Why** are these changes needed?
2. A user story reference: `US: [TICKET-KEY](url)`

Do **not** describe how the change is implemented here — that belongs in Approach.

---

### Approach

Two parts, always in this order:

**Summary (2–3 sentences):** A high-level technical narrative. The reader should understand the main idea without reading any code.

**Implementation details (bullet list):** Each bullet covers one concrete, self-contained change.

Rules for implementation details:
- **One bullet per logical change** — a new class, a changed contract, a new config property, etc.
- **Up to 2 sentences per bullet.** First sentence: what was done. Optional second: why, or a notable consequence.
- **No test changes** — omit added/updated tests unless the PR is exclusively about testing.
- **No documentation changes** — omit README or Javadoc updates unless the PR is exclusively about documentation.
- Use backticks for class names, method names, property keys, and values.
- Start each bullet with a past-tense verb: *Introduced*, *Changed*, *Added*, *Replaced*, *Removed*.

---

### Pre-Review Checklist

Always include the full checklist. Tick items that apply; leave the rest unchecked. Do not delete any item.

```markdown
- [ ] **Self-reviewed Code** — Reviewed code for issues, unnecessary parts, and overall quality.
- [ ] **Change Notes** — NEWS.md updated with clear description and issue key.
- [ ] **Testing** — Confirmed changes were tested locally or on dev environment.
- [ ] **Dependent module build verification** — Ran manually when library changes impact downstream modules.
  > Actions → Verify Dependent Modules → Run workflow → select branch → Run.
- [ ] **Breaking Changes (if any)** — Handled if changes affect integration with other services.
- [ ] **New Properties / Environment Variables** — Updated README.md if new configs were added.
- [ ] **Environment Recreation Test (if needed)** — Verified that environment can be recreated successfully.
```

Tick **Self-reviewed Code**, **Change Notes**, and **Testing** by default (replace `[ ]` with `[x]`).
Tick **Dependent module build verification** only if a shared library changes its public API.
Tick **Breaking Changes** only if an interface, configuration key, or serialized format changes incompatibly.
Tick **New Properties / Environment Variables** only if new config keys are added.
Tick **Environment Recreation Test** only if infrastructure or startup configuration changes.

---

## Step 3 — Output

Print the complete PR description as a single markdown code block, ready to paste into GitHub.

For the full canonical guide with detailed examples, see [../../docs/pr/pr-description.md](../../docs/pr/pr-description.md).
