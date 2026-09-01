---
type: Guidance
title: Putting the seam at the commodity API, not at the vendor
description: Make the architectural seam a commodity API that several independent implementations already speak — the S3 API for object storage — or, where no commodity API exists, a narrow provider interface owned by the domain layer, and require the local development double to honor the same seam, choosing that double on upstream health rather than popularity.
tags: [portability, seam, s3-api, provider-interface, local-double, adapter, test-double, lock-in]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:34:36Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: s3-api-reference
    resource: https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html
    title: Amazon S3 API Reference — the de-facto object-storage interface
  - id: gcs-interoperability
    resource: https://cloud.google.com/storage/docs/interoperability
    title: Google Cloud Storage — XML API interoperability with the S3 API
  - id: r2-s3-compat
    resource: https://developers.cloudflare.com/r2/api/s3/api/
    title: Cloudflare R2 — S3 API compatibility, including documented divergences
  - id: cockburn-hexagonal
    resource: https://alistair.cockburn.us/hexagonal-architecture/
    title: Cockburn — Hexagonal Architecture (ports and adapters)
  - id: fowler-contract-test
    resource: https://martinfowler.com/bliki/ContractTest.html
    title: Fowler — Contract Test
  - id: fowler-test-double
    resource: https://martinfowler.com/bliki/TestDouble.html
    title: Fowler — Test Double
  - id: hohpe-lockin
    resource: https://martinfowler.com/articles/oss-lockin.html
    title: Hohpe — Don't get locked up into avoiding lock-in
---

# Putting the seam at the commodity API, not at the vendor

## Technique

Choose *where* the vendor stops and your system starts, and put that line at an
interface that is already a commodity rather than at the vendor's own SDK.

Two shapes, depending on whether the commodity interface exists yet:

**Where a commodity API exists, target the API.** Object storage is the clearest
case: the S3 API is spoken by the dominant provider, by competing providers
natively, by at least one major hyperscaler through an interoperability mode, and
by several self-hostable open-source servers. Targeting that API with one client
means the same code path reaches the local double, the production bucket, and
the named migration target — so a provider change is configuration rather than an
SDK swap. The test for "commodity" is **several independent implementations you
would actually consider**, not the popularity of any one of them.

**Where no commodity API exists, define a narrow interface and own it in the
domain layer.** Authentication is the standard example: a provider interface
with domain-shaped operations — verify a credential, get the current user,
provision a user, revoke a user, assign a role — declared in the layer that owns
the meaning, with the vendor library sitting behind it as one adapter. The
direction of the dependency is the whole point: the domain declares the port,
the edge implements it, and no vendor type crosses the line.

Four commitments make the difference between a seam and a decorative interface:

**The local development double sits on the same seam.** If local development
talks to a vendor emulator while production talks through the commodity API, the
seam is never exercised and the double tests a path you do not ship. Putting the
double behind the same interface means every local run and every integration test
is also a portability test — the cheapest possible continuous exercise of the
escape valve described in
`guidance-portability-seams/concepts/named-migration-triggers.md`.

**Choose the double on upstream health, not popularity.** The most familiar
double is often the wrong one. *Evidence shape: a production system rejected the
most popular self-hostable S3 double — the obvious, best-documented choice —
because its upstream had been abandoned, leaving a set of unfixed CVEs and a
distribution-level "insecure" marking, and adopted a maintained alternative
instead.* The reasoning generalizes cleanly: on localhost with throwaway
credentials the specific vulnerabilities were largely inapplicable, so the
decision did not turn on threat modelling — it turned on the fact that a
substrate you intend to keep should not be founded on a dependency nobody
maintains. Production was never going to be the double, which is exactly what
frees the local role to optimize for maintenance and determinism over community
familiarity. Weigh, in order: is upstream alive; does it honor the exact leg you
depend on; does it come up deterministically (static credentials, single process,
a real readiness signal); and only then, how many answers exist online.

**Hazards of the seam belong at the seam.** Cross-implementation incompatibilities
are properties of the commodity API, not of one server. When a client-library
default breaks against S3-compatible servers generally — the canonical example
being a checksum parameter computed over an empty payload at presign time, so
the real upload body then fails validation — the fix belongs in the one shared
client factory, with a test asserting it, not at the call site that happened to
hit it first. A seam with a scattered set of one-off workarounds is a seam you
cannot reason about.

