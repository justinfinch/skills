---
type: Guidance
title: Enforcing an append-only source stream at the database-role level
description: Grant the writing role INSERT and nothing else on the table that everything else is derived from, revoke UPDATE and DELETE, make corrections new events rather than edits, dedup on a client-generated key, and keep large payloads outside the row by reference — because application-level immutability discipline is honoured ninety-five percent of the time and the other five percent is permanent.
tags: [append-only, immutability, event-stream, source-of-record, database-roles, idempotency, redaction]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:08:15Z }
status: stable
stale_after: 2029-06-01
sources:
  - id: helland-immutability
    resource: https://queue.acm.org/detail.cfm?id=2884038
    title: Pat Helland — Immutability Changes Everything (ACM Queue, 2015)
  - id: helland-life-beyond-dt
    resource: https://queue.acm.org/detail.cfm?id=3025012
    title: Pat Helland — Life beyond Distributed Transactions (ACM Queue, 2016)
  - id: fowler-event-sourcing
    resource: https://martinfowler.com/eaaDev/EventSourcing.html
    title: Martin Fowler — Event Sourcing
  - id: fowler-retroactive-event
    resource: https://martinfowler.com/eaaDev/RetroactiveEvent.html
    title: Martin Fowler — Retroactive Event
  - id: kleppmann-ddia
    resource: https://dataintensive.net/
    title: Martin Kleppmann — Designing Data-Intensive Applications (immutability, logs, and the limits of deletion)
  - id: postgres-grant
    resource: https://www.postgresql.org/docs/current/sql-grant.html
    title: PostgreSQL — GRANT
---

# Enforcing an append-only source stream at the database-role level

## Technique

The table that everything else is derived from is made append-only **by
privilege, not by policy**. The role the application and the workers use holds
`INSERT` on that table and nothing else; `UPDATE` and `DELETE` are revoked:

```sql
GRANT  INSERT         ON events TO app_writer;
REVOKE UPDATE, DELETE ON events FROM app_writer;
```

The enforcement point matters more than the rule. Application-level immutability
discipline — reject `UPDATE` in code, document the convention, trust the
practice — is honoured ninety-five percent of the time, and the five percent is
permanent. Every engineer who joins after the rule was written reaches for an
ORM that updates rows by default, and every coding agent writing against the
existing patterns in a file has no way to see a convention that lives in a
document. A grant is visible to all of them, in the only place that gets
consulted at write time.

**Corrections are new events.** A misparsed field, a wrong classification, a
mistaken capture: each is expressed as a further event that supersedes the
earlier one by reference, never as an edit. The stream keeps "what was recorded
at the time" and "what we later believed" as separate, both recoverable — which
is the entire point, since re-deriving through improved logic requires reading
the original inputs unmodified. Fix the schema at the design stage; you cannot
fix it by `UPDATE` afterwards.

**Every event carries a client-generated identifier as its dedup key** — a UUID
minted by whoever originates the event, unique-constrained on the table, with
insertion as `ON CONFLICT (dedup_key) DO NOTHING`. Client-side generation is
load-bearing: the server cannot recognize "this is a retry of the thing you sent
me three minutes ago" from content alone, especially when a payload was uploaded
before the row was created. The key must be minted once per logical event and
reused across every retry of it, not per attempt. This is one end of a longer
chain — see `guidance-event-delivery/concepts/end-to-end-idempotency.md` for the
hops downstream.

**Large payloads are referenced, never embedded.** Media, documents, and blobs
live in object storage; the row carries a reference plus the metadata worth
querying. Bytes in the row means the ingestion server touches every byte of
every upload, the store becomes a bottleneck at trivial scale, and — most
damaging — the replay the whole architecture depends on becomes a bulk
data-transfer problem instead of a table scan.

**Name the escape valve rather than pretending there isn't one.** Legal hold,
breach response, and court-ordered erasure are real. The escape valve is a
separate, audit-logged administrative session performed by a human, not a grant
handed to a service. Writing it down is what keeps it from being invented under
pressure and then quietly reused.

## Applies when

- **The table is genuinely a source of record** — the thing everything else is
  derived from, and those derived things are rebuildable from it. This is the
  reciprocal of [rebuildable-projections.md](rebuildable-projections.md): the
  rebuild guarantee is only as strong as this table's immutability.
- **You intend to re-derive later through improved logic**, which requires the
  original rows to read identically years from now. If nothing will ever re-read
  the history, the guarantee is unfunded.
