# Issue-driven skill evaluations — 2026-09-09

Evidence for the changes to `skill-feedback`, `write-user-story`, and `write-bug`
that address issues #12, #18, #17, #26, and #36.

This document records what was actually run. It is batch-specific: it is not a
reusable evaluation framework, and it adds no CI job or new dependency.

## Baseline

- Reviewed commit and actual pre-edit commit are the same: `0823219ff08b17c4749f312b548388433ddff752`.
- The three skill directories were clean in the working tree at that commit, so no
  second content snapshot was needed.
- All five issues were open with zero comments at the start of this work.

## Method

- **Before** and **after** arms use the pre-edit and post-edit copies of the full
  skill directory, references included. Fixtures were snapshotted from the commit
  above **before** any file was edited.
- Each run is a fresh-context subagent. Neither the implementation prompt nor the
  scoring rubric was placed in a tested agent's context.
- Arms differ only in which skill directory the agent is pointed at. Task text,
  tooling, and stub responses are identical.
- Tested model: **Claude Sonnet** (`sonnet`), the model available for subagents in
  this session. No second model was available without new access, so there is **no
  cross-model validation**.
- GitHub and Jira were simulated by local stub executables that record every call
  (argv and stdin) and never touch the network. No real GitHub issue and no real
  Jira ticket was created at any point.
- Automated scoring was used to triage, but every flagged match was read by hand.
  Two automated flags were false positives and were corrected on reading (noted below).

## 1. Structural checks

| Check | Command | Result |
|---|---|---|
| Skills CLI discovery | `npx skills add . --list` | **PASS** — exit 0; 16 skills exposed; all three changed skills listed with their new descriptions |
| Whitespace errors | `git diff --check` | **PASS** — exit 0, no output |
| README preset names exist | Python check over `--skill` names | **PASS** — 15 referenced names all resolve to `skills/<name>/SKILL.md` |
| Frontmatter valid | name/description present, `name` == directory, lowercase-hyphen | **PASS** — all 16 skills; changed skills' descriptions 120 / 176 / 145 chars (limit 1024) |
| Relative links resolve | 29 links across changed skill files and changed docs | **PASS** — 0 broken |
| Markdown fences balanced | changed skill files + issue template | **PASS** — 0 unbalanced |
| Report contract agreement | `references/report-template.md` vs `.github/ISSUE_TEMPLATE/skill-feedback.md` | **PASS** — same heading order, all 7 enums present in both, `no-major-issues` in both |
| Inventory / presets / packaging | `git status`, `skills-lock.json`, `.claude-plugin/` | **PASS** — unchanged by this work |

`skills-ref validate` was not available in this environment, so it was not used.
The repository has no root test runner and no CI workflow for this package; none
was invented.

### Stale active obligations

Scanned the three skill directories, the GitHub issue template, and `README.md`
for the obligations this batch removes:

| Obligation | Active surfaces |
|---|---|
| Mandatory improvement question | clean |
| Separate "Draft fields" review | clean* |
| Fixed `/tmp/skill-feedback.md` path | clean |
| Mandatory manual-only story testing | clean |
| Late-only duplicate search | clean |
| `skill_fit_assessment` / constant `report_type` | clean |

\* The only textual match is the new rule that forbids it
(`Do not add a separate "Draft fields" review.`) — a prohibition, not an obligation.

`docs/us/user-story.md` and `docs/superpowers/specs/2026-04-22-feedback-skill-design.md`
still contain legacy wording by design; both now carry a banner scoping them as
historical. They were excluded from the active-surface scan for that reason.

### Instruction size

Operational detail was pushed into references rather than into the runtime skill.

| Skill | SKILL.md words | references words |
|---|---|---|
| `skill-feedback` | 858 → 1109 (+29%) | 428 → 1331 |
| `write-user-story` | 650 → 1077 (+66%) | 1865 → 2762 |
| `write-bug` | 1499 → 1976 (+32%) | 1915 → 3341 |

## 2. Observed behavioral results

`n` is fresh-context repetitions per arm.

### F1 — positive feedback, no forced improvement question (#12) — n=5

