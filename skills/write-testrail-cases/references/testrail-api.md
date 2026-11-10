# TestRail API, Metadata and Markup

## Test Group values

- **Smoke (1)** — not used for manual cases (automated only).
- **Critical Path (2)** — the feature's core business-rule cases, key status transitions, main create/edit/delete, key capability boundaries. ~24% of recent human manual cases.
- **Extended (3)** — default: UI element checks, search/filter, edge and negative cases, secondary flows, regression of adjacent behavior. ~70% of recent human manual cases.
- **Obsolete (4), Draft (5), Backend (6), Edge Cases (7)** — never set on a new case unless the user asks.

---

## Metadata Fields Reference

> **Resolve IDs at runtime.** Dropdown fields (Type, Priority, Release, Test Group, Execution Type, Dev Team, Customer Name, Automation Scope/Team/For) take a **numeric option ID**, not the label string — sending a label returns `400 Field :<name> is not a valid natural number`. Look up the current IDs with `GET /index.php?/api/v2/get_priorities`, `get_case_types`, and `get_case_fields`. Checkbox fields take a JSON **boolean** (`true` / `false`). The option IDs below are a snapshot from `foliotest.testrail.io` and may change — always confirm via the API.
>
> **Required fields:** `custom_test_group` and `custom_automation_type` (labelled "Execution Type"). A case will not post without them.
>
> **Standing defaults (do not ask the user):** `ECS Unsupported = false` on every case, and **every case gets the `ai` label (id 67)**. Set `ECS Enabled = true` only when the story explicitly tests cross-tenant / ECS behavior.

