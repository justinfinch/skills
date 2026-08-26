---
type: Guidance
title: Structuring an HTTP boundary as one slice per endpoint
description: Give every route its own directory holding a request schema validated at the boundary, a thin handler that invokes exactly one command or query, and a response DTO — wired by a registration helper that is deliberately a convenience and not a command bus, with dependencies injected at registration and a composition file that registers endpoints and contains no inline handler.
tags: [architecture, api, http, repr, vertical-slice, endpoints, boundary]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:22:41Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: bogard-vertical-slice
    resource: https://www.jimmybogard.com/vertical-slice-architecture/
    title: Jimmy Bogard — Vertical Slice Architecture
  - id: deviq-repr
    resource: https://deviq.com/design-patterns/repr-design-pattern/
    title: DevIQ — REPR (Request–EndPoint–Response) Design Pattern
  - id: ardalis-api-endpoints
    resource: https://github.com/ardalis/ApiEndpoints
    title: ApiEndpoints — endpoints instead of controllers
  - id: parnas-decomposition
    resource: https://dl.acm.org/doi/10.1145/361598.361623
    title: Parnas — On the Criteria To Be Used in Decomposing Systems into Modules
---

# Structuring an HTTP boundary as one slice per endpoint

## Technique

Every route in the HTTP layer becomes a **self-contained slice**: one directory
per endpoint, holding three things and nothing else.