| Arm | Result |
|---|---|
| before | **FAIL 5/5.** Every run stopped to ask "What should this skill improve first?" even though the user had already given complete positive feedback. Zero create calls (the approval gate already worked). |
| after | **PASS 5/5.** Every run used the feedback already given, selected `no-major-issues`, produced one publication preview, and stopped for approval. No invented friction signals, no improvement paragraph. Zero create calls before approval. |

Variance was low in both arms — the five runs converged on the same shape.

### F2 — exact artifact and literal Markdown (#12) — n=1 per arm

| Observable | before | after |
|---|---|---|
| Literal `$(printf NOT_A_COMMAND)` preserved verbatim | yes | yes |
| Create calls before approval | 0 | 0 |
| Removed metadata in the preview | **yes** (`skill_fit_assessment` / `Report type`) | no |
| Stray temporary `.md` files | none | none |

The removed-metadata contract is the behavioral difference. The edit → re-approval
and cancel branches were **NOT RUN** (see limitations).

### F3 — permission fallback (#18) — n=1 per arm

**Both arms created the issue.** This confirms that #18's baseline already performs
the connector → `gh` fallback; it is *not* a failing baseline.

| Observable | before | after |
|---|---|---|
| Sequence | connector (403) → `gh issue create` | connector (403) → `gh auth status` → `gh issue create` |
| Body transport | wrote a temp file, `--body-file <path>` | piped on stdin, `--body-file -` |
| Repeat of the denied connector call | no | no |
| Explanation | "connector returned a 403 … fell back" | "the connector's auth path wasn't permitted … fell back to your local `gh`" |

The differences are the removal of the unnecessary temp-file write and a more
accurate description of which authentication path was refused.

### F4-B — skip an already-known denial (#18) — n=1 per arm

| Arm | Connector create attempts | Result |
|---|---|---|
| before | **1** — retried a path already known to be denied this session | FAIL |
| after | **0** — went straight to the configured `gh` | **PASS** |

### F5 — uncertain write outcome (#18) — n=1 per arm

Mock: the connector create times out with no response, but the issue *was* created.

| Arm | Create attempts | Verified first | Outcome |
|---|---|---|---|
| before | **2** | no | **FAIL — created a duplicate issue** |
| after | 1 | yes (`list-issues`, then `issue view`) | **PASS — found the existing issue and returned it without resubmitting** |

This is the clearest behavioral gain in the batch.

### S1 — library timeout story (#17) — n=5

| Observable | before | after |
|---|---|---|
| Unrelated MTE recovery/resume exclusion | **1/5** (run 1 named `mgr-tenant-entitlements` explicitly) | **0/5** |
| Manual-testing section | 5/5 | 0/5 |
| Controlled/local verification | 1/5 | 5/5 |
| Required contracts covered (7 checks) | 7/7 all runs | 7/7 all runs |
| Test code or fixtures in the story | none | none |
| Length | 813–1056 words | 561–687 words |

Out of Scope entries in both arms otherwise restated boundaries the **user stated
explicitly** (no UI, no retry/recovery policy change). Those are permitted, and an
automated flag that first marked them as drift was corrected on reading.

### S2 — pure discovery/policy ticket (#26) — n=5

**Partially not reproduced.**

| Observable | before | after |
|---|---|---|
| Runtime `Testing Guidance` on a decision ticket | **0/5 — failure did not reproduce** | 0/5 |
| `Testing Guidance: N/A` | 0/5 | 0/5 |
| Invented end-user persona | 0/5 | 0/5 |
| Review/sign-off condition in AC | 5/5 | 5/5 |
| Sibling MODSCHED keys as a bare list | **5/5** | 0/5 — omitted (1/5) or each relationship explained (4/5) |
| Length | 716–804 words | 221–558 words |

So the reported "runtime testing forced onto a policy ticket" behavior did not
occur at baseline in this fixture, while the "flat list of adjacent Jira keys"
behavior did, and changed.

### S3 — binding constraint must not live only in Notes (#26) — n=2 before, n=1 after

The before arm ran twice: the first run's output was scored, then a second run
(started because the first had not yet written its file) overwrote it. Both were
scored, and they disagree on one observable — useful variance, so both are reported.

