---
name: guidance-vertical-slices
description: >-
  Vertical-slice organization in one application, at two layers — REPR
  (Request–EndPoint–Response) endpoint slices on the API side, one route per file
  named for the command or query it calls, wired by a registration helper that is
  deliberately not a command bus; and by-feature folders on the client side, with a
  knows-business-logic sorting rule, features as non-importing peers, and
  direction-only import boundaries enforced by a dependency tool. Plus where shared
  code goes — the shape constraints that keep a controller from reassembling in a
  sliced tree. Use when organizing endpoints or components, when a routes or resource
  file has grown several routes, when a components folder is unwieldy, when
  features import each other, when deciding where shared error mapping or middleware
  belongs, when weighing vertical slice architecture, feature folders, or
  Feature-Sliced Design, or when writing dependency-cruiser or import-boundary rules.
  Not service granularity — a deployment question — nor a framework recommendation.
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
2. Read [shared-code-between-peers.md](bundle/concepts/shared-code-between-peers.md)
   whenever either layer is actually being adopted, and not only when someone
   asks where a shared helper goes. It covers the pressure the other two pages
   create and do not relieve: peers may not import each other, so the code they
   would have shared has to live *somewhere*, and wherever it lands acquires
   gravity. That page is where the hub comes back, and it is the reason a sliced
   tree quietly becomes the controller it replaced.
3. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so. The most common wrong adoption for the two layer pages
   is the same one: a codebase small enough that a single routes file, or a
   single components folder, is still legible end to end.
4. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-vertical-slices/<path-within-bundle>`, so the rationale outlives
   the conversation. In an Arche, that record is the ADR and the citation goes
   in its `sources:`.
5. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
6. Every page here depends on invariants a machine checks — one route per slice
   file, every slice reachable from the composition root, no slice or feature
   importing a sibling, no inline handler in the composition file, nothing but
   functions in a shared module. Carry the checks into whatever record cites the
   page. Unenforced, all three techniques decay into directory trees that *look*
   like boundaries, which is worse than the flat layout they replaced, because a
   reader now believes a boundary exists.
7. Note where the checks go, not just that they exist. A guard placed where the
   last failure happened watches the wrong place for the next one: once slices
   exist, the composition root is the one location that stops eroding, and the
   slice tree — which nothing is reading — is where the controller regrows.

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
