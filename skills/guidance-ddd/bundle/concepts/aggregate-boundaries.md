---
type: Guidance
title: Sizing an aggregate's consistency boundary
description: Group entities by the invariants that must hold atomically, and reference everything else by identity so the consistency model is stated rather than assumed.
tags: [ddd, aggregates, consistency]
created: 2026-08-26
generated: { by: write-guidance/claude-opus-5, at: 2026-08-26T00:00:00Z }
status: stable
stale_after: 2031-01-01
sources:
  - id: evans-ddd
    resource: https://www.domainlanguage.com/ddd/
    title: Eric Evans — Domain-Driven Design
---

# Sizing an aggregate's consistency boundary

## Technique

Group into one aggregate exactly those entities that must be consistent with
each other at every instant, and give it a single root through which all changes
pass. Everything outside is referenced by identity and reconciled eventually.

The aggregate boundary **is** the transaction boundary. Drawing it is therefore
a statement about the system's consistency model, not an object-modelling
preference — one transaction, one aggregate, and anything spanning two is
eventually consistent by construction.

## Applies when

- A real invariant spans more than one entity — a rule that must never be
  observed broken, such as a total that must equal the sum of its lines, or a
  limit that must not be exceeded by concurrent additions.
- Concurrent modification is genuine: two actors can plausibly change the same
  cluster at the same moment, and last-write-wins would silently corrupt the
  rule.
- You need to state, and be held to, which parts of the system are immediately
  consistent and which are not.

## Doesn't apply when

- **No invariant spans the entities.** If each entity's rules are local, the
  aggregate is ceremony: a root that exists to be loaded and saved, adding a hop
  and a lock without protecting anything.
- **The "invariant" is a query concern.** "The dashboard should show a
  consistent total" is a read-model requirement, not a reason to enlarge a
  transaction boundary. Enlarging it to fix a report is how contention gets
  designed in.
- **The rule tolerates being briefly wrong.** Many business rules are
  compensating rather than preventive — the business already handles the
  overdraft, the oversell, the double booking. If violation is recoverable and
  rare, eventual consistency is the cheaper correct answer.
- **Contention would make the aggregate a bottleneck.** If the boundary implies
  serializing an operation the business expects to be concurrent, that is
  evidence the boundary is wrong — not evidence that aggregates are wrong.

## Trade-offs

Buys an explicit, defensible consistency story: a clear unit of locking, an
obvious place for invariants to live, and a concurrency answer that does not
depend on the database's isolation level being what you assumed.

Costs eventual consistency everywhere else, and all the machinery that implies —
domain events, idempotent handlers, reconciliation for the cases that fail
mid-flight, and a UI that must represent "not yet" without looking broken. Small
aggregates are correct and are also the reason the rest of the system gets
harder.

## Failure modes

- **Sized by object graph rather than by invariant.** The aggregate grows to
  match how the data is naturally navigated, so a high-traffic entity ends up
  inside a root that everything must lock. Symptom: transaction timeouts and
  retry storms under load, on an operation nobody thought was contended.
- **Loading a whole aggregate to change one field.** Correct by the rules and
  ruinous in practice once the aggregate holds thousands of children. The 3am
  version of this is a memory exhaustion in a background job that has run
  nightly for a year and just crossed a threshold.
- **Cross-aggregate transactions sneaking back in.** Two repositories called
  inside one transaction restores the coupling the boundary was drawn to remove,
  and it is invisible in review because each call looks ordinary.
- **Eventual consistency asserted but never handled.** Events are published, the
  happy path works, and there is no reconciliation for the handler that failed
  after the aggregate committed. The inconsistency is real, permanent, and
  discovered by a customer.

## Alternatives considered

- **Database-enforced constraints** — wins when the invariant is expressible as
  a unique index or a check constraint. Cheaper, faster, and harder to get wrong
  than an application-level boundary; reach for it before designing an aggregate
  around the same rule.
- **Optimistic concurrency on a single entity** — wins when the rule is local
  and the only hazard is lost updates. A version column solves it without a
  cluster.
- **A process manager over small aggregates** — wins when the invariant is
  really a multi-step business process with compensations, rather than a
  condition that must hold at every instant.
