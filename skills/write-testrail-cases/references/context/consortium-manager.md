# FOLIO Consortium Manager App - Business Logic Context

> Generated/refreshed by the build-app-context workflow on 2026-06-18.
> Sources:
> - TestRail section subtree under group_id=23689 scoped to Consortium Manager roots (sections: 80, cases: 380 total).
> - Focus releases requested: Umbrellaleaf, Trillium, Sunflower, Ramsons, 2023 Poppy (312 matching cases; no Umbrellaleaf-tagged cases found in this subtree).
> - GitHub: folio-org/ui-consortia-settings, folio-org/mod-consortia (7 files read).
> - Jira: UICONSET, MODCON, and FOLIO component "Consortium manager" (0 Done stories, 0 Done bugs returned in this run).
> Strings marked [confirmed] appear in both GitHub and TestRail signals.
> Strings marked [from source] come from GitHub source only.
> Strings marked [from cases] come from TestRail case corpus.

---

## What is Consortium Manager

Consortium Manager is the ECS administration surface used to coordinate centrally-managed and member-scoped settings across a multi-tenant consortium. It lets users in the central tenant pick member libraries, view shared settings, and create local or shared terms for supported settings domains (Inventory, Users, Circulation, Authorization roles/policies, and log visibility areas).

The app is ECS-specific and relies on tenant affiliation context. In practical test design, behavior is strongly permission-scoped per tenant and per setting domain.

---

## Key Terms

| Term | Definition |
|---|---|
| ECS | Enhanced Consortial Support multi-tenant architecture in FOLIO. |
| Central tenant | Consortium administrative tenant where shared actions are initiated. |
| Member tenant | Affiliated library tenant receiving shared settings and/or local updates. |
| Shared setting | Setting saved with Share enabled and confirmed for ALL selected members. |
| Local setting | Setting created for selected members only (without Share-to-all). |
| Select members | Modal workflow used to scope target member libraries for local operations. |
| Affiliation | Tenant context tied to the acting user; impacts accessible settings and logs. |

---

## Record Hierarchy / Architecture

Consortium Manager
- Management pane
  - Users settings
    - Departments
    - Patron groups
  - Circulation settings
    - Request cancellation reasons
  - Inventory settings
    - Formats, call number types, material types, etc.
  - Authorization
    - Authorization roles
    - Authorization policies
  - Logs and reports
    - Data import logs by member
    - Data export logs by member
- Select members modal
  - Search and filter pane
  - Members pane
  - Total selected counter

---

## Lifecycle / Workflow

Main create/update flow used across most managed setting types:

1. Open Consortium Manager.
2. Select target members in Select members.
3. Choose settings area from Management pane.
4. Click New or open existing record.
5. Save with either shared or local intent.
6. Confirm in modal:
   - shared path: Confirm share to all
   - local path: Confirm member libraries
7. Verify list update and resulting toast.

Status values are not consistently explicit in this section subtree (log tables expose a Status column but canonical status vocabularies are not fully enumerated in extracted cases).

---

## Main Sections / UI Structure

### Panes
- Management [confirmed]
- Members [confirmed]
- Inventory [from cases]
- Search and filter [from cases]
- Authorization roles [from cases]
- Holdings sources [from cases]
- Subject types [from cases]
- Subject sources [from cases]

### Accordions
- Capability sets [from cases]
- Capabilities [from cases]
- Assigned users [from cases]
- User roles [from cases]
- User permissions [from cases]

### Key Navigation Paths
- Apps > Consortium manager > Management > Data import
- Apps > Consortium manager > Management > Data export
- Apps > Consortium manager > Management > Inventory > Subject types
- Settings > Authorization roles
- Settings > Authorization policies

---

## Exact UI Texts

> Use these verbatim in expected results. Never paraphrase.
> ✅ Corrected/confirmed 2026-07-21 against `folio-org/ui-consortia-settings/translations/ui-consortia-settings/en_US.json`. The controlled-vocabulary CRUD toasts follow a single templated pattern (below) — earlier paraphrases like "was successfully created for All libraries." are replaced with the exact template. `<b>…</b>` = bold; `{term}`, `{members}`, `{count}` interpolate.

