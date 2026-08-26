---
type: Guidance
title: Making a load-bearing decision executable in CI
description: Name, at decision time, the executable check that detects each load-bearing decision's violation, and run it in CI in a fast static lane and a slower integration lane, so architectural erosion fails a build instead of surfacing in production.
tags: [architecture, fitness-functions, ci, evolutionary-architecture, governance]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T15:58:59Z }
status: stable
stale_after: 2029-06-01
sources:
  - id: ford-parsons-kua-evolutionary
    resource: https://evolutionaryarchitecture.com/
    title: Ford, Parsons, Kua — Building Evolutionary Architectures
  - id: archunit
    resource: https://www.archunit.org/userguide/html/000_Index.html
    title: ArchUnit User Guide
  - id: dependency-cruiser
    resource: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md
    title: dependency-cruiser — Rules Reference
---

# Making a load-bearing decision executable in CI

## Technique

Every load-bearing architectural decision names, **at decision time**, the
executable check that detects its violation. The decision record does not end at
"the read model must not import the domain model"; it ends at the rule file, the
test path, and the CI lane that will fail a pull request which does exactly that.
A decision without a named check is a decision that survives only as long as
everyone who made it is still reviewing the diffs.

The checks run in CI in **two lanes**:

- **Static** — dependency-direction rules, privilege lint, file-placement and
  registration checks, forbidden-import rules. Cheap, hermetic, no services
  required. Runs on **every** pull request.
- **Integration** — database-privilege probes, cross-tenant probes, rebuild-time
  and replay budgets. Needs a real engine and real data. Runs on every pull
  request when it is fast enough, and **nightly** when it is not.

Placing a check in a lane is a design decision, not a scheduling detail: the
static lane is where a violation is stopped, the nightly lane is where a
violation is *discovered*, and moving a check from the first to the second is a
deliberate reduction in guarantee that should be recorded as such.

One sentence is the contract, and it belongs beside every check:

> **Tripping this means a real architectural regression, not a flaky test.**

That sentence is what separates a fitness function from a test. It sets the
expected response — stop, read the decision record, either fix the code or
change the decision — and it forbids the response that kills the practice, which
is re-running the job until it goes green. A check nobody is willing to write
that sentence about is not a fitness function; it is a test with ambitions.

Two lanes are not the whole taxonomy, and it is worth knowing what the lanes
leave out. Some checks are **continual** — they run against the live system
rather than against a build, as monitors, synthetic probes, or deliberate fault
injection — and some are **holistic**, asserting two qualities *together*
because each one passes alone and the combination is what breaks. This page is
about the CI-gated kind, which is the majority and the cheapest to start with;
when a property can only be established against a running system, say so in the
decision record and give it a runtime check with an owner, rather than
manufacturing a build-time proxy that asserts something weaker.

Name each check after the **decision** it defends, not the mechanism that
implements it — `read-model-does-not-import-domain`, not `dependency-cruiser
rule 14`. The name is what appears in a red build at 6pm, and it has to point at
the reason on its own. Track the set in a
[registry](fitness-function-registry.md), so "we have a fitness function for
that" is a claim someone can check rather than a thing someone remembers.

## Applies when

- **The decision has a structural expression a machine can check.** Dependency
  direction, module and package boundaries, database grants and role privileges,
  schema properties (a policy exists on every table carrying a given column),
  file placement and registration conventions, build-output size, replay or
  rebuild duration. If you can say what a violating commit looks like in the
  repository or in the database catalog, the check is writable.
- **CI exists and its failures actually block.** A merge gate on a protected
  branch. Where a red build can be force-merged as routine, the check reports
  rather than enforces, and should be labelled as reporting.
- **The code will be written by more hands than made the decision** —
  emphatically including coding agents. Erosion is invisible in a diff to
  everyone who was not in the room for the decision, and an agent completing a
  task has no memory of a boundary it was never shown. This is the condition
  that has strengthened most: the ratio of code authored to decisions understood
  has moved sharply, and a machine-checkable boundary is the only kind that
  survives it.
- **The decision is expensive to reverse once violated.** A boundary that erodes
  over fifty commits costs a refactor to restore; a `DELETE` grant that leaks
  onto the wrong role costs an incident. Cheap-to-reverse decisions do not earn
  the second artifact.
