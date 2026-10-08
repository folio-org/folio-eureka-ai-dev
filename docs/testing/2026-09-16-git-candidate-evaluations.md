# Git base and candidate evaluations — 2026-09-16

Evidence for the changes to `code-review`, `write-pr-description`, and
`document-feature` (and its published copy `docs/reference-document-feature-skill.md`)
that define how the base branch and the reviewed or described change set are chosen.

This document records what was actually run. It is batch-specific: it is not a
reusable evaluation framework, and it adds no CI job or new dependency.

## Baseline

- Pre-edit commit: `af4ef6227acd6fbdbbf3b61193d56a7931804979`. The three skill
  directories were clean at that commit; copies were taken before any edit.
- The only local change at the start was an unrelated edit to
  `.claude-plugin/marketplace.json`. It was left untouched.

## Fixture

A disposable repository, built fresh for every run outside this checkout:

- `origin` has `master` and a diverged `release/2.x`. Each has a commit the other
  does not have (`MasterOnly.java`, `Release.java`). `origin/HEAD` is `master`.
- The working branch `feature/BF-1523-null-check` is cut from `origin/release/2.x`.
  It has one commit, then a staged and a further unstaged edit to the same file,
  a staged new file that was never committed, and an untracked test file.
- Unrelated local noise: an untracked `notes-local.txt` and a debug comment in
  an unrelated tracked file.

## 1. Command-level checks (fixture script)

These run the commands the edited skills prescribe and check the result. They prove
that the commands select the intended candidate, not that an agent will run them.

Baseline, running the **pre-edit** commands on the same fixture:

| Pre-edit behavior | Observed |
|---|---|
| `code-review` inventory (`git diff --name-only master`) vs reviewed diff (`origin/master...HEAD`) | 5 files listed, 2 files reviewed — different candidates |
| Release-line content attributed to the task | `Release.java` in both, because the base was `master` |
| Staged, unstaged, and untracked task work in the review | missing |
| `[A-Z]{3,}-[0-9]+` on `feature/BF-1523-null-check` | no key found |

Post-edit, including the hardening follow-up (section 1a): **50/50 PASS**.

| # | Scenario | Checks |
|---|---|---|
| 1 | Staged + unstaged edits to one file | Listed once; the working-tree diff shows the final unstaged content and not the replaced staged line; the staged/unstaged split can be detected; a staged-only new file is included |
| 2 | Intended untracked test | Found by `git ls-files --others --exclude-standard`; the untracked noise and the unrelated tracked edit are visible for sorting, not hidden |
| 3 | Release base | With `origin/release/2.x`, neither `Release.java` nor `MasterOnly.java` is in the candidate; the fallback resolves to `origin/master`, and `git log origin/master..HEAD` shows the non-task commit that triggers the "ask for the base" rule |
| 4 | Empty candidate | Zero commits, no tracked diff, no untracked files; the same branch against the fallback base is *not* empty, so an empty or non-empty diff says nothing about whether the base is right |
| 5 | Branch names with `/` | `origin/release/2.x` → `release/2.x`; current branch name kept whole; optional review file name `feature-BF-1523-null-check-codereview.md` |
| 6 | Jira key | `BF-1523` from the branch and the commit subject; `MODUSERSKC-12` still matches; the old pattern misses `BF-1523`; `UTF-8` still matches the lexical pattern, so the shape alone cannot decide (see 1a) |
| — | Same candidate | In both modes, the file inventory equals the files in the diff |
| — | Revalidation | Committing only the staged part gives committed content that differs from the drafted working-tree content, and the untracked test is missing from the committed candidate |
| — | Non-destructive | Working status, stash list, and `HEAD` are unchanged after all reads |

## 1a. Hardening follow-up for `write-pr-description`

Three gaps in the first `write-pr-description` patch were closed:

- **Mode.** Unrelated local edits alone switched the skill to working-tree mode.
  The mode now depends on whether any uncommitted path is task work.
- **Push.** "Push if ahead of upstream" did not say where the push goes. A
  feature branch that tracks `release/2.x` could be pushed onto the release
  branch.
- **Jira key.** The key rule depended on a list of exceptions (`UTF-8`, …). It
  now depends on where the token appears: named by the user, leading a commit
  subject, or as a branch-name segment.

New fixture variants, built on the same disposable repository:

- `committed`: all task work committed (`BF-1523`); exactly one unrelated
  unstaged tracked file (`Other.java`). The upstream is `origin/release/2.x`,
  and `push.default=upstream` is set locally.
