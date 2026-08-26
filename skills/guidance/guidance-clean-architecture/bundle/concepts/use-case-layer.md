---
type: Guidance
title: The use-case layer — first-class operations, sliced by feature
description: Make each state-changing business operation a first-class, named use case that owns its transaction boundary and speaks the domain's vocabulary, organize use cases as feature slices inside the clean boundary rather than as a horizontal service layer, let simple slices be transaction scripts, and refuse to write the use case that would only proxy a repository call.
tags: [architecture, clean-architecture, use-cases, application-layer, vertical-slices, screaming-architecture, transaction-script]
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
  - id: bogard-vertical-slices
    resource: https://www.jimmybogard.com/vertical-slice-architecture/
    title: Jimmy Bogard — Vertical Slice Architecture
  - id: fowler-pdd-layering
    resource: https://martinfowler.com/bliki/PresentationDomainDataLayering.html
    title: Martin Fowler — PresentationDomainDataLayering
  - id: jovanovic-vsa-vs-clean
    resource: https://milanjovanovic.tech/blog/vertical-slice-vs-clean-architecture
    title: Milan Jovanović — Vertical Slice vs Clean Architecture
  - id: shcherbyuk-use-cases
    resource: https://medium.com/@VolodymyrSch/the-complexities-of-clean-architecture-use-cases-71ac89ea8b40
    title: Volodymyr Shcherbyuk — The Complexities of Clean Architecture Use Cases
---

# The use-case layer — first-class operations, sliced by feature

## Technique

Every state-changing business operation is a **use case**: one named,
callable unit (`placeOrder`, `suspendTenant`, `approveInvoice`) that takes a
plain input, enforces the operation's rules via the domain model, owns the
transaction boundary (one use case, one transaction, one aggregate —
`guidance-ddd/concepts/aggregate-boundaries.md`), and returns a plain output.
It is the thing a driving adapter calls and the thing a test drives. The
folder names come from the business, not the framework — a directory listing
that reads `billing/ invoicing/ provisioning/` is Martin's screaming
architecture, and it is also what lets Cockburn's "driven equally by users,
programs, or tests" claim hold, because every driver calls the same named
operation.

Inside the clean boundary, organize by **feature slice**, not by horizontal
layer: `invoicing/approve-invoice/` holds the use case, its input/output
types, and the ports only it consumes — the by-feature taxonomy and its
import rules are `guidance-vertical-slices/concepts/feature-folder-organization.md`,
applied inside the core. Coupling is minimized between slices and maximized
within one; shared domain objects are extracted to the domain model when
duplication starts to hurt, not preemptively. This is also where the two
supposedly rival schools converge — Fowler's "domain-oriented modules,
internally layered" and Jovanović's "vertical slices inside a clean
solution structure" are the same landing point.

Two escape hatches keep the layer honest. **Per-slice rigor:** a slice with
real invariants gets a rich domain model; a simple slice is allowed to be a
transaction script — a use case that just does its steps in order — and is
refactored toward patterns only when smells emerge (Bogard's rule). And the
**pass-through refusal:** if the use case would be one line that forwards to
a repository, do not write it. A read path belongs to the thin query model
(`guidance-cqrs-projections/concepts/cqrs-lite.md`) wired directly to its
endpoint (`guidance-vertical-slices/concepts/repr-endpoints.md`); a
state-changing one-liner means either the operation has no rules yet (call
the repository from the endpoint's handler until it does) or the rules are
hiding somewhere they shouldn't be.

## Applies when

- Operations carry rules beyond storage: validation against current state,
  invariants spanning fields or entities, side effects that must happen
  atomically with the write (`guidance-event-delivery/concepts/transactional-outbox.md`
  for the atomic side-effect mechanics).
- The same operation is invoked from more than one driver — HTTP now, a
  queue consumer or scheduled job later — and must behave identically from
  each.
- Per-operation cross-cutting concerns exist: authorization decisions,
  audit records, or idempotency keyed to the business operation rather than
  the transport.
- The codebase is large enough, or agent-written enough, that "where does
  this rule go" needs a mechanical answer: it goes in the use case named
  after the operation.

## Doesn't apply when

- The endpoint is select-and-serialize. Reads get no use case — the tempting
  mistake is symmetry ("every endpoint calls a use case"), which is exactly
  the generator of the 500-one-liner pathology the critique literature
  documents.
- The whole application is forms-over-data with no invariants: a use-case
  layer over nothing is a service layer over nothing, and the framework-native
  handler is the honest implementation until rules arrive.
- The operation's rules live entirely inside one aggregate method and there
  is truly one driver: a REPR endpoint handler calling the domain object
  directly is a legitimate partial form — the use case earns its file when a
  second driver or a cross-cutting concern shows up.

## Trade-offs

**Buys:** a stable, transport-free surface for tests and new drivers; a
codebase that names its operations after the business, which is what makes
both screaming architecture and per-operation authorization/audit tractable;
per-slice freedom to be as rigorous or as plain as the slice's rules warrant;
and localized change — a new feature adds a slice rather than fattening a
shared service.

**Costs:** one more hop on every write path, and a real risk of ceremony
where conditions don't hold — use-case proliferation is the most-reported
failure of Clean Architecture in practice; some cross-slice duplication is
accepted deliberately (the price of slice independence), and someone must
watch for the moment duplicated rules should be extracted into the domain
model; the "which slice owns this" judgment call Bogard flags as requiring
team maturity.

## Failure modes

- **Use-case proliferation.** Hundreds of one-line classes proxying the data
  layer, with mappers converting identical shapes back and forth. Symptom: a
  new CRUD screen adds five files and zero rules; developers describe the
  layer as paperwork. Cause is always the same conditions failure: use cases
  written for reads or rule-less writes.
- **The god application service.** The opposite pole: `InvoiceService` with
  forty methods, shared state, and every slice's rules. The use-case layer
  exists in name but the coupling is maximal between features. Symptom:
  every feature PR touches the same file; merge conflicts as a way of life.
- **Use cases calling use cases.** A web of internal invocations where the
  transaction boundary blurs — does `approveInvoice` calling `notifyBilling`
  join its transaction or start one? Extract the shared rule into the domain
  model, or publish an event (`guidance-event-delivery`) and let the second
  operation be its own use case with its own transaction.
- **Anemic slices over an anemic domain.** All rules written imperatively in
  use cases, entities reduced to property bags. Works — it is transaction
  script — until the same invariant appears in four slices and drifts in
  two. Symptom: bug reports of the form "you can still do X via path Y after
  we blocked it on path Z."

## Alternatives considered

- **REPR endpoint straight to domain** — the endpoint handler validates,
  loads the aggregate, calls its method, saves
  (`guidance-vertical-slices/concepts/repr-endpoints.md`). Wins for
  single-driver operations with aggregate-local rules; it is this page's
  partial form, not its rival.
- **Transaction script throughout** — no domain model at all, each operation
  a procedure. Wins when rules are simple, independent, and unlikely to be
  shared; the failure to watch for is silent rule duplication across
  scripts.
- **Horizontal service layer** — `OrderService`, `CustomerService`, one per
  entity. The traditional shape this page rejects: it couples unrelated
  features through shared classes and names the code after nouns instead of
  operations. Wins mainly when a team's tooling and habits are built around
  it and the entity count is small.
- **Command bus / mediator** — use cases as message handlers behind a
  dispatcher. Adds discoverable cross-cutting middleware at the cost of
  indirection in every trace; `guidance-vertical-slices/concepts/repr-endpoints.md`
  deliberately rejects the bus for the registration-helper shape — follow
  that reasoning unless the middleware need is proven.
