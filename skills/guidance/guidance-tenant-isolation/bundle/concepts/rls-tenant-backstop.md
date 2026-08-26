---
type: Guidance
title: Backstopping tenant isolation in the database
description: Keep application-level tenant filters as the first line and add row-level policies keyed on a per-transaction session variable, so a query that forgets its filter returns nothing rather than another tenant's rows.
tags: [multi-tenancy, rls, postgres, security, isolation]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T15:35:34Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: postgres-rls
    resource: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
    title: PostgreSQL — Row Security Policies
---

# Backstopping tenant isolation in the database

## Technique

Every tenant-scoped table carries the tenant key. Application query filters stay
the first line of defence — but the database carries a **row-level security
policy** on each of those tables, keyed on a session variable set per
transaction:

```sql
ALTER TABLE <tenant_table> ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON <tenant_table>
  USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- once per request / per command, inside the transaction:
SELECT set_config('app.current_tenant', $1, true);
```

The point is not defence in depth as a slogan. It is that a cross-tenant read or
write becomes **structurally impossible even when an application query forgets
its `WHERE tenant_id = ?`** — the failure mode that turns a one-line omission
into a disclosure incident. The transaction-local flag on `set_config` is
deliberate — unlike bare `SET LOCAL`, which accepts only literals, `set_config`
takes a bind parameter, and the variable still dies with the transaction, so a
pooled connection cannot carry one tenant's context into the next tenant's work.

**One term, one column.** Whatever the business calls a tenant — organization,
account, workspace — pick that word and use it for the column on every table and
for the session variable. A system carrying both `tenant_id` and
`organization_id` has a mapping layer to maintain and two candidate answers to
"which one does the policy key on"; the policy must key on the column the
schema actually uses, everywhere, without translation.

**Background consumers set the tenant per unit of work.** Workers, projection
consumers and push pumps process events across all tenants, so they cannot run
under one fixed value. They set `app.current_tenant` from the message's own
metadata before touching tenant tables, and reset it per message.
`BYPASSRLS` belongs to maintenance and migration roles only — never the request
path and never the worker path.

**Two policy shapes, stated deliberately.** Domain tables are **fail-closed**:
no tenant context, no rows. Tables owned by an authentication framework often
cannot be, because the framework reads them *before* a tenant is chosen — "which
tenants does this user belong to?" is by definition a question asked without a
tenant context. Those tables get a **permissive** variant that admits the
null-context read and scopes everything else:

```sql
USING (current_setting('app.current_tenant', true) IS NULL
       OR tenant_id = current_setting('app.current_tenant', true)::uuid)
```

Write both shapes down, and write down *which tables get which*. The backstop on
those tables is real — it still scopes any query issued from inside a tenant
request — it simply cannot fail closed in the login path, where the framework's
own scoping is the isolation of record.

## Applies when

- Rows for multiple tenants share one database and one set of tables, and every
  tenant-scoped table carries the tenant key (or can, before it holds data).
- The engine supports row-level policies natively — PostgreSQL, or another
  engine with equivalent per-row predicates enforced below the application.
- Every connection path can guarantee per-transaction session state: the
  request path, the worker path, and any batch or admin path that touches tenant
  tables in the same pool.
- The application connects as a role that is **not** the owner of the tenant
  tables, or the tables are declared `FORCE ROW LEVEL SECURITY`. Owners bypass
  their own policies by default.
- The highest-severity failure the system can produce is cross-tenant
  disclosure — a hosting arrangement where one customer's data sitting in another
  customer's response is a breach rather than a bug.
- The schema is new, or small enough to retrofit. This is near-free before the
  first table exists and brutal on a populated multi-tenant database.

## Doesn't apply when

- **Isolation is already physical.** Database-per-tenant or schema-per-tenant
  puts the boundary above the row; row policies then add a predicate and a
  session-variable contract that guard a boundary the connection already
  guarantees.
- **The tenant key is not yet on every tenant-scoped table.** Fix the schema
  first. Policies on half the tables are *worse* than none, because the
  architecture diagram, the onboarding doc and the next engineer all read the
  system as covered. A partial backstop is a false negative you have institutionalized.
- **A connection pooler prevents reliable per-transaction session state.**
  Transaction-mode pooling that multiplexes statements across sessions, or a
  serverless data proxy that does not guarantee the whole unit of work runs in
  one transaction on one session, breaks the `SET LOCAL` contract. Verify it on
  your actual pooler configuration; do not infer it from the engine's docs.
- **The application must legitimately span tenants on the request path.**
  Cross-tenant marketplaces, brokered supplier access, or aggregate reporting
  that reads many tenants in one query need an explicit multi-tenant read model
  and its own authorization story. Bolting a widening exception onto the policy
  is how the backstop stops meaning anything.
