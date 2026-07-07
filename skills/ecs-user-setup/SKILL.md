---
name: ecs-user-setup
description: Expert guide for setting up users in Enhanced Consortia Support (ECS) tests. Use when generating or reviewing Cypress tests where ecs_enabled is true in TestRail, or when user mentions consortia/ECS/multi-tenant tests.
---

## When to Use This Skill

Invoke this skill when:
- TestRail test case has `ecs_enabled: true`
- User mentions "consortia test", "ECS test", or "multi-tenant test"
- Test involves multiple tenants (Central, College, University)
- Test requires affiliation switching or cross-tenant operations
- Reviewing/debugging user creation/deletion in consortia tests

**DO NOT use this skill for regular (non-ECS) tests.**

## Core Principles

### Principle 0: TestRail Preconditions Are Law
**ALWAYS create users in the tenant specified by TestRail preconditions.**

- TestRail says "User A has been created in member-1 tenant" → Create in College tenant
- TestRail says "User B has been created in central tenant" → Create in Central tenant
- **ECS rules supplement TestRail requirements - they NEVER override them**

### Principle 1: User Creation Tenant Context
Users must be created in the exact tenant specified by TestRail preconditions.

**Implementation:**
```javascript
// For member-1 tenant (College)
cy.setTenant(Affiliations.College);
cy.createTempUser([permissions_for_member1]).then((userProperties) => {
  userA = userProperties;
  // Continue setup...
});

// For central tenant (default)
cy.resetTenant(); // Central is default
cy.createTempUser([permissions_for_central]).then((userProperties) => {
  userB = userProperties;
  // Continue setup...
});
```

**Key Constants:**
- `Affiliations.College` = member-1 tenant
- `Affiliations.University` = member-2 tenant
- `cy.resetTenant()` = Central (Consortia) tenant (default)

### Principle 2: Login Tenant Context (Primary Affiliation)
**Users automatically log into their PRIMARY AFFILIATION - the tenant where they were created.**

**CRITICAL FOR TEST DESIGN**: If a test needs to work in a specific tenant from the start (without UI affiliation switching), **create the user in that tenant**.

**Primary Affiliation Rules:**
- The tenant where a user is created becomes their **primary affiliation**
- UI login automatically opens the primary affiliation tenant
- To avoid affiliation switching in tests, create users in the tenant where they'll primarily work

**Design Pattern:**
```javascript
// ✅ GOOD: User needs to work in College tenant - create in College
cy.setTenant(Affiliations.College);
cy.createTempUser([permissions]).then((userProperties) => {
  userA = userProperties;
  // User A's primary affiliation = College
  // Login will open College tenant directly
});

// ❌ BAD: User needs College but created in Central - requires switch
cy.resetTenant(); // Central
cy.createTempUser([permissions]).then((userProperties) => {
  userA = userProperties;
  // User A's primary affiliation = Central
  // Login opens Central, must switch to College in UI
});
```

**When Affiliation Switch IS Needed:**

If TestRail requires login to a different tenant than primary affiliation:
1. User logs in (automatically to creation tenant = primary affiliation)
2. User must **switch affiliation** in UI using `ConsortiumManager.switchActiveAffiliation()`

**Example:**
```javascript
// User created in College (primary), needs to work in Central
cy.resetTenant();
cy.login(userA.username, userA.password); // Logs into College (primary affiliation)

// Switch to Central tenant in UI
ConsortiumManager.switchActiveAffiliation(tenantNames.college, tenantNames.central);
```

**Tenant Name Constants:**
- `tenantNames.central` = "Consortia"
- `tenantNames.college` = "College"
- `tenantNames.university` = "University"

### Principle 3: User Deletion Tenant Context
**Always delete users from the same tenant they were originally created in.**

```javascript
after('Delete test data', () => {
  cy.getAdminToken();
  
  // User A was created in College
  cy.setTenant(Affiliations.College);
  Users.deleteViaApi(userA.userId);
  
  // User B was created in Central
  cy.resetTenant();
  Users.deleteViaApi(userB.userId);
});
```

