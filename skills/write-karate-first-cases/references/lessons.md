# Lessons from reviews and runs

Rules learned after the skill produced a test. Apply every entry on each run. Add new entries at the end: one rule per entry, with the source. Remove an entry only when a team rules file now states it (then point to the file).

| # | Rule | Source |
|---|---|---|
| 1 | A fund and budget used by several scenarios are not created in `Background` with `callonce uuidN`; each scenario creates its own with `call uuid`, so encumbrances from parallel scenarios do not mix | Validator finding on PR #2620 (MODORDERS-1428), Nov 2026 |
| 2 | TestRail cases are written in business language; endpoints, status codes and payloads live only in the feature | Developer feedback (Thunderjet), Nov 2026 |
| 3 | Capabilities are listed in the TestRail case as Eureka capability sets; the feature does not model them with per-case users | Developer feedback (Thunderjet), Nov 2026 |
| 4 | Read both acquisitions system prompts and the Karate Coding Standards wiki page before writing; check PR #2426 runner structure and the FAT-13426 / FAT-20199 refactorings for examples | Developer feedback (Thunderjet), Nov 2026 |
| 5 | Do not add a case or scenario for behaviour an existing Karate scenario already asserts; extend that scenario or cite it | Developer feedback (Thunderjet), Nov 2026 |
