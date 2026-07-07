---
name: testrail-bug-report
description: 'Generate Jira-ready bug reports from failed FOLIO test cases. Takes TestRail test case ID, investigates failure context, and creates structured bug report with Title, Description, Environment, Steps to Reproduce, Expected Result, and Actual Result. Optionally uses Chrome DevTools MCP to investigate live application behavior.'
argument-hint: 'Test case ID (e.g., C389500) and optional failure details'
---

# TestRail Bug Report Generator

This skill generates comprehensive, Jira-ready bug reports from failed test cases in TestRail for FOLIO application testing. It extracts test case details, determines environment configuration, and formats a structured bug report ready for copy-paste into Jira.

## When to Use

- Test execution failed and needs bug reporting to Jira
- Need to document and report application defects
- Want consistent, well-structured bug reports
- Need to investigate failure before reporting
- User provides test case ID like "C389500" and mentions bug report

## Prerequisites

- TestRail MCP server configured and operational
- Test case ID from TestRail (e.g., C389500)
- Access to `cypress.config.js` for environment details
- (Optional) Chrome DevTools MCP server for live investigation when failure details are insufficient

## Procedure

### Step 1: Retrieve Test Case Details

Fetch the complete test case information from TestRail:

```javascript
mcp_testrail_getCase({ caseId: 389500 }) // Use numeric ID without 'C' prefix
```

**Extract and Note:**
- **Title**: `title` field - will be used for bug report title
- **Preconditions**: `custom_preconds` field - context needed before test execution
- **Test Steps**: `custom_steps_separated` field - array of step objects with `content` and `expected`
- **Automation Status**: `custom_automation_status` - confirm test is automated
- **Test Section**: `section_id` - helps identify feature area
- **Attachments**: Check if test references attached files (MARC records, screenshots, etc.)

**Decision Point:**
- ✅ **Test case retrieved successfully**: Continue to Step 2
- ❌ **Test case not found**: Verify test case ID format and existence
- ⚠️ **Test case not automated**: Clarify if manual test needs bug report

### Step 2: Determine Environment

Extract the environment URL from Cypress configuration:

```javascript
// Read cypress.config.js and find baseUrl
// Default: 'https://folio-etesting-cypress-diku.ci.folio.org'
```

**Search in:**
1. `cypress.config.js` - look for `baseUrl` property
2. Check if user specified a different environment in the request
3. Check for environment-specific config files (e.g., `cypress.config.BF.R.Eureka.js`)

**Environment Format:**
- Include full URL with tenant if applicable
- Example: `https://folio-etesting-cypress-diku.ci.folio.org (diku tenant)`

**Decision Point:**
- ✅ **BaseUrl found**: Use that environment
- ⚠️ **User specified different environment**: Use user-provided value
- ⚠️ **Multiple configs exist**: Ask user which environment was used

### Step 3: Analyze Failure Context

Understand the failure by reviewing available information:

**From User Input:**
- Failure description or error messages
- Screenshots or logs mentioned
- Specific behavior observed

**From Test Case:**
- Which step failed (if known)
- Expected vs actual behavior from test steps
- Any special preconditions or setup

**Decision Point:**
- ✅ **User provided detailed failure info**: Use directly in bug report, skip to Step 5
- 🔍 **Insufficient or unclear failure details**: Proceed to Step 4 for Chrome DevTools investigation
- ⏭️ **Sufficient context gathered**: Skip to Step 5

### Step 4: (Optional) Live Investigation with Chrome DevTools

**Use this step ONLY when failure details are insufficient or unclear.**

If user provided vague or missing failure information, investigate using Chrome DevTools MCP:

**Prerequisites:**
- Chrome DevTools MCP server configured
- Test credentials available in TestRail test case preconditions or notes
- Understanding of test flow from Step 1

**Investigation Process:**

1. **Open new browser page:**
```javascript
mcp_chrome-devtoo_new_page()
```

2. **Navigate to environment:**
```javascript
mcp_chrome-devtoo_navigate_page({ url: "<baseUrl from Step 2>" })
```

3. **Login:**
   - Get credentials from test case `custom_preconds` field or TestRail project settings
   - Typical FOLIO credentials: Look for "Login as user with permissions..." in test steps
   - Use TestRail MCP to retrieve test case details if credentials not visible
   - Use `mcp_chrome-devtoo_fill` and `mcp_chrome-devtoo_click` for login flow

