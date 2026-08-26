# Bulk Edit — TestRail Config

Section IDs verified against `foliotest.testrail.io` project 14 on 2026-08-19.

## Project

| Property | Value |
|---|---|
| `project_id` | `14` (FOLIO Bug Fest) |
| `suite_id` | `21` (Master) |
| Target (archive) section | `65470` |
| Release threshold | `20` (R1 2026 Trillium) — ⚠️ see note below |

## Source Sections

| Section | ID |
|---|---|
| Root | `17140` |
| Capabilities | `17141` |
| Identifier | `17142` |
| Query | `21336` |
| Repeatable fields | `17481` |
| Logs | `21205` |
| Bulk Edit - FOLIO Instances | `31447` |
| Bulk Edit - Instances with source MARC | `40726` |
| Bulk Edit - Holdings | `19564` |
| Bulk Edit - Items | `19563` |
| Bulk Edit - Users - In App | `18881` |
| Bulk Edit - Users - Local | `19565` |
| Bulk Edit - ECS (parent) | `37956` |
| Central tenant | `48414` |
| Member tenant | `48415` |
| Bulk Edit - Profiles | `17480` |

## Release IDs

| ID | Release |
|---|---|
| `21` | R2 2026 Umbrellaleaf |
| `20` | R1 2026 Trillium |
| `19` | R1 2025 Sunflower |
| `18` | R2 2024 Ramsons |
| `17` | R1 2024 Quesnelia |
| `16` | R2 2023 Poppy |

Descends to `1` (Q1 2019). Confirm with `GET /index.php?/api/v2/get_case_fields` — option IDs shift as releases are added.

## Test Group IDs

| ID | Group |
|---|---|
| `1` | Smoke |
| `2` | Critical Path |
| `3` | Extended |
| `4` | Obsolete |
| `5` | Draft |
| `6` | Backend |
| `7` | Edge Cases |

## Notes

- ⚠️ **The release threshold expires.** It must name the release currently under test, so it needs bumping every release — `20` was set while Trillium was current, but `21` (Umbrellaleaf) is now the latest. Confirm it before every run: too low means already-shipped cases get edited in place with no archive copy. Nothing detects a stale value automatically.
- Section `19563` (Items) held 104 cases as of 2026-08-19, releases distributed `{20: 86, 19: 5, 18: 1, 17: 3, 16: 7, 21: 2}` — a threshold of `20` archives 16 of them.
- The archive section `65470` is large and slow to fetch. Paginate and expect timeouts on a single unbounded request.