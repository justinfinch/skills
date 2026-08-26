---
type: Guidance
title: Composing authorization as strictly-narrowing gates
description: Compose the authority surfaces above the tenant boundary as gates that each narrow the last, evaluate them in one place, and resolve the containment set once per request rather than once per row.
tags: [authorization, multi-tenancy, access-control, hierarchy]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T15:35:34Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: zanzibar
    resource: https://www.usenix.org/conference/atc19/presentation/pang
    title: Pang et al. — Zanzibar, Google's Consistent, Global Authorization System (USENIX ATC 2019)
  - id: nist-abac
    resource: https://csrc.nist.gov/pubs/sp/800/162/upd2/final
    title: NIST SP 800-162 — Guide to Attribute Based Access Control (ABAC) Definition and Considerations
  - id: owasp-authz
    resource: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
    title: OWASP — Authorization Cheat Sheet
  - id: karwin-sql-antipatterns
    resource: https://pragprog.com/titles/bksqla/sql-antipatterns/
    title: Bill Karwin — SQL Antipatterns (Naive Trees; the closure-table alternative)
  - id: postgres-recursive-cte
    resource: https://www.postgresql.org/docs/current/queries-with.html
    title: PostgreSQL — WITH Queries (Common Table Expressions), including RECURSIVE
---

# Composing authorization as strictly-narrowing gates

## Technique

Order the system's authority surfaces so that each one **strictly narrows** the
one before it, and never widens it:

```
tenant                     (the hard outer boundary, enforced below the query)
  ⊃ reachable subgraph     (which nodes of the containment structure a user can see)
     ⊃ specific grant      (what the user may do at a node they can see)
```

One evaluator answers every access question by walking the gates in order, and a
denial at any gate is final:

- `canSee(user, node)` = same tenant **∧** `node ∈ reachable(user)`
- `canDo(user, node, action)` = `canSee(user, node)` **∧** `grant(user, node, action)`

The containment structure does not need a graph database. A parent pointer per
node and a table of user-to-node grants is enough; "what can this user see"
is a recursive traversal down from each granted node:

```sql
WITH RECURSIVE reachable AS (
  SELECT node_id FROM user_node_grants WHERE user_id = :user
  UNION ALL
  SELECT c.node_id FROM nodes c JOIN reachable r ON c.parent_id = r.node_id
)
SELECT node_id FROM reachable;
```

**Resolve the reachable set once per request, into a set, and filter rows
against it.** The wrong shape asks "can they see *this* node?" per row and runs
the traversal two hundred times to render one list. Same answer, one traversal.

Two rules keep the composition honest. **Roles seed, they do not decide**: an
application role may create a user's default grants at provisioning time, but it
is not consulted at read time, or it becomes a second authority surface that can
disagree with the first. And **the authentication library's roles stay on
membership and billing** — the moment they also carry domain permissions there
are two permission systems, and a later auth-library swap drags domain
authorization with it.

This gate structure catches what a tenant-level backstop structurally cannot:
over-sharing *within* a tenant. Row-level tenant policies guarantee a user never
sees another customer's data; nothing in them notices a traversal bug that shows
a user a sibling subtree in their own tenant.

## Applies when

- Access follows a **containment structure** the business already recognizes —
  a location or asset tree, an org hierarchy, a portfolio-of-accounts — and
  users are granted at a node, inheriting what sits under it.
- **More than one permission granularity exists**: seeing a thing and acting on
  it are different questions with different answers, so there is a real second
  gate to narrow through.
- A tenant boundary already exists beneath these gates, enforced independently
  (see [Backstopping tenant isolation in the database](rls-tenant-backstop.md)).
  These gates narrow within a tenant; they are not a tenant boundary and must
  never be asked to be one — two tenants can each have a node called "Building
  A", and reachability alone will not stop a traversal from crossing between
  them.
- Authorization decisions are needed on **collections**, not just single
  resources: list endpoints, feeds and exports, where per-row evaluation shows
  up as latency.

## Doesn't apply when

- **Flat roles fully describe access.** If "admin sees everything, member sees
  their own records" is the whole model, there is no containment to narrow
  through and no second granularity. A single evaluator is then indirection in
  front of a boolean.
- **Permissions are per-resource ACL grants with no containment.** When every
  document carries its own share list and nothing is implied by position, there
  is no subgraph to resolve — the grant *is* the whole answer, and modelling it
  as a narrowing gate adds a traversal that always returns one node.