### Principle 4: Automatic Central Affiliation
**Users created by admin automatically get Central (Consortia) affiliation.**

- **NEVER manually assign Central affiliation** - it's automatic
- Only manually assign member tenant affiliations (College, University)
- Use `cy.assignAffiliationToUser()` for member affiliations only

```javascript
// BAD - Don't do this:
cy.assignAffiliationToUser(Affiliations.Consortia, userA.userId); // WRONG!

// GOOD - Only assign member affiliations:
cy.assignAffiliationToUser(Affiliations.College, userA.userId);
cy.assignAffiliationToUser(Affiliations.University, userA.userId);
```

## Complete Implementation Pattern

### Standard ECS User Setup

```javascript
describe('ECS Test Example', () => {
  const testData = {};
  let userA;
  let userB;

  before('Create test data', () => {
    cy.getAdminToken();
    
    // TestRail: "User A has been created in member-1 tenant with permissions X, Y"
    // IMPORTANT: Create in member-1 because User A's primary affiliation = College
    // This means User A will log into College tenant automatically
    cy.setTenant(Affiliations.College); // Create in member-1
    cy.createTempUser([
      Permissions.inventoryAll.gui,
      Permissions.uiQuickMarcQuickMarcBibliographicEditorAll.gui,
    ]).then((userProperties) => {
      userA = userProperties;
      
      // Assign Central tenant permissions (Central affiliation is automatic)
      cy.resetTenant();
      cy.assignPermissionsToExistingUser(userA.userId, [
        Permissions.consortiaSettingsConsortiumManagerView.gui,
      ]);
      
      // Assign additional member affiliations if needed
      cy.assignAffiliationToUser(Affiliations.University, userA.userId);
    });
    
    // TestRail: "User B has been created in central tenant with permissions Z"
    // IMPORTANT: Create in Central because User B's primary affiliation = Central
    // This means User B will log into Central tenant automatically
    cy.resetTenant(); // Create in Central (default)
    cy.createTempUser([
      Permissions.settingsUsersView.gui,
    ]).then((userBProperties) => {
      userB = userBProperties;
      // User B automatically has Central affiliation
      // Assign member affiliations if TestRail specifies them
      cy.assignAffiliationToUser(Affiliations.College, userB.userId);
    });
  });

  it('C123456: Test requiring affiliation switch', {
    tags: ['extendedPathECS', 'spitfire', 'C123456']
  }, () => {
    // TestRail: "User A logs in and switches to Central tenant"
    cy.resetTenant();
    cy.login(userA.username, userA.password, {
      path: TopMenu.inventoryPath,
      waiter: InventoryInstances.waitContentLoading,
    });
    
    // User logged into College (where created), switch to Central
    ConsortiumManager.switchActiveAffiliation(tenantNames.college, tenantNames.central);
    
    // Now working in Central tenant
    // ... test steps ...
  });

  after('Delete test data', () => {
    cy.getAdminToken();
    
    // Delete from original creation tenants
    cy.setTenant(Affiliations.College); // Where User A was created
    Users.deleteViaApi(userA.userId);
    
    cy.resetTenant(); // Where User B was created (Central)
    Users.deleteViaApi(userB.userId);
  });
});
```

### Primary Affiliation Design Patterns

**Pattern 1: Test Works in User's Primary Affiliation (No Switch Needed)**

When test needs to work in Member tenant from the start:
```javascript
before('Create test data', () => {
  cy.getAdminToken();
  
  // Create user in College tenant - primary affiliation = College
  cy.setTenant(Affiliations.College);
  cy.createTempUser([permissions_for_college]).then((userProperties) => {
    testUser = userProperties;
    
    // Assign Central permissions if needed (Central affiliation is automatic)
    cy.resetTenant();
    cy.assignPermissionsToExistingUser(testUser.userId, [permissions_for_central]);
  });
});

it('Test in College tenant', () => {
  // User logs directly into College tenant (primary affiliation)
  cy.setTenant(Affiliations.College);
  cy.login(testUser.username, testUser.password, {
    path: TopMenu.inventoryPath,
    waiter: InventoryInstances.waitContentLoading,
  });
  
  // Already in College tenant - no affiliation switch needed
  ConsortiumManager.checkCurrentTenantInTopMenu(tenantNames.college);
  // ... test steps in College tenant ...
});
```