- **Duplicate arrival is expected.** Mobile clients, flaky networks, at-least-
  once ingestion, retried uploads. The dedup key stops being a nicety and
  becomes the thing that makes append-only survivable.
- **An audit or evidentiary story depends on "as captured" being recoverable** —
  regulatory, contractual, or simply a dispute you expect to have.
- **You control the schema and the database roles.** Role-level enforcement is
  unavailable on platforms that hand you one connection string with owner
  privileges, and the technique degrades to convention there.
- **Large payloads have a natural home outside the row**, i.e. object storage
  exists in the architecture already.

## Doesn't apply when

- **Legal erasure obligations require destroying rows in place and no
  redaction-by-reference design exists.** Redaction-by-reference is the usual
  way out: the sensitive payload lives outside the row, the row carries a
  reference and a redaction state, and destroying the payload satisfies erasure
  while the row and the stream's shape survive. Crypto-shredding — encrypting
  per-subject and discarding the key — is the other form. But if the personal
  data is in the row's own columns and cannot be moved out, in-place deletion is
  a hard requirement and this technique is the wrong enforcement: an append-only
  grant that must be bypassed on a compliance clock will be bypassed badly.
  Decide this before the schema, not after the first erasure request.
- **The table is not actually a source of record.** A working table, a cache, a
  scratch queue, a staging area. Append-only there is cargo cult with a real
  bill: dead-tuple churn, unbounded growth, and a convention that trains people
  to route around it.
- **The row must carry mutable lifecycle state.** This is the tempting one. A
  `status` column gets added to the stream table — "captured / processed /
  failed" — and now the table needs `UPDATE`. What has happened is that an
  aggregate has been merged into a stream. Separate them: the stream row is what
  happened, and the mutable state belongs on an aggregate table or in the
  projection.
- **Schema churn is expected and unavoidable.** Append-only constrains
  migrations to `ADD COLUMN` with defaults; you cannot backfill a column with an
  `UPDATE`, and an `ALTER COLUMN` that rewrites rows is off the table. A schema
  still being discovered weekly will fight this constantly.
- **The stream must be consumed outside the database with log semantics** —
  partitioned consumers, compaction, retention tiers, replay from an offset. A
  log product is the better home for that shape, at the cost of losing the
  single-transaction atomicity with the aggregate write.

## Trade-offs

Buys a permanently recoverable input set: every re-derivation reads exactly the
bytes the first one did, which is what turns "we can improve the logic later"
from an aspiration into a property. Buys idempotent ingestion as the default
rather than a feature someone remembers to add. Buys an audit trail that is the
data rather than a parallel log that can disagree with it. And buys the
rebuild guarantee real teeth — without this page, that guarantee rests on
nobody having edited anything.

Costs the convenience of correction. A fix is a new row, so every reader must
understand supersession, and "the current view of event X" becomes a query with
a rule in it rather than a primary-key lookup. Costs migration flexibility, as
above. Costs storage that is never reclaimed — and the obvious relief valve, a
retention policy, is precisely the thing you have promised not to do. Costs a
redaction design that has to be built before it is needed, because it cannot be
retrofitted with a `DELETE`.

The quality attributes this moves are **integrity**, **auditability**, and
**evolvability**. It pays for them in **modifiability** of the schema and in
**operational flexibility** — the ability to just fix a bad row, which teams
routinely value more highly than they admit until it is gone.

**State the ordering and consistency model, because a downstream projector will
otherwise assume one.** Append-only guarantees that a row, once visible, never
changes. It does **not** guarantee global ordering. Sequence numbers and
timestamps are assigned before commit, so a row can become visible *after* a
reader has already passed its position — a cursor over `created_at` or over a
sequence will silently skip rows committed out of order, with no error anywhere.
What you actually have is: immutability per row, whatever ordering you
explicitly enforce per key, and no total order unless inserts are serialized,
which they are not. Consumers that need ordering need it stated and provided,
not inferred from a monotonically-increasing-looking column.

**What would make this stale.** Two things. If regulatory erasure regimes
tighten to the point that reference-based redaction and crypto-shredding are no
longer accepted as erasure — a live argument, not a settled one — then in-place
deletion becomes mandatory for any stream touching personal data, and the
counter-case above swallows most real systems. Separately, if managed database
platforms ship first-class immutable or ledger-typed tables with
cryptographically verifiable history and built-in redaction primitives, the
hand-rolled grant split becomes a weaker version of a feature you have.

## Failure modes

