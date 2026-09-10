# Context Search

Finding existing Jira context before the first complete bug draft.

## Searching

Start from any keys or links the user already named, and from distinctive symptom,
error, entity, or field names. Use the project and component you actually know — do not
invent a Jira project key from a module name. If the project is unknown but the symptom
is distinctive, search on that; a full intake interview is not a prerequisite.

Do not add status, resolution, date, or issue-type filters by default: they exclude
exactly the old fixes and closed duplicates you are looking for. Run a targeted query
first; if nothing convincing comes back, vary the wording before concluding anything.
A few focused queries and a read of the strongest candidates is usually enough. Account
for pagination and for projects you cannot see — do not call a search exhaustive when
you reviewed one page.

Adapt queries to the configured tool's schema; do not build one by pasting an arbitrary
user string into it. For exact phrases and escaping rules, see
https://support.atlassian.com/jira-software-cloud/docs/search-for-work-items-using-the-text-field/

For a strong candidate, read the description, the relevant comments, the status and
resolution, the available versions, and the directly relevant links — only far enough to
close a specific gap. Do not turn bug drafting into a root-cause audit.

## Classifying what you find

- **Likely duplicate** — observable behavior, trigger, and applicable conditions match.
  A similar title is not enough.
- **Prior fix** — comparable behavior was fixed before; check whether that fix's scope
  applies here.
- **Possible regression** — reason to suspect previously fixed behavior has returned,
  but the evidence about the fix, the deployment, or comparability is incomplete.
- **Confirmed regression** — a working baseline was verified and the behavior was then
  reproduced as broken under comparable conditions. This still does not identify the
  commit that introduced it.
- **Related context** — changes your understanding of scope or expected behavior
  without being a duplicate.
- **Insufficient evidence** — the relationship could not be established with confidence.

Closed or Done does not necessarily mean Fixed. A fix version is not proof that the fix
is deployed in the affected environment, a later version number alone does not prove a
regression, and a previous fix ticket is not automatically the ticket that introduced
the current defect. Always check the resolution; when a candidate is closed as a
duplicate, follow the link and read the canonical issue if you can reach it.

## When the search is limited

State the actual limitation instead of a conclusion you did not earn:

- **No access** — say plainly that the duplicate and history check was not performed.
- **Partial access** — name the specific limitation, and draw no confident conclusion
  about a candidate you could not read.
- **Nothing suitable found** — "No likely match was found in the searches performed",
  with a short note on what that covered; not "No duplicates exist".
- **User asked to work offline** — respect it, run no external queries, and record that
  the check was not done.

A useful draft is still possible in every one of these cases. Do not fill the gap with
invented comments, fix versions, or relationships.
