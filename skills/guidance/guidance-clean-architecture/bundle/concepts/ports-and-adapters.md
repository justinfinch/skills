---
type: Guidance
title: Ports and adapters — boundary mechanics for a clean core
description: Give the core its seams as ports it declares and adapters implement, honoring the driving/driven asymmetry — driving adapters call the core, driven adapters are called through core-owned interfaces — with ports declared next to the use case that consumes them, a repository port on the write side only, translation DTOs only where representations genuinely diverge, and partial boundaries where a full seam is not yet defensible.
tags: [architecture, clean-architecture, hexagonal, ports-and-adapters, repository, dto, boundaries]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T18:19:12Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: cockburn-hexagonal
    resource: https://alistair.cockburn.us/hexagonal-architecture/
    title: Alistair Cockburn — Hexagonal Architecture
  - id: martin-clean-architecture
    resource: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
    title: Robert C. Martin — The Clean Architecture
  - id: johnson-standard-package-layout
    resource: https://www.gobeyond.dev/standard-package-layout/
    title: Ben Johnson — Standard Package Layout
  - id: taylor-template-discussion
    resource: https://github.com/jasontaylordev/CleanArchitecture/discussions/482
    title: Jason Taylor CleanArchitecture template — Application-layer EF Core discussion
  - id: earezki-maintainability
    resource: https://earezki.com/clean-architecture-maintainability-nightmare/
    title: earezki — Why Clean Architecture is a Maintainability Nightmare
  - id: netflix-hexagonal
    resource: https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749
    title: Svrtan & Makagon — Ready for changes with Hexagonal Architecture (Netflix TechBlog)
---

# Ports and adapters — boundary mechanics for a clean core

## Technique

A **port** is an interface the core owns, named for what the core needs
(`OrderRepository`, `Clock`, `PaymentGateway`), not for the technology behind
it. An **adapter** converts between a port and one technology. Cockburn's
asymmetry does real work and is worth preserving because it is a *testing*
instruction:

- **Driving (primary) adapters** call the core: the HTTP route handler, the
  queue consumer, the CLI command, the cron entry. The core does not know
  they exist. In tests, the test itself is the driving adapter.
- **Driven (secondary) adapters** are called by the core through ports: the
  Postgres repository, the SMTP sender, the vendor SDK wrapper. In tests, a
  double or in-memory implementation substitutes here — and only here.

Declare each port next to the use case that consumes it, not in a central
`ports/` directory — the consumer-owned interface (Go's "accept interfaces,
return structs", equally idiomatic in TypeScript) keeps ports minimal because
a port only grows a method when a consumer needs one.

Persistence gets a deliberately asymmetric treatment. The **write side** gets
a repository port: load one aggregate, save one aggregate, one transaction —
a real seam, because invariants live behind it and an in-memory double makes
use-case tests trivial. The **read side** does not: queries go through a thin
DTO query model that never touches the domain
(`guidance-cqrs-projections/concepts/cqrs-lite.md`), because read paths have
no invariants to protect and a repository that tries to carry every query
shape becomes a leaky pass-through. Translation DTOs at other boundaries
follow the same test: map where the representations genuinely diverge (wire
format vs domain type, vendor payload vs domain event); never write an
identity map for symmetry's sake.

Where a full port is not yet defensible, use a **partial boundary**: a
one-way interface or a facade at the seam, with the named trigger that would
justify upgrading it recorded where decisions live
(`guidance-portability-seams/concepts/named-migration-triggers.md`).

## Applies when

- The seam has a named alternative or a named migration trigger — "reads move
  off the legacy JSON API next year" (the Netflix case), "we exit this vendor
  if unit cost crosses X" — so the port is priced insurance, not superstition.
- The driven dependency is out-of-process or nondeterministic (database,
  clock, network, randomness): exactly the dependencies whose absence makes
  tests fast and deterministic.
- More than one driving adapter exercises the same use case — HTTP plus a
  queue consumer plus a scheduled job — so the core's independence from any
  one transport is load-bearing today, not someday.
- The write side has real invariants: an aggregate whose rules must hold
  across operations is worth a repository port even when nothing else is.

## Doesn't apply when

- Only one implementation is conceivable and it is deterministic and
  in-process. Port-wrapping your own domain services, pure functions, or a
  standard-library data structure is interface ceremony with no seam behind
  it — the tempting version of this mistake is "we might want to mock it,"
  which `concepts/testing-at-the-boundary.md` argues is itself the wrong
  test strategy.
- The port would mirror a vendor SDK one-to-one. An interface whose methods
  are the vendor's methods renamed defends nothing — a migration rewrites
  every call site anyway. Either the seam belongs at a commodity API the
  industry standardized (`guidance-portability-seams/concepts/standard-api-seams.md`)
  or the honest move is calling the SDK directly behind a partial boundary.
- The path is a read path. Fetching rows to render them needs no aggregate,
  no invariants, and no port; forcing reads through the write-side repository
  is where "repository interfaces with fourteen query methods" come from.
- The team treats the ORM's unit-of-work as the boundary (the Jason Taylor
  stance: DbContext-as-repository, Prisma-client-in-application). This is a
  coherent, contested position that trades the Dependency Rule's letter for
  less ceremony — but it is a different technique than this page, and mixing
  the two (some use cases on ports, some on the ORM, no stated rule) is
  worse than either.

