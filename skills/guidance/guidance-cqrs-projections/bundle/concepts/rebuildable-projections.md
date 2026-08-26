---
type: Guidance
title: Treating read projections as rebuildable rather than backed up
description: Let projection workers be the only writers of derived read tables, stamp every row with the projector version that produced it, and buy safety with a rebuild guarantee on a CI-verified time budget instead of a backup — which means splitting durability targets deliberately, strong for the source stream and zero for everything derived from it.
tags: [projections, read-models, rebuild, durability, projector-version, derived-data, backfill]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:08:15Z }
status: stable
stale_after: 2029-06-01
sources:
  - id: kleppmann-ddia
    resource: https://dataintensive.net/
    title: Martin Kleppmann — Designing Data-Intensive Applications (systems of record vs. derived data)
  - id: fowler-event-sourcing
    resource: https://martinfowler.com/eaaDev/EventSourcing.html
    title: Martin Fowler — Event Sourcing
  - id: fowler-retroactive-event
    resource: https://martinfowler.com/eaaDev/RetroactiveEvent.html
    title: Martin Fowler — Retroactive Event
  - id: young-es-versioning
    resource: https://leanpub.com/esversioning
    title: Greg Young — Versioning in an Event Sourced System
  - id: azure-materialized-view
    resource: https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view
    title: Azure Architecture Center — Materialized View pattern
  - id: helland-immutability
    resource: https://queue.acm.org/detail.cfm?id=2884038
    title: Pat Helland — Immutability Changes Everything (ACM Queue, 2015)
  - id: vogels-eventually-consistent
    resource: https://queue.acm.org/detail.cfm?id=1466448
    title: Werner Vogels — Eventually Consistent (ACM Queue, 2008)
---

# Treating read projections as rebuildable rather than backed up

## Technique

Derived read tables are written by **projection workers and by nothing else** —
enforced at the database-role level, not by convention. The API role has
`SELECT` on the projection tables and no write grants at all; the worker role
has the writes. That single grant split is what makes "no request path writes a
projection" a property of the database rather than a rule in a style guide, and
it is assertable as a check against the live grants
(`projection-path-has-no-write-access`) rather than against the code — see
`guidance-fitness-functions`.

Every projection row carries a **`projector_version`** column identifying the
logic that produced it. Version is the unit of generational evolution:
improved logic writes v2 rows alongside the v1 rows, readers select the current
version, and v1 rows are retired as a deliberate cutover once v2 has caught up.
Projectors are **idempotent**, keyed on `(source event ids, projector_version)`
as a natural key, so a replay produces the same row rather than a second one.

The table carries an explicit **rebuild guarantee**: dropping it and replaying
every projector against the source stream reproduces it, within a stated time
budget, and **that budget is verified in CI** — a scheduled job that rebuilds
against a production-shaped dataset and fails when it exceeds the number
(`rebuild-within-budget`). A rebuild guarantee that is never exercised is not a
guarantee; it is a belief that other decisions are resting on.

Then the move this whole page exists for: **split the durability targets
deliberately.**

| Data | Durability target | What buys the safety |
| :--- | :--- | :--- |
| Source event stream, and any referenced payloads | The strong number — 11 nines class, cross-region replication, the works | Replication and backup |
| Projection tables | **Zero** | The rebuild path, on its budget |

Projections get **zero nines** on purpose. They are mathematically reproducible
from the source plus the projector version, so backing them up duplicates cost
without adding safety — and a restored projection is a set of rows from an
older projector version that now silently disagrees with the source, which is
worse than having no backup at all. **Rebuildable-within-budget replaces
backed-up.** The reason to say this explicitly is that a single "reliability"
number applied across the board simultaneously over-commits on the largest and
fastest-growing tables in the system and under-protects the one dataset that is
genuinely irreplaceable.

The reciprocal obligation is on the source: this only works if the source
stream is complete and immutable. See
[append-only-source-stream.md](append-only-source-stream.md) — the two pages are
one decision viewed from either end, and adopting this one without that one is
the failure mode described below.

## Applies when

- **An authoritative event or observation stream exists and is retained in
  full.** This is the load-bearing condition. Everything else on this page is
  downstream of it.
- **The projection's contents are a deterministic function of that stream** —
  same inputs, same projector version, same rows. Determinism is what makes
  "rebuild" a restore rather than a re-decision.
- **Derivation logic is expected to improve.** You intend to re-derive old
  inputs through better logic later; `projector_version` is what makes that a
  rollout instead of a migration.
- **Read latency budgets rule out computing on the read path.** If the query
  could be computed per-request within its p95, there is no projection table to
  make rebuildable.
