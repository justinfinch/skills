---
type: Guidance
title: Publishing events through a transactional outbox
description: Write the state change and an outbox row in one transaction, then let a single relay claim rows, publish them under the row id, and mark them done — so what was published can never diverge from what was committed.
tags: [event-delivery, outbox, messaging, reliability, postgres, dual-write]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T15:44:32Z }
status: stable
stale_after: 2029-01-01
sources:
  - id: microservices-io-outbox
    resource: https://microservices.io/patterns/data/transactional-outbox.html
    title: microservices.io — Transactional outbox pattern
  - id: aws-outbox
    resource: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
    title: AWS Prescriptive Guidance — Transactional outbox pattern
  - id: decodable-revisiting-outbox
    resource: https://www.decodable.co/blog/revisiting-the-outbox-pattern
    title: Decodable — Revisiting the Outbox Pattern
  - id: helland-data-outside
    resource: https://www.cidrdb.org/cidr2005/papers/P12.pdf
    title: Pat Helland — Data on the Outside versus Data on the Inside (CIDR 2005)
---

# Publishing events through a transactional outbox

## Technique

The write that changes state and the write that records the intent to publish go
into **the same database transaction**. The aggregate row is updated or
inserted; an **outbox row** carrying the event envelope is inserted beside it. If
the transaction rolls back, neither exists. There is no window in which the state
changed and the event didn't, or the event fired and the state didn't.

A **single relay process** then drains the table:

```sql
-- the relay, and only the relay, touches these rows
SELECT * FROM outbox
 WHERE processed_at IS NULL
 ORDER BY id
   FOR UPDATE SKIP LOCKED
 LIMIT :batch;
```

For each claimed row the relay publishes to the broker **with the outbox row id
as the message id**, waits for the publish acknowledgement, and only then marks
the row processed. The order is load-bearing: publish-then-mark yields
at-least-once (a crash in between republishes, and the message id absorbs it);
mark-then-publish yields silent loss.

**Claim visible rows; do not advance a time cursor.** The tempting
implementation is `WHERE created_at > :last_seen ORDER BY created_at` — and it
silently skips events. A transaction can stamp a row `created_at = T` and *commit
after* a reader's cursor has already passed `T`; that row becomes invisible
forever, with no error anywhere. `FOR UPDATE SKIP LOCKED` against an
unprocessed-row predicate has no such gap, because it claims what is visible now
rather than what is newer than a timestamp.

**The outbox is a transient delivery queue, not a state log.** Rows are claimed,
marked, and pruned. The system of record for history is whatever table the
aggregate lives in — the outbox is *data on the outside*: the message being
forwarded, not the truth being kept. Rebuilds and backfills read the aggregate
tables; they never read the outbox.

**Partition the grants.** The application's writer role gets `INSERT` on the
outbox and nothing else. The relay's role owns the claim/mark/delete columns.
That single split is what makes "only the relay drains the outbox" a property of
the database rather than a convention in a code review.

**Carry the event, don't point at it.** The outbox payload should contain what a
consumer needs to act. A payload that carries only an id, leaving the consumer to
re-read the aggregate at consume time, reintroduces exactly the divergence the
outbox removes — the consumer sees a *later* state than the one that produced the
event, and the event's meaning changes retroactively.

## Applies when

- A state change and its announcement must not diverge — some downstream effect
  (a projection, an accounting entry, a notification, a partner feed) is wrong or
  unrecoverable if the state committed and the event never went out.
- The system of record is a relational store, and the aggregate write and the
  outbox insert can be issued inside **one** transaction on one connection.
- At-least-once delivery is acceptable downstream, because consumers are
  idempotent (or can be made so — see
  [end-to-end-idempotency.md](end-to-end-idempotency.md)).
- You are unwilling to run a distributed transaction between the database and the
  broker. This is usually the deciding condition: the outbox exists precisely to
  remove the need for two-phase commit across two systems with different failure
  behaviour.
- The publishing writes go through code you control. An outbox is a discipline on
  the write path; a write path you don't own can't honour it.
- **The integration style is messaging** — a one-way announcement that something
  happened, whose effects the caller does not wait for. An outbox is not a
  mechanism for request/response: if the caller needs the downstream result
  before it can answer, you want a synchronous call and a different failure
  story.
- The event contract is meant to be stable and deliberate — an envelope you
  design, versioned on your terms, rather than whatever shape the table happens
  to have this quarter.

## Doesn't apply when

