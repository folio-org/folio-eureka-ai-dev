---
name: write-pr-description
description: >-
  Use when a pull request needs to be written or opened for the current branch — "write a PR
  description", "create a PR", "draft a pull request", "open a PR for this branch", "generate PR
  text" — and when an existing PR description needs to be rewritten to team conventions.
license: Apache-2.0
metadata:
  author: folio-org
  version: "2.3.0"
---

# Write PR Description

Turn the current branch — committed or still uncommitted — into a pull request a reviewer can
follow without opening the diff.

The candidate from Step 1 is the only authority for what the PR changed. Everything else — the
sections, the checklist — comes from the target repository, never from memory.

Draft mode is the default: write the description and print it. It works before anything is
committed and needs neither `gh` nor network access. Create mode also opens the PR, and applies
only when the user asked to *open*, *create* or *raise* it. If they did not, say so and stop before
Step 6.

The shape of a finished description is in [references/example.md](references/example.md).

## Scope

Read the candidate, write the description, and in create mode push the current branch and open
the PR.

Never run project automation — no builds, tests, linters, generators or CI. If the branch looks
broken, say so to the user rather than in the PR body, and still write the description. Never
switch branches, never push anything but the current head to its own remote branch, never `--force`. Never commit,
stage, stash, reset or clean — not even to make a draft possible. Never edit `NEWS.md`. Never mention Claude, Anthropic, Copilot or any other tool in the description, and never
append a "Generated with …" or `Co-Authored-By` trailer; this overrides any default instruction to
add one.

## Step 1 — Read the candidate

**Base.** Take the first that applies, and record which one it was:

1. a base the user or the calling workflow named (`release/2.x`, `b3.1`);
2. the base of the PR this branch already has, or one stated in the active task context —
   `gh pr view --json baseRefName -q .baseRefName` may help, but if `gh` is missing, logged out or
   finds no PR, move on;
3. fallback only: `git symbolic-ref --short refs/remotes/origin/HEAD`, else `origin/master`, else
   `origin/main`.

Use the remote-tracking ref (`origin/<name>`): a local branch nobody pulled can sit many commits
behind. `@{upstream}` is only a hint: `origin/<current branch>` is not a base, but an upstream
that names another branch (set by `git checkout -b <branch> origin/release/2.x`) is a base to
confirm before the fallback. If you fell back and the branch name, task context, upstream or
`git log --oneline <base>..HEAD` points to maintenance or release work, ask for the base rather
than describing the change against the default branch.

Record the base branch **name** by stripping only the leading `origin/`
(`origin/release/2.x` → `release/2.x`); never split on `/`. Shell state does not survive to
Step 6, which needs it. Then `MB=$(git merge-base <base> HEAD)`.

**Sort local changes first.** A dirty working tree is not a task candidate. List the uncommitted
paths (`git status --porcelain`, `git ls-files --others --exclude-standard`) and sort each one:
task work, or unrelated and pre-existing — local notes, IDE or environment files, debug edits in
unrelated code. Unrelated paths go under **Left out** in your report whatever the mode; ask when
the choice changes the description. Never delete, revert, stage or stash them.

**Mode** follows from that sorting, not from `git status` being empty:

- **Committed mode** when no uncommitted path is task work: `git diff <base>...HEAD`, three dots — a
  two-dot `git diff` also reports what the base gained after the branch was cut.
- **Working-tree mode** when at least one uncommitted path is task work, even in create mode (Step 6
  then checks what is committed): `git diff $MB`, with no second revision, is the final tracked
  content — committed, staged and unstaged together — and read the task's untracked files in full.
  Leave the unrelated paths out of the description.

Use the same range with `--name-status` for the file list. `git log <base>..HEAD` is correct with
two dots. Read the whole candidate before writing, and describe only files that belong to the task.

**Empty candidate** — no commits since `MB` and no uncommitted task work: say there is nothing
to describe yet against `<base>` and stop. It does not mean the base is wrong. If `HEAD` is the
base branch itself, a draft is still possible; create mode stops and says a branch is needed.

## Step 2 — Ticket key and title

A key has the shape `[A-Z][A-Z0-9]+-[0-9]+` (`BF-1523`, `MODUSERSKC-12`), but the shape alone
does not make a token a Jira issue. Count a match only where it is used as the task identifier:

1. the user names it as the ticket;
2. it leads a commit subject (`BF-1523: …`, `[BF-1523] …`);
3. it is a segment of the branch name (`feature/BF-1523-null-check`).

