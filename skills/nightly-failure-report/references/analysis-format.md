# analysis.json format

Write `<WORK>/analysis.json` once, in English. `render.py` reads it together with `tests.json` and `meta.json`.

## Example

```json
{
  "environment": "folio-etesting-cypress, tenant diku",
  "fixes": [
    {
      "id": "F01",
      "type": "app",
      "cause": "app-bug",
      "title": "mod-kb-ebsco-java rejects the customDisplayName its own GET returns",
      "confidence": "Confirmed",
      "evidence": "GET /eholdings/packages/58-473 returns customDisplayName \"\"; PUT with the same body returns 422 (PackageCustomAttributesValidator.java:41 checkIsNotBlank).",
      "repo": "mod-kb-ebsco-java",
      "ref": "e1c1c75",
      "owner": "<module owner team, if known>",
      "jira": "PUT /eholdings/packages/{id} returns 422 for the empty customDisplayName returned by GET",
      "changes": [
        {
          "path": "src/main/java/org/folio/rest/validator/packages/PackageCustomAttributesValidator.java",
          "line": 38,
          "tests": "all",
          "why": "Treat blank as 'not set'.",
          "diff": "-    if (displayName == null) {\n+    if (displayName == null || displayName.isBlank()) {"
        }
      ],
      "tests": {"C1259792": null, "C356762": null, "C356760": null}
    }
  ]
}
```

## Fix fields

| field | required | value |
|---|---|---|
| `id` | yes | `F01`, `F02`, ... |
| `type` | yes | `test` \| `app` \| `data` |
| `cause` | yes | `test-bug` \| `outdated-test` \| `env-pollution` \| `parallel-conflict` \| `app-bug` \| `data-missing` \| `infra` |
| `title` | yes | One concrete problem. Vague words (misc, other, various, several, unknown, ...) are rejected. |
| `confidence` | yes | `Confirmed` (a response body, code or screenshot proves it) \| `Likely` |
| `evidence` | yes | The proof in one or two sentences. Not the error text. |
| `repo` | app | Module repository, e.g. `mod-orders`, `ui-users`. |
| `ref` | app | Module commit you read (printed by `app_repo.py`). |
| `jira` | app | Jira summary for the module bug. When an existing ticket covers it (often one linked to the tests in TestRail or in the case's `refs`), write `Existing: <KEY> <summary>` and put the key in `ticket` too; such a fix needs no `changes`, `ref` or `repo`. |
| `owner` | no | Team owning the module. Teams on the card come from the test tags automatically. |
| `ticket` | no | Jira key (`UIEH-1553`) or commit/PR URL that shows why the behavior changed. Allowed on the fix or on a single change. |
| `same_cause` | no | One sentence proving why tests with different errors are fixed by the same change, e.g. "all 13 specs import calendar id a8531527 from calendar-e2e-test-values.js". Without it, a shared change may only cover tests that fail with the same error. |
| `changes[]` | test, app | Code changes, see below. |
| `data[]` | data | Environment changes, see below. |
| `tests` | yes | Map of test id to note. Every failed test id appears exactly once across all fixes. The note says what is specific to this test and is required when its error differs from the rest of the fix; otherwise `null`. When an open ticket linked to the test (`linked_defects.json`) is not the cause, the note says why. |

Linked tickets (from `linked_defects.py`) are shown on each test in the report automatically; you do not copy them into `analysis.json`. `render.py` warns about open linked tickets that a fix's text never mentions.

## changes[]

- `path`: from the repository root.
- `line`: at the run commit (stripes-testing) or at `ref` (module).
- `diff`: full `-`/`+` lines copied from the file. No `...` and no no-op stubs like `() => true`.
- `tests`: `"all"` when one change fixes every test of the fix, otherwise the list of test ids this change fixes.
- `why`: one short sentence.

## data[]

- `what`: what is missing or broken.
- `request`: `{"method": "...", "path": "...", "body": {...}}` - the exact API call.
- `ui`: exact UI steps, when there is no API for it.

Give at least one of `request` and `ui`. Look up real ids and values on the environment or in the test; use `<placeholder>` only when the value differs per environment.