4. **Follow test steps:**
   - Execute each step from `custom_steps_separated`
   - Use `mcp_chrome-devtoo_take_snapshot` to capture page state
   - Use `mcp_chrome-devtoo_click`, `mcp_chrome-devtoo_fill`, `mcp_chrome-devtoo_type_text` for interactions
   - Use `mcp_chrome-devtoo_wait_for` if elements load asynchronously

5. **Capture failure:**
   - Take screenshot at failure point: `mcp_chrome-devtoo_take_screenshot`
   - Check console errors: `mcp_chrome-devtoo_list_console_messages`
   - Check network issues: `mcp_chrome-devtoo_list_network_requests`
   - Evaluate JavaScript state: `mcp_chrome-devtoo_evaluate_script`

6. **Document observations:**
   - Exact error messages displayed
   - UI elements that didn't behave correctly
   - Network errors or API failures
   - Console warnings/errors

**Decision Point:**
- ✅ **Failure reproduced**: Document exact behavior for Actual Result
- ⚠️ **Cannot reproduce**: Note as "intermittent issue" in bug report
- ❌ **Investigation blocked**: Document blockers and use available information

### Step 5: Construct Bug Report

Create Jira-ready bug report with required sections:

#### **Title Format:**
`[Module/Feature] Brief description of defect`

**Rules:**
- Include feature area/module from user input or context (e.g., `[MARC Bibliographic]`, `[Inventory]`, `[Circulation]`)
- If user doesn't specify module, ask them to identify it based on test case context
- Use clear, concise description (max 100 characters)
- Focus on what's broken, not test case name

**Examples:**
- `[MARC Bibliographic] Unable to save new field when scope is local`
- `[Inventory] Holdings record not displaying after creation`
- `[Circulation] Check-in fails for items with pending requests`

#### **Description:**
Brief context about the defect:
```
Brief summary of what's broken and impact on functionality.
Related test case: C<TestCaseId>
```

#### **Environment:**
```
URL: <baseUrl from Step 2>
Browser: Chrome (browser version not critical)
Date Tested: <current date>
Test Case: C<TestCaseId>
```

#### **Steps to Reproduce:**
Extract from test case `custom_steps_separated`, formatted as numbered list:
```
Preconditions:
- <Each line from custom_preconds>

Steps:
1. <First step from custom_steps_separated[0].content>
2. <Second step from custom_steps_separated[1].content>
3. <Continue for all steps>
```

**Formatting Rules:**
- Remove HTML tags from TestRail content
- Convert markdown formatting if needed
- Number steps sequentially
- Include preconditions before steps
- Stop at the failing step if known

#### **Expected Result:**
Extract from the failing step's `expected` field or final step:
```
<Expected behavior from custom_steps_separated[failingStepIndex].expected>
```

If multiple steps, combine relevant expected results.

#### **Actual Result:**
Document observed behavior:
```
<Description of actual behavior>
<Error messages if any>
<Evidence reference (screenshots/logs) if provided by user>
```

**Sources:**
- User-provided failure description (primary source)
- Chrome DevTools investigation findings (if Step 4 was executed)
- Error messages from console/network
- Reference to Cypress screenshots or logs if user mentions their location

### Step 6: Format for Jira

Present the complete bug report as formatted text ready for copy-paste:

```
---
**Copy to Jira:**

**Title:**
[Module] Brief description

**Description:**
Brief summary of defect.
Related test case: C389500

**Environment:**
URL: https://folio-etesting-cypress-diku.ci.folio.org
Browser: Chrome
Date Tested: March 30, 2026
Test Case: C389500

**Steps to Reproduce:**

Preconditions:
- User has permission X
- Data Y exists

Steps:
1. Navigate to module Z
2. Click on button A
3. Enter value B in field C
4. Submit the form

**Expected Result:**
The system should save the record and display success message.

**Actual Result:**
The system displays error "Invalid field configuration" and does not save the record.
Console shows error: "Cannot read property 'id' of undefined"

---
```

**Additional Notes Section (Optional):**
- Link to test execution results
- Link to TestRail test case
- Attachments or screenshots reference
- Any workarounds discovered

