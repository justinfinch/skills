---
type: Guidance
title: Four kinds of client state, four stores — never one store for everything
description: Split client state by what it is rather than by what is convenient — a server cache owned by a query library that fetches, expires and invalidates; ephemeral UI state in a light store or component state; durable pending writes in a purpose-built persistent queue that is deliberately not the query library's mutation cache; and real-time push events patching that query cache directly, which is where an eventually-consistent backend's optimistic read-your-writes echo lives on the client.
tags: [client-state, react, typescript, tanstack-query, zustand, redux, server-state, cache-invalidation, sse, websocket, offline-queue, read-your-writes]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:56:31Z }
status: stable
stale_after: 2027-09-01
sources:
  - id: tanstack-query
    resource: https://tanstack.com/query/latest/docs/framework/react/overview
    title: TanStack Query — asynchronous server-state management for React
  - id: tanstack-query-caching
    resource: https://tanstack.com/query/latest/docs/framework/react/guides/caching
    title: TanStack Query — caching, staleness and invalidation model
  - id: tkdodo-query-as-state-manager
    resource: https://tkdodo.eu/blog/react-query-as-a-state-manager
    title: Dorfmeister — React Query as a State Manager
  - id: tkdodo-practical-react-query
    resource: https://tkdodo.eu/blog/practical-react-query
    title: Dorfmeister — Practical React Query (query keys, staleTime, the server-state boundary)
  - id: redux-style-guide
    resource: https://redux.js.org/style-guide/
    title: Redux Style Guide — official priorities for what belongs in the store
  - id: redux-faq-organizing-state
    resource: https://redux.js.org/faq/organizing-state
    title: Redux FAQ — Organizing State (what should and should not go in Redux)
  - id: rtk-query
    resource: https://redux-toolkit.js.org/rtk-query/overview
    title: RTK Query — server-cache layer inside a Redux store
  - id: zustand
    resource: https://zustand.docs.pmnd.rs/
    title: Zustand — minimal client-state store
  - id: dodds-state-management
    resource: https://kentcdodds.com/blog/application-state-management-with-react
    title: Dodds — Application State Management with React (colocation and state kinds)
  - id: mdn-server-sent-events
    resource: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
    title: MDN — Using server-sent events
  - id: apollo-normalized-cache
    resource: https://www.apollographql.com/docs/react/caching/overview
    title: Apollo Client — normalized cache (the alternative cache shape)
  - id: kleppmann-local-first
    resource: https://www.inkandswitch.com/local-first/
    title: Kleppmann et al. — Local-first software (the sync-engine counter-case)
---

# Four kinds of client state, four stores — never one store for everything

## Technique

Sort every piece of state in the client by **what it is**, not by what is
convenient to reach from a component, and give each kind its own store with its
own lifetime and its own owner. There are four kinds, and the whole technique is
refusing to merge them.

**1 — Server state: a query library owns it.** Anything whose source of truth is
the remote API is held in a query cache (TanStack Query in this stack) keyed by
the request that produced it. The library — not application code — owns
fetching, deduplication, staleness, background refetch, retry, and invalidation
after a mutation. Application code declares *what data a screen needs* and *what
a write invalidates*. The cache is a **disposable client-side replica**: never
the source of truth, always re-fetchable, and safe to throw away at any moment.
That disposability is the property everything else in this page leans on.

**2 — Ephemeral UI state: component state, or a light store when it must be
shared.** Open dialogs, active filters, wizard step, selection, unsaved form
input. Start in `useState` colocated with the component that owns it; promote to
a light store (Zustand in this stack) only when genuinely distant components
must agree. This state is disposable by construction — it dies with the screen
and nobody mourns it — and it should hold **identifiers and view intent, not
copies of server objects**. Store `selectedInvoiceId`, never `selectedInvoice`.