| Observable | before run 1 | before run 2 | after |
|---|---|---|---|
| Constraint in Requirements | **no** | **no** | **yes** |
| Constraint in acceptance criteria | yes | yes | yes |
| Constraint only in Additional Notes | no | no | no |
| `MODSCHED-88` present as the interval dependency | yes | yes | yes |
| Unrelated `MODSCHED-90`/`91` listed | **yes** | no | no |
| Length | 852 words | 1163 words | 582 words |

The reproducible baseline weakness is constraint **placement**: 2/2 before runs put
the binding constraint only in acceptance criteria and not in Requirements, while the
after run put it in both. Carrying the unrelated backlog keys happened in 1 of 2
before runs, so that observable is not stable at this sample size.

Both before runs explored the real workspace repositories (see limitations).

### S4 — useful sections and runtime verification survive (#17, #26) — n=1 per arm

Identical on every observable in both arms: the explicit third-party-API Out of
Scope boundary kept, `circulation.renew-bulk` in Requirements/AC, the renewal-policy
reference retained, the partial-success failure case kept, and manual UI verification
present. This is the intended **no-overcorrection** result: the changes did not
strip legitimate optional sections or manual QA.

### B1 — early context search on a draft-only request (#36) — n=1 per arm

**Not reproduced.** Both arms searched **before** writing the draft, used no
status or resolution filter, read the candidate, and identified `DEMO-101` as a
likely duplicate. Neither arm made any mutating Jira call.

| Observable | before | after |
|---|---|---|
| Searches before the draft | 3 | 3 |
| Candidates read | 1 (`DEMO-101`) | 2 (`DEMO-101`, and `DEMO-102` explicitly ruled out) |
| Status/resolution filters used | 0 | 0 |
| Mutating calls | 0 | 0 |

The after arm read the near-miss candidate and stated why it did not match; the
before arm did not examine it.

### B2-A — prior fix is not a proven regression (#36) — n=1 per arm

**Not reproduced.** Both arms read closed `DEMO-40` (Fixed, 2.5.0), compared it
with the affected environment (2.4.0), and concluded the environment predates the
fix rather than claiming a regression. Neither invented an introducing commit.

### B4-A — search capability absent (#36) — n=1 per arm

**Not reproduced.** With `jira` unavailable, both arms produced a usable draft and
stated that the duplicate/history check was not performed. Neither claimed "no
duplicates".

## 3. Not reproduced, NOT RUN, and limitations

### Reported behavior that did not reproduce

- **#26 runtime testing on a decision ticket (S2):** 0/5 baseline runs exhibited it.
- **#36 late-only search (B1), prior-fix-as-regression (B2-A), unavailable-search
  disclosure (B4-A):** the baseline already behaved correctly.

For these, the instruction gap in the pre-edit sources is real and the fix is
structurally confirmed, but **no behavioral gain is claimed**.

### Invalid control arm

The planned no-guidance control for F1 is **invalid**. Subagents inherit the host's
installed skill registry, which already contains an older `skill-feedback` skill;
4 of 5 control runs loaded and followed it, so that arm measured the old skill by a
second route rather than measuring unguided behavior. The 5th run behaved unguided
and drafted a positive report, then attempted to publish it without an approval
step. No valid no-guidance control was obtained for F1, S1, or S2. This does not
affect the before/after comparison, which is the comparison these changes rest on.

### NOT RUN

No observation exists for: F1 cancel and ambiguous-target variants; F2 edit →
re-approval and cancel branches; F3 rate-limit variant; F4 variants A and C; F5
verification-unavailable variant; S4 mixed policy+prototype variant;
B2 variants B, C, D; B3 and its pagination variant; B4 variants B, C, D; B5 and all
its variants. Fixtures and stub modes exist for these; the runs were not executed.

### Other limitations

- Single model (Sonnet). No evidence about behavior on other everyday models.
- Stub integrations only. A stub success says nothing about real GitHub connector
  permissions or a real Jira deployment.
- Four story runs (S1 before-5, S1 after-5, and both S3 before runs) explored the real
  workspace repositories and changed the substance of their ticket. S1's are paired;
  S3's are not. These runs are noisier than the rest.
- In two runs (one F1 control, one F4-B before), the host permission classifier
  blocked a stub call. That is a harness effect, not skill behavior.
- Sample sizes are small: n=5 for F1/S1/S2, n=1 per arm elsewhere.