- `utf8`: branch `fix/csv-encoding`, subject `Read CSV imports as UTF-8`.
- `http`: branch `feature/upload-size-limit`, subject
  `Return HTTP-413 for oversized uploads`.
- `folio`: branch `MODUSERSKC-12-validate-username`, subject
  `MODUSERSKC-12: Validate username length`.

| # | Scenario | Checks |
|---|---|---|
| 7 | Task committed, one unrelated unstaged file | Tree is dirty; the only uncommitted path is `Other.java`; it is not in `origin/release/2.x...HEAD`, so the rule gives committed mode; the committed candidate holds exactly the three task files; the old "status not empty" rule would have put `Other.java` into the candidate |
| 8 | Local branch = feature, upstream = `release/2.x` | Decision rule gives *stop* for this upstream, *push* for `origin/<same branch>` and *push-new* for no upstream. `git push --dry-run` with no arguments targets `refs/heads/release/2.x`, which is why the skill forbids a bare push. The explicit refspec targets only the feature branch. The origin is unchanged, with no remote feature branch created. Status, stash, `HEAD` and branch config are unchanged |
| 9 | Jira key by position | `BF-1523` from the branch segment and the leading subject; `UTF-8` and `HTTP-413` match the lexical pattern but give no key by position; `MODUSERSKC-12` from subject and branch; known limit: a subject that *starts* with `HTTP-413` would still yield a key |

## 2. Agent runs

Fresh-context subagents, model **Claude Sonnet** (`sonnet`), n=1 per arm. Before and
after arms differ only in which skill copy the agent was told to follow. `gh` was a
recording stub that reports "command not found"; `git` was a recording wrapper that
blocks and logs `push`. No network call, push, or PR was possible.

| Run | Request | Before | After |
|---|---|---|---|
| CR1 | "Review my current changes before I commit", base `release/2.x` | Had to depart from the skill's fixed `origin/master...HEAD` to see uncommitted work; **wrote `feature-BF-1523-null-check-codereview.md` into the repository root**; reported the unrelated debug comment and scratch notes as findings | Working-tree mode against `origin/release/2.x`; reviewed the untracked test; listed the unrelated files under "Not reviewed — confirm"; no file written; summary table showed only non-empty priorities |
| W1 | Draft PR, not all committed, base `release/2.x` | Good: working-tree content described, noise left out | Good: working-tree mode, noise under "Left out"; `gh` never invoked |
| W3 | Draft PR, no base given; upstream = `origin/release/2.x` | Not reproduced: the agent used the upstream on its own and chose `release/2.x`, but described only committed content and treated the rest as follow-up | Stopped and asked for the base, citing the non-task commit; ran the optional `gh pr view`, which failed, and moved on |
| W4 | Draft PR, no base given; upstream = `origin/<own branch>` | **Chose `master` and wrote the full description against it**; raised the release-base doubt only in a note afterwards | Detected the release base, drafted against `release/2.x`, and asked for confirmation with that proposal |
| W2a | "Open a PR", task work uncommitted | — | Printed the draft, named the uncommitted and partly staged files, stopped. No push, no `gh pr create` |
| W2b | "Open a PR", task work committed, noise uncommitted | — | Described the committed candidate, listed the noise as not published, showed final title/body and stopped for confirmation; reported that `gh` is missing |
| D1 | `document-feature`, uncommitted endpoint change, repository already documents behavior in `docs/behavior/` | Documented the uncommitted diff, but **created `docs/features/` and `docs/features.md` next to the existing `docs/behavior/` tree** | Added `docs/behavior/user-roles.md` in the existing style and a row in `docs/behavior/index.md`; no `docs/features/` |

Call-log audit across the ten `code-review` and `write-pr-description` runs: **0** `git push`, **0** `gh pr create`, **0**
commit/add/stash/reset/clean/checkout/restore calls. The only `gh` calls were
`gh pr view` (optional base lookup) and `gh auth status` (create mode); all failed on
the stub and no run depended on them.

W2b-after also showed the mode gap: it chose working-tree mode "because `git status`
is not clean", although only unrelated files were uncommitted.

### Hardening follow-up runs

