---
name: guidance-cqrs-projections
description: >-
  Command–query separation over a single relational database — three models (a
  command model whose unit of work is one aggregate in one transaction, a
  projection model owning the derivation logic, and a thin DTO query model that
  never touches the domain), conditional aggregate hydration, read projections
  written only by projection workers and stamped with a projector version,
  rebuildable on a CI-verified time budget with zero durability targets instead
  of backups, append-only source streams enforced by database-role grants, and
  eventual read-your-writes via an optimistic client echo. Use when reads are
  getting slow or complex, when designing read models, feeds, or ledger-style
  surfaces, when arguing event sourcing versus CRUD, when asking whether a
  derived table can be rebuilt or has to be backed up, or when a query path has
  started importing domain code. Not full CQRS with separate read stores;
  strategic aggregate sizing lives in guidance-ddd.
---

# guidance-cqrs-projections

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Start with [cqrs-lite.md](bundle/concepts/cqrs-lite.md). It is the gate: if
   the read shape matches the write shape, plain CRUD is the right answer and
   nothing else in this pack is worth its cost — that page says so in its
   **Doesn't apply when**, and it is the most common wrong adoption. The other
   two pages are only reachable through it.
   [rebuildable-projections.md](bundle/concepts/rebuildable-projections.md)
   decides what the projection model's tables are *worth* — whether they are
   derived data you can drop and replay, or a primary store that needs real
   backups — and
   [append-only-source-stream.md](bundle/concepts/append-only-source-stream.md)
   is the same decision seen from the other end, since a rebuild guarantee is
   only as strong as the immutability of what it replays from. Read those two
   together or neither: adopting the rebuild story without the append-only
   enforcement is precisely how the guarantee becomes a belief.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-cqrs-projections/<path-within-bundle>`, so the rationale outlives
   the conversation. In an Arche, that record is the ADR and the citation goes
   in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
5. Every page here fixes a consistency model, and each one states its own.
   Carry that statement into whatever record cites the page. A recommendation
   from this pack repeated without "reads are eventually consistent," "the
   stream has no global order," or "a rebuild leaves reads incomplete, not
   merely stale" has dropped the half that determines whether it was ever the
   right call.

The distinction the pack exists to keep sharp: **separating the paths, owning
the derived data, and protecting the source are three separate decisions.**
Three models buys read shapes that write shapes can't serve, and says nothing
about whether the projection tables can be recreated. A rebuild guarantee makes
derived tables cheap to lose, and says nothing about whether the source it
replays from is intact. Append-only protects the source, and says nothing about
how anything reads it. Solving one and assuming the others is how a system ends
up with a table everyone calls a projection and nobody can rebuild.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