- **The event store *is* the system of record.** Under event sourcing the append
  of the event *is* the state change; an outbox duplicates the log you already
  have and creates a second thing that can drift. Consumers read the event store
  (or a stream fed directly from it) instead.
- **There is exactly one consumer and it lives in the same database.** A worker
  that can read the source table under the same transaction boundary needs no
  envelope, no relay, and no second table. Add the outbox when a consumer moves
  out of the database, not before.
- **Losing an occasional event is genuinely acceptable.** Cache invalidation
  hints, best-effort activity pings, metrics samples. Publish after commit, on a
  best-effort basis, and say in writing that delivery is best-effort — that is
  simpler *and* more honest than an outbox whose reliability nobody depends on.
- **The store cannot give you one transaction across both writes.** Cross-shard
  writes, a document store without multi-document transactions, or a write path
  that already spans two services have no atomic point to hang the outbox on.
  Find the single-writer boundary first; an outbox on top of a dual-write is
  still a dual-write.
- **Change data capture is already streaming the aggregate tables and the row
  shape is an acceptable contract.** Log-based CDC off the write-ahead log gives
  you the same atomicity for free, because there is only one write. The cost is
  real and often underestimated: your table schema becomes the published contract,
  so every column rename is a consumer-visible breaking change, and consumers see
  physical row states rather than domain events. Choose this deliberately, not by
  default. (An outbox table read *by* CDC is a different, compatible design — the
  outbox still shapes the contract; CDC merely replaces the polling relay.)
- **The write path is a third-party or off-the-shelf application** you cannot
  modify. CDC or a scheduled reconciliation job is the honest option there.

## Trade-offs

Buys the elimination of one specific bug class: the dual-write. "Committed but
never published" and "published but never committed" both stop being possible,
which means the reconciliation job that hunts for them, and the runbook for
replaying what it finds, both stop being necessary. That is a large amount of
permanent operational work removed for a table and a process.

Costs a relay in the deployment footprint — a process that must always be running,
be monitored, and have exactly-one-ish semantics of its own — plus a table that
grows, a pruning job for it, and a fitness function asserting that every
publishing write path actually inserts its outbox row. It also costs churn in the
database: claim-and-mark is `UPDATE`/`DELETE` traffic on a hot table, which
produces dead tuples and wants its own vacuum attention.

The quality attribute this moves is **integrity**, and it is paid for in
**latency** and **operability**. Delivery is no longer synchronous with the
commit; there is now a publish-to-deliver lag with a distribution, a tail, and an
alarm threshold. If a product requirement says "the downstream effect is visible
immediately," the outbox does not deliver that and no amount of relay tuning
makes it a synchronous call.

It also fixes the consistency model in place, so state it out loud: **atomic
publish-intent, at-least-once delivery, per-aggregate-key ordering at best, no
global ordering**. A consumer that assumes it sees events in commit order across
different aggregates is relying on something the outbox never promised — and the
promise gets weaker the moment a second relay instance or a parallel batch is
introduced.

**What would make this stale.** The outbox is a hand-assembly of something the
storage engine could in principle provide: an atomic commit that also hands a
message to a subscriber. If relational engines or managed database platforms ship
a first-class transactional publish — a durable change stream or queue primitive
committed with the transaction and consumable outside the database — then the
table, the relay process, and the pruning job all become machinery you are
maintaining for a feature you already have. Watch for that, and re-grill this page
when it appears in the engine you actually run.

## Failure modes

- **Relay lag under burst, discovered downstream.** The write path absorbs a
  spike happily — inserts are cheap — and the relay drains at its own rate.
  Nobody notices until a projection is twenty minutes stale and a user reports
  that something they did "didn't happen." The metric to alarm on is not outbox
  row count but **the age of the oldest unprocessed row**; depth alone can look
  identical for a fast-draining spike and a wedged relay. Alarm on age, page on
  age, and put the number in the runbook.
- **The relay is dead and nothing says so.** Writes still succeed — that is the
  outbox's gift and its trap. There is no error on the request path, no failed
  publish, no exception in a log anywhere; the system looks perfectly healthy
  from every direction except the one nobody is watching. A relay that publishes
  a heartbeat, or a liveness check on oldest-row age, is the difference between
  minutes and the next morning.
- **Unbounded outbox growth.** With no retention policy the table accumulates
  every event ever published. The claim query's plan degrades as the index grows,
  autovacuum falls behind the update churn, and the eventual mitigation — a mass
  `DELETE` on a table the relay is actively claiming from — happens under
  pressure at the worst possible time. Decide retention when you create the
  table (age after `processed_at`), not when the disk alert fires.
