---
type: Guidance
title: Separating commands, projections, and queries over one database
description: Run three models over a single relational store — a command model whose unit of work is one aggregate in one transaction, a projection model that owns derivation logic, and a query model returning DTOs that never touch the domain — and keep the separation honest with a dependency rule rather than a folder convention.
tags: [cqrs, command-query-separation, unit-of-work, projections, read-models, eventual-consistency, ddd]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:08:15Z }
status: stable
stale_after: 2029-06-01
sources:
  - id: fowler-cqrs
    resource: https://martinfowler.com/bliki/CQRS.html
    title: Martin Fowler — CQRS
  - id: fowler-cqs
    resource: https://martinfowler.com/bliki/CommandQuerySeparation.html
    title: Martin Fowler — CommandQuerySeparation
  - id: young-cqrs-documents
    resource: https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf
    title: Greg Young — CQRS Documents
  - id: dahan-clarified-cqrs
    resource: https://udidahan.com/2009/12/09/clarified-cqrs/
    title: Udi Dahan — Clarified CQRS
  - id: helland-life-beyond-dt
    resource: https://queue.acm.org/detail.cfm?id=3025012
    title: Pat Helland — Life beyond Distributed Transactions (ACM Queue, 2016)
  - id: terry-session-guarantees
    resource: https://doi.org/10.1109/PDIS.1994.331722
    title: Terry et al. — Session Guarantees for Weakly Consistent Replicated Data (PDIS 1994)
  - id: vogels-eventually-consistent
    resource: https://queue.acm.org/detail.cfm?id=1466448
    title: Werner Vogels — Eventually Consistent (ACM Queue, 2008)
  - id: fowler-reporting-database
    resource: https://martinfowler.com/bliki/ReportingDatabase.html
    title: Martin Fowler — ReportingDatabase
---

# Separating commands, projections, and queries over one database

## Technique

Split the application into **three models over one database** — not two. The
usual framing is "write side and read side"; the third model is the one that
gets lost, and losing it is where this pattern goes fuzzy.

**The command model** is the full domain model. A command executes as a **unit
of work**: it loads one aggregate, mutates it through domain methods that
enforce that aggregate's invariants, and persists the aggregate state — and
appends to an outbox in the same transaction — before returning. Four
boundaries collapse into one rule:

> unit of work = aggregate = transaction = outbox append

That single alignment is what makes "mutated but never announced" structurally
impossible rather than a bug class you monitor for. Which aggregate that is —
how big it should be, what invariant justifies it — is settled before this page
applies; see `guidance-ddd/concepts/aggregate-boundaries.md`. How the appended
events actually leave the database is a separate concern owned by
`guidance-event-delivery`; this page only requires that the append shares the
transaction.

**The projection model** consumes those events and writes derived read tables.
It is *not* "the read side." It is where derivation logic lives — the
classification, the state-change interpretation, the roll-up, the enrichment —
and that logic has its own invariants and its own evolution schedule. It runs
asynchronously and is eventually consistent by design. What its tables are
worth — droppable derived data, or a primary store nobody realized they had —
is the separate decision on
[rebuildable-projections.md](rebuildable-projections.md), which in turn rests on
[append-only-source-stream.md](append-only-source-stream.md).

**The query model** is thin reads over the projection tables and the source
stream, returning **DTOs**. It does not hydrate domain objects, ever. No
aggregate is loaded, tracked, or returned on the read path.

**Command richness is conditional, not uniform.** A command hydrates a full
aggregate only when there is a real invariant to enforce:

| Command shape | Treatment |
| :--- | :--- |
| A cross-field or multi-entity invariant must hold after the mutation | Full aggregate hydration inside the unit of work |
| A pure append with a single cheap precondition | Thin handler: check the precondition, insert the row, append the event |

The test is one question: *is there a cross-field or multi-entity invariant to
enforce on this mutation?* If yes, aggregate. If no, thin append. Applying full
hydration uniformly pays rehydration cost on the hottest path in the system and
pressures engineers to invent rich aggregates around pure appends just to
satisfy a rule.