**3 — Durable pending writes: a purpose-built persistent queue.** Writes made
where the network may not be there, whose loss is unacceptable, are written to
device-durable storage *first* — SQLite or an equivalent on native, IndexedDB on
web — each carrying a client-generated idempotency key from the moment of
creation, and drained by a background worker. This store is the one piece of
client state that is **not disposable**, and that difference is why it is a
separate store rather than a mode of the query cache. Specifically it is *not*
the query library's persisted-mutation cache: that machinery is an in-memory
mutation model with persistence bolted behind it, tuned for resuming a
convenience retry, and it is not a durability guarantee that survives process
kill, low battery, and an OS reclaiming the app mid-upload. See
`guidance-client-state/concepts/store-and-forward-capture.md` for when this
fourth store is worth building at all — for most applications it is not, and
this taxonomy then has three members.

**4 — Real-time push: events patch the query cache.** One subscription
(SSE or WebSocket), owned in one place, receives server events and **patches or
invalidates entries in the query cache** — it does not maintain a parallel store
of its own. Push and fetch converge on the same cache because they carry the
same data; the only question is which one wrote it last.

This fourth kind is where an eventually-consistent backend's read-your-writes
story lands on the client. When the server acknowledges a command before the
authoritative read model has caught up, the client writes an **optimistic
entry** into the query cache immediately, and reconciles it against the
authoritative event when that event arrives on the push channel, matched on a
stable client-generated key. `guidance-cqrs-projections/concepts/cqrs-lite.md`
owns the server half of that arrangement — the command/projection split that
makes the read lag exist, and the consistency guarantees it does and does not
provide. This page owns the client half: the echo is a cache entry, the
reconciliation is a cache patch, and both live in the query cache rather than in
a bespoke "pending" structure beside it.

Two ownership rules make the four stores hold:

- **One direction of copying.** Server state may be *read* by UI state through a
  selector or an id lookup; it is never *copied into* it. A component that needs
  both reads from both.
- **One writer per cache key.** For every query key, exactly one rule says
  whether push patches it, or a refetch owns it. Not both, not per-feature
  improvisation.

The taxonomy is a claim about **kinds, not instances**, and the two are
frequently confused. "Four kinds of state" does not mean four objects: the
server cache is conventionally one cache with many keys, and ephemeral UI state
is usually *many* small stores or slices — one per feature, colocated with it —
rather than one application-wide store, because merging them recreates the
global-store problem inside kind 2. How many instances each kind has is a
separate, local decision driven by how state is shared between components. What
the taxonomy fixes is that no instance may span two kinds.

**What transfers to other ecosystems, and what to re-derive.** The four-way
taxonomy transfers whole: it is a statement about lifetimes and sources of
truth, and it holds in Vue, Svelte, SwiftUI, Flutter, Android, or a server-driven
UI. So does the ownership pair above, and so does the claim that durable pending
writes are a separate store from the disposable cache. What is stack-bound and
must be re-derived locally is the *library assignment* — TanStack Query, Zustand,
and this ecosystem's persisted-mutation machinery are the current best fits in
React/TypeScript, not the technique. Other ecosystems answer the same four
questions with different components (SWR or a framework loader; Pinia or a view
model; Room or Core Data behind the queue; a first-party observable store), and
some collapse two kinds into one framework primitive, which is fine as long as
the collapse is a decision rather than an accident.

## Applies when

- **You are building a React/TypeScript application against a remote HTTP
  API.** This is the stack condition and it is stated first because the
  recommendations below name libraries. An agent in another ecosystem should
  keep the four kinds and the two ownership rules, and re-derive the components.
- **The same remote data is read by more than one component, or on more than one
  screen.** This is the checkable test for "do I have a cache problem": if two
  places need the same resource, something must decide whether the second read
  refetches, and a query library is the answer to that question. One component
  reading one resource once is not this situation.
- **Writes invalidate reads.** After a mutation, at least one list or detail view
  elsewhere in the app is now wrong. If nothing is ever stale after a write, most
  of what a query library buys is unused.
- **The API is genuinely remote and can be slow, flaky, or unavailable** — as
  opposed to a local process or an in-memory fixture. Retry, deduplication, and
  background refetch are the value, and they are only value against a network.
- **You can name the data whose source of truth is the server, and the data
  whose source of truth is the client.** If that sorting cannot be done for a
  given screen, the screen's data model is unclear and no store choice will fix
  it — sort first.
