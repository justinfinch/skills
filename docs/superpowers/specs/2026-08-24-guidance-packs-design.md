# Guidance packs — installable architectural judgment

**Date:** 2026-08-24
**Branch:** `guidance-packs`
**Status:** approved, ready for planning

## Goal

Introduce a fourth skill family, `guidance-*`: installable packs of durable, general architectural knowledge that an agent consults during a decision and cites in the resulting ADR. Each pack is simultaneously an agent skill (so it installs and triggers through machinery that already exists) and an OKF v0.2 bundle (so it has a citable, versioned identity).

Add `write-guidance`, an authoring skill that extracts packs from existing project Arches or authors them greenfield, using the architect lenses adversarially.

Prove the shape by extracting `arche-architect/references/LENSES.md` into the first pack, `guidance-architecture-lenses`, adding Mark Richards in the process.

## Why

Projects that share an architecture currently re-derive it. Every new repo starts with an empty Arche and `/arche-architect` grills every decision from zero, including decisions already made — well — three times before.

The obvious fix is to ship pre-made decisions: seed the new project's `.arche/concepts/` with ADRs harvested from prior projects. That fix is wrong, for two reasons that turn out to be the same reason.

**It corrupts the Arche's central claim.** The Arche captures *institutional context* — what this organization decided, what its SMEs know, what its customers require. A borrowed ADR is neither institutional nor project-specific. Its `generated.by` names an actor from another project; its `verified` means nothing here; its `status: stable` asserts an agreement nobody in this repo ever made. The agent will then cite it as settled. An inherited decision that was never re-confirmed is worse than no decision.

**It transfers the conclusion and drops the reasoning.** A project ADR reads *"Postgres with a transactional outbox, because we already run Postgres and can't justify a broker for three consumers."* Generalize by stripping the project-specific parts and you get "use the outbox pattern" — precisely the context-free best-practice statement that *Fundamentals of Software Architecture* spends a book arguing does not exist. The rationale is the transferable part, and stripping context is what destroys it.

Both problems dissolve under one move: **generalizing should convert context into conditions, not delete it**, and the result should live outside the Arche entirely.

```markdown
## Applies when
- Single relational store, and the write and the publish must not diverge.
- No transactional publish available from your broker.

## Doesn't apply when
- Your broker supports transactional publish.
- You can tolerate lost events.
```

That is the difference between a starter template and an experienced architect. An architect does not say "use the outbox." They say when it is right and when it is not. What a new project inherits is not old answers but pre-loaded judgment: `/arche-architect` grills against a trade-off space it no longer has to reconstruct, and the ADR that comes out is genuinely this project's, with `sources:` pointing at the guidance that informed it.

The pattern already exists in this repo, unnamed. `arche-architect/references/LENSES.md` and `devbox-add/references/CATALOG.md` are both durable general knowledge trapped inside a single skill, un-installable and un-citable. Two guidance packs already written.

## Decisions

| # | Decision | Choice |
|---|---|---|
| 1 | Relationship to the Arche | **Fully separate.** Guidance never enters `./.arche/`. The Arche cites packs via `sources:`; it does not absorb them. |
| 2 | Packaging | **Skill + OKF bundle in one directory.** `SKILL.md` is the relevance trigger; `bundle/` holds the citable content. |
| 3 | Distribution | **The existing installer.** `npx skills add justinfinch/skills --skill guidance-outbox`. No new CLI. |
| 4 | Page type | **New OKF type `Guidance`,** not a reuse of `Concept`. |
| 5 | Layout | **Flat, prefix-namespaced.** `skills/guidance-<topic>/`, no category directory. |
| 6 | Authoring | **`write-guidance`,** in the `write-*` family, deliberately not `guidance-write`. |
| 7 | First pack | **`guidance-architecture-lenses`,** extracted from `arche-architect`, as the design's own test. |

Decision 1 is load-bearing. An earlier draft kept borrowed pages inside `.arche/` and marked them `inherited_from:` with `status: draft` to stop them masquerading as local decisions. Moving the boundary removes the need for the marking entirely — the separation does the work the stamping was papering over. Every subsequent decision follows from it.

## Pack anatomy

```
skills/guidance-outbox/
  SKILL.md              # relevance trigger + "cite the bundle in your ADR"
  bundle/
    index.md
    concepts/
      transactional-outbox.md
      alternatives-to-outbox.md
```

`SKILL.md` is thin by design: frontmatter carrying the trigger `description`, and a short instruction to read the bundle and cite it. It is the doorbell, not the content. The substance lives one directory down where it has frontmatter, a version, and an identity worth citing — no duplication between the two.

A pack may hold several `Guidance` pages under one trigger. "Monorepo guidance for TypeScript" is really workspace-tool choice, build orchestration, and versioning as three pages that travel together.

### The `Guidance` type