### Toast Messages

**Controlled-vocabulary CRUD (shared settings) — one template for every vocab type** [confirmed]:
- Created: `<b>{term}</b> was successfully <b>created</b> for <b>{members}</b> {count, select, 1 {library} other {libraries}}.`
- Updated: `<b>{term}</b> was successfully <b>updated</b> for <b>{members}</b> {count} {library/libraries}.`
- Deleted: `<b>{term}</b> was successfully <b>deleted</b> for <b>{members}</b> {count} {library/libraries}.`
- Partial failure (create/update/delete): `<b>{term}</b> was <b>not created</b> for members: <b>{members}</b>.` (delete variant: `... could not be deleted from members: <b>{members}</b>, so the source has been changed to local.`)

| Event | Toast text | Source |
|---|---|---|
| Permission boundary | `You do not have permissions at one or more members: <b>{members}</b>` | [confirmed] |
| Role duplicated | `The role <b>{name}</b> has been successfully <b>duplicated</b>` | [confirmed] |
| Role duplicate error | `There was an error while duplicating the role <b>{name}</b>` | [confirmed] |
| Permission set saved | `The permission set <strong>{permissionName}</strong> was successfully <strong>saved</strong>.` | [confirmed] |
| Permission set deleted | `The permission set <strong>{permissionName}</strong> was successfully <strong>deleted</strong>.` | [confirmed] |
| Member (address) deleted | `The member <b>{term}</b> was successfully <b>deleted</b>` | [confirmed] |
| Central ordering updated | `Central ordering setting was successfully updated` | [confirmed] |
| Role created | `Role has been created successfully` | [from cases] |
| Role create name collision (Central, unique-name check within same tenant) | `Role could not be created: Failed to create keycloack role` (sic — literal backend typo "keycloack") | [from cases (C523671)] |
| Role updated | `Role has been updated successfully` | [from cases] |
| Role deleted | `Role has been deleted successfully` | [from cases] |
| Role duplicated (Eureka authorization role, exact case text) | `The role has been successfully duplicated` | [from cases (C986307, C663331)] — note this differs slightly in word order from the generic "Role duplicated" row above; both forms appear across cases, treat as equivalent |
| Role shared successfully | `Role has been shared successfully` | [from cases] |
| Role share blocked by name collision (one member) | `Role could not be shared: Name is already in use at one or more member libraries - <b>{member name}</b>.` | [from cases (C692096)] |
| Role share blocked by name collision (multiple members) | `Role could not be shared: Name is already in use at one or more member libraries - <b>{member1}</b>, <b>{member2}</b>.` | [from cases (C1030054)] — lists every conflicting member, comma-separated |
| Role rename (edit) blocked by name collision with member role | `Role could not be updated: Name is already in use at one or more member libraries - <b>{member name}</b>.` | [from cases (C1263896)] |
| Authorization policy saved (create) | `Authorization policy has been saved` | [from cases (C543762)] — note: simpler wording than the templated role/vocab toasts; policies do not follow the `<b>{term}</b> was successfully created` pattern |

### Modal / Dialog Messages (confirmed)

| Modal | Heading / message |
|---|---|
| Select members | `Select members`; results `{amount} members found`; `Total selected: {amount}`; warning `Settings for the following selected members can be modified at the same time.` (header when selected: `{amount} members selected`) |
| Confirm share to all | `Confirm share to all` / `Are you sure you want to share {term} with <b>ALL</b> members?` |
| Confirm member libraries | `Confirm member libraries` / `<b>{term}</b> will be saved for the member libraries:` |
| Switch active affiliation | user dropdown `Switch active affiliation`; modal `Select affiliation`; select label `Consortium members`; primary tenant suffix `(Primary)` |
| Central ordering activate | `Are you sure you would like to activate this functionality?` (alert: `In this version of FOLIO, once activated this setting cannot be disabled.`) |