- **A real-time channel exists or is planned** (SSE, WebSocket, or push-triggered
  refetch), *and/or* the backend acknowledges writes before reads reflect them.
  Either condition alone makes kinds 1 and 4 interact, and the cache-key
  ownership rule becomes load-bearing rather than tidy.

## Doesn't apply when

- **Server state is trivially small and read-once.** A configuration blob
  fetched at startup, a single form posted to an endpoint, a marketing page with
  one list. A query library here is machinery installed against a cache problem
  the application does not have — it adds a dependency, a provider, a key
  convention, and a devtools panel to solve nothing. The honest test: if you can
  count the distinct remote resources on one hand and none of them is read from
  two places, `fetch` in a loader or an effect is the right size.
- **A local-first sync engine is already in use.** When a sync engine holds a
  local replica of the domain data and reconciles it with the server, **the sync
  engine *is* the taxonomy** — it is simultaneously the server cache, the
  durable write queue, and the real-time channel, and it derives the UI's data
  from one coherent local store with one consistency model. Layering a query
  cache on top of it produces two replicas of the same data with different
  staleness rules and no arbiter. Adopt one or the other. If a sync engine is
  in play, the only member of this taxonomy still worth keeping separate is
  ephemeral UI state, which the sync engine correctly does not want.
- **The framework already owns the server-cache role and you are not fighting
  it.** A server-rendered application where data is fetched on the server per
  navigation and mutations trigger a server-side revalidation has a cache — it
  is just not on the client. Adding a client query cache beside it means two
  caches disagreeing across a navigation. Either commit to the framework's model
  or move data ownership to the client deliberately; the failure is having half
  of each.
- **All state is genuinely ephemeral.** A drawing tool, a local editor, a game —
  the "server" is a save button. Kind 2 is the whole application, and imposing
  the taxonomy is ceremony.
- **The organization mandates a state library that already spans the kinds.**
  If Redux with RTK Query is the platform standard across a portfolio, the four
  kinds still apply as a *discipline* (see Alternatives), but replacing the
  store is a political project, not an architectural one. Apply the taxonomy
  inside the mandated tool.

## Trade-offs

**Buys** the elimination of the single largest category of client-side data
bugs: data that is wrong because nobody knew whose job it was to update it. When
server state has one owner, "why is this list stale after I edited the row" has
one answer and one place to fix. It buys a *disposable* cache — a client that
can be reloaded, hard-refreshed, or backgrounded for an hour and recover by
refetching, because nothing important was living in memory. It buys fetching,
deduplication, retry, and background refresh as configuration rather than as
hand-written effects, which is where the code-volume saving actually comes from.
And it buys an isolation guarantee at the point it matters most: the one store
holding unlosable writes is small, separately owned, and cannot be corrupted by
a cache eviction policy tuned for convenience.

**Costs**, first, more than one state library in the dependency graph — two
plus a bespoke queue in the full four-kind case — each with its own idioms,
devtools, and upgrade cadence, and a standing question at every code review
about which one a new piece of state belongs in. Second, a **query-key
convention** that is now architecture: keys must be structured consistently or
invalidation becomes guesswork, and this is unenforced by the type system in
most codebases. Third, a real learning curve: the query library's
staleness-versus-cache-time distinction is the single most misunderstood thing
in this stack, and a team that has not internalized it will ship either a
thundering herd of refetches or a UI that never updates. Fourth, the durable
queue in kind 3 is bespoke code you own and must test against process kill —
priced in full on the page that owns it. Fifth, the taxonomy is a *convention*
unless something checks it: nothing in the type system stops a developer from
putting a fetched object into the UI store.

The quality attributes moved are **correctness of displayed data** and
**modifiability** — a new screen's data needs are declarative, and the blast
radius of a write is expressed as a set of invalidated keys. What is paid is
**simplicity** and **onboarding time**: four stores is four mental models, and a
developer who has only ever seen one global store will experience this as
fragmentation before they experience it as clarity.

