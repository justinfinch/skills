---
type: Guidance
title: Scope the offline promise to one write path — store-and-forward capture, not offline mode
description: Name the single workflow that must survive dead connectivity and make only its writes unlosable — a durable local queue that persists before the UI acknowledges, survives process death, and drains in order on reconnect with a client-generated idempotency key, plus a session-scoped read-only cache of just the context that workflow needs — while explicitly declining general offline mode, offline browsing, and conflict resolution, so everything off that path fails visibly instead of pretending.
tags: [offline, store-and-forward, durable-queue, idempotency, capture, resiliency, react-native, background-upload, offline-first, sync-engine]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:56:31Z }
status: stable
stale_after: 2028-03-01
sources:
  - id: mdn-background-sync
    resource: https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API
    title: MDN — Background Synchronization API
  - id: workbox-background-sync
    resource: https://developer.chrome.com/docs/workbox/modules/workbox-background-sync
    title: Workbox — background sync queue for failed requests
  - id: android-workmanager
    resource: https://developer.android.com/topic/libraries/architecture/workmanager
    title: Android WorkManager — deferrable, guaranteed background work
  - id: apple-background-transfer
    resource: https://developer.apple.com/documentation/foundation/urlsession/downloading_files_in_the_background
    title: Apple — URLSession background transfer service
  - id: stripe-idempotency
    resource: https://docs.stripe.com/api/idempotent_requests
    title: Stripe API — idempotent requests via client-supplied keys
  - id: tanstack-query-offline
    resource: https://tanstack.com/query/latest/docs/framework/react/guides/mutations
    title: TanStack Query — mutations, retry and persistence (the mechanism deliberately not used here)
  - id: kleppmann-local-first
    resource: https://www.inkandswitch.com/local-first/
    title: Kleppmann et al. — Local-first software (the full offline commitment this declines)
  - id: offline-first-primer
    resource: https://offlinefirst.org/
    title: Offline First — the design stance and its scope
  - id: nygard-release-it-patterns
    resource: https://pragprog.com/titles/mnee2/release-it-second-edition/
    title: Nygard — Release It! (bulkheads, backpressure, and failing visibly)
---

# Scope the offline promise to one write path — store-and-forward capture, not offline mode

## Technique

Do not decide "should this app work offline". Decide **which single workflow
must survive dead connectivity**, make the writes on that one path unlosable,
and let everything else fail visibly. The narrowing *is* the technique. What
makes it work is not the queue — queues are easy — it is the refusal to extend
the promise past the named path.

The commitment has three parts, and all three are load-bearing:

**A durable local queue on the write path.** When the user performs the critical
action, the payload is written to device-durable storage *before the UI
acknowledges it*, together with a client-generated idempotency key created at
that moment. Durable means it survives process death: an OS kill, a crash, a
dead battery, a force-quit mid-transfer. A background worker drains the queue in
capture order when connectivity returns, and an item leaves the queue only on a
server acknowledgement. The idempotency key is the contract that makes the drain
safe, because at-least-once delivery is the only delivery this design can offer
— the client cannot know whether an unacknowledged request was applied.

**A session-scoped, read-only cache of exactly the context that workflow
needs.** The person doing the work needs to see something to do it correctly —
prior activity, the relevant reference list, the classification vocabulary they
must choose from. That context is pre-fetched when the workflow session begins,
held read-only for the duration, and aged out when the session ends. It is
scoped to the entity in front of the user, not the corpus. This is the read-side
complement of the write-side queue and it has the same narrowness: enough
context to make the captured writes correct, and not one record more.

**An explicit, written decline of everything else.** No offline browsing of
arbitrary data, no offline editing of previously synced records, no conflict
resolution, no multi-day disconnected operation, no queue-management UI beyond a
depth indicator. This is not an omission to be quietly filled in later — it is
the decision, and it must be recorded as one, because every one of those
features is individually reasonable and collectively a sync engine. The line
between "the resiliency floor" and "offline mode as a feature" is the artifact
this technique produces.