- **Some surface must legitimately widen another.** Break-glass support access,
  a regulator's read-only view, or a supplier who spans several tenants by
  design all *widen* rather than narrow. If even one of these is a requirement,
  "strictly narrowing" is false as stated, and pretending otherwise means the
  exception gets implemented as a special case nobody can reason about. Model
  those as separate, explicitly named principals with their own evaluation path,
  or move to an engine with first-class allow/deny precedence.
- **Policy must be authored or audited outside the codebase.** When a compliance
  function needs to read the policy, change it without a deploy, or be handed a
  decision log explaining why a specific access was permitted, a hand-written
  evaluator is the wrong artifact. Use a policy engine that externalizes rules
  and emits decisions.
- **The containment structure is unstable.** Nodes that move between parents
  frequently make inherited access change under users without any grant
  changing. That is a legitimate model, but it needs an explicit story for
  in-flight sessions and cached sets; if there isn't one, inheritance is
  surprising rather than convenient.

## Trade-offs

Buys one auditable place where domain access is decided. `canSee` and `canDo`
can be unit-tested against a synthetic hierarchy, reviewed as a unit, and
followed by a contributor — or a coding agent — without inventing a parallel
path. Grants stay small: granting a user at one node covers everything beneath
it forever, including nodes that do not exist yet.

Costs an invariant every engineer has to internalize, and a discipline no
compiler enforces. "Resolve once per request" is a review-and-test rule, not a
build gate. Inherited access is also harder to explain to a user than an
explicit list — "why can they see that?" is answered by a traversal, not by a
row.

It also costs a performance cliff you must name in advance. A recursive
traversal is microseconds on a shallow tree and a problem on a deep or wide one.
Pick the trigger before you need it — a latency budget, or the traversal
appearing in the slow-query log — and migrate to a precomputed closure table of
`(ancestor, descendant)` pairs refreshed on structure change. Building the
closure table before the trigger fires is a refresh path to maintain with no load
to justify it.

## Failure modes

- **A traversal bug over-shares inside the tenant, and nothing notices.** The
  user is granted at one subtree and sees a sibling — a join condition inverted,
  a `UNION` that lost its parent constraint, a fixed depth limit that quietly
  became "everything". Every tenant-level control passes, because the disclosure
  never crosses a tenant. Only a test catches it: build a small hierarchy, grant
  at one subtree, assert the user sees exactly that subtree and nothing sideways.
  Make it a per-PR check, not a one-off.
- **Queries that bypass the evaluator "because they know the answer".** A report,
  an export, a new list endpoint written under deadline — each embeds the filter
  inline instead of calling the evaluator, each is correct on the day it is
  written, and none of them changes when the gate logic does. Months later the
  evaluator has a fix that three call sites never received. The tell is a
  hierarchy join appearing anywhere outside the evaluator.
- **The evaluator called per row.** Correct, and quadratic. A list page that was
  fast with ten items times out at two hundred, and the fix looks like "add
  caching" rather than "hoist the traversal". The symptom arrives with a
  customer whose portfolio grew, not with a deploy.
- **Denial is indistinguishable from absence.** Filtered lists return fewer rows
  with no signal, so a mis-scoped grant reads to the user as missing data and to
  support as a bug in the feature. Log the denials even when the response cannot
  mention them.
- **The role that was supposed to only seed starts being consulted.** Someone
  adds `if (user.role === 'admin') return true` at the top of the evaluator to
  fix an urgent access problem. Now there are two authority surfaces, one of
  which widens, and the composition rule is dead without anyone editing the
  document that describes it.
- **A stale reachable set inside a long-running request or a cached session.**
  Resolved once per request is correct; resolved once per session is a
  revocation that does not take effect. Bound the set's lifetime to the request,
  and say what happens to grants revoked mid-flight.
- **A fourth permission system arrives by accident.** The auth library's roles,
  the app role, the node grants and the action grants each answer part of the
  question, and no single page says which wins. This does not fail loudly; it
  fails as an access review nobody can complete.

## Alternatives considered

- **Flat role-based access control** — wins when access does not vary by
  position in a structure. Cheaper to explain, cheaper to test, and the honest
  answer far more often than hierarchy enthusiasts expect.
- **Relationship-based authorization as a service** (a Zanzibar-shaped store) —
  wins when relationships are numerous, cross several services, and need to be
  queried in both directions ("who can see this?" as well as "what can they
  see?"). Costs an external dependency in the read path and a consistency model
  to reason about.
- **An external policy engine with a policy language** — wins when policy
  changes faster than deploys, or must be audited independently of the
  application. The gates then describe how policy is *composed*; the engine
  evaluates it.
- **Denormalizing the reachable set onto each row** — wins when the hierarchy is
  effectively static and reads dominate. It trades write-time fan-out and a
  rebuild path for a plain indexed predicate at read time.
