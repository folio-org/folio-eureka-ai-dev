---
name: create-release-tasks
description: >-
  Use when someone asks to create the Jira module release ticket (task) for a module version, with or
  without backports, for example "create the release for folio-module-foo v4.0.5", "release ticket for
  folio-keycloak-plugins v26.8.2", "release ticket for MODFOO Trillium CSP#1", or "make release tasks
  for this patch". Works from Jira alone and only creates tickets; it never uses git, Maven, or
  NEWS.md. Not for creating backports (use create-backport-tasks) and not for doing the release itself.
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.1.0"
---

# Create release tasks

Create the release ticket for one module version. There are two kinds:

- **Service patch release:** the version belongs to a flower patch ("Trillium CSP#1"), and backports wait for it. The ticket follows the team's approved template and links the backports.
- **Regular release:** any other module version (for example `folio-keycloak-plugins v26.8.2`). No flower, no `CSP#`, no backports. The ticket copies the shape of the project's earlier release tickets.

Both kinds get the same short release guide in the body. The people who ask (PO, PM, scrum master, developer) know the module and the version or the patch, and may know nothing about git. So everything here comes from Jira and from what they tell you. Never open a repository, run git or Maven, or edit `NEWS.md`.

If the skill was only mentioned, or the user asks what it does, explain it in two or three sentences and ask for the module and the version or patch. Make no Jira call.

## Inputs

- The project or module (`MODFOO` or `folio-module-foo`; the Jira project name equals the module name), and the version (`4.0.5`) or the flower patch ("Trillium CSP#1"). If either is missing, ask for it in one short question and wait.
- Optional: the ticket this release delivers (for example `KEYCLOAK-137`) and one line of context (for example "contains Keycloak 26.8.2"). Do not ask for them; use them when the user gave them.

The release is a **service patch release** when the user named a flower patch or the waiting backports carry a service-patch Release value (step 3). Otherwise it is a **regular release**.

Jira site (`cloudId` for every call): `folio-org.atlassian.net`. Use only read calls (`getJiraIssue`, `searchJiraIssuesUsingJql`, `getJiraIssueTypeMetaWithFields`) until the user confirms the draft.

## Steps

1. **Check the version.** Call `getJiraIssueTypeMetaWithFields` for the project and issue type `10003` with `requiredFieldsOnly: false`. The answer is large; if it is saved to a file, search that file for only `fixVersions` (and `customfield_10046`, the Release field). This skill never creates a Fix Version. A missing version does not stop the work: the version is often created later, by the person who owns the module release. Remember the result as `version exists` or `version missing`.
   - Exists and unreleased: use it as the Fix Version.
   - Missing: carry on and create the ticket without a Fix Version. Tell the user in the draft: "Version X does not exist in project P yet. The ticket is created without a Fix Version; add it after the version is created."
   - Already released: stop and say so.

   If the user gave only a patch, take the version from the backports that wait for it (step 4). Count only unreleased Fix Versions, because a released version cannot be released again. Exactly one: use it, say where it came from, and carry on to the draft; the final confirmation covers it. None or several: ask.

2. **Look for an existing release ticket.** Search the project, closed tickets included, with any issue type. If the version exists: `project = <P> AND summary ~ "Release" AND (fixVersion = "<X.Y.Z>" OR summary ~ "\"<X.Y.Z>\"")`. If it is missing, leave out the `fixVersion` part, because JQL fails on a version that does not exist: `project = <P> AND summary ~ "Release" AND summary ~ "\"<X.Y.Z>\""`. A hit is a release ticket for this version, even when it is Closed, the version is still unreleased, or the summary is spelled differently (`v 4.0.7`, `SP#1`). Report its key, status, and summary, and draft nothing.

3. **Name the patch (service patch release only).** Flower, patch number, and release name come from the Release value, `<Flower> (<release name>) Service Patch #<n>` (for example `Trillium (R1 2026) Service Patch #1` gives `Trillium`, `1`, `R1 2026`), found on the user's patch or on the waiting backports. A version description such as `Trillium R1 2026 SP#1 Release` can confirm it. If you cannot tell, or the value is not a service patch (`Security Patch Release #8.2`), ask. `CSP#<n>` fits service patches only.