**Read-your-writes is eventual, by contract.** A command returns a lightweight
result — ids plus the facts just committed — which the client renders
**optimistically**. The authoritative projected read model arrives
asynchronously and reconciles against that echo on a stable key. Projection
does **not** run synchronously inside the command transaction. This is a
[session guarantee](https://doi.org/10.1109/PDIS.1994.331722) implemented in the
client, not a consistency property of the server, and the difference matters the
moment the client is not yours.

**Implementation is deliberately un-framework'd.** Commands are plain
application-service functions. Queries are a separate read module of
hand-written SQL returning DTOs. Cross-cutting concerns — transaction, auth,
audit, logging — are explicit wrappers, not a mediator or command bus. No
dispatch registry until handler count and cross-cutting needs actually earn one.

**The separation is enforced by a dependency rule, not a folder name.** A
build-time check asserts the query module has no import edge into the domain
model (`query-must-not-import-domain`). The rule exists because the erosion is
invisible in review and invisible to a coding agent: nothing about a `queries/`
directory stops a file in it from importing an aggregate class. See
`guidance-fitness-functions` for how such a check is registered and kept alive.

## Applies when

- **The read shape genuinely diverges from the write shape.** A read serves
  several aggregates at once, or a denormalized feed, or a roll-up that no
  single aggregate owns. This is the deciding condition: without divergence
  there is nothing for three models to buy.
- **There is real derivation logic** between what was written and what is read —
  classification, interpretation, aggregation — rather than a mechanical field
  mapping. Derivation with logic in it is what makes the projection model a
  model rather than a mapper.
- **One relational store, and a second datastore would be a real operational
  cost.** The "lite" in this pattern is that the projection tables live in the
  same database as the aggregate tables. That is a deliberate scope limit, not
  an oversight.
- **Invariants are concentrated.** A few aggregates carry genuine cross-field
  rules; the majority of writes are appends with one cheap precondition.
  Conditional hydration only pays when the distribution is lopsided.
- **Eventual read-model freshness is acceptable to the product**, and you own
  the client well enough to render an optimistic echo — or the product can
  tolerate a visible "processing" state.
- **Events already leave the write transaction**, or will. The projection model
  needs a trigger, and the outbox append is it.
- **Aggregate boundaries are already settled.** This is the application-layer
  corollary of a domain model that exists. Adopting it before the boundaries
  are drawn produces three models of nothing.

## Doesn't apply when

- **Read shape ≈ write shape.** Plain CRUD over a handful of tables. Three
  models is ceremony: you pay the conceptual surface, the DTO duplication, the
  dependency gate, and the eventual-consistency UX tax for a read that could
  have been a `SELECT` off the table you just wrote. This is the most common
  wrong adoption and the easiest to check — write the read query against the
  aggregate tables first, and only split when it stops being writable.
- **Reads must be strictly consistent and no echo trick is acceptable.** A
  regulated display that must show committed state; a partner system that
  writes and then immediately polls; a compliance readback. An optimistic echo
  is a UI affordance, not a consistency guarantee, and it does not survive a
  caller you do not control. Either project synchronously (a different pattern,
  with the coupling that implies) or read the aggregate tables directly on that
  path and say so.
- **The team actually needs separate read stores.** Read scaling, read-path
  availability isolation, or an index the write store cannot provide (search,
  graph, columnar). That is full CQRS, and it is a different cost profile — a
  second datastore to operate, replicate, secure, and back up. Do not adopt
  three-models-over-one-database as a *substitute* for it and then discover the
  read pressure was the real problem.
- **The derivation is a genuinely mechanical fold** with no logic and no
  expected evolution. Then the projection model is a mapper, and naming it a
  third model is vocabulary overhead. Collapse to two and revisit if
  derivation logic ever shows up.
- **The write path is not yours.** A third-party application, or a shared
  database written to by systems you do not deploy, cannot honour the unit-of-
  work rule. The command model's guarantees are guarantees about code you own.
- **Nobody will hold the dependency rule.** If the check will not be added to
  CI and kept green, the separation is a naming convention with a two-quarter
  half-life. Better to know that before paying for the conceptual surface.

## Trade-offs

Buys a single coherent answer to "where does this logic go" — command
invariants in aggregates, derivation logic in projectors, none at all on the
read path. Buys thin, fast reads that never pay hydration cost. Buys a command
commit and its announcement as one atomic boundary. Buys a projection model
that can be rewritten and re-run without touching a line of command code, which
is the property that makes improving derivation logic cheap later.

Costs three models' worth of conceptual surface where "just CRUD" needs one.
Every engineer must know which path they are on and internalize the conditional-
hydration test. Every command-then-read interaction in the product must handle
the optimistic-echo-then-reconcile dance rather than assuming freshness. DTOs
are hand-maintained alongside the projection tables they read — deliberate
duplication, accepted specifically so that "just return the aggregate" is never
the convenient shortcut. And the dependency check is one more CI gate to keep
green.

The quality attributes this moves are **modifiability** and **read
performance**. It pays for them in **consistency** and in **conceptual
simplicity** — and the second is the one teams underprice, because it shows up
as onboarding time and as the review comment "why are there two places that
describe this record."

**State the consistency model out loud**, because the pattern is otherwise
silently assumed to have one it doesn't:

- Strong consistency **inside one aggregate, inside one transaction**. Nothing
  larger.
- Everything across aggregates, and everything on the read path, is
  **eventually consistent**, with a lag that is bounded in practice only by an
  alarm someone remembered to set.
- **Read-your-writes is a client-side illusion.** It holds for the session that
  issued the command, for as long as that session holds its echo. It does not
  survive a page reload before the projection lands, a second device, or a
  different caller.
- **Monotonic reads are not guaranteed.** A client that reconciles its echo
  against a projection, then re-reads before the projector has caught up, can
  watch its own write disappear and come back. Design the reconcile key so this
  is detectable rather than merely surprising.

**What would make this stale.** The projection model is hand-built machinery
for something a database could in principle maintain: derived tables kept
current transactionally, without a worker. If incremental view maintenance in
the engine you actually run becomes cheap and general enough to express real
derivation logic — not just SQL folds — then the projector fleet, its dispatch,
and its lag alarm become infrastructure you maintain for a feature you already
have. Re-grill this page when that lands in your engine, not when it appears in
someone's conference talk.

## Failure modes

- **The query side quietly imports domain code until the separation is
  fiction.** This will happen; the dependency rule exists because it will
  happen. It starts as a reasonable-looking reuse — a value object for
  formatting, an enum, one factory — and ends with a read endpoint that
  lazy-loads an aggregate graph and issues eighty queries. The symptoms arrive
  before the diagnosis: read latency that regressed with no schema change, and
  a read path that turns out to be mutating tracked entities. Without a
  build-time check, the erosion is invisible in review, and completely
  invisible to an agent writing code against the existing patterns in the file.
- **Commands grow return values until callers treat them as queries.** The
  progression is reliable: return the created id; then return the created row;
  then "while you're in there" return the joined view; then someone projects
  synchronously inside the command transaction so the return value can be
  authoritative. The async model is now defeated, the command transaction is
  inflated, and the outbox append shares a transaction with derivation work
  that can fail. The rule that holds the line: a command's public return type
  is ids plus facts it committed itself, never a projected view.
- **The projector is dead and the system looks healthy.** Writes succeed.
  Commands return. The client's optimistic echo renders. Every dashboard is
  green, because the only thing broken is that reads are getting older. This is
  the 3am page, and it does not page anyone unless someone built it: alarm on
  **the age of the oldest unprojected event**, not on queue depth or worker
  liveness. Support hears about it first, in the form of "the app lost my
  data" — which is exactly what a stale projection looks like from the outside
  after the echo is gone.
- **The optimistic echo and the projector disagree.** The client renders what
  it thinks the projection will say; the projector computes something else. The
  user watches a value change under them a few seconds after acting. Worse is
  the silent version: the echo is *right* and the projection never arrives, so
  the client's temporary rendering is the only place that data has ever been
  seen, and it vanishes on reload. Reconciliation needs a key that lets the
  client tell "not yet" from "never."
- **The reconcile key is missing or unstable**, so the projected row cannot be
  matched to the echo and the client shows both — a duplicate entry in a feed,
  which users report as a data-integrity bug and which is actually a
  client-state bug.
- **Conditional hydration degenerates in one of two directions.** Either
  everything becomes an aggregate — invariants get invented to justify the
  hydration, and the capture path pays rehydration cost it has no budget for —
  or nothing does, and real invariants drift out of the domain model into
  handlers, then into database constraints nobody can name the reason for. Both
  are gradual and both look locally reasonable in the pull request that
  introduces them.
- **"No command bus" is outgrown without anyone deciding.** Explicit wrappers
  are the right call at ten handlers. At sixty, the transaction/auth/audit
  wrapper stack is copy-pasted, and exactly one handler is missing the
  transaction wrapper. The failure is not an error: it is a state change that
  committed without its outbox row, discovered downstream, months later. If you
  keep plain handlers, keep a check that every command entry point is wrapped.
- **Three models become three names for two.** The projection model is folded
  into "the read side" in conversation, then in the code layout, then the
  derivation logic ends up in query functions — where it re-runs on every read,
  cannot be versioned, and cannot be re-run against historical data. The
  vocabulary is load-bearing; when people stop saying "projection model," check
  the imports.

## Alternatives considered

- **Plain CRUD over one model** — wins when read shape matches write shape and
  derivation is trivial. It is the correct default and the thing this pattern
  must justify itself against, not the other way round.
- **Two-sided split (command vs. read), projection folded into "the read
  side"** — wins when derivation really is a mechanical fold with no
  independent evolution. Loses when derivation carries genuine logic: the fold
  framing is precisely where the "we can re-derive later" promise quietly
  erodes, because logic that lives on the read path cannot be versioned or
  replayed.
- **Full CQRS with a separate read store** — wins when read scaling, read-path
  availability isolation, or a fundamentally different index shape is needed,
  and when the team can operate a second datastore. Loses when the only real
  driver was read *shape*, which one database serves fine.
- **Event sourcing as the source of truth for command aggregates** — wins when
  the history of changes is itself the valuable thing and current state is a
  fold over it. Loses when most reads want current state: it adds rehydration
  cost and snapshot machinery to every command for no read-path benefit. Note
  that being event-sourced on *evidence* — an append-only source stream feeding
  projections — is a different and much cheaper commitment.
- **Synchronous projection for a whitelist of critical reads** — project inline
  in the command transaction so the writer sees the read model immediately.
  Wins when a genuinely small, stable set of reads must be strict and the
  derivation for them is bounded and cannot fail. Loses generally: it couples
  command and projection, inflates the transaction, and partially defeats the
  asynchrony the outbox exists to provide.
- **Command bus / mediator with pipeline middleware** — wins with many handlers
  and rich cross-cutting concerns, where the registration ceremony is cheaper
  than the copy-paste it replaces. Loses early, where it is indirection and
  reflection standing between a reader and forty lines of logic.
- **Folder convention and code review only** — wins in a small, stable, highly
  disciplined team with total review coverage. Loses as the primary guard for
  the reason the dependency rule exists: nothing stops a query module importing
  an aggregate, and the erosion produces no failing test, no error, and no
  visible symptom until the read path is already coupled.
- **A reporting database or read replica** — wins when the pressure is
  analytical queries competing with transactional load, which is a resource
  problem, not a modelling one. Loses as a substitute for this pattern: it
  gives you the same shapes on different hardware.
