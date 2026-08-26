---
type: Guidance
title: Splitting a workspace into apps and packages with the domain package at the dependency center
description: Divide a monorepo into apps (deployables at the edge) and packages (libraries), with the domain package at the dependency center — packages point inward toward domain, domain imports nothing app- or infrastructure-flavored, apps only compose — and make the import direction a tool-enforced fact while a task-graph runner keyed on the workspace graph orchestrates builds.
tags: [architecture, monorepo, workspace, dependency-direction, clean-architecture, build-orchestration]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T17:08:40Z }
status: stable
stale_after: 2028-03-01
sources:
  - id: pnpm-workspaces
    resource: https://pnpm.io/workspaces
    title: pnpm — Workspaces
  - id: turborepo-task-graph
    resource: https://turborepo.com/docs/core-concepts/package-and-task-graph
    title: Turborepo — Package and Task Graph
  - id: nx-module-boundaries
    resource: https://nx.dev/features/enforce-module-boundaries
    title: Nx — Enforce Module Boundaries
  - id: fowler-monolith-first
    resource: https://martinfowler.com/bliki/MonolithFirst.html
    title: Martin Fowler — MonolithFirst
  - id: google-monorepo
    resource: https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/
    title: Potvin & Levenberg — Why Google Stores Billions of Lines of Code in a Single Repository
  - id: clean-architecture
    resource: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
    title: Robert C. Martin — The Clean Architecture
  - id: dependency-cruiser-rules
    resource: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md
    title: dependency-cruiser — Rules Reference
---

# Splitting a workspace into apps and packages with the domain package at the dependency center

## Technique

Divide the workspace into two tiers and give the dependency graph one direction.

- **`apps/*`** — the deployables. Each app is a process someone runs: an HTTP
  server, a worker pool, a web client, a mobile client. Apps sit at the **edge**
  of the graph: nothing imports an app. An app's own code is composition —
  wiring, configuration, transport, rendering — and the business decisions it
  makes are decisions it delegates.
- **`packages/*`** — the libraries. Persistence schema and migrations, API
  request/response contracts, shared render-free logic, shared toolchain config.
  Packages are imported by apps and by each other.
- **`packages/domain`** — the center. Types, invariants, and the interfaces the
  rest of the system implements. It is the one package that imports **nothing
  from the other two tiers**, and ideally nothing at runtime at all.

The rule that makes this a structure rather than a folder convention is the
direction: **apps depend on packages; packages depend on domain; domain depends
on neither.** This is Martin's dependency rule applied at workspace granularity —
the same inversion as a hexagonal or clean architecture, drawn one level up where
a package manager can see it. The domain declares an interface for what it needs
from the outside (a clock, a provider of identity, a repository shape); an
infrastructure package implements it; an app picks the implementation at startup.

Three properties follow, and each is worth stating as a claim someone can check:

1. **The domain is testable without infrastructure.** If exercising a business
   rule requires a database container, the center has already leaked. This is the
   cheapest continuous signal that the topology is still real.
2. **Apps are thin enough to be substitutable.** A second client, a second
   worker runtime, or a replacement transport is added at the edge without the
   center noticing. If adding an app means changing the domain, the domain was
   carrying app-shaped concerns.
3. **A change to a shared type is atomic.** One commit updates the domain and
   every consumer, and CI proves every consumer still compiles. This is the
   single largest thing a monorepo buys over a polyrepo, and it is bought
   precisely by *not* versioning the internal packages.

**Enforce the direction with a tool, not with review.** A dependency analyzer
(dependency-cruiser and equivalents) or a workspace-native boundary system (Nx
module boundary tags, package-manager workspace constraints) runs in CI with
rules of roughly this shape:

- `packages/domain` must not import any other workspace package;
- `packages/domain` must not import an infrastructure driver — the database
  client, the HTTP framework, the object-store SDK, the auth library;
- no package may import an app;
- no app may import another app.

Every rule must be **verified to bite** at authoring time: write the violating
import, watch CI fail, delete it. A boundary rule keyed on a path that does not
exist passes vacuously and reads as coverage. Naming these checks, assigning
them a lane, and tracking whether they still run is the practice in
`guidance-fitness-functions/bundle/concepts/architectural-fitness-functions.md`;
this page only supplies the direction worth checking.

