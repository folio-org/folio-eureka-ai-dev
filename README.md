# folio-eureka-ai-dev

This repository contains installable AI agent skills for FOLIO development workflows, plus supporting prompts and documentation.

## 🤖 AI Agent Skills

This repository serves as a skills registry containing guidelines (`SKILL.md`). These skills can be loaded into AI assistants like Cursor, Claude Code, or Copilot using the skills.sh CLI.

### Available skills

- `code-review` - Reviews branch diffs and produces a structured code quality report.
- `document-feature` - Documents implemented behavior by analyzing code changes and writing feature docs.
- `liquibase-migration` - Guides FOLIO Liquibase migration authoring, structure, naming, and database conventions.
- `skill-feedback` - Captures user-validated feedback after a skill session and prepares a GitHub-ready report.
- `unit-testing` - Applies Java unit testing guidance for JUnit 5, Mockito, strict stubbing, and clear test structure.
- `write-bug` - Drafts reproducible FOLIO bug reports with steps, expected and actual results, and supporting evidence.
- `write-pr-description` - Drafts PR descriptions following team conventions for purpose, approach, and checklist.
- `write-user-story` - Drafts user stories with scope, requirements, acceptance criteria, and manual testing guidance.

### Installing skills

To install these skills in your project, run:

```bash
npx skills add folio-org/folio-eureka-ai-dev
```

Running this command in the terminal of a target project will automatically download our AI context. This ensures that your AI assistant is aware of our specific architectural and testing standards when generating or refactoring code.

For more information about skills.sh, see the [official documentation](https://skills.sh/docs).

### Updating skills

To update to the latest version of our team's AI guidelines, run:

```bash
npx skills update folio-org/folio-eureka-ai-dev
```

### GitHub issue reporter

Use the `skill-feedback` skill when you finish working with another skill and want to report what worked well, what was confusing, or what should be improved. It is useful for skill-related bugs, missing guidance, unclear instructions, improvement ideas, requests for additional examples, and proposals for new skills.

Ask your AI agent to run the skill feedback workflow after a skill session. The agent should review the session context, prepare a GitHub-ready issue draft, show the full draft for your approval, and then create an issue in this repository if GitHub access is available. If the agent cannot create the issue directly, copy the approved draft and create the GitHub issue manually.

The feedback loop should stay lightweight: it should be easy to create GitHub issues for bug fixes, requests, ideas, and new skill proposals, and easy to use GitHub Actions later for labeling, triage, or follow-up automation. We will continue improving these skills together with the community based on real usage and feedback.

## Prompts and docs

- Document Feature skill: `docs/reference-document-feature-skill.md`
- Unit testing guidelines: `docs/testing/unit-testing.md`
- PR description guide: `docs/pr/pr-description.md`

### Feature documentation

To generate feature documentation after implementing or updating a feature, use this snippet.

```text
Fetch and follow instructions from https://raw.githubusercontent.com/folio-org/folio-eureka-ai-dev/refs/heads/master/docs/reference-document-feature-skill.md
```

### Unit tests

To follow our unit testing guidelines (structure, naming, Mockito usage, verification patterns), use this snippet before starting tests.

```text
Fetch and follow instructions from https://raw.githubusercontent.com/folio-org/folio-eureka-ai-dev/refs/heads/master/docs/testing/unit-testing.md
```

### PR description

To write a consistent, reviewable pull request description following our conventions, use the snippet.

```text
Fetch and follow instructions from https://raw.githubusercontent.com/folio-org/folio-eureka-ai-dev/refs/heads/master/docs/pr/pr-description.md
```