### Step 7: Validation & Delivery

Review the bug report for completeness:

**Checklist:**
- ✅ Title is clear and includes module/feature
- ✅ Environment includes URL and browser
- ✅ Steps are reproducible by someone else
- ✅ Expected result is clear and specific
- ✅ Actual result includes error messages and evidence
- ✅ Test case ID is referenced
- ✅ No sensitive credentials included
- ✅ Formatting is clean (no HTML artifacts)

**Presentation:**
1. Display the formatted bug report
2. Offer to adjust any section if user requests
3. Provide the text in a code block for easy copy-paste
4. Ask if user needs additional investigation or details

## Error Handling

### Scenario: Test Case Not Found in TestRail

**Response:**
```
Unable to retrieve test case C<TestId> from TestRail. Please verify:
- Test case ID is correct (numeric ID without 'C' prefix: <numericId>)
- TestRail MCP server is connected
- You have access to this test case

Would you like to provide failure details manually for bug report creation?
```

### Scenario: No Failure Details Provided

**Response:**
```
I found test case C<TestId>: "<TestTitle>"

To create a comprehensive bug report, I need information about the failure:
- What step failed or what unexpected behavior occurred?
- Any error messages displayed?
- Do you want me to investigate the application live using Chrome DevTools?
```

### Scenario: Chrome DevTools Investigation Blocked

**Response:**
```
Unable to complete live investigation due to:
<reason: no credentials, page not loading, etc.>

I'll create bug report based on test case information. You can:
1. Provide failure details directly
2. Add screenshots/logs after creating the Jira ticket
3. Manually reproduce to gather additional evidence
```

### Scenario: Environment Config Not Found

**Response:**
```
Warning: Could not determine environment from cypress.config.js
Using default: https://folio-etesting-cypress-diku.ci.folio.org

Is this correct, or should I use a different environment URL?
```

## Best Practices

### Title Consistency
- Use module names that match FOLIO's project structure
- Keep titles under 100 characters
- Avoid test case numbers in title (include in Description instead)

### Steps Clarity
- Write steps as if for someone unfamiliar with the test
- Include navigation details ("from Settings > Inventory")
- Specify exact field names and button labels
- Note any timing considerations ("wait for record to load")

### Evidence Collection
- Reference screenshots/logs if available
- Include exact error message text
- Note console errors when relevant
- Capture network failure status codes

### Sensitive Information
- **Never include** passwords or API keys
- Generalize credentials: "Login with valid user credentials"
- Redact tenant-specific data if needed
- Use test data identifiers: "user created in preconditions"

## Integration with Other Skills

- **testrail-marc-attachments**: If test case references MARC file attachments, use this skill to understand test prerequisites. Mention attached files in bug report preconditions if relevant to the failure.
- **test-review-agent**: If uncertain whether failure is application bug or test issue, suggest reviewing the test implementation first

## Example Workflow

**User Request:** "Create bug report for C389500, test failed at step 3"

**Execution:**
1. Retrieve C389500 from TestRail → "Create local MARC Bibliographic field"
2. Extract baseUrl from cypress.config.js → `https://folio-etesting-cypress-diku.ci.folio.org`
3. Build Steps to Reproduce from test case steps 1-3
4. Expected Result from step 3's expected field
5. Actual Result from user: "test failed at step 3" + ask for details
6. Format complete bug report
7. Present for copy-paste to Jira

**Output:**
```
**Copy to Jira:**

**Title:**
[MARC Bibliographic] Unable to save local field with scope "local"

**Description:**
System fails to persist MARC field configuration when scope is set to "local".
Related test case: C389500
...
```

## Skill Outputs

This skill produces:
1. **Formatted bug report text** - Ready for Jira copy-paste
2. **Investigation findings** - If Chrome DevTools was used
3. **Validation report** - Checklist confirmation
4. **Recommendations** - Suggestions for additional evidence or investigation

## Trigger Prompts Examples

- "Create bug report for C389500"
- "Generate Jira bug from test case C412345, it failed at login step"
- "I need to report bug for failed test C399999, can you investigate it?"
- "Bug report for C389500 - error saving field"
- "Test C412000 failed, help me write bug report for Jira"
