# Golden example — Circulation log

> Real, human-written case from TestRail suite 21 (2026), selected for verification depth. Match its depth, value precision and step shape when writing cases for this area. Use `references/examples.md` for cross-area patterns and anti-patterns.

**Why it is golden:** Cross-app, ECS-aware log case: the same cancellation events are verified in the Circulation log of the member tenant, the Central tenant and again in the member tenant, with exact Object / Circ action values.

### C1282810 — Mediated request cancellation event with Shared cancellation reason is logged correctly in Circulation log app in all tenants

Source: [C1282810](https://foliotest.testrail.io/index.php?/cases/view/1282810) · Type Functional · Priority Medium · Test Group Extended · refs MODAUD-271,MODAUD-301,MODAUD-317

```
Preconditions:
1) A **Shared **cancellation reason is created in "Consortium manager" app in Central tenant - make sure to populate all 3 text fields with different values (note them)
2) 2 Mediated requests have been created in **Secure **tenant for a patron from Secure tenant:
- Request #1 is **Item **level for an **item **from any **Member **tenant
- Request #2 is **Title **level for an **instance **having an Available item in the same **Member **tenant
3) The created requests have been **cancelled **in Secure **tenant** **-> **Shared **reason from precondition #1 is selected from "Reason for cancellation" dropdown -> "Confirm" cancellation in the modal
4) User is logged in with following permissions/capabilities assigned in **Central,** **Member **and **Secure **tenants:
- Requests: View / data - UI-Requests - view
- Circulation log: View / data - UI-Circulation-Log Log-Event - view
5) User is on **Secure **tenant

Steps:
1. Action:   - Go to "Requests" app
             - Search for the 2 requests created in precondition #2
             - Check the details page for both request #1 and #2
   Expected: For both request #1 and #2:
             - "Request status" is "Closed - Cancelled"
             - "Cancellation reason" is the Shared cancellation reason from precondition #1
2. Action:   - Go to "Circulation log" app
             - Search for records related to Request cancellation (e.g. filter by "Cancelled" in "Request" facet)
   Expected: - Circulation logs are found for both cancelled requests with "Object" = "Request" and "Circ action" = "Cancelled"
             - "Description" contains "Reason for cancellation: <shared reason from precondition #1> - text from "**Description (internal)**" field"
3. Action:   - Switch active affiliation to **Central **tenant
             - Go to "Requests" app
             - Search for the 2 requests created in precondition #2
             - Check the details page for both request #1 and #2
   Expected: For both request #1 and #2:
             - "Request status" is "Closed - Cancelled"
             - "Cancellation reason" is "DCB Cancelled."
             **Note**: behavior might change to show Shared cancellation reason from precondition #1 after MODAUD-317
4. Action:   - Go to "Circulation log" app in Central **tenant
             - Search for records related to Request cancellation (e.g. filter by "Cancelled" in "Request" facet)
   Expected: - Circulation logs are found for both cancelled requests with "Object" = "Request" and "Circ action" = "Cancelled"
             - "Description" contains "Reason for cancellation: DCB Cancelled."**
             **
             **Note**: behavior might change to show Shared cancellation reason from precondition #1 after MODAUD-317
5. Action:   - Switch active affiliation to **Member **tenant
             - Go to "Requests" app
             - Search for the 2 requests created in precondition #2
             - Check the details page for both request #1 and #2
   Expected: For both request #1 and #2:
             - "Request status" is "Closed - Cancelled"
             - "Cancellation reason" is "DCB Cancelled."
             **Note**: behavior might change to show Shared cancellation reason from precondition #1 after MODAUD-317
6. Action:   - Go to "Circulation log" app in **Member **tenant
             - Search for records related to Request cancellation (e.g. filter by "Cancelled" in "Request" facet)
   Expected: - Circulation logs are found for both cancelled requests with "Object" = "Request" and "Circ action" = "Cancelled"
             - "Description" contains "Reason for cancellation: DCB Cancelled."**
             **
             **Note**: behavior might change to show Shared cancellation reason from precondition #1 after MODAUD-317
```
