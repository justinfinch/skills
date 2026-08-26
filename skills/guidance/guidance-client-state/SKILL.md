---
name: guidance-client-state
description: >-
  Client state in React/TypeScript apps — a four-way taxonomy giving each kind
  its own store: server state in a query cache (TanStack Query), ephemeral UI
  state in a light store (Zustand) or component state, durable pending writes in
  a purpose-built persistent queue rather than the query library's mutation
  cache, and SSE or WebSocket push events patching the query cache, which is
  where an eventually-consistent backend's optimistic read-your-writes echo
  lives on the client; plus store-and-forward capture, a deliberately narrower
  promise than offline mode that makes one named write path unlosable. Use when
  asking where a piece of state should live, choosing between Redux, a query
  library and Zustand, chasing data that is stale after a mutation, deciding
  whether a field or mobile workflow must survive dead connectivity, or asking
  whether you need offline mode. Not local-first sync engines; not server-side
  caching.
---

# guidance-client-state

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Start with
   [client-state-taxonomy.md](bundle/concepts/client-state-taxonomy.md) and walk
   it as a sorting exercise: take the state actually in front of you, put each
   piece into one of the four kinds, and read the ownership rules for the kinds
   you landed in. Most questions this pack is loaded for are answered there.
   [store-and-forward-capture.md](bundle/concepts/store-and-forward-capture.md)
   is the taxonomy's third kind priced in full, and it is reached *only* by
   passing its **Doesn't apply when** — the great majority of applications
   should read it and conclude that a visible failure and a retry button is the
   honest answer. Read it whenever "do we need offline mode" is asked, because
   the useful reply is usually a narrower question about one write path.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as `guidance-client-state/<path-within-bundle>`,
   so the rationale outlives the conversation. In an Arche, that record is the
   ADR and the citation goes in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
5. Both pages state a consistency model, and both are weaker than they look: the
   query cache is an eventually-consistent replica with no read-your-writes
   guarantee beyond the one the optimistic echo simulates, and the capture queue
   delivers at-least-once with per-device ordering only. Carry those statements
   into whatever record cites the page. A screen that cannot tolerate them has
   to fetch fresh and say so.

The pack's stack scoping is deliberate. The four kinds, the ownership rules, and
the scope-the-offline-promise move are stack-agnostic reasoning; the named
libraries are the ecosystem the evidence came from. An agent working in another
ecosystem should keep the taxonomy and re-derive the assignment — which
component owns the server cache, what "durable" actually guarantees on that
platform, and whether the framework has already claimed one of the four kinds.
Each page says which of its parts transfer and which must be re-derived.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
