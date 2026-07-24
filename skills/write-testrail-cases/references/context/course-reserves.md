# FOLIO Course Reserves — Business Logic Context

> Built 2026-07-21 (browser-based). **Exact UI Texts confirmed against `folio-org/ui-courses/translations/ui-courses/en_US.json` (2026-07-21).** TestRail: suite 21 section 1116 "Course Reserves" (subsections 1117 Courses, 1118 Reserve Items, 1119 Settings, 1125 Permissions, 1126 "Courses: Read only"). This area is legacy/lightly-maintained (many cases from 2020, unchanged since) — real cases are often thinner and less rigorous than newer areas like Fees/Fines; still apply this skill's full verification-depth rules when generating new cases, don't mirror the legacy case's shallowness.

---

## What is Course Reserves

The Courses app lets library staff link Inventory items to an academic course so students can find and borrow "reserve" materials (readings, media) tied to that course/term. A **Course** record (name, code, section, term, instructor(s), department, location) has a list of **Reserve items** (Inventory items added by barcode) and can be **cross-listed** with other course sections. Reserve items get a **temporary location** and **temporary loan type** applied while on reserve, and can be tracked for copyright/processing status.

---

## Key Terms

| Term | Definition |
|---|---|
| Course | The organizing record: name, code, section, term, department, instructors, service desk |
| Cross-listed course | A second course record sharing the same reserve items as the original ("Crosslist" action) |
| Reserve item | An Inventory item added to a course by barcode; gets temporary location/loan type while reserved |
| Term | A configured date range (start/end) a course runs within (Settings > Courses > Terms) |
| Course type | Configured category for a course (Settings > Courses > Course Types) |
| Processing status | Configured workflow status for a reserve item (Settings > Courses > Processing Statuses) |
| Copyright status | Configured copyright-tracking status for a reserve item (Settings > Courses > Copyright Statuses) |
| Instructor | A person tied to a course, either a full User record (via Look up user) or a free-text name+barcode |

---

## UI structure [confirmed]

- **Courses main page**: left pane `Search & filter` (search box with dropdown scope: `All fields`, `Course name`, `Course code`, `Section`, `Instructor`, `Registrar ID`, `External ID`; filter accordions `Department`, `Course type`, `Term`, `Location`); middle pane list of courses (columns `Course name`, `Course code`, `Department`, `Service desk`, `Start date`, `End date`, `Instructor`, `Status`); `New` button (`Create course`).
- **Course detail pane** accordions: `Course data` (principal data), `Cross-listed courses`, `Instructors`, `Term`, `Organization` (local info), reserves accordion titled with a live count (`{count} item(s)`), `Developer info` (raw JSON dump), `Notes`.
- **Reserve item row** (within the reserves accordion): Title, Barcode, Contributor, Permanent location, Temporary location, Call number, Volume, Copy, Enumeration, Status, Processing status; `Edit reserve` / `Remove` actions per row.
- **Add item to reserves**: `Enter or scan barcode` box + `Add item` button; option to `Add existing Inventory item as a reserve` or `Create new Inventory item and add it as a reserve` (Fast Add: `Add Fast Add item`).
- **Instructors accordion**: `Add instructor` button opens a form with `Name`, `Barcode` fields OR a `Look up user` action to attach a real User record; `Edit` / `Remove` per instructor row.
- **Crosslist**: `Crosslist` button on an existing course opens `New course within listing` — `Cross listing information` pre-filled from the source course, `Basic course information` empty for the new section.
- **Duplicate course**: `Duplicate` action opens a modal with `Duplicate all cross-listed courses` checkbox (default state driven by the Settings > Display setting below) + `Create duplicate course(s)`.
- **Settings > Courses**: `Terms`, `Course Types`, `Course Departments`, `Processing Statuses`, `Copyright Statuses`, `Roles`, `Display settings` (`Duplicate cross-listed courses` toggle).

---

## Exact UI Texts [confirmed against en_US.json]

### Toasts / messages

