---
name: "sprint-quarter-progress"
description: "Generate a professional 1-slide PPTX showing sprint feature progress for any Jira team — tasks grouped by UXPROD/feature filter, with progress bars, % done, and summary stats."
---

# Sprint Quarter Progress Slide

Generate a professional 1-slide PPTX showing a team's sprint progress grouped by FY quarter features.

## When to use
User asks for a sprint progress slide, sprint report, or feature status for a team. Typical phrasing:
- "Generate a sprint progress slide for [Team] Sprint [N]"
- "Show feature progress for [Team] FY[Q] sprint [N]"
- "Create a sprint report slide for [Team]"

## Required inputs — ask if not provided
Before starting, confirm:
1. **Team name** (e.g. "Kitfox", "Spitfire", "Volaris")
2. **Sprint number / name** (e.g. "247", "Kitfox Sprint 247")
3. **Feature filter ID or JQL** — the Jira filter that lists the FY quarter features (e.g. `filter=24986`). These are usually UXPROD issues labelled with the FY quarter.

## Step-by-step workflow

### 1. Find the Scrum board and sprint
```
jira_get_agile_boards(board_name="<Team>")          // find board ID
jira_get_sprints_from_board(board_id, state="active")  // find sprint ID
// if not active, also check state="closed" with limit=5
```

### 2. Get all sprint issues
```
jira_get_sprint_issues(sprint_id, fields="summary,status,issuetype,parent,labels,assignee,priority", limit=50)
```
Build a dict: `{ issue_key → status_name }` for every issue in the sprint.
If `total > 50`, paginate using `start_at`.

### 3. Violation check — run before slide generation
Before building the slide, verify every sprint task is linked to a feature in the filter:

For each sprint task, check its `issuelinks` for an outward `Defines` link pointing to a UXPROD issue.
- If the linked UXPROD issue is **not in the filter** → violation
- If there is **no Defines link at all** → violation

If violations exist, **do not generate the slide**. Instead, output a violation report:

```
⚠️  Violation Report — Sprint <N>
──────────────────────────────────
The following tasks are not linked to a feature in filter <FILTER_ID>:

  RANCHER-XXXX  <summary>        No Defines link
  RANCHER-YYYY  <summary>        Links to UXPROD-ZZZ (not in filter)
  ...

Total: N violation(s). Fix links in Jira, then say "recheck".
```

Wait for user to confirm fixes, then repeat steps 2–3 before continuing.

### 4. Get the FY features from the filter
```
jira_search(jql="filter = <FILTER_ID>", fields="summary,status,issuetype,issuelinks,parent,labels", limit=50)
```
Each result is a feature (typically a UXPROD "New Feature" issue).

### 5. Map sprint tasks → features via "Defines" issue links
For each feature:
```
jira_get_issue(issue_key, fields="summary,status,issuelinks")
```
Extract all `issuelinks` where `type.name == "Defines"` (both inward `is defined by` and outward `defines`). Collect the linked RANCHER/task keys.

Cross-reference with the sprint issue dict to find which tasks are **in this sprint** for each feature.

### 6. Count statuses per feature
For each feature's sprint tasks:
- **Done**: status category = `Done`  (Closed, Done, Resolved, In bugfix review)
- **In Progress**: status category = `In Progress`  (In Progress, In Review, In Code Review, In Testing)
- **Blocked**: status name == `Blocked`
- **Open**: any other status

Features with 0 sprint tasks are shown as "No sprint activity" with their feature-level status badge.

### 7. Build the PPTX slide

Install pptxgenjs if needed:
```bash
cd outputs && npm install pptxgenjs
```
Run scripts with:
```bash
NODE_PATH=outputs/node_modules node script.js
```

**Slide layout — 10" × 5.625" (LAYOUT_16x9)**

Color palette (Midnight Executive):
```js
const C = {
  bg:'0D1B2A', cardDark:'0F1F30', cardMed:'152539', divider:'1E3050',
  accent:'4DA6FF', done:'00C897', inProg:'FFAB40', blocked:'FF6666',
  open:'3E5875', inactive:'1A2A40',
  white:'FFFFFF', subtext:'7A9BBE', muted:'3E5572', caption:'2E4460', strip:'0078D4',
  badgeOpen:'1C3A50'
};
```

**Header (y: 0–0.95")**
- Left accent strip: `x:0, y:0, w:0.07, h:5.625` in `strip` color
- Team + quarter label: `"<TEAM> TEAM  ·  FY<QQ>"` — 9pt bold `accent`, charSpacing 2.5
- Title: `"Sprint <N> — Feature Progress"` — 28pt bold `white` Cambria
- Subtitle: `"<StartDate> – <EndDate>  ·  Active/Closed sprint"` — 10pt `subtext`
- Separator line: `y:0.95, h:0.018` in `divider`

**Feature rows**

Row height and layout adapt to the number of active features:
- ≤4 features: `ROW_H = 0.95`
- 5 features: `ROW_H = 0.82`
- 6 features: `ROW_H = 0.675`

For **active features** (has sprint tasks):
- Row bg (alternating `cardDark`/`cardMed`): `x:0.08, w:7.67, h:ROW_H-0.04`
- Feature key (UXPROD-XXXX): 8pt bold `accent`
- Feature name: 12pt bold `white`
- Progress bar bg: `x:0.22, w:5.1, h:0.12` in `divider`
- Segments in order: done(`done`), inProg(`inProg`), blocked(`blocked`), open(`open`) — width proportional to count/total
- Percentage: 24pt bold Cambria — `done` if 100%, `accent` if ≥70%, `inProg` if in progress, else `blocked`; right-aligned
- Task count: `"X / Y tasks"` — 9pt `subtext`, right-aligned

For **inactive features** (0 sprint tasks):
- Row bg in `inactive`
- Key in `muted`, name in `subtext`
- Status badge: small rectangle in `badgeOpen`, text = feature-level status (Closed / Open) in `muted`
- "No sprint activity" label in `muted`

**Vertical divider**: `x:7.82, w:0.018` in `divider`

**Stats panel (x: 8.02–9.75")**
- "SPRINT SUMMARY" — 8pt bold `subtext`, letter-spaced
- Mini overall progress bar (done/total proportion)
- "XX% Complete" — 9pt bold `done`
- 4 stacked stats: Total Tasks (`white`), Done (`done`), In Progress (`inProg`), Blocked (`blocked`)
  - Value: 42pt bold Cambria
  - Label: 8pt bold `subtext`

**Footer (y: 5.36")**
- Legend: 4 colored squares + labels (Done, In Progress, Blocked, Open) — 8pt `subtext`
- Right: `"<Team> Team  ·  <Date>"` — 8pt `caption`

### 8. Visual QA
```bash
libreoffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
# Read slide-1.jpg to verify layout
```

Fix any overflow, clipping, or misalignment before presenting.

### 9. Present the file
```
present_files([{ file_path: "outputs/<filename>.pptx" }])
```

## Output naming convention
`kitfox_sprint<N>.pptx`  (team prefix + sprint number)
e.g. `kitfox_sprint247.pptx`, `spitfire_sprint112.pptx`

## Notes
- The "Defines" link type is FOLIO/RANCHER-specific. If another org uses different link types ("implements", "is child of"), adapt step 5 accordingly.
- If features are Epics rather than UXPROD New Features, use the `parent` field instead of `issuelinks`.
- When Jira search results exceed the token limit (~80 KB), save the raw JSON to a temp file and parse with `python3` via bash to extract only the fields needed.
- The violation check is mandatory — never generate a slide when unlinked tasks exist.
