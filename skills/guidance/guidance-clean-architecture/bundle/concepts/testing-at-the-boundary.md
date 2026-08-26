---
type: Guidance
title: Testing at the boundary — sociable tests through use cases
description: Test business behavior by driving the use-case boundary the way a driving adapter would, with real domain objects and real in-memory implementations of driven ports, substituting doubles only for out-of-process dependencies — never mock-per-class — and push computation-heavy logic into a functional core tested with plain values and no doubles at all.
tags: [testing, clean-architecture, sociable-tests, test-doubles, functional-core, tdd]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T18:19:12Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: fowler-unit-test
    resource: https://martinfowler.com/bliki/UnitTest.html
    title: Martin Fowler — UnitTest (solitary vs sociable)
  - id: cooper-tdd
    resource: https://www.youtube.com/watch?v=EZ05e7EMOLM
    title: Ian Cooper — TDD, Where Did It All Go Wrong (NDC 2013)
  - id: fowler-mocks-stubs
    resource: https://martinfowler.com/articles/mocksArentStubs.html
    title: Martin Fowler — Mocks Aren't Stubs
  - id: bernhardt-boundaries
    resource: https://www.destroyallsoftware.com/talks/boundaries
    title: Gary Bernhardt — Boundaries (SCNA 2012)
  - id: seemann-functional-ports
    resource: https://blog.ploeh.dk/2016/03/18/functional-architecture-is-ports-and-adapters/
    title: Mark Seemann — Functional architecture is Ports and Adapters
  - id: seemann-impureim
    resource: https://blog.ploeh.dk/2020/03/02/impureim-sandwich/
    title: Mark Seemann — Impureim sandwich
  - id: cockburn-hexagonal
    resource: https://alistair.cockburn.us/hexagonal-architecture/
    title: Alistair Cockburn — Hexagonal Architecture
  - id: dhh-design-damage
    resource: https://dhh.dk/2014/test-induced-design-damage.html
    title: David Heinemeier Hansson — Test-induced design damage
---

# Testing at the boundary — sociable tests through use cases

## Technique

The unit of test is a **behavior**, not a class. A test enters the system
where a driving adapter would — it calls the use case — and asserts on
observable outcomes: the returned output, the state visible through ports,
the events emitted. Everything inside the boundary is real: real entities,
real domain services, real value objects. Doubles substitute only on the
**driven** side, and only for dependencies that are out-of-process or
nondeterministic — the database behind the repository port, the clock, the
payment gateway. This is Cockburn's asymmetry used as a test plan: the test
harness replaces the primary actor; fakes replace the secondary ones.

Prefer a shared, behaviorally honest **in-memory fake** per driven port (an
`InMemoryOrderRepository` used by every test) over per-test mock setups. A
fake accumulates the port's real semantics in one place; per-test mocks
restate the implementation's call sequence, which is how tests come to break
under refactoring that changes no behavior — the mock-per-class habit Cooper
identifies as where TDD went wrong. Refactoring inside the boundary should
never break a test; that property is the test suite's own fitness function.

Where the domain is computation-heavy, go further: shape the use case as a
**functional core in an imperative shell**. The shell (the use case body)
does IO up front — load the aggregate, read the clock — then calls pure
functions that make every decision, then does IO again to persist the
result: Seemann's impureim sandwich. The pure core is tested with plain
values and *no doubles at all*; purity has enforced the Dependency Rule
without a single interface. The remaining shell is so thin that a handful of
sociable tests cover it.

Two suites this page does not replace: **adapter contract tests**, run
against the real technology (a real Postgres in a container), which verify
that the fake and the real adapter agree on the port's semantics —
uniqueness violations, transaction scope, ordering — and **a few end-to-end
smoke tests** through the composition root proving the wiring is real. The
budget-shaped rule: hundreds of millisecond boundary tests, tens of adapter
contract tests, a handful of E2E.

