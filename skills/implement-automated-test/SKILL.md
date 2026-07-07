---
name: implement-automated-test
description: "Use this skill whenever generating, editing, or reviewing Cypress E2E tests for the FOLIO library management system UI. Triggers include: any mention of 'FOLIO', 'Stripes', 'Cypress test', 'cy.js', 'page object', 'interactor', 'test fragment', or FOLIO module names (Inventory, Orders, Organizations, etc.). Also use when creating test spec files, support fragments, permission assignments, or test data setup/teardown logic. Do NOT use for unit tests, backend API-only tests, non-FOLIO projects, or general Cypress tasks unrelated to the FOLIO Stripes framework."
---

# FOLIO Stripes — Cypress E2E Test Generation

## Overview

FOLIO Stripes Testing is a Cypress-based E2E framework for the FOLIO library management system. Tests follow the **page object / fragment** pattern, use `@interactors/html` component abstractions, and combine API-driven test data setup with UI validation.

## Quick Reference

| Task | Approach |
|------|----------|
| Create a new test | New `.cy.js` spec file per test case |
| Reuse UI interactions | Import/extend fragments from `cypress/support/fragments/` |
| Interact with DOM | Prefer interactors over raw selectors |
| Set up test data | API calls in `before()` hook via `cy.getAdminToken()` |
| Clean up test data | API deletions in `after()` hook |
| Assign permissions | `cy.createTempUser([Permissions.xyz.gui])` |

---

## Project Structure

```
cypress/
  e2e/                          # Test specs by FOLIO module
  support/
    fragments/                  # Page objects / UI helpers
    dictionary/
      permissions.js            # Centralized permission definitions
    constants.js                # Shared constants and data structures
interactors/                    # Component-level DOM abstractions
```

---

## Test File Creation — Required Checklist

1. **One spec file per test case** — never bundle unrelated tests in a single file.
2. **File naming**: `descriptive-test-name.cy.js` — lowercase, hyphenated.
3. **File location**: mirror the FOLIO module hierarchy, e.g. `cypress/e2e/inventory/settings/`.
4. **Test ID in `it` name**: include `C######` identifier in the test description string.
5. **Tags attribute** — every `it` block must have exactly 3 tag components:

```javascript
it('C627455 Verify something works', { tags: ['extendedPath', 'spitfire', 'C627455'] }, () => { ... });
```

| Tag position | Values |
|---|---|
| Test group | `criticalPath`, `smoke`, `extendedPath`; append `ECS` for consortia: `criticalPathECS` |
| Dev team | lowercase team name: `spitfire`, `thunderjet`, `eureka`, etc. |
| Test ID | exact identifier: `C######` |

6. **Unique test data prefix**: `AT_C######_Description_${getRandomPostfix()}`.

---

## Describe Block Hierarchy

Map the provided test case hierarchy directly to nested `describe` blocks:

```
"Inventory › Settings › Call number browse"
```

becomes:

```javascript
describe('Inventory', () => {
  describe('Settings', () => {
    describe('Call number browse', () => {
      it('C##### Test name', { tags: [...] }, () => { ... });
    });
  });
});
```

If no hierarchy is specified, mirror the structure of the most similar existing test.

---

## Standard Test Template

