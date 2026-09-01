---
type: Guidance
title: The Dependency Rule — source dependencies point toward policy
description: Keep every source dependency pointing from infrastructure toward business policy — the domain and use-case core imports nothing framework- or IO-flavored, outer code implements interfaces the core declares, and one composition root at the process entry point wires the graph — treating the named layers as schematic and collapsing any layer that would be pass-through.
tags: [architecture, clean-architecture, dependency-rule, hexagonal, composition-root, framework-independence]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T18:19:12Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: martin-clean-architecture
    resource: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
    title: Robert C. Martin — The Clean Architecture
  - id: martin-screaming
    resource: https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html
    title: Robert C. Martin — Screaming Architecture
  - id: seemann-composition-root
    resource: https://blog.ploeh.dk/2011/07/28/CompositionRoot/
    title: Mark Seemann — Composition Root
  - id: dhh-design-damage
    resource: https://dhh.dk/2014/test-induced-design-damage.html
    title: David Heinemeier Hansson — Test-induced design damage
  - id: martin-design-damage
    resource: https://blog.cleancoder.com/uncle-bob/2014/05/01/Design-Damage.html
    title: Robert C. Martin — Design Damage
  - id: bennett-no-service
    resource: https://www.b-list.org/weblog/2020/mar/16/no-service/
    title: James Bennett — Against service layers in Django
  - id: netflix-hexagonal
    resource: https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749
    title: Svrtan & Makagon — Ready for changes with Hexagonal Architecture (Netflix TechBlog)
  - id: sepchuk-critique
    resource: https://dev.to/bosepchuk/why-i-cant-recommend-clean-architecture-by-robert-c-martin-ofd
    title: Blaine Sepchuk — Why I can't recommend Clean Architecture
---

# The Dependency Rule — source dependencies point toward policy

## Technique

Divide the codebase into a **core** (domain model plus use cases — the code
that states what the business does) and an **outside** (HTTP, persistence,
frameworks, vendor SDKs — the code that connects that statement to the world),
and make every source dependency point from outside toward core. The core
imports nothing framework- or IO-flavored; when it needs the outside — a
clock, a repository, a mail sender — it declares an interface and the outside
implements it. One **composition root** at the process entry point (`main`,
the serverless handler module, the server bootstrap) constructs the graph and
injects implementations; nothing else knows which implementation is live.

The named layers of the canonical diagram — entities, use cases, interface
adapters, frameworks — are schematic, and Martin says so in the original
post: "you may find that you need more than just these four." The rule, not
the ring count, is the architecture. A layer that would only forward calls is
collapsed, not built for symmetry. In a TypeScript monorepo this rule is
drawn at package granularity — `guidance-monorepo/concepts/domain-centered-workspace.md`
is the same rule where the package manager can see it; this page is the rule
inside a single deployable, where only an import-linting tool can see it.

What the direction buys is **deferred decisions**: the database, the web
framework, and the transport are consumed through seams, so choosing them —
and changing them — stays cheap for as long as the rule actually holds. What
proves the rule holds is not the diagram but two checkable facts: the core's
test suite runs without any process boundary, and an import-boundary check
(`guidance-fitness-functions/concepts/architectural-fitness-functions.md`)
fails the build when an infrastructure import lands in the core.

## Applies when

- The system is expected to outlive its current infrastructure choices —
  multi-year lifespan, or an infrastructure decision (queue, search index,
  vendor API, upstream data source) that is genuinely likely to be revisited.
  Netflix's documented two-hour swap of an entity's reads from a JSON API to
  GraphQL paid off precisely because data-source churn was a *known* axis of
  change, not a hypothetical one.
- Domain logic is rich: invariants span more than one operation, the same
  rules are exercised by more than one driver (HTTP, queue consumer, cron),
  or correctness of the rules matters more than time-to-first-endpoint.
- The framework is a host, not the spine — Node/Express/Fastify, Go services,
  Lambda handlers, Spring-as-plumbing — so "the framework is a detail" is a
  true statement about the code, not an aspiration.
- The team intends to test business behavior in-memory through use-case
  boundaries (`concepts/testing-at-the-boundary.md`); the rule is what makes
  those tests possible.
- More than one team or a rotating cast works in the codebase, so enforced
  boundaries substitute for tribal knowledge about where things go.

## Doesn't apply when