- **Outbox-as-log.** The most seductive failure on this page, because it looks
  like a simplification. Keep the rows forever, let each consumer hold its own
  cursor into the outbox table, skip the broker. What you have built is a broker
  inside your database, missing its parts: every consumer is now coupled to the
  outbox schema, every consumer's offset and dedup state is your operational
  burden, and the cursor is a timestamp — which carries the silent skip described
  above. **Evidence shape: a production system shipped exactly this design,
  complete with a notify-based wakeup and a per-consumer cursor table, and
  corrected it to the canonical single-relay-to-broker shape within weeks of
  writing it down** — the correction was cheap only because the envelope had
  already been designed to map onto a broker's message shape. The tell that you
  are heading here: an "append-only outbox" rule, or a second consumer being
  handed a `SELECT` against the outbox table.
- **Mark-before-publish, or a publish that isn't acknowledged.** A relay that
  marks rows processed and then fires a non-blocking publish loses every message
  in flight when it restarts, silently and permanently, because the rows are gone
  from the claim query. The same happens with a fire-and-forget client that never
  waits for the broker's ack. Publish, await the ack, then mark — and accept the
  duplicates that ordering implies.
- **A write path ships without its outbox insert.** A new endpoint, or a
  refactor that splits the aggregate write and the outbox insert across two
  transactions, produces state that is correct and downstream effects that never
  happen. Nothing fails. The only thing that catches this is a test asserting the
  two writes share a transaction — roll back, and neither row exists.
- **Poison rows and retry storms.** A row whose publish always fails is claimed,
  fails, is released, and is claimed again forever. With `SKIP LOCKED` the rest
  of the table keeps moving, so throughput looks fine while one row burns the
  relay's attempts and floods the logs. Bounded attempts plus a dead-letter or
  abandoned state, decided up front, is the whole fix.
- **Two relays, one assumption about order.** Running a second relay instance for
  availability is safe for correctness (`SKIP LOCKED` prevents double-claiming)
  and fatal for any consumer that assumed commit order. The failure is not an
  error; it is a projection that computes the wrong running total once a week.
  Either keep the relay singleton and say so, or state that ordering is
  per-aggregate-key only and make consumers tolerate it.
- **The pruning job and the slow consumer disagree.** Pruning is sized for disk;
  replay expectations are sized for incidents. If anyone believes "we can always
  re-drain the outbox," check that belief against the retention window — usually
  it is false, and the real replay source is the aggregate tables.

## Alternatives considered

- **Publish after commit (plain dual-write)** — wins when event loss is
  acceptable and stated, and when the operational cost of a relay genuinely
  exceeds the cost of an occasional missing event. Loses the moment anyone
  downstream treats the stream as complete.
- **Two-phase commit / XA across the database and the broker** — wins in
  environments that already run a transaction coordinator and where both
  resources support it properly. Loses almost everywhere else: it couples the
  availability of the write path to the availability of the broker, which is the
  exact coupling the outbox is bought to avoid.
- **Log-based CDC on the aggregate tables** — wins when you cannot modify the
  write path, when the physical row shape is an acceptable published contract,
  and when the team already operates a CDC pipeline. Loses when the event
  vocabulary should be a designed, versioned contract rather than a mirror of the
  schema.
- **Event sourcing** — wins when the history of changes is itself the thing of
  value and the current state is a fold over it. Then the outbox is redundant by
  construction. Loses when most reads want current state and the team is not
  prepared for the versioning, snapshotting, and tooling burden.
- **The aggregate row as the published event** — consumers cursor on a state
  column and read the row. Wins for one consumer, in one database, with no
  contract obligations. Loses as soon as there are two: the row's schema becomes
  the wire format, "when did this change" and "has this been delivered" collapse
  into the same column, and a mutable row cannot represent a thing that happened.
  This is the design a transactional outbox is usually the correction *of*.
- **Per-consumer queue tables (fanout on insert)** — one row per (event,
  consumer). Wins when consumers are few, permanently known, and need
  independently durable positions without a broker. Loses because the publisher
  now knows the subscriber list, so adding a consumer is a schema change on the
  publish path.
- **A general-purpose job queue in the same database** — wins when the real need
  is "run this work later," not "announce that this happened." Loses as an outbox
  because a job queue models work to be consumed, not committed facts to be
  published, and its retry semantics are tuned for the former.
