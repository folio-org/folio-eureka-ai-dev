# Shape of a finished description

Skeletons, not content. Everything in `<angle brackets>` is filled from the branch and the target
repository. Nothing here is text to copy into a PR.

The two differ only in whether the repository has a PR template. Which one applies is decided in
Step 3 by looking for the file, never by which of these reads better.

<example name="no template file">

```markdown
## <KEY: short description, or a plain semantic title when there is no key>

### Purpose
<one or two sentences: why this change is needed>
Jira: [<KEY>](https://folio-org.atlassian.net/browse/<KEY>)     <- omit the line when there is no key

### Approach
<2–3 sentences a reviewer can follow without opening the diff>

**Implementation details:**                                     <- omit this whole block for a
                                                                   small or single-purpose change
- <Past-tense verb> <what changed, one logical change>, <why, or the consequence>.
- <one bullet per logical change; no tests, no documentation>
```

No template file, so the body ends here. There is no checklist.

</example>

<example name="template present">

```markdown
## <KEY: short description>

<the template's own sections, in the template's own order, with its headings kept exactly as
written — including any bold or punctuation inside them — and each instruction line replaced by
real content:>

### <Purpose, as the template spells it>
<why this change is needed>
Jira: [<KEY>](https://folio-org.atlassian.net/browse/<KEY>)

### <Approach, as the template spells it>
<summary, then Implementation details only if the change needs them>

---

### <the template's checklist heading>

<the checklist reproduced from the template file: every item, same wording, same order, same
indentation, same blockquote notes and sub-items — and every box left unticked>
```

</example>

## Create mode

Both skeletons are draft mode, where the title is printed as a `##` heading above the sections.

In create mode the title is the `--title` value, so the body file starts at the first section and
never repeats it.
