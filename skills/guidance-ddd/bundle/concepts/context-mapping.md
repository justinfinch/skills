---
type: Guidance
title: Naming the relationship between two contexts
description: Choose and state the integration relationship explicitly, so translation cost and the power balance between teams are visible rather than assumed.
tags: [ddd, context-map, integration]
created: 2026-08-26
generated: { by: write-guidance/claude-opus-5, at: 2026-08-26T00:00:00Z }
status: stable
stale_after: 2031-01-01
sources:
  - id: evans-ddd
    resource: https://www.domainlanguage.com/ddd/
    title: Eric Evans — Domain-Driven Design
---

# Naming the relationship between two contexts

## Technique

For each pair of contexts that integrate, name the relationship explicitly and
record it. The name fixes two things that otherwise stay implicit: **who absorbs
the translation cost**, and **who wins when the models disagree**.

The patterns below are the ones that carry a genuine decision. Each is a
different answer to "how much of the other model are we willing to let in."

| Relationship | Choose it when |
| :--- | :--- |
| **Anticorruption layer** | The upstream model would distort yours, and your model is worth protecting. You pay for a translation layer and own it forever. |
| **Conformist** | You have no leverage over upstream and its model is tolerable. You adopt their model wholesale and spend nothing on translation. |
| **Shared kernel** | Two teams share a genuinely common subset AND can coordinate releases. The coordination requirement is the whole condition. |
| **Published language** | Many consumers, none of whom should know your internals. You invest in a stable contract that is nobody's internal model. |
| **Open host service** | You are upstream, consumers are numerous, and per-consumer integration has become the bottleneck. |
| **Separate ways** | The integration's value does not exceed its cost. Duplicate the small thing and move on. |

## Applies when

- Two contexts exchange data or behaviour and are owned by different teams,
  release on different cadences, or sit on different sides of a trust boundary.
- The models genuinely differ — the same concept exists on both sides with
  different shape, lifecycle, or authority.
- The relationship is going to persist. Naming it is an investment in the
  conversation you will have repeatedly.

## Doesn't apply when

- **There is only one context.** A context map with one node is a diagram of
  nothing. Reach for this after boundaries exist, not to justify creating them.
- **You control both sides and they change together.** If the two always ship
  in the same deploy and the same team owns both, the honest description is one
  context, or a shared kernel at most. A formal map between them is bureaucracy
  around a decision you already effectively made.
- **The integration is genuinely throwaway.** A one-off migration or a
  scheduled backfill does not need a named relationship; it needs deleting when
  it is done.
- **The relationship you would name is aspirational.** Recording "published
  language" for a contract that changes whenever upstream feels like it does not
  make it stable — it makes the map lie, which is worse than having no map.

## Trade-offs

Buys visible power dynamics. Most integration pain is not technical but
political — who has to change when the other side moves — and naming the
relationship makes that negotiable in advance instead of discoverable in an
incident.

Costs real engineering in the cases where you choose protection. An
anticorruption layer is a component with tests, an on-call story, and a tendency
to accumulate special cases; the alternative — conformist — is genuinely cheaper
and is sometimes right.

## Failure modes

- **An anticorruption layer that doesn't translate.** It passes upstream shapes
  through under local names, so the corruption arrives anyway with a layer of
  indirection in front of it. The tell is that an upstream field rename requires
  changes in your domain logic.
- **Conformist by default rather than by decision.** Nobody chose it; the
  first integration just adopted upstream's model and everything since inherited
  it. This is the most common state and the least examined — it is only a failure
  when the model was in fact worth protecting.
- **Shared kernel between teams that cannot coordinate.** The condition on the
  pattern is release coordination, and it is the one people skip. Without it, the
  kernel becomes a contended file that breaks both sides on alternate weeks.
- **Published language nobody publishes.** The contract exists but changes ship
  without notice, so consumers defensively parse it, and the "language" becomes a
  set of private assumptions per consumer.
- **The map goes stale.** Drawn once during a design phase, never revised, and
  then cited in decisions years later as though it still describes reality.

## Alternatives considered

- **A single context** — wins when the boundary was wrong. If naming the
  relationship keeps being hard, the honest answer may be that these are one
  model with a seam drawn through it.
- **Event-carried state transfer without a formal map** — wins for one-way
  notification between contexts with a thin, stable payload, where the ceremony
  of a named relationship exceeds the integration's weight.
