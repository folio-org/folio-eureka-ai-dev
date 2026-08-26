# Skill Engineering: Writing, Tuning, and Benchmarking

How we build and improve skills in this registry. Sources: Anthropic skill
authoring best practices, the agentskills.io specification, and the
superpowers `writing-skills` TDD methodology.

## Proven authoring practices

1. **Concise is key.** The context window is a public good. Only skill
   name+description load at startup; the body loads when triggered — but once
   loaded, every token competes with the task. Assume the model is smart:
   include only what it cannot derive (verified URLs, house conventions,
   non-obvious invariants). Target: SKILL.md under ~500 words.
2. **Description = triggers only.** Start with "Use when…", never summarize
   the workflow — models shortcut to the description and skip the body.
   Include role/task vocabulary users actually say ("file a defect",
   "who owns module X").
3. **Progressive disclosure.** SKILL.md is the router; heavy content goes to
   `references/*.md` loaded on demand. Avoid deep reference nesting.
4. **Right degrees of freedom.** Rules where deviation is expensive
   (migrations, PR format); principles where judgment is needed (reviews).
5. **Feedback loops inside skills.** "Run validator → fix → repeat" patterns
   outperform one-shot instructions.
6. **TDD for skills** (`writing-skills`): no skill or edit without a failing
   test first. RED — run realistic scenarios via subagents *without* the
   skill, record failures verbatim; GREEN — write the minimum that fixes
   them; REFACTOR — close rationalization loopholes, re-test. If baselines
   pass without the skill, don't ship that content.
7. **Test with every model/agent you support** — a skill tuned on a strong
   model may under-trigger on weaker ones.

## What to include vs omit (context budget)

Include: one-line platform topology, invariants that cause wrong actions,
verified resource links, routing tables to other skills, guardrails.
Omit: anything derivable from the repo (endpoints, class names), volatile
facts (ports, versions, team rosters), narrative explanations, second
examples of the same pattern.

## Feedback, benchmarking, iteration

- **Structured feedback:** the `skill-feedback` skill produces one
  machine-prepared, user-validated report per skill per session, filed to
  this repo. Invoke it when a skill produced friction or a wrong result,
  while the session context is still fresh.
- **Scenario suite as regression tests:** keep the RED/GREEN scenarios
  (clean-environment subagent prompts) with the registry; re-run them after
  every skill edit and after major model upgrades.
- **Metrics worth tracking per skill:** trigger rate (sessions where it
  should have fired vs did), compliance rate (followed the skill's steps),
  correction count (user had to redirect), outcome time (turns to done),
  feedback sentiment from skill-feedback reports.
- **A/B testing:** run the same scenario suite against two variants (e.g.
  two descriptions) with N≥5 runs each — LLM behavior is stochastic, single
  runs prove nothing. Compare trigger and compliance rates; ship the winner.
- **Iteration cadence:** collect skill-feedback issues → batch review →
  RED-test proposed fixes → release a registry version → `npx skills update`.

## Example: tool-context bootstrap skill

A minimal bootstrap for a coding agent (Codex/OpenCode/Claude Code) that
loads project context fast and constrains repository search:

```markdown
---
name: project-bootstrap
description: Use when starting any task in this repository, before reading
  code or running commands.
---

# Project Bootstrap

1. Read `README.md` and `AGENTS.md` (if present) — nothing else upfront.
2. Locate the area of work via the source map below; do not crawl the tree.
   - `src/main/java/...` — production code; `src/test/java/...` — tests
   - `descriptors/` — module descriptor (routes/permissions)
   - `docs/` — behavioral feature docs
3. Search rules:
   - Use targeted search (rg/grep by symbol), never open-ended directory dumps.
   - Never read `target/`, `node_modules/`, `~/.m2`, lockfiles, generated code.
   - Library internals: read the dependency's source repo or docs by link,
     not the unpacked jar.
4. Constraints: single-module scope unless the task names another repo;
   propose (don't run) environment-changing commands.
```

The FOLIO instance of this pattern is `skills/folio-ecosystem`: platform
orientation only — what the platform is, the invariants newcomers get wrong,
and a pointer map to deeper context. It names the registry's task skills as
available but does not orchestrate them (see the v3.0.0 amendment in
docs/superpowers/specs/2026-07-04-folio-ecosystem-skill-design.md).