- **CI can reproduce the property being checked.** An integration probe asserts
  against the database CI builds, not the one production runs. If the migrations
  and the role grants that CI applies are not the same ones production applies,
  the check asserts a property of a fixture. Make the CI environment derive from
  the same migration and grant source, or state plainly that the check covers
  the definition and not the deployment.

## Doesn't apply when

- **The decision has no mechanically checkable expression.** Vendor and product
  choices, naming taste, "the domain model should be rich", "handlers should be
  thin". A check written for one of these tests something *adjacent* — a proxy
  the decision does not actually mean — and then rots, because refactors move the
  proxy while the decision holds. Write the ADR and leave it at that.
- **The only possible check is so slow or so flaky that the team will learn to
  ignore it.** Move it to a nightly lane with a named owner, or do not write it.
  A check that trains people to hit rerun is worse than an absent one, because it
  spends the credibility that the other checks are running on.
- **Nothing in the repository yet has the shape the rule keys on.** A rule
  matching zero files passes vacuously and reads as coverage. Either write it
  **forward-binding** — key it on the path convention the new code will use, so
  it binds when that code arrives without failing on today's layout — or file it
  as deferred with the milestone that creates the shape.
- **The design is still in flux.** Pinning an exploratory boundary in CI
  converts iteration into a rule change plus a check change per experiment, and
  the usual outcome is that the check gets exemptions until it matches nothing.
  Wait until the boundary stops moving.
- **The platform can make the violation impossible instead of detectable.** A
  privilege that was never granted beats a test asserting it is absent; a module
  the build cannot resolve beats a lint rule forbidding the import. Prefer the
  structural impossibility, and then, if the configuration can drift, write the
  much smaller check that asserts the configuration is still what it was.
- **The property spans systems that no single pipeline sees.** "No service calls
  another synchronously on the request path" is not a static-analysis question
  inside one repository. Cross-system properties need consumer-driven contract
  tests, runtime assertions, or trace-based checks; a repository-local rule that
  looks like it covers them is a false negative with a badge on it.

## Trade-offs

**Buys:** decisions stay enforced without review vigilance. The property moves
from "someone will notice in review" to "the build will not go green", which
means it holds on the Friday deploy, in the PR nobody had time to read
carefully, and in code an agent generated at 2am. It also converts an ADR from
a document into an executable claim: the check is the honest answer to "is that
decision still true in this codebase?", and it is the only answer that stays
correct without maintenance.

**Costs:** every architectural change now has **two artifacts** to update, and
the second one is the one people forget. Build time grows — the integration lane
especially — and change friction grows with it, which is the point when the
change is a violation and pure loss when the change is a legitimate refactor
that happens to move a path the rule keys on. A wrong check is worse than no
check: it is a false constraint enforced with a machine's authority, and it
teaches the team that the fitness lane is an obstacle rather than a signal.

The quality attributes this moves are **modifiability** and, for the privilege
and isolation checks, **security**; what it spends is **build speed** and
**change latency**. It is a good trade when violations are expensive and
frequent, and a bad one when the boundary was never really under pressure.

**What would make this stale.** The practice itself is durable, but two of its
assumptions are not: that CI is a gate a human respects, and that structural
violations are hard to detect any other way. If automated review reliably
catches boundary violations at authoring time, the static lane's job shrinks to
the ones that must be *proved* rather than noticed — grants, policies, budgets.

## Failure modes

- **A check is skipped to green under deadline, and the decision is silently
  revoked.** Someone adds the exemption, the exclusion glob, or the
  `--no-fitness` flag to ship on Thursday, and nobody removes it. There is no
  event marking the moment the architecture stopped being enforced — the build
  is green the whole way. The 3am version arrives months later: an incident
  traces to a boundary that a rule was supposedly guarding, and the git blame on
  the exemption is older than anyone's memory of it. Treat exemption lines as
  architectural changes — require the decision record to change with them, and
  make the exemption list something a human reads at each milestone.