### Modal / Dialog Titles

| Modal | Trigger | Source |
|---|---|---|
| Select members | Click Select members on main page | [confirmed] |
| Confirm member libraries | Save local setting | [confirmed] |
| Confirm share to all | Save shared setting | [confirmed] |
| Delete holdings source | Delete Holdings Source term | [from cases (15.50)] |
| Delete holdings type | Delete Holdings Type term | [from cases (13.05)] |
| Delete resource type | Delete Resource Type term | [from cases (11.70)] |
| Delete role | Delete authorization role | [from cases (6.50)] |
| Duplicate authorization role? | Click "Duplicate" in Actions menu on a role detail pane | [from cases (C552361, C986307: "Duplicate role?" short form also seen)] |

### Button Labels (key actions)

Select members, Save and close, Save, New, Edit, Delete, Confirm, Cancel, Keep editing, Actions.

### Error / Warning Messages

| Condition | Message text | Source |
|---|---|---|
| Missing cross-tenant permission | You do not have permissions at one or more members: <b>{members}</b> | [from source] |
| Data loading failure | Could not load jobs data. | [from source] |
| Permission failure in logs/policies | User does not have required permissions. | [from source] |
| Role create denied | Role could not be created: Access Denied | [from cases] |

---

## Status Values

### Log table status field (Data import / Data export)
Not consistently enumerated in extracted focus-release case text; verify concrete status vocabulary in environment before asserting exact values.

---

## Capability Sets (Eureka)

> Extracted from TestRail preconditions and normalized for repeated patterns.

| Action | Capability Set |
|---|---|
| View Consortium Manager | Data - UI-Consortia-Settings Consortium-Manager - View |
| Edit Consortium Manager settings | Data - UI-Consortia-Settings Consortium-Manager - Edit |
| Execute share to all | Procedural - UI-Consortia-Settings Consortium-Manager Share - Execute |
| View data import logs | Data - UI-Data-Import - view |
| View or edit data export context | Data - UI-Data-Export - view, Data - UI-Data-Export - edit |
| Manage authorization roles | Settings - UI-Authorization-Roles Settings - View/Edit/Delete/Create |
| Manage role assignments | Settings - UI-Authorization-Roles Users Settings - Manage |
| View authorization policies | Settings - UI-Authorization-Policies Settings Admin - View |
| Manage inventory shared settings | Settings - UI-Inventory Settings <Setting-Type> - View (per setting type and tenant) |
| Manage users settings terms | Settings - UI-Users Settings Departments - manage, Settings - UI-Users Settings Usergroups - manage |

Warning: Legacy permission-style strings are still present in several older cases and mixed-format preconditions. Validate final Eureka naming in environment where exact capability IDs are required.

---

## Common Verification Patterns

> Copy these into expected results where applicable.

### Data import logs by selected member

```
Action:   Do not change selection in Member dropdown and verify table.
Expected: Data import logs table displays jobs only for selected tenant; count text matches; default sort is by Ended running descending with v icon.
```

### Data import member switch behavior

```
Action:   Select a different tenant in Member dropdown.
Expected: Table refreshes to selected tenant data; logs count updates; active sort indicator remains on selected column.
```

### Data export logs by selected member

```
Action:   Keep default member selection in Data export pane.
Expected: Data export jobs are scoped to selected tenant and sorted by Ended running descending by default.
```

### Data export member switch sorting

```
Action:   Change member selection after applying sort on a data column.
Expected: Selected tenant value persists; table updates for tenant; sort order/indicator remains applied.
```

---

## Authorization Roles / Policies — Eureka Deep-Dive (Consortium Manager)

> The "Consortium manager (Eureka)" TestRail subtree (section 40125) covers Authorization roles/policies management, which is largely distinct from the vocabulary-sharing (Departments, Loan types, etc.) patterns documented above. Extracted from a 15-case sample (C523593, C523671, C552361, C552447, C986307, C692096, C1030054, C1263896, C543745, C543755, C663331, C552363, C566123, C552368, C1045994, C543762).

