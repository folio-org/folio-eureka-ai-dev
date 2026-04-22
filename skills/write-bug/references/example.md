# Complete Example FOLIO Bug

```markdown
## Summary (Jira title)

Order expended amount is not converted to system currency when invoice uses a foreign currency

---

## Overview

When a paid invoice uses a currency different from the system/tenant currency,
the Order's "Total Expended" field shows the invoice amount with the system
currency symbol but without converting the value. This produces misleading
financial totals on orders with foreign invoices.

---

## Preconditions

1. Environment: folio-etesting-snapshot, tenant `diku`, release Sunflower bugfest build.
2. User `diku_admin` with Orders and Invoices full-access capabilities.
3. System currency = USD in Settings → Tenant → Language and localization.
4. An open PO with one POL, Ongoing = false, Receiving = Synchronized.
5. No prior invoices associated with the PO.

---

## Steps to reproduce

1. Log in to folio-etesting-snapshot as `diku_admin`.
2. Navigate to the Invoices app.
3. Click New → Create an invoice with currency = `EUR`, exchange rate = `1.10`.
4. Add an invoice line linked to the POL from Preconditions step 4, sub-total = `100 EUR`.
5. Approve the invoice.
6. Pay the invoice.
7. Navigate to the Orders app and open the PO from Preconditions step 4.
8. Open the PO line and view the "Total Expended" field in the POL third pane.

---

## Expected result

- "Total Expended" displays `$110.00 USD` (100 EUR × 1.10 exchange rate).
- Matches behavior documented in the API spec for `CompositeOrderTotalFieldsPopulateService#getTotalAmount`.

---

## Actual result

- "Total Expended" displays `$100.00 USD` — the raw invoice amount with the
  system currency symbol, **without** applying the exchange rate.
- No error toast is shown; the number is silently incorrect.

---

## Additional information

**Reproducibility:** Always (5/5 attempts)
**Environment:** folio-etesting-snapshot, tenant `diku`
**Module versions:** mod-orders 13.0.5, mod-invoice 5.10.2, ui-orders 9.1.2
**Regression source:** Not identified; present at least since Ramsons.

**Hypothesis (not verified):**
`CompositeOrderTotalFieldsPopulateService#getTotalAmount` does not call the
currency conversion service before summing invoice amounts.

**Request / response for GET /orders/composite-orders/{id}:**

\`\`\`json
{
  "id": "abc-...",
  "totalExpended": 100.00,
  "currency": "USD"
}
\`\`\`

**Attachments:** `order-expended-before.png`, `order-expended-hover.png`
(attach to Jira).

**Workaround:** Manually convert in an external spreadsheet until fixed.

**Test Cases:** C15201, C15202 (TestRail — if applicable for your team).
```

---

## Notes on why this example works

- **Summary** names the area (Order expended amount), the symptom (not converted),
  and the trigger (foreign currency invoice).
- **Preconditions** let another tester reproduce without guessing — system currency,
  user role, and record state are all specified as properties.
- **Steps** are atomic and start from login. No step combines two actions.
- **Expected** anchors to a spec reference.
- **Actual** quotes the exact displayed value and notes the absence of any error.
- **Additional information** separates verified facts from a clearly labelled
  hypothesis, includes reproducibility rate, and lists the module versions — all
  things triagers need.
