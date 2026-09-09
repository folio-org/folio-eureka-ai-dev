# Context Search

One bounded workflow for finding existing Jira context before the first complete bug draft.

## Search scope

- Start from issue keys or links the user already named, and from distinctive symptom, error, entity, or field names.
- Use the project and component you actually know. Do not invent a Jira project key from a module name.
- When the project is unknown but the component or symptom is distinctive enough, search on that. A full intake interview is not a prerequisite.
- Do not add status, resolution, date, or issue-type filters by default. Those exclude the old fixes, closed duplicates, and related stories you are looking for.
- Run a targeted query first. If nothing convincing comes back, vary the wording to the terms other people would have used, then widen to directly related components or projects when there is a reason to.
- Two or three focused queries and a read of the three to five strongest candidates is usually enough. That is a guide, not a quota, and not a reason to ignore an obvious extra link.
- Account for pagination and for projects you cannot see. Do not describe a search as exhaustive when you reviewed one page of results.

Illustrative JQL — adapt to the project and terms at hand:

```jql
project = MODORDERS AND text ~ "totalExpended" ORDER BY updated DESC
```

```jql
project = MODORDERS AND (text ~ "currency" AND text ~ "expended") ORDER BY updated DESC
```

Use the schema of whatever search tool is configured; the parameter names above are not required. For exact phrases and escaping rules, see the Atlassian text-search documentation: https://support.atlassian.com/jira-software-cloud/docs/search-for-work-items-using-the-text-field/

Do not build JQL by pasting an arbitrary user string straight into a query.

## Candidate inspection

For a strong candidate, read the description, the relevant comments, the status and resolution, the affected and fix versions that are available, and the linked issues, PRs, or docs that are directly relevant.

Follow documentation only to close a specific gap: what the expected behavior is, whether an earlier fix applies here, or what conditions reproduce the defect. Do not turn bug drafting into a full codebase or root-cause audit.

## Classification

- **Likely duplicate** — observable behavior, trigger, and applicable conditions match. A similar title is not enough.
- **Prior fix** — comparable behavior was fixed before; check the scope of that fix and whether it applies here.
- **Possible regression** — there is reason to suspect previously fixed behavior has returned, but the evidence about the fix, the deployment, or comparability is incomplete.
- **Confirmed regression** — a working baseline was verified and the behavior was then reproduced as broken under comparable conditions. This still does not identify the commit that introduced it.
- **Related context** — changes your understanding of scope or expected behavior without being a duplicate.
- **Insufficient evidence** — the relationship could not be established with confidence.

Closed or Done does not necessarily mean Fixed. A fix version is not proof that the fix is deployed in the affected environment. A later version number alone does not prove a regression. A previous fix ticket is not automatically the ticket that introduced the current defect.

Always check the resolution. When a candidate is closed as a duplicate, follow the link and read the canonical issue if you can reach it. Never apply a blanket rule that a closed issue means you should open a new regression.

## Limited or unavailable search

- **No access:** say plainly that the duplicate and history check was not performed.
- **Partial access:** name the specific limitation, and do not draw confident conclusions about a candidate you could not read.
- **Nothing suitable found:** write "No likely match was found in the searches performed", with a short note on what that covered — not "No duplicates exist".
- **User asked to work offline:** respect it, run no external queries, and record that the check was not done.

In all of these cases you can still produce a useful draft. Do not fill the gap with invented comments, fix versions, or relationships.
