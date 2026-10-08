# PR templates and confirmation

## Default template

Use this body when the repository has no PR template. Fill the placeholders from the changes;
omit the Jira line without a known key and the implementation block for a small change.

```markdown
### Purpose
<1–2 sentences: the problem and resulting behavior>
Jira: [<KEY>](https://folio-org.atlassian.net/browse/<KEY>)

### Approach
<2–3 sentences explaining the change>

**Implementation details:**
- <One concise bullet per substantive part>
```

There is no default checklist. Show the title separately above the body; pass it as `--title`
when creating the PR.

## Repository template

Use the repository template's own headings and their order, even when they differ from Purpose
and Approach. Replace prose instructions with content. Preserve checklist wording, indentation,
notes and sub-items, leaving every box unticked.

## Commit task files

When opening a PR with uncommitted task files, list the files and ask whether to commit them.
Stop before modifying Git. After approval, use only those paths for staging and committing:

```bash
git add -- <approved paths>
git commit --only -m "<task summary>" -- <approved paths>
```

This includes intended new files and keeps unrelated staged changes out of the commit.
An answer declining the commit stops creation; a request only for text does not commit anything.

## Confirm publication

Show the actual title and filled body, then one question:

> Create the PR? This will push the current branch and open the PR.

If the current commits are already on the remote, say that no push is needed.
After approval, push only if necessary and create the PR. Do not ask a second push question.