**Say what is inside the seam and what is outside.** The boundary is a scope
decision as much as a technical one. A vendor's own permission model is the
common trap: an auth library ships roles and groups, and if those roles are
allowed to decide domain access, then swapping the library later drags the
authorization model with it. Keep vendor-provided roles scoped to what the vendor
owns — membership, billing, user administration — and let domain authorization be
decided by your own model (see `guidance-tenant-isolation`). The seam holds only
if the concepts on either side stay separate.

## Applies when

- **A commodity API exists with several independent implementations you would
  genuinely consider**, and you can name two of them. One implementation plus a
  specification is not a commodity.
- **The capability you are actually buying lives on the commodity path.** For
  object storage: store bytes, retrieve bytes, presign a URL, list a prefix. If
  what you need is on that path, the seam costs you nothing in capability.
- **You need a local or CI double at all** — because the double is the second
  implementation that keeps the seam honest, and its existence changes the
  economics of the whole technique. Without one, an interface with a single
  implementation is much harder to justify.
- **You have already named a migration target for this layer**, and the target
  speaks the same commodity API. The seam is what turns that named target from an
  aspiration into a configuration change.
- **The vendor's differentiating value is somewhere other than the API surface** —
  durability guarantees, operational maturity, regional footprint, integration
  with the rest of the platform, procurement acceptability. Then you can take the
  value and leave the coupling.
- **For a bespoke provider interface:** the concept is a domain concept with
  several competing vendor implementations and a plausible swap horizon — an
  enterprise customer demanding a federation your current library cannot do, a
  licensing change, a per-user pricing model that compounds badly. The interface
  is worth its indirection when a specific future swap is nameable, not merely
  imaginable.
- **The dependency is reached through an in-process client library**, so the seam
  can be a type in your own codebase. When the integration shape is a network
  gateway, a sidecar, or a managed connector that the platform owns, the seam is
  a wire protocol and a deployment artifact instead, and the portability question
  becomes whose infrastructure speaks it — a different analysis with different
  costs.
- **The data behind the seam is the expensive part.** Bytes and user records are
  what pin a system to a vendor. A seam in front of the layers that hold them is
  where portability work actually pays.

## Doesn't apply when

- **The proprietary API surface is the thing you are buying.** If you chose a
  product for a capability only it has, hiding it behind a generic interface pays
  the abstraction cost and forfeits the reason for the purchase. The tempting
  version is using a database you chose for its unique features as a queue and
  then wrapping it in a generic queue interface: now the interface has to be the
  intersection of "database" and "queue", the features that justified the choice
  are unreachable through it, and the abstraction protects a migration you would
  not want.
- **The commodity API is a least-common-denominator that forfeits the capability
  that justified the dependency.** Sort the capability into one of two buckets
  first, because they have different remedies and conflating them is how teams
  reach for an escape hatch they did not need. *In the API and unevenly
  implemented*: multipart upload and lifecycle configuration are both part of the
  S3 API and both implemented by the mainstream alternatives — the risk is not
  absence but divergence in part-size rules, expiration semantics and error
  codes, and the remedy is the contract test suite described under the drift
  failure mode below, not a vendor-native path. *Genuinely off the commodity
  path*: server-side transforms, tiering across proprietary storage classes,
  event notification wiring, and fine-grained IAM have no portable equivalent —
  the alternatives either do not implement them or express them in a different
  model entirely. If something in the second bucket is load-bearing, the honest
  options are to go vendor-native and record the reversal cost, or to put the
  vendor-native path through a labelled escape hatch on the seam so the exception
  is visible and countable — not to pretend the commodity API covers it.
- **There is only one implementation.** A "standard" with one implementation is a
  vendor API with extra ceremony. This is worth re-checking rather than assuming:
  implementations get abandoned, and a two-implementation commodity can quietly
  become a one-implementation one.
- **The interface would have exactly one implementation, forever, with no double
  and no named swap target.** That is indirection with no counterparty: every
  reader pays the extra hop, nobody ever benefits. Write the vendor call
  directly and be honest in the record that you did.
- **The seam would sit at the wrong granularity.** Wrapping an entire relational
  database behind a generic persistence interface, to be portable across engines
  you will never use, costs you the dialect features you chose the engine for —
  recursive queries, notification channels, full-text indexing, row-level
  security. Seams belong at replaceable components, not at the foundation the
  design assumes.