## Trade-offs

**Buys:** driven dependencies substitutable in tests and in production;
use-case tests that run in memory; adapters developable and reviewable in
isolation; vendor and infrastructure churn confined to the adapter layer —
when the churn actually comes, the swap is an adapter's worth of work, not an
application's.

**Costs:** an interface and usually a mapping per seam — the mapping fatigue
critique is correct wherever a port exists that the conditions above do not
justify; abstraction leak risk, because a port hides *how* but cannot hide
runtime characteristics (an API call does not behave like a file read, and a
repository silently hides transaction scope and query cost); and the
discipline cost of keeping ports consumer-shaped as the system grows.

## Failure modes

- **The leaky repository.** The port hides transaction scope and lazy-load
  behavior; a use case makes three "cheap" calls that are three round trips,
  or two saves that the caller assumed were atomic. Symptom: N+1 storms and
  consistency bugs that only reproduce in production. Countermeasure: ports
  own their transactional semantics explicitly (a unit-of-work boundary per
  use case), and constraint-dependent behavior is tested against the real
  database, not the in-memory double.
- **The vendor-shaped port.** `StripeGateway` with Stripe's method names and
  Stripe's types. The day the vendor changes, the "seam" moves nothing.
  Symptom: the port's types import the SDK.
- **Interface explosion.** Every class gets an interface on principle; DI
  wiring becomes its own subsystem; every test starts with ten mocks. The
  architecture is now generating the mock-heavy tests it promised to
  eliminate. Symptom: interfaces with exactly one implementation and no test
  double anywhere.
- **Business logic in the adapter.** The HTTP handler validates invariants,
  or the repository implementation decides what "active" means. The core
  stays clean and empty; the rules live outside where no fast test reaches
  them. Symptom: changing a business rule means editing an adapter.

## Alternatives considered

- **ORM-as-boundary** — the application layer uses the ORM's context
  directly, treating unit-of-work/DbSet as repository enough. Wins when the
  ORM is stable, the team is fluent in it, and in-memory use-case testing is
  not the strategy (integration tests against a real database instead).
- **Functional core / imperative shell** — pass values in and out instead of
  injecting interfaces; the shell does all IO up front and after
  (`concepts/testing-at-the-boundary.md`). Wins when use cases can be
  restructured as decide-then-act; removes the interface count entirely at
  the seams it covers.
- **Direct calls plus contract tests** — no port; call the dependency and
  pin its behavior with contract tests. Wins for stable internal services
  where the "swap" scenario is not credible and the contract test documents
  the real semantics a port would have hidden.
