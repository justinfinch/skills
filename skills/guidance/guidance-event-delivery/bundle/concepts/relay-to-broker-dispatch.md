---
type: Guidance
title: Dispatching through one relay and a broker
description: Let exactly one relay publish into a durable broker and give every consumer its own durable subscription there, so consumers keep their position in the broker rather than in the source database — and know the threshold at which database notifications stop being enough.
tags: [event-delivery, messaging, broker, fanout, durable-subscription, listen-notify]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T15:44:32Z }
status: stable
stale_after: 2029-01-01
sources:
  - id: eip-publish-subscribe
    resource: https://www.enterpriseintegrationpatterns.com/patterns/messaging/PublishSubscribeChannel.html
    title: Hohpe and Woolf, Enterprise Integration Patterns — Publish-Subscribe Channel
  - id: eip-durable-subscriber
    resource: https://www.enterpriseintegrationpatterns.com/patterns/messaging/DurableSubscription.html
    title: Hohpe and Woolf, Enterprise Integration Patterns — Durable Subscriber
  - id: postgres-notify
    resource: https://www.postgresql.org/docs/current/sql-notify.html
    title: PostgreSQL — NOTIFY
  - id: jetstream-model
    resource: https://docs.nats.io/nats-concepts/jetstream
    title: NATS — JetStream streams, durable consumers and retention
---

# Dispatching through one relay and a broker

## Technique

**One** process publishes. A durable broker holds the stream and does the fanout.
Each consumer is an **independent durable subscription** that tracks its own
position **in the broker**, not in the source database.

The shape, end to end:

```
write tx ──> outbox ──> [ single relay ] ──> broker stream
                                               ├── durable consumer A  (projection worker)
                                               ├── durable consumer B  (live push pump)
                                               └── durable consumer C  (added later, no publish-path change)
```

Three properties follow from that arrangement and none of them follow without it:

- **Independent pace.** A projection worker that falls an hour behind does not
  stall the push pump, and neither of them holds up the relay. Each subscription
  has its own position, its own redelivery, its own backlog.
- **Independent failure.** A consumer can be down for its own reasons, be
  redeployed, or fail a message repeatedly into the broker's dead-letter handling
  without any of that being visible to the publish path or to its siblings.
- **Registration, not integration.** Consumer number three subscribes to an
  existing subject. No schema change, no publish-path change, no new cursor table,
  no deployment coupling.

**Exactly one writer into the stream.** The relay is the only thing that reads
the outbox and the only thing that publishes. Two publishers means two orderings
and two dedup domains; a consumer that also publishes back into the same stream
means a cycle nobody drew. Keep the relay singleton, or make its concurrency
explicit and downgrade the ordering claim accordingly.

**Position lives in one place.** Once the broker exists, a consumer that still
keeps a cursor in the source database has two positions and no single answer to
"what has this consumer processed." The hybrid is worse than either pure design:
it inherits the database cursor's ordering hazards *and* the broker's operational
surface. Move the position to the broker or don't adopt the broker.

**Subjects are a public contract.** The subject or topic taxonomy — commonly
`<domain>.<aggregate-type>.<event-type>` — is what consumers filter on and what
you cannot rename without dual-publishing through a transition. Design it once,
with room for event types you have not invented, and write down that new event
types are new subjects on the existing stream rather than new streams.

**"Adopt a broker" and "how finely to slice it" are two decisions.** The
condition that justifies a broker is fanout to consumers with independent pace
and failure — that argues for the *existence* of a durable stream and says
nothing about how many streams there should be, how fine the subject hierarchy
goes, or whether each consumer gets its own filtered view. Decide the first on
the conditions below; decide the second on ordering requirements and retention
policy, which are the two things that genuinely differ per stream. The common
default — one stream over a hierarchical subject space, with per-consumer filters
— exists because it keeps the second decision reversible while the first is not.

**Say what the stream is for.** A broker stream is normally a **transit buffer**
with a bounded retention, not the system of record. Replay within retention comes
from the broker; replay beyond it comes from the durable source of truth. Two
different mechanisms, two different bounds — state which one your rebuild story
depends on before you need it.

## Applies when

- **Two or more consumers with independent pace or failure domains.** This is the
  load-bearing condition. Consumers that must not block each other, live in
  different processes or services, or have materially different latency
  requirements cannot be served by one in-process dispatcher.
- The consumers genuinely live in different deployment units — for instance one
  inside a request-serving process that holds client connections and one in a
  background worker fleet. A single relay cannot be resident in both, so
  something has to carry events between them.
- **Replay is required.** Rebuilding a projection, onboarding a new consumer that
  needs recent history, or reprocessing after a bad deploy are all product or
  operational requirements — not hypotheticals — and the broker's retained stream
  is the mechanism.
- Per-consumer redelivery, bounded delivery attempts, and dead-lettering are
  needed, and the alternative is writing that machinery by hand in application
  code.
