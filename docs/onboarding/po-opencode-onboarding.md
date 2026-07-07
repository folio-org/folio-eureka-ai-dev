# Product Owner Onboarding: OpenCode + FOLIO Skills

A practical, **non-technical** guide for Product Owners to start using OpenCode
to draft Jira issues with the team's `write-user-story` and `write-bug` skills.

> **What you will learn**
> 1. What OpenCode is and how to install the Desktop App.
> 2. How to connect an LLM provider so the agent can think.
> 3. How to install the FOLIO skills repository.
> 4. How to use the `write-user-story` and `write-bug` skills.
> 5. The **end-to-end workflow** to produce a Jira-ready description.

---

## 1. What is OpenCode?

OpenCode (<https://opencode.ai>) is an open-source AI agent. It is the same kind of tool developers use to write code, but you can use it for any **structured writing task** — including drafting Jira tickets.

OpenCode comes in multiple forms, but for Product Owners, the **Desktop App** is the easiest way to get started.

| Form | What it is | When to use it |
|------|------------|----------------|
| **Desktop App** | A standalone graphical application. You chat with the agent, see its progress, attach files, and approve actions easily. | **Recommended for POs.** Use this for everything below. |
| **Terminal (command-line)** | A text-based tool that runs in your terminal. | Power-user automation. You won't need it on day one. |

---

## 2. Install OpenCode

### 2.1 Download the Desktop App

The easiest way to get started is to download the standalone Desktop App.

1. Go to **<https://opencode.ai/download>**
2. Download the installer for your operating system (macOS, Windows, or Linux).
3. Run the installer and open the OpenCode app.

*(Note: If you prefer the terminal, you can install the CLI version via `curl -fsSL https://opencode.ai/install | bash` or Homebrew, but the Desktop App provides a friendlier chat interface.)*

---

## 3. Connect an LLM provider

OpenCode is just the agent — the "brain" comes from a Large Language Model
(LLM) provider. You need to connect at least one. **Pick whichever your
employer has approved.**

### 3.1 Start OpenCode

Open the **OpenCode Desktop App**. You will see a chat interface. Like the terminal version, you can use `/` commands to configure settings.

### 3.2 Connect your provider

In the chat bar, type:

```
/connect
```

A picker appears. Choose your provider. The most common choices for POs:

| Provider | When to choose | What you'll need |
|----------|----------------|------------------|
| **OpenCode Zen** | You want a curated, pre-tested set of models and a single bill. The OpenCode team recommends this for newcomers. | A Zen account at <https://opencode.ai/auth> and a payment method. |
| **Anthropic (Claude)** | Your team already has Claude Pro/Max or an Anthropic API key. | OAuth login (Claude Pro/Max), or an API key from <https://console.anthropic.com>. |
| **OpenAI (ChatGPT)** | Your team uses ChatGPT Plus/Pro or has an OpenAI API key. | OAuth login or an API key from <https://platform.openai.com/api-keys>. |
| **GitHub Copilot** | Your team already pays for Copilot. | Device-code login at <https://github.com/login/device>. Some models need Copilot Pro+. |
| **GitLab Duo** | Your team uses GitLab Premium/Ultimate with Duo enabled. | OAuth or a GitLab personal access token (`api` scope). |

OpenCode supports 75+ providers; the full list lives at
<https://opencode.ai/docs/providers/>. The flow is the same: `/connect` →
choose provider → authenticate → done.

> **Where are credentials stored?** Locally on your machine in
> `~/.local/share/opencode/auth.json` (macOS/Linux) or
> `%APPDATA%\opencode\auth.json` (Windows). They never leave your computer
> except when sent to the provider you chose.

### 3.3 Pick a model

Once a provider is connected, choose which model the agent uses:

```
/models
```

A picker shows the models that provider exposes. For drafting Jira tickets,
prefer a **higher-quality reasoning model** (e.g. Claude Sonnet/Opus, GPT-5,
or whichever your provider's flagship is) — quality of writing matters more
than speed.

### 3.4 Sanity check

Type a quick prompt at the bottom and press Enter:

```
Say hello and tell me which model you are.
```

If you get a response, you are ready.

---

## 4. Install the FOLIO Product Owner skills

Before you can use the `write-user-story` and `write-bug` skills, OpenCode
needs a local working folder and the FOLIO Product Owner preset installed in it.

The PO preset installs these four skills:

- `folio-ecosystem`
- `write-user-story`
- `write-bug`
- `skill-feedback`

There are two ways to do this. **Pick the one that suits you best.**

---

### Option A — Guided setup inside OpenCode *(recommended)*

If you prefer to avoid the terminal entirely, OpenCode can walk you through
the setup step by step.

1. Open the **OpenCode Desktop App** and start a new chat.
2. Make sure you have a model connected (see Section 3).
3. Copy and paste the prompt below into the chat and press Enter.
4. Follow the agent's instructions one step at a time.

> **Important:** OpenCode can guide you through installation, but it cannot
> install Node.js for you if it is missing. If Node.js is not on your machine
> yet, the agent will stop and direct you to install it first — just follow
> those instructions, then come back and continue.

#### Ready-to-paste setup prompt

```
Help me set up OpenCode for FOLIO Product Owner ticket drafting in a way
that is safe for a non-technical user.

My goal:
- Create a local folder for Jira drafting work.
- Install the FOLIO Product Owner skills from folio-org/folio-eureka-ai-dev.
- Make sure I can use folio-ecosystem, write-user-story, write-bug, and skill-feedback in OpenCode.

Please follow these rules:
1. Explain each step in plain English before asking me to do it.
2. Do not assume I know terminal commands.
3. First, check whether Node.js is installed by asking me to run
   `node --version` and explain how to open a terminal on my
   operating system.
4. If Node.js is missing, stop and tell me to install the LTS version
   from https://nodejs.org, then wait for me to confirm before
   continuing.
5. Once Node.js is confirmed, guide me to create a folder named
   `folio-jira-drafts` in my home directory.
6. Then guide me to open that folder in a terminal and run:
      npx skills add folio-org/folio-eureka-ai-dev --skill folio-ecosystem --skill write-user-story --skill write-bug --skill skill-feedback
7. After installation, help me verify that the skills are available.
8. Then remind me how to open that folder in the OpenCode Desktop App
   and run `/init` if needed.
9. At the end, give me a short checklist confirming that setup
   is complete.

If there is a simpler OpenCode-native way to install or verify skills
from inside the app, prefer that and explain it clearly.
```

---

### Option B — Manual setup

If you are comfortable with a terminal, you can run the steps directly.

#### 4B.1 Check for Node.js

`npx` is a tool that comes with **Node.js**. It lets you run small programs
(like the skills installer) without manually installing anything extra.
If Node.js is not installed yet, the commands below will not work.

Open a terminal:
- **macOS:** press ⌘ Space, type `Terminal`, press Enter.
- **Windows:** press Windows + R, type `cmd`, press Enter.

Then run:

```bash
node --version
```

- If you see a version number (e.g. `v20.11.0`), continue to the next step.
- If you see an error, install the **LTS** version of Node.js from
  <https://nodejs.org> (just click the LTS download button and run the
  installer, accepting all defaults). Restart your terminal and re-run
  `node --version` to confirm.

#### 4B.2 Pick a project folder

Skills are installed into a specific project folder. For PO work, create a
folder to hold your drafts:

```bash
mkdir -p ~/folio-jira-drafts
cd ~/folio-jira-drafts
```

Alternatively, create the folder using your file manager (Finder on macOS,
File Explorer on Windows) — navigate to your home folder, right-click, and
create a new folder named `folio-jira-drafts`.

#### 4B.3 Install the skills

From inside that folder, run:

```bash
npx skills add folio-org/folio-eureka-ai-dev --skill folio-ecosystem --skill write-user-story --skill write-bug --skill skill-feedback
```

This installs the Product Owner preset into the folder. It includes
`folio-ecosystem`, `write-user-story`, `write-bug`, and `skill-feedback`.
To update later:

```bash
npx skills update folio-org/folio-eureka-ai-dev
```

See the [README](../../README.md) for other role presets and the advanced
all-skills install option.

#### 4B.4 Verify the install succeeded

After the command finishes, check what was installed:

```bash
npx skills list
```

You should see `folio-ecosystem`, `write-user-story`, and `write-bug` listed.
If not, re-run the install command above. You should also see
`skill-feedback`, because it is part of every role preset.

---

### 4.1 Launch OpenCode in that folder *(both options)*

Open the **OpenCode Desktop App** and use the **File > Open Folder...** menu
(or the equivalent button in the UI) to open `~/folio-jira-drafts`.

Inside the chat, run **once per project**:

```
/init
```

This generates an `AGENTS.md` file so the agent understands the folder. For
a drafts folder you can keep the defaults.

> **After this one-time setup, all normal PO work happens inside the
> OpenCode Desktop App.** You will not need to touch a terminal again
> unless you want to update the skills package.

---

## 5. The two PO writing skills

You will use these two skills the most:

### 5.1 `write-user-story`

Produces a **structured user story** with:

- Purpose / Overview (business context, persona, links)
- Functional requirements
- **Acceptance criteria in Given-When-Then format**
- Manual testing guidance

Full reference: [`skills/write-user-story/SKILL.md`](../../skills/write-user-story/SKILL.md)

### 5.2 `write-bug`

Produces a **reproducible FOLIO bug report** with:

- A summary that passes the "scan test" (`[Area] symptom when trigger`)
- Preconditions
- Numbered, atomic steps to reproduce
- Expected vs actual results
- Evidence (logs, stack traces, screenshots, reproducibility rate)
- Optional: file the bug straight into Jira via MCP

Full reference: [`skills/write-bug/SKILL.md`](../../skills/write-bug/SKILL.md)

---

## 6. Example prompts

You don't need to memorise the skill names — just describe what you want and
mention the skill. The agent will load it automatically.

### 6.1 `write-user-story` — example prompts

**Example 1 — Brand new feature, you have a rough idea:**

```
Use the write-user-story skill to draft a story for this feature:

As a circulation librarian I want to bulk-renew loans for a patron so that
I don't have to renew each loan one by one when a patron walks up to the desk.

Context:
- Affects the ui-users patron details screen.
- Should respect the patron's loan-policy renewal limits.
- A failure on one loan should not block the others.
- Out of scope: API for third-party renewal.

Ask me follow-up questions before drafting if anything is unclear.
```

**Example 2 — You already have raw notes from a stakeholder call:**

```
I just got off a call with the cataloging team. Here are my notes:

- They want an "undo" on the inventory record-edit screen
- Only the last edit needs to be reversible (within 5 minutes)
- Must work for instances, holdings AND items
- Audit log entry is required for every undo
- Person: a metadata librarian doing a quick fix

Use the write-user-story skill to turn this into a proper FOLIO story with
Given-When-Then acceptance criteria. Flag anything you had to assume.
```

**Example 3 — Refining an existing story:**

```
Use the write-user-story skill to review and rewrite the story below.
Tighten the acceptance criteria, add an error scenario, and remove anything
that prescribes implementation:

[paste the existing story here]
```

### 6.2 `write-bug` — example prompts

**Example 1 — You have a clear reproduction:**

```
Use the write-bug skill to file this defect.

What I saw:
- On folio-etesting-snapshot, when I update the receiptDate on a POL
  the audit history's updatedDate field stays the same.
- Reproduces every time on Orders, mod-orders 13.0.5.
- Expected: audit history updatedDate should change to "now".
- Target Jira project: MODORDERS.

Ask me only for things you can't reasonably leave to triage.
```

**Example 2 — You only have a symptom and need help:**

```
Use the write-bug skill. I think there's a bug but I'm not 100% sure how to
reproduce it. Walk me through the questions I need to answer, then draft
the ticket.

Symptom: the expended amount on an order shows the foreign-currency value
instead of the tenant's base currency after I pay an invoice in EUR on a
USD tenant.
```

**Example 3 — You already have a stack trace:**

```
Use the write-bug skill to file a P2 bug. Here's a stack trace from the
mod-inventory log when a user tries to move holdings between instances on
the bugfest environment:

[paste stack trace here]

The user is a cataloger; happens about 3 of 10 attempts. Target project:
MODINV. Suggest a summary that follows the [Area] symptom when trigger
format.
```

> **Tip.** If you stay quiet, the skill will ask you for the things it needs
> (target Jira project, environment, reproducibility, evidence, expected vs
> actual). Answer in plain English; the agent does the formatting.

---

## 7. End-to-end workflow: from idea to Jira description

This is the workflow we want every PO to use.

```
┌──────────────┐   ┌────────────┐   ┌───────────┐   ┌──────────────┐   ┌────────────┐
│ 1. Open App  │ → │ 2. Invoke  │ → │ 3. Answer │ → │ 4. Review &  │ → │ 5. Paste   │
│    in drafts │   │ the skill  │   │ follow-up │   │ iterate on   │   │ into Jira  │
│    folder    │   │ in plan    │   │ questions │   │ the draft    │   │ (or let    │
│              │   │ mode       │   │           │   │              │   │ MCP do it) │
└──────────────┘   └────────────┘   └───────────┘   └──────────────┘   └────────────┘
```

### Step 1 — Open OpenCode in your drafts folder

Open the Desktop App and open your `~/folio-jira-drafts` folder.

### Step 2 — Switch to **Plan mode** before drafting

Click the **Plan/Build toggle** (or press **Tab**) to switch the interface into *Plan* mode.

In plan mode the agent will not write any files — it will only **propose** a
draft in the chat. This is exactly what you want for ticket writing.

### Step 3 — Invoke the skill with your prompt

Use one of the prompt templates from [Section 6](#6-example-prompts). For
example:

```
Use the write-user-story skill to draft a FOLIO story for...
```

### Step 4 — Answer the agent's clarifying questions

Both skills are designed to ask you what they need:

- `write-user-story` will probe for **persona, value, requirements, and edge
  cases**.
- `write-bug` will probe for **target Jira project, environment,
  reproducibility, evidence, and expected vs actual** behaviour.

Answer in natural language — bullet points, fragments, or full sentences all
work.

### Step 5 — Iterate on the draft

The agent posts a draft in Markdown. Read it against the skill's checklist
(both skills include one near the bottom of `SKILL.md`). Then refine:

```
Tighten AC2 — the trigger isn't specific enough. Also add an AC for what
happens when the patron has zero renewable loans.
```

```
The summary doesn't pass the scan test. Rewrite it as
"[Area] symptom when trigger" and propose 3 alternatives.
```

```
Add a "Workaround" line to Additional information. The workaround is to
re-open the order and save it again.
```

You can repeat this freely. If you go off track, you can also run:

```
/undo
```

…to revert the most recent assistant turn and try again.

### Step 6 — Get Jira-flavoured markup

The drafts are written in Markdown. **Jira does not render Markdown natively**
(unless your project has the Markdown macro installed). Both skills ship a
`references/jira.md` reference for converting Markdown to Jira wiki markup.
Just ask:

```
Convert the final draft to Jira wiki markup. Use {code} blocks for stack
traces and h2./h3. for headings.
```

The agent returns a version you can paste directly into the Jira **Description**
field.

### Step 7 — File the ticket

You have two options:

**Option A — Manual (everyone can do this).**
Copy the Jira-markup version, open Jira, create a new issue in the right
project, paste the description, and set priority/components/labels yourself.

**Option B — Automatic via the Jira MCP integration (if your team has it set up).**
The `write-bug` skill explicitly supports this (see "Optional: file the bug
in Jira" inside [`skills/write-bug/SKILL.md`](../../skills/write-bug/SKILL.md)).
After approving the draft, just say:

```
Looks good. Search Jira for duplicates first, show me the top matches,
then create the issue in MODORDERS as a Bug with priority P2.
```

The agent will:
1. Run a duplicate search via Jira MCP and show you matches.
2. Create the issue once you confirm.
3. Return the issue key and URL.

> If `mcp-atlassian_jira_create_issue` is not available in your environment,
> the agent will tell you and you can fall back to **Option A**.

### Step 8 — Save your work (optional)

If you want to keep a local archive of every ticket you draft:

```
Save the final Markdown draft to drafts/<JIRA-KEY>.md in this folder.
```

Switch out of plan mode first by pressing **Tab** again (the same Tab you
used in Step 2) so the agent is allowed to write files.

### Step 9 — Share the conversation (optional)

If a teammate wants to see how you arrived at the draft:

```
/share
```

A shareable URL is copied to your clipboard.

---

## 8. Daily-use cheat sheet

| You want to… | Do this |
|---|---|
| Start OpenCode | Open the Desktop App and point it to `~/folio-jira-drafts` |
| Switch between **Plan** (read-only) and **Build** (can write files) modes | Click the Plan/Build toggle (or press **Tab**) |
| Connect a new LLM provider | `/connect` |
| Change the active model | `/models` |
| Undo the last assistant turn | `/undo` |
| Redo what you just undid | `/redo` |
| Share the conversation with a teammate | `/share` |
| Get a list of all commands | `/help` |
| Reference a file in your prompt | Type `@` and start typing the filename |
| Add a screenshot to a prompt | Drag and drop the image into the chat |
| Update FOLIO skills to the latest version | Open a terminal in your `folio-jira-drafts` folder and run `npx skills update folio-org/folio-eureka-ai-dev`. If `npx` is not recognised, install Node.js LTS from <https://nodejs.org> first. |

---

## 9. Good habits and pitfalls

**Do**
- Always invoke the skill by name ("Use the `write-user-story` skill…"). It
  loads the right structure and checklist.
- Use **Plan mode** for ticket drafting. You don't want the agent writing
  files until you ask.
- Let the skill ask you questions instead of front-loading every detail.
- Iterate. The first draft is rarely the final draft.
- Run a duplicate search before filing a bug.

**Don't**
- Don't paste secrets, real patron data, or production credentials into
  prompts.
- Don't skip the persona / business value in a user story — that's what
  separates a story from a task.
- Don't propose a fix inside a bug ticket. That belongs in the PR or a
  follow-up story.
- Don't worry about Markdown vs Jira markup until the final step — the agent
  converts for you.

---

## 10. Where to get help

- **OpenCode docs:** <https://opencode.ai/docs>
- **OpenCode providers list:** <https://opencode.ai/docs/providers>
- **OpenCode troubleshooting:** <https://opencode.ai/docs/troubleshooting>
- **OpenCode Discord:** <https://opencode.ai/discord>
- **FOLIO skills repo & issues:** <https://github.com/folio-org/folio-eureka-ai-dev>
- **Skill feedback:** invoke the `skill-feedback` skill at the end of a
  session, or open an issue directly in the repo above.

Welcome aboard.
