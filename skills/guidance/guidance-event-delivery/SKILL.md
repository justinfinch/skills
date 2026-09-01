---
name: guidance-event-delivery
description: >-
  Reliable event delivery from a relational system of record — the transactional
  outbox (the state change and the outbox row in one transaction), a single relay
  claiming rows with `FOR UPDATE SKIP LOCKED` and publishing under the row id, a
  durable broker fanning out to independent durable consumers, and end-to-end
  idempotency keys that make at-least-once delivery safe at every hop. Use when
  asking how to publish events without losing them, worrying about a dual-write
  between a database and a queue, choosing between Postgres LISTEN/NOTIFY and a
  message broker, sizing a dedup window or a stream's retention, or investigating
  consumers that see duplicates, projections that fall behind, or state that
  committed while its event never arrived. Not event sourcing as a persistence
  model; not a broker product comparison.
---

# guidance-event-delivery

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Start with
   [transactional-outbox.md](bundle/concepts/transactional-outbox.md). It is the
   gate: if a state change and its event can be allowed to diverge, none of the
   rest of this pack is worth its cost, and that page says so in its **Doesn't
   apply when**. The other two build on it and are read against a decision it has
   already settled —
   [relay-to-broker-dispatch.md](bundle/concepts/relay-to-broker-dispatch.md)
   decides what happens *after* the relay claims a row (and, just as often,
   decides that a broker is not yet earned), and
   [end-to-end-idempotency.md](bundle/concepts/end-to-end-idempotency.md) is the
   other half of the at-least-once bargain the first two deliberately accept.
   Reading the broker page alone produces infrastructure without the property it
   was bought to protect.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-event-delivery/<path-within-bundle>`, so the rationale outlives the
   conversation. In an Arche, that record is the ADR and the citation goes in its
   `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
5. When a page's conditions don't hold *yet*, record the threshold that would
   change the answer, with a number in it. The broker page carries concrete
   thresholds for exactly this reason: a deferral with a named trigger is what
   makes the eventual reversal cheap, and a deferral without one is folklore that
   decays.

The distinction the pack exists to keep sharp: **atomicity of publish-intent,
fanout, and duplicate tolerance are three separate problems.** An outbox makes
publication inseparable from the state change and says nothing about how many
consumers there are. A broker makes consumers independent and says nothing about
whether the event was ever recorded atomically. Idempotency keys make redelivery
harmless and say nothing about either. Solving one and assuming coverage of the
others is the failure all three pages are written against.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
