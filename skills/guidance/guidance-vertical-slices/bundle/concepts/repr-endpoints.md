---
type: Guidance
title: Structuring an HTTP boundary as one slice per endpoint
description: Give every route its own file — one route per slice, named for the application command or query it calls, grouped in a resource folder that is navigational only — holding a request schema validated at the boundary, a thin handler that invokes exactly one command or query, and a response DTO; wired by a registration helper that is deliberately a convenience and not a command bus, with dependencies injected at registration, authority declared at each slice's own registration site, and a composition file that registers endpoints and contains no inline handler.
tags: [architecture, api, http, repr, vertical-slice, endpoints, boundary]
created: 2026-08-26
generated: { by: write-guidance/claude-opus-5, at: 2026-09-01T00:00:00Z }
status: stable
stale_after: 2028-03-01
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
  - id: ford-parsons-kua-evolutionary
    resource: https://evolutionaryarchitecture.com/
    title: Ford, Parsons, Kua — Building Evolutionary Architectures
---

# Structuring an HTTP boundary as one slice per endpoint

## Technique

Every route in the HTTP layer becomes a **self-contained slice** holding three
things and nothing else.

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
with an inline handler body**.

### The physical unit is a file, not a directory

**One route, one file.** A slice lives at `endpoints/<resource>/<slice>.<ext>`
and contains exactly one endpoint definition. The resource folder groups routes
so a reader can find them and does nothing else.

The natural first phrasing of this pattern is "a directory per endpoint," and
it is a trap — one this page sets for itself. The recommendation below is to
factor the request and response *shapes* into a package shared with clients.
Do that, and an endpoint directory holds exactly one file. An implementer facing
fifteen single-file directories will collapse them, correctly, and will collapse
them to whatever grouping is available, which is the resource — and a file
holding every route for a resource is a controller. The pattern's own advice
about contract sharing, plus a directory-shaped unit, produces the exact shape
the pattern exists to reject. Specify the unit as a file and the trap does not
close.

The file becomes a directory later, if a slice grows a genuinely private
collaborator — a fixture, a mapper nothing else calls. That promotion is local,
costs one rename, and should not be paid for in advance by every slice that will
never need it.

**Name the slice for the application function it calls.** The filename is the
command or query the handler invokes, in the tree's naming case:
`start-walk`, `capture-photo`, `list-members`. One vocabulary then runs from the
wire to the domain — a reader who knows the command name knows the filename, and
renaming a command renames its slice. The two tempting alternatives both lose by
inventing a second vocabulary: resource-noun-first names (`walk-create`) are
redundant once the folder groups the resource, and they can be *actively wrong*
when the invented verb phrase asserts something the domain does not mean;
HTTP-intent names (`post-walks`) read well from an access log and break the
moment a route is versioned or re-pathed.

Trivial routes (`/`, health) are slices too, and so are **mount or passthrough
registrations** — a third-party library's catch-all, a static asset mount, a
proxy — expressed as a plain `register(app, deps)` in the same tree. Both kinds
register from the same place, so the no-inline-handlers invariant holds
uniformly and needs no exemption list. An exemption list is a maintenance
surface and a place for real endpoints to hide. Slices with no application call
keep descriptive names; that is the one case the naming rule does not cover.

### The registration helper is explicitly not a command bus

This is the line that keeps the pattern cheap, and it is the one that erodes.
The helper resolves a slice's route, applies the shared parse and error-mapping
wrapper, and passes the injected dependencies. It has no dispatch registry keyed
by message type, no middleware pipeline that handlers opt into by declaring an
attribute or implementing a marker interface, and no indirection between "this
URL" and "this function". A reader following a request from the route table to
the business logic passes through exactly one hop of framework machinery.

**Dependencies are injected at registration**, never reached as module
singletons: the connection pool, the auth provider, the storage adapter arrive
as a `deps` argument that `registerEndpoints` threads through. That is what
makes a slice unit-testable with fakes and no running process, and it is most of
the practical payoff.

**Cross-cutting concerns stay explicit wrappers named at each slice's own
registration site** — session resolution, tenant scoping, capability checks —
rather than a shared pre-composed chain the slices import. Hoisting them into a
shared `writeMiddleware` const is the obvious cleanup and it is the wrong trade
for anything security-relevant: a change to that const lands in a diff showing
one line and *not* which routes it altered. Two duplicated lines that make an
authorization change visible are worth more than the indirection that conceals
it. The duplication is deliberate, has a real cost — omission on one slice is
silent, see **Failure modes** — and must be recorded as deliberate or the next
author will tidy it away. The general form of this rule, its counter-case, and
its eventual successor are in
[sharing code between peer slices](shared-code-between-peers.md).