**The consistency model, stated.** The query cache is an *eventually consistent
replica* of server state. A rendered screen shows what the server said at some
point in the past, possibly patched by a push event, possibly holding an
optimistic entry the server has not confirmed. There is no read-your-writes
guarantee except the one the optimistic echo simulates, and no guarantee at all
that two components rendered in the same frame from two different query keys
reflect the same server instant. Any screen where that matters — a balance the
user is about to act on, a compliance readback — must fetch fresh and say so,
not read the cache.

**What would make this stale, and why the date is where it is.** This page's
reasoning is durable; its library assignments sit on the fastest-churning layer
in software, and the `stale_after` is set against the churn, not the reasoning.
Three specific futures would move it. First, **framework absorption**: if
server-side rendering with server-driven mutations and revalidation becomes the
default shape for new React applications, kind 1 moves out of the client for a
large class of apps and this page becomes advice for the remainder. Second,
**sync engines becoming boring**: several are converging on a local replica plus
server reconciliation as a general-purpose default. If one becomes the obvious
choice for ordinary CRUD applications, the "sync engine is in use"
counter-case above stops being an edge case and becomes the mainline — that is
the single change most likely to invert this page. Third, **library
consolidation or displacement**: the specific named libraries could merge,
be absorbed into a framework, or be displaced by a reactivity primitive that
makes ephemeral state a language-level concern. Note that the first two futures
attack the *taxonomy's applicability*, and only the third attacks the *library
choices* — a revision should say which one moved. The date allows roughly a
year, which is about the observed period over which the default answer to
"where does server state live in a React app" has historically shifted.

## Failure modes

- **Server data is copied into the UI store "for convenience", and goes
  permanently stale.** This is the failure the taxonomy exists to prevent, and
  it is the one that actually happens. A component needs the selected customer's
  name in a header, so the whole customer object gets put in the global store on
  selection. Now there are two copies: one the query library refetches and
  invalidates correctly, and one that was correct at 09:14 and will be correct
  at 09:14 forever. The user edits the customer, the detail pane updates, the
  header does not, and the bug report says "sometimes the name is wrong". It
  reproduces for nobody because reproduction requires the specific
  select-then-edit-then-look-elsewhere sequence. The fix is the copying rule —
  store the id, read the object — and the smell to watch for is any store field
  whose name matches an API response type.
- **Push patches and refetches fight over the same cache key.** A push event
  patches a list entry; a window-focus refetch replaces the whole list with a
  server response that predates the event; the user watches a row change and
  change back. Or the inverse: a patch lands after a refetch and reintroduces an
  item the server has deleted. Nothing errors. The symptom is "flickering" or
  "it fixes itself if I reload", which sends people to the rendering layer for
  days. The cause is that no rule says who owns the key. State the rule per key
  family — pushed keys are patch-owned and refetched only on reconnect, or
  push merely invalidates and refetch is the sole writer — and prefer the second
  when in doubt, because invalidate-and-refetch is strictly easier to reason
  about and costs only a request.
- **Push events carrying partial payloads poison the cache.** An event delivers
  a delta — a status change, a new count — and the handler merges it into a
  cached entity that was fully populated. Fields the event did not carry are
  overwritten with `undefined`, or the merged object no longer matches its type
  at runtime because the event's shape drifted from the query's response shape.
  Downstream components crash on a missing field, in a component nowhere near
  the subscription. Either events carry a complete replacement for the entry
  they patch, or the handler invalidates and lets a refetch produce a
  well-formed entity. Do not hand-merge deltas into typed cache entries.
- **The subscription drops and nothing resynchronizes.** This is the one that
  pages someone. A push connection is lost — a proxy idle timeout, a laptop
  lid, a mobile network handover — and reconnects, and the client now
  silently holds a cache built from a *prefix* of the event stream. Every screen
  renders confidently wrong data with no error state, and it persists until
  something else happens to invalidate the key. In an operational surface, that
  is a user acting on state the server abandoned minutes ago. The mitigation is
  mandatory and cheap: on every reconnect, invalidate everything the channel
  owns and refetch. Treat "the channel was down and I don't know what I missed"
  as the default assumption rather than the exception, and instrument the
  reconnect count — a client reconnecting every 60 seconds is producing a
  refetch storm nobody has noticed either.