- **Request** — a schema (a runtime validator such as zod, or whatever the
  ecosystem's equivalent is) that parses the incoming body, params, and query at
  the boundary and yields a typed value. Nothing downstream re-validates and
  nothing downstream sees an unparsed request.
- **EndPoint** — a **thin handler**: parse, invoke *exactly one* application
  command or query, shape the result, return. No branching over business rules,
  no second call to a second command, no transaction management.
- **Response** — the DTO the handler returns, owned as a named type rather than
  an anonymous object literal built inline.

A small shared helper — call it `defineEndpoint` — standardizes the parse →
handle → respond flow and the mapping from thrown or returned errors to a
uniform wire error shape. A `registerEndpoints(app, deps)` step walks the slices
and wires each into the framework's router. The application's composition file
constructs dependencies and calls that step, and contains **no route definition
with an inline handler body** — which is a one-line static check, not a
convention. (Naming the check and putting it in a CI lane is the practice
`guidance-fitness-functions/bundle/concepts/architectural-fitness-functions.md`
covers; this page only supplies the check that is worth naming.)

**The registration helper is explicitly not a command bus.** This is the line
that keeps the pattern cheap, and it is the one that erodes. The helper resolves
a slice's route, applies the shared parse and error-mapping wrapper, and passes
the injected dependencies. It has no dispatch registry keyed by message type, no
middleware pipeline that handlers opt into by declaring an attribute or
implementing a marker interface, and no indirection between "this URL" and "this
function". A reader following a request from the route table to the business
logic passes through exactly one hop of framework machinery. Cross-cutting
concerns — session resolution, tenant scoping, rate limits — stay **explicit
wrappers named at the registration site**, so that reading the registration file
tells you which endpoints are gated and which are not.

**Dependencies are injected at registration**, never reached as module
singletons: the connection pool, the auth provider, the storage adapter arrive
as a `deps` argument that `registerEndpoints` threads through. That is what makes
a slice unit-testable with fakes and no running process, and it is most of the
practical payoff.

Two slice kinds are enough for real systems: standard request/response endpoints
through the helper, and **mount or passthrough registrations** — a third-party
library's catch-all handler, a static asset mount, a proxy — expressed as a plain
`register(app, deps)` function living in the same directory tree. Both are
registered from the same place, so the no-inline-handlers invariant holds
uniformly and needs no exemption list. Trivial routes (`/`, health) are slices
too; an exemption list is a maintenance surface and a place for real endpoints to
hide.

Where the wire contract is shared with clients you also own, the request schema
and response DTO **shapes** belong in a package both sides import, while the
slice owns the **binding** — validating with the shared schema, shaping the
shared DTO. That keeps one source of truth for the contract without making the
slice a place clients reach into.

This is one principle applied at one layer. The same principle — slice by
capability, keep slices from importing each other — organizes a client
application's source tree as
[feature folders](feature-folder-organization.md); the two pages describe the
same move on either side of the wire.

## Applies when

- **The API is a synchronous request/response HTTP surface** with a route table,
  and each route has its own request and response contract. This is the
  integration shape the pattern assumes; see **Doesn't apply when** for the
  shapes it does not fit.
- **There is an application layer to be thin over.** REPR presumes the handler
  has exactly one function to call. If the business logic has no home outside
  the handler, adopting REPR just relocates a fat handler into a nicer directory
  — establish the command/query seam first, then slice the boundary over it.
- **Endpoint count is growing and the route file is where new work lands.**
  The honest trigger is a single routes or controller file that every feature
  branch edits, producing repeated merge conflicts and a per-route re-derivation
  of parse → call → map-errors → respond.
- **Error shapes have started drifting between routes.** Two endpoints returning
  a validation failure in two different envelopes is the symptom the shared parse
  and error-mapping step exists to fix; if there is only one route, there is
  nothing to make uniform.
- **The framework is unopinionated about endpoint organization** — a minimal
  router where handlers are plain functions and where nothing in the framework
  already imposes a one-file-per-operation shape.
- **Code will be written by hands that were not in the room** — new contributors
  and coding agents alike. A copyable exemplar slice plus a CI check is a
  convention that survives authors who never read the decision; a paragraph in a
  README is not.
- **Endpoints need to be unit-testable in isolation.** If the only current way to
  test a route is booting the whole app and issuing a request, injected
  dependencies plus a plain handler function is the seam that changes that.

## Doesn't apply when

- **The API is a handful of endpoints and a single routes file is still fully
  legible.** Below roughly a dozen routes, one file that can be read top to
  bottom beats a directory tree that must be navigated. The cost is paid per
  endpoint from day one; the benefit only arrives with volume. Adopt when the
  file stops being readable, and use the existing routes as the reference
  refactor rather than pre-building structure for endpoints that do not exist.
- **The framework's own idiom already gives one-file-per-endpoint.** Several
  ecosystems ship file-system routing, endpoint classes, or handler modules
  where the framework already co-locates the request contract with the handler.
  Layering a second convention on top of one that already does the job buys
  nothing and costs a permanent translation between two vocabularies. Use the
  framework's grain; carry over only the parts it lacks — usually the explicit
  dependency injection and the thin-handler rule.
- **An actual mediator or command bus is in use.** If the system already
  dispatches through a bus with a middleware pipeline, the bus's conventions own
  request validation, cross-cutting behavior, and handler discovery. A second
  registration mechanism beside it produces two ways to add an endpoint and two
  places to look for why one is behaving differently. Pick one. (The converse
  matters too: if you find yourself wanting the pipeline, adopt the bus
  deliberately rather than growing one inside the helper — see **Failure
  modes**.)
- **The surface is not route-shaped.** A GraphQL schema with resolvers, a gRPC
  service definition, a message-driven consumer, or a WebSocket/streaming
  endpoint all have their own unit of organization — a field resolver, an RPC
  method, a subscription handler. The vertical-slice *principle* still holds;
  the REPR *shape* is specific to request/response HTTP, and forcing it produces
  a directory per resolver with two-thirds of the structure empty.
- **The endpoints are genuinely uniform CRUD over a table, generated or nearly
  so.** Where a resource layer or generated router already emits the standard
  five operations correctly, hand-writing five slices per resource is transcription.
  Slice the endpoints that have real contracts; let the generated ones stay
  generated.
- **The team is one or two people who will not enforce the invariant.** The
  pattern's value is that the shape is predictable. Without the static check,
  the first deadline reintroduces an inline handler and the tree becomes "mostly
  slices, plus the ones that aren't" — which is worse than either pure option,
  because a reader can no longer trust where anything lives.

## Trade-offs

**Buys:** one obvious home per endpoint, so the question "where does this route's
validation live?" has a mechanical answer. Uniform request parsing and a single
error-mapping path, so wire error shapes stop drifting per route. Endpoint slices
unit-testable with injected fakes and no process boot. A composition file that
reads as a composition root rather than as the application. A copyable exemplar,
which is the actual mechanism by which a convention propagates to contributors
and agents who never read the decision. And a merge-conflict surface that shrinks
to near zero, because two features adding two endpoints touch two disjoint
directories.

**Costs:** more files per endpoint — three artifacts and a directory where there
was a closure. A helper you now own and must keep lean; it is a piece of
infrastructure with no external maintainer. A validation library becomes a load-
bearing dependency at the transport edge. One more CI gate to keep green. A
one-time refactor of the existing routes, which is pure churn in the diff and
must be sequenced away from in-flight feature work. And genuine cross-endpoint
duplication: two endpoints returning near-identical DTOs will each shape their
own, and the pattern's discipline says to leave it that way until the
duplication is proven rather than to hoist a shared mapper that re-couples the
slices.

The quality attribute this moves is **modifiability** — specifically, the cost of
adding or changing one endpoint without reading the others. What it spends is
**simplicity at small scale** (more indirection than a route file needs when
there are five routes) and a little **build/dependency weight**. It is a good
trade when endpoint count is climbing and multiple authors are working in
parallel, and a bad one for a stable, small surface.

Two things it does **not** buy, and should never be sold as buying. It changes no
consistency property: the transaction boundary lives in the command the handler
calls, and a slice that opens a transaction has already stopped being thin. And
it makes no claim about **deployment granularity** — see below.

## Failure modes

- **The registration helper accretes behavior until it *is* an undeclared
  command bus.** This is the characteristic failure and it arrives one reasonable
  commit at a time: an `auth: true` flag on the endpoint definition, then a
  `transactional: true`, then an array of `middleware`, then a lookup keyed by a
  declared operation name. Each step is small and each is locally justified. The
  end state is a dispatch framework with a pipeline, invented in-house, with no
  documentation and no maintainer, that nobody ever decided to adopt — and the
  team is now paying the bus's indirection cost while telling itself it has plain
  handlers. The tell is when explaining "how does a request reach the business
  logic" takes more than two sentences, or when a new endpoint's behavior depends
  on configuration in the helper rather than on code in the slice. Set the rule
  at authoring time — the helper takes no behavioral flags, and cross-cutting
  concerns are wrappers named at the registration site — and treat a proposed
  flag as an ADR, not a refactor. If the pipeline is genuinely wanted, adopt a
  real, maintained bus and get its ecosystem, rather than growing a worse one.
- **Handlers grow business logic because "it's just one line more."** A second
  command call to keep the client from making two round trips. A conditional
  because one tenant behaves differently. A retry. None of them are refactored
  back out, and within a year the business rule for a workflow lives in the HTTP
  layer, is untested except through the transport, and is invisible to any other
  entry point — so the same rule is reimplemented, differently, in the batch job
  or the second client. The observable symptom is a handler that mentions a
  domain concept the application layer has no function for. The check that
  actually holds this line is not a lint rule but a review question with a
  number in it: how many application calls does this handler make, and is the
  answer still one?
- **A slice is written but never registered.** The directory exists, the unit
  test passes because it calls the handler function directly, review sees a
  complete-looking endpoint, and the route 404s in production. This is the 3am
  version of the pattern's failure: the very indirection that makes slices
  testable also decouples "the endpoint exists" from "the endpoint is reachable".
  Cover it with a registration assertion — every slice module in the tree is
  present in the registered route table — or at minimum one smoke test per route
  that goes through the real router.
- **The uniform error mapper flattens distinctions that mattered.** Everything
  unrecognized becomes a 500 with a generic envelope, so a domain conflict that
  should have been a 409 and a genuine bug look identical from the outside.
  Clients then retry an operation that will never succeed, and the on-call
  signal — the thing that would have told you which of the two it was — was
  discarded at the boundary. Make the mapper's default case loud in logs, and
  require each command's known failure modes to be mapped explicitly rather than
  falling through.
- **A cross-cutting wrapper is forgotten on exactly one slice.** Because gating
  is explicit per registration rather than pipeline-wide, omission is silent —
  the endpoint works, it just works for everyone. This is the direct cost of
  refusing the pipeline, and it must be paid deliberately: assert at
  registration that every endpoint declaring itself gated is wrapped, or that
  the ungated set is a short, reviewed, explicit list.
- **Slice names drift into the framework's or the table's vocabulary.** Directories
  named for HTTP verbs and table names (`post-rows`, `patch-record`) instead of
  the capability the endpoint provides. The tree becomes a second rendering of
  the schema rather than a map of what the system does, and the "one obvious
  home" property quietly stops being obvious.
- **The shared contracts package becomes a coupling channel.** It starts as
  request and response shapes; someone adds a validation helper, then a domain
  enum, then a small piece of logic "both sides need". Clients and server are
  now coupled through a package that is nobody's layer, and a wire-contract
  change becomes a lockstep release. Keep it shapes only, and treat any behavior
  landing there as a defect in the package's charter.

## Alternatives considered

- **Inline handlers in one routes file** — wins while the whole surface fits in
  one screenful of reading, for prototypes, and for internal tools whose
  endpoints will never grow contracts. Loses the moment two people add endpoints
  in the same week, or the moment error shapes start differing between routes.
- **MVC-style controllers grouping actions by resource** — wins when the
  framework's idiom *is* controllers (fighting it costs more than it saves) and
  when actions on a resource genuinely share setup. Loses because it groups by
  the resource noun rather than by the thing that actually varies, which is the
  individual request/response contract; the observable decay is shared controller
  state and a fat base class that every action inherits and none needs.
- **A mediator or command bus at the HTTP layer** — wins with many handlers and
  genuinely rich, uniform cross-cutting concerns (validation, authorization,
  transactions, logging) that would otherwise be repeated at every registration
  site, and where the ecosystem has a mature, maintained bus. Loses when handler
  count is modest: the registration ceremony and the dispatch indirection are
  paid immediately and the pipeline payoff is not. The decisive question is not
  "how many endpoints" but "how many cross-cutting concerns apply uniformly" —
  one or two are wrappers, six are a pipeline.
- **Hand-rolled request parsers instead of a schema library** — wins for the rare
  non-JSON or streaming edge where a schema library has nothing to offer. Loses
  as the default: every endpoint hand-maintains a type and a validator and keeps
  them in sync by discipline, and error shapes drift because there is no shared
  parse step to make uniform.
- **A heavier endpoint framework** — decorators, DI container, generated
  OpenAPI, auto-discovery. Wins when the API is a product surface with external
  consumers who need a published, always-accurate specification, or when the
  endpoint count is large enough that the framework's conventions are cheaper
  than the ones you would otherwise write down. Loses early: it is a large,
  hard-to-reverse dependency bought against a benefit that scales with endpoint
  count. The reversible path is to start with the dozen-line helper and adopt
  the framework when the specification requirement is real.
- **Contract-first code generation from an OpenAPI document** — wins when the
  contract is negotiated with external parties before implementation, or when
  multiple languages must stay in sync. Complementary rather than competing:
  generate the request/response types, keep the slice as the home for the
  handler and the wiring.

**A boundary claim is not a granularity claim.** Everything on this page is about
how source code inside *one deployable* is organized. It says nothing about how
many services there should be, where the process boundaries fall, or what should
be extracted. Slices are cheap and reversible; a service boundary is a
distributed-systems commitment with latency, partial failure, and independent
deployment attached. The two decisions share a vocabulary and nothing else, and
conflating them — "we have vertical slices, so each slice could be a service" —
is how a clean code layout becomes an unplanned distributed system. Decide
granularity on its own grounds.