**Registration is data, not a function.** Each resource folder exports an
*array* of registrations; the composition root concatenates the arrays and walks
them. Never a composite `registerResource()` that calls its siblings — that is
the controller wearing a function signature, and it is precisely where a fourth
route gets defined inline instead of beside its peers. An aggregation module
that contains no endpoint definition is structurally incapable of becoming one.

### Where genuinely shared code goes

Sibling slices really will need the same error translation. Put it in a module
scoped to the resource that shares it, holding **exported functions only** — no
module state, no factories, no constants whose value is composed behavior —
because a function-only module has no gravity and nothing a new sibling would
want to sit beside. This is the force that regrows controllers inside a sliced
tree, and it is covered in full, at both layers, in
[sharing code between peer slices](shared-code-between-peers.md).

### The checks

Four, and the fourth is the one usually written alone.

1. **One endpoint definition per slice file.** Tripping it means a second route
   joined a slice, which is the first increment of the controller shape. Mount
   slices that register without the helper go on an explicit allowlist *inside
   the check*, not a pattern exemption, so adding one is a visible decision.
2. **Every slice is registered** — every exported registration symbol in the
   tree is reachable from the composition root's list, resolved transitively
   through the per-resource arrays. Catches the slice that was written and never
   wired, and catches an array registering siblings behind the root's back.
3. **No cross-slice imports.** A slice may import the helper, its own resource's
   shared functions, the middleware modules, the shared contracts, the
   application layer, and third-party code — not a sibling slice. Aggregation
   modules are exempt in one direction only: they may import their own siblings
   and nothing else. This is the transport-layer form of the rule a dependency
   analyzer already enforces for [feature folders](feature-folder-organization.md).
4. **No inline route handlers in the composition file.**

Write all four when the pattern is adopted, not just the fourth. **A check
placed where the last failure occurred watches the wrong place for the next
one.** Once slices exist, the composition file is the one location erosion stops
happening — the inline handler is gone and nobody puts it back — while the tree
the check does not read is where a controller can grow for months without
tripping anything. Naming these checks, choosing their CI lane, and tracking
whether they still run is the practice in
`guidance-fitness-functions/concepts/architectural-fitness-functions.md`; this
page only supplies the checks worth naming.

### Contracts shared with clients

Where the wire contract is shared with clients you also own, the request schema
and response DTO **shapes** belong in a package both sides import, while the
slice owns the **binding** — validating with the shared schema, shaping the
shared DTO. That keeps one source of truth for the contract without making the
slice a place clients reach into. Note that this is the choice that makes the
per-endpoint directory degenerate, above; the two decisions have to be made
together.

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
  the handler, adopting REPR just relocates a fat handler into a nicer file —
  establish the command/query seam first, then slice the boundary over it. The
  naming rule is a second reason: a slice named for the command it calls needs
  the command to exist.
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
  dependencies plus a plain handler function is the seam that changes that. Note
  that individually-exported registrations are what make this possible — the
  composite registration function this page bans is also the thing that forces
  every endpoint test to boot the whole resource.

## Doesn't apply when

- **The API is a handful of endpoints and a single routes file is still fully
  legible.** Below roughly a dozen routes, one file that can be read top to
  bottom beats a tree that must be navigated. The cost is paid per endpoint from
  day one; the benefit only arrives with volume. Adopt when the file stops being
  readable, and use the existing routes as the reference refactor rather than
  pre-building structure for endpoints that do not exist.
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
  a file per resolver with two-thirds of the structure empty.
- **The endpoints are genuinely uniform CRUD over a table, generated or nearly
  so.** Where a resource layer or generated router already emits the standard
  five operations correctly, hand-writing five slices per resource is transcription.
  Slice the endpoints that have real contracts; let the generated ones stay
  generated.
- **The team is one or two people who will not enforce the invariants.** The
  pattern's value is that the shape is predictable. Without the checks, the first
  deadline reintroduces an inline handler or a second route in an existing file,
  and the tree becomes "mostly slices, plus the ones that aren't" — which is
  worse than either pure option, because a reader can no longer trust where
  anything lives.

## Trade-offs