**Pattern 2: Test Requires Affiliation Switch**

When test needs to switch between tenants:
```javascript
before('Create test data', () => {
  cy.getAdminToken();
  
  // Create user in College tenant - primary affiliation = College
  cy.setTenant(Affiliations.College);
  cy.createTempUser([permissions_for_college]).then((userProperties) => {
    testUser = userProperties;
    
    // Assign Central permissions for switch
    cy.resetTenant();
    cy.assignPermissionsToExistingUser(testUser.userId, [permissions_for_central]);
  });
});

it('Test switches from College to Central', () => {
  cy.resetTenant();
  cy.login(testUser.username, testUser.password, {
    path: TopMenu.inventoryPath,
    waiter: InventoryInstances.waitContentLoading,
  });
  
  // User logged into College (primary affiliation)
  // Switch to Central tenant in UI
  ConsortiumManager.switchActiveAffiliation(tenantNames.college, tenantNames.central);
  ConsortiumManager.checkCurrentTenantInTopMenu(tenantNames.central);
  // ... test steps in Central tenant ...
});
```

### ECS with Capabilities (Eureka Platform)

```javascript
// For Eureka tests using capabilities instead of permissions
before('Create test data', () => {
  cy.getAdminToken();
  
  const capabsToAssign = [Capabilities.settingsEnabled];
  const capabSetsToAssign = [
    CapabilitySets.uiAuthorizationRolesSettingsView,
  ];
  
  // TestRail: "User has been created in member-1 tenant"
  cy.setTenant(Affiliations.College);
  cy.createTempUser([]).then((userProperties) => {
    testData.user = userProperties;
    
    // Assign capabilities in member tenant
    cy.assignCapabilitiesToExistingUser(
      testData.user.userId,
      capabsToAssign,
      capabSetsToAssign,
    );
    
    // Assign Central tenant capabilities (Central affiliation is automatic)
    cy.resetTenant();
    cy.assignCapabilitiesToExistingUser(
      testData.user.userId,
      [Capabilities.settingsEnabled],
      [CapabilitySets.uiConsortiaSettingsView],
    );
  });
});
```

## Common Patterns & Troubleshooting

### Pattern: User Works in Member Tenant Only
```javascript
// TestRail: "User created in member-1, works in member-1"
cy.setTenant(Affiliations.College);
cy.createTempUser([permissions]).then((userProperties) => {
  testData.user = userProperties;
  
  cy.login(testData.user.username, testData.user.password); // Logs into College
  // No affiliation switch needed - already in correct tenant
});
```

### Pattern: User Created in Central, Works in Central
```javascript
// TestRail: "User created in central, works in central"
cy.resetTenant(); // Central is default
cy.createTempUser([permissions]).then((userProperties) => {
  testData.user = userProperties;
  
  cy.login(testData.user.username, testData.user.password); // Logs into Central
  // No affiliation switch needed
});
```

### Pattern: Multiple Users, Different Tenants
```javascript
// Complex multi-user, multi-tenant scenario
let centralUser;
let collegeUser;
let universityUser;

cy.resetTenant();
cy.createTempUser([centralPermissions]).then((user) => {
  centralUser = user;
});

cy.setTenant(Affiliations.College);
cy.createTempUser([collegePermissions]).then((user) => {
  collegeUser = user;
});

cy.setTenant(Affiliations.University);
cy.createTempUser([universityPermissions]).then((user) => {
  universityUser = user;
});

// Delete each from their creation tenant
after('Delete test data', () => {
  cy.getAdminToken();
  cy.resetTenant();
  Users.deleteViaApi(centralUser.userId);
  cy.setTenant(Affiliations.College);
  Users.deleteViaApi(collegeUser.userId);
  cy.setTenant(Affiliations.University);
  Users.deleteViaApi(universityUser.userId);
});
```