4. **Find the backports to include (service patch release only).** Run `project = <P> AND (fixVersion = "<X.Y.Z>" OR customfield_10046 = "<Release value>") AND (statusCategory != Done OR status = "Awaiting release")`. Do not filter by status category alone: `Awaiting release` is in the Done category, and those tickets are exactly the ones to find. If the version is missing, drop the `fixVersion` part and use only the Release value. Leave out release tickets themselves (summary starts with `Release`). Sort the rest:
   - **Propose:** status `Awaiting release`, and Fix Version equal to this version or empty.
   - **Show but do not propose:** other statuses (not ready yet) and tickets with a different Fix Version.

   Show the proposed list (key, summary, status, Fix Version) and let the user confirm or change it. The user may add or drop keys. If nothing waits, say so and ask for keys or whether to create the release without links.

5. **Find the model ticket (regular release only).** Run `project = <P> AND summary ~ "Release" ORDER BY created DESC` (maxResults 5) and take the newest ticket whose summary starts with `Release`. Copy its issue type, priority, and labels into the draft, and say so ("same type, priority and labels as FKP-38"). If there is none, use Task (`10003`), no priority change, and no labels.

6. **Draft and show.**

   | Field | Service patch release | Regular release |
   |---|---|---|
   | Project, type | the project, Task (id `10003`) | the project, the model ticket's type |
   | Summary | `Release <module> v<X.Y.Z> <Flower> CSP#<n> Release (<release name>)` | `Release <module> v<X.Y.Z>` |
   | Fix Version | `<X.Y.Z>` if the version exists; not set if it is missing | same |
   | Release | not set | not set |
   | Priority, labels | labels all included backports share; none if there are no backports | the model ticket's |
   | Links | `has to be done after <BACKPORT-KEY>`, one for each confirmed backport | `Blocks` the delivered ticket, only if the user gave one |

   `<module>` is the Jira project name. Do not set assignee, sprint, or team; the user does that in Jira.

   Body: the guide first, always, exactly as written:

   ```markdown
   * Update NEWS
   * Release version (see [guide](https://dev.folio.org/guidelines/release-procedures/))
   * Check artifacts on [Nexus](https://repository.folio.org/#browse/browse)
   ```

   Then, for a service patch release, a blank line and:

   ```markdown
   This release includes the backports linked with "has to be done after". In NEWS.md, list each change by its source ticket key, not the backport key. After the release, move the linked backports to Awaiting deployment.
   ```

   For a regular release, a blank line and the user's context line, if they gave one (for example `Release folio-keycloak-plugins v26.8.2. The release contains Keycloak 26.8.2.`). If they gave none, add nothing after the guide.

   Put the draft first. Add only what the user must know or decide: the backports left out and why, and open questions. Then ask: "Create this ticket and N links?" Create nothing yet, even if the user said "just create it": the draft is the safety check, because tickets in this shared Jira cannot be deleted.

7. **Create after an explicit yes** to the draft you last showed. If the user changes anything, revise, show again, and ask again. Call `createJiraIssue` (project, the draft's issue type, summary, markdown description, and in `additional_fields` the labels and priority, plus `fixVersions: [{"name": "<X.Y.Z>"}]` only when the version exists; never send `fixVersions` for a missing version). Then create the links:
   - Service patch release: for each backport, `createIssueLink` with type `Gantt End to Start`, `inwardIssue` the backport and `outwardIssue` the release (reads "release has to be done after backport").
   - Regular release: if the user named a delivered ticket, `createIssueLink` with type `Blocks`, `inwardIssue` the delivered ticket and `outwardIssue` the release (the release shows "blocks <ticket>").

   Report the new keys and stop. If the version was missing, remind the user that the Fix Version still has to be set on the release ticket after the version is created. Do not change statuses, add comments, or do the release work.
