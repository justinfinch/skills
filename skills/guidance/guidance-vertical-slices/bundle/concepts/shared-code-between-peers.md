---
type: Guidance
title: Sharing code between peer slices without re-centralizing them
description: Constrain any module shared between peer slices to exported functions with no state and no composed behavior, scope it to the narrowest group that actually shares it, and assemble the peers from data rather than from a composite registration function — so the hub the slicing removed is structurally incapable of reassembling inside it.
tags: [architecture, vertical-slice, module-boundaries, shared-code, cohesion, erosion]
created: 2026-09-01
generated: { by: write-guidance/claude-opus-5, at: 2026-09-01T00:00:00Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: parnas-decomposition
    resource: https://dl.acm.org/doi/10.1145/361598.361623
    title: Parnas — On the Criteria To Be Used in Decomposing Systems into Modules
  - id: metz-wrong-abstraction
    resource: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
    title: Sandi Metz — The Wrong Abstraction
  - id: ford-parsons-kua-evolutionary
    resource: https://evolutionaryarchitecture.com/
    title: Ford, Parsons, Kua — Building Evolutionary Architectures
  - id: bogard-vertical-slice
    resource: https://www.jimmybogard.com/vertical-slice-architecture/
    title: Jimmy Bogard — Vertical Slice Architecture
---

# Sharing code between peer slices without re-centralizing them

## Technique

Slicing by capability removes a hub — a controller, a god component, a service
class every operation hung off. The hub then grows back, from the inside, and
the thing that grows it is not laziness. It is **genuinely shared code**: two or
three sibling slices really do need the same error translation, the same
authorization chain, the same formatting. Once that shared thing exists, it has
a location, and the location attracts its callers.

So constrain the shape of anything peers share, rather than trusting discipline
about where it lives. Three rules, all checkable.

**1. A shared module exports functions. It does not export behavior.**

The distinction is not stylistic. An exported *function* is invoked at the call
site, so the call site is where the decision is written and where a diff shows
it. An exported *composed value* — a pre-built middleware chain, a configured
client, a registry object, anything assembled at module scope — is imported and
spread, so the call site declares nothing and the decision lives somewhere no
reader of the call site will visit.

A module shared between peers may hold pure functions and type declarations. It
may not hold module-level state, factories that close over configuration, or
constants whose value is composed behavior. This is the rule that does the real
work, because a function-only module has no gravity: there is nothing in it a
new sibling would want to sit next to.

**2. Scope it to the narrowest group that actually shares it.**

If three routes on one resource share an error mapper, the mapper belongs beside
those three, not in an application-wide `shared/`. A shared module's blast
radius is its reach, and reach is chosen, not discovered. The default direction
of drift is upward — a second group needs one function, so the module is
promoted — and each promotion is a small, locally-correct commit that widens
coupling permanently. Promote deliberately or duplicate; a shared module one
level too high is a shared kernel nobody decided to adopt.

**3. Peers are assembled from data, never by a composite function.**

Something has to collect the slices and hand them to the composition root. Make
that thing a **list**: each slice group exports an array of registrations, the
root concatenates the arrays and walks them. Never a `registerEverything()`
function that calls its siblings.

A function that calls its siblings *is* the hub, wearing a different signature.
It is a place behavior can be added between the calls, it is a place ordering
becomes significant, and it is a place a fourth sibling can be defined inline
instead of beside its peers. An array cannot host any of that. The structural
version of the rule is stronger than the stated one and is what to actually
check: **an aggregation module contains no definition of a peer** — no handler
body, no component, no route — so it is incapable of becoming one.

**Grouping folders group for navigation, never for cohesion.** A directory that
exists so a reader can find things is fine and worth having. It becomes the hub
the moment it acquires module state or shared behavior beyond rule 1's carve-out
— which is what a `_shared/`, `common/`, or `base/` subfolder inside it always
turns out to be. Say in the record that the folder is navigational, and keep the
one narrow shared module directly in it rather than in a subfolder that will
grow.

**When the shared thing preserves known debt, name it as debt with an exit.**
Sometimes the honest reason a shared module exists is that the logic in it is in
the wrong layer entirely — a persistence detail being translated at the
transport boundary, a domain rule living in the presentation tier — and keeping
one copy is cheaper than keeping four. That is a legitimate reason to have the
module and an illegitimate reason to call it the pattern. Write down which
functions are debt, which layer they should move to, and note that no check will
detect them; the constraints on this page keep the debt from spreading, and do
nothing at all to make it leave.

This is the counterpart to the boundary rules on
[REPR endpoint slices](repr-endpoints.md) and
[feature folders](feature-folder-organization.md). Those pages say peers must not
import each other. This page covers what happens to the code they would have
imported — which is the pressure those rules create and do not, on their own,
relieve.

## Applies when

- **Peer-slice organization is already adopted**, at any layer — endpoint slices,
  feature folders, use-case directories, packages in a workspace — and a rule
  says peers do not import each other. This page has nothing to say about a
  codebase organized by technical role; there, shared code is the point.
- **Real duplication has appeared across two or more siblings** and is not
  hypothetical. The trigger is a second slice needing the same translation, not
  a first slice's author anticipating one.
- **The duplicated logic's divergence would be silent.** Error-to-status
  mapping, currency or date formatting, retry classification, wire-error copy:
  things where two siblings drifting apart produces no failing test and no type
  error, only a client that sees two different behaviors from two endpoints that
  should agree. Silent divergence is what makes a shared module worth its
  coupling; loud divergence is not.
- **The shared logic is derivation or translation** — input in, output out — as
  opposed to a resource that has to be constructed once and handed around.
  Rule 1 is only cheap when the thing being shared is genuinely function-shaped.
- **More than one author or agent is adding peers in parallel.** Concurrent
  authorship is what converts a shared module's gravity from a slow drift into a
  fast one, because each author independently finds the existing shared thing
  and lands beside it.
- **The hub has already grown back once**, here or in a sibling system. A
  codebase that has done this once will do it again in the same place; the
  constraint is worth its cost only where the pressure is demonstrated.

## Doesn't apply when

- **The shared thing is infrastructure every peer depends on** — a connection
  pool, an HTTP client, an auth provider, a logger. These are constructed once,
  hold state by nature, and are supposed to be identical everywhere. Rule 1
  would forbid exactly the thing they are, and applying it produces a factory
  called at every call site to rebuild what should be a singleton. These arrive
  by injection from the composition root instead, which is a different technique
  with a different reason. The sorting question is *does every peer depend on
  this, or only these three?* — universal dependency is infrastructure,
  local sharing is what this page governs.
- **Omission is a worse failure than invisible change.** The rules above trade
  centralized uniformity for per-call-site visibility, and that trade inverts
  when the concern is one where *missing it* is catastrophic and *changing it*
  is routine — a mandatory audit log, an encryption-at-rest wrapper, a
  regulatory gate that must be on every path without exception. There, a
  pipeline that cannot be omitted beats N visible declarations that can be
  forgotten once. Decide which failure you are actually more afraid of, and say
  so in the record; this is the single most important judgment on this page and
  the one most often made by default rather than on purpose.
- **The peer count is high enough that duplicated declarations will drift.**
  Per-call-site declaration is legible at a dozen peers and a liability at a
  hundred, where nobody can hold the set in their head and two siblings quietly
  gate on different things. The successor is a **declarative field** on the
  peer's own definition — the peer states *what* it requires, a shared mechanism
  supplies *how* — which keeps the per-peer visibility and drops the
  duplication. Adopt it when the count justifies it, not before, and know that
  it moves the shared mechanism toward being a framework.
- **The ecosystem's idiom is a pipeline or a decorator, and the codebase is
  otherwise conventional.** Where the framework's own grain is centrally-declared
  middleware or attribute-driven behavior, imposing per-call-site composition
  costs a permanent translation between two vocabularies and forfeits the
  ecosystem's tooling. Take the smaller idea instead: keep the *shared module*
  function-only even inside a pipeline-shaped codebase.
- **The duplication is two lines with no logic in it.** A response shape both
  siblings build, a status code both return. Hoisting that is the wrong
  abstraction bought at the price of coupling; leave it duplicated and say in a
  comment where the duplicate lives that you declined to hoist.
- **There is no enforcement and there will not be.** Every rule here is a shape
  constraint, and shape constraints decay silently — the module still exists,
  still has the right name, and now holds a configured instance. Without a check,
  a team gets the ceremony of the constraint and the erosion anyway, which is
  worse than an honestly centralized module a reader knows to distrust.

## Trade-offs

**Buys:** the hub cannot reassemble by increments, because the shapes it would
have to grow through are forbidden and checked rather than discouraged and
reviewed. Changes to shared behavior land in diffs that name every peer they
affect, which is the property that matters most when the shared behavior is
security-relevant — an authorization change that touches six routes shows six
lines, not one. A shared module that is safe to import from anywhere, since it
holds nothing. Peers that stay independently testable, because nothing they
depend on has to be initialized in a particular order. And a merge-conflict
surface that stays near zero: adding a peer touches the peer's own files and one
array, never a function that every other peer also lives inside.

**Costs:** deliberate duplication at call sites, which reads as sloppiness to
anyone who has not read the reason, and therefore needs the reason written down
where the duplication is. N places to update when a genuinely uniform concern
changes, with no compiler help for the one you missed. A shape rule that is only
real if a check enforces it, so this technique is not free of tooling. The
sorting decision in **Doesn't apply when** has to be made per concern rather than
once. And you give up the pipeline's actual guarantee: with central declaration,
a concern applied to the pipeline is applied to everything, and no amount of
per-call-site discipline reproduces that.

The quality attributes this moves are **modifiability** and, more unusually,
**analyzability** — the ability to answer "what does this change affect?" by
reading the diff. What it spends is **uniformity of cross-cutting behavior**,
which is not a rhetorical cost: it is the direct source of the failure mode
below. It is a good trade where the cross-cutting concerns are few and the peers
are many; a bad one where the concerns are many and must be identical.

It changes no runtime property. A function-only shared module compiles to the
same work a behavior-holding one would; this is entirely about what a future
change costs and what a future reader can see.

## Failure modes

- **A cross-cutting gate is omitted on exactly one peer, and nothing says so.**
  This is the 3am entry and it is the direct, deliberate cost of per-call-site
  declaration. A new endpoint ships without its authorization line, or a new
  feature without its tenant scope. The build is green. The tests pass, because
  the tests exercise the handler the author was thinking about. The endpoint
  works — it just works for everyone, and the first evidence is a customer
  seeing another customer's data. Nothing about the duplication makes the
  omission visible; the visibility this technique buys is on *change*, not on
  *absence*. Pay for absence separately and explicitly: assert over the **set**,
  not the instances — every peer either declares a gate or appears on a short,
  reviewed, in-repo list of the deliberately ungated. That list is the artifact,
  and it must be read at every milestone rather than appended to.
- **Duplicated declarations drift into disagreement.** Two siblings implementing
  the same operation gate on different capabilities, or map the same failure to
  different status codes, because one was updated and the other was not found.
  This is the mirror of the omission above and it is quieter: both endpoints
  work, they simply disagree, and the disagreement surfaces as a support ticket
  about inconsistent behavior rather than as an incident. The peer count at which
  this overtakes the visibility benefit is the trigger for the declarative-field
  successor.
- **The function-only rule erodes one convenience at a time.** A function becomes
  a memoized const "for performance". A const becomes a factory taking config. A
  factory becomes a configured instance because every caller passed the same
  config. Each commit is small and defensible and the module now holds behavior;
  the next sibling that needs it lands in the same file, and the hub is back. The
  tell is any export in a shared module that is not a function or a type. Check
  it mechanically, because it is exactly the kind of change that reads as a
  cleanup in review.
- **The narrow module is promoted upward until it is a shared kernel.** A second
  group needs one function from a resource-local module, so the module moves up a
  level. Then a third. Within a year it is an application-wide `shared/` that
  every peer imports, which is the maximum-blast-radius shape the slicing was
  adopted to escape — reached without a single commit that looked wrong. Treat
  upward promotion as a decision that gets recorded, and prefer duplicating one
  function to widening a module's reach.
- **The grouping folder grows a `common/` subfolder.** Same failure, relocated:
  the folder was supposed to be navigational, and now it has a cohesion point
  inside it. The subfolder is where the composite function and the configured
  middleware chain reappear, one level below where anyone is looking for them.
- **The debt in the shared module becomes the pattern.** The module was created
  partly to hold logic that belongs in another layer, on the understanding that
  it would move. It does not move, because it works and it has one home and one
  home is tidy. Two years later the leak is the convention, new peers copy it,
  and the exit is a semantic refactor nobody will schedule. No check detects
  this — the module has the right shape and the wrong contents. It survives only
  as a tracked, dated item with a named destination layer.
- **The check is written against a directory layout that does not exist yet.**
  A rule keyed on `*/shared/*` in a tree that names it `common/`, or scoped to
  the wrong workspace, passes vacuously and reads as coverage. Every rule here
  must be verified to bite when authored — write the violating export, watch it
  fail, delete it — and re-verified after any rename, which is precisely when a
  path-keyed rule stops matching.

## Alternatives considered

- **Duplicate into every peer; no shared module at all** — wins when the
  duplicated logic is small, and especially when its divergence is *loud*: a
  shape the type system checks, a value a test asserts, anything where two
  siblings drifting apart fails a build. Maximal independence, zero coupling, and
  no rules to enforce. Loses when divergence is silent and client-visible —
  status codes and error copy are the standing example — because the failure
  arrives as an inconsistency report from a user rather than as a red build.
- **One application-wide shared module** — wins for genuine infrastructure, and
  for logic that is uniform across the whole system by definition rather than by
  coincidence. Single home, no duplication, easy to find. Loses as the default
  for peer-shared code: it is the widest reach available, every peer imports it,
  and it re-centralizes precisely what the slicing decentralized. The honest
  version of this alternative is to admit it is a shared kernel and record it as
  one.
- **A centrally-declared pipeline or middleware chain** — wins when
  cross-cutting concerns are numerous and genuinely uniform, when omission is the
  dominant risk, and when the ecosystem supplies a maintained mechanism. Its real
  advantage is the one this page cannot reproduce: apply it once, it applies
  everywhere. Loses at low concern count, where the indirection is paid
  immediately and the payoff is not, and loses badly when the pipeline is
  hand-grown in-house — at which point there is a dispatch framework with no
  documentation and no maintainer that nobody decided to adopt. One or two
  concerns are wrappers; six are a pipeline. Adopt it deliberately or not at all.
- **Declarative fields on the peer's own definition** — the peer states
  `requires: X`, a shared mechanism builds the behavior. Genuinely the successor
  rather than a rival: it keeps per-peer visibility, drops the duplication, and
  makes the whole set greppable from one field, which matters most for
  security-relevant concerns. Loses at small scale for one reason — it pushes the
  shared mechanism from a convenience toward a framework, which is the boundary
  the peer-slice pattern is usually protecting. Adopt when peer count makes drift
  more likely than invisible change, and note that it is an additive change, so
  deferring it costs nothing.
- **A base class or mixin the peers inherit** — wins where the ecosystem's idiom
  is inheritance-shaped and the shared behavior is genuinely universal. Loses in
  almost every other case: it is the hub with an inheritance edge instead of a
  call edge, and it drags the standard fat-base-class decay along with it, where
  every peer inherits everything and none needs it.
- **Extract the shared logic into its own package** — wins when it has real
  consumers outside this tree, a stable contract, and someone who owns it. Loses
  as a way to resolve an in-tree coupling argument: a package boundary adds
  versioning and release friction without changing whether the module holds
  behavior, so the same hub reassembles with a `package.json` in front of it.
- **Rely on review** — wins never, and is named here because it is what actually
  happens by default. Every erosion step on this page is one line, locally
  correct, and invisible to a reviewer who was not in the room for the decision.
  A shape constraint with no check is a preference, and preferences decay.
