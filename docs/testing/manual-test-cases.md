# QA Onboarding: OpenCode + the `write-testrail-cases` Skill

A practical guide for QA engineers to start using OpenCode (or Claude Code) to turn a Jira story into **TestRail test cases** with the team's `write-testrail-cases` skill — written in the FOLIO QA team's own style and posted straight into TestRail.

## What you will learn

- What the `write-testrail-cases` skill does and why it exists.
- What you need before your first run (agent, model, TestRail + Jira credentials).
- How to install the FOLIO QA skills.
- The end-to-end workflow: Jira key → confirmed scenarios → cases posted in TestRail.
- The two confirmation gates that keep you in control.

---

## 1. What the skill does

`write-testrail-cases` reads a Jira story (by key, or pasted) and generates **manual test cases for TestRail** (project 14 "FOLIO Bug Fest", suite 21) that match how the real FOLIO QA team writes:

- **Detects the application area** (Orders, Inventory, Finance, Check-in, …) and loads a curated context file with that area's exact UI strings, business rules, and house style (Type, typical size, journey usage).
- **Analyses the story into scenarios** — happy path, business-rule verification, capability boundaries, negative/edge cases, and inferred integration journeys (rollover, from-template, ECS) — and **shows you the list first**.
- **Writes each case** with numbered preconditions, imperative steps, and terse observable expected results, using the correct metadata (Type, Priority, Test Group, Release, Dev Team, `refs`).
- **Posts to TestRail via API** after you confirm a preview and give a Section (folder) ID — and returns the created `C…` case numbers.

It is agentic: it asks you clarifying questions, waits for your confirmation twice, and never posts anything until you say so.

