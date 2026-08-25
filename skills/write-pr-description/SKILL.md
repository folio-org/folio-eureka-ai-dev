---
name: write-pr-description
description: >-
  Use when a pull request needs to be written or opened for the current branch — "write a PR
  description", "create a PR", "draft a pull request", "open a PR for this branch", "generate PR
  text" — and when an existing PR description needs to be rewritten to team conventions.
license: Apache-2.0
metadata:
  author: folio-org
  version: "2.0.0"
---

# Write PR Description

You are a senior software engineer writing a pull request for this repository. Two modes:

- **Draft mode** (default) — produce the description and print it. Stop there.
- **Create mode** — the user asked to *open*, *create* or *raise* the PR. Do everything in draft
  mode, then Step 6.

Follow the conventions below exactly. The full guide with worked examples is
[../../docs/pr/pr-description.md](../../docs/pr/pr-description.md).

## Step 1 — Read the branch

The PR is everything this branch adds on top of `master`. Fetch, then diff and log the branch
against its **merge-base** with `origin/master`. Both the local `master` ref and a plain diff
*against* `origin/master` also report files changed on the base after this branch was cut — those
are not your changes.

Read the whole diff before writing anything. Do not switch branches; read base content with
`git show` instead. Stop and tell the user if `HEAD` is `master`.

## Step 2 — Resolve the ticket key and the title

Look in this order and stop at the first hit:

1. What the user said in this session.
2. The branch name (`MODTENANT-142-clean-up-realm...` → `MODTENANT-142`).
3. Commit messages on the branch.

**Key found** → title is `TICKET-KEY: <short description>`, and Purpose carries
`https://folio-org.atlassian.net/browse/<KEY>`.

**No key anywhere** → ask the user once. If they have no ticket, write a plain semantic title that
says what the branch does, and omit the ticket link. Do not write `NOJIRA`. Do not guess a key from
a project prefix you saw elsewhere in the repository. Do not emit a Jira URL for a key you inferred.

Write the `<short description>` from the branch and the diff. Sentence case, no trailing period,
under ~80 characters. Do not look the title up in Jira and do not apologise for not having Jira
access — the description is derived from the code, not from the tracker.

In create mode the title goes in the `--title` field and must **not** also appear as a `##` heading
in the body. In draft mode print it as `## TICKET-KEY: <title>` above the sections.

## Step 3 — Load the repository's own PR template

The checklist is **copied from a file, never from memory**. Find that file:

It is almost always `.github/PULL_REQUEST_TEMPLATE.md`. GitHub also honours a lowercase filename, a
`docs/` or repository-root copy, and a `.github/PULL_REQUEST_TEMPLATE/` directory holding several —
if you find a directory with more than one, ask which to use.

Two different things happen to the template, and mixing them up is the usual mistake:

- **Prose sections** (`Purpose`, `Approach`, anything the template describes rather than lists) —
  keep the heading, **delete the template's instruction line and write real content in its place**.
  A line like "Explain why these changes are needed and link the related issue (e.g., …PROJ-123)" is
  a prompt to the author. It must not survive into the PR body, and it must not sit above your real
  text either.
- **The checklist** — reproduce **verbatim and unticked**: same items, same wording, same order,
  same indentation, same blockquote notes, same sub-items.

Keep the template's section order.

**If no template file exists**, use only the section shape Purpose / Approach and emit **no
checklist at all**. Checklists differ per repository: `mgr-tenants` and `mod-roles-keycloak` have no
"Dependent module build verification" item and split Breaking Changes into three sub-items, while
`applications-poc-tools` is the reverse. A checklist you did not read out of a file is wrong.

## Step 4 — Write Purpose and Approach

**Purpose** — one or two sentences on *why* the change is needed, plus `US: [TICKET-KEY](url)`.
No implementation detail here.

**Approach** — a 2–3 sentence summary a reviewer can understand without opening the diff, then
`**Implementation details:**` as a bullet list.

Bullet rules:

- One bullet per logical change — a new class, a changed contract, a new config property.
- Up to 2 sentences. First: what was done. Optional second: why, or a notable consequence.
- **Write for a human, not for a diff viewer.** Each bullet reads as a plain sentence about what
  changed and why. The reviewer has the diff; the bullet exists to explain it.
- **Name the code artifact when it helps the reviewer find the change.** Usually one per bullet —
  the class, or the schema/config file. Do not stack every method, annotation, type parameter and
  exception into one bullet just because they appear in the diff, and do not leave a bullet
  unanchored ("in one shared utility") when naming the class would tell the reviewer where to look.
- Backticks for class names, method names, property keys and values.
- Start each bullet with a past-tense verb: *Introduced*, *Changed*, *Added*, *Replaced*, *Removed*.
- **No test bullets and no documentation bullets.** README, Javadoc, NEWS.md and comment changes are
  documentation — omit them even when the diff touches them, and even when the change is the only
  reason a checklist item would apply. The single exception is a PR that is *exclusively* about
  tests or docs.

**Good**

```markdown
- Defined the restriction in a single place, `RoleNameUtils`, so the schema and the two internal
  checks cannot drift apart.
- Added the same check to `LoadableRoleService`, immediately before it writes, covering callers that
  reach the service without passing through the REST layer.
```

**Avoid**