A new first-class OKF type rather than a reuse of `Concept`. OKF §11 explicitly forbids consumers rejecting a bundle over unknown types, so it costs nothing, and the shape genuinely differs: a `Concept` asserts what something *is*, a `Guidance` asserts *when a technique is the right call*. The same reasoning promoted ARD/SAD/ADR to first-class types in `SCHEMA.md`.

Body sections, in order:

| Section | Holds |
|---|---|
| Technique | What the thing is, in a few sentences |
| Applies when | The conditions under which it is the right call |
| Doesn't apply when | The conditions under which it is not — **required, non-empty** |
| Trade-offs | What it buys, and what it costs to buy it |
| Failure modes | What actually breaks, operationally |
| Alternatives considered | The other options and when each wins |

`stale_after` earns its keep at pack granularity. An outbox pack is good for years; a TypeScript monorepo tooling pack rots in eighteen months. OKF already has the field to say so, and `/arche-lint` already knows how to read it.

Two conformance notes, both verified against `tools/okf_conformance.py`. `Guidance` being a type no consumer recognizes is safe: §11 forbids rejecting a bundle over unknown `type` values, and the checker's own docstring names that as something it must never flag. And packs carry **no `log.md`** — a pack's changelog is its git history, and §11 forbids rejecting a bundle for a missing index or log. `index.md` is kept anyway, for progressive disclosure in multi-page packs.

### Example

```markdown
---
type: Guidance
title: Transactional outbox
description: Deliver cross-context events atomically with the state change that caused them.
status: stable
stale_after: 2028-01-01
sources: [...]
---

## Technique
Write the event to a table in the same transaction as the state change; a relay
polls and publishes.

## Applies when
- Single relational store, and the write and the publish must not diverge.
- No transactional publish available from your broker.
- Consumer count low enough that a broker isn't yet justified.

## Doesn't apply when
- Your broker supports transactional publish (Kafka txns, ASB sessions).
- You can tolerate lost events — then just publish and move on.

## Trade-offs
Buys atomicity. Costs at-least-once semantics (consumers must be idempotent),
a relay process to operate and monitor, and outbox-table growth needing a reaper.

## Failure modes
Relay lag under write bursts. Reaper deleting unpublished rows. Ordering
guarantees people assume but the poller doesn't provide.

## Alternatives considered
Listen-to-yourself, CDC/Debezium, 2PC — with when each wins.
```

## Naming convention

Four prefixes, where the prefix says what *kind* of thing it is. This matters once skills install flat alongside other people's.

| Prefix | Kind |
|---|---|
| `arche-*` | Workflows that act on the repo's Arche |
| `devbox-*` | Workflows that act on the repo's dev environment |
| `guidance-*` | Knowledge that is consulted and cited; never runs |
| `write-*` | Tools that author the other kinds |

Flat layout, no category directories. The agent-skills spec requires `name` to match the parent directory name, so a nested `skills/guidance/guidance-outbox/` would say "guidance" twice; the prefix alone is sufficient and matches how this repo already works.

`guidance-`, not a coinage. `arche` earns its Greek because it names a genuinely novel concept. Guidance packs are not novel — they are guidance. A second obscure word would cost a second etymology to explain and buy nothing.

`write-guidance` stays in the `write-*` family rather than becoming `guidance-write`, so the authoring tool is not interleaved alphabetically among a dozen packs that behave nothing like it. The article mismatch with `write-a-skill` is accepted; renaming a published skill costs more than the inconsistency does.

## Integration with `arche-architect`

Smaller than expected, which is the point. A pack's `SKILL.md` description *is* its relevance trigger, so the agent loads it mid-grill exactly as it loads any skill. No registry, no enumeration, no assumptions about where skills were installed.

Two edits to `arche-architect/SKILL.md`:

1. **Phase 4, ADR writing** — if a guidance pack informed a decision, cite it in the ADR's `sources:`, so the rationale trail survives past the conversation.
2. **Phase 3, the grill** — when a decision area has no pack covering it, say so. That is the gap signal.

The gap signal closes the loop:

```
arche-architect consumes packs
        │
        ├─→ notices "no guidance covers X"
        ↓
write-guidance authors or extracts the pack for X
        ↓
next project's architect session arrives pre-loaded
```

That loop is the original goal — projects not starting from scratch — running on transferable judgment rather than transplanted decisions.

## `write-guidance`

Three modes, one discipline.

- **Extract** — given one or more existing project Arches and their repos, find techniques that recur under different names, separate technique from project particulars, and convert those particulars into `Applies when` conditions rather than deleting them. Cite the source projects as evidence.
- **Author** — greenfield on a topic. Interview-driven, same output shape.
- **Revise** — a pack hit `stale_after`, or reality moved. Re-grill, rewrite the whole `generated` mapping, mark superseded claims rather than silently overwriting.

### Lenses as attackers