**Orchestrate builds with a task graph keyed on the workspace graph.** A runner
(Turborepo, Nx, and equivalents) reads the same dependency edges the package
manager already resolved and derives task order from them: build the domain
before the packages that import it, and skip any task whose inputs are unchanged.
The workspace graph is therefore load-bearing twice — once for module resolution,
once for build scheduling — which is a reason to keep it honest, and a reason
that a graph shaped like a star (everything pointing at one hub) has worse CI
behavior than one shaped like a shallow tree.

What this page does **not** decide: how source is arranged *inside* an app —
that taxonomy is `guidance-vertical-slices` — and what the domain model actually
contains, which is `guidance-ddd`. This is a claim about workspace topology and
nothing else. In particular, "we have packages" is not a claim about services:
package boundaries are compile-time and free to cross, service boundaries carry
latency, partial failure, and independent deployment. A package graph is not a
migration path to microservices, and treating it as one is how a legible layout
becomes an unplanned distributed system.

## Applies when

- **Two or more deployables share a business core.** This is the load-bearing
  condition. An API and a worker pool that both understand the same entities, or
  a server and two clients that must agree on the same contract, are the case
  the topology exists for. The plural matters: with one deployable the center has
  nobody to be central *to*.
- **The deployables share a release cadence.** Everything ships from one commit,
  or close enough that a single version of a shared type across the tree is
  acceptable at all times. Un-versioned internal packages are exactly the
  simplification a monorepo trades for, and they only work if consumers move
  together.
- **The language has first-class workspace tooling.** A package manager that
  resolves intra-repo dependencies natively (pnpm workspaces, npm/yarn
  workspaces, Cargo workspaces, Go modules with a work file, Gradle composite
  builds), plus a way to express the boundary rule mechanically. Without both, the
  topology is a naming convention, and every failure mode below gets worse.
  Examples throughout this pack are drawn from the TypeScript ecosystem — pnpm
  workspaces plus a Turborepo task graph — because that is where the reasoning
  was hardened; the tiers, the direction, and the enforcement point transfer
  unchanged, and only the tool names need re-deriving.
- **The team is small enough to hold the whole graph.** A monorepo's atomic
  cross-cutting change is a benefit when one team can review a diff that touches
  five packages, and a hazard when five teams have to.
- **Cross-cutting change is expected, not exceptional.** If shared types and
  contracts are still being discovered — an early product, an evolving domain —
  the atomic-change property is being used weekly. If the contract is settled and
  each deployable evolves alone, that property is being paid for and not used.

## Doesn't apply when

- **There is exactly one deployable.** A workspace is ceremony here: directories
  inside one project do everything a package boundary would, without a package
  manifest, a build edge, or a resolution step per boundary. Use folders until
  the second app is **real** — running, deployed, and importing the shared code —
  and only then extract packages from the code that turned out to be shared. The
  tempting version of this mistake is the one that actually happens: scaffolding
  `packages/domain`, `packages/contracts`, and `packages/ui-logic` for apps that
  exist on a roadmap. The boundaries get drawn from a guess about what will be
  shared, they are wrong, and they are now expensive to redraw because they have
  manifests and build config attached. A single-app repo that later grows a
  second app has a much easier day than a five-package repo whose boundaries were
  invented before the second consumer existed.
- **Teams need independent release cadence and ownership boundaries.** Once two
  teams must ship on their own schedules, un-versioned shared packages become
  the coupling: any change to the center forces the other team's tree to rebuild
  and revalidate on your timetable. Either split the repositories, or keep one
  repo and introduce **strict internal versioning** with a changeset/release
  workflow — which restores independence and gives back most of the atomic-change
  benefit that motivated the topology. Choose knowingly; the halfway state
  (one repo, no versioning, independent teams) is the one that generates
  interrupt-driven work for whoever owns the center.
- **Packages are published to external semver consumers.** Publishing changes the
  calculus entirely. Public consumers cannot be updated atomically, so every
  internal refactor now has a deprecation window, a compatibility policy, and a
  release process. A repo that publishes libraries and a repo that composes
  applications are different artifacts that happen to share a directory shape;
  do not reason about the second using experience from the first.
- **The languages differ across deployables.** With a Python worker pool and a
  TypeScript API, no package manager resolves the graph and no task runner
  derives order from it. A polyglot repo can still be one repository, but the
  domain-at-the-center property has to be re-established a different way — a
  schema registry, generated clients from one specification — and the technique
  on this page is not what you are doing. See
  [the single-language bet](single-language-end-to-end.md) for the choice
  upstream of this one.
