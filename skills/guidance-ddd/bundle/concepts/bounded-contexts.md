---
type: Guidance
title: Where a bounded context boundary belongs
description: Draw boundaries where the language changes meaning, not where the org chart or the deployment topology happens to fall.
tags: [ddd, bounded-context, boundaries]
created: 2026-08-26
generated: { by: write-guidance/claude-opus-5, at: 2026-08-26T00:00:00Z }
status: stable
stale_after: 2031-01-01
sources:
  - id: evans-ddd
    resource: https://www.domainlanguage.com/ddd/
    title: Eric Evans — Domain-Driven Design
---

# Where a bounded context boundary belongs

## Technique

Draw an explicit boundary inside which one model holds and every term has
exactly one meaning. Across the boundary, terms are **translated, never
shared** — the same word may exist on both sides meaning different things, and
that is correct rather than a defect to reconcile.

The boundary is a language boundary first. Whether it later becomes a module, a
service, or a deployment unit is a separate decision, made for separate reasons.

## Applies when

- One term already carries two meanings that people disambiguate by context in
  conversation. "Order" meaning a customer's purchase and "order" meaning a
  warehouse picking instruction is two contexts already in play.
- A model has started accumulating conditionals that only apply "when it's for
  X" — flags, nullable fields that are mandatory in one flow and meaningless in
  another, subclasses that share a parent for no behavioural reason.
- Different parts change at genuinely different rates, and changes to one keep
  forcing regression testing of the other.
- Separate teams own the lifecycle, and coordination on every release has become
  the dominant cost.

## Doesn't apply when

- **The terms are actually consistent.** One team, one model, no collisions.
  Splitting adds a translation layer and buys nothing — you pay the seam cost
  forever to solve a problem you do not have.
- **The proposed boundary is a technical layer.** UI, service, and data-access
  are not bounded contexts; they are one model sliced horizontally. Drawing
  contexts there gives you the translation cost of a boundary with none of the
  independence.
- **The two "meanings" are one concept with a missing attribute.** Sometimes
  "order" differs across teams only because nobody modelled `status`. Add the
  attribute and the collision disappears. Splitting first hardens an accident
  into architecture.
- **The system is small enough to hold in one head.** A boundary is a bet that
  coordination will get expensive. When it doesn't, the bet just costs.

## Trade-offs

Buys independent evolution and, more importantly, a smaller model on each side —
the real benefit is that each model gets to be *simple*, not that each team gets
to be *autonomous*.

Costs a translation layer at every seam, and duplicated concepts that must stay
coherent without being shared. Two contexts both holding "customer" is not
duplication to be eliminated; keeping them honest is nonetheless ongoing work
somebody must own.

## Failure modes

- **Boundaries drawn as service boundaries first, language second.** The split
  is made for deployment reasons, then a model is retrofitted to justify it. The
  symptom is chatty synchronous calls between two services that turn out to share
  one invariant — a distributed monolith with extra latency and a worse failure
  story.
- **A shared database under two contexts.** The boundary exists in the code and
  not in the data, so a schema change silently breaks the other side. This
  nullifies the seam while leaving all of its cost in place.
- **The language leaks anyway.** The translation layer passes the upstream
  model's shapes through under local names. Six months later both models are the
  upstream one, and nobody noticed it happen.
- **Boundary confused with granularity.** *Where* the seam belongs and *how
  small* the pieces should be are different questions with different answers. A
  correct boundary split into five pieces is four wrong decisions layered on one
  right one.

## Alternatives considered

- **One model, well-factored modules** — wins when the boundary is real but the
  coordination cost of separate contexts isn't yet warranted. Keeps the seam
  visible and cheap to move, which matters while you are still wrong about where
  it goes.
- **A single model with explicit variant types** — wins when the divergence is
  narrow and enumerable, rather than pervasive.
- **Separate ways** — wins when two contexts turn out to need nothing from each
  other. Duplicating a small amount of logic beats maintaining an integration
  that exists because someone assumed one was needed.
