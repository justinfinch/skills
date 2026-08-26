---
okf_version: "0.2"
---

# Concepts

* [Backstopping tenant isolation in the database](concepts/rls-tenant-backstop.md) - Keep application-level tenant filters as the first line and add row-level policies keyed on a per-transaction session variable, so a query that forgets its filter returns nothing rather than another tenant's rows.
* [Composing authorization as strictly-narrowing gates](concepts/narrowing-authorization-gates.md) - Compose the authority surfaces above the tenant boundary as gates that each narrow the last, evaluate them in one place, and resolve the containment set once per request rather than once per row.
