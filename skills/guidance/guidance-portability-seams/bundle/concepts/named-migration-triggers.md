---
type: Guidance
title: Naming the escape valve and the triggers that reopen the decision
description: When you commit all-in to a platform you cannot cheaply leave, make the same decision record carry the specific alternative you would move to and per-layer triggers — measurable thresholds on cost, latency, consumer count or a named feature gap — whose firing produces a new decision record rather than an automatic migration.
tags: [portability, lock-in, migration-trigger, adr, reversibility, escape-valve, platform-commitment]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:34:36Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: nygard-adr
    resource: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
    title: Nygard — Documenting Architecture Decisions
  - id: adr-org
    resource: https://adr.github.io/
    title: Architecture Decision Records — conventions and templates
  - id: hohpe-lockin
    resource: https://martinfowler.com/articles/oss-lockin.html
    title: Hohpe — Don't get locked up into avoiding lock-in
  - id: hohpe-cloud-strategy
    resource: https://architectelevator.com/book/cloudstrategy/
    title: Hohpe — Cloud Strategy (the architect's guide to hybrid and multi-cloud decisions)
  - id: fowler-irreversibility
    resource: https://martinfowler.com/bliki/Irreversibility.html
    title: Fowler — Irreversibility
  - id: ford-evolutionary-architecture
    resource: https://evolutionaryarchitecture.com/
    title: Ford, Parsons and Kua — Building Evolutionary Architectures
  - id: eu-data-act
    resource: https://digital-strategy.ec.europa.eu/en/policies/data-act
    title: European Commission — Data Act (Reg. (EU) 2023/2854), Art. 29 withdrawal of switching charges
---

# Naming the escape valve and the triggers that reopen the decision

## Technique

When a decision commits the system all-in to one platform or product, the **same
decision record** carries two further artifacts, written at commitment time and
not deferred:

1. **A named escape valve.** Not "we could move" — the specific alternative you
   would actually move to, named as a product, per layer. Naming it costs a
   fraction of a migration study and is the only thing that makes "we are not
   locked in" a claim rather than a hope.
2. **Per-layer migration triggers.** For each layer of the commitment, an
   **observable threshold** that reopens the decision: a monthly cost line item,
   a sustained rate, a consumer or worker-class count, a topology change, or a
   specific feature gap becoming a requirement.

A useful shape is a table in the decision record with one row per layer and four
columns — *layer*, *what we chose*, *what we would move to*, *what would make us
move* — because the four-column discipline is what stops a trigger from being
written without a target or a target from being written without a trigger.

**A trigger is a fact someone can measure.** "Sustained egress above fifty
dollars a month," "more than five consumer classes," "a consumer in a different
region from the database," "resumable upload becomes a product requirement."
Not "if costs become unreasonable," not "when it gets painful." If you cannot
state the threshold as a number or a binary event, you have not found the
trigger yet — you have found a feeling, and a feeling does not survive the
personnel change that guidance like this exists to survive.

The four dimensions worth a threshold are **cost**, **latency**, **consumer
count**, and a **named feature gap**, and latency is the one most often left as
a feeling. Write it as a percentile against a named observation point, because
"the database feels far away" is unactionable and a p99 is not:

> *Trigger (database layer): p99 read latency measured from the EU worker pool
> against the US-region managed Postgres exceeds 120 ms for seven consecutive
> days on the existing APM dashboard. Rationale: 120 ms is the point at which
> the worker's 400 ms end-to-end budget stops absorbing a retry, measured in
> the March soak. Firing this reopens the decision toward the named target — the
> same vendor's multi-region offering — not automatically toward leaving.*

That row has everything the other three dimensions need too: the metric, the
observation point, the number, the duration, the dashboard it is read from, and
why the number is that number. A latency trigger stated without an observation
point is ambiguous by construction — the same system is fast from one region and
slow from another, and the trigger has to say which one it is watching.

**Per layer, not per platform.** A single-vendor commitment is not one decision;
it is one decision per layer — compute, database, object storage, identity,
messaging, media transform — bundled for operational convenience. Each layer has
its own economics, its own market, and its own reversal cost, so each gets its
own escape valve and its own trigger. A separate, coarser whole-stack escape
valve covers the case where the *bundle* stops being worth it rather than any
one layer.

**Firing a trigger produces a decision, not a migration.** The threshold's job is
to force a re-grill from the named target rather than from zero. "The trigger
fired, we looked, we are staying, here is why" is a legitimate and common
outcome — and is itself a record. A trigger that automatically executes a
migration is an operational hazard; a trigger that fires and produces silence is
the failure mode below.

**Write down why the number is the number.** A threshold without its rationale
cannot be revised intelligently: the next reader has no way to tell whether 100
per second was a measured limit, a vendor-documented ceiling, or a guess. With
the rationale attached, the number stays revisable as the platform changes
underneath it.

**Some "triggers" are experiments in disguise.** If the uncertainty is *"will
this platform hold up under our actual workload"* rather than *"will the
economics shift"*, a threshold is the wrong instrument. That is a **go/no-go
gate**: run the soak or the spike before the commitment hardens, and let the
escape valve be taken immediately on a failure rather than years later on a
threshold. Validating the riskiest integration last is exactly backwards, and
dressing it up as a migration trigger is how it gets scheduled last.

**Shape the design as though the trigger will fire tomorrow.** The most valuable
effect of naming the alternative is backward, on what you build now: an event
envelope that maps cleanly onto the named broker's subject space, a client
factory that hides a vendor SDK behind a commodity API, a schema that does not
depend on a proprietary type. That work is cheap while the code is being written
and expensive afterwards. See
`guidance-portability-seams/concepts/standard-api-seams.md` for where the seam
should sit.

## Applies when

- **The commitment is expensive to reverse and gets more so with time.** Reversal
  cost is dominated by data gravity and by contract-shaped coupling (identity,
  billing, IAM), both of which grow monotonically. If you can name the thing that
  would be hard to move — bytes, a schema, a users table, an issued-token
  contract — the trigger is worth writing.
- **The platform market is live.** At least one credible alternative exists
  *today* and the field is moving: pricing changes, new entrants, products
  reaching or leaving general availability, a competitor's alpha service becoming
  a real option. A live market is what makes "the calculus can shift" a
  prediction rather than a platitude.
- **The commitment was made for consolidation reasons rather than capability
  reasons** — one billing relationship, one IAM, one observability pane, one
  local-development story, less context-switching for a small team. That is a
  legitimate reason to go all-in and a poor reason to stay all-in forever, and
  the trigger is precisely what distinguishes deliberate consolidation from
  inertia.
- **The quantity that would change the answer is already measurable, or cheap to
  start measuring.** A billing line item, a metric you already emit, a count of
  deployed consumers. If the measurement does not exist and nobody will build it,
  see the first failure mode.
- **The organization keeps decision records and someone reads them.** Triggers
  are a written-culture technique. They pay off when the person who hits the
  threshold in two years can find the record and the record still means
  something.
- **An external party will ask.** Enterprise procurement, security review, and
  investor diligence all ask a version of "what happens if this vendor
  disappears or triples its price." A per-layer trigger table is the shortest
  credible answer.

## Doesn't apply when

- **The commitment is cheap to reverse anyway.** A stateless service in an OCI
  container behind a commodity API, a library behind an interface you own, a
  managed service with an hour of data in it. Writing a trigger table for those
  is ceremony that dilutes the ones that matter — and diluting them is the
  mechanism behind trigger inflation below. The test is arithmetic, not taste:
  estimate the reversal in engineer-days; below a week, just move when you want
  to.
- **Trigger-writing has become a way to avoid a decision that is cheap to make
  now.** This is the tempting case, and it is the one to guard against. A
  deferral with a named threshold *feels* like rigor: it is written down, it has
  numbers, it cites a target. But the artifact is doing two different jobs —
  preserving optionality, and postponing an evaluation — and only the first is
  legitimate.

  *Evidence shape: a production system wrote a careful deferral record for a
  message broker — named product, three numeric thresholds, an explicit "not at
  v1" — and adopted that broker at v1 a few weeks later, because correcting an
  unrelated design flaw turned out to require the fanout the deferral had
  assumed away.* Two lessons, and they point in opposite directions, so keep
  both. The trigger record was not wasted: it had already forced the event
  envelope to be shaped so it mapped onto the broker's subjects and message ids,
  which turned the reversal into a publish-handler change and a deployment
  rather than a redesign. But the honest reading of the episode is that **the
  deferral itself was the wrong call** — the evidence needed to adopt was
  available at decision time and the threshold table made it comfortable not to
  look. Before writing a deferral trigger, ask what the decision would cost to
  simply make now. If the answer is "about the same as writing this table," make
  it. (The broker side of the same episode is told in
  `guidance-event-delivery/concepts/relay-to-broker-dispatch.md`; this page is
  about the decision hygiene, not the messaging mechanics.)
- **You cannot state the threshold as a number or a binary event.** Then it is
  not a trigger. The honest alternatives are a dated re-evaluation ("revisit
  2027-06-01") or an experiment run now, and both are better than a threshold
  phrased as a mood.
- **The commitment is genuinely one-way and no alternative exists.** A
  sole-supplier integration, a regulator-designated system, an ecosystem with
  exactly one implementation. Write the constraint and its blast radius, not a
  fictional escape valve — a named target nobody could actually take is worse
  than an admitted dependency, because it stops the conversation.
- **The layer is a commodity you would replace without ceremony.** Nobody needs
  a migration trigger for a CDN or a transactional-email provider. Reserve the
  table for layers where the migration would be a project.
- **The switching cost is contractual rather than technical, and the contract is
  the lever.** Renewal negotiations, committed-spend discounts and exit clauses
  move that cost far more than architecture does. The trigger still helps as a
  negotiating input, but do not let a portability programme substitute for
  reading the contract.

## Trade-offs

**Buys** a bounded, pre-analyzed reversal: when the threshold fires, the next
person re-grills from a named target with a stated rationale instead of starting
a vendor evaluation from zero under time pressure. It buys a defensible answer
to lock-in questions from procurement and diligence. And — the underrated half —
it buys **design pressure in the present**: naming the alternative forces you to
notice which parts of the design assume the vendor, while those parts are still
cheap to change.

**Costs** three things. First, real analysis at commitment time: you must
evaluate the alternatives well enough to name one, which is a fraction of a
migration study paid up front, before you know you will need it. Second, an
ongoing measurement burden — every trigger is a number someone has to watch, and
watching costs more than writing. Third, and least visible, a **false sense of
safety**: a trigger table can be read as proof of portability when it is only
proof that portability was once considered, which is exactly how the seam gets
to rust unnoticed.

There is also a failure mode adjacent to the technique rather than inside it.
Teams that take portability seriously sometimes buy it by abstracting everything,
and land on a least-common-denominator architecture that forfeits the capability
they chose the platform for. The trigger is meant to keep the *decision*
reversible, not to make the *architecture* vendor-neutral. Those are different
goals with different prices, and the second is usually the worse deal.

The quality attributes moved are **modifiability** and **cost predictability
under vendor change**. What is paid is **time-to-decide**, **operability** (more
things to monitor), and the analytical effort itself.

**What would make this stale.** The whole technique is priced off switching
costs, and switching costs are under active downward pressure from two
directions. Regulation is one, and it is worth reading precisely, because the
loose version of this claim inverts what the rule actually does. The EU Data Act
(Reg. (EU) 2023/2854, Art. 29) withdraws **switching charges** — what a provider
bills for the switching process itself, including the egress incurred in moving
data out — and it explicitly carves out charges for services rendered in the
ordinary course. So it lowers the *one-time exit bill*, which is the denominator
of the reversal-cost estimate; it does **not** touch routine operational egress
billing, which is the numerator of a running-cost trigger. The worked example
above — "sustained egress above fifty dollars a month" — is ordinary service
consumption and survives the regulation unchanged. What genuinely gets staler is
any trigger phrased around the exit event: "migration would cost us N in egress
fees" stops being a threshold worth tracking in the covered market, because the
answer trends to zero by statute. Standardization is the other: as container
runtimes, managed
Postgres, and object-storage APIs converge, the reversal cost for the middle of
the stack falls toward the "cheap to reverse anyway" counter-case above. Push in
the other direction and the technique gets *more* load-bearing, not less: as
managed AI surfaces, proprietary identity federation, and vendor-specific data
formats become the reason to pick a platform, the coupling migrates to layers
where no commodity API exists and no threshold is easy to state. Re-derive which
layers actually deserve a row in your table; do not inherit the list.

## Failure modes

Note the shape of this list before reading it: **none of these page anyone.**
Every failure here is silent and slow, discovered months or years late during a
migration study, a bill review, or a diligence questionnaire. That is precisely
why the counter-measures are all scheduled rather than reactive — there is no
alarm that fires when a decision quietly becomes irreversible.

- **An unmonitored trigger is a comment.** The single most common outcome. The
  egress threshold was written, nobody wired it to a billing alert, and two years
  later the bill sits at four times the trigger with no one aware. The threshold
  did not fail — it was never a control, only prose. The test to apply at
  authoring time, per trigger: *name the dashboard, alert, or recurring review
  where this gets checked, and the role that owns it.* If you cannot, you have
  two honest options — build the measurement, or delete the trigger and say
  plainly that this layer is unmonitored. Leaving it in place is worse than
  either, because it converts an unknown into a false assurance.
- **The escape valve is named but never exercised, and the seam has silently
  rusted shut.** The named alternative sits in the record while the deployment
  pipeline grows vendor-specific steps, infrastructure code adopts vendor-only
  resource types, application code picks up an SDK-only convenience, and the
  identity model absorbs the vendor's group semantics. The record still says
  "bounded migration"; the reality is a quarter of work nobody has scoped. The
  diagnostic is a question with a suspiciously vague answer: *how long would the
  move take, and when did anyone last check?* Remedies are all forms of
  exercise — run the local double or the alternative in CI, deploy one component
  to the named target in staging once a year, or encode the boundary as a
  build-failing check (see `guidance-fitness-functions`). Erosion is continuous
  and silent, so the counter-measure has to be periodic and loud.
- **The trigger fires and nothing happens.** This is an organizational failure
  wearing a technical costume. The threshold was set at a level nobody would
  actually act on, or the owner moved teams, or the migration is now unaffordable
  and admitting that is uncomfortable. The symptom is a metric visibly past its
  stated threshold in a dashboard everyone looks at. The rule that prevents it:
  a fired trigger's required output is a **new dated record**, and "we are
  staying, here is what changed" satisfies it. Silence does not.
- **The threshold sits on the wrong side of the pain.** The number was chosen
  where the cost becomes *noticeable* rather than where the migration is still
  *affordable*, and by the time it fires the data gravity accumulated in the
  interim has made the move three times harder than it was when the record was
  written. Set thresholds against reversal cost, not against annoyance.
- **Trigger inflation.** Every decision record grows a trigger table because the
  template has one, so there are forty triggers and nobody measures any. The
  effect is worse than having none: it teaches readers that trigger tables are
  decoration. Ration them to layers where the migration would be a project.
- **A superseded trigger left standing.** The technology was adopted, or the
  layer was replaced, and the old record still reads `accepted` with its
  thresholds intact. Someone now measures a number that no longer means anything,
  or worse, cites the old target in a new decision. Mark the record superseded,
  point at what replaced it, and keep the text — the "we thought X until Y" trail
  is most of the value — but do not leave it looking live.
- **The trigger is written as one-directional.** Deferral triggers in particular
  are written as "adopt when the number is exceeded", and the number is not how
  they usually fire. What actually happens is an unrelated design correction that
  makes the deferred thing necessary, or a licensing change that makes the named
  target unavailable, or a competitor's product reaching general availability.
  Triggers fire in either direction and from outside the variable you chose to
  watch; write the record so that "we are adopting this early, for reasons not on
  this list" is an expected path rather than an embarrassment.
- **Compute portability is celebrated while the data is pinned.** Containers move
  in an afternoon; the object store holding years of bytes, the managed database
  with its extensions and its replication topology, and the identity provider
  holding every user's credentials do not. A trigger table that covers the easy
  layers and goes quiet on the hard ones is a portability story about the parts
  that were never the problem. Order the table by reversal cost and let the
  expensive rows be uncomfortable.
- **The named target decays.** It was the obvious second choice at commitment
  time; since then it changed licence, was acquired, entered maintenance mode, or
  sunset the specific service you named. Nobody noticed because nobody looks at
  the alternative until they need it. Re-validating the named target is part of
  the periodic review, not part of the migration.

## Alternatives considered

- **Commit and write nothing.** Wins when the reversal cost is genuinely
  acceptable, when the platform is an industry constant on your time horizon, or
  when the team is small enough that the knowledge does not need to survive a
  handover. Loses the moment someone external asks the lock-in question, or the
  original decider leaves — at which point the commitment looks accidental even
  if it was deliberate.
- **Actively multi-vendor from day one, or an abstraction layer over providers.**
  Wins when a contract or regulator genuinely requires a second source, or when
  the workload really does run in two places. Loses almost everywhere else on
  cost: you pay for two of everything, operate the intersection of both feature
  sets, and lag both providers' releases — while an unexercised second provider
  is no more ready than an unexercised escape valve.
- **A dated re-evaluation ("revisit in twelve months").** Wins when the driving
  variable is genuinely unmeasurable — a vendor's strategic direction, a team's
  future skill mix — where a threshold would be false precision. Loses because
  calendar reviews decouple from reality in both directions: they get skipped
  when nothing is wrong, and they arrive months after the thing they should have
  caught. Best used *alongside* thresholds, as the sweep that catches what no
  metric watches.
- **An organization-level one-way-door register** — a list of decisions
  classified as irreversible, reviewed at a higher bar. Wins as a complement at
  scale: it makes the class of decision visible before it is made. Loses as a
  substitute, because it names the door without naming the exit; the per-layer
  target and threshold still have to be written somewhere.
- **A go/no-go gate before the commitment hardens** — a soak test or spike run
  first, with a verdict rule that takes the escape valve immediately on failure.
  Wins outright when the uncertainty is *"does this platform hold our workload"*
  rather than *"will the economics shift"*, and should replace a threshold for
  that class of risk rather than sitting beside it. Loses when the risk genuinely
  is future economics, which no gate run today can settle.
- **Sacrificial architecture** — build for the current horizon and plan to
  replace the whole thing. Wins when the horizon is short and the growth curve is
  steep enough that today's design will not survive regardless, which makes
  per-layer portability work a poor investment. Loses when the data outlives the
  system, which it usually does — the bytes and the schema are the part you were
  never going to sacrifice.
- **Escrow, exit clauses, and committed-spend negotiation** — moving the
  switching cost contractually rather than architecturally. Wins when the
  coupling is commercial, which for large platform commitments it substantially
  is, and it is far cheaper than engineering. Loses when the vendor exits the
  business or sunsets the service, where no clause returns your architecture to
  you.
