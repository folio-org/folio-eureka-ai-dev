---
name: brainstorming
description: Use when exploring solutions to a FOLIO/Eureka design problem, planning a new feature, choosing between technical approaches, or working through architectural uncertainty. Generates diverse options without premature commitment.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
  source: adapted from obra/superpowers (https://github.com/obra/superpowers)
---

# Brainstorming

## Overview

Brainstorming is divergent thinking — generating a wide option space before converging on a solution.

**Core principle:** Quantity and diversity of ideas first. Evaluation comes after, never during generation.

**Violating the letter of this process is violating the spirit of brainstorming.**

## The Iron Law

```
NO EVALUATION DURING GENERATION
```

If you're judging ideas while generating them, you're not brainstorming.

## When to Use

Use for ANY design decision or uncertainty in the FOLIO/Eureka codebase:
- Designing a new FOLIO module interface or API contract
- Choosing between architectural approaches (e.g., synchronous vs. event-driven)
- Solving a performance bottleneck in a Spring Boot service
- Planning Keycloak integration strategy for a new tenant type
- Deciding how to handle a Liquibase migration for a breaking schema change
- Resolving a cross-module dependency or ordering problem
- Identifying risks before starting a large feature
- Unblocking when multiple team members disagree on approach

**Use this ESPECIALLY when:**
- The first solution that comes to mind seems obvious (obvious ≠ best)
- The team is stuck in a single framing of the problem
- A past solution is being reapplied by habit, not by analysis
- You're about to commit to an approach you haven't fully examined
- The problem crosses multiple FOLIO module or service boundaries

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Problem Framing

**Before generating any ideas:**

1. **State the problem clearly in one sentence**
   - What are we actually trying to solve?
   - Write it down explicitly
   - If you can't state it in one sentence, the problem is not yet understood

2. **Identify constraints**
   - Hard constraints (must not break): published FOLIO interface versions, backward-compatible Liquibase migrations, Keycloak realm boundaries, Okapi routing contracts
   - Soft constraints (prefer not to): increase deployment complexity, add new inter-module dependencies, require coordinated releases
   - Known unknowns: what do we not yet know that could change the answer?

3. **Identify success criteria**
   - What does a good solution look like?
   - How will we know it worked?
   - What would make this solution better than the status quo?

4. **Check the framing**
   - Are we solving the right problem?
   - Is this a symptom of a deeper issue?
   - Would solving this create a new problem elsewhere in the module graph?

### Phase 2: Idea Generation

**Rules during this phase:**
- ✅ Generate as many options as possible — aim for at least 5-7
- ✅ Include unconventional, ambitious, and even "bad" ideas
- ✅ Build on ideas with variations ("what if we took option 3 but applied it at the API layer?")
- ❌ No evaluation, no "but that won't work because..."
- ❌ No anchoring on the first idea
- ❌ No dismissing ideas as too simple or too complex

**Idea categories to consider in FOLIO context:**

| Category | Prompts |
|---|---|
| **Interface-level** | Could this be solved by changing the FOLIO interface contract? Adding a new interface? Versioning up? |
| **Module boundary** | Should this logic live in a different module? Could a new lightweight module own this? |
| **Infrastructure** | Is this a Keycloak, Eureka, or Okapi-level concern rather than a module concern? |
| **Data layer** | Could a schema change, index, or Liquibase migration solve this more cleanly than code? |
| **Event-driven** | Would an async/messaging approach remove coupling that makes this hard? |
| **Simplification** | What is the simplest possible version of this that still meets the criteria? |
| **Do nothing** | Is the current behaviour acceptable? Are we solving a non-problem? |
| **Existing patterns** | Does another FOLIO module already solve an analogous problem? Can we reuse its pattern? |

**Generation format:**
```
Option 1: [Name]
  Approach: [One sentence]
  How it works: [2-3 sentences]

Option 2: ...

(continue until 5-7+ options generated)
```

### Phase 3: Evaluation

**Only after Phase 2 is complete:**

1. **Score each option** against the success criteria and constraints from Phase 1

   Use a simple matrix:

   | Option | Meets criteria | Fits constraints | Complexity | Risk | Reversible? |
   |--------|---------------|-----------------|------------|------|-----------|
   | Option 1 | ✅/⚠️/❌ | ✅/⚠️/❌ | Low/Med/High | Low/Med/High | Yes/No |
   | ... | | | | | |

2. **Prefer reversible over irreversible**
   - FOLIO interface changes and Liquibase migrations are hard or impossible to undo
   - Prefer approaches that can be rolled back or evolved incrementally
   - Flag any option that requires a coordinated multi-module release

3. **Prefer simple over clever**
   - The solution that is easiest for a new Eureka team member to understand is usually better
   - Clever solutions create maintenance debt

4. **Consider the failure modes**
   - What happens when this option goes wrong?
   - Is the failure detectable and recoverable?
   - Does failure stay contained within one module or cascade?

5. **Identify the top 2-3 candidates** with reasoning
   - Don't force a single winner if two options are genuinely close
   - It's valid to say "Option A for short term, Option C for long term"

### Phase 4: Decision and Next Steps

1. **Select the approach** (or the top 2 if genuinely tied)
   - State the choice and the key reasons
   - Explicitly note which constraints it satisfies and which trade-offs it accepts

2. **Identify open questions**
   - What do we still not know?
   - What needs a spike or proof-of-concept before full implementation?

3. **Define next steps**
   - What is the first concrete action?
   - Does this need team alignment before proceeding?
   - Does it need an RFC or architectural decision record (ADR)?

4. **Write a plan** (hand off to `writing-plans` skill if scope is large)

## Anti-Patterns

| Pattern | Problem |
|---------|----------|
| Jumping to the first idea | Anchoring bias — the first idea shapes all subsequent thinking |
| Evaluating while generating | Kills unconventional options before they're explored |
| Only considering module-level solutions | FOLIO problems often have infrastructure-level solutions |
| Reusing the last approach by default | What worked for one module may not fit another's constraints |
| Skipping Phase 1 | Without clear problem framing, good ideas solve the wrong problem |
| Declaring consensus prematurely | Silent non-disagreement ≠ agreement — ask for explicit objections |

## Quick Reference

| Phase | Key Output | Done When |
|-------|-----------|----------|
| **1. Framing** | Problem statement, constraints, success criteria | Can state the problem in one sentence |
| **2. Generation** | 5-7+ diverse options | Evaluation urge resisted throughout |
| **3. Evaluation** | Scored matrix, top 2-3 candidates | Each option assessed against Phase 1 criteria |
| **4. Decision** | Chosen approach, open questions, next steps | Clear next action defined |