**Buys:** one obvious home per endpoint, so the question "where does this route's
validation live?" has a mechanical answer. A whole route's contract — path,
method, authority, schema, error mapping, handler — on one screen, diffing
cleanly. Uniform request parsing and a single error-mapping path, so wire error
shapes stop drifting per route. Endpoint slices unit-testable with injected
fakes and no process boot. A composition file that reads as a composition root
rather than as the application. A copyable exemplar, which is the actual
mechanism by which a convention propagates to contributors and agents who never
read the decision. Mechanical navigation from wire to domain, because the
filename is the function name. And a merge-conflict surface that shrinks to near
zero, because two features adding two endpoints touch two disjoint files.

**Costs:** file count grows linearly with routes, and a resource that had one
file now has seven. A helper you now own and must keep lean; it is a piece of
infrastructure with no external maintainer. A validation library becomes a
load-bearing dependency at the transport edge. Four CI gates to build, keep green,
and keep from false-positiving. A per-resource registration array to keep in
sync when a slice is added — guarded by check 2, but still a thing to remember.
Duplicated cross-cutting declarations at every gated slice, accepted
deliberately and paid for in the failure mode below. A one-time refactor of the
existing routes, which is pure churn in the diff and must be sequenced away from
in-flight feature work. And genuine cross-endpoint duplication: two endpoints
returning near-identical DTOs will each shape their own, and the pattern's
discipline says to leave it that way until the duplication is proven rather than
to hoist a shared mapper that re-couples the slices.

The quality attribute this moves is **modifiability** — specifically, the cost of
adding or changing one endpoint without reading the others — and, secondarily,
**analyzability**: an authorization change shows you every route it touches. What
it spends is **simplicity at small scale** (more indirection than a route file
needs when there are five routes), a little **build/dependency weight**, and the
**uniformity** a central pipeline would have guaranteed. It is a good trade when
endpoint count is climbing and multiple authors are working in parallel, and a
bad one for a stable, small surface.

Two things it does **not** buy, and should never be sold as buying. It changes no
consistency property: the transaction boundary lives in the command the handler
calls, and a slice that opens a transaction has already stopped being thin. And
it makes no claim about **deployment granularity** — see below.

## Failure modes

- **The controller reassembles inside the slice tree.** This is the
  characteristic failure and it is worth stating precisely, because every step is
  locally reasonable. Two routes on one resource get put in one file, because two
  is not many. An error mapper both need goes in the same file, because that is
  where its callers are. A middleware constant joins it, for the same reason. A
  composite `registerResource()` appears to wire the growing set. Six months on
  the file is two hundred lines holding seven routes, shared state, and a
  dispatch function — a resource controller, reached by increments, sitting
  inside the directory the pattern created to prevent it. Nothing fails, because
  the only check watches the composition file. The three structural rules on this
  page — one route per file, function-only shared modules, registration as data —
  each close one increment, and checks 1–3 are what make them facts rather than
  preferences.
- **The registration helper accretes behavior until it *is* an undeclared
  command bus.** The same erosion in the other direction, one reasonable commit
  at a time: an `auth: true` flag on the endpoint definition, then a
  `transactional: true`, then an array of `middleware`, then a lookup keyed by a
  declared operation name. The end state is a dispatch framework with a pipeline,
  invented in-house, with no documentation and no maintainer, that nobody ever
  decided to adopt — and the team is now paying the bus's indirection cost while
  telling itself it has plain handlers. The tell is when explaining "how does a
  request reach the business logic" takes more than two sentences, or when a new
  endpoint's behavior depends on configuration in the helper rather than on code
  in the slice. Set the rule at authoring time — the helper takes no behavioral
  flags — and treat a proposed flag as a decision record, not a refactor. If the
  pipeline is genuinely wanted, adopt a real, maintained bus and get its
  ecosystem, rather than growing a worse one.
- **A cross-cutting wrapper is omitted on exactly one slice.** The direct,
  deliberate cost of declaring authority per registration site. The endpoint
  ships without its capability check; the build is green; the tests pass, because
  they exercise the handler the author was thinking about; the endpoint works —
  it just works for everyone. First evidence is a customer seeing another
  customer's data. Per-site declaration buys visibility on *change* and buys
  nothing on *absence*, so absence must be paid for separately: assert over the
  **set** — every slice either declares a gate or appears on a short, reviewed,
  in-repo list of the deliberately ungated — and read that list at every
  milestone rather than appending to it.
- **Handlers grow business logic because "it's just one line more."** A second
  command call to keep the client from making two round trips. A conditional
  because one tenant behaves differently. A retry. None are refactored back out,
  and within a year the business rule for a workflow lives in the HTTP layer, is
  untested except through the transport, and is invisible to any other entry
  point — so the same rule is reimplemented, differently, in the batch job or the
  second client. The observable symptom is a handler that mentions a domain
  concept the application layer has no function for. The check that holds this
  line is not a lint rule but a review question with a number in it: how many
  application calls does this handler make, and is the answer still one?