| Event | Message |
|---|---|
| Item added to reserves | `Added item "{title}"` |
| Duplicate barcode added | `Duplicate barcode {barcode}: this item is already on reserve for this course` |
| Add item failed | `Failed to add item {barcode}: {message}` |
| Missing barcode on Add item | `Please enter a barcode before selecting "Add item"` |
| Remove reserve failed | `Remove reserve failed: {message}` |
| Remove instructor failed | `Remove instructor failed: {message}` |
| Course deleted | `The course <b>{name}</b> with course number <b>{number}</b> was deleted.` |
| Confirm course deletion (modal) | `Confirm deletion of course` |
| Term deleted | `The term <b>{term}</b> was successfully <b>deleted</b>` |
| Term deletion confirm (modal body) | `The term <b>{term}</b> will be <b>deleted.</b>` |
| Term delete blocked | Header `Cannot delete the term`; body `This term cannot be deleted, as it is in use by one or more records.` |

### Field labels / statuses [confirmed]

Course status values: `Pending`, `Active`, `Inactive`. Reserve item fields: `Course code` (`field.number`), `Section`, `Course type`, `Registrar ID`, `External ID`, `Barcode`, `Patron group`, `Term`, `Start date`, `End date`, `Location`, `Service desk`, `Item barcode`, `Contributor`, `Permanent location`, `Call number`, `Volume`, `Copy`, `Enumeration`, `Status`, `Temporary location`, `Temporary loan type`, `Processing status`, `URL/PDF link`, `Additional sections of this item used`, `Copyright status`, `Total number of pages in item`, `Total number of pages used`, `Total % of pages used`, `Payment based on`.

### Empty-search message pattern (confirmed C9185)

`No results found for "{search term}". Please check your spelling and filters.`

---

## Capability Sets (Eureka) — from legacy permission display names [confirmed permission strings]

| Legacy permission | Scope |
|---|---|
| `Courses: All permissions` | Full access |
| `Courses: Read all` | View only |
| `Courses: Read, add, and edit courses` | Course CRUD minus delete |
| `Courses: Read, add, edit, and delete courses` | Full course CRUD |
| `Courses: Add and edit courses' reserved items` | Reserve items create/edit |
| `Courses: Add, edit, and remove courses' reserved items` | Reserve items full CRUD |
| `Settings (Courses): Can view course settings` | View Terms/Course Types/Departments/etc. |
| `Settings (Courses): Can create, edit and delete course settings` | Manage those settings |

> Curate exact Eureka Capability Set names in env before use — only legacy Okapi permission display names are confirmed here (see section 1125/1126 "Courses: Read only" for the read-only-boundary case pattern: a read-only user must NOT see create/edit/remove controls, only view).

---

## Common Verification Patterns

### Create a course (confirmed pattern, C9171)

Preconditions: Course Reserve settings (Term, at least) already configured; user with course-create permission.
1. From Courses main page click `New` (`Create course`).
2. Fill required fields `Course name`, `Term`, `Service desk` (plus any others in scope) → `Save & close`.
3. Expected: new course appears in the course list (search may be needed if the list exceeds the page).

### Add a reserve item and cross-check against Inventory (confirmed pattern, C9183)

Preconditions: a Course exists; an Inventory item with a known barcode exists.
1. On the course, scroll to the reserves section, enter the barcode in `Enter or scan barcode`, click `Add item`.
2. Expected: item appears in the reserve list (toast `Added item "{title}"`).
3. Compare reserve-row values against the Inventory item record: `Title`, `Contributors`, effective `Call number`, `Permanent location`, `Status`, `Copy`, `Volume` must match exactly — this is a genuine cross-app data-integrity check, not just "item is displayed".

### Remove a reserve item — verify the Inventory-side side effect (confirmed pattern, C9190)

1. Note the reserve item's current temporary location and permanent location before removing.
2. Click `Remove` on the reserve row.
3. Expected: item no longer in the course's reserve list AND (cross-app check) the Inventory item's temporary location is cleared — verify in Inventory, not just in Courses.

### Instructors — two distinct add paths (apply the "every entry point" rule)