```javascript
import permissions from '../../../support/dictionary/permissions';
import TopMenu from '../../../support/fragments/topMenu';
import ModulePage from '../../../support/fragments/moduleName/modulePage';
import { getRandomPostfix } from '../../../support/utils/stringTools';

describe('Module', () => {
  describe('Feature Area', () => {
    describe('Specific Function', () => {
      const randomPostfix = getRandomPostfix();
      const testData = {
        name: `AT_C######_Description_${randomPostfix}`,
      };
      let user;

      before('Create test data', () => {
        cy.getAdminToken().then(() => {
          // Create entities via API
        });

        cy.createTempUser([
          permissions.somePermission.gui,
        ]).then((userProperties) => {
          user = userProperties;
          cy.login(user.username, user.password, {
            path: TopMenu.someModulePath,
            waiter: ModulePage.waitContentLoading,
          });
        });
      });

      after('Delete test data', () => {
        cy.getAdminToken().then(() => {
          // Delete entities via API
        });
      });

      it('C###### Test description', { tags: ['extendedPath', 'teamName', 'C######'] }, () => {
        // UI interactions and assertions
      });
    });
  });
});
```

---

## Interactors — Preferred Over Raw Selectors

Always prefer interactors. Only fall back to raw Cypress selectors when no interactor exists.

```javascript
// ✅ Preferred
cy.do(Button('Save').click());
cy.expect(TextField('Name').has({ value: 'test' }));
cy.do(Select('Status').choose('Active'));

// ❌ Avoid unless necessary
cy.get('[data-testid="save-button"]').click();
```

**Before writing a new selector**, search existing fragments:
- `grep_search("functionName", { includePattern: "support/fragments/**" })`
- `semantic_search("description of the UI action you need")`

---

## Fragment Architecture

Fragments are the page object layer. They expose named methods for navigation, interaction, and assertion — never raw selectors.

```javascript
// support/fragments/moduleName/subModule.js
const SubModule = {
  waitLoading: () => cy.expect(/* loading indicator gone */),
  openForm: () => cy.do(Button('New').click()),
  fillName: (value) => cy.do(TextField('Name').fillIn(value)),
  save: () => cy.do(Button('Save').click()),
  verifyRecordExists: (name) => cy.expect(MultiColumnListCell(name).exists()),
};

export default SubModule;
```

**Always reuse existing fragment methods before creating new ones.**

---

## Permissions

- Import from `support/dictionary/permissions.js`
- Always use `.gui` suffix for UI-level permissions

```javascript
import permissions from '../../../support/dictionary/permissions';

cy.createTempUser([
  permissions.inventoryAll.gui,
  permissions.uiOrdersView.gui,
]);
```

For **consortia (ECS)** tests, permissions may need to be assigned per tenant.

---

## Environment Variants

### ECS / Consortia
- Multi-tenant tests with affiliation switching
- Tags use the `ECS` suffix: `criticalPathECS`
- Permissions assigned per tenant

### Eureka
- Uses **authorization roles** instead of permission sets
- Uses **capability sets / capabilities** instead of permissions
- Detect with `Cypress.env('eureka')`

```javascript
if (Cypress.env('eureka')) {
  // Eureka-specific setup
}
```

---

## Common Patterns

### Search Before Writing

Before implementing anything:
1. `semantic_search("description of scenario")` — find similar tests
2. `grep_search("FragmentName", { includePattern: "support/fragments/**" })` — find page objects
3. Check `support/dictionary/permissions.js` — verify permissions exist
4. Check `support/constants.js` — find reusable data structures

### Timing

- **Never** use bare `cy.wait(ms)` for UI stability — use fragment `waitLoading()` methods
- Default interactor timeout is 50 s globally; adjust only if a specific step genuinely requires it

### Unique Data

```javascript
import { getRandomPostfix } from '../../../support/utils/stringTools';
const randomPostfix = getRandomPostfix();
const itemName = `AT_C123456_Item_${randomPostfix}`;
```

### Cleanup

Always delete test data in `after()` to prevent test pollution across runs.

---

## Critical Rules

- **One spec file per test case** — no exceptions unless explicitly instructed
- **Never skip `after()` cleanup** — always delete created entities via API
- **Never use raw selectors when a fragment or interactor exists** — search first
- **Always include all 3 tag components** — group, team, test ID
- **Always prefix test data** with `AT_C######_` + postfix for uniqueness
- **ECS tests** need permissions assigned per tenant, not globally
- **Eureka tests** use capability sets, not permission sets — check `Cypress.env('eureka')`