- The team can actually operate a stateful system: it has somewhere to put a
  persistent volume, a local-development story, a CI story, an upgrade story, and
  a backup-and-restore story for the stream.

## Doesn't apply when

- **There is one consumer and no replay requirement.** Call it directly, or let it
  poll the outbox. A broker is operational surface with no fanout to pay for it —
  you take on the deployment, the monitoring, and the 3am failure modes to move
  events between two things that could have been one call.
- **The team cannot operate another stateful system, and consumer count is stable
  at one or two.** Database `LISTEN`/`NOTIFY` as a low-latency wakeup, plus a
  polling claim as the durable fallback, covers this gap honestly and adds zero
  infrastructure. But the deferral is only defensible if you write down the
  threshold that ends it. Concrete thresholds worth stating, in the order they
  usually bite:
  - **Consumer classes above roughly five.** Each one is another position to
    monitor and another dedup table to operate; the hand-rolled burden overtakes
    the broker's operational cost right about there.
  - **Sustained publish rate above roughly a hundred events per second.** Notify
    itself scales well past this; the per-consumer polling underneath it does
    not, and the table-scan load becomes operationally visible.
  - **A consumer in a different region from the database**, where notification
    latency and connection fragility become the thing you are debugging.
  - **Replay-from-history becomes a requirement** rather than a nice-to-have.
  - **Any consumer needs to be down for hours** without the others degrading.

  Crossing any one of these is the migration. Write the numbers into the decision
  record; a trigger without a threshold is folklore that decays.
- **Global ordering across all events is a hard requirement.** Brokers typically
  guarantee ordering per subject or per partition key, and a relay you scale out
  gives up commit order entirely. A single-threaded relay driving a single
  consumer is the design that actually preserves total order. If you need it, say
  so before adopting fanout, because fanout is what takes it away.
- **The deployment target cannot host it.** Fully serverless footprints with no
  persistent volume, edge or air-gapped environments, or a platform policy
  against self-hosted stateful services. Managed brokers are the answer there —
  if the constraint that pushed you to serverless was cost or vendor policy,
  check whether it also excludes those.
- **The consumers are multi-step workflows with human-in-the-loop steps, waits,
  and scheduled retries** rather than stateless transforms. A broker plus
  hand-rolled state is a worse durable-workflow engine than a durable-workflow
  engine.

## Trade-offs

Buys fanout, per-consumer durable positions, replay, redelivery, and
dead-lettering as **infrastructure primitives** instead of application code. The
value is not the feature list; it is that these are the things teams build badly
by hand, in increments, each one looking small — the offsets table, then the
dedup table, then the retry loop, then the poison-message quarantine — until
there is a homegrown broker in the codebase that nobody chose to write and
everybody has to maintain.

Costs an operational surface that is often wildly disproportionate to current
throughput: a service in local development, a container in CI, a deployment
target with persistent storage, monitoring, upgrades, and a backup story for the
stream. At ten events a day, the honest description is that you are running a
message broker for ten events a day, and that cost is paid every day whether or
not the fanout is exercised.

It also adds a hop. Two things — relay and broker — now sit between a committed
write and a delivered effect, so **publish-to-deliver lag** becomes the key
metric and the broker becomes a new availability dependency for delivery (though
not, thanks to the outbox, for the write path).

The quality attributes moved are **modifiability** and **availability of the
consumer set**: new consumers are cheap, and one consumer's failure is contained.
What is paid is **operability** and **simplicity**, and — under a scaled-out
relay — **ordering**.

**What would make this stale.** The counter-case on this page rests almost
entirely on operational cost, and operational cost is the thing that erodes. If
brokers become ambient — a near-zero-effort managed tier, or a stream primitive
inside the database you already run — then "the team cannot operate another
stateful system" stops being a real condition and the thresholds below become
irrelevant, because the broker costs nothing to have. The reverse pressure is
also live: as in-database queue and stream extensions mature, the ceiling on the
LISTEN/NOTIFY answer rises and the thresholds move up rather than away.
Re-derive the numbers against what your platform offers rather than inheriting
them.

## Failure modes

- **The broker is adopted "for later" and runs unexercised.** One consumer, no
  replay, no dead-letter traffic; the stream is a pass-through nobody watches.
  Then a real incident becomes the first time anyone learns how this thing
  behaves when its disk fills, when a consumer's position is invalid, or when it
  restarts under load. Unexercised infrastructure is not readiness — it is a
  dependency with no operational history. If you adopt it early, exercise it
  early: put the second consumer on it, run a replay drill, and kill it in
  staging on purpose.
- **A deferral trigger fires immediately.** *Evidence shape: a production system
  wrote a careful migration-trigger decision record — named broker, three
  numeric thresholds, an explicit "not at v1" — and adopted the broker anyway
  within weeks, because correcting an unrelated design flaw turned out to
  require the fanout the deferral had assumed away.* The lesson is not that
  writing the trigger was wasted. It was the opposite: the trigger record had
  already forced the envelope to be shaped so it mapped cleanly onto broker
  subjects and message ids, which turned the reversal into a publish-handler and
  a deployment rather than a redesign. **Write the deferral down, including what
  would end it, and shape the seam as though it will end tomorrow — because it
  might.**