The reason the floor is worth committing to when the feature is not: the failure
modes are asymmetric. A stale read is a visible, recoverable inconvenience — the
user sees old data, reconnects, sees new data. A lost write is silent,
permanent, and usually discovered by someone who was not there. When the work
being captured cannot be recreated by returning later — an observation of a
condition at a moment in time, a measurement, a photograph of something that has
since changed — the asymmetry is total, and it justifies bespoke code on the
write path that would be indefensible anywhere else in the client.

Two supporting rules fall out of practice:

- **Buy the transfer machinery; build only the queue's bookkeeping.** Durable
  storage, background execution, and retry with backoff are all solved by
  platform or well-maintained libraries. The version of this technique most
  likely to drop a write is the one hand-rolled from an HTTP call, a timer, and
  a key-value store, because that combination silently gives up when the process
  is suspended. Own the state machine and the idempotency key; do not own the
  transfer.
- **One queue for the named path, not a queue per write type.** The scoping
  claim is about which *path* is durable; it is not licence to give every
  feature its own persistence. Multiple queues mean multiple drain schedulers
  competing for the same connection with no shared ordering or backpressure, and
  each additional one is another thing that can silently stall. If a second
  write path genuinely qualifies, it becomes a second item type in the same
  queue.
- **Keep transfers whole until a named trigger says otherwise.** Retrying a
  complete payload is simple and safe under an idempotency key. Chunked or
  resumable transfer is a real improvement under large payloads or chronically
  bad links — adopt it when a stated trigger fires (payload size crosses a
  threshold; retry waste exceeds a measured share of traffic), not preemptively.

**What transfers to other ecosystems, and what to re-derive.** The scoping move
transfers completely, and it is the part worth carrying: name one path, make its
writes durable before acknowledgement, decline the rest in writing. So do the
idempotency-key contract, the session-scoped read cache, and every failure mode
below — none of them is about React. What is stack-bound is the *implementation
assignment*. In React/TypeScript on native, that means a device SQLite database
plus the platform's background-transfer capability, with the query library from
`guidance-client-state/concepts/client-state-taxonomy.md` deliberately kept out
of the write path. On web the same shape is IndexedDB plus a service worker's
background-sync facility, with materially weaker durability guarantees that must
be checked against the browsers actually in use before the promise is made to
users. On other platforms it is that platform's guaranteed-background-work API
over its own local database. Re-derive the components; keep the contract.

## Applies when

- **You are building a React/TypeScript application** — in practice a
  React Native or equivalent native-target client, since that is where
  guaranteed background execution and real device durability are available.
  This is the stack condition, stated first because the mechanisms named below
  are this ecosystem's. The scoping reasoning transfers; the components do not.
- **You can name the one workflow.** Not "the app should be resilient" — a
  specific, identifiable path a specific role performs, which someone can point
  at on a screen. If naming it produces a list of three or more, this technique
  is not what you need; you need either a sync engine or a smaller product.
- **Writes on that path happen under unreliable connectivity as a routine
  condition, not an incident.** The checkable version: the physical places the
  work happens are known to have poor coverage — basements, plant rooms, remote
  sites, structures, vehicles in motion — and the user cannot simply step
  outside and retry without abandoning the task.
- **Losing a captured write is unacceptable while serving a stale read is
  tolerable.** This is the asymmetry test and it is the core condition. Ask what
  each failure costs: if a stale read can cause a wrong decision with real
  consequences, you have a consistency problem this technique does not solve.
- **The captured work cannot be recreated later.** The observation is of a
  moment or a condition that changes. If the user can simply redo the action
  tomorrow with the same result, the value of durability drops sharply and a
  retry button may be enough.
- **The capture payload is bounded and the session is bounded.** A workflow
  session produces tens of items, not thousands, and ends within a working day.
  This bounds device storage, queue depth, and drain time, all of which are
  unbounded in a general offline mode and all of which become failure modes when
  unbounded.