An instructor can be added two ways with different resulting data shape:
- **Free-text add**: `Add instructor` → fill `Name` + `Barcode` manually → no linked User record.
- **Look up user**: `Add instructor` → `Look up user` → search/select a real user → instructor row shows name + barcode + patron group pulled from the User record.
Both paths, plus `Edit instructor` and `Remove instructor`, should be covered as distinct scenarios — they exercise different code paths (manual entry vs. user-search plugin) and have independently regressed before.

### Crosslisting (confirmed pattern, C9174)

1. On an existing course, click `Crosslist`.
2. Expected: `New course within listing` opens with `Cross listing information` pre-filled from the source course and `Basic course information` empty.
3. Fill `Course name` (+ any other fields) → `Save & close`.
4. Expected: new course appears under `Cross-listed courses` on the original course record.

### Search & filter (confirmed pattern, C9185/C9186)

Search dropdown scope options: `All fields`, `Course name`, `Course code`, `Section`, `Instructor`, `Registrar ID`, `External ID` — verify at least one real hit and one no-hit case per relevant scope (no-hit message above). Filter accordions `Department`, `Course type`, `Term`, `Location` — verify each expands, filters correctly alone, and in combination with a second filter.

**Known live issue (BF-809, cited directly in C9186)**: filtering by `Course type` currently does NOT work correctly — a case exercising this filter should expect/flag the discrepancy rather than assume it behaves like the other three (Department/Term/Location, which do work).

### Notes accordion — confirmed NOT to leak other apps' checkboxes [confirmed — C421983]

Both the `New note` and `Edit note` windows opened from a Course record's Notes accordion correctly OMIT the `Check out app` and `Users app` checkboxes that exist on Notes forms in other apps — this is a regression-guard assertion (not a live bug) confirming Courses' Notes integration stays properly scoped to just Course-relevant note types/fields.

### Settings — Processing Statuses / Copyright Statuses [confirmed — C9176; resolves prior Known Gap]

Both follow the identical `New` → `Name` + `Description` → `Save` pattern as Terms/Course Types/Departments. Once created, both become immediately selectable in a reserve item's own `Edit Reserve` form (`Processing Status` / `Copyright Status` dropdowns) — no separate publish/activate step.

### Settings — Term / Course Type / Course Department [confirmed — C9175; resolves prior "other settings entities" gap]

Term additionally requires `Start Date`/`End Date` (beyond Name); Course Type and Course Department follow the plain Name+Description pattern. All three, once created, become immediately available in the Course record's own `Edit` form dropdowns (`Term`, `Course Type`, `Course Department`).

### Edit Reserve item form [confirmed — C9184]

Opens with the Item's Title + Contributors displayed at the top of the screen, followed by the full set of editable reserve-item fields below.

### Temporary loan type always displays by name, never by UUID [confirmed — C357543]

The Items accordion's `Temporary loan type` field always renders the human-readable name (e.g. "Course reserves"), never the raw UUID — a specific regression-style assertion worth including whenever a case touches this field.

### Duplicate Cross-Listed Courses — setting directly drives the modal's default checkbox [confirmed — C343206]

Toggling Settings > Courses > Display Settings > `Duplicate Cross-Listed Courses` and saving directly controls whether the `Duplicate all cross-listed courses` checkbox on the course's own Duplicate modal opens pre-checked or pre-unchecked — confirmed both directions (checked setting → checked modal box; unchecked → unchecked).

---

## Key Business Rules for Test Cases

