---
name: create-backport-tasks
description: >-
  Use when someone asks to create Jira backport tasks (tickets) for a source ticket and one or more
  flower patches, for example "backport MODFOO-100 to Trillium CSP#1 and Sunflower CSP#12", "create
  backport tickets for MODFOO-100", or "plan a patch for MODFOO-100". Works from Jira alone and only
  creates tickets; it never uses git, branches, commits, or PRs. Not for doing the backport itself
  (cherry-pick) and not for release tickets (use create-release-tasks).
license: Apache-2.0
metadata:
  author: folio-org
  version: "1.0.0"
---

# Create backport tasks

Create one Jira Task per pair of source ticket and flower patch, from the team's approved template. The people who ask (PO, PM, scrum master, developer) know the source ticket and the patch, and may know nothing about git. So everything here comes from Jira and from what they tell you. Never open a repository, run git, or ask for a branch, a commit, or a PR.

If the skill was only mentioned, or the user asks what it does, explain it in two or three sentences and ask for the source ticket and the patch. Make no Jira call.

## Inputs

- The source ticket key and one or more target patches, each a flower plus a patch number: "Trillium CSP#1", "Sunflower CSP#12". If either is missing, ask for it in one short question and wait.
- Optional facts from the user that can become a `Notes:` line (see Draft).

Jira site (`cloudId` for every call): `folio-org.atlassian.net`. Use only read calls (`getJiraIssue`, `searchJiraIssuesUsingJql`, `getJiraIssueTypeMetaWithFields`) until the user confirms the draft.

## Steps

1. **Read the source ticket.** Take its summary, project, and labels. The backport goes into the same project. Stop if the ticket does not exist.

2. **Match each patch to a Release value.** Call `getJiraIssueTypeMetaWithFields` for the project and issue type `10003` with `requiredFieldsOnly: false`. The answer is large; if it is saved to a file, search that file for only `customfield_10046` (Release) and `fixVersions`. Pick the Release value that reads `<Flower> (<release name>) Service Patch #<n>`. The allowed values change with every patch, so never write one from memory. If no value matches, or the only candidate is not a service patch (for example `Security Patch Release #8.2`), skip that patch, show the current values, and ask. `CSP#<n>` fits service patches only.

3. **Look for an existing backport first.** Run `issue in linkedIssues(<SOURCE>)` and read summary, status, `fixVersions`, and `customfield_10046`. A linked ticket is the backport for a patch when its Release value is that patch, or its summary names the flower and the patch (`SP#1` and `CSP#1` both count). Older backports use a `clones` link, a different summary, and may even omit the source key. Report each one found (key, status, summary) and draft nothing for that patch, whatever its status. Closed work still counts.

4. **Choose the Fix Version.** Leave it empty by default. Propose a version only when it is in the project's version list from step 2, is unreleased, and either its description names this flower and patch (for example `Sunflower R1 2025 SP#11 Release`) or an open release ticket for this patch carries it (step 5). Show the proposal and why, and set it only if the user agrees. Never create a version: many people cannot, and the template allows adding it later. If the user names a version, check that it exists and is unreleased.

5. **Look for an open release ticket.** Run `project = <P> AND issuetype = Task AND summary ~ "Release" AND statusCategory != Done ORDER BY created DESC`. Keep tickets whose summary names this flower and patch (`SP#n` and `CSP#n` both count) or whose Fix Version equals the backport's. One match: add the link. Several: ask which. None: no link; the release skill links it later.

6. **Draft every ticket and show all drafts.** Follow the template exactly:

   | Field | Value |
   |---|---|
   | Project, type | the source's project, Task (id `10003`), even when the source is a Bug or Story |
   | Summary | `[Backport <Flower> CSP#<n>] <SOURCE-KEY>: <original summary>`, the source summary unchanged |
   | Release | the value from step 2 |
   | Fix Version | from step 4, or empty |
   | Labels | copied from the source ticket |
   | Links | `relates to <SOURCE-KEY>`; `has to be done before <RELEASE-KEY>` only when step 5 found one |

   Body:

   ```markdown
   Source ticket: [<SOURCE-KEY>](https://folio-org.atlassian.net/browse/<SOURCE-KEY>)

   This task backports the change from the source ticket to <Flower> CSP#<n>.
   ```

   Add `Notes: <one sentence>` under it only when the source ticket alone is not enough, and only from a fact the user gave or the source ticket shows: the Jira project covers several repositories, the commits carry a different key than the source (for example `Notes: the commits for this change are under EUREKA-899.`), or only part of the change goes to the release branch. Without such a fact, write no Notes line. Do not guess and do not ask for one.

   Put the drafts first. After them, add only what the user must know or decide: skipped duplicates, a proposed Fix Version, open questions. Then ask for confirmation ("Create these tickets?"). Create nothing yet, even if the user said "just create them" or "no need to show me": the draft is the safety check, because tickets in this shared Jira cannot be deleted.

7. **Create after an explicit yes** to the draft you last showed. If the user changes anything, revise, show again, and ask again. Then for each draft call `createJiraIssue` (project, `issueTypeName: Task`, summary, markdown description, and in `additional_fields` the labels, `customfield_10046: {"value": "<Release value>"}`, and `fixVersions: [{"name": "<version>"}]` only when set). Then link with `createIssueLink`: type `Relates` between the backport and the source, and, only if a release ticket was found, type `Gantt End to Start` with `inwardIssue` the backport and `outwardIssue` the release (reads "backport has to be done before release"). Report the new keys and stop. Do not change statuses, add comments, or do the backport work.