### Create Role / Create Policy

- Roles are created per-tenant: the "Member" dropdown on the Authorization roles pane must be set to the target tenant BEFORE the "New" action creates a role scoped to that tenant. A role created while "Member" = Central is invisible when the dropdown is switched to a Member tenant, and vice versa — verified both via Consortium Manager's own list and independently via Settings > Authorization roles in each tenant.
- Creating a role in a tenant with a name that collides with an EXISTING role name in that SAME tenant fails with the literal (backend-passthrough, misspelled) toast `Role could not be created: Failed to create keycloack role` — the "Create role" form stays open. [C523671]
- Policies follow the same tenant-scoping pattern, but the "New" button for Authorization policies is ONLY shown when "Member" dropdown = Central tenant — Member tenants get a read-only (no New button) policies list in Consortium Manager. [C543762]
- Assigning users to a newly created role uses an "Assign/Unassign" button opening a "Select User" modal; checking its "Active" checkbox filters the user list to ONLY users of the currently selected tenant (cross-tenant users are excluded even if affiliated). [C523593]
- Editing a role's Description and clicking "Save & close" produces toast `Role has been updated successfully`.

### Duplicate Role

- Reachable via Actions > Duplicate on any role detail pane (own or shared) → confirmation modal ("Duplicate authorization role?" / "Duplicate role?") with Duplicate/Cancel buttons.
- The duplicate ALWAYS: (a) keeps the same capabilities/capability sets as the source role, (b) has a BLANK "Assigned users" accordion (users are never carried over), (c) is created as a **local, non-shared** role in the tenant it was duplicated from — even when duplicating a role that itself was shared/centrally-managed. [C552361, C552447, C986307]
- For a role that IS currently shared: viewed from a Member tenant, its Actions menu offers ONLY "Duplicate" — "Edit" and "Delete" are absent (members cannot modify a centrally-shared role directly, only duplicate it into their own local copy). Viewed from Central, the same shared role's Actions menu offers Edit + Delete but not "Share to all" again (already shared). [C552447, C543755]
- The duplicate itself, once created, has full Edit/Duplicate/Delete available (it's a plain local role), and can be deleted with the standard `Role has been deleted successfully` toast. [C552447, C663331, C986307]
- Duplicating and then deleting is a common test pattern for cleanup verification across Central + every Member tenant in one case.

### Delete Role

- Actions > Delete → "Delete role" confirmation modal (Cancel/Delete). Cancel aborts with no changes.
- Confirmed delete: toast `Role has been deleted successfully`; role disappears from the Consortium Manager list AND from Settings > Authorization roles in that tenant.
- If the deleted role had users assigned, those users' own "User roles" accordion (in the Users app, User details pane) becomes empty as a direct side effect — this cross-app check is a standard verification step in delete cases. [C543745]
- Deleting a SHARED role from Central removes it consortium-wide; Member-tenant views of the (now-deleted) shared role no longer show it as a Duplicate-only Actions option since it no longer exists at all.

### Share to All — Name-Collision Blocking (critical, case-insensitive)

- A role CANNOT be shared to all members if a role with the exact same name — compared **case-insensitively** — already exists in ANY member tenant. The share is blocked per-conflicting-member, not globally: if only one member conflicts, only that member is named in the error; if two conflict, both are named.
  - One conflict: `Role could not be shared: Name is already in use at one or more member libraries - <b>{member}</b>.`
  - Two conflicts: `Role could not be shared: Name is already in use at one or more member libraries - <b>{member1}</b>, <b>{member2}</b>.`
  - [C692096, C1030054]
- The fix pattern tested: rename the Central role to something unique across all tenants (toast `Role has been updated successfully`), THEN retry Share to all → succeeds with `Role has been shared successfully` and "Centrally managed" flips from "No" to "Yes".
- The SAME case-insensitive collision check applies when EDITING (renaming) an already-shared role to match a name that exists in a member tenant: `Role could not be updated: Name is already in use at one or more member libraries - <b>{member}</b>.` — the edit is rejected and the role keeps its old name. [C1263896]
- Role names containing CQL reserved words/operators/quotes/backslashes (e.g. `and Test`, `Test AND staff`, `"test and staff"`, `Test-and_staff`, `Name==test`) are valid and share successfully without any escaping problems — a dedicated regression case exists purely to confirm CQL-lookalike names don't break the share/search flow. [C1045994]

### Compare Roles (capability diff tool) — undocumented feature, first citation

- Reached via Actions > "Compare roles" from any Authorization role detail pane. Opens a full-page "Compare roles" view with two independent side-by-side panes (left/right).
- Each pane has its own: Member dropdown, Authorization roles dropdown (disabled until a Member is chosen), Capabilities accordion, Capability sets accordion (both collapsed by default).
- Selecting a Member then a Role in a pane populates that pane's accordions; switching a pane's Member dropdown clears that pane's Role selection and both accordions.
- Capabilities/capability sets held by BOTH selected roles are visually highlighted (yellow) in each pane, letting a tester diff two roles' capability grants across tenants at a glance — including comparing the same role name across three different tenants (Central, Member 1, Member 2) one pair at a time. [C552363]
- Empty states use distinct placeholder text: "No capabilities found" (accordion has no data at all) vs "No capability sets found" (role has capabilities but zero capability-set groupings).

### Users Settings — "Permission sets" heading intentionally absent

- Consortium Manager > Settings > Users shows exactly two settings: "Patron groups" and "Departments". "Permission sets" is deliberately NOT present in the Eureka-based Consortium Manager Users pane (legacy permission sets have no Eureka/role-based equivalent surfaced here). [C566123]

### Management Pane Collapse

- The left "Management" pane can be collapsed via a "<" control (collapses to an icon-only rail with a ">" reopen button); before any setting is chosen, the pane shows placeholder text "Choose settings". Collapsing/expanding does not reset the "Select members" selection state. [C552368]

---

## ECS / Multi-Tenant Notes

- Cases are heavily ECS-specific (custom_ecs_enabled=true is common in this subtree).
- Central tenant context is required for most share-to-all flows and cross-tenant log visibility checks.
- Select members controls target scope for local setting management and is repeatedly asserted in expected results.
- Negative cases repeatedly verify tenant-scoped permission boundaries where a user can see one member but not another.

---

## Key Business Rules for Test Cases

1. Consortium Manager behavior is tenant-scoped and requires ECS-enabled affiliation context. (cases + github)
2. Shared vs local persistence is chosen at save time and confirmed by different modals (Confirm share to all vs Confirm member libraries). (cases + github)
3. A user can access logs/settings only for members where required capability sets are present; missing capabilities produce explicit permission errors. (cases + github)
4. Select members determines operation scope and displayed member count; Save and close must persist selection state. (cases)
5. Data import log view validates tenant-specific rows, row counts, and sortable table columns under selected member. (cases)
6. Data export log view follows the same tenant-scoped pattern as import logs. (cases)
7. Shared setting create/edit/delete flows for many Inventory vocabularies follow one reusable pattern with setting-type substitution. (cases)
8. Local setting management requires both central access and member-level setting capabilities; this is enforced in negative tests per setting type. (cases)
9. Authorization roles/policies flows are represented as Consortium Manager scenarios in Eureka context, including role duplication and role capability boundaries. (cases)
10. Deletion flows use explicit Delete <type> modal variants and must verify successful deletion toast or usage-blocking message. (cases + github)
11. Error-state UI for insufficient permissions is part of expected behavior and should be asserted explicitly, not treated as setup failure. (cases + github)
12. Release signal in this subtree is concentrated in Poppy, Trillium, Sunflower, and Ramsons; Umbrellaleaf-specific updates are not yet represented. (cases)
13. Roles/policies are strictly per-tenant scoped for both creation and same-tenant name-uniqueness checks; a role created under one "Member" dropdown selection is invisible under any other, confirmed independently via Settings > Authorization roles. (cases)
14. Duplicating a role NEVER carries over assigned users and ALWAYS produces a local (non-shared) copy, even when the source role was centrally shared. (cases)
15. A shared role can only be Edited/Deleted from the Central tenant; Member-tenant views of a shared role expose only "Duplicate" in Actions. (cases)
16. Share-to-all is blocked, case-insensitively, by ANY member-tenant role name collision; the error names every conflicting member explicitly, and the same case-insensitive check blocks renaming an already-shared role into collision. (cases)
17. Role names containing CQL reserved words/operators are valid and shareable — name validation does not reject CQL-lookalike strings. (cases)
18. "Compare roles" is a dedicated capability-diff tool (Actions menu on a role) with two independent Member+Role selector panes and yellow-highlighted shared capabilities/capability sets. (cases)
19. Authorization policies are Central-tenant-create-only in Consortium Manager (no "New" for Members) and use their own simpler save toast, distinct from the templated vocab/role toasts, with no visible Share-to-all mechanism in the sampled cases. (cases)

---

## Authoring style (measured 2026-07-23)

Consortium Manager: **`Func` 100%**, median **~18 steps** (the largest cases in the project — ~two-thirds are ≥15 steps), `User Journey` ~0%. These are big end-to-end ECS setup/administration journeys — share a setting to all members, confirm member-library selection, manage affiliations, authorization roles/policies, and verify propagation across Central + multiple member tenants. Use `Functional`. Preconditions establish the consortium (Central + ≥2 members, user affiliations, the setting/role under test); steps walk the full share/confirm/verify-per-tenant flow with a tenant-switch (its own step) before each cross-tenant assertion. Don't try to atomize these — the length is inherent to verifying propagation across tenants.

---

## Known Gaps / Items to Verify

- [ ] Umbrellaleaf-tagged cases are not present in this Consortium Manager subtree; verify new-release deltas in environment.
- [ ] Jira extraction for UICONSET/MODCON/FOLIO component returned zero Done issues in this run; rule dating is therefore TestRail/GitHub-led.
- [ ] Exact Status value vocabularies in Data import/export tables are not consistently enumerated in current case text.
- [ ] Some TestRail capability lines are mixed-format (legacy + Eureka + free text); validate exact capability-set names before posting new cases.
- [ ] Authorization policies: whether a "Share to all" mechanism exists at all for policies (vs. roles) was not confirmed positively or negatively beyond the single sampled create case (C543762); the sampled case's precondition capability list did not include a policy-share capability set, but this is not conclusive — re-verify in environment.
- [ ] The exact confirmation-modal title for role Delete ("Delete role" vs "Delete authorization role") appears in two slightly different forms across cases (C543745 says "Delete role" window; UI Texts table above cites "Delete authorization role" from a different, older case at position 6.50) — reconcile which is current.

> N≥10 audit round (2026-07-22): 15 cases read (C523593, C523671, C552361, C552447, C986307, C692096, C1030054, C1263896, C543745, C543755, C663331, C552363, C566123, C552368, C1045994, C543762) — first deep pass into the "Consortium manager (Eureka)" TestRail subtree (section 40125), which the file's original build had left almost entirely uncited. Added a full new "Authorization Roles / Policies — Eureka Deep-Dive" section covering Create/Duplicate/Delete/Share-to-all name-collision rules (case-insensitive, per-member error text), the previously undocumented "Compare roles" capability-diff tool, CQL-safe role-name handling, the missing "Permission sets" heading in Consortium Manager's Users settings, and Management-pane collapse behavior. Added 9 new Key Business Rules (13-19, some cases covered by more than one) and several new exact toast strings including the literal "Failed to create keycloack role" backend-passthrough typo.