## Applies when

- The Dependency Rule actually holds (`concepts/dependency-rule.md`): the
  core imports no IO, so boundary tests can construct it in memory. This
  page is downstream of that one — sociable boundary testing is the payoff
  that justifies the rule's cost.
- Use cases exist as callable, transport-free entry points
  (`concepts/use-case-layer.md`).
- Behavior is where the risk is: rules, state transitions, calculations —
  code whose failure is a wrong decision, not a wrong wire format.

## Doesn't apply when

- The logic lives in the database or the framework — a complex SQL
  projection, a Django queryset chain, a Rails validation stack. Testing a
  fake of the thing that contains the logic tests nothing; test through the
  framework's harness or against the real database. This is the true half of
  DHH's critique: where the framework is the behavior, framework-free tests
  are the wrong instrument.
- The behavior under test *is* an integration semantic: uniqueness under
  concurrency, FK cascades, transaction isolation, query performance. The
  in-memory fake is structurally incapable of honesty here — these belong to
  the adapter contract suite against the real engine, and a green boundary
  suite says nothing about them.
- The system is a thin pipe — an adapter-shaped service that transforms and
  forwards with no decisions. E2E tests plus contract tests cover it;
  boundary tests would just restate the mapping.

## Trade-offs

**Buys:** a suite fast enough to run on every save, covering every rule path
without a process; tests that survive refactoring because they pin behavior,
not structure; executable documentation whose test names read as the
operation's specification; and — via the shared fakes — a single place where
each port's assumed semantics are written down.

**Costs:** the fakes are code that must be maintained and *verified* — an
unverified fake is a standing source of false green; the adapter contract
suite it depends on needs real infrastructure in CI, which is the slow lane
(`guidance-fitness-functions/concepts/architectural-fitness-functions.md`
for the lane split); and the approach gives little on systems whose risk is
integration rather than logic, where its cost buys coverage of the wrong
thing.

## Failure modes

- **The lying fake.** The in-memory repository happily saves two orders with
  the same number; real Postgres raises a unique violation the use case
  never handles. Suite green, production 500. This is the failure that
  actually pages someone: it reproduces only against the real engine, at
  whatever hour the duplicate arrives. Countermeasure: one contract suite
  run against both the fake and the real adapter, so their behaviors are
  pinned to each other.
- **Mock drift back in.** Under deadline, developers stub the use case's
  collaborators per-test instead of extending the shared fake; six months
  later renaming a method breaks ninety tests that all still pass
  behaviorally. Symptom: refactoring PRs dominated by test-file churn.
- **The sandwich with a soggy middle.** The "pure" core quietly acquires a
  repository call mid-decision; now it needs doubles again and the no-mocks
  property is gone. Symptom: a function in the core whose tests construct a
  fake. Where the language cannot enforce purity, an import-boundary check
  scoped to the core's folder is the mechanical guard.
- **Coverage theater at the wrong altitude.** Hundreds of boundary tests,
  zero contract tests, one heroic E2E — and the incident review finds the
  bug in an adapter nobody's suite owned. The three suites are a system;
  dropping one silently reassigns its risk to production.

## Alternatives considered

- **Solitary/mockist TDD** — a double for every collaborator, tests as
  interaction specifications. Wins narrowly where the interaction *is* the
  contract (protocol implementations, outbound API orchestration); as a
  default it couples tests to structure and multiplies with the interface
  count.
- **Integration-first testing** — every test through HTTP against a real
  database. Wins for CRUD apps and thin pipes (and is DHH's position for
  framework-spine stacks); the cost curve arrives with combinatorial rule
  paths, where per-test seconds make the suite something developers stop
  running.
- **Property-based testing on the functional core** — generate inputs, assert
  invariants. Complements rather than replaces the boundary suite once a
  pure core exists; wins outright for calculation-dense domains (pricing,
  scheduling) where example-based tests undersample the space.