| Field | TestRail API key | Type | Default | Options / Notes (current IDs) |
|---|---|---|---|---|
| Title | `title` | string | — | See `house-style.md` → Titles. Prefixes only if already used in the target section. |
| Type | `type_id` | dropdown (id) | **Per area — see `house-style.md`** | Resolve via `get_case_types`. Current: **Functional=6**, Other=7 (also Acceptance=1, Regression=9, Smoke & Sanity=11). Type is area-dependent: acquisitions (Orders/Invoices/Finance/Organizations/Mediated) skew **Functional**; most circulation/ERM/export areas (Loans/Fees&Fines/Bulk Edit/Agreements/License/Data Export/OAI-PMH/etc.) skew **Other**; several are ~50/50. Use the dominant Type of the target area's row, or sample the area's section if it's not listed. |
| Priority | `priority_id` | dropdown (id) | **Medium (2)** | Resolve via `get_priorities`. Current: Low=1, Medium=2, High=3, Critical=4. People set Medium on 83% of recent manual cases. **High** — the main daily workflow of the feature. **Critical** — failure blocks a core library operation (check-in/out fulfillment, opening/paying an order, posting an invoice). Edit/duplicate, capability boundaries, UI checks, search/filter, edge/negative → Medium. |
| Release | `custom_release` | dropdown (id) | latest release | Resolve the newest option from `get_case_fields` at runtime. Snapshot 2026-11: **R2 2026 Umbrellaleaf=21**, R1 2026 Trillium=20, R1 2025 Sunflower=19. 87% of manual cases created since Sep 2026 use 21. |
| Test Group | `custom_test_group` | dropdown (id) | **Extended (3)** | **Required.** Smoke=1, Critical Path=2, Extended=3, Obsolete=4, Draft=5, Backend=6, Edge Cases=7 |
| Execution Type | `custom_automation_type` | dropdown (id) | `Manual` (2) | **Required.** Automated=1, Manual=2, Karate=3, Unit=4, Backend Component=5 (TestRail label is "Execution Type"; API key is `custom_automation_type`) |
| User Journey | `custom_user_journey` | checkbox (bool) | `false` | Set `true` when the case is a **journey/lifecycle case** — one case walking a multi-step flow through several checkpoints or outcomes (e.g. check in an item with an open request through both the in-transit and hold-shelf outcomes plus slip reprints; order open → receive → pay). Keep `false` for atomic feature/element cases. This flag must agree with the case shape you chose in "Journey vs atomic cases" — a journey case with `User Journey = false` is a self-review failure. |
| Multi-Tenant | `custom_multi_tenant` | checkbox (bool) | `false` | `true` / `false` |
| Bug Created | `custom_bug_created` | checkbox (bool) | `false` | `true` / `false` |
| Unstable | `custom_unstable` | checkbox (bool) | `false` | `true` / `false` |
| ECS Enabled | `custom_ecs_enabled` | checkbox (bool) | `false` | Set to `true` when the story explicitly tests ECS/cross-tenant behavior. Otherwise `false`. |
| ECS Unsupported | `custom_ecs_unsupported` | checkbox (bool) | `false` | **Always `false`. Never ask the user.** |
| Capabilities Ready | `custom_capabilities_ready` | checkbox (bool) | `true` | `true` / `false` |
| Dev Team | `custom_dev_team` | dropdown (id) | — | From "Development Team" in the story. e.g. Concorde=1, Firebird=3, Folijet=4, Spitfire=6, Thor=7, **Thunderjet=8**, Vega=9, Volaris=13, Citation=18, Eureka=21 (full list via `get_case_fields`) |
| Customer Name | `custom_customer_name` | dropdown (id) | — | Optional. All=1, MOBIUS/GALILEO=2, LOC=3 — set only when the story targets a specific customer |
| Automation Scope | `custom_automation_scope` | dropdown (id) | — | Optional; omit if N/A. Review by MQA=1, Review by PO=2, Automation Ready=3, Not an automation candidate=4, Mriya scope=5, Karate Approved=6, Karate Not Applicable=7, FE scope=8 (no "None" option) |
| Automated For | `custom_case_automated_in` | dropdown (id) | — | Optional; omit if N/A. Old releases=1, R2 2024 Ramsons=2, R1 2025 Sunflower=3, R2 2025 Trillium=4 |
| Automation Team | `custom_automation_team` | dropdown (id) | — | Optional; omit if N/A. TaaS=1, Mriya=2, FE team=3 (no "None" option) |
| References | `refs` | string | — | The work item(s) this case verifies, comma-separated. Often a Bug or Tech-Debt ticket rather than a story, and may span several projects (e.g. `UIF-525, MODFIN-391`). Do not invent a story key when none exists; do not auto-add unrelated links pulled in via enrichment. |
| Labels | `labels` | array | `[67]` | **Always `ai` (id 67 on foliotest.testrail.io; resolve via `get_labels/{project_id}`).** `BFreviewed` (id 62) only where surrounding cases carry it (Requests, Renewals, Check In; never Invoices). Never add other labels on your own. |

---

---

## HTML markup for TestRail fields

> **Verified against the real TestRail corpus** (`foliotest.testrail.io`, project 14, suite 21) by reading the *raw* `custom_preconds` / `custom_steps_separated` JSON (not the HTML-stripped preview) of real cases — C446093, C446007, C442797, C442809, C446167, C468169, C1045421, C374168.

`custom_preconds`, `custom_steps_separated[].content`, and `custom_steps_separated[].expected` are **HTML fields**, not plain text. Whatever string you send is stored close to as-is — the API does **not** auto-convert `\n`, hand-typed `1.`/`-`/`;` characters, or Markdown into real paragraphs, lists, or bold. You must send actual HTML tags, or the case will render wrong in the TestRail UI.

### The failure mode this section fixes

Sending plain text with hand-typed structure (`"1. First\n2. Second"`, `"- item"`, `"A; B; C"`) gets wrapped in a single `<p>...</p>` tag. Browsers collapse a raw `\n` inside `<p>` (it is not `<br>`), so it renders as **one flat run-on paragraph** with no visible numbering, no bullets, and no line breaks — even though the string looked formatted when it was typed. This exact mistake happened when case C1538608 was first posted (plain-text `"1. ... 2. ..."` preconditions collapsed into one paragraph; semicolon-joined expected results rendered as one flat sentence instead of the bullets used by every sibling case in that section). Never rely on plain-text punctuation to create structure — always build the HTML tags below.

### Preconditions