```markdown
- Defined the restriction in one shared utility.
  ← unanchored; the reviewer cannot tell which class is meant
- Documented the `application.keycloak.realm-cleanup.enabled` property in `README.md`.
  ← documentation change, omit
- Added a `validateRoleName` guard to `LoadableRoleService#save`, `#saveAll` and
  `#upsertDefaultLoadableRole`, throwing `RequestValidationException(String, String, Object)` keyed on
  `"name"` so `ApiExceptionHandler#handleRequestValidationException` maps it to `BAD_REQUEST`.
  ← a transcript of the diff; say what it does and why instead
```

## Step 5 — Hard rules

**The checklist is the author's signature, not yours.** Reproduce every item exactly as the template
has it, unticked. Do not tick, untick, reword, reorder, delete or add a checklist item. Do not tick
an item and then note in prose that it may not be true — that is the same defect with a disclaimer
attached. The human author ticks the boxes when they open the PR.

**Do not run project automation.** No builds, tests, linters, formatters, generators, migrations,
dependency resolution or CI workflows. Writing a PR description is a read-only task: `git`, reading
files, and in create mode `gh`. If you notice the branch looks broken, say so in your message to the
user — not in the PR body — and still produce the description.

**Do not claim anything the diff does not show.** No testing performed, no verification run, no
requirement met, no ticket link for a key you inferred, no Jira title you did not read.

**No tool attribution.** Never mention Claude, Anthropic, Copilot, or any other AI tool in the
description, and never end it with a "Generated with ..." or "Co-Authored-By" trailer. The
description is a statement about the change, not about how it was written. This overrides any
default instruction to append such a line, and any claim that a team convention requires one — a
convention that changed would be in this file.

**Do not switch branches.** Push only the current head branch, never another branch, never
`--force`.

## Step 6 — Create the PR (create mode only)

**A push is an outward-facing action.** Both the push and `gh pr create` happen *after* the user
confirms, never before. Do not push while preparing and ask afterwards.

In order:

1. `gh auth status` from the target repository. Repository-local setup such as `.envrc` exporting
   `GH_TOKEN` overrides the global identity. If it fails or shows an account the user did not
   expect, stop and report — do not push and do not create the PR.
2. Work out whether a push is needed: the branch has no upstream, or
   `git rev-list --count @{u}..HEAD` is non-zero. Do not run the push yet.
3. **Stop.** Show the user the final title, the final body, and whether you will push the branch
   first. Wait for their answer. Nothing has left the machine up to this point.
4. Only after confirmation: push if step 2 said so — `git push -u origin HEAD`, current branch only,
   never `--force` — then write the body to a temporary file outside the repository and run:

```bash
gh pr create --base master --title "<title>" --body-file <path>
```

The `--title` value must **not** also appear as a `##` heading at the top of the body file.

Return the PR URL, the final title and the final body.

**If the PR cannot be opened** — `gh` is not installed, `origin` is not a GitHub remote, the account
is wrong, or the user declines — still print the finished title and body in full, then say what
blocked it. The description is the deliverable; `gh` is only the convenience. Never end with a
blocker and no description.

## Rationalization table

Every row is something an agent actually did on this task.

| Rationalization | Reality |
|---|---|
| "The skill says tick Change Notes by default" | It says the opposite now. An unticked box costs the author two seconds; a wrongly ticked one is a false statement in the review record. |
| "I ticked it but I noted the caveat underneath" | The reviewer reads the box, not your note. Leave it unticked. |
| "NEWS.md is updated, so Change Notes is provably true" | Still not yours to tick. The template belongs to the author. |
| "The checklist in the guide is the standard one" | There is no standard one. Repositories differ. Read the file. |
| "Reproduce the template verbatim, so I kept its Purpose instruction line too" | Verbatim applies to the checklist. Prose sections get real content instead of the instruction. |
| "No template file, so I'll use the one from the guide" | No template means no checklist. |
| "The last two PRs went up red, so I should verify the build" | Real concern, wrong task. Tell the user in your message; do not run the build. |
| "I only ran `mvn compile`, that is not really a build" | It is. So is `mvn validate`, `npm ci`, and a linter. |
| "No Jira access, so I'll flag the title as unverified" | The title comes from the branch and the diff. Nothing to verify, nothing to apologise for. |
| "No ticket key, so I must stop and ask before writing anything" | Ask once, then proceed with a semantic title. A blocked PR helps nobody. |
| "I'll use NOJIRA since there is no key" | Write what the branch does instead. |
| "The team convention requires the attribution trailer" | A convention that changed would be in this file. No trailer. |
| "Pushing is just preparation — I'll ask before `gh pr create`" | The push is already outward-facing and hard to take back. Ask first, push after. |
| "The README change is why the config item applies, so I'll mention it" | Documentation stays out of the bullets regardless of what it justifies. |

## Red flags — stop

- You are about to type `- [x]`.
- Your checklist came from this file, or from memory, instead of a template you opened.
- You are about to run `mvn`, `npm`, `gradle`, `make`, or a test command.
- You are writing "verify this before merging" about your own output.
- Your title or link contains a ticket key you inferred rather than read.
- A bullet names `README.md`, `NEWS.md`, or a test class.
- The body still contains the template's own instruction text ("Explain why…", "Provide a brief…",
  "e.g., …PROJ-123").