- **The organization cannot enforce the direction.** No dependency analyzer, no
  CI gate, no appetite to add one. Then the graph is a belief, not a property,
  and the "domain quietly imports infrastructure" failure below is not a risk but
  a schedule. Say honestly that the layout is a convention, and expect it to be
  approximately true within a year.

## Trade-offs

**Buys:** atomic cross-cutting change — rename a domain type and every consumer
in the tree is updated and type-checked in one commit, with no version bump, no
publish, no coordination window. Note the scope of that guarantee: it holds
**within a commit**, over the source in the repository. Artifacts already
deployed — a running service on the old revision, a mobile binary in the field —
were compiled against an earlier graph and are unaffected by your commit, so
wire-level compatibility remains a separate obligation
([the language page](single-language-end-to-end.md) has the failure mode). One
dependency graph, so "who uses this?" is a
query and not a survey. Shared toolchain configuration in one place. A domain
that can be exercised in unit tests without any infrastructure at all, which
makes the cheapest tests the ones that cover the most important rules. And a
layout legible to a new contributor or a coding agent in one look: the tier tells
you what a file may import before you read it.

**Costs, in the order they are felt:**

- **One toolchain version for everyone.** A compiler, linter, or test-runner
  upgrade is a whole-repo event. The app that needs the new version and the app
  that cannot take it yet are in the same tree, and the second one wins by
  default. This is the trade most often discovered late.
- **CI that must scale with the graph.** A naive pipeline runs everything on
  every commit, and the cost grows with package count, not with change size.
  Affected-package selection and remote caching are not optimizations here; they
  are the thing that makes the topology survive its second year. Budget for them
  at adoption, not when CI reaches twenty minutes.
- **Blast radius grows with every package pointed at the center.** A change to the
  domain is, by construction, a change that can break everything. That is the
  property being bought — you find out immediately — but the cost is real: the
  domain becomes the file people are most reluctant to touch, and reluctance to
  touch the center is how the center calcifies.
- **A per-file boundary judgment.** Every new module needs an answer to "which
  tier?", and the answer is occasionally arguable. The rule below is what keeps
  it cheap: *does it know a business rule and nothing about how the system is
  deployed?* → domain. *Does it talk to something outside the process?* →
  infrastructure package. *Is it a process someone starts?* → app.

The quality attribute this moves is **modifiability**, specifically the cost of a
change that crosses component boundaries. What it spends is **deployability
independence** (one cadence) and **build/CI time**. It is a good trade for a
small team shipping several deployables from a shared core, and a bad trade for
independent teams with settled contracts — which is the same trade, evaluated
with different inputs.

## Failure modes

- **A `shared` or `utils` package sits at the center instead of the domain.**
  This is the characteristic failure and it is nearly universal. `shared` is the
  package nobody argues about in review, so anything that two packages need lands
  there: a date formatter, then a config loader, then an HTTP client, then a
  business rule. Within a year it is a **dependency magnet** — every package
  couples through it, so every change to it rebuilds and revalidates the entire
  tree, and its own dependency footprint (the HTTP client, the SDK someone added)
  is now transitively in every consumer including the client bundles. The
  observable symptom is a package with the most inbound edges and no coherent
  answer to "what is this about". The diagnostics are mechanical: count inbound
  edges per package and look at the top one; and grep the shared package for the
  domain's vocabulary — hits are code that belongs in the domain. The fix is
  always decomposition by subject, never a bigger `shared`. Prevention is cheaper:
  do not create the package. Name packages after what they are about.
- **The domain quietly imports infrastructure until the center is decorative.**
  It never happens in one commit. A type import from the database package "just
  for the row shape". A validation helper pulled from the HTTP library. An SDK's
  error class in a domain signature. Each is locally reasonable and passes review.
  The end state is a domain package that cannot be loaded without a database
  driver present, tests that need a container to assert a business rule, and a
  dependency direction that exists in the README and nowhere else. There is no
  incident and no alarm — the build is green the entire way down. **This is a
  fitness-function candidate and should be one of the first checks a project
  writes**: a CI rule asserting the domain's import list, plus a test job that
  runs the domain suite with no services running at all. See
  `guidance-fitness-functions/bundle/concepts/architectural-fitness-functions.md`
  for how to name it, lane it, and keep it from silently ceasing to run; the
  topology claim — that the direction is what makes the domain independently
  testable — is this page's.