- **The server accepts a client-supplied idempotency key on that path.** If it
  does not and cannot, the technique is not available: the drain will duplicate,
  and duplicates in a stream of captured evidence are worse than they sound.

## Doesn't apply when

- **Users must browse arbitrary data offline.** If the requirement is "I need to
  look things up when I have no signal", that is real offline mode: a local
  replica of a meaningful subset of the corpus, a sync protocol, a conflict
  model, and an invalidation story. It is a different and much larger cost
  class, and reaching it by growing this technique is the failure mode below.
  The tempting middle position — "just cache a bit more, aggressively" — is the
  worst of both, because it is a sync engine with none of the guarantees and
  none of the owner.
- **Connectivity is reliable enough that a failed write with a retry button is
  honest UX.** Most applications are here, including many that believe otherwise.
  An office application, a desktop tool, a consumer app used on a phone with
  normal coverage: a clear error, preserved form input, and an explicit retry is
  a *better* experience than a silent queue, because the user knows the state of
  their work. Requiring evidence rather than intuition is the point — if nobody
  can name where coverage actually fails, the answer is a retry button.
- **Multiple users edit the same records concurrently while disconnected.** This
  technique has no conflict model, by design; it works because captured writes
  are append-only additions to a stream rather than edits to shared state. The
  moment two disconnected clients can modify the same record, you need merge
  semantics, and that is a sync engine's job.
- **A sync engine is already in the stack.** It provides this and more; a second
  queue beside it is a second source of truth for pending writes and no way to
  order them against each other.
- **Disconnection lasts days rather than minutes.** Queue depth, device storage,
  the staleness of the session cache, and the user's memory of what is pending
  all degrade past the point where a depth indicator is an adequate interface.
  Multi-day disconnected operation is a product feature that needs designing,
  not a floor.
- **The write is a command whose outcome the user must see before proceeding** —
  a payment, an approval, an irreversible state transition someone else acts on.
  Acknowledging locally and reconciling later is dishonest for those; they need
  a real round trip and a real failure.

## Trade-offs

**Buys** exactly one guarantee, and it is a strong one: connectivity gaps stop
equalling lost work on the path that matters. The user-visible latency of the
critical action becomes local-storage latency rather than network latency, which
is often the larger product win — the interaction stops having a spinner in it
at all. It buys a bounded scope: one queue, one path, one session cache, all
sized by a workflow you can describe, which is what makes the code reviewable
and testable rather than open-ended. And it buys an honest failure surface
elsewhere — because the rest of the app does not pretend, a user who is offline
finds out immediately instead of discovering it later.

**Costs**, first, a genuinely non-trivial state machine: durable write, upload
attempt, retry with backoff, acknowledgement, cleanup, plus the transitions for
permanent failure and for items that outlive their session. In a mobile client
this is routinely the single largest piece of client complexity, and it is the
piece most in need of tests that are awkward to write. Second, **server-side
idempotency becomes mandatory, not optional** — a cost paid outside the client,
by a team that may not have asked for it, and one that has to hold forever once
clients in the field depend on the key shape. Third, device storage consumption
that scales with captured-but-undelivered volume, which needs a bound and a
policy. Fourth, a test matrix nobody enjoys: airplane mode, mid-transfer process
kill, reconnect drain, duplicate arrival, storage full, permission revoked,
partial acknowledgement. Fifth, the session cache adds a prefetch step at
session start and an invalidation step at session end, both of which are places
a workflow can get stuck. Sixth, the client contract is close to permanent:
binaries in the field cannot be made to change their idempotency-key shape.

The quality attributes moved are **durability** and **availability** of one
workflow. What is paid is **simplicity**, **testability**, and **time to
market** — and there is a subtler cost to **usability**, since a local
acknowledgement means the user is told their work is safe before the server has
seen it, which is only true if the queue is genuinely durable. That claim must
be earned by testing, not asserted by a checkmark.