Preconditions must always be **visually separated, one per line/block** — never concatenated into one paragraph. Use the style the target section already uses (workflow step 4); with no section signal, use style 1. Observed share in recent human cases: `<ul>` 32%, plain `<p>` 26%, `<ol>` 22%, `<p>1)` 14% — so matching the section matters more than any global rule.

1. **TestRail's built-in numbered list (preferred)** — wrap the whole precondition list in `<ol>`, one `<li>` per item:
   ```html
   <ol><li>First precondition</li><li>Second precondition</li><li>Third precondition</li></ol>
   ```
   Confirmed real example (C374168, raw `custom_preconds`):
   ```html
   <ol>
   <li>An Acquisition unit with all restrictions (View, Edit, Create, Delete options are <strong>active</strong>) exists in Settings-&gt;Acquisition units</li>
   <li>A user with all Finance permissions exists</li>
   <li>A user from Precondition item #2 is assigned to Acquisition unit from Preconditions item #1</li>
   </ol>
   ```

2. **Manual numbering in plain text** — when the section uses it (common in Orders, OAI-PMH, Circulation log) or the user asks. Each numbered item is still its own separate `<p>` tag (do not rely on `\n` to separate them):
   ```html
   <p>1) First precondition</p><p>2) Second precondition</p><p>3) Third precondition</p>
   ```
   Confirmed real example (C1045421): `<p>1) Profile pictures are disabled on environment</p><p>2) User has experience...</p>`

3. **No numbering** — only when the section uses it or the user asks; steps then reference preconditions by content, not by number. Still one `<p>` per item:
   ```html
   <p>First precondition</p><p>Second precondition</p><p>Third precondition</p>
   ```
   Confirmed real example (C446093/C446007/C442797): `<p>Profile pictures are enabled...</p><p>User "B" is created...</p><p>User "A" is logged in...</p>`

A sub-list under one precondition item (e.g. Capability Sets under "User is logged in with...") is a nested `<ul><li>` inside that item's `<li>`/`<p>` — see Nested lists below.

### Steps — `content` (the Action)

Complements the content-level "Steps — Granularity and Format" rules above; this is how to encode that structure as HTML for the API.

- **One action → plain text, no list markup.** Wrap in a single `<p>`:
  ```html
  <p>Click "Actions" -&gt; "Edit" on the user details pane</p>
  ```
- **Several actions in sequence → an optional intro line + a real `<ul><li>` bullet list**, one `<li>` per sub-action, each ending in `;` (the last one may end in `.`):
  ```html
  <p>Create a new request:</p>
  <ul>
  <li>Go to "Requests" app;</li>
  <li>Click "Actions" -&gt; "New request";</li>
  <li>Populate this;</li>
  <li>Populate that;</li>
  <li>Click "Save &amp; close".</li>
  </ul>
  ```
  Omit the intro `<p>` line when the sub-actions don't need a lead-in.

### Steps — `expected` (the Expected Result)

- **One assertion → plain text, one line.** Wrap in a single `<p>`:
  ```html
  <p>"Save" button becomes active</p>
  ```
- **Several assertions → a real `<ul><li>` bullet list**, one `<li>` per checkable fact:
  ```html
  <ul><li>"Edit" pane is closed</li><li>Profile picture is not present on 3rd pane view</li></ul>
  ```
- **Nested elements within one assertion (e.g. "the following options are present: A, B, C") → a nested `<ul><li>` inside the outer `<li>`.** Confirmed real example (C468169, raw `expected`):
  ```html
  <ul>
  <li>Accordion is expanded</li>
  <li><p>Following options are present:</p>
  <ul><li>"Local file"</li><li>"External URL"</li><li>"Delete"</li></ul></li>
  </ul>
  ```

### Bold emphasis (`<strong>`)

Use `<strong>...</strong>` — never Markdown `**...**`, which renders as literal asterisks in a TestRail HTML field — to highlight:
- **Tenant names** in ECS steps/preconditions. Confirmed real example (C446167): `<p>Switch active affiliation to the <strong>Member</strong> tenant</p>`, and preconditions naming `<strong>Central</strong>` / `<strong>Member</strong>` tenants throughout.
- **Negation**. Confirmed real example (C442809): `Make sure user <strong>does not</strong> have permissions...`.
- **An important note or a non-obvious, complex precondition** — sparingly, only where a reviewer skimming the case could otherwise miss the critical detail.