- **"Just this one fix" migrations that bypass the role.** The 3am failure in
  disguise, because it is silent and permanent. Migrations run as an owner or
  superuser role, so the grant does not protect against them — someone corrects
  a batch of rows in a migration, it passes review because migrations always
  contain DML, and the guarantee is void with no alarm, no failing test, and no
  symptom until a rebuild produces rows nobody can explain. The only defence is
  a check on the migration path itself: no `UPDATE` or `DELETE` against the
  stream table in any migration, asserted in CI.
- **Blob payloads bloating the stream until replay is impractical.** It starts
  as one small embedded field and grows. Backup and restore cost compounds; the
  ingestion path touches every byte; and the replay that the entire
  rebuildability story depends on quietly becomes a multi-day data-transfer job.
  The architecture is still correct on paper and no longer operable.
- **Corrections accumulating with no supersession convention.** Three rows about
  the same fact and no rule for which one wins. Each reader invents its own —
  latest by timestamp, highest id, most-fields-populated — and two readers
  disagree about the same entity. Decide supersession semantics when you decide
  append-only, because the two are the same decision.
- **The dedup key generated per attempt rather than per event.** A retry mints a
  fresh UUID, the `ON CONFLICT` never fires, and the duplicate is now permanent
  in a table you cannot delete from. This is worse in an append-only stream than
  anywhere else, precisely because the usual cleanup is unavailable.
- **Dedup keys colliding or being reused.** A client that regenerates local
  state and replays old keys, or a key namespace that is not tenant-scoped,
  turns `DO NOTHING` from a safety net into silent data loss — the second event
  is genuinely new and is dropped without a trace.
- **Retention quietly enabled for cost.** The table grows, the storage line item
  is noticed, and someone adds a ninety-day retention policy in an
  infrastructure change. The rebuild guarantee dies without a single alarm and
  the durability split on
  [rebuildable-projections.md](rebuildable-projections.md) becomes unfunded. Put
  the "no retention on this table" rule where the infrastructure lives, not only
  in an architecture document.
- **The escape valve becoming routine.** The audit-logged administrative session
  is used monthly, then weekly, then a service account is granted the
  privilege "temporarily." Check who holds `UPDATE`/`DELETE` on the stream table
  as a standing assertion, not as a one-off audit.
- **A soft-delete flag treated as deletion by every reader.** A `deleted_at`
  column is added, every query filters on it, and the stream is now effectively
  mutable with none of the audit benefit — the rows are there but nothing reads
  them, so a rebuild reproduces a history the product denies exists.
- **An ORM auto-migration that rewrites the table.** Adding a `NOT NULL` column
  without a default, or changing a column type, can force a full table rewrite —
  which the owner role will happily perform. Large stream tables also make this a
  lock-duration incident, so it fails loudly on the way to failing permanently.

## Alternatives considered

- **Application-level immutability discipline** — wins in a small team with
  total review coverage, no ORM, and no agents writing code. Loses for the
  reason this page exists: it is honoured almost always, and the exceptions are
  irreversible.
- **Triggers that reject `UPDATE` and `DELETE`** — wins when you cannot control
  roles at all, which is common on managed platforms that give you one
  owner-privileged connection. Loses because a role that can write can usually
  disable the trigger, and because per-row trigger cost lands on the hottest
  insert path in the system. Reasonable as a second layer, weak as the only one.
- **Soft mutability with an audit-log row per change** — wins when the audit
  trail is the requirement and the original bytes are not. Loses the
  re-derivation guarantee outright unless the audit stores complete
  before-images, at which point you have built an append-only stream with extra
  steps and a mutable table in front of it.
- **An external log or event-store product** (a broker with long retention, a
  purpose-built event store) — wins when the stream must be consumed outside the
  database with log semantics, or when retention tiering and compaction are the
  point. Loses the same-transaction atomicity between the aggregate write and
  the append, which is the property that makes the write path's guarantees
  simple; see `guidance-event-delivery` for what you take on instead.
- **Blob bytes stored in the row** — wins for genuinely small payloads that must
  commit atomically with the event and are always read together with it. Loses
  at any scale, and loses the replay story first.
- **Content-hash dedup keys instead of client-generated identifiers** — wins
  when originators cannot mint stable identifiers and the full payload is
  available at insert time. Loses when the payload is uploaded before the row
  exists, and loses when two legitimately distinct events have identical
  content, which collapses them into one.
- **Full event sourcing, where the stream is also the command model's state** —
  wins when current state is genuinely a fold over history and the history is
  the valuable artifact. This page is the cheaper commitment: append-only on
  *evidence*, with aggregate rows still holding current state. Full event
  sourcing loses when most reads want current state and nobody wants
  snapshotting machinery.
