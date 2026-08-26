---
name: guidance-ddd
description: >-
  Strategic domain-driven design — whether a domain model is warranted at all,
  which subdomains deserve the investment (core, supporting, generic), where
  bounded-context boundaries belong, how to relate two contexts (anticorruption
  layer, conformist, shared kernel, customer/supplier, published language,
  separate ways), and how to size aggregates as consistency boundaries. Use
  when starting a greenfield system in a business domain, shaping a new
  system's domain model or schema, drawing or reviewing service and context
  boundaries, splitting a monolith, integrating systems owned by different
  teams, choosing between transactional and eventual consistency, when the same
  business term means different things to different teams, or when the user
  mentions DDD, domain modelling, ubiquitous language, bounded contexts,
  context maps, aggregates, or event storming. The first page is the case
  against adopting DDD at all. Strategic design only; tactical patterns
  (entities, value objects, repositories) are out of scope.
---

# guidance-ddd

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Start at [strategic-ddd.md](bundle/concepts/strategic-ddd.md) — it is the
   gate in front of the other four. Bounded contexts, context maps, and
   aggregates are machinery that only pays off once *that* decision has been
   made deliberately. Reading them first is how a project ends up with the cost
   of DDD and none of the benefit. Directly behind the gate sits
   [core-domain.md](bundle/concepts/core-domain.md): the commitment cannot hold
   everywhere, so decide where it holds before drawing any boundary.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as `guidance-ddd/<path-within-bundle>`, so the
   rationale outlives the conversation. In an Arche, that record is the ADR and
   the citation goes in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

Two distinctions this pack keeps separate, because conflating them is where
most of the damage happens: **where a boundary belongs** is not **how small the
pieces should be**, and **an aggregate boundary** is a statement about the
consistency model rather than an object-modelling preference.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
