---
name: guidance-fitness-functions
description: >-
  Architectural fitness functions — encoding each load-bearing architectural
  decision (dependency direction, module and layer boundaries, database
  privileges, tenant isolation, file-placement conventions, rebuild and replay
  budgets) as a named CI check in a fast static lane and a slower integration or
  nightly lane, plus the registry that tracks each check's name, enforcement
  point, lane, and status. Use when asking how to stop an architecture eroding,
  when decision records get violated silently and nobody notices, when enforcing
  layer or module boundaries in a codebase where coding agents write much of the
  code, when writing dependency-cruiser or ArchUnit-style rules, or when a
  decision record needs to name the check that will detect its own violation.
  Not general test strategy, not coverage practice, not CI pipeline design.
---

# guidance-fitness-functions

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of a `Guidance` page plus a supporting `Concept` page.

## How to use this pack

1. Start with
   [architectural-fitness-functions.md](bundle/concepts/architectural-fitness-functions.md) —
   it is the gate. Walk its conditions against the specific decision in front of
   you and decide whether that decision earns a check at all; a decision with no
   mechanically checkable expression is meant to leave without one.
   [fitness-function-registry.md](bundle/concepts/fitness-function-registry.md)
   is its bookkeeping companion: read it once the answer is yes, for the shape
   of the table that keeps the resulting set of checks honest. Reading the
   registry page first produces a well-formed table of checks nobody decided to
   need.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-fitness-functions/<path-within-bundle>`, so the rationale outlives
   the conversation. In an Arche, that record is the ADR and the citation goes
   in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

The sentence the whole practice rests on: **tripping a fitness function means a
real architectural regression, not a flaky test.** A check nobody will write
that sentence about is a test, and belongs in the ordinary suite.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