- **No migration is plausible.** A contractual or regulatory single-vendor
  mandate, an air-gapped environment with one available service. Record the
  constraint instead of building a seam that protects against nothing.

## Trade-offs

**Buys** one client across local development, CI, production and the named
alternative, which collapses four integration surfaces into one and makes the
migration a configuration change. It buys a local double that genuinely exercises
the production code path, so a green local run is evidence about production
rather than about the emulator. And it buys a small, auditable list of places
where the vendor is actually mentioned — which is what makes erosion detectable
at all.

**Costs**, first, capability: you are living on the intersection of the
implementations, so vendor-native features arrive as named migrations rather than
free, and "we could just use the provider's feature for that" becomes a decision
instead of a shrug. Second, you own compatibility: the S3-compatible ecosystem
has real behavioural divergence, and when a client-library default breaks against
one implementation you find it and you fix it — the vendor will not, because from
the vendor's point of view nothing is wrong. Third, ergonomics: a maintained but
less ubiquitous double has a smaller answer base online, unfamiliar admin
tooling, and its own bring-up quirks, and those costs land on every developer
every day rather than once at migration time. Fourth, for a bespoke provider
interface, a layer of indirection to read through and a constant pressure to
widen it.

The quality attributes moved are **portability** and **testability**. What is
paid is **peak capability**, some **developer ergonomics**, and the introduction
of a new defect class — cross-implementation divergence — that did not exist
before.

**What would make this stale.** The technique is priced entirely off the
existence of a commodity API with live competing implementations, and both halves
of that can move. It gets *weaker* if the object-storage API bifurcates — if
providers' compatibility modes drift far enough that "S3-compatible" stops being
a useful claim and each implementation needs its own conditional handling, the
seam becomes a compatibility matrix and stops paying. It also gets weaker if the
capabilities that matter migrate off the commodity path: as more of the value in
storage moves to server-side processing, event integration, and lifecycle
intelligence, the intersection shrinks and the least-common-denominator
counter-case above swallows more cases. It gets *stronger*, or rather changes
shape, if protocol-level standards commoditize a layer that today needs a bespoke
interface: where identity federation converges on well-implemented open
protocols, the protocol becomes the seam and a hand-rolled provider interface in
front of it turns into redundant indirection. Re-check, per layer, whether the
commodity interface still has more than one serious implementation and still
carries the capability you need.

## Failure modes

- **Seam erosion.** A vendor-specific parameter goes through "just this once",
  behind a flag, for a feature that ships next week. Then a second, because the
  first one set the precedent. Then the deployment pipeline learns a
  vendor-specific step, and the infrastructure code adopts a vendor-only resource
  type. Nothing breaks, no review objects to any single instance, and the seam is
  decorative long before anyone says so — usually discovered during the migration
  study it was supposed to make unnecessary. The diagnostic is mechanical: search
  for imports of the vendor SDK outside the adapter directory and count them over
  time. The remedy is equally mechanical — encode the import boundary as a
  build-failing check so the third exception has to be argued for rather than
  merged (see `guidance-fitness-functions`).
- **The double drifts behaviorally from production, so local green means
  nothing.** The double implements the same API and different behaviour, and the
  divergences are exactly the ones nobody tests: checksum computation and
  validation, presigned-URL signature versions and expiry semantics, path-style
  versus virtual-host addressing, multipart thresholds and part-size rules,
  conditional-request headers, listing pagination and ordering, and error codes
  and status mapping on the failure paths. The shape of the incident is always
  the same — the full suite passes locally, the first real upload fails with a
  digest or signature error, and the debugging starts from the assumption that
  the code is wrong. Counter it with a contract test suite that runs unchanged
  against both the double and a real bucket on a scheduled lane, and keep the
  known-divergence list in the repository as a living document rather than in
  someone's memory.
- **The double's conveniences leak into the design.** Static, long-lived
  credentials make the local environment deterministic, and then the code quietly
  assumes long-lived credentials while production issues short-lived, rotated
  workload identity. The same happens with permissive default bucket policies,
  absent rate limits, and consistency: a single-node double gives immediate
  read-after-write and stable list ordering for free, so code that would race
  against a replicated production store — reading a key straight after writing
  it, or paging a listing while another writer appends — passes locally every
  time. The double should be deterministic in its *setup* and faithful in its
  *semantics*; when those conflict, state the consistency model you are actually
  shipping against, write the difference down, and test the retry path somewhere
  that has it.
