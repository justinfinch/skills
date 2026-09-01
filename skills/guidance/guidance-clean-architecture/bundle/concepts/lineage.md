---
type: Concept
title: Lineage — BCE, Hexagonal, Onion, Clean
description: The family tree behind Clean Architecture — Jacobson's Entity-Control-Boundary, Cockburn's Hexagonal, Palermo's Onion, and Martin's synthesis — with what each formulation actually contributed, where the community treats them as synonyms, and the three differences that still matter in practice.
tags: [architecture, clean-architecture, hexagonal, onion-architecture, entity-control-boundary, history]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T18:19:12Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: cockburn-hexagonal
    resource: https://alistair.cockburn.us/hexagonal-architecture/
    title: Alistair Cockburn — Hexagonal Architecture
  - id: palermo-onion
    resource: https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/
    title: Jeffrey Palermo — The Onion Architecture, part 1
  - id: martin-clean-architecture
    resource: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
    title: Robert C. Martin — The Clean Architecture
  - id: ecb-wikipedia
    resource: https://en.wikipedia.org/wiki/Entity%E2%80%93control%E2%80%93boundary
    title: Wikipedia — Entity-control-boundary (Jacobson)
  - id: graca-explicit-architecture
    resource: https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/
    title: Herberto Graça — DDD, Hexagonal, Onion, Clean, CQRS — How I put it all together
  - id: android-arch-guide
    resource: https://developer.android.com/topic/architecture
    title: Google — Guide to app architecture (Android)
  - id: seemann-functional-ports
    resource: https://blog.ploeh.dk/2016/03/18/functional-architecture-is-ports-and-adapters/
    title: Mark Seemann — Functional architecture is Ports and Adapters
---

# Lineage — BCE, Hexagonal, Onion, Clean

Clean Architecture is a synthesis, and knowing what it synthesized settles
most vocabulary disputes before they start. The pack's technique pages
(`concepts/dependency-rule.md`, `concepts/ports-and-adapters.md`) take
positions; this page is the map behind those positions.

## The four formulations

**Entity–Control–Boundary — Jacobson, 1992.** From *Object-Oriented Software
Engineering*: every use case is realized by entities (domain objects),
boundaries (interfaces to actors), and controls (use-case orchestration).
Martin cites BCE directly; Clean Architecture's entities, interactors, and
boundary interfaces are Jacobson's triad renamed. BCE contributed Clean's
most distinctive feature relative to the others: **use cases as first-class
objects**.

**Hexagonal / Ports & Adapters — Cockburn, ~2005.** Intent, verbatim: "allow
an application to equally be driven by users, programs, automated test or
batch scripts, and to be developed and tested in isolation from its eventual
run-time devices and databases." Two zones only — inside and outside — with
ports as protocol-defined interaction points and adapters converting per
technology. The **driving/driven asymmetry** is Cockburn's alone, and it is
the formulation's real content: substitute test drivers on the driving side,
doubles on the driven side. The hexagon means nothing; Cockburn picked it so
the diagram had room to draw ports. Notably, hexagonal is the *least*
prescriptive of the family — it says nothing about how to structure the
inside, and it explicitly distrusts layer stacks, observing that layered
architectures historically re-accumulate business logic in the wrong layer
within a few years.

**Onion — Palermo, 2008.** Rings around a domain core: domain model at dead
center, then domain services, application services, with UI, infrastructure,
and tests sharing the outermost ring. Tenets: the application builds around
an independent object model; inner layers define interfaces, outer layers
implement them; "all coupling is toward the center"; the core compiles and
runs without infrastructure. Onion contributed the **ring picture** and the
DDD-flavored "domain at the center" emphasis, and Palermo scoped it honestly
from the start — for long-lived, behavior-rich applications, not simple
ones.

**Clean — Martin, 2012 post / 2017 book.** The synthesis: Onion's rings,
BCE's use-case objects, Hexagonal's inversion at the seams, plus two things
of its own — the **Dependency Rule** stated as an absolute ("source code
dependencies can only point inwards"), and the **boundary-crossing data
discipline** (isolated simple data structures cross boundaries; never
entities, never database rows, format owned by the inner circle). The book
adds the Humble Object pattern, Main-as-plugin (the composition root), and —
in chapter 24, usually ignored by adopters — partial boundaries, conceding
that full boundaries are expensive and architects "must guess —
intelligently" about where they'll pay.

## Synonyms, mostly — three differences that matter

The community broadly treats the four as one pattern, and for the core
inversion it is right: Graça's Explicit Architecture merges them onto a
single diagram without contradiction. The differences that still change what
a team builds:

1. **Prescription level.** Hexagonal mandates inside/outside and nothing
   else; Onion adds rings; Clean adds a named layer stack, interactors, and
   the DTO discipline. A team "doing hexagonal" may legitimately skip
   use-case objects and boundary DTOs; a team "doing Clean" by the book may
   not. Most mapping-fatigue complaints attach to Clean's additions, not to
   the shared inversion.
2. **Driving/driven asymmetry.** Only Cockburn's formulation carries the
   test-strategy instruction (drivers on one side, doubles on the other) —
   absent from Martin's ring diagram, and load-bearing enough that this
   pack's testing page (`concepts/testing-at-the-boundary.md`) is built on
   it.
3. **Use cases as objects.** Only BCE→Clean has them. They are what makes
   screaming architecture possible — and what produces the one-line-use-case
   pathology when applied without conditions
   (`concepts/use-case-layer.md`).

## Two modern branches worth naming

**Functional core / imperative shell** (Bernhardt 2012; Seemann's "functional
architecture *is* ports and adapters") restates the family's inversion with
purity instead of interfaces: a pure function cannot call an impure one, so
the compiler pushes IO to the edge and the ports-and-adapters shape falls
out without a single declared interface.

**The institutional counter-example**: Google's Android architecture guide
deliberately rejects the Dependency Rule for standard apps — its domain
layer is optional and its data layer does not depend inward — after years of
community Clean-Architecture templates on the platform. A reminder that the
family's prescriptions are contested at the highest levels of practice, and
that the conditions on this pack's Guidance pages are not decoration.
