---
name: guidance-portability-seams
description: >-
  Keeping expensive platform commitments reversible — a named escape valve (the
  specific alternative you would move to, per layer) plus measurable per-layer
  migration triggers on cost, latency, consumer count or a named feature gap,
  written at commitment time; and commodity-standard APIs as the seam between the
  system and the vendor, such as the S3 API spanning a local double, cloud
  interop and an alternative provider, or a provider interface owned by the
  domain layer for auth, with the local development double honoring the same seam
  and chosen on upstream health rather than popularity. Use when choosing a cloud
  platform or a managed service, asking whether you are locked in, running a
  vendor lock-in or exit review, deferring an adoption decision behind a
  threshold, or picking a local development stand-in for a cloud service. Not a
  multi-cloud advocacy piece; not a cloud-provider comparison.
---

# guidance-portability-seams

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. The two pages answer different halves of one question and are read in the
   order the decision arrives.
   [named-migration-triggers.md](bundle/concepts/named-migration-triggers.md)
   comes first when a commitment is being made — it decides *whether* this
   commitment deserves a written escape valve at all, and its **Doesn't apply
   when** is where most commitments should stop.
   [standard-api-seams.md](bundle/concepts/standard-api-seams.md) comes first
   when code is being written against a provider, because that is when the seam
   is cheap. Read both when either fires: a trigger with no seam behind it is a
   promise nobody can keep, and a seam with no trigger in front of it is
   portability work with no stated payoff.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-portability-seams/<path-within-bundle>`, so the rationale outlives
   the conversation. In an Arche, that record is the ADR and the citation goes in
   its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
5. Every artifact this pack recommends has an expiry condition attached to a
   person: a trigger needs a named dashboard and owner, a seam needs periodic
   exercise. If neither can be named for a given layer, say that plainly rather
   than filing the artifact anyway — an unmonitored trigger and an unexercised
   escape valve both read as safety and provide none, which is worse than an
   admitted dependency.

The distinction the pack exists to keep sharp: **a reversible decision and a
vendor-neutral architecture are not the same goal.** A named trigger keeps the
*decision* open at a known cost. A commodity seam lowers that cost for one layer.
Neither is an argument for abstracting every dependency or running on two
providers, and pursuing vendor neutrality as an end in itself buys a
least-common-denominator system that forfeits the capability the vendor was
chosen for. What is worth paying for is knowing the price of leaving, per layer,
and having checked recently that the price is still what the record says.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