Don't bold whole sentences or routine UI labels/button names — those already stand out via quotes; reserve `<strong>` for the tenant/negation/critical-note cases above.

### HTML escaping

Escape `&`, `<`, `>` in literal text: `&amp;`, `&lt;`, `&gt;` — e.g. `"Save & close"` → `"Save &amp; close"`, `Settings->Acquisition units` → `Settings-&gt;Acquisition units` (see the confirmed `<ol>` example above). This matters even inside prose, not just around tags — an unescaped `<` or `>` can be misparsed as markup.

### Mandatory pre-post check

**Before calling `add_case` / `update_case`, mentally render the HTML you are about to send and confirm it displays identically to how you displayed the case in your chat reply**: a numbered line in your preview → `<ol>` or manual `1)` `<p>`s in the payload; a bulleted line in your preview → `<ul><li>` in the payload; **bold** text in your preview → `<strong>` in the payload; a plain prose line in your preview → a plain `<p>` in the payload. If what you're about to POST would not visually match what you showed the user, fix the HTML before posting — never post first and check the rendering afterward.

---

## API Integration

### Credentials

Read credentials using this fallback chain (try in order, stop at first hit):

1. `.env` file in the repository root — parse KEY=VALUE pairs
2. `~/.folio-credentials` — legacy local file
3. Environment variables — for CI/Codespaces

Keys to read:
```
TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_API_KEY
JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN
GITHUB_TOKEN (optional)
```

Never ask the user for credentials — try all three silently. If all three fail — report which keys are missing and stop.

### Jira MCP Integration

When the user provides a Jira ticket ID instead of pasting a User Story:

1. Use the Jira MCP tool to fetch the issue by ID
   - Extract: Summary, Description, Acceptance Criteria, Development Team, Fix Version
   - Use the issue key as `refs` value
   - Use Development Team field for `custom_dev_team`
2. If Jira MCP is not available — ask the user to paste the User Story manually
3. Proceed with the Mandatory Workflow as normal

### Sampling the target section (workflow step 4)

```
GET {TESTRAIL_URL}/index.php?/api/v2/get_cases/14&suite_id=21&section_id={section_id}&limit=10&offset=<newest>
```

Use the 10 most recently created cases (sort by `created_on`). Read the **raw** `custom_preconds` and `custom_steps_separated` (not an HTML-stripped preview) and record: preconditions markup, permissions block, title prefixes, separators, Type, labels, step count. Prefer cases without the `ai` label as the style reference — they are what reviewers accept as the norm.

### Finding existing cases (workflow step 4b)

```
GET {TESTRAIL_URL}/index.php?/api/v2/get_cases/14&suite_id=21&refs=UICIRC-1390
```

The `refs` filter returns every case whose `refs` contains the key (e.g. `UICIRC-1387,UICIRC-1390,UICIRC-1399`). Run it for each key from step 3. Title search: `search_test_cases` (MCP) or `get_cases/14&suite_id=21&section_id=<id>&filter=<text>`.

### Posting preview

After generation and self-review, ask: _"Please provide the TestRail Section (folder) ID where the cases should be posted."_ Then show:

```
Ready to post 5 test cases to Section ID: XXXXX

1. User with Edit capability set can create unlocked mapping profile — Other / High / Critical Path
2. User with Edit capability set can edit unlocked mapping profile — Other / High / Critical Path
3. User with Edit capability set cannot delete mapping profile referenced in job profile — Other / High / Critical Path
4. Mapping profile "Status" column shows "Locked" after lock checkbox is enabled — Other / Medium / Extended
5. User with View-only capability set cannot see "New" or "Actions" buttons — Other / High / Critical Path

Confirm? (yes / no / edit)
```

Wait for explicit confirmation, then post.

### Add case request

