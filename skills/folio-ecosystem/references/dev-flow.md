# Development Lifecycle → Skill Orchestration

Canonical descriptions live in each skill's own `SKILL.md` frontmatter — this
file only positions skills in the flow. Enumerate what is actually installed
on disk before relying on this table.

| Stage | Skill | Example trigger phrases |
| --- | --- | --- |
| 1. Story writing | `write-user-story` | "write a user story", "define acceptance criteria" |
| 1. Bug reporting | `write-bug` | "file a defect", "prepare a bug for Jira" |
| 2. DB change during implementation | `liquibase-migration` | "add a column", "write a migration" |
| 3. Unit tests | `unit-testing` | "write unit tests", "review these Java tests" |
| 4. Feature documentation | `document-feature` | "document this feature" |
| 5. PR description | `write-pr-description` | "draft a pull request", "generate PR text" |
| 6. Code review | `code-review` | "review code changes", "analyze a diff" |
| 7. Meta: feedback on a skill | `skill-feedback` | "the liquibase skill missed X — record that" |

## Wrap-up sequence (feature finished on a branch)

```
verify build/tests → document-feature → write-pr-description → code-review
                                                    ↓
                              skill-feedback (if any skill misbehaved)
```

## Proactivity rules

- Reaching a stage IS the trigger — do not wait for the user to name the skill.
  Finished implementing? Run document-feature. Preparing the PR? Run
  write-pr-description, then code-review.
- One stage may recur (e.g. code-review after fixes) — re-run the skill on the
  final state.
- If a stage's skill is not installed, tell the user and propose
  `npx skills update folio-org/folio-eureka-ai-dev` (or `npx skills add …`);
  do not silently skip the stage and do not run the command unprompted.
- After any registry skill produces friction or a wrong result, invoke
  `skill-feedback` while the session context is fresh.

## Notes

- No implementation-coding skill exists in the registry; stage 2 covers only
  the DB-change slice. Implementation itself follows module conventions and
  repo-local instructions.
- `write-bug` (and optionally `write-user-story`) can create tickets via the
  Jira MCP integration when available.
