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

### Toast Messages

| Event | Toast text | Source |
|---|---|---|
| Permission boundary | You do not have permissions at one or more members: | [confirmed] |
| Duplicate role | The role has been successfully duplicated | [confirmed] |
| Shared create success | was successfully created for All libraries. | [from cases (37.45)] |
| Shared update success | was successfully updated for All libraries. | [from cases (20.20)] |
| Role delete success | Role has been deleted successfully | [from cases (7.40)] |
| Role share success | Role has been shared successfully | [from cases (6.70)] |
| Role update success | Role has been updated successfully | [from cases (6.10)] |
| Access denied create | Role could not be created: Access Denied | [from cases (2.50)] |

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

---

## Known Gaps / Items to Verify

- [ ] Umbrellaleaf-tagged cases are not present in this Consortium Manager subtree; verify new-release deltas in environment.
- [ ] Jira extraction for UICONSET/MODCON/FOLIO component returned zero Done issues in this run; rule dating is therefore TestRail/GitHub-led.
- [ ] Exact Status value vocabularies in Data import/export tables are not consistently enumerated in current case text.
- [ ] Some TestRail capability lines are mixed-format (legacy + Eureka + free text); validate exact capability-set names before posting new cases.