- **Someone will own the rebuild number.** A named budget ("full rebuild under
  N hours") that a person defends as data grows, backed by a scheduled check.
  Without an owner, the budget decays into folklore between the day it is
  written and the day it is needed.
- **The read surface can tolerate degradation for the length of a rebuild**, and
  product has agreed to that in writing — not been assumed into it.

## Doesn't apply when

- **Source events are pruned, sampled, or were never complete.** *A projection
  you cannot rebuild is a primary store wearing a costume.* Give it real
  durability targets — backups, point-in-time recovery, a tested restore — and
  stop calling it derived. The costume is dangerous precisely because it is
  convincing: the table is named like a projection, written by a worker, and
  documented as reproducible, so nobody backs it up, and the gap is invisible
  until a restore is needed.
- **Rebuild time exceeds tolerable staleness and no incremental path exists.** A
  six-hour full rebuild against a thirty-minute recovery objective is not a
  safety story. Either build the incremental path (periodic snapshot plus delta
  replay, or per-partition rebuild that restores the hot slice first), or accept
  that this table needs backups.
- **Derivation is non-deterministic and not pinned.** The projector calls a
  model, a third-party classifier, or an external service whose output changes
  over time. A rebuild then produces *different* rows, and nobody can say which
  set is correct. Two honest fixes: record the external output as source data at
  the time it was obtained (making the projector deterministic over a richer
  stream), or treat the projection as primary and back it up. Deciding not to
  choose is how you get a table that is neither.
- **Humans edit projection rows as part of the workflow.** A correction workflow
  that writes to the projection has made those edits source data living in a
  derived table. Either route corrections into the source stream as events, or
  the table is primary.
- **The projection is the only place some fact ever existed** — a
  projection-time timestamp, an externally-assigned identifier captured on
  first write, a monotonic counter. Those fields do not survive a rebuild
  intact, and one such column is enough to make the whole table
  non-reproducible.
- **The table is small and cheap to back up and the derivation is trivial.** The
  rebuild machinery — the version column, the idempotency key, the scheduled
  budget check, the retirement process — has real cost. A thousand-row lookup
  table does not need it.

## Trade-offs

Buys the removal of an entire operational concern — backup, restore, and
point-in-time recovery — from the largest and fastest-growing tables in the
system, and replaces it with a path you exercise routinely rather than a
procedure you rehearse annually and hope about. Buys safe projector evolution:
drop, replay, compare is a testable operation, so improving derivation logic
stops being a schema migration and becomes a version rollout. Buys the property
that **projection workers are stateless transforms rather than owners of
irreplaceable state**, which is what makes them free to kill, redeploy, scale,
and rewrite.

Costs idempotence and determinism as hard requirements on every projector, which
constrains what derivation logic is allowed to do — no reading the clock, no
unrecorded external calls, no dependence on processing order that the stream
does not guarantee. Costs a scheduled rebuild job and a synthetic dataset that
has to grow with production, or the check measures a world you left behind.
Costs a version-retirement process that is deliberate and manual. Costs a
degraded-reads window during any real rebuild.

The quality attributes this moves are **recoverability** and **evolvability**.
It pays for them in **availability of the read surface** during a rebuild, in
**CI time**, and in **constrained projector design**. Note what it does *not*
move: it does nothing for read latency, correctness, or write throughput. If a
proposal to "make it rebuildable" is sold on any of those, the reasoning has
drifted.

The consistency model is worth stating alongside the durability one: projections
are **eventually consistent with the source, with no upper bound on lag except
the one you alarm on**, and during a rebuild they are *incomplete* rather than
merely stale — a semantically different state that reads must be able to
distinguish. A query that cannot tell "not projected yet" from "not true"
will report absence as fact for the whole rebuild window.

**What would make this stale.** Two futures. If engines you actually run ship
incremental view maintenance general enough to express real derivation logic and
maintain it transactionally, then `projector_version`, the worker fleet, and the
rebuild budget become machinery for something the storage layer does — and
"rebuild" becomes a DDL operation with a plan. Separately, if rebuild-from-
source gets cheap enough to run continuously — blue/green projections rebuilt on
every projector deploy — then the budget stops being a recovery SLO and becomes
a routine build time, and this page's framing of it as a safety guarantee is the
wrong emphasis.

## Failure modes

- **The rebuild budget is silently blown as data grows.** This is the central
  one. A rebuild that took forty minutes when the budget was written takes five
  hours two years later, and nothing announced the crossing, because the number
  was never measured after the day it was chosen. The scheduled rebuild check is
  the alarm — and it should alarm on the **trend**, not just the threshold: a
  rebuild at 80% of budget and climbing is the signal, and a rebuild that first
  fails on the day you need it is the outcome without one. When this fails, it
  fails at the worst possible moment, because the moment you need a rebuild is
  by definition a moment something else is already wrong.
- **A projector deploy writes wrong rows for hours, and the fix reveals the
  rebuild was never real.** The 3am shape of the previous entry. The remedy for
  bad projector logic is always "fix and replay," so the replay path is on the
  critical path of every projection incident. If it has only ever been run
  against a fixture, you find out during the incident.
- **The projection path acquires write access to the source.** Someone gives the
  worker role broader grants for an unrelated reason — a migration, a shared
  role, a convenience — and a projector "fixes" a source row. The rebuild
  guarantee is now void and nothing reports it, because the corrupted input
  produces perfectly consistent output on the next replay. Enforce at the
  database-role level and check the grants, not the code.
- **Hand-edits to projection rows that vanish on rebuild.** A support engineer
  corrects a wrong row with a `UPDATE` in a console. It works. Weeks later a
  routine rebuild silently reverts it, and nobody connects the two events
  because they are separated by weeks and by teams. This is the failure that
  destroys trust in the projections rather than in the process, which is the
  wrong lesson to learn. Revoke the grants that make it possible.
- **Non-determinism discovered mid-rebuild.** The replay finishes and the rows
  differ from the originals. Now there is no oracle: the old rows and the new
  rows are both plausible, the diff is thousands of rows deep, and the decision
  is being made under incident pressure. The defence is a comparison rebuild run
  routinely against a slice, so drift is discovered on a Tuesday.
- **Partial rebuild that looks complete.** The replay stops early on an error —
  a poison event, a worker OOM, a connection reset — leaving the table with most
  of its rows. Reads succeed. Dashboards fill. Nothing distinguishes "rebuilt"
  from "80% rebuilt" unless the rebuild writes a completion marker that queries
  actually check.
- **Version proliferation.** v1, v2, and v3 rows coexist because retirement is a
  manual process nobody scheduled. Queries acquire `WHERE projector_version =
  (SELECT MAX(...))` subqueries, the table is three times the size it needs to
  be, the rebuild budget triples with it, and dropping an old version becomes
  scary because some query somewhere might still pin it.
- **The rebuild saturates the database the write path depends on.** Replay is
  the heaviest sustained write load the system ever produces, and it runs
  against the same store serving commands. A rebuild triggered during peak turns
  a read-surface degradation into a capture-path outage.
- **"We can always rebuild" is load-bearing and unfunded.** The durability
  decision, the backup bill, and the storage architecture all rest on this
  belief. Untested, the belief is the single point of failure for all three, and
  it is the cheapest thing on this page to verify.

## Alternatives considered

- **Back up the projections like every other table** — wins when derivation is
  non-deterministic, the source is pruned, rebuild exceeds the recovery
  objective, or the table carries facts that exist nowhere else. Loses on cost
  and on truth when the projection really is reproducible: a restored
  projection is old logic's output masquerading as current.
- **Materialized views maintained by the database** — wins when derivation is
  expressible in SQL, refresh atomicity is acceptable, and nobody needs
  generational rollout. Loses when derivation needs code, when v2 logic must run
  alongside v1 during a cutover, or when the version stamp needs to live on the
  row: view DDL does not carry `projector_version` cleanly, and refresh is
  all-or-nothing rather than projector-by-projector.
- **Compute on the read path, no projection table at all** — wins at low query
  volume with generous latency budgets, and it is the simplest thing that could
  work. Loses against p95 targets, and loses harder when derivation is expensive
  enough that caching becomes the real design.
- **Cache with a TTL in front of computed reads** — wins when the computation is
  cheap-ish and staleness is the only concern. Loses when the read spans many
  aggregates, when the derivation logic itself must be versioned, or when the
  read must be queryable (filtered, sorted, paged) rather than merely fetched.
- **Snapshot plus incremental delta replay** — wins when a full rebuild exceeds
  the budget but the source stream is intact; it is the correct escape hatch
  from this page's second counter-case rather than a rejection of the approach.
  Loses on complexity: two paths to maintain, and the snapshot is now state that
  needs its own durability answer.
- **Project into a separate read store** — full CQRS. Wins when read scaling or
  a different index shape drives it. Loses as a durability strategy: the
  rebuildability argument is unchanged by where the rows live, so this is an
  orthogonal decision that is often mistaken for this one.