### Troubleshooting: User Can't See Data in Target Tenant
**Problem:** User switches to Central but can't see expected data.

**Solution:** Ensure user has:
1. Correct permissions assigned in target tenant
2. Correct affiliation assigned (automatic for Central, manual for members)
3. Switched affiliation in UI using `ConsortiumManager.switchActiveAffiliation()`

### Troubleshooting: User Deletion Fails
**Problem:** `Users.deleteViaApi()` fails with 404 or permission error.

**Solution:** Verify you're deleting from the correct tenant:
- Set tenant context to WHERE USER WAS CREATED
- Not where user logged in or worked

## Required Imports for ECS Tests

```javascript
import Affiliations from '../../../support/dictionary/affiliations';
import ConsortiumManager from '../../../support/fragments/consortium-manager/consortiumManager';
import { tenantNames } from '../../../support/dictionary/affiliations';
import Users from '../../../support/fragments/users/users';
import Permissions from '../../../support/dictionary/permissions';

// For Eureka capabilities approach:
import Capabilities from '../../../support/dictionary/capabilities';
import CapabilitySets from '../../../support/dictionary/capabilitySets';
```

## Decision Tree for ECS User Setup

1. **Read TestRail Preconditions** - What tenant is user created in?
2. **Set Tenant Context** - Use `cy.setTenant()` or `cy.resetTenant()`
3. **Create User** - Use `cy.createTempUser()` with tenant-specific permissions
4. **Assign Cross-Tenant Permissions** - Switch to other tenants, use `cy.assignPermissionsToExistingUser()`
5. **Assign Member Affiliations** - ONLY for College/University (NOT Central)
6. **Login** - User logs into creation tenant automatically
7. **Switch Affiliation If Needed** - Use `ConsortiumManager.switchActiveAffiliation()`
8. **Cleanup** - Delete from creation tenant in `after()` hook

## Validation Checklist

Before completing ECS test implementation, verify:

- [ ] Users created in exact tenant specified by TestRail preconditions
- [ ] Central affiliation NOT manually assigned (it's automatic)
- [ ] Member affiliations assigned when required by TestRail
- [ ] Affiliation switches implemented when TestRail specifies different login tenant
- [ ] User deletion happens in original creation tenant
- [ ] Tags include "ECS" suffix (e.g., `smokeECS`, `criticalPathECS`)
- [ ] All tenant context switches use correct methods (`cy.setTenant()`, `cy.resetTenant()`)
- [ ] Required imports present (`Affiliations`, `ConsortiumManager`, `tenantNames`)

## Key Differences: ECS vs Non-ECS Tests

| Aspect | Non-ECS Test | ECS Test |
|--------|-------------|----------|
| User Creation | Single tenant (default) | Specific tenant via `cy.setTenant()` |
| Permissions | Assigned during creation | May span multiple tenants |
| Affiliations | Not relevant | Central automatic, members manual |
| Login | Direct to application | May require affiliation switch |
| Deletion | Simple `deleteViaApi()` | Must match creation tenant |
| Tags | `smoke`, `criticalPath`, etc. | `smokeECS`, `criticalPathECS`, etc. |

## Remember

- **TestRail preconditions are the source of truth** - always follow them exactly
- **Central affiliation is automatic** - never assign it manually
- **Login tenant = creation tenant** - always, without exception
- **Delete from creation tenant** - not from where user worked
- **Member affiliations are manual** - use `cy.assignAffiliationToUser()`
- **Affiliation switch ≠ tenant context switch** - UI operation vs API operation

When in doubt, refer back to TestRail preconditions and follow them literally.
