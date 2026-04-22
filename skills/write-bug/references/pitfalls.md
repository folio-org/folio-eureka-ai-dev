# Common Pitfalls — Before / After

## Pitfall 1: Vague summary

❌ **Before**
> Orders is broken

✓ **After**
> POL "Date Received" field update does not refresh "Record last updated" timestamp

Why: names component, action, observed symptom.

---

## Pitfall 2: Compound steps

❌ **Before**
```
1. Log in, open the order, click Actions and pick Move holdings, then confirm.
```

✓ **After**
```
1. Log in to folio-etesting-snapshot as diku_admin.
2. Navigate to the Orders app.
3. Open the PO from Preconditions step 3.
4. Click Actions.
5. Select "Move holdings/items to another instance".
6. In the Confirm move dialog, click Continue.
```

Why: each step is independently verifiable and the failing step can be pinpointed.

---

## Pitfall 3: Missing preconditions

❌ **Before**
```
Steps:
1. Open an order.
2. Pay an invoice.
3. See wrong total.
```

✓ **After** — state tenant, data, roles, and exchange rate before the steps,
so the bug is reproducible without tribal knowledge.

---

## Pitfall 4: Hypothesis masquerading as the bug

❌ **Before (Actual result)**
> `CompositeOrderTotalFieldsPopulateService#getTotalAmount` doesn't call the
> conversion service, so the total is wrong.

✓ **After (Actual result)**
> "Total Expended" displays `$100.00 USD` instead of the expected `$110.00 USD`.

Move the hypothesis to _Additional information_ and label it as unverified.

---

## Pitfall 5: "Expected" without a source of truth

❌ **Before**
> Expected: it should work correctly.

✓ **After**
> Expected: "Total Expended" displays the invoice amount converted to system
> currency using the invoice's exchange rate, per the API contract in
> `mod-orders` RAML and the behavior of prior releases.

---

## Pitfall 6: Mixing multiple defects

❌ **Before**
> When moving holdings the acquisition link is missing, **and** the currency
> total is wrong, **and** the PO line audit history doesn't update.

✓ **After** — file three tickets. Cross-link them if they share a root cause.

---

## Pitfall 7: Inline noise above the fold

❌ **Before** — 300 lines of stack trace pasted between Steps and Expected,
pushing Expected / Actual below the fold.

✓ **After** — move large payloads (stack traces, query plans, JSON blobs) to
the **Additional information** section below Expected and Actual, wrapped in a
fenced code block so Jira renders it as a scrollable panel:

```markdown
**Stack trace:**

\`\`\`
java.lang.NullPointerException: ...
    at org.folio...
\`\`\`
```

---

## Pitfall 8: Secrets and PII

❌ **Before**
> curl -H "Authorization: Bearer eyJhbGciOi..." https://real-tenant.example.com/...
> User email: real.person@library.edu

✓ **After** — redact tokens, use `diku_admin` or fictional emails, strip real
tenant URLs unless required and approved for the ticket.

---

## Pitfall 9: Silent intermittent bugs

❌ **Before**
> Sometimes pieces don't load.

✓ **After**
> Pieces do not load in the Claiming app on 2 of 10 attempts against
> `sprint testing`. First request to `/orders/wrapper-pieces` times out
> at 30s; the next request succeeds in ~12s. Query plan attached.

Why: reproduction rate, environment, and timing data make it triageable.
