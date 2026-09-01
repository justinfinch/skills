---
type: Guidance
title: Where the modelling investment belongs
description: Classify subdomains as core, supporting, or generic, so the scarce modelling effort lands on what differentiates the business and the rest is bought or kept deliberately plain.
tags: [ddd, core-domain, distillation, subdomains]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T14:24:19Z }
status: stable
stale_after: 2031-01-01
sources:
  - id: evans-ddd
    resource: https://www.domainlanguage.com/ddd/
    title: Eric Evans — Domain-Driven Design
---

# Where the modelling investment belongs

## Technique

Classify each subdomain by its relationship to what the business wins by:

- **Core** — the software the business competes on. Model it deeply, staff it
  with the strongest people, build it in-house. This is where everything the
  rest of this pack describes actually pays.
- **Supporting** — necessary and bespoke, but not differentiating. Keep it
  deliberately plain; CRUD is not an insult here, it is the budget.
- **Generic** — solved industry-wide: identity, billing, notifications,
  scheduling. Buy it, adopt it, or conform to it.

Write a domain vision statement — a few sentences naming why the core is
valuable and to whom — and use it as the tie-breaker when classification is
contested.[^evans-ddd] The core is small. If the classification says most of
the system is core, distillation has not happened yet; it has been voted on.

This decision sits directly behind the gate in
[strategic-ddd.md](strategic-ddd.md): that page decides *whether* the domain
model is the primary design artifact; this one decides *where within the
system* that commitment holds, because it cannot hold everywhere.

[^evans-ddd]: *Domain-Driven Design* — strategic distillation: core domain, generic subdomains, domain vision statement.

## Applies when

- The system is large enough that modelling effort is rationed whether or not
  anyone decides how. Distillation does not create the scarcity; it makes the
  allocation deliberate instead of accidental.
- The business genuinely competes on some behaviour of this software, and you
  can say which — the differentiator is nameable, not aspirational.
- A build-versus-buy or staffing decision is pending, and "it depends on how
  important that part is" keeps coming up without anyone owning the answer.

## Doesn't apply when

- **The whole system is one subdomain.** A small system with one job has
  nothing to rank. Uniform treatment is correct, and the classification
  ceremony buys a one-row table.
- **The business does not compete on this software.** Cost-centre systems —
  internal tooling, back-office automation — where adequate is the goal have
  no core in Evans' sense. The honest output of classifying them is "all
  supporting and generic", and the useful decision is a build-versus-buy
  sweep, not a modelling investment.
- **The strategy is not stable enough to name a differentiator.** Before
  product–market fit, this quarter's core is next quarter's discard.
  Classification hardens a guess and redirects investment behind it; the
  missing input is strategy, and no amount of domain analysis substitutes.

## Trade-offs

Buys concentration of the two scarcest inputs — domain-expert time and the
strongest engineers — where they compound, and something less obvious:
explicit permission for the rest of the estate to be plain. That permission is
what actually frees the investment; without it, effort diffuses to wherever
the most vocal stakeholder or the most interesting problem sits.

Costs a deliberate quality gradient that engineers read as unfairness — "why
is my area not allowed to be good" is a real conversation the classification
obliges you to have. And the classification is itself a strategic claim that
can be wrong: misplace the core and the whole apparatus efficiently directs
investment at the wrong thing, which is worse than diffusing it.

## Failure modes

- **Everything declared core.** Each stakeholder defends their area, the
  classification ends in consensus, and nothing is deprioritized. A ranking
  that ranks nothing is a renaming exercise, and it is the most common outcome
  of running distillation as a workshop instead of a decision.
- **A generic subdomain built bespoke.** The team ships its own identity
  system, its own scheduler, its own notification pipeline. The core starves
  while the team polishes a worse version of something purchasable, and the
  3am page comes from the home-built component — because the bought one had an
  on-call rotation and the bespoke one has a README.
- **The core outsourced.** The inverse, and quieter: the differentiator gets
  delegated to a vendor platform because it looked like the hard part. The
  business now differentiates on a roadmap it does not control, discovered
  when the vendor deprecates the feature the business is built on.
- **Classified by difficulty or sunk effort rather than differentiation.** The
  hairiest legacy module is declared core because it hurts the most and has
  absorbed the most engineering years — and it turns out to be a generic
  scheduling problem someone built in-house in 2009.
- **Investment follows interest rather than the map.** The strongest engineers
  drift to the most technically interesting subdomain, which is rarely the
  core — the core is domain-hard, not algorithm-hard. The classification
  exists and the staffing quietly ignores it.
- **The classification is never revisited.** Differentiators commoditize:
  yesterday's core — delivery tracking, recommendation, search — is today's
  API subscription. A classification with no review date becomes archaeology,
  and the investment keeps flowing to a moat that has already been filled in.

## Alternatives considered

- **A uniform quality bar everywhere** — wins on small, single-team systems
  where administering a gradient costs more than it saves. Stops working the
  moment effort must be rationed, which is earlier than teams admit.
- **Buy-first across the board** — wins for cost-centre estates with no core,
  where the honest strategy is adequacy at minimum spend. It is distillation's
  own recommendation applied to the degenerate case.
- **Follow the churn** — invest wherever change requests concentrate. Wins
  briefly when strategy is genuinely unreadable, but churn measures friction,
  not differentiation; the noisiest subdomain is often a supporting one with a
  bad interface.
