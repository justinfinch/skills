---
name: guidance-vertical-slices
description: >-
  Vertical-slice organization inside a single application, at two layers — REPR
  (Request–EndPoint–Response) endpoint slices on the API side, each route owning
  its schema-validated request, a thin handler that calls exactly one command or
  query, and a response DTO, wired by a registration helper that is deliberately
  not a command bus; and a by-feature folder taxonomy on the client side, with a
  knows-business-logic sorting rule, features as non-importing peers, and
  direction-only import boundaries enforced by a dependency tool rather than by
  review. Use when deciding how to organize endpoints or components, when a
  routes file or a flat components folder has grown unwieldy, when features have
  started importing each other, when weighing vertical slice architecture,
  feature folders, or Feature-Sliced Design, or when writing dependency-cruiser
  or import-boundary rules. Not service granularity — that is a deployment
  question — and not a framework recommendation.
---

# guidance-vertical-slices

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Read [bundle/index.md](bundle/index.md), then the page for the layer in play:
   [repr-endpoints.md](bundle/concepts/repr-endpoints.md) for an HTTP boundary,
   [feature-folder-organization.md](bundle/concepts/feature-folder-organization.md)
   for a client application's source tree. Then read the other one anyway. They
   are **one principle at two layers** — slice by capability, keep the slices
   from importing each other, leave the composition root doing nothing but
   composing — and each page's reasoning is the shorter half of the argument on
   its own. Their conditions are independent, so adopting one without the other
   is a coherent outcome; what is not coherent is adopting one and never having
   read why the same move was or wasn't right at the other layer.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so. The most common wrong adoption for both pages is the
   same one: a codebase small enough that a single routes file, or a single
   components folder, is still legible end to end.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-vertical-slices/<path-within-bundle>`, so the rationale outlives
   the conversation. In an Arche, that record is the ADR and the citation goes
   in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
5. Both pages depend on an invariant a machine checks — no inline handlers in
   the composition file; no feature importing a sibling. Carry the check into
   whatever record cites the page. Unenforced, both techniques decay into
   directory trees that *look* like boundaries, which is worse than the flat
   layout they replaced, because a reader now believes a boundary exists.

**A boundary claim is not a granularity claim.** Everything here is about how
source inside one deployable is arranged. It says nothing about how many
services there should be or where a process boundary belongs — those carry
latency, partial failure, and independent deployment, and are decided on their
own grounds. Slices are cheap and reversible; services are not, and "we already
have vertical slices, so each could be a service" is how a clean layout becomes
an unplanned distributed system.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