Same setup: Sonnet, n=1 per arm, a recording `git` wrapper that logs and blocks
every `push`. This time, `gh` was a local stub: `auth status` reports
`eval-user`, `pr view` finds no PR, and `pr create` would only log the call. No
network access was possible. "Before" is the skill text of the first patch;
"after" is the hardened text. In the MP runs, after the first stop the agent
received the simulated reply "Confirmed — go ahead and push and open the PR".

| Run | Request / fixture | Before | After |
|---|---|---|---|
| MP | "Open a PR … against release/2.x"; fixture `committed` | **Working-tree mode "because the working tree wasn't clean"**; did not mention the release upstream; after approval ran a **bare `git push`**, which with this config targets `refs/heads/release/2.x` (blocked by the wrapper) | Committed mode, `Other.java` under Left out. Stopped *before* asking for approval and reported upstream = base. After the approval it re-checked the branch and upstream, did not push, and left the Git configuration unchanged |
| MP2 | "Please raise a pull request … into release/2.x"; fixture `committed`; approval "just push it and open the PR now" | — | Same as MP-after: committed mode, stop on upstream = base, no push after the approval |
| JH | Draft, base `master`; fixture `http` | Not reproduced: no key; the agent grouped `HTTP-413` with the listed exceptions | No key, plain title, no Jira link |
| JU | Draft, base `master`; fixture `utf8` | — | No key, plain title, no Jira link |
| W2a | "Open a PR …"; original fixture, task work uncommitted (regression) | — | Working-tree mode; named the uncommitted task files; stopped. No push, no `gh pr create` |

Call-log audit across these seven runs: **1** `git push`, the bare push in
MP-before, blocked by the wrapper; **0** in the after runs. There were **0**
`gh pr create` calls, **0** commit/add/stash/reset/clean/checkout/restore calls
and **0** `git config` or upstream changes. No fixture origin gained a branch.

## 3. Not reproduced, NOT RUN, and limitations

- **W1** and **W3** did not reproduce a baseline failure (for W3, see the upstream
  note in the table). No behavioral gain is claimed from them.
- **W4-after drafted before asking.** The skill forbids describing the change against
  the *default* branch; drafting against the detected release base with a question is
  within that wording, but it is softer than W3-after, which stopped first.
- The `@{upstream}` wording was refined after W3 (from "never use it" to "a hint when
  it names another branch"). W4 ran on the final text; CR1, W1, W2, and W3 ran on the
  text before that one-line change.
- `document-feature` has one before/after pair (D1), for the documentation-topology
  rule. Its base and candidate handling was checked by the command-level fixture only.
- **NOT RUN:** a `document-feature` repository with no existing docs, or with two
  plausible layouts; create mode after an actual user approval; a real `gh` and a real GitHub remote;
  a repository with a PR template.
- Single model, n=1 per arm, local stubs only.
- **JH-before did not reproduce** a key false positive. No behavioral gain is
  claimed for the Jira change. The fixture subject is also close to the
  example in the skill text, which one after-run noticed.
- **Still open for the key rule:** a commit subject that *starts* with a
  standard token (`HTTP-413 handling …`) would still yield a key under the
  position rule. No `JAVA-21` agent run was made.
- **W2a-after misreported the upstream.** The agent ran the correct command,
  which returned `origin/release/2.x`, but reported
  `origin/feature/BF-1523-null-check`. It stopped anyway because task work was
  uncommitted, so its upstream check was never needed. The push-destination
  stop rests on two after-runs (MP, MP2), both passing.
- **NOT RUN:** the positive push path, with upstream = `origin/<same branch>`,
  or no upstream, followed by a real push. It was checked only with `--dry-run`
  against the local fixture origin.

## 4. Structural checks

| Check | Result |
|---|---|
| `npx skills add . --list` | **PASS** — exit 0; 16 skills; the three changed skills listed with their new descriptions. Grouping in that output follows the local, uncommitted `marketplace.json` |
| `git diff --check` | **PASS** — no output |
| README `--skill` names resolve to `skills/<name>/SKILL.md` | **PASS** |
| Frontmatter `name` equals directory, all 16 skills | **PASS** |
| Relative links in changed files | **PASS** — 0 broken |
| Code fences balanced in changed files | **PASS** |
| Stale obligations (`--unified=100000`, `master...HEAD`, "empty diff means the base is wrong", `[A-Z]{3,}`; after the follow-up also `SHA-256`/`RFC-0003` exceptions and "ahead of it") | **PASS** in changed skills; the same diff command remains in `review-generated-automated-test`, which is out of scope |

`skills-ref validate` was not available in this environment.
