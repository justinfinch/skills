---
name: guidance-clean-architecture
description: >-
  Clean Architecture as a pragmatic synthesis — the Dependency Rule (source
  dependencies point toward policy; the core imports nothing
  framework-flavored) as the invariant, layers collapsing when they would be
  pass-through; ports and adapters with the driving/driven asymmetry,
  consumer-declared ports, and a write-side-only repository; a use-case layer
  sliced by feature; sociable tests driven through use-case boundaries; and
  the hexagonal/onion/BCE lineage. Examples assume TypeScript/Node; the
  reasoning is stack-agnostic. Use when structuring a new service or app,
  asking where business logic should live, whether to abstract the ORM or
  framework, whether a use-case or service layer is warranted, how to test
  domain logic without a database, or when framework code and business rules
  have grown together. Monorepo topology is guidance-monorepo; endpoint and
  folder organization is guidance-vertical-slices; the domain model's content
  is guidance-ddd; CI boundary enforcement is guidance-fitness-functions.
---

# guidance-clean-architecture

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages, plus a supporting `Concept` page on the
pattern family's lineage.

## How to use this pack

1. Read [bundle/index.md](bundle/index.md), then the pages relevant to the
   decision actually in play. The pages are ordered: `dependency-rule` is the
   invariant the other three assume; read it first when structuring something
   new, and read the lineage page only when the vocabulary itself is in
   dispute. Each technique page is walked condition by condition, not skimmed
   for the recommendation.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as `guidance-clean-architecture/<path-within-bundle>`,
   so the rationale outlives the conversation. In an Arche, that record is the
   ADR and the citation goes in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
