---
type: Concept
title: The fitness-function registry
description: One table in the architecture document listing every named check, the exact script or test that enforces it, its CI lane, and whether it is active, pending a milestone, or deferred — so "we have a check for that" is a claim a reader can verify.
tags: [architecture, fitness-functions, ci, registry, governance]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T15:58:59Z }
status: stable
stale_after: 2029-06-01
sources:
  - id: ford-parsons-kua-evolutionary
    resource: https://evolutionaryarchitecture.com/
    title: Ford, Parsons, Kua — Building Evolutionary Architectures
  - id: archunit
    resource: https://www.archunit.org/userguide/html/000_Index.html
    title: ArchUnit User Guide
---

# The fitness-function registry

A registry is **one table, in the architecture document, listing every named
check**. It is the bookkeeping companion to
[making a load-bearing decision executable in CI](architectural-fitness-functions.md):
that page decides *whether* a decision earns a check, this one keeps the set of
checks honest once there are more than three of them.

It exists because the interesting question about a fitness function is almost
never "what does it assert?" — the decision record already answers that. It is
**"is it actually running, and if not, when will it be?"** Without a single
table, that question is answered by reading the CI configuration, and nobody
reads the CI configuration.

## The columns

| Column | What it holds | Why it is load-bearing |
| :--- | :--- | :--- |
| **Fitness function** | The check's name, taken from the decision it defends — not from the tool that implements it. | This is the string that appears in a red build. It has to point at the reason without a lookup. |
| **Enforced by** | The exact script or test path, as a reader could run it. Multiple paths when a decision is guarded from two sides (a static rule *and* a runtime probe). | An entry with a prose description instead of a path is not enforced; it is intended. The path is what makes the row falsifiable. |
| **Lane** | Which CI lane runs it: static, integration, or nightly. A check may sit in two. | The lane is the guarantee. Static stops a violation; nightly discovers one. Moving a row between lanes is a change in what the architecture promises. |
| **Status** | Active, pending a named milestone, or deferred to a named milestone. | Turns the gap between the decisions made and the decisions enforced into something visible rather than something felt. |

## Status vocabulary

- **✅ active** — the check runs today and a violation fails the build. Requires
  a real path in *Enforced by*. There is no such thing as an active check with
  no enforcement point.
- **⏳ pending → \<milestone\>** — the decision is made and the check is
  specified, but the code it keys on is still being written. The milestone is
  named, not implied.
- **⏸ deferred → \<milestone\>** — the check cannot be written yet because its
  subject does not exist (a package not yet created, a surface not yet built).
  The milestone that creates the subject is named.

**Deferred entries are commitments with a date, not aspirations.** A deferred
row without a milestone is a wish, and a registry that accumulates wishes stops
being read. If a deferred row cannot name the milestone that will activate it,
either the milestone is missing from the plan or the check was never really
going to be written — resolve which, and either name it or delete the row.

Some checks measure rather than gate — a latency or bundle-size budget that
alerts on regression instead of failing the build. Mark those explicitly
(**📊 reporting**) rather than filing them as active, so nobody reads the
registry as promising a boundary it does not enforce.

## Example

A filled registry, with generic entries — a reader should be able to see the
shape without the entries meaning anything in their own system:

| Fitness function | Enforced by | Lane | Status |
| :--- | :--- | :--- | :--- |
| append-only role | `db/checks/append-only.mjs` (grant lint) + `db/test/append-only.integration.test.ts` | static + integration | ✅ active |
| row-policy-on-every-scoped-table | `db/test/policy-present.integration.test.ts` | integration | ✅ active |
| cross-tenant probe | `db/test/cross-tenant-read.integration.test.ts` | integration | ✅ active |
| read-model-does-not-import-domain | `.dependency-cruiser.cjs` rule `read-model-not-domain` | static | ✅ active |
| feature-does-not-import-sibling-feature | `.dependency-cruiser.cjs` rule `feature-isolation` | static | ✅ active |
| semantic-tokens-only-in-components | `lint/rules/no-primitive-tokens.mjs` | static | ✅ active |
| no-inline-route-handlers | `scripts/check-route-registration.mjs` | static | ⏳ pending → M2 (endpoint refactor) |
| full-rebuild-within-budget | `ci/nightly/replay.integration.test.ts` (synthetic seed) | nightly | ✅ active |
| cold-start-within-budget | `ci/perf/cold-start.mjs` | nightly | 📊 reporting |
| surface-boundary (no app imports another app) | — (needs the shared logic package to exist) | — | ⏸ deferred → M3 (second client surface) |

Two things the example is meant to show. First, the **append-only role** row is
guarded from both sides — a static grant lint and a runtime probe — because a
check that only reads the migration source cannot see a grant applied by hand,
and a check that only probes the running database cannot see a grant about to be
applied by a merged migration. Second, the **surface-boundary** row is deferred
with its milestone and its reason, rather than being quietly absent; the absence
is the thing worth writing down.

## Rules that keep it honest

- **The registry lives beside the decisions, in one place.** One table in the
  architecture document, not a section per decision record. Decision records name
  their own check and link here; the registry is the only place the *whole set*
  is visible, which is the only place the gaps are visible.
- **A row is added when the decision is made, not when the check is written.**
  A decision that ships with a `⏳ pending` row is honest. A decision that ships
  with no row is how a check gets forgotten.
- **Every active row's path must resolve.** The commonest drift is a renamed
  file or a test that fell out of a lane's glob while the registry kept saying
  active. Audit the paths on a schedule — at each milestone is enough — and
  prefer a lane that fails when a named check produced no result at all.
- **Exemptions are visible or they are invisible forever.** If a rule carries
  suppressions, the registry row says so. An exemption list nobody reads is
  indistinguishable from a deleted check.
- **Deleting a row is a decision.** A check removed because the decision was
  reversed is fine, and should be traceable to the decision record that reversed
  it. A check removed because it kept failing is an architectural change made by
  attrition — the trail is what stops that from happening silently.
