---
type: Guidance
title: Betting on one language across API, workers, and clients
description: Choose one language for every runtime in the product — API, background workers, web and mobile clients — so domain types and validation schemas travel from the database boundary to the UI as imports rather than as translation layers, and treat the bet as a decision with an explicit revisit trigger rather than a default.
tags: [architecture, monorepo, language-choice, shared-types, polyglot, type-safety]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T17:08:40Z }
status: stable
stale_after: 2028-03-01
sources:
  - id: ford-polyglot
    resource: https://nealford.com/memeagora/2006/12/05/Polyglot_Programming.html
    title: Neal Ford — Polyglot Programming
  - id: boring-technology
    resource: https://mcfunley.com/choose-boring-technology
    title: Dan McKinley — Choose Boring Technology
  - id: ts-project-references
    resource: https://www.typescriptlang.org/docs/handbook/project-references.html
    title: TypeScript — Project References
  - id: node-conditional-exports
    resource: https://nodejs.org/api/packages.html#conditional-exports
    title: Node.js — Package Entry Points and Conditional Exports
  - id: openapi-spec
    resource: https://spec.openapis.org/oas/latest.html
    title: OpenAPI Specification
  - id: zod
    resource: https://zod.dev/
    title: Zod — TypeScript-first schema validation
---

# Betting on one language across API, workers, and clients

## Technique

Pick one language and use it for **every runtime in the product** — the HTTP
server, the background workers, the web client, the mobile client, the migration
and operational scripts. The point is not uniformity for its own sake. It is that
a **type declared once travels everywhere by import**.

Two artifacts do the travelling, and they are the whole argument:

- **Domain types.** The entities, their states, and the shapes that cross the
  wire are declared in one package and imported by the server that produces them
  and the client that consumes them. A rename is a compile error at every call
  site in the repository, in one commit.
- **Validation schemas.** A schema declared once (Zod and its peers in the
  TypeScript ecosystem; the equivalent single-source validator elsewhere) is
  *executed* at the HTTP boundary to parse untrusted input, and its *inferred
  type* is what the client and the domain compile against. Validation and type
  therefore cannot drift, because one is derived from the other rather than
  written alongside it.

The alternative is not "no types" — it is a **translation layer**: an interface
description, a generator, a build step, a generated client, and a review habit
that keeps the description in sync with the code that actually runs. That is a
legitimate and well-trodden engineering choice with real advantages (see
Alternatives). It is also a permanent piece of infrastructure, and the bet on
this page is that for a small team it costs more than the second language is
worth.

**The workspace is what makes this real.** Shared types are only genuinely shared
if there is a package to put them in and a dependency graph that lets both sides
import it — the topology in
[the domain-centered workspace](domain-centered-workspace.md). Without it, "we use
the same language on both sides" degrades within weeks into two copies of the
same interface in two directories, kept in sync by hand, which has all the cost of
this bet and none of its benefit. The two decisions are separable in principle and
paired in practice: the language bet is what the workspace is *for*, and the
workspace is what makes the language bet pay.