```
POST /index.php?/api/v2/add_case/{section_id}
Content-Type: application/json
Authorization: Basic <base64(email:api_key)>
```

```json
{
  "title": "User with Edit capability set can delete unlocked mapping profile not referenced in job profile",
  "type_id": 7,
  "priority_id": 2,
  "refs": "MODFIN-273",
  "custom_preconds": "<ol><li>User with the following capability sets is logged in:<ul><li>data - UI-Data-Export Settings - edit</li></ul></li><li>Unlocked mapping profile NOT referenced in any job profile exists</li><li>User is on Settings &gt; Data export &gt; Field mapping profiles</li></ol>",
  "custom_steps_separated": [
    {
      "content": "<p>Click on the row with the unlocked mapping profile from Preconditions #2</p>",
      "expected": "<p>Mapping profile view form is displayed; \"Lock profile\" checkbox is disabled, unchecked; \"Actions\" menu is enabled</p>"
    },
    {
      "content": "<p>Click \"Actions\" menu</p>",
      "expected": "<p>Menu expands and displays the following options: Edit, Duplicate, Delete</p>"
    },
    {
      "content": "<p>Click \"Delete\" option</p>",
      "expected": "<p>\"Delete mapping profile\" modal opens with: \"The mapping profile &lt;name&gt; will be deleted.\" text, \"Cancel\" button (enabled), \"Delete\" button (enabled, focused)</p>"
    },
    {
      "content": "<p>Click \"Cancel\" button</p>",
      "expected": "<p>\"Delete mapping profile\" modal closes; mapping profile view form is displayed</p>"
    },
    {
      "content": "<p>Click \"Actions\" menu -&gt; \"Delete\", then \"Delete\" in modal</p>",
      "expected": "<p>Modal closes; toast message \"Mapping profile &lt;name&gt; has been successfully deleted\" is displayed; \"Field mapping profiles\" pane shows list without deleted profile</p>"
    }
  ],
  "custom_release": 21,
  "custom_test_group": 3,
  "custom_automation_type": 2,
  "custom_dev_team": 4,
  "custom_customer_name": 1,
  "custom_multi_tenant": false,
  "custom_user_journey": false,
  "custom_bug_created": false,
  "custom_unstable": false,
  "custom_ecs_enabled": false,
  "custom_ecs_unsupported": false,
  "custom_capabilities_ready": true,
  "labels": [67]
}
```

> The dropdown values above are **option IDs**, not labels. Resolve via `get_case_fields` / `get_priorities` / `get_case_types`. `custom_ecs_unsupported` is **always `false`**; `custom_ecs_enabled` is `true` only for ECS stories. `"labels": [67]` is the `ai` label, always added. Every `content`/`expected` value is HTML (`<p>`, `<ul><li>`), escaped (`&gt;`, `&amp;`) — see HTML markup above.

### Success output

After posting all cases, report:
```
✅ Posted 5 test cases to Section 1042:
  C123456 — User with Edit capability set can create unlocked mapping profile
  ...
```

### Error handling

| HTTP status | Action |
|---|---|
| `401` | Credentials error — check `.env` or `~/.folio-credentials` |
| `400` | Show the full error body and identify which field caused it |
| `404` | Confirm the Section ID exists and is accessible |
| Any failure | Do not skip silently — report the failed case title and full error message |

---

## Fallback Output (no API access)

If posting via API fails entirely, output each case in this format:

```
---
Title:          [title]
Type:           [Functional | Other — per area]
Priority:       Medium   [unless house-style.md says otherwise]
Release:        [latest release]
Test Group:     [Smoke | Critical Path | Extended]
Execution Type: Manual
Dev Team:       [from story]
References:     [jira_ids]

Preconditions:
1. User with the following capability sets is logged in:
   - data - UI-[App] [Resource] - [action]
2. [Required data with exact values]
3. User is on [app/page]

Steps:
1. Action:   [step]
   Expected: [result]
---
```

Capability set format: `[data | procedural | settings] - UI-<App> <Resource> - <action>` — see `writing-rules.md` → Preconditions.
For API field IDs: `GET /index.php?/api/v2/get_case_fields`

---
