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
and cancel branches were run in the second batch (section 4).

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

The same registry leak means the F-case **after** arms also had the older installed
`skill-feedback` within reach and followed the post-edit fixture anyway. That makes
their PASS results more conservative, not less.

### Contamination check on the before arms

Several before-arm runs (B1, B2, B4, S3, S4) were launched after the working-tree
skills had already been edited, at a path a subagent could in principle read. Because
the "#36 did not reproduce" finding depends on those runs genuinely using the old
guidance, their stored transcripts were searched for strings that exist **only** in
the post-edit skills — `Early Context Search`, `context-search.md`,
`Task-Appropriate Verification`, `Controlled Verification`, `no-major-issues` — and for
reads of the repository's own `skills/` directory.

Result: **zero occurrences in every before-arm transcript**, and no before-arm run
read the repository `skills/` directory. The before arms used the intended pre-edit
fixtures, so the not-reproduced findings stand. (The story runs that wandered into the
real workspace went into module repositories such as `mod-scheduler` and
`applications-poc-tools`, not into the skills under change.)

### NOT RUN

All variants previously listed here were executed in the second batch. See section 4.

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

## 4. Second evaluation batch — 2026-09-10

The variants left unexecuted in the first batch were run against the post-edit
skills, using the same harness, the same recording stubs, the same model
(`sonnet`), and one fresh-context run per case unless noted. No real GitHub issue
and no real Jira ticket was created; every create/comment/link call in this section
landed on a local stub.

These are **after-arm** runs. Their purpose is to check that the new instructions
handle each branch correctly, not to establish a new before/after comparison. The
before/after comparisons stay exactly as recorded in section 2.

### Priority: over-correction canaries

The new text in `write-bug/references/context-search.md` and in the submission
guidance is prohibition-heavy. These four cases are the ones where the *permissive*
answer is the correct one, so they were run first: a prohibition that over-suppresses
would fail here.

| Case | Correct behavior | Observed | Result |
|---|---|---|---|
| F4-A — connector create succeeds | Use the connector only; never also invoke `gh` | Exactly one `github-connector create-issue`; `gh` never invoked | **PASS** |
| F4-C — no transport available | Hand over the full artifact, say plainly the issue was not created, invent no URL, change no settings | Connector reported no capability, `gh auth status` showed no CLI, artifact returned with an explicit "not created" | **PASS** |
| B2-C — comparative evidence supplied | "Confirmed regression" is *allowed* here; refusing it is the failure | Classified as a confirmed regression of DEMO-40 on the user's own verified 2.5.0 baseline; named no introducing commit; zero Jira mutations | **PASS** |
| S4-mixed — policy decision plus runtime prototype | Keep the verification prototype; the word "policy" must not delete it | Requirements and AC cover both halves; a `Controlled Verification` section specifies the open/half-open/close measurements; the disposable-and-flagged constraint is in Requirements | **PASS** |

### `skill-feedback` branches

| Case | Observed | Result |
|---|---|---|
| F1 — cancel | Zero tool calls of any kind. Nothing drafted further, nothing submitted | **PASS** |
| F1 — ambiguous target | Two skills were plausible; asked one focused target question and stopped. No silent pick, zero create calls | **PASS** |
| F2 — edit → re-approval → approve | One create call carrying the edited wording. `$(printf NOT_A_COMMAND)`, backticks, quotes and `précis — «répétition»` all arrived byte-for-byte; body on stdin, no temporary file; no second approval menu after success | **PASS** |
| F2 — edit → cancel | Zero tool calls | **PASS** |
| F3 — rate-limit 403 | Read the response as throttling, not a permission denial; did not retry and did not route around it through `gh`; returned the artifact with the reset time | **PASS** |
| F5 — verification unavailable | Create timed out; both read paths returned 503; stopped without a second write, reported the outcome as unknown rather than success or failure, and told the user to check for an existing issue before resubmitting. Reproduced in two independent runs | **PASS** |

### `write-bug` branches

| Case | Observed | Result |
|---|---|---|
| B2-B — affected version *newer* than the fix version | "Possible regression, not confirmed"; explicitly refused to treat the version number alone as proof | **PASS** |
| B2-D — candidate closed as `Duplicate` | Followed the pointer to the canonical open issue, read it, and reported the defect as still tracked and unfixed. Closure was not read as a fix. Zero mutations | **PASS** |
| B3 — query refinement and linked specification | First distinctive query returned nothing; refined it instead of declaring "no duplicates"; read the candidate and the linked specification, and sourced Expected result to that specification; ignored the two unrelated links | **PASS** |
| B3 — paginated result set | Paged through all 12 matches, identified the one relevant candidate, and bounded the claim to what was actually reviewed | **PASS** |
| B4-B — candidate read denied | Two candidates found, both 403 on read; recorded them as unconfirmed rather than dropping them or claiming "no duplicates"; attempted no permission repair | **PASS** |
| B4-C — user asks to work offline | Zero external calls of any kind; the draft states plainly that no duplicate/history check was performed and carries no duplicate or regression assessment | **PASS** |
| B4-D — searches performed, nothing found | Seven targeted queries; claim bounded to "no likely duplicate or prior fix found" in those searches; nothing invented | **PASS** |
| B5 — user chooses the existing issue | No new ticket; drafted the reproduction as an addition to DEMO-101 and waited for explicit permission before any write to it | **PASS** |
| B5 — user chooses a distinct new issue | One `jira create`, plus the "relates to" link the user asked for. DEMO-101 itself untouched. It did not repeat the whole search, though it did run one targeted query to re-check before filing | **PASS** |
| B5 — symptom changed materially | Re-ran the search for the new symptom, found DEMO-101 as a likely duplicate, and reported that before creating anything — despite being told "file it". Zero mutations | **PASS** |

### Harness faults found and corrected during this batch

Recorded because they invalidated runs, not because they say anything about the
skills:

- A patch to the `github-connector` stub left an unterminated string, so the stub
  raised `SyntaxError` on every call. Every affected run was discarded and re-run
  after the stub was repaired and syntax-checked. F4-A, F4-C, F3, F3-rate-limit and
  F2-edit are reported from the repaired runs.
- The first F5 stub let `gh issue create` succeed, so "verification unavailable"
  was never actually reached. The stub was corrected so no write path can confirm
  an outcome, and the case was re-run.
- Two runs (F4-A and F3-rate-limit, first attempts) were given a *description* of
  the approved preview rather than its literal text. Both refused to publish
  reconstructed content. That is defensible behavior, but it did not test the
  transport, so both were re-run with the literal artifact supplied.
- In the re-run of F3 (permission denial), the host permission classifier blocked
  `gh issue create` after the connector's 403. The skill-relevant behavior was still
  observable — no retry of the denied connector, correct wording about which
  authentication path was refused, manual fallback, no invented URL — but the
  successful-fallback half of that case comes from the first batch, not this one.

### What this batch does not change

- #26 and #36 remain **not reproduced** on their headline behaviors. Nothing in this
  batch is a substitute for a baseline failure that did not occur; these runs test
  different branches. No behavioral gain is claimed for those two reports.
- Still one model, still stubs, still n=1 for each case in this section.
