# Section-by-section guidance

## Summary

The single most-read field. Optimize it for scanning by triagers and for search.

**Anatomy**: `<optional area prefix> <symptom> <trigger/condition>`

**Length**: ≤ 120 characters. Jira truncates in list views.

**Include**:
- The observable symptom — not a guess at the cause.
- The trigger condition or entry point.

**Avoid**:
- Solutions or hypotheses (`"Add null check in ..."`).
- Emotional framing (`"urgent"`, `"horrible"`).
- Ticket numbers (use _links_ instead of the summary).

## Overview / Context

Optional. Use it to answer "why does this matter?" in 1–3 sentences.

Good context:
- "Regression introduced in UIOR-1501 that migrated custom fields to mod-settings."
- "Libraries report blocked month-end close because totals are wrong."

Bad context (move to _Additional information_ or drop):
- Speculation about root cause.
- Long narrative of how you discovered the bug.

## Preconditions

Preconditions are **independently verifiable states** — a QA engineer must be
able to confirm each bullet without running your steps.

Order them from broadest to narrowest:
1. Environment / tenant / build.
2. User role / capabilities / permissions.
3. Data state (records, statuses, relationships).
4. Feature flags / settings.
5. Any prior tickets implemented that set up the scenario.

**Prefer property-based descriptions** over concrete IDs so other testers can
recreate the state:

✓ "An Order in 'Open' status with one PO Line, Receiving workflow = Synchronized,
  Create inventory = Instance/Holding/Item"

✗ "Order `d4e7-...`"

## Steps to reproduce

Rules:
- **One action per step.** If a step contains "and", split it.
- **Start from a named entry point.** "Navigate to Orders app" not "Go there".
- **Use literal labels and paths.** "Click 'Actions' → 'Move holdings/items to
  another instance'" matches the UI.
- **For API bugs**, include method, path, and query string.
- **Stop at the failure.** Post-failure diagnostic actions belong under
  _Additional information_.

Example:
```
1. Log in to folio-etesting-snapshot as diku_admin.
2. Navigate to the Orders app.
3. Open the PO line created in Preconditions step 3.
4. In the Date Received field, change the date to today.
5. Click Save & Close.
```

## Expected result

Answer: what should the user observe if the system works correctly?

Anchor to a source of truth:
- "Per acceptance criterion AC3 in UIOR-1501 ..."
- "Matches the behavior in Ramsons release."
- "Per the API spec in `mod-orders/ramls/...`"

When the "expected" is subjective, **ask the user** where the expectation comes
from rather than asserting it.

## Actual result

Answer: what does the user observe today?

- **Quote error text verbatim.** Include toast text, banner text, HTTP status,
  and response body. Preserve casing and punctuation.
- **Contrast with expected.** "Field shows `Pending` instead of the expected
  `Open`."
- **Do not theorize.** Don't write "Actual: the service is null-deref-ing in X";
  write the user-observable symptom, and put hypotheses in _Additional
  information_.

## Additional information

Structure this section as key: value pairs or short sub-headings, not prose.

Recommended items:
- **Reproducibility**: Always | Intermittent (N/M attempts) | Once.
- **Environment**: tenant, URL, release name.
- **Module versions**: backend and UI modules involved.
- **Correlation IDs / request IDs** for reproducing in logs.
- **Regression source**: the ticket or commit that introduced it, if known.
- **Logs**: include timestamp, logger, level; wrap in a fenced code block.
- **Stack traces**: wrap in a fenced code block.
- **Screenshots / video**: attach in Jira and reference by filename.
- **Workaround**: any steps that let users proceed until the fix ships, or
  `None`. Some FOLIO teams surface this as a dedicated labelled line
  (`Workaround: ...`) rather than a bullet — either is acceptable.
- **Test Cases**: TestRail IDs (e.g. `C15189, C15190`) if your team cross-links
  manual test cases.

## Labels & components

Defer to the triage team unless you have high confidence. Common FOLIO label
patterns you may see, and when to use them:

- `back-end` — for back-end projects.
- `front-end` — for front-end projects.

If unsure, leave labels and components empty and let triage populate them.