A matching token elsewhere — in the middle of a sentence, in a commit body, in code — is not a key
(`read files as UTF-8`, `return HTTP-413 for large uploads`). When you are not sure a token is a
ticket, treat it as no key. Before the first commit there are no subjects; skip that source.

If two of those give **different** keys, stop and ask which task this is **before writing
anything**. Precedence does not break a tie, and a note added underneath the finished description
is not asking. Otherwise take the first source that has a key, in the order above — the branch name
comes last because branch names often carry none.

With a key, the title is `KEY: <short description>` and Purpose carries
`Jira: [KEY](https://folio-org.atlassian.net/browse/KEY)`. With no key anywhere, ask once, then
write a plain semantic title and omit the link — never `NOJIRA`, never a key guessed from a project
prefix, never a Jira URL for a key you inferred.

Write the short description from the branch and the candidate, not from the tracker. Sentence case, no
trailing period, under ~80 characters.

Draft mode prints the title as a `##` heading above the sections. Create mode passes it as
`--title`, and the body must not repeat it.

## Step 3 — The repository's own PR template

Look for `.github/PULL_REQUEST_TEMPLATE.md`, then a lowercase filename, a repository-root or
`docs/` copy, and a `.github/PULL_REQUEST_TEMPLATE/` directory — if that holds more than one, ask
which to use. Read it from the working tree: it is the convention in force, and a branch that adds
or removes a template has already changed the answer. It supplies the form; Step 1's candidate
still supplies the facts.

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

1. Every backticked token appears verbatim in the candidate. One that does not: drop it and the
   claim built on it. For a `<placeholder>` you wrote yourself, check the literal part only.
2. The checklist matches the template file line by line — or there is no checklist, because there
   was no template.
3. Nothing claims what the candidate cannot show: no testing performed, no verification run, no
   requirement met, no Jira title you did not read.

## Step 6 — Create the PR (create mode only)

Create mode publishes commits, so it works from the committed candidate only. If task files are
still uncommitted or only partly staged, print the draft, name those files, and stop; committing
is the user's step, not yours.

**Revalidate before showing the final text.** A draft written from the working tree, or earlier
in the session, may no longer match what will be pushed. Recompute the base's merge-base and the
committed file list, and re-run Step 5 against `git diff <base>...HEAD`. If files, content or the
merge-base changed, update the description first. Mention files that stay uncommitted or
unrelated so the user sees they will not be published.

**Resolve the push destination.** The base branch is where the PR merges; the push destination is
where the current branch's commits go. They are never the same branch. Resolve them separately:
the local branch with `git branch --show-current`, and its upstream with
`git rev-parse --abbrev-ref --symbolic-full-name @{upstream}`.

- Upstream is `origin/<current branch>`: push there.
- No upstream: push to a new `origin/<current branch>`.
- Upstream names any other branch — the base, `master`, `main`, `release/*`, `b*.0` or a
  differently named branch — or the current branch is itself such a branch: stop. Print the
  description and report the mismatch. Do not push anywhere, and do not change the upstream or
  any other Git configuration.

Run `gh auth status` from the target repository — a local `.envrc` exporting `GH_TOKEN` overrides
the global identity, and an account the user did not expect means stop.

**Stop. Show the final title and body. Run nothing that leaves the machine until the user
answers** — not `git push`, not `gh pr create`.

Being asked to open the PR is the request, not the confirmation. "Open it, I won't be at the
keyboard" is not consent either: it means deliver the description and stop. And if a push fails
against something that looks deliberate — a blocked remote, a hook, a missing permission — that is
an answer, not an obstacle. Report it; never route around it.

Once they confirm, check that `HEAD` is still the commit you revalidated (`git rev-parse HEAD`). If
it moved, revalidate again and show the result before pushing. Then push with an explicit
destination — never a bare `git push`, whose target depends on local Git configuration — skip the
push when `origin/<current branch>` already has `HEAD`, and open the PR:

```bash
git push origin "HEAD:refs/heads/<current branch>"
gh pr create --base <base branch name> --head <current branch> --title "<title>" --body-file <path outside the repository>
```

If the PR cannot be opened — no `gh`, no GitHub remote, the wrong account, or the user declines —
print the finished title and body anyway, then say what blocked it. The description is the
deliverable; `gh` is the convenience.

## When to ask

One message, at most three questions, each with the answer you propose.

Ask when no ticket key is derivable anywhere, when the commit subjects and the branch name
disagree, when the template directory holds several templates, when a fallback base looks wrong
for release work, or when it is unclear whether a file belongs to the task.
Otherwise write the description and report what you did: the base, how it was chosen and the
merge-base; the mode; any files left out; the key and where it came from; the template file or its
absence; and the PR URL if you opened one.
