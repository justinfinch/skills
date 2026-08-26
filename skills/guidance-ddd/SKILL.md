---
name: guidance-ddd
description: >-
  Strategic domain-driven design — whether the modelling investment is warranted
  at all, where a bounded-context boundary belongs, how to name the relationship
  between two contexts, and how to size an aggregate's consistency boundary.
  Strategic design only; tactical patterns (entities, value objects,
  repositories) are code-level and deliberately out of scope. Consult when a
  design touches domain modelling, service or context boundaries, integration
  between systems owned by different teams, or transactional consistency
  boundaries — and especially before adopting DDD, since the first page is the
  case against it. Read `bundle/` and cite the pages that inform a decision in
  that decision's record — in an Arche, the ADR's `sources:`. This pack is
  knowledge, not a workflow — it decides nothing on its own and writes nothing.
---

# guidance-ddd

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Start at [strategic-ddd.md](bundle/concepts/strategic-ddd.md) — it is the
   gate in front of the other three. Bounded contexts, context maps, and
   aggregates are machinery that only pays off once *that* decision has been
   made deliberately. Reading them first is how a project ends up with the cost
   of DDD and none of the benefit.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as `guidance-ddd/<path-within-bundle>`, so the
   rationale outlives the conversation.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

Two distinctions this pack keeps separate, because conflating them is where
most of the damage happens: **where a boundary belongs** is not **how small the
pieces should be**, and **an aggregate boundary** is a statement about the
consistency model rather than an object-modelling preference.

## What this pack is not

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