> Where it runs: this guide uses the **OpenCode Desktop App** (to match the team's other onboarding guides). The skill is agent-agnostic — it works identically in **Claude Code (the VS Code extension)**. If your team standardises on Claude Code, use "Reload Window / new chat" wherever this guide says "start a new chat", and skip the OpenCode-specific `/` commands.

---

## 2. Install OpenCode

The easiest way to start is the standalone **Desktop App**.

1. Go to <https://opencode.ai/download>.
2. Download the installer for your OS (macOS, Windows, or Linux).
3. Run the installer and open the OpenCode app.

*(Terminal/CLI and the Claude Code VS Code extension are both fine alternatives — the skill behaves the same.)*

---

## 3. Connect an LLM provider and pick a model

The agent's "brain" comes from an LLM provider. Connect at least one your employer has approved.

1. In the chat bar type `/connect`, choose your provider (Anthropic/Claude, OpenAI, OpenCode Zen, Copilot, …), and authenticate.
2. Pick a model with `/models`. **Prefer a high-quality reasoning model** (Claude Sonnet/Opus, GPT-5, or your provider's flagship) — case-writing quality matters more than speed.
3. Sanity check: type `Say hello and tell me which model you are.` — if you get a reply, you're ready.

Credentials are stored locally (`~/.local/share/opencode/auth.json` on macOS/Linux; `%APPDATA%\opencode\auth.json` on Windows) and only ever sent to the provider you chose.

---

## 4. Install the FOLIO QA skills

### 4.1 Check for Node.js

`npx` (the skills installer) ships with Node.js.

- **macOS:** ⌘ Space → `Terminal` → Enter.
- **Windows:** Windows + R → `cmd` → Enter.

Run `node --version`. If you see a version number (e.g. `v20.11.0`), continue. If not, install the **LTS** build from <https://nodejs.org> (accept the defaults), restart the terminal, and re-check.

### 4.2 Create a working folder and install the skill

```
mkdir -p ~/folio-testrail-work
cd ~/folio-testrail-work
npx skills add folio-org/folio-eureka-ai-dev --skill write-testrail-cases
```

Verify:

```
npx skills list
```

You should see `write-testrail-cases`. To update later: `npx skills update folio-org/folio-eureka-ai-dev`.

> Prefer to avoid the terminal? Paste this into a new OpenCode chat and follow along:
>
> ```
> Help me set up OpenCode for FOLIO TestRail case drafting as a non-expert.
> Goal: create a local folder for TestRail work and install the write-testrail-cases
> skill from folio-org/folio-eureka-ai-dev.
> Rules: explain each step in plain English; first check Node.js via `node --version`
> and tell me how to open a terminal; if Node is missing, stop and point me to
> https://nodejs.org (LTS) and wait; then guide me to create `folio-testrail-work` in my
> home folder and run the npx install; then help me verify and open the folder in OpenCode.
> ```

### 4.3 Add your credentials (one-time, required for posting)

The skill reads TestRail and Jira credentials from a `.env` file in your working folder. Create `~/folio-testrail-work/.env` with:

```
# TestRail
TESTRAIL_URL=https://foliotest.testrail.io/
TESTRAIL_EMAIL=you@epam.com
TESTRAIL_API_KEY=<your TestRail API key>

# Jira (so the skill can fetch a story by key)
JIRA_BASE_URL=https://folio-org.atlassian.net
JIRA_USER_EMAIL=you@epam.com
JIRA_API_TOKEN=<your Jira API token>
```

- **TestRail API key:** TestRail → *My Settings* → *API Keys* → *Add Key*.
- **Jira API token:** <https://id.atlassian.com/manage-profile/security/api-tokens> → *Create API token*.
- **Keep `.env` private.** Never paste these keys into chat or commit them to git (add `.env` to `.gitignore`). Rotate a key immediately if it's ever exposed.

### 4.4 Open the folder in OpenCode

Open the Desktop App → **File > Open Folder…** → select `~/folio-testrail-work`. Run `/init` once so the agent understands the folder. After this, all normal work happens in the app.

---

## 5. Find your TestRail Section ID (where cases will be posted)

The skill posts into a specific TestRail **section** (folder). Get its ID from the URL:

1. Open TestRail → project 14, suite 21 → open the folder you want.
2. Look at the URL: `…&group_id=114774` — the number after `group_id=` (or `section_id=`) is your **Section ID**.

Have this ready before you post. If you don't provide one, the skill will ask.

---

## 6. The end-to-end workflow

```
┌──────────────┐   ┌───────────────┐   ┌────────────────┐   ┌────────────────┐   ┌───────────────┐
│ 1. Open App  │ → │ 2. Invoke the │ → │ 3. Confirm the │ → │ 4. Confirm the │ → │ 5. Cases live │
│  in the work │   │ skill on a    │   │ scenario list  │   │ posting preview│   │ in TestRail   │
│  folder      │   │ Jira key      │   │ (gate #1)      │   │ + Section ID   │   │ (C… numbers)  │
│              │   │               │   │                │   │ (gate #2)      │   │               │
└──────────────┘   └───────────────┘   └────────────────┘   └────────────────┘   └───────────────┘
```

**Step 1 — Open OpenCode** in `~/folio-testrail-work`.

**Step 2 — Invoke the skill.** Paste a prompt (see Section 7). The skill fetches the Jira story, detects the area, and reads the matching context file.

**Step 3 — Confirmation gate #1: the scenario list.** The skill shows a **Scenario Analysis** (business rules touched + the scenarios it plans to cover, including inferred integration journeys) and **stops**. Add, remove, or reword scenarios, then confirm. Nothing is generated until you do.

**Step 4 — Confirmation gate #2: the posting preview.** After generating and self-reviewing the cases, the skill shows a numbered preview (title / Type / Priority / Test Group) and asks for the **Section ID**. Review it, provide the ID, and confirm.

**Step 5 — Cases are posted.** The skill posts each case via the TestRail API and returns the created `C…` numbers and links.

---

## 7. Example prompts

You don't have to memorise the skill name — mention it and describe what you want.

**Universal prompt** (swap `{JIRA-KEY}` and `{SECTION_ID}`):

```
Use the write-testrail-cases skill to create TestRail cases for Jira story {JIRA-KEY}.

Follow the full skill workflow:
1. Detect the area and read the matching context file. State which area/file you loaded.
2. Fetch {JIRA-KEY} from Jira; extract summary, acceptance criteria, Dev Team, and the
   ticket(s) the cases should reference.
3. FIRST show me the full Scenario Analysis (including an "Inferred integration journeys"
   block) and WAIT for my confirmation. Do not generate or post anything before I confirm.
4. Match the target area's house style (Type, size, journey usage from the context file).
5. Use exact UI strings / validation messages from the story and context file; keep expected
   results terse and observable.
6. After I confirm the scenarios, generate the cases, then show the posting preview and post
   to TestRail section ID {SECTION_ID} — only after I confirm the preview.
```

**Story pasted directly** (no Jira access needed for the read):

```
Use the write-testrail-cases skill for the story below. Show me the scenario list first,
then after I confirm, post to TestRail section {SECTION_ID}.

[paste the story text — summary, description, acceptance criteria]
```

**Dry run only** (see the cases in chat, don't post):

```
Use the write-testrail-cases skill for {JIRA-KEY}. Show me the scenarios, then generate the
cases in the chat only — do NOT post to TestRail. I'll review first.
```

> If you stay quiet, the skill asks for what it needs (area if ambiguous, Section ID, ECS vs non-ECS). Answer in plain English — the agent handles the TestRail formatting and metadata IDs.

---

## 8. Daily-use cheat sheet

| You want to… | Do this |
|---|---|
| Start work | Open the Desktop App in `~/folio-testrail-work` |
| Draft cases for a story | `Use the write-testrail-cases skill for {JIRA-KEY}…` |
| See cases without posting | Add "generate in chat only — do NOT post to TestRail" |
| Post to a folder | Give the **Section ID** when the preview asks |
| Connect / change model | `/connect` · `/models` |
| Undo the last agent turn | `/undo` |
| Share the conversation | `/share` |
| Update the skill | Terminal in the work folder → `npx skills update folio-org/folio-eureka-ai-dev` |

---

## 9. Good habits and pitfalls

**Do**

- Invoke the skill by name ("Use the write-testrail-cases skill…") so it loads the area context and house style.
- Let it show you the **scenario list first** and edit it there — cheaper than fixing 12 posted cases.
- Give the correct **Section ID**; double-check it's the right folder in project 14 / suite 21.
- Trust the area's **house style**: some areas are short atomic cases (Fees&Fines ~2 steps), others are large workflows (Bulk Edit ~14) — the skill matches the local norm.
- Keep expected results **terse and observable** — if a result reads like an explanation, ask the agent to cut it.

**Don't**

- Don't build cases around **unshipped behavior** or hedge with "IF present / IF not" — cover what's actually testable now.
- Don't let expected results become a **wall of text**: a list of `field = value` checks should be bullets, not a semicolon run-on. If you see one, say "bullet the field list in step N".
- Don't invent concrete values where the team uses **symbolic placeholders** (`S`, `<barcode>`) — that's the circulation convention.
- Don't paste API keys, secrets, or real patron data into prompts. Keep them in `.env`.

---

## 10. Where to get help

- OpenCode docs: <https://opencode.ai/docs> · providers: <https://opencode.ai/docs/providers> · Discord: <https://opencode.ai/discord>
- FOLIO skills repo & issues: <https://github.com/folio-org/folio-eureka-ai-dev>
- TestRail API reference: <https://support.testrail.com/hc/en-us/articles/7077196481428-Introduction-to-the-TestRail-API>
- Skill internals (for the curious): `write-testrail-cases/SKILL.md` (workflow, metadata IDs, House Style table) and `references/examples.md` (golden cases + anti-patterns).
- Feedback on the skill: open an issue in the repo above, or note what the skill got wrong so the context files / SKILL can be tuned.

Welcome aboard.