- **Over-broad invalidation turns every write into a refetch storm.** The
  easy fix for the previous failures is to invalidate generously after each
  mutation. With a hierarchical key convention, one careless invalidation at a
  high prefix refetches every active query in the app; multiply by every user
  performing writes in a busy period and the API's read load is now a function
  of write volume. It surfaces as unexplained backend load and slow screens
  under exactly the conditions where the product needs to be fast. Invalidation
  scope is a design decision per mutation, not a default.
- **The durable queue gets implemented as "persisted mutations" because it was
  one configuration line.** The queue looks like it works in every test, because
  every test runs in a process that stays alive. It fails when the OS kills the
  app between the user's action and the flush — precisely the situation the
  queue existed for. The failure is invisible at the moment it happens and
  discovered later as missing data. If kind 3 is in the taxonomy at all, its
  durability must be tested by killing the process, not by toggling a network
  flag.
- **Ephemeral state that turns out to be durable.** A multi-step form, a
  half-written note, a selection representing twenty minutes of work — all
  correctly placed in kind 2, all correctly disposable, right up until the tab
  is closed or the app is backgrounded and the user loses the work. The
  taxonomy's kinds are about lifetime, and "ephemeral" is a claim about what the
  user is willing to lose. Re-ask that question for any screen where the user
  invests effort before submitting.

## Alternatives considered

- **One global store for everything (classic Redux, hand-rolled thunks or
  sagas).** Wins where the application's state is genuinely a single coherent
  machine — an editor, a trading blotter, a simulation — where time-travel
  debugging or middleware-level auditing of every transition is a real
  requirement, and where server data is a small part of the whole. Its cost is
  exactly the failure mode above: server data becomes ordinary store data, and
  the store gets no help with staleness, deduplication, retry, or invalidation,
  so all of it is hand-written and each screen writes it slightly differently.
- **A server-cache layer inside the same store (RTK Query).** Wins whenever
  Redux is already load-bearing in the codebase or mandated by the
  organization: it provides the same server-state ownership as a standalone
  query library while keeping one store, one devtools, one set of idioms. It is
  the right answer far more often than a greenfield-only comparison suggests —
  the taxonomy is what matters, not which package implements kind 1. It loses
  on ceremony for a small team with no existing Redux investment, and it couples
  the server-cache choice to the client-store choice, so replacing either means
  touching both.
- **A GraphQL client with a normalized cache (Apollo, Relay, urql).** Wins with
  a GraphQL API, where a normalized entity cache lets a mutation response update
  every view containing that entity without naming keys — which dissolves the
  cache-key ownership problem rather than solving it, and is a genuinely
  stronger position. It costs the GraphQL commitment end to end, and it trades
  key-management for normalization-configuration, which is easier when the
  schema is well-shaped and harder when it is not.
- **A local-first sync engine.** Wins when offline use is the product rather
  than a resiliency floor, when multiple users edit the same data concurrently
  and need merge semantics, or when the target experience is instant local reads
  with background reconciliation. It subsumes three of the four kinds and gives
  a coherent consistency story instead of the per-key rules above. It costs a
  fundamentally larger commitment: a schema the engine understands, a
  conflict-resolution model the domain must accept, a server component, and a
  data model that is hard to walk back.
- **Framework-native data loading (route loaders, server components, server
  actions).** Wins when navigation is the natural cache boundary and the app is
  substantially read-and-submit: the framework fetches on the server, revalidates
  after mutation, and no client cache exists to go stale. It costs client-side
  interactivity between navigations — optimistic updates, real-time patching,
  and offline behavior all become work performed *against* the model rather than
  with it. The combination is viable but must be deliberate: framework-owned for
  page data, client-owned for a named set of interactive surfaces.
- **Plain `fetch` in effects, no cache layer.** Wins for genuinely small
  surfaces and is the correct answer to the first counter-case above. It loses
  the moment a second component needs the same resource, because the
  deduplication, invalidation, and retry logic then gets written by hand once
  per screen — inconsistently, and with the mistakes each library exists to
  encode against.
