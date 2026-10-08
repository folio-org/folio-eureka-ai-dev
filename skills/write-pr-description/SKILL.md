---
name: write-pr-description
description: >-
  Use when a pull request needs to be written or opened for the current branch — "write a PR
  description", "create a PR", "draft a pull request", "open a PR for this branch", "generate PR
  text" — and when an existing PR description needs to be rewritten to team conventions.
license: Apache-2.0
metadata:
  author: folio-org
  version: "2.4.0"
---

# Write PR Description

Prepare a title and body from the current changes, using the repository's PR template or the
[default template](references/example.md). Show the text before publishing.

Draft-only is the default and needs neither `gh` nor network access. Create mode applies when
the user asks to open, create or raise a PR; it includes any necessary push after text approval.

## Step 1 — Check for uncommitted task files

Read `git status --short`, including untracked files. Identify files that belong to the task;
leave unrelated changes untouched and name them briefly. Ask if their scope is unclear.

In create mode, if task files are uncommitted, show their paths and ask:
"There are uncommitted task files. Commit them before preparing the PR?"
**Stop and wait.** Approval to create a PR alone does not approve this commit.

- If the user agrees, stage and commit only those files, including intended untracked files.
  Use explicit paths for both operations; `git commit --only` keeps unrelated staged files out
  of the commit. See the [scoped commit example](references/example.md#commit-task-files).
- If the user declines, leave the files untouched and stop creation.
- In draft-only mode, describe the intended changes without staging or committing.

## Step 2 — Read the changes

Resolve the base in this order:

1. The base named by the user or calling workflow.
2. The branch's existing PR base, when available, or the active task context.
3. `git symbolic-ref --short refs/remotes/origin/HEAD`, else `origin/master`, else `origin/main`.

Use `origin/<name>` for branch bases and preserve names containing `/`.
An upstream naming a different branch is a base hint to confirm before the fallback;
`origin/<current branch>` is not a base. If the fallback suggests the wrong release or
maintenance line, ask for the base.

Set `MB=$(git merge-base <base> HEAD)`. Read the file list and full diff over the same range:

- Committed changes, including create mode after Step 1: `git diff <base>...HEAD`.
- Draft with uncommitted task work: `git diff $MB`, plus the task's untracked files in full.

Use `--name-status` and `--stat` with that range. Read surrounding code where needed and
exclude unrelated local edits from the description. If there are no task changes, report that
there is nothing to describe and stop; an empty diff does not mean the base is wrong.

## Step 3 — Choose the template

Look for `PULL_REQUEST_TEMPLATE.md` or its lowercase form under `.github/`, the repository
root or `docs/`, and for templates in their `PULL_REQUEST_TEMPLATE/` directories.
If several templates are equally applicable, ask which to use.

Read the template from the working tree. Keep its headings, order and checklist wording;
replace author instructions with real content and leave every checkbox unticked.
If there is no template, use the [default](references/example.md#default-template):
Purpose, Approach and optional Implementation details, without a checklist.

## Step 4 — Write the description

Write a short sentence-case title from the changes, roughly under 80 characters.
Use a Jira key named by the user, leading a task commit subject, or appearing as a branch segment
(`BF-1523`, `MODUSERSKC-12`). Ask once if those sources conflict. Tokens such as `UTF-8` or
`HTTP-413` in ordinary prose are not ticket identifiers.
With a known key, use `KEY: <summary>` and include its Jira link in the body.
Without a key, use a plain title and omit the link; no question is needed.

Fill the chosen template with the problem and resulting behavior. For the default, write
1–2 sentences for Purpose and 2–3 for Approach; add short implementation bullets when the
change has several substantive parts. Support technical names and claims with the code.
Mention verification only when its results were observed in this session or provided by the user.

Check that the body matches the chosen template and the changes.
For draft-only requests, show the title and body and stop. For create mode, continue to Step 5.

## Step 5 — Confirm and create the PR

Before GitHub calls, check the effective `gh auth status` from the target repository;
a local `.envrc` can override the account. If authentication is unavailable or unexpected,
deliver the description and report the blocker.

Read the current branch with `git branch --show-current`. Creation needs a named feature branch,
different from the base. Check the actual remote tip with
`git ls-remote origin "refs/heads/<current branch>"`; compare it with `git rev-parse HEAD`.
If the branch is absent or the local commits are ahead, a push is needed.
If the remote has diverged, stop and report it instead of forcing a push.

Show the final title and body, say whether a push is needed, and ask "Create the PR?"
**Wait for approval of this text. That approval includes the necessary push of the current
branch; do not ask separately for push permission.** Reuse approval if this exact preview has
already been approved.

If task files, HEAD, the base or template changed while awaiting approval, revisit the affected
step and show the updated preview. Otherwise proceed without repeating the preparation.

Push only when needed, with an explicit destination:

```bash
git push origin "HEAD:refs/heads/<current branch>"
```

Then create the PR with the approved body in a file outside the repository:

```bash
gh pr create --base <base branch name> --head <current branch> --title "<title>" --body-file <path>
```

Strip only the leading `origin/` from the base branch name; preserve the remaining `/`.
The explicit `--head` prevents `gh` from performing an implicit push.
Return the PR URL. If push or creation fails, stop and return the description with the blocker.

## Keep the operation scoped

Do not run builds, tests, linters or generators, or edit `NEWS.md`. Do not switch branches,
stash, reset, clean, force-push, change Git configuration or bypass rejected hooks/permissions.
Never include secrets or tool attribution in the PR text.