- **Task-graph caches poisoned by nondeterministic build steps.** A build step
  reads a timestamp, embeds a git SHA, writes an absolute path, or resolves a
  floating dependency version, and its output stops being a pure function of its
  declared inputs. The runner caches it anyway. From then on **"cached green"
  stops meaning anything**: a cache hit reports success for an artifact that
  would not be produced by a clean build. The failure surfaces as the worst class
  of bug — CI passes, the deployed artifact is wrong, and re-running CI passes
  again. It also surfaces in reverse, as a cache that never hits because an input
  changes every run, quietly turning the runner into a slow no-op that costs
  configuration without buying speed. Guard it: declare inputs and outputs
  explicitly rather than defaulting to the whole package, keep environment
  variables out of build steps unless declared as part of the cache key, and run
  a scheduled cache-disabled full build so a divergence is discovered by a nightly
  job instead of by a customer. Treat a stale-cache incident as a defect in the
  task definition, never as a reason to add a blanket `--force`.
- **The dependency rule is written but never verified to bite.** A glob keyed on
  a path that was renamed, a rule scoped to the wrong workspace, a config file
  the tool silently stopped reading. The check passes, the badge is green, and
  nothing is guarded. Re-verify after every directory rename — the exact moment a
  path-keyed rule stops matching.
- **Exemptions accumulate until the boundary means nothing.** Each one is granted
  for a real deadline; the allowlist is never read as a whole. There is no moment
  that marks when the architecture stopped being enforced. Read the exemption list
  at each milestone and require the decision record to change when it grows.
- **CI time crosses the threshold where people route around it.** Every package
  builds on every commit; the pipeline reaches twenty minutes; someone adds a
  path filter that skips tests for "docs-only" changes, and the filter is wrong.
  The observable precursor is pipeline duration growing with package count rather
  than with diff size. Fix the graph selection, not the coverage.
- **Circular workspace dependencies.** Two packages import each other, usually via
  a type that "belongs to both". The package manager may tolerate it; the task
  runner cannot order it, and the build breaks in a way whose error message points
  nowhere useful. The cycle is almost always a missing package: the shared concept
  wants to be extracted downward, toward the domain.

## Alternatives considered

- **Polyrepo, one repository per deployable** — wins when teams need independent
  release cadence, when ownership boundaries should be enforced by access control
  rather than by convention, and when the shared surface is small and stable
  enough to live behind a published, versioned package. Loses on cross-cutting
  change: a rename that touches four repositories is four pull requests, four
  reviews, four releases, and a window during which the contract is inconsistent.
- **Monorepo with strict internal versioning** (changesets, independent package
  releases) — wins as soon as either an external consumer or an independent team
  enters the picture; it keeps one checkout and one review surface while restoring
  release independence. Loses the atomic-change property that is most of the
  argument for the topology, and adds a release workflow to maintain. This is the
  correct destination when the team grows, and worth naming as the planned exit
  rather than discovering it under pressure.
- **A flat single application with folders** — wins under the single-deployable
  condition above, and wins for longer than most teams expect. Loses when a
  second deployable needs the same code, at which point the extraction is real
  work — but it is work done with knowledge of what is actually shared, which is
  strictly better than guessing early.
- **`shared`/`common` as the center** — wins never, as a deliberate design. It
  appears by accretion, not by decision, which is why it is listed here: the
  alternative to naming a domain package is not "no center", it is an accidental
  center with worse properties.
- **Layer-named packages** (`packages/services`, `packages/repositories`,
  `packages/models`) — wins where a genuine technical layering is the thing that
  varies, and where the whole team already thinks in those terms. Loses for the
  reason by-role organization generally loses: it groups by what changes least
  rather than by what changes together, so a single business change fans out
  across every package, and the dependency direction has to be re-argued per
  layer instead of stated once.
- **A build system with its own dependency model** (Bazel, Pants, Buck) — wins at
  a scale where hermetic, remotely-executed, language-agnostic builds pay for
  themselves: very large repositories, polyglot trees, strict reproducibility
  requirements. Loses for a small team in a single ecosystem, where the ecosystem
  package manager already resolves the graph and the build description becomes a
  second, hand-maintained model of the same thing.
- **No enforcement, direction as documentation** — wins when the repo is
  short-lived or single-authored and the tooling cost is genuinely not repaid.
  Loses everywhere else, and loses in a specific way worth naming: an unenforced
  boundary is worse than no boundary, because readers believe it holds and reason
  from it.
