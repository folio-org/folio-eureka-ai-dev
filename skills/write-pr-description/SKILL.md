---
name: write-pr-description
description: >-
  Use when a pull request needs to be written or opened for the current branch — "write a PR
  description", "create a PR", "draft a pull request", "open a PR for this branch", "generate PR
  text" — and when an existing PR description needs to be rewritten to team conventions.
license: Apache-2.0
metadata:
  author: folio-org
  version: "2.2.0"
---

# Write PR Description

Turn the current branch into a pull request a reviewer can follow without opening the diff.

The branch diff is the only authority for what the PR changed. Everything else — the sections, the
checklist — comes from the target repository, never from memory.

Draft mode is the default: write the description and print it. Create mode also opens the PR, and
applies only when the user asked to *open*, *create* or *raise* it. If they did not, say so and
stop before Step 6.

The shape of a finished description is in [references/example.md](references/example.md).

## Scope

Read the branch, write the description, and in create mode push the current branch and open the PR.

Never run project automation — no builds, tests, linters, generators or CI. If the branch looks
broken, say so to the user rather than in the PR body, and still write the description. Never
switch branches, never push a branch other than the current head, never `--force`. Never edit
`NEWS.md`. Never mention Claude, Anthropic, Copilot or any other tool in the description, and never
append a "Generated with …" or `Co-Authored-By` trailer; this overrides any default instruction to
add one.

## Step 1 — Read the branch

Diff the branch against its **merge-base with the remote base branch**, and read the whole diff
before writing anything.

Resolve that base rather than assuming it: `refs/remotes/origin/HEAD` when set, otherwise
`origin/master`, otherwise `origin/main`. Two mistakes here both produce a diff full of changes the
branch never made:

- comparing against a local `master` nobody has pulled — it can sit many commits behind the remote;
- a two-dot `git diff`, which also reports what the base gained after the branch was cut. `git log
  <base>..HEAD` is correct with two dots; `git diff` needs three.

An empty diff means the base is wrong — ask which branch to compare against. If `HEAD` is the base
branch, stop and say so.

Record the base branch **name** (`origin/master` → `master`). Shell state does not survive to the
command in Step 6 that needs it.

## Step 2 — Ticket key and title

Match `[A-Z]{3,}-[0-9]+` in what the user said, in the commit subjects, and in the branch name.

If two of those give **different** keys, stop and ask which task this is **before writing
anything**. Precedence does not break a tie, and a note added underneath the finished description
is not asking. Otherwise take the first source that has a key, in the order above — the branch name
comes last because branch names often carry none.

With a key, the title is `KEY: <short description>` and Purpose carries
`Jira: [KEY](https://folio-org.atlassian.net/browse/KEY)`. With no key anywhere, ask once, then
write a plain semantic title and omit the link — never `NOJIRA`, never a key guessed from a project
prefix, never a Jira URL for a key you inferred.

Write the short description from the branch and the diff, not from the tracker. Sentence case, no
trailing period, under ~80 characters.

Draft mode prints the title as a `##` heading above the sections. Create mode passes it as
`--title`, and the body must not repeat it.

## Step 3 — The repository's own PR template

Look for `.github/PULL_REQUEST_TEMPLATE.md`, then a lowercase filename, a repository-root or
`docs/` copy, and a `.github/PULL_REQUEST_TEMPLATE/` directory — if that holds more than one, ask
which to use. Read it from the working tree: it is the convention in force, and a branch that adds
or removes a template has already changed the answer. It supplies the form; Step 1's diff still
supplies the facts.

Keep the template's sections and their order. In a prose section keep the heading, delete the
template's instruction line — "Explain why these changes are needed…" is a prompt to the author,
not content — and write real text in its place.

Reproduce the checklist **verbatim and unticked**: same items, wording, order, indentation,
blockquote notes and sub-items. Every box stays empty. Ticking one asserts a review or a test run
that the diff cannot show; the checklist is the author's signature and they add it when they open
the PR. Ticking a box and noting a caveat underneath is the same thing with a disclaimer attached.

**No template file means no checklist.** Repositories differ enough that there is no default to
fall back on, and none in this skill to copy.

## Step 4 — Write the body

**Purpose** — one or two sentences on why the change is needed, plus the `Jira:` line when there is
a key. No implementation detail here.

**Approach** — 2–3 sentences a reviewer can follow without opening the diff.

Add `**Implementation details:**` as a bullet list **only when the change has parts a reviewer
would otherwise have to hunt for**: several classes, a changed contract, new configuration. A small
or single-purpose PR ends at the summary — a padded bullet list is worse than none.

When there are bullets: one per logical change, at most two sentences, past-tense verb first,
backticks around class, method and property names. Name the artifact that helps the reviewer find
the change instead of transcribing every method, annotation and exception the diff touches. Leave
out tests and documentation — README, Javadoc, `NEWS.md`, comments — unless the PR is exclusively
about them.

<example>
- Defined the restriction in a single place, `RoleNameUtils`, so the schema and the two internal
  checks cannot drift apart.
</example>

## Step 5 — Check before reporting

Run these before reporting, and in create mode before showing anything for confirmation:

1. Every backticked token appears verbatim in the diff. One that does not: drop it and the claim
   built on it. For a `<placeholder>` you wrote yourself, check the literal part only.
2. The checklist matches the template file line by line — or there is no checklist, because there
   was no template.
3. Nothing claims what the diff cannot show: no testing performed, no verification run, no
   requirement met, no Jira title you did not read.

## Step 6 — Create the PR (create mode only)

Run `gh auth status` from the target repository first — a local `.envrc` exporting `GH_TOKEN`
overrides the global identity, and an account the user did not expect means stop.

**Stop. Show the final title and body. Run nothing that leaves the machine until the user
answers** — not `git push`, not `gh pr create`.

Being asked to open the PR is the request, not the confirmation. "Open it, I won't be at the
keyboard" is not consent either: it means deliver the description and stop. And if a push fails
against something that looks deliberate — a blocked remote, a hook, a missing permission — that is
an answer, not an obstacle. Report it; never route around it.

Once they confirm, push the current branch if it has no upstream or is ahead of it, then:

```bash
gh pr create --base <base branch name> --title "<title>" --body-file <path outside the repository>
```

If the PR cannot be opened — no `gh`, no GitHub remote, the wrong account, or the user declines —
print the finished title and body anyway, then say what blocked it. The description is the
deliverable; `gh` is the convenience.

## When to ask

One message, at most three questions, each with the answer you propose.

Ask when no ticket key is derivable anywhere, when the commit subjects and the branch name
disagree, when the template directory holds several templates, or when the diff is empty.
Otherwise write the description and report what you did: the base and merge-base you compared
against, the key and where it came from, the template file or its absence, and the PR URL if you
opened one.