`arche-architect` uses lenses to help you *design*. `write-guidance` uses the same roster to *attack what you have written*, because the failure mode of guidance is writing down what you happened to do and calling it universal.

| Lens | Attack |
|---|---|
| Nygard | "Your Failure modes section has two entries. What actually pages someone at 3am?" |
| Ford | "Under what future does this stop being right? That's your `stale_after`." |
| Helland | "You've assumed a consistency model without stating it." |
| Hohpe | "This presumes a particular integration shape. Say which." |
| Evans | "Is that your project's vocabulary, or the domain's?" |
| Richards | "You recommended it without naming what it costs." |

### The counter-case rule

**No recommendation ships without its counter-case.** The skill refuses to file a pack whose `Doesn't apply when` section is empty. If you cannot articulate when the technique is wrong, you have not extracted guidance — you have written a testimonial.

### Sanitization

Extract mode draws on real projects. Evidence like *"decided in project-a, project-b"* is fine in a private pack and a leak in a public one. Since this repo is public, extraction sanitizes by default: cite the *shape* of the evidence — "two internal services, roughly five consumers each" — never the client or repo name. The user can opt back in per pack.

`write-guidance` owns its own templates (`guidance.template.md`, `pack-skill.template.md`), consistent with the rest of the library.

## Adding Mark Richards

`arche-architect/SKILL.md` Phase 3 already reads *"**Patterns and trade-offs** (Fowler, Richards)"*, but `LENSES.md` defines twelve lenses and Richards is not among them. The workflow cites a lens the roster never defines. This fixes an existing inconsistency rather than merely growing the panel.

His territory is unclaimed. Ford holds evolutionary architecture and fitness functions; Newman holds service boundaries; Bass holds the quality-attribute taxonomy. Nobody holds **style selection and granularity** — squarely Richards, across *Fundamentals of Software Architecture* (with Ford) and *Software Architecture: The Hard Parts*.

```markdown
## Mark Richards — architecture styles, granularity, and explicit trade-offs

**Pushes on:** deliberate style selection (layered, pipeline, microkernel,
service-based, event-driven, space-based, microservices) and what each buys;
granularity as distinct from boundaries — disintegrators vs. integrators;
ranking driving characteristics to a handful; refusing any recommendation
that doesn't state what it costs.

**Trigger cues:**
- A style is in play implicitly ("we'll do microservices") → ask which style
  this is and which characteristics drove that choice, not the other way round.
- Services keep getting smaller → ask for the disintegrator forcing the split
  and the integrator arguing against it.
- More than about seven driving characteristics are named → force a ranking;
  everything prioritized means nothing is.
- An option is recommended without its cost → "there are no best practices" —
  name what you're giving up, explicitly.
```

Newman and Richards are the pairing most likely to blur, and the distinction is worth stating where both appear: **Newman asks where the seam belongs; Richards asks how small is too small.** They disagree often, which makes them productive to surface together.

Richards is also the natural patron of `write-guidance` itself — the `Applies when / Doesn't apply when / Trade-offs` page shape *is* Richards and Ford's trade-off analysis.

## First pack: `guidance-architecture-lenses`

`LENSES.md` is already durable, general, transferable knowledge, trapped inside one skill. Extracting it is `write-guidance`'s first extraction, performed on content already trusted. If the format cannot absorb `LENSES.md` cleanly, the format is wrong and that surfaces immediately.

The pack ships with thirteen lenses — the existing twelve plus Richards — so the first content change made *through* the new shape is a real one. Both `arche-architect` and `write-guidance` then depend on the pack rather than one skill owning the file the other needs.

## Non-goals

- **Organizational architecture governance.** No mandates, no conformance gates, no deviation-approval workflow. Considered and rejected: better tools exist for that, and it would drag a deliberately simple mechanism into ARB territory.
- **A dedicated CLI.** `npx arche add` was the original framing; `arche`, `arches`, `arche-cli`, and `create-arche` are all taken on npm, and the fetch step is the cheap 20% of the work anyway. The existing skills installer covers it.
- **Seeding `.arche/` with borrowed ADRs.** See Decision 1.
- **An upgrade or pin protocol for packs.** Packs are git-versioned; re-installing gets the current version. Revisit only if drift proves painful in practice.
- **Migrating `devbox-add/references/CATALOG.md`.** It is a guidance pack in spirit, but it is not architectural and it is not load-bearing for this design. Later, if ever.

## Success criteria

1. `npx skills add justinfinch/skills --skill guidance-architecture-lenses` installs a working pack.
2. `bundle/` passes `tools/okf_conformance.py`.
3. An `/arche-architect` session loads a pack unprompted, mid-grill, and the resulting ADR carries the pack in `sources:`.
4. An architect session with no relevant pack emits the gap signal.
5. `write-guidance` refuses to file a pack with an empty `Doesn't apply when`.
6. `arche-architect` and `write-guidance` both read the lenses from the pack; neither owns the file.
