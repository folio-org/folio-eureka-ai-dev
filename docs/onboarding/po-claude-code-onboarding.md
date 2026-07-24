# Product Owner Onboarding: Claude Code + Jira MCP

A practical, **non-technical** guide for Product Owners to start using Claude
Code to draft Jira issues with the team's `write-user-story` and `write-bug`
skills — and file them straight into Jira.

> **What you will learn**
> 1. What Claude Code is and how to install the Desktop app.
> 2. How to install the FOLIO Product Owner plugin — **Option A** (a settings
>    file in your drafts folder, no terminal) or **Option B** (two one-time
>    terminal commands).
> 3. How to connect Jira with a normal browser login — no tokens.
> 4. How to use the `write-user-story` and `write-bug` skills.
> 5. The **end-to-end workflow** from idea to a filed Jira issue.

> **Terminal-free daily use.** Everything you do day-to-day happens inside
> the Claude Code Desktop app. Only the one-time plugin install offers a
> choice: **Option A** stays entirely in the app; **Option B** uses a
> terminal once, for two commands. Unlike the
> [OpenCode setup](po-opencode-onboarding.md), no Node.js is required either
> way.

---

## 1. What is Claude Code?

Claude Code (<https://code.claude.com/docs/en/quickstart>) is Anthropic's AI
agent. It is the same tool developers use to write code, but it works for any
**structured writing task** — including drafting Jira tickets.

It comes in two forms. For Product Owners, the **Desktop app** is the easiest
way to get started.

| Form | What it is | When to use it |
|------|------------|----------------|
| **Desktop app** | A standalone graphical application. You chat with the agent, open folders with a click, and approve actions with buttons. | **Recommended for POs.** Use this for everything below. |
| **Terminal (CLI)** | A text-based tool that runs in your terminal. | Power users — plus the one-time setup in [Option B](#option-b--one-time-terminal-setup). See [Appendix A](#appendix-a--terminal-cli-reference). |

> **Good to know:** slash commands you may see in blog posts — `/plugin`,
> `/mcp`, `/resume` — belong to the **terminal (CLI)** version. The Desktop
> app uses buttons and menus for the same things. This guide always shows
> the Desktop way first.

---

## 2. Install Claude Code

### 2.1 Download the Desktop app

1. Go to **<https://claude.com/download>**.
2. Download the installer for your operating system (macOS or Windows).
3. Run the installer and open the app.

### 2.2 Sign in

Sign in with your **work Claude account**. Claude Code needs a paid seat
(Claude Pro, Max, Team, or Enterprise). If you don't know which account to
use, ask your team lead — you do **not** need any API keys.

That's it: your Claude account is also the "brain". There is no separate
model-provider setup like OpenCode's `/connect` step.

### 2.3 Sanity check

Open the **Code** area of the app, start a chat, and type:

```
Say hello and tell me which model you are.
```

If you get a response, you are ready.

---

## 3. Create your drafts folder and open it

Claude Code works inside a folder. Create one to hold your Jira drafting
work:

1. In **Finder** (macOS) or **File Explorer** (Windows), go to your home
   folder.
2. Create a new folder named `folio-jira-drafts`.
3. In Claude Code, use the folder picker to open `folio-jira-drafts`
   (the app asks you to choose a folder when you start a new session).

The first time you open a folder, the app asks whether you **trust** it.
Since you just created it yourself, answer yes.

---

## 4. Install the FOLIO PO plugin

The FOLIO Product Owner preset ships as a **Claude Code plugin** called
`folio-po`. One install gives you:

- the PO skills — `write-user-story`, `write-bug`, `skill-feedback`;
- the **official Atlassian Jira MCP server**, pre-configured (you only log
  in — see [Section 5](#5-connect-jira)).

> **Already managed by your org?** If your Claude admin distributes the
> `folio-ai-dev` marketplace through managed settings, you can skip both
> options: click the **+** button next to the prompt box → **Plugins** →
> **Add plugin**, pick `folio-po`, and jump to
> [Section 5](#5-connect-jira).

Pick **one** of the two options below. Both end in the same place: the
`folio-ai-dev` marketplace registered and the `folio-po` plugin installed.

### Option A — Stay in the Desktop app *(recommended)*

The Desktop app cannot register a new plugin marketplace from its menus
yet, but it **does** read a small settings file inside your drafts folder.
You don't have to create that file by hand — ask the agent to do it.

1. Open `folio-jira-drafts` in the Desktop app
   ([Section 3](#3-create-your-drafts-folder-and-open-it)).
2. Paste this prompt into the chat **exactly as written**:

   ````
   Create a file at .claude/settings.json in this folder with exactly this
   content, then show me the result:

   {
     "extraKnownMarketplaces": {
       "folio-ai-dev": {
         "source": {
           "source": "github",
           "repo": "folio-org/folio-eureka-ai-dev"
         }
       }
     },
     "enabledPlugins": {
       "folio-po@folio-ai-dev": true
     }
   }
   ````

3. Approve the file creation when the agent asks.
4. Start a **new session** in the same folder. Claude Code reads the
   settings file and asks you to install the `folio-ai-dev` marketplace and
   trust the `folio-po` plugin. Approve the prompts.
5. **If no prompt appears:** click the **+** button next to the prompt box
   → **Plugins** → **Add plugin**. The plugin browser now lists the
   `folio-ai-dev` marketplace — select `folio-po` and install it.

> **Note:** enabling the plugin through the folder's settings file scopes
> it to this folder. Since all your Jira drafting happens in
> `folio-jira-drafts`, that is exactly what you want.

### Option B — One-time terminal setup

If Option A gives you trouble (or a teammate is setting you up), the
terminal route takes two commands and you never need it again afterwards.
The CLI is a **native binary — Node.js is not required.**

1. Install the CLI.

   **macOS:** open Terminal (⌘ Space, type `Terminal`) and run:

   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   ```

   **Windows:** open PowerShell (Windows key, type `PowerShell`) and run:

   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```

2. Start it in your drafts folder and sign in when prompted:

   ```bash
   cd ~/folio-jira-drafts
   claude
   ```

3. Run these two commands in the chat, one after the other, and approve the
   confirmation prompts:

   ```
   /plugin marketplace add folio-org/folio-eureka-ai-dev
   ```

   ```
   /plugin install folio-po@folio-ai-dev
   ```

4. Type `/exit`, close the terminal, and go back to the Desktop app. The
   Desktop app and the CLI share the same configuration, so the plugin is
   now available in your Desktop sessions too.

### Verify the install (either option)

Start a new session in `folio-jira-drafts` and ask:

```
Which FOLIO skills do you have available?
```

The agent should mention `write-user-story` and `write-bug`. You can also
check visually: in the Desktop app, click **+ → Plugins** and confirm
`folio-po` is listed and enabled (in the CLI, run `/plugin`).

> **Troubleshooting:** if the marketplace is rejected with a policy
> message, your organization restricts plugin marketplaces — ask your
> Claude admin to allow `folio-org/folio-eureka-ai-dev` (and ideally to
> distribute it via managed settings so this whole section becomes one
> click).

**Updating the plugin later:** in the Desktop app, open **+ → Plugins**,
select `folio-po`, and reinstall/update it from there. In the CLI, run
`/plugin marketplace update folio-ai-dev`. (Auto-update is off by default
for third-party marketplaces.)

> The developer-oriented `write-pr-description` skill also lives in the
> same repo but is **not** bundled in the `folio-po` plugin. If you want
> it, see [Appendix A.3](#a3-npx-skills-alternative).

---

## 5. Connect Jira

The plugin already contains the connection settings for the **official
Atlassian MCP server**. You just need to log in once.

**In the Desktop app:** start a new session in your drafts folder and ask:

```
Search Jira for open issues assigned to me and list the top 5.
```

The first time the agent reaches for Jira, Claude Code asks you to
authenticate the **atlassian** server. Approve it — your browser opens the
Atlassian login page. Log in with your normal FOLIO Jira account
(<https://folio-org.atlassian.net>) and approve the access request. Back in
Claude Code, the request completes and your issues appear.

**In the CLI:** run `/mcp`, select **atlassian**, choose **Authenticate**,
and complete the same browser login.

No API tokens, no configuration files — it is the same login you use for
Jira in the browser, and you can revoke it any time from your Atlassian
account settings.

### Sanity check

```
Search Jira for open issues assigned to me and list the top 5.
```

If you see your issues, Jira is connected.

---

## 6. The two PO writing skills

You will use these two skills the most:

### 6.1 `write-user-story`

Produces a **structured user story** with:

- Purpose / Overview (business context, persona, links)
- Functional requirements
- **Acceptance criteria in Given-When-Then format**
- Manual testing guidance

Full reference: [`skills/write-user-story/SKILL.md`](../../skills/write-user-story/SKILL.md)

### 6.2 `write-bug`

Produces a **reproducible FOLIO bug report** with:

- A summary that passes the "scan test" (`[Area] symptom when trigger`)
- Preconditions
- Numbered, atomic steps to reproduce
- Expected vs actual results
- Evidence (logs, stack traces, screenshots, reproducibility rate)
- Filing the bug straight into Jira via the connected MCP server

Full reference: [`skills/write-bug/SKILL.md`](../../skills/write-bug/SKILL.md)

---

## 7. Example prompts

You don't need to memorise the skill names — just describe what you want and
mention the skill. The agent loads it automatically.

### 7.1 `write-user-story` — example prompts

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

### 7.2 `write-bug` — example prompts

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

## 8. End-to-end workflow: from idea to Jira issue

This is the workflow we want every PO to use.

```
┌──────────────┐   ┌────────────┐   ┌───────────┐   ┌──────────────┐   ┌────────────┐
│ 1. Open the  │ → │ 2. Invoke  │ → │ 3. Answer │ → │ 4. Review &  │ → │ 5. File it │
│    drafts    │   │ the skill  │   │ follow-up │   │ iterate on   │   │ via Jira   │
│    folder    │   │ in Plan    │   │ questions │   │ the draft    │   │ MCP        │
└──────────────┘   └────────────┘   └───────────┘   └──────────────┘   └────────────┘
```

### Step 1 — Open Claude Code in your drafts folder

Open the Desktop app and open your `folio-jira-drafts` folder.

### Step 2 — Switch to **Plan mode** before drafting

Switch the session into **Plan mode** — use the mode selector next to the
send button in the Desktop app (in the CLI, press **Shift+Tab**).

In Plan mode the agent may still read files and look things up, but it does
not create or change anything — it only **proposes** a draft in the chat.
This is exactly what you want while writing and refining a ticket.

### Step 3 — Invoke the skill with your prompt

Use one of the prompt templates from [Section 7](#7-example-prompts). For
example:

```
Use the write-user-story skill to draft a FOLIO story for...
```

### Step 4 — Answer the agent's clarifying questions

Both skills are designed to ask you what they need:

- `write-user-story` probes for **persona, value, requirements, and edge
  cases**.
- `write-bug` probes for **target Jira project, environment,
  reproducibility, evidence, and expected vs actual** behaviour.

Answer in natural language — bullet points, fragments, or full sentences all
work.

### Step 5 — Iterate on the draft

The agent posts a draft. Read it against the skill's checklist (both skills
include one near the bottom of `SKILL.md`). Then refine:

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

Repeat freely — the first draft is rarely the final draft.

### Step 6 — File the ticket via the Jira MCP *(main path)*

First, **switch out of Plan mode** (toggle it back with the mode selector)
— creating a Jira issue is a real action, and in Plan mode the agent only
proposes.

Because the official Atlassian MCP server is connected, the agent can search
and create issues for you. After approving the draft, say:

```
Looks good. Search Jira for duplicates first, show me the top matches,
then create the issue in MODORDERS as a Bug with priority P2.
```

The agent will:

1. Run a duplicate search in Jira and show you the matches.
2. Ask you to confirm, then create the issue.
3. Return the issue key and URL.

You will see a confirmation prompt before the issue is created — **read what
it is about to file before approving.**

### Step 7 — Manual fallback: paste into Jira yourself

If the Jira connection is unavailable (or you prefer to file by hand), ask:

```
Convert the final draft to Jira wiki markup. Use {code} blocks for stack
traces and h2./h3. for headings.
```

Then copy the result, open Jira, create the issue in the right project, and
paste it into the **Description** field. (Jira does not render Markdown
natively, which is why the conversion step exists.)

### Step 8 — Save your work *(optional)*

To keep a local archive of every ticket you draft, say (with Plan mode still
off):

```
Save the final Markdown draft to drafts/<JIRA-KEY>.md in this folder.
```

---

## 9. Daily-use cheat sheet

| You want to… | Desktop app | Terminal (CLI) |
|---|---|---|
| Start Claude Code | Open the app and open `folio-jira-drafts` | `cd ~/folio-jira-drafts` then `claude` |
| Switch between **Plan** (propose only) and normal mode | Mode selector next to the send button | **Shift+Tab** |
| Log in to Jira / check the connection | Approve the auth prompt when the agent first uses Jira | `/mcp` |
| See installed plugins and skills | **+ → Plugins** | `/plugin` |
| Update the FOLIO plugin | **+ → Plugins** → select `folio-po` | `/plugin marketplace update folio-ai-dev` |
| Interrupt the agent mid-answer | **Stop** button (or type a correction and send it) | **Esc** |
| Resume an earlier conversation | Pick the session in the sidebar | `/resume` |
| Reference a file in your prompt | Type `@` and start typing the filename | Same |
| Add a screenshot to a prompt | Drag and drop the image into the chat | Same |
| Browse available commands and skills | Type `/` in the prompt box | `/help` |

---

## 10. Good habits and pitfalls

**Do**

- Always invoke the skill by name ("Use the `write-user-story` skill…"). It
  loads the right structure and checklist.
- Use **Plan mode** for drafting. You don't want the agent taking actions
  until you ask.
- Let the skill ask you questions instead of front-loading every detail.
- Iterate. The first draft is rarely the final draft.
- Run a duplicate search before filing a bug.
- Read every Jira confirmation prompt before approving — the agent creates
  real issues in the real tracker.

**Don't**

- Don't paste secrets, real patron data, or production credentials into
  prompts.
- Don't skip the persona / business value in a user story — that's what
  separates a story from a task.
- Don't propose a fix inside a bug ticket. That belongs in the PR or a
  follow-up story.
- Don't approve an MCP action you haven't read — "create issue" means a
  real ticket appears in the project.

---

## 11. Where to get help

- **Claude Code docs:** <https://code.claude.com/docs/en/quickstart>
- **Desktop app guide:** <https://code.claude.com/docs/en/desktop>
- **Connecting tools (MCP):** <https://code.claude.com/docs/en/mcp>
- **Plugins:** <https://code.claude.com/docs/en/discover-plugins>
- **Settings reference** (the keys used in Option A): <https://code.claude.com/docs/en/settings>
- **FOLIO skills repo & issues:** <https://github.com/folio-org/folio-eureka-ai-dev>
- **Skill feedback:** invoke the `skill-feedback` skill at the end of a
  session, or open an issue directly in the repo above.

---

## Appendix A — Terminal (CLI) reference

For POs who prefer the terminal, or when a teammate wants to script things.
Installation is covered in [Option B](#option-b--one-time-terminal-setup);
the CLI is a **native binary — Node.js is not required.**

### A.1 Daily use in the CLI

```bash
cd ~/folio-jira-drafts
claude
```

Everything in this guide works the same: the `/plugin` commands from
[Option B](#option-b--one-time-terminal-setup), the `/mcp` login from
[Section 5](#5-connect-jira), and **Shift+Tab** for Plan mode. Because the
CLI and the Desktop app share configuration, anything you install or
authenticate in one is available in the other.

### A.2 Jira MCP without the plugin *(fallback)*

If you only want the Jira connection (no skills), you can add the Atlassian
server directly:

```bash
claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp --scope user
```

Then run `/mcp` inside Claude Code to authenticate, as in
[Section 5](#5-connect-jira).

### A.3 `npx skills` alternative

If you already use the [skills.sh](https://skills.sh/docs) workflow from the
[README](../../README.md), the Product Owner skill set installs with:

```bash
npx skills add folio-org/folio-eureka-ai-dev --skill write-user-story --skill write-bug --skill write-pr-description --skill skill-feedback
```

This requires Node.js and installs only the skills — you still add the Jira
MCP server separately (A.2). The plugin route in
[Section 4](#4-install-the-folio-po-plugin) does both in one step and is the
recommended path.

Welcome aboard.