**The consistency model, stated.** Delivery is at-least-once and ordering is
per-device only. The server may receive the same item twice; it may receive
device A's item before device B's earlier one; and there is a window during
which the user believes something is recorded and no server knows about it. The
design is only sound because captured items are independent appends whose order
across devices does not change their meaning. If the domain requires exactly-once
or global ordering, this technique is the wrong shape.

**What would make this stale, and why the date is where it is.** This page
carries a later `stale_after` than the taxonomy beside it, deliberately: its
reasoning rests on physical connectivity, on the asymmetry between a lost write
and a stale read, and on a scoping discipline, none of which are tied to a
library's release cadence. The futures that would move it are slower and larger.
**Ubiquitous connectivity** — if satellite-to-handset and dense coverage make
"no signal in a basement" genuinely rare in the deployment geography, the
premise weakens, and this is regional rather than global, so re-check per
market rather than in the abstract. **Sync engines becoming cheap and boring** —
the strongest candidate: if adopting a general local-first replica becomes a
weekend's work with an acceptable conflict model, the argument for a bespoke
narrow queue loses its main justification, which was always that the full
commitment costs too much. **Platform primitives closing the gap** — if
guaranteed background transfer with durable queuing becomes a first-class,
uniform capability across the platforms you ship to, including the web, the
"bespoke code you own" cost shrinks toward configuration. Revisit sooner than
the date if the second one lands.

## Failure modes

- **The queue grows silently when the drain fails, and an outage becomes data
  loss discovered weeks later.** This is the one that matters most and the one
  most often missed, because in testing the drain always succeeds. In
  production the upload endpoint returns a persistent 4xx after a deploy, or a
  credential expires, or a permission is revoked, and items accumulate. The user
  sees no error — the UI acknowledged each capture locally, exactly as designed
  — and keeps working. Days later someone notices the data is not arriving, and
  by then the device may have hit a storage limit, been wiped, or been replaced.
  The mitigations are not optional: **surface queue depth and oldest-item age in
  the UI**, escalate the surfacing when either crosses a threshold, distinguish
  permanent failures from transient ones and stop retrying the former loudly
  rather than quietly, and report queue depth to the backend from clients that
  can reach it at all so the problem is visible from the server side. An
  invisible queue is not a resiliency feature; it is a delayed incident with the
  alarm disconnected.
- **The read-only session cache quietly accretes write features until an
  accidental sync engine exists.** It begins with an obviously reasonable
  request — let the user fix a typo on a cached record while offline — then
  editing a second record type, then a rule for what happens when the server's
  copy changed meanwhile. Each step is a small ticket. What emerges is a system
  with a local replica, local mutations, and conflict resolution, built
  incrementally by whoever was on the ticket, with no owner, no consistency
  model, and no tests for the case where two devices disagree. It fails in
  production as data that silently reverts. The counter is governance, not code:
  the read cache is read-only is a stated invariant, and any request to write
  through it is a request to adopt a sync engine and must be priced as one.
- **Duplicates arrive and the server has no idempotency, so the drain
  multiplies the data.** A retry after an acknowledgement was lost in transit
  sends the item again. Without a key, the stream of captured records now
  contains duplicates that look like real repeated observations, and cleaning
  them up after the fact requires domain judgement about which are genuine. The
  key must be generated at capture time on the client and honoured server-side
  as a uniqueness constraint, not applied later.
- **The reconnect drain stampedes the API.** A regional outage ends and every
  client in the field starts uploading its backlog simultaneously — the largest
  payloads the system handles, at the moment the backend is recovering. The
  incident extends itself. Jitter the drain start, cap concurrency per client,
  and respect backpressure signals as instructions rather than as errors to
  retry through.
- **Background execution is not as guaranteed as assumed.** Every platform
  reserves the right to suspend or terminate background work, on rules that
  change between OS versions and that low-power modes tighten further. A queue
  that only drains while the app is foregrounded works perfectly in every test
  and stalls on real devices belonging to users who close apps. Verify against
  the platform's actual guarantees, and make foreground open trigger an
  immediate drain regardless of what the background scheduler was supposed to do.