1. A reserve item's `Temporary location` / `Temporary loan type` are applied to the underlying Inventory item while reserved, and cleared when the reserve is removed — always cross-check the Inventory item record, not just the Courses-app row. (cases — C9190)
2. Adding the same barcode twice to the same course is blocked with an explicit duplicate message, not a silent no-op. (github — `addItem.duplicateItem`)
3. Reserve-item field values (Title, Contributors, Call number, Permanent location, Status, Copy, Volume) must be sourced from and match the Inventory item exactly. (cases — C9183)
4. Instructors can be added either as free-text (Name+Barcode only) or via `Look up user` (full User-record link) — these are two different data shapes and two different UI entry points. (cases — C9173, C9187)
5. Crosslisting a course pre-fills `Cross listing information` from the source course but leaves `Basic course information` blank for the new section — the two courses then share reserve items. (cases — C9174)
6. Duplicating a course offers a `Duplicate all cross-listed courses` checkbox whose default state is itself a configurable Setting (`Display settings > Duplicate cross-listed courses`) — a case touching duplicate-defaults must set/verify that setting first. (github)
7. A Term/Course Type/etc. that is referenced by an existing course/record cannot be deleted — same "in use, cannot delete" guard pattern as other settings areas. (github — Term shown; other settings entities follow the same convention, verify per-entity wording in env)
8. Read-only permission (`Courses: Read all` / "Courses: Read only" role) must NOT expose New/Edit/Remove/Delete controls anywhere in the app — verify absence of controls, not just inability to save. (cases — section 1126)
9. Course list is sortable by column headers (Course name, Course code, Section, etc.) with correct locale-aware alphabetic ordering (team explicitly checks Scandinavian A–Å ordering) — verify ascending AND reversed-on-second-click. (cases — C825318)
10. Courses with more than 20 reserve items must still display per-item Status for every item, not just the first page — a real regression (UICR-210) when the reserve list required pagination/expansion. (cases — C605979)
11. Sorting applies uniformly across multiple list column headers (Course name, Course code, Section, etc.), each toggling ascending/descending on repeated clicks with locale-aware alphabetic ordering. (cases — C825318)
12. Processing Statuses and Copyright Statuses (like Term/Course Type/Department) become immediately selectable in their respective forms as soon as created — no separate activation step. (cases — C9176, C9175)
13. The Course type search filter is a known-broken exception among the four filter accordions (BF-809) — don't assume parity with Department/Term/Location without verifying against the current release. (cases — C9186)

---

## Authoring style (measured 2026-07-23)

Course Reserves: **`Other` ~61%** / Func ~39%, median **~3 steps** (short), `User Journey` ~0%. Compact atomic cases — create/edit a course, add/remove a reserve item, assign an instructor, crosslist, verify a display field. `Other` for display/config; `Functional` for behavior that changes item temporary loan type / location on reserve add-remove. Setup (a course, an instructor, an item) lives in Preconditions; steps stay short.

---

## Known Gaps / Items to Verify

- [ ] Exact Eureka Capability Set names — only legacy Okapi permission display names confirmed; verify in env.
- [x] Copyright-tracking and Processing-status field-level validation/behavior — **confirmed** (C9176): same New/Name+Description/Save pattern as other settings entities; see "Settings — Processing Statuses / Copyright Statuses" above.
- [x] Notes-accordion behavior in Courses — **corrected and confirmed** (C421983): the case is actually a regression-GUARD confirming the Check-out/Users checkboxes do NOT leak onto a Courses note (the prior note in this file mischaracterized it as showing a live bug — it documents the expected, bug-free state).
- [x] Settings entities beyond Terms — **confirmed** (C9175, C9176): Course Types, Course Departments, Processing Statuses, and Copyright Statuses all follow the identical New/Name(+Description or dates)/Save pattern and immediately populate their respective Course/Reserve-item form dropdowns.
- [ ] Courses app baseline keyboard shortcuts (C350570) exist as a dedicated list (same convention as Organizations/Licenses) but the exact shortcut table itself was only referenced via an attachment image in the pulled case, not captured as text — pull again with an eye toward extracting the literal key combinations if a case specifically needs them.

> N≥10 audit round (2026-07-22): 14 cases read (C421983, C9176, C9184, C357543, C9189, C343206, C350570, C825318, C605979, C9175, C9185, C9186, C9174, C9187). Resolved three of the file's four open Known Gaps (Copyright/Processing status behavior, Notes-accordion — including correcting a prior mischaracterization of C421983 as a bug when it's actually a regression guard confirming no leak, and full settings-entity parity for Course Types/Departments/Processing/Copyright Statuses). Also surfaced a known live filter bug (BF-809, Course type filter non-functional) worth flagging rather than assuming works. Added 3 new Key Business Rules (11-13).