**Write the bet down with its revisit trigger.** The decision has one load-bearing
assumption — that the ecosystem covers every runtime need *in view* — and that
assumption expires when the roadmap grows a workload the ecosystem serves badly.
Name that trigger at decision time ("a workload requiring a numerical or ML
library stack we do not have", "a component whose latency budget the runtime
cannot meet"), so the first exception is a decision with a record rather than an
accident with a pull request. A single-language bet without a named exit is not a
strategy; it is an assumption waiting to be violated quietly.

Two boundaries this page does not cross. It says nothing about *what* belongs in
the domain model — that is `guidance-ddd`. And "one language" is not "one process"
or "one service": the API and the workers are separate deployables that happen to
share a compiler, and their process boundary is decided on runtime grounds
(long-lived connections, isolation of CPU-heavy work, independent scaling), not
on language grounds.

## Applies when

- **A small team owns the whole surface.** The concrete version: the same people
  write the server and the client in the same week. Context-switching cost is
  paid per person per switch, and it is the dominant cost at this size. At a size
  where the client team and the server team are different teams, the switch is
  not happening and the argument weakens sharply.
- **The product genuinely spans client and server.** The bet pays in the seam
  between them. A backend-only system with no first-party client has almost
  nothing to share across a language boundary, and should choose its language on
  runtime and library grounds alone.
- **The ecosystem covers every runtime need currently in view.** Check this
  against the roadmap, not against today's code. Enumerate the workloads: HTTP
  serving, background processing, the client runtimes, scheduled jobs, data
  transformation, anything on the near roadmap. If the language has a credible,
  maintained answer for each, the bet is available. If one workload already has
  no good answer, the bet is being made *against* known evidence.
- **The wire contract changes often.** Early product work, an evolving domain,
  contracts still being discovered. This is when imported types earn the most,
  because the alternative is regenerating and reviewing a specification on the
  same cadence. A settled contract that changes twice a year weakens the argument
  considerably — a generator run twice a year is not a burden.
- **Every consumer of the contract is first-party.** The clients are built from
  this repository and deployed by this team. The moment a third party, a partner
  integration, or a public API consumes the same contract, the shared-import
  mechanism reaches only half of them and a published, versioned interface
  description is required regardless — which usually makes it the better single
  answer for both halves.
- **The team's existing depth is in that language.** Not a preference — an
  observable fact about who is available. This assumption is load-bearing enough
  that it belongs in the decision record by name, because if it turns out to be
  false the decision should be reopened rather than lived with.

## Doesn't apply when

- **A workload has a decisive ecosystem elsewhere.** Machine learning and
  numerical work in Python; a high-performance systems component in Rust, Go, or
  C++; a domain with one mature library that exists in exactly one language. Here
  the calculation inverts: **one translation seam at one boundary costs less than
  exiling the workload from its ecosystem.** Re-implementing what an established
  library already does, or living without it, is a permanent tax, while the seam
  is a bounded, well-understood cost paid once — a queue, a schema, a generated
  client. Recognize the shape: the exception should be *a workload*, with a named
  boundary and a defined contract, not a general permission to add languages.
- **The team's existing strength is genuinely polyglot.** A team that is deep in
  two ecosystems and would have to retrain to consolidate is paying retraining
  cost, delivery-velocity cost, and morale cost to remove translation layers it
  is already comfortable maintaining. The honest comparison is retraining versus
  the seams the consolidation would remove — and for an experienced polyglot team
  the seams are usually the cheaper side.
- **Different runtimes have genuinely different operational profiles that the
  single language cannot serve.** A worker whose latency budget or memory profile
  the runtime cannot meet is not an argument to be won by discipline. Measure
  before conceding this — it is also the most commonly *claimed* exception and
  the least commonly true one at early scale.
- **Hiring depends on it.** Team composition is a constraint, not a preference.
  If the labor pool available to this organization is deep in a different
  ecosystem, an elegant type-sharing story that nobody hired can maintain is not
  an advantage.
- **Compliance, certification, or a platform mandate names the stack.** A
  regulated environment, a certified toolchain, or a customer requirement can
  remove the choice entirely. Establish this before designing around it.

## Trade-offs

**Buys:** one cognitive model, so any contributor can follow a feature from the
database boundary to the UI without switching mental gears. Contract drift becomes
a compile error rather than a runtime surprise — the class of bug where a field
was renamed on one side and not the other simply stops existing. No interface
description to maintain, no generator in the build, no generated code in review.
Validation and type stay identical because one is derived from the other. Tooling
consolidates: one linter, one formatter, one test runner, one dependency-audit
surface, one set of CI images. And onboarding is a single ecosystem, which for a
new contributor or a coding agent is the difference between one context and
several.

**Costs:** the ecosystem's weaknesses become the product's weaknesses, everywhere,
with no local escape hatch — you have concentrated risk rather than diversified it.
Runtime and library choices for each workload are constrained to what the language
offers, so some component is running on the ecosystem's second-best answer.
Upgrades are correlated: a compiler or runtime major version is a whole-repo event
(the workspace-level version of this cost is on
[the workspace page](domain-centered-workspace.md)). And the bet is one decision
deep — if the load-bearing assumption about team depth or ecosystem coverage
turns out to be wrong, the correction is expensive and touches everything.

The quality attribute this moves is **modifiability**, and specifically the cost
of a change that crosses the client/server seam. What it spends is
**performance/operational optionality per workload** and **risk diversification**.
It is a good trade for a small team on an evolving product and a bad one for a
system with one workload whose runtime demands are the dominant constraint.

## Failure modes

- **The bet erodes one "temporary exception" at a time, with no record of the
  erosion.** A service in another language because a library was convenient. A
  script in another because someone knew it better. A worker in another because a
  benchmark once looked bad. Each is individually defensible, and none of them
  triggers a decision. Two years later the repository is polyglot, nobody chose
  it, and the team is paying the full cost of a polyglot estate — several
  toolchains, several deployment paths, several dependency-audit surfaces,
  translation at every internal seam — without having received the benefit that
  motivates one, which is *deliberately* placing each workload in its best
  ecosystem. The tell is that no decision record exists for any of the additions.
  Guard it procedurally, not technically: adding a language to the estate requires
  an amendment to the decision that named the bet, stating which condition above
  stopped holding. The exception itself may well be correct — the failure is the
  silence around it.
- **Shared type packages leak server-only concerns into client bundles.** This is
  the specific technical hazard the technique creates, and it is the one with a
  security edge. A shared package holds a domain type; someone adds a constant
  next to it; the constant is a configuration default that references an
  environment variable; a helper is added that imports the database client for a
  row type. Now every client importing that package pulls a transitive server
  dependency into its bundle, and — in the worst version — a secret or an internal
  hostname into a file served to browsers. The failure is silent: type-checking
  passes, the app runs, and the evidence is a bundle nobody inspected. Symptoms in
  order of severity: an unexplained jump in client bundle size; a server-only
  package appearing in the client's lockfile resolution; a string that should
  never have left the server appearing in a shipped asset. Guards, cheapest first
  — keep the shared package free of runtime dependencies so there is nothing to
  leak; use conditional exports so a server-only entry point cannot be resolved
  from a client build; put a bundle-size budget in CI so growth is a failing check
  rather than a graph; and scan built client assets for secret-shaped strings.
  Treat any secret that reaches a bundle as a rotation event, not a code fix.
- **A shared package becomes a coupling point rather than a contract.** Types
  start narrow and accumulate helpers, then behavior, then business rules, until
  changing anything requires rebuilding and redeploying every consumer including
  the mobile app in app-store review. The symptom is a shared package whose commit
  frequency matches the product's, rather than the contract's.
- **Type sharing is mistaken for a compatibility guarantee.** Compile-time types
  are erased at runtime in many ecosystems, and a deployed client is a *previously
  compiled* consumer. A mobile client in the field was built against last month's
  types and cannot be recompiled by your commit. Shared types eliminate drift
  between the code in the repository, not between the server and every binary
  already installed. Versioned endpoints and explicit backward-compatibility rules
  are still required, and the confidence the compiler provides makes forgetting
  this *more* likely, not less.
- **The runtime's weak spot arrives in production rather than in a benchmark.**
  The workload the ecosystem serves badly is usually known in advance and
  discounted. It shows up as latency under load, memory pressure, or a job that
  cannot finish in its window — at which point the exception is granted under
  incident pressure, which is the worst circumstance for choosing a boundary.
  Benchmark the known-weak workload before committing, not after.
- **"One language" is used to justify one process.** The API and the workers get
  collapsed into a single deployable because they share a compiler, and then a
  CPU-heavy background job starves the request path. Language sharing and process
  boundaries are unrelated decisions; keep the deployables separate on runtime
  grounds even when nothing but a build target distinguishes them.

## Alternatives considered

- **Specification-first with generated clients** (OpenAPI, gRPC/Protobuf, and
  equivalents) — wins when consumers are outside the repository, when a language
  boundary is already unavoidable, when the contract is a product in its own
  right, or when strict versioned compatibility must be provable. The
  specification becomes the reviewable artifact and the source of truth, which is
  a genuine advantage at organizational scale. Loses for a small team with only
  first-party consumers: it is a build step, a generator version, generated code
  in review, and a description that can disagree with the code that runs.
- **A best-tool-per-workload polyglot estate** — wins when workloads genuinely
  differ enough that each one's ecosystem materially outperforms a shared choice,
  and when the team has the depth to run several toolchains well. Loses on
  aggregate overhead for a small team: every seam needs a contract, every runtime
  needs a deployment path and a dependency-audit surface, and the context switch
  is paid per person per day.
- **A shared language on the server tier only**, with native clients per platform
  — wins when the platform experience is the product and native SDKs are the
  reason, or when client and server teams are separate. Loses the seam where the
  sharing actually pays: the client/server contract is exactly the boundary the
  bet is trying to make free.
- **One language chosen for the *server* and a different one for the clients**
  (the common real-world split) — wins when the server workload has a decisive
  runtime requirement. Loses on precisely one axis, and it is worth naming
  because it is the only one: every wire contract needs a second declaration or a
  generator. If the contract is small and stable, that cost is small; if it is
  large and moving, it is the cost this whole page is about.
- **Hand-written duplicate types on each side, no generator** — wins for a tiny,
  frozen contract, and it is not a straw man: two copies of a five-field interface
  that has not changed in a year cost nothing. Loses as soon as the contract moves,
  and it loses invisibly — the copies drift, both compile, and the disagreement is
  reported by a user.
