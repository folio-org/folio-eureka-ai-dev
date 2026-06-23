# AI Test Case Generation — MQA Team Guide

**TL;DR:** A Copilot agent now writes and posts manual test cases to TestRail from a Jira story in one command. This guide explains how to use it, what to feed it, and how to improve it.

---

## What Changed

The `write-testrail-cases` skill is a Copilot agent that:

1. Reads a Jira story (by ticket ID)
2. Loads business-logic context for the relevant FOLIO app
3. Enriches context automatically from Jira, GitHub, and TestRail if needed
4. Proposes a set of test scenarios for your review
5. Generates structured manual test cases after you confirm
6. Posts them directly to TestRail via API — with all metadata filled in

The agent understands FOLIO's domain: it knows which team owns which module, where the GitHub repos live, which TestRail sections map to which application area, and how capability sets work in Eureka. You don't need to spell that out.

---

## Installation and Updates

Skills live in the shared repository [`folio-org/folio-eureka-ai-dev`](https://github.com/folio-org/folio-eureka-ai-dev). Copilot pulls them automatically when you open the workspace — but they don't update themselves.

### First-time setup

If you haven't installed the skills yet, run once in the repo root:

```bash
npx skills update folio-org/folio-eureka-ai-dev
```

### Keeping skills up to date

**Run this command before starting a new session** — especially after the team announces a skill update in the channel:

```bash
npx skills update folio-org/folio-eureka-ai-dev
```

That's it. The command pulls the latest `SKILL.md` files, context files, and examples from the repo. No restart needed — changes take effect in the next Copilot session you open.

> **Why does this matter?** Bug fixes, new context files, and calibration improvements are pushed to the repo regularly. An outdated skill may generate cases with the wrong style, wrong capability set names, or miss newly added business rules. When in doubt — update.

---

## Quick Start

The shortest prompt that works:

```
Use the write-testrail-cases skill to cover UIBULKED-123.
```

The agent will detect the area, load context, and present a Scenario Analysis for your approval before generating anything. **It will not post cases until you confirm.**

---

## Recommended Prompt (copy and adapt)

```
Use the write-testrail-cases skill to cover UICHKIN-485.

Fetch the story from Jira and proceed through the full Mandatory Workflow.
Present the Scenario Analysis before generating any cases —
I'll confirm or adjust coverage before you write.

Additional context:
- This is a Check In area story (team: Vega)
- Focus on the happy path and the two negative scenarios from the
  acceptance criteria — skip load/performance for now
- TestRail section for posting: 17150

Do not post until I explicitly confirm the preview.
```

**What each part does:**

| Part | Why it helps |
|---|---|
| Jira ticket ID | Agent pulls summary, AC, dev team, fix version automatically |
| "Present Scenario Analysis" | You review coverage before any cases are written — easy to add/remove scenarios |
| Additional context | Optional — helps when area auto-detection might be ambiguous or you want to constrain scope |
| Section ID | Saves a back-and-forth at the end |
| "Do not post until I confirm" | Safety net — agent waits for your explicit "yes" before writing to TestRail |

---

## What the Agent Uses to Generate Cases

The agent pulls context from three layers, in order:

### 1. The Jira Story
Acceptance criteria, description, dev team, fix version. The story is always the primary source — if anything conflicts with other sources, the story wins.

### 2. Context Files (`references/context/`)
Each FOLIO application area has a dedicated context file that describes:
- Domain model and record hierarchy
- Lifecycle statuses and transitions
- Key business rules (each rule = a potential test scenario)
- Exact UI texts: toast messages, modal titles, confirmed capability set names

Currently available: **Agreements, Bulk Edit, Check In, Check Out, Consortium Manager, Data Export, Data Import, eHoldings, Finance, Inventory, Invoices, Licenses, Lists, MARC Authority, Mediated Requests, OAI-PMH, Orders, Receiving, Requests, Users.**

### 3. Live Enrichment (automatic fallback)
If the context file is missing, out of date, or has too few business rules, the agent automatically fetches:
- GitHub: `en_US.json` (exact UI strings), `package.json` (capability sets), Cypress fragments (UI labels)
- Jira: acceptance criteria from subtasks and linked bugs
- It knows where to look based on the module/team — you don't need to provide URLs

---

## The Scenario Analysis Step

Before writing any cases, the agent presents a plan like this:

```
I've read UIBULKED-123 and the Bulk Edit context.
Business rules touched: #3 (identifier gating), #7 (preview before commit), #12 (errors accordion).

Happy path:
1. User can upload a valid CSV and reach the preview screen → Critical Path

Business-rule verification:
2. Error accordion is displayed and expanded by default after processing with invalid identifiers → Critical Path

Capability boundaries:
3. User without Bulk Edit Edit capability set cannot access the commit button → Critical Path

Negative / edge cases:
4. Upload fails gracefully when CSV contains only invalid identifiers → Extended

Does this coverage look complete? Any scenarios to add or remove?
```

**This is your most important interaction point.** Reply with adjustments before saying "go ahead":
- "Add a scenario for the download errors CSV button"
- "Skip scenario 4, we have that covered elsewhere"
- "Split scenario 2 into separate cases for Users and Items"

---

## What Good Generated Cases Look Like

The agent is calibrated on 195 real team cases (Trillium/Umbrellaleaf/Sunflower releases, sections 98/105/329/454/96/17140/17995/23689). Expected output characteristics:

- **Imperative steps**: "Click Actions menu", "Navigate to Finance app > Fund A > Transactions" — not "User B clicks"
- **Absolute values in expected results**: `Encumbered = 0.00`, `Available = 200.00` — never "increased by 50"
- **Exact toast text**: `"The Purchase order - <PO number> has been successfully opened"` — never "success toast displayed"
- **Business-critical table rows verified column by column**: Type, Source, Amount, Status — not "transaction is displayed"
- **Numbered preconditions** referenced in steps as "Preconditions #3"
- **5–10 steps** per case (team median is 9)
- **Labels: AI** added to every generated case automatically

---

## How to Give Feedback

The skill is in alpha — your feedback directly improves it. Three channels:

### 1. Fix a context file yourself
Context files live in `write-testrail-cases/references/context/<area>.md`. You know these apps better than any automated extraction process. Open the file, fix what's wrong, add what's missing. The most valuable additions:
- Missing business rules (add to the "Key Business Rules" section)
- Exact toast texts the agent gets wrong (add to "Exact UI Texts")
- Correct capability set names (the agent sometimes uses legacy permission names)
- ECS-specific behaviour if the file doesn't cover it

**No special process needed — just edit the file and commit.**

### 2. Talk to the build-app-context agent
`build-app-context` is a companion agent that regenerates context files from live data. If a file is stale or missing:

```
Use the build-app-context skill to build context for the Requests app.
TestRail section ID: 96
```

The agent will pull 100–300 cases from TestRail, read GitHub translation files and permission sets, query Jira closed stories and bugs, and produce an enriched context file. You can give it extra guidance:

```
Use the build-app-context skill to build context for the Agreements app.
TestRail section ID: 130
Jira component: Agreements
GitHub repos: folio-org/ui-agreements, folio-org/mod-agreements, folio-org/stripes-erm-components
Releases to focus on: Umbrellaleaf, Trillium, Sunflower

Additional notes:
- Agreements is part of the ERM suite alongside Licenses and eHoldings
- Key integration points: Licenses app, eHoldings, Orders, Organizations
- K-Int team owns this module
```

### 3. Report what's wrong with a specific case
If the agent generates a bad case, the most useful feedback includes:
- What was wrong (wrong business rule? invented UI label? missing scenario? too few steps?)
- The Jira ticket it was generated from
- What the correct case should look like (a real case from TestRail is ideal)

Post in the team channel or open a comment in the PR that modifies the context file.

---

## Known Limitations (Alpha)

| Issue | Status |
|---|---|
| ECS Enabled sometimes set to No for ECS stories | Fixed in latest SKILL.md — requires new agent session |
| `refs` field picks up linked bugs/spikes in addition to the story key | Fixed in latest SKILL.md — the agent should set only the original story key |
| Context files for some areas are thin (docs-only, no live TestRail data yet) | Help wanted — edit the file or run build-app-context for your area |
| Jira access is restricted for some projects (ERM, MARC Authority, OAI-PMH) | Known — those context files rely on TestRail + GitHub only |
| Agent may use legacy permission names if context file has them | Fix: update "Capability Sets" section in the relevant context file |

---

## Files Reference

```
.agents/skills/
├── write-testrail-cases/
│   ├── SKILL.md                    ← agent instructions (v1.5.0, calibrated)
│   └── references/
│       ├── examples.md             ← golden cases the agent learns style from
│       └── context/
│           ├── bulk-edit.md        ← 730 cases, Trillium-heavy
│           ├── check-in.md
│           ├── check-out.md
│           ├── consortium-manager.md ← 380 cases
│           ├── data-export.md
│           ├── data-import.md
│           ├── finance.md          ← 249 cases
│           ├── inventory.md        ← 775 cases + Jira + GitHub
│           ├── invoices.md         ← 276 cases
│           ├── licenses.md
│           ├── marc-authority.md
│           ├── oai-pmh.md
│           ├── orders.md
│           ├── receiving.md
│           ├── requests.md
│           ├── users.md
│           └── ...
└── build-app-context/
    └── SKILL.md                    ← context file generation agent
```

---

## FAQ

**Q: Do I need to provide the TestRail section ID?**
You can give it upfront in the prompt (recommended) or the agent will ask after you confirm the cases.

**Q: Can I generate cases for a story that spans two apps?**
Yes — the agent reads both context files automatically. Just mention both in the prompt if you want to be explicit: "This story touches Orders and Finance."

**Q: What if the context file for my area doesn't exist?**
The agent warns you and generates from the story alone. Results will be less accurate for domain-specific preconditions. Use `build-app-context` to create the file.

**Q: Can I adjust a generated case before it's posted?**
Yes — after the agent shows the posting preview, reply "edit case 3: change the priority to Medium and add a step verifying the toast message" before confirming.

**Q: The agent posted cases with wrong metadata. How do I fix them?**
```
Update TestRail case C[ID]: set ECS Enabled to true, 
set refs to UIBULKED-123 only.
```

**Q: Can I run this for multiple stories at once?**
Run one story per session. The agent's context window is better focused on one story at a time — mixing stories risks scenarios bleeding across cases.