- **The queries that matter don't go through the database role you can
  constrain.** Analytics replicas, BI tools with their own credentials, and
  direct exports are outside this boundary unless they are also inside it. Know
  which, and say so.

## Trade-offs

Buys a boundary that does not depend on review discipline. The property "no
query can return another tenant's rows" becomes checkable in CI — assert every
table carrying the tenant key has row security enabled and a policy — instead of
being re-established by every code review, forever. It is also the boundary a
coding agent cannot accidentally route around, because it is not in the code the
agent is writing.

Costs a convention that must be honoured on every connection path exactly once
and then never broken, an extra predicate on every tenant-table query plan
(negligible with the tenant key indexed, not free), and policies that live in
raw SQL outside whatever migration tool owns the table definitions — which means
schema tooling will not tell you when a new table shipped without one. A CI
check has to.

The security gain is paid for in operability. A missing tenant context fails in
the safe direction, and the safe direction is also the confusing one: the system
returns nothing rather than raising an authorization error. Debugging gets
worse in exchange for breaches getting impossible.

## Failure modes

- **A forgotten `SET LOCAL` presents as data loss, not as an auth error.** Under
  a fail-closed policy the query is valid, the transaction commits, and zero rows
  come back. The 3am version: a new endpoint, or a background job that acquired
  its own connection, reports "the customer's data is gone." Hours go into the
  data layer before anyone suspects the session variable. Make the absence
  loud — have the data-access layer raise when it opens a tenant transaction
  without a tenant set, rather than relying on the policy to be the first thing
  that notices.
- **Policies present, RLS ineffective, because the application owns the
  tables.** Table owners bypass their own row security unless the table is
  declared `FORCE ROW LEVEL SECURITY`, and superusers bypass it regardless. The
  policies exist, the CI check that greps for them passes, and the backstop has
  never once been exercised. The only honest test is a cross-tenant integration
  test that runs a deliberately unfiltered `SELECT` on the *real* application
  role and asserts it returns nothing.
- **Authentication tables break login under a fail-closed policy.** The
  framework's "which tenants does this user belong to?" query runs before any
  tenant context exists, matches nothing, and every login fails — usually in the
  same deploy that added the policy, and usually for everyone at once. Evidence
  shape: a production multi-tenant system had to amend its policy for exactly
  those tables to a permissive variant after a modular-auth code review found
  login broken. The trap repeats: a later contributor "fixes" the inconsistency
  by making those two policies match the domain tables, and takes down login
  again. Put the reason in a comment on the migration, not just in the decision
  record.
- **A worker leaks the previous message's tenant.** A consumer that processes
  events across tenants on one long-lived connection, and sets the variable
  rather than scoping it to the transaction, applies message N-1's tenant to
  message N when a code path skips the set — writing one tenant's projection row
  into another's. Silent, durable, and discovered by a customer. `SET LOCAL`
  inside a per-message transaction, with a reset on the error path, is the whole
  fix.
- **A new table ships without a policy.** The tenant key is copied from a
  neighbouring table, the policy is not, and nothing fails. Every subsequent
  query against that table is unbackstopped. This is the regression the CI
  fitness function exists for; without it, the gap is invisible until it is a
  disclosure.
- **`BYPASSRLS` migrates onto the hot path.** Granted for a migration, kept for
  "the one job that needs it", and eventually held by the role the API uses
  because a query was easier that way. The backstop is now decorative and
  nothing in the system reports that.
- **The unit of work spans two transactions.** A request that reads in one
  transaction and writes in another must set the variable in both. Code that
  reads correctly and writes into the void is the tell.

## Alternatives considered

- **Application-layer filters only** — wins when a single well-audited
  data-access layer genuinely owns every query, and there is no raw SQL, no
  reporting path, and no coding agent writing one-off queries. The condition is
  strict and erodes: it holds on day one of a small codebase and rarely holds
  two years later.
- **A mandatory tenant-scoped query helper plus a CI static-analysis gate** —
  lint fails any raw query against a tenant table that bypasses the repository.
  Wins as a *complement*: it catches the mistake at authoring time, where the fix
  is cheap. Loses as the primary guard, because it is defeatable at runtime and
  blind to queries built dynamically.
- **Database-per-tenant or schema-per-tenant** — wins when compliance demands
  physical separation, when tenants are few and large enough that N migrations
  are affordable, or when per-tenant backup and restore is a product
  requirement. Loses when tenants are many, the team is small, or the product
  deliberately spans tenants.
- **A dedicated authorization/policy service in front of the data** — wins when
  policy must be authored and audited independently of the application, or when
  many services share one policy. It sits above the database, so it constrains
  the services that call it and nothing else; it is not a substitute for a
  boundary below the query.