- **A single-node broker becomes an unbacked single point of failure.** One
  instance, one volume, no replication, and a backup-and-restore procedure nobody
  has written because the stream is "just a buffer." It is just a buffer right up
  to the moment it is the only copy of two hours of undelivered events. Decide
  explicitly whether the stream is recoverable or disposable, and if it is
  disposable, verify that everything in it can be regenerated from the source of
  record.
- **The outbox silently becomes the buffer during a broker outage.** Writes keep
  succeeding, the relay keeps failing to publish, the outbox grows. This is
  correct behaviour and it has a bound nobody computes until it matters: at the
  current write rate, how long can the outbox absorb a broker outage before disk
  or vacuum pressure turns a delivery incident into a database incident? Compute
  that number and put it in the runbook next to the broker's recovery procedure.
- **Retention shorter than the slowest consumer's worst outage.** A consumer is
  down over a long weekend, its position ages out of the stream, and on restart it
  either resumes from a position the broker no longer holds — an error, if you are
  lucky — or silently jumps to the head of the stream and skips everything in
  between. The gap is discovered later as missing rows in a projection. Size
  retention from the longest realistic consumer outage, not from disk
  convenience, and alarm on any consumer whose lag approaches the retention edge.
- **Poison messages with unbounded redelivery.** No maximum delivery count means
  one bad message is redelivered forever, occupying the consumer, filling logs,
  and — for an ordered subject — blocking everything behind it. The symptom is a
  consumer at a hundred percent utilization making zero progress.
- **Ephemeral where durable was meant, or the reverse.** A live-push consumer
  configured ephemeral reconnects and quietly resumes at the head, dropping
  whatever arrived while it was away; a "best-effort" consumer configured durable
  accumulates a backlog it will replay into users' faces after an outage. Both
  are configuration, both are silent, and both are found by a customer.
- **Two positions after migration.** The database cursor is left in place "just
  in case" alongside the broker subscription. Now events are processed twice, or
  the two disagree about what has been handled, and every incident starts with
  ten minutes of figuring out which position is real.
- **The subject taxonomy is outgrown.** Subjects were designed around today's
  aggregates; a new event type doesn't fit, and the fix that gets shipped is a
  subject that overlaps an existing filter. Consumers start receiving messages
  they were never written to handle. Renaming means publishing to both names
  through a transition window with every consumer updated in between — plan the
  taxonomy as a contract, because that is what it is.
- **Relay scaled out for availability, ordering assumption unchanged.** A second
  relay instance is added during an incident and never removed. Correctness of
  delivery holds; commit order does not. The resulting defect is intermittent,
  data-dependent, and will not reproduce in a test.

## Alternatives considered

- **Relay invokes consumers directly (in-process or over HTTP)** — wins with one
  consumer, or with a small fixed set that lives in the same process as the
  relay. Loses when consumers span deployment units, when one consumer's slowness
  must not become another's, or when a consumer needs to catch up after being
  down: the relay would have to hold the retry state for each of them, which is
  the broker you didn't adopt, badly.
- **Database `LISTEN`/`NOTIFY` plus a durable polling claim** — wins at low
  throughput with one or two consumers and a team that will not operate another
  stateful system; adds no infrastructure and reuses the transaction boundary you
  already trust. Loses at the thresholds named above, and note the semantics:
  notifications are best-effort and are dropped on disconnect, so the polling
  claim must be the authority and the notify merely the latency improvement.
  Treating notify as the delivery mechanism is a data-loss bug waiting for a
  network blip.
- **A managed cloud pub/sub or hosted streaming service** — wins when operational
  surface is the binding constraint and third-party spend is permitted; you get
  durability, fanout and dead-lettering without owning a stateful service. Loses
  under a hard no-paid-dependencies or no-vendor-coupling constraint, in
  air-gapped environments, and when local-development and CI fidelity matter more
  than ops savings.
- **A heavyweight log platform (partitioned commit-log systems)** — wins when
  throughput is genuinely high, when long retention makes the log a queryable
  history, or when an ecosystem of connectors is the actual draw. Loses badly at
  low throughput, where the operational surface dwarfs the workload. (Which
  broker product to pick is a separate evaluation and deliberately outside this
  pack.)
- **Per-consumer queue tables in the database (fanout on insert)** — wins when
  consumers are few and permanently known and you want durable per-consumer
  positions with no new infrastructure. Loses because the publisher must know the
  subscriber list, so every new consumer is a change to the publish path.
- **A durable-workflow platform as the consumer runtime** — wins when the work
  downstream of an event is a multi-step process with waits, human approvals, or
  scheduled retries. Loses when consumers are stateless transforms, where it is
  substantially more machinery than the job requires.