- **A check pins implementation detail rather than the decision, so honest
  refactors trip it.** The rule keys on a filename, a directory that moved, or a
  helper's exact name instead of the property. Every legitimate rename produces a
  red build that the author correctly identifies as noise. The observable damage
  is not the wasted hour; it is that the team now *expects* fitness failures to
  be noise and applies that expectation to the next real one.
- **The registry says active for a check that no longer runs.** A rule file was
  renamed, a test moved out of the lane's glob, a CI job stopped being called by
  the workflow, a suite skips itself when its container is unavailable. The
  registry, the architecture document, and the onboarding conversation all still
  say the boundary is guarded. This is the most dangerous failure in the practice
  because everything is green and everyone is confident. Periodically assert the
  lane's own health: that each named check ran and produced a result, and that
  rules match a non-zero number of files.
- **A vacuous pass on a check that matters.** A cross-tenant probe that
  connects with a role holding an unintended bypass, a privilege test asserting
  against a CI database whose grants were never applied, a dependency rule whose
  glob matches nothing after a directory rename. The check reports success
  having tested nothing. Every check that guards a security property needs a
  **negative control**: a deliberately violating case that the check must catch,
  run alongside it, so a check that has stopped working fails loudly.
- **A flaky integration check trains the rerun reflex.** One check with a
  timing-dependent probe fails once a week. The team learns to re-run. Six months
  later a genuine cross-tenant regression is re-run away twice before anyone
  reads the output. Flakiness in a fitness lane is not a test-quality problem; it
  is an erosion of the one sentence the practice runs on.
- **The nightly lane fails unowned.** Nobody is paged for a nightly job. The
  rebuild-budget check goes red in March and is noticed in June, by which point
  the budget was blown by a change nobody can now isolate. Every nightly check
  needs a named owner and an alert that reaches a human, or it belongs in the PR
  lane where a person is already looking.
- **Two artifacts drift in the safe-looking direction.** The decision is
  loosened in the ADR — deliberately, correctly — and the check stays strict.
  Builds now fail for conformant code, and the fix that gets applied under
  pressure is an exemption rather than a rule change, which lands the codebase in
  the first failure mode above.

## Alternatives considered

- **Code review as the guard** — wins when the codebase is small, every author
  was in the room for the decision, and the boundary is visible in a single
  diff. Loses as soon as the violation is a *cumulative* pattern rather than a
  single bad line, and loses entirely for code written by an agent that never
  attends the review.
- **Decision record and documentation only** — wins for genuinely one-time,
  irreversible choices with no ongoing violation surface: the vendor, the
  protocol, the language. There is nothing for a check to detect after the
  choice is made, and writing one manufactures a proxy.
- **Runtime or platform enforcement** — database privileges, module systems,
  package-boundary tooling, separate deployables. Wins whenever the platform can
  make the violation *impossible* rather than detectable; prefer it, and demote
  the fitness function to a drift check on the configuration. Loses when
  enforcement would have to be so coarse that legitimate work is blocked, or
  when the property is about source structure the runtime cannot see.
- **Scheduled architecture review or manual audit** — wins for the qualities
  that genuinely cannot be automated: usability judgement, whether the model
  still fits the domain, whether the decision is still the right one. Keep it,
  name it as a manual gate with a cadence and an owner, and do not let its
  existence excuse the absence of the automatable checks.
- **Continual checks against the running system** — monitors, synthetic probes,
  and deliberate fault injection that assert an architectural property in
  production rather than in a build. Wins for properties that only exist under
  real load, real data volume, or real failure — resilience, saturation
  behaviour, actual latency distributions — where a CI approximation asserts
  something the production system never promised. Loses as a first move: it
  needs an owner, an alerting path, and a tolerance for testing in production
  that a build-time check does not.
- **Measured-and-alerting budgets, non-gating** — wins for properties whose
  measurement is noisy: cold-start times, p99 latency, bundle size on a
  fast-moving surface. Report and alert on regression rather than failing the
  build, and record in the registry that this check reports rather than gates,
  so nobody mistakes it for a boundary.
- **Consumer-driven contract tests** — wins for the cross-service properties a
  repository-local rule cannot see. Complementary, not competing: contracts guard
  the seams between systems, fitness functions guard the structure within one.
