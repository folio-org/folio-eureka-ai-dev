# folio-eureka-ai-dev

This repo is evolving documentation and prompts (plugins may come later).

## Prompts and docs

- Document Feature skill: `docs/reference-document-feature-skill.md`
- Unit testing guidelines: `docs/testing/unit-testing.md`

### Feature documentation

To generate feature documentation after implementing the feature or updatation feature implementation, use the snippet.

```text
Fetch and follow instructions from https://raw.githubusercontent.com/folio-org/folio-eureka-ai-dev/refs/heads/master/docs/reference-document-feature-skill.md
```

### Unit tests

To follow our unit testing guidelines (structure, naming, Mockito usage, verification patterns), use snippet - just copy and paste before start with tests.

```text
Fetch and follow instructions from https://raw.githubusercontent.com/folio-org/folio-eureka-ai-dev/refs/heads/master/docs/testing/unit-testing.md
```
## 🤖 AI Agent Skills

This repository serves as a skills registry containing guidelines (SKILL.md). These skills can be easily loaded into AI assistants like Cursor, Claude Code, or Copilot using the skills.sh CLI.

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