- CRUD-over-database dominates: if most endpoints are a query plus
  serialization, the core has nothing in it, every layer is pass-through, and
  the rule taxes every reader while protecting nothing. Use the thin query
  path (`guidance-cqrs-projections/concepts/cqrs-lite.md`) and framework-native
  handlers; add the core when invariants arrive.
- The code is a prototype, a spike, or pre-product-market-fit: the entire
  value proposition is deferred-decision optionality, and code that will not
  live long enough for a deferred decision to arrive pays the premium and
  never files the claim.
- The framework is the spine — Rails, Django, Laravel, classic Active Record —
  and the team is leveraging it fully. Here the burden of proof flips: the
  ORM *is* the application's data layer, wrapping it costs indirection that
  fights the framework's grain, and both DHH ("test-induced design damage")
  and Bennett (Django's models/managers are where logic goes) argue the wrap
  is damage. Martin's rebuttal — business rules change at different rates
  than framework bindings — is the strongest counter, and this remains
  genuinely contested; the honest position is that in these stacks whoever
  wants the boundary must name what it defends against.
- The only justification anyone can state is a hypothetical database swap.
  Practitioner consensus is near-universal that you keep Postgres; a boundary
  must be defended by testability, parallel development, or a *named*
  migration trigger (`guidance-portability-seams/concepts/named-migration-triggers.md`),
  not by vendor-swap insurance nobody prices.

## Trade-offs

**Buys:** decisions deferred and revisable (transport, persistence, vendors
consumed through seams); business behavior testable in milliseconds without
processes; parallel development against interfaces before implementations
exist; a codebase whose top level names the domain rather than the framework
(screaming architecture), which is also what lets a coding agent or a new
hire find the rules without a guide.

**Costs:** more files and more indirection per request — a reader tracing one
call crosses at least one interface whose implementation lives elsewhere;
an onboarding tax on developers used to framework-native code; and a standing
enforcement burden, because the rule is a discipline, not a property — it
erodes unless a tool fails the build on violation. The critique literature
(Sepchuk) is also right that Martin's own evidence is experiential: the rule's
payoff depends on the conditions above actually holding, and the book
under-specifies them.

## Failure modes

- **Silent erosion.** Nothing crashes when someone imports the ORM into the
  core — the diagram stays clean while `grep` says otherwise, and the claims
  (in-memory tests, swappable adapters) quietly become false. Six months
  later the visible symptom is a test suite that cannot run without Docker.
  The countermeasure is a build-failing import check from day one; a rule
  enforced by review alone lasts about one deadline.
- **Ceremony without a core.** The team builds the four ring folders on a
  CRUD app; every "use case" is a one-line proxy and every entity mirrors a
  table. From outside it looks like discipline; from inside every change
  touches five files that each add nothing. This is the most common failure
  in practice, and it is a *conditions* failure — the pattern was applied
  where its Applies-when did not hold.
- **The claimed boundary with the borrowed type.** The core declares
  repository interfaces but their signatures traffic in ORM entity types, so
  the dependency points inward on the import graph and outward in reality.
  Any real swap — or in-memory test double — now requires retyping the core.
- **Framework upgrades that touch the core.** The tell that the rule has
  failed: a Fastify or Prisma major-version bump produces diffs inside the
  domain or use-case folders. Under the rule those diffs are confined to
  adapters and the composition root.

## Alternatives considered

- **Framework-native (the Rails/Django way)** — logic in models, managers,
  and controllers, tested through the framework's harness. Wins when the
  framework is the spine and the team leverages it fully; the deferred
  decisions Clean Architecture protects were already made permanently when
  the framework was chosen.
- **Vertical slices without a shared core** — each feature owns its stack
  top to bottom, refactoring toward patterns per slice
  (`guidance-vertical-slices/concepts/feature-folder-organization.md`). Wins
  when features share little domain logic; composes with this rule rather
  than opposing it when slices share an extracted core.
- **Functional core / imperative shell** — purity, not interfaces, forces
  dependencies outward; see `concepts/testing-at-the-boundary.md`. Wins when
  the domain is computation-heavy and the team is comfortable with a
  values-in/values-out style; it is the same rule enforced by the type of
  the function rather than the direction of the import.
- **Partial boundaries** — Martin's own chapter 24 concession: where a full
  boundary is not yet defensible, a one-way seam or facade at the one or two
  places with a named migration trigger, upgraded later. Wins early in a
  system's life, when guessing every boundary "intelligently" is not yet
  possible.