- **The double's bring-up is not atomic, and CI goes flaky.** Multi-component
  stores frequently expose the API port before the component behind it is ready —
  a metadata or filer tier can lag the S3 endpoint by tens of seconds on a cold
  start — so bucket provisioning succeeds intermittently. The failure looks like
  a test-suite problem and is an infrastructure one. Wait on a real readiness
  probe of the component you are about to use, never on a sleep.
- **The double is abandoned upstream mid-project.** The reason to pick on
  maintenance in the first place, and the reason to re-check: an actively
  developed store at adoption can be archived two years later, at which point you
  are pinning an old version, carrying unfixed issues, or doing an unplanned swap
  during a release. Put the double's upstream health in the same periodic review
  as the named migration target.
- **Vendor types leak through a provider interface.** The signature promises a
  domain type; the implementation returns the vendor's session or user object,
  and within a month three call sites are reading fields that only exist on it.
  The interface still compiles, the boundary is gone, and the swap that the
  interface existed to enable now touches every one of those call sites. Return
  types you define; map at the adapter; make the mapping boring and total.
- **The interface is declared on the wrong side of the boundary.** The adapter
  package defines the port and the domain imports the adapter, so the dependency
  arrow points at the vendor and the "seam" is one package deep. This is
  invisible in a diagram and obvious in an import graph — and it is the single
  most common way ports-and-adapters is implemented backwards.
- **Scope creeps across the seam.** The vendor's model of roles, groups, or
  organizations starts being used for decisions the domain owns, because it is
  right there and it almost fits. By the time a swap is considered, the vendor
  supplies a load-bearing part of the authorization model and replacing the
  library means reimplementing access control. Cheap to prevent at the interface's
  design, expensive at any point after.
- **The seam is exercised only in one direction.** Local development and CI hit
  the double every day; nothing ever hits the second production-grade
  implementation. That is far better than no exercise, but it validates the seam
  against the *easiest* implementation, and the divergences that matter are the
  ones between two real providers. Once a year, point the integration suite at
  the named migration target and see what breaks.

## Alternatives considered

- **Vendor-native SDK with no seam.** Wins when there is one plausible provider,
  when the vendor-specific features are precisely the point, and when you accept
  that a migration would be a rewrite. It is the cheapest and most capable path
  and it is a legitimate choice — just record it as one, with the reversal cost
  named, rather than arriving at it by default.
- **Vendor-native SDK now, adapter written at migration time.** Wins when the
  migration probability is genuinely low and the codebase is small enough that
  retrofitting an adapter is a contained job. Loses in the usual case: the
  adapter gets written under deadline pressure, against a vendor surface that has
  been used inconsistently for years, with no local double behind it to prove it
  works.
- **A cloud-abstraction or multi-cloud SDK layer.** Wins when you genuinely
  operate on two providers today and the library is well maintained. Loses as a
  portability hedge, because you take on a second dependency with its own
  least-common-denominator, its own lag behind provider features, and its own
  upstream-health risk — the exact risk that made you distrust the vendor in the
  first place, now with a smaller maintainer base.
- **The provider's own emulator as the local double.** Wins when you have decided
  to be vendor-native and want the highest local fidelity to *that* vendor,
  including features off the commodity path. Loses the moment your named
  migration target speaks a different API, because you then need an adapter
  anyway and the emulator has been quietly validating the wrong contract.
- **A real cloud sandbox per developer instead of a local double.** Wins on
  fidelity, decisively — there is no divergence to discover because there is no
  double. Loses on cost, on offline and airplane development, on test
  determinism, on CI wall-clock time, and on the credential-management burden of
  handing every contributor real cloud access.
- **Ports and adapters everywhere, by policy.** Wins on uniformity and on not
  having to argue the case per dependency. Loses because most dependencies have
  no swap horizon and no second implementation, so the policy manufactures
  indirection that never pays — and, worse, devalues the seams that do, since a
  codebase where everything is behind an interface gives no signal about which
  boundaries are load-bearing.