- **A slice is written but never registered.** The file exists, the unit test
  passes because it calls the handler directly, review sees a complete-looking
  endpoint, and the route 404s in production. The very indirection that makes
  slices testable also decouples "the endpoint exists" from "the endpoint is
  reachable" — and adding a per-resource registration array adds a second place
  the wiring can be dropped. This is what check 2 is for, and it has to resolve
  *transitively* through the arrays or it verifies the wrong hop.
- **The uniform error mapper flattens distinctions that mattered.** Everything
  unrecognized becomes a 500 with a generic envelope, so a domain conflict that
  should have been a 409 and a genuine bug look identical from the outside.
  Clients then retry an operation that will never succeed, and the on-call
  signal — the thing that would have told you which of the two it was — was
  discarded at the boundary. Make the mapper's default case loud in logs, and
  require each command's known failure modes to be mapped explicitly rather than
  falling through.
- **The error mapper reads persistence errors at the transport boundary.** A
  related and more insidious version: rather than the application layer throwing
  a typed domain error, the slice sniffs a database error code, or worse,
  string-matches a constraint message. It works, so it stays, and the transport
  layer is now coupled to the schema — a migration that renames a constraint
  changes an HTTP status code. Default to typed domain errors thrown by the
  layer that knows the rule; where a raw mapper must survive at the edge, record
  it as debt with a named destination layer, because no check on this page will
  detect it.
- **Slice names drift into the framework's or the table's vocabulary.** Files
  named for HTTP verbs and table names instead of the capability the endpoint
  provides. The tree becomes a second rendering of the schema rather than a map
  of what the system does, and the "one obvious home" property quietly stops
  being obvious. Naming the slice for the application function it calls is the
  rule that prevents this, and it only holds if renaming a command is understood
  to rename its slice.
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
- **A directory per endpoint** — wins when slices have private collaborators to
  colocate: a fixture, a mapper used by nothing else, a large response projection.
  Loses when the request and response shapes have been factored into a shared
  contracts package, which is this page's own recommendation — the directory then
  holds one file, and a tree of single-file directories gets collapsed to
  something worse. Reversible in the cheap direction: start with files and
  promote the one slice that grows a collaborator.
- **A flat file per endpoint with no resource folders** — wins at genuinely small
  route counts, and it is the simplest thing that satisfies one-route-per-file.
  Loses steadily as the API grows: the at-a-glance resource map disappears and
  the directory becomes a long alphabetical list. The folder costs nothing so
  long as it is constrained to navigation, so this is mostly a question of when,
  not whether.
- **MVC-style controllers grouping actions by resource** — wins when the
  framework's idiom *is* controllers (fighting it costs more than it saves) and
  when actions on a resource genuinely share setup. Loses because it groups by
  the resource noun rather than by the thing that actually varies, which is the
  individual request/response contract; the observable decay is shared controller
  state and a fat base class that every action inherits and none needs. Worth
  noting that this is not only an alternative but the *attractor* — a sliced tree
  left unchecked arrives here on its own.
- **Mirroring an application layer's command/query split into the endpoint tree**
  — wins where reads and writes have genuinely divergent transport treatment
  (different auth, different caching, different response envelopes) and the split
  carries information. Loses at ordinary scale, because the HTTP method already
  encodes read-versus-write at this boundary; the extra path segment is pure
  depth and one more thing to get wrong.
- **A mediator or command bus at the HTTP layer** — wins with many handlers and
  genuinely rich, uniform cross-cutting concerns (validation, authorization,
  transactions, logging) that would otherwise be repeated at every registration
  site, and where the ecosystem has a mature, maintained bus. Loses when handler
  count is modest: the registration ceremony and the dispatch indirection are
  paid immediately and the pipeline payoff is not. The decisive question is not
  "how many endpoints" but "how many cross-cutting concerns apply uniformly" —
  one or two are wrappers, six are a pipeline.
- **Declarative authority fields on the slice's definition** (`capability: "X"`,
  with the helper composing the chain) — the real successor rather than a rival.
  It removes the duplicated wrapper lines, keeps authority visible on each slice,
  and makes the whole set auditable by grepping one field, which is worth a great
  deal for a security-relevant concern. Loses at first adoption for one reason:
  it pushes the helper from a registration convenience toward the framework this
  pattern is protecting against. Additive and therefore cheap to defer — adopt it
  when route count makes duplicated declarations more likely to drift than a
  central change is to hide.
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
