---
type: Guidance
title: Whether strategic DDD is warranted
description: Decide whether to treat the domain model as the primary design artifact, before adopting any of the machinery that follows from it.
tags: [ddd, domain-modelling, strategy]
created: 2026-08-26
generated: { by: write-guidance/claude-opus-5, at: 2026-08-26T00:00:00Z }
status: stable
stale_after: 2031-01-01
sources:
  - id: evans-ddd
    resource: https://www.domainlanguage.com/ddd/
    title: Eric Evans — Domain-Driven Design
---

# Whether strategic DDD is warranted

## Technique

Treat the domain model as the primary design artifact. Discover the language
domain experts already use, make that language the one the code speaks, and let
context boundaries and module structure follow the language rather than the
database schema or the delivery framework.[^evans-ddd]

This page is the gate in front of the rest of the pack. Bounded contexts,
context maps, and aggregates are all machinery that only pays off once this
decision has been made deliberately.

[^evans-ddd]: *Domain-Driven Design* — strategic design: ubiquitous language, bounded contexts, and the context map.

## Applies when

- Outcomes depend on rules and state transitions, not just field validation —
  the same input produces different results depending on what the system already
  knows.
- The same word means different things to different parts of the business.
  That collision is the observable signal that more than one model is already in
  play, whether or not anyone has named them.
- The system is long-lived enough that a wrong boundary costs more than the
  modelling would. If it is still running in three years, a boundary drawn
  around the wrong concept will be paid for the whole time.
- Domain experts are available for repeated conversation, not a one-off
  requirements handover.

## Doesn't apply when

- **The domain is CRUD and the only rules are field-level validation.** There is
  no model to discover because there is no domain logic. Modelling ceremony buys
  indirection and nothing else.
- **The complexity is technical rather than domain.** A high-throughput
  pipeline, a compiler, a rendering engine. DDD addresses domain complexity
  specifically; pointed at technical complexity it produces an elaborate model of
  a simple domain while the genuinely hard part goes unaddressed. This one is
  tempting precisely because the system *is* hard.
- **The model is dictated externally.** You are implementing a published
  standard, a regulatory schema, or a partner's API contract. The ubiquitous
  language already exists and is not yours to discover. Modelling it your own way
  commits you to a translation layer maintained forever against a specification
  that wins every disagreement.

## Trade-offs

Buys a structure that absorbs change along the lines the business actually
changes, and a vocabulary that makes requirements conversations shorter because
both sides mean the same thing by the same word.

Costs sustained domain-expert time, which is usually the scarcest resource in
the building; a slower start, because the first model is always wrong and the
second one is what you wanted; and a layer of indirection that a newcomer reads
as overhead until they hit the change it was there to absorb.

## Failure modes

- **Attempted without a domain expert.** The team models its own guesses and
  ships them as the ubiquitous language. This is worse than having no shared
  vocabulary, because the invented one looks authoritative and gets defended in
  review for years.
- **Tactical patterns adopted without strategic design.** Repositories,
  entities, and value objects appear, the folder layout changes, and no boundary
  or language decision was ever made. The cost is paid and none of the benefit
  arrives — the most common way "we do DDD" turns out to mean a directory
  structure.
- **The model is written once and never revised.** It becomes archaeology: a
  diagram nobody trusts, describing a business that has moved on. The
  distinguishing symptom is that people check the code to find out what is true.
- **The language lives in documents but not in conversation or code.** If the
  standup still says "the record" while the model says "policy", the language was
  never adopted; it was published.

## Alternatives considered

- **Transaction script** — wins when the logic is thin and procedural. Directly
  expresses "when this request arrives, do these steps." Stops scaling when the
  steps start needing to know about each other.
- **CRUD with generated scaffolding** — wins when the system's job really is
  data entry and retrieval, and honesty about that is cheaper than a model.
- **Anemic model plus a service layer** — usually an accident rather than a
  choice, but a legitimate one when the domain rules are genuinely centralized in
  a few operations and there is no invariant worth protecting inside the objects.