- **Device storage fills.** Undelivered payloads accumulate against a finite
  disk, and the failure arrives as a write error at the exact moment of
  capture — the one moment the technique promised would always work. Bound the
  queue, decide in advance what happens at the bound (refuse new captures with a
  clear message, rather than silently dropping the oldest), and surface
  consumption before the limit rather than at it.
- **The local acknowledgement is a lie for one class of item.** A payload
  fails server-side validation permanently — malformed, too large, referencing
  something deleted. The user was told it was captured. There is no path back to
  them except a notification the app must be designed to deliver, and if it was
  not, the item sits in a dead-letter state that only a developer will ever see.
  Decide where permanently-failed items go, and who is told, before shipping.
- **The session cache's boundaries are wrong and the user hits a wall
  mid-workflow.** The prefetch scoped to one entity, and the work turned out to
  span two; or the session ran longer than the cache's validity and it aged out
  under the user. The write path still works, which is what was promised, but
  the user cannot see what they need to capture *correctly*. Scope the prefetch
  from observed workflow shape rather than from the data model's tidiest
  boundary, and prefer a slightly stale cache over an empty one while the
  session is open.
- **Nobody tests process death.** Every other failure here is survivable;
  this one voids the entire premise. If the only offline test is toggling a
  network flag, the durability claim is untested. Kill the process mid-transfer,
  reboot the device with a full queue, and reinstall-with-restore, on real
  hardware, as a release gate.

## Alternatives considered

- **Online-only with a visible failure and a retry button.** Wins whenever
  connectivity is reliable enough, and it is the correct default for most
  applications — it is honest, it is nearly free, and it keeps the user's model
  of their own work accurate. Loses precisely where the work cannot be recreated
  and the user cannot retry without abandoning the task.
- **A full local-first sync engine.** Wins when offline browsing and offline
  editing are product requirements, when several users edit shared data
  concurrently, or when the target is instant local reads everywhere. It gives
  one coherent consistency model instead of a narrow guarantee plus a set of
  rules, and it removes the accretion failure mode by making the thing the
  accretion was heading toward an owned, tested component. It costs a schema
  commitment, a conflict-resolution model the domain must genuinely accept, a
  server-side component, and a decision that is expensive to reverse.
- **A generic persisted-mutation cache from the query library.** Wins for
  convenience-level resiliency on ordinary mutations — a form submitted as the
  train enters a tunnel, resumed when it exits — and costs almost nothing to
  enable, which is exactly why it gets reached for. It loses on the capture path
  because its durability model is in-memory-first with persistence behind it,
  tuned for continuity across a page reload rather than survival of a process
  kill mid-transfer. Use it for everything *except* the named path; that
  division is the point.
- **A platform background-transfer service with no application-level queue.**
  Hand the transfer to the OS at capture time and let it own retries. Wins for
  simple single-file transfers where the OS's guarantees are strong and the
  application needs no visibility into pending state. Loses when you need queue
  depth in the UI, ordering, per-item domain metadata, or a dead-letter path —
  which is why the recommended shape uses the platform service *underneath* an
  application-owned queue rather than instead of it.
- **A local write-ahead log with no upload logic, drained by an operator tool.**
  Wins in genuinely extreme environments — long disconnection, controlled
  hardware, an explicit sync ritual at the end of a shift. It is far simpler
  than a background drain and completely predictable, at the cost of requiring a
  human step that will sometimes not happen.
- **Deferring the whole question and shipping online-only "for now".** Worth
  naming because it is the most common actual outcome. It wins when the
  connectivity assumption has been *checked* and holds. It loses badly when the
  assumption was never checked, because the cost of retrofitting durability is
  not the queue — it is the server-side idempotency contract, the field
  binaries already deployed without a key, and the work already lost.
