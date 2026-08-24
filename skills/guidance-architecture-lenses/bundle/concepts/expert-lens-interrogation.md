---
type: Guidance
title: Interrogating a design through expert lenses
description: Drive architectural questioning from a fixed roster of named expert viewpoints so coverage is deliberate rather than incidental.
tags: [architecture, method, review]
created: 2026-08-24
generated: { by: claude-sonnet-5, at: 2026-08-24T22:17:02Z }
status: stable
stale_after: 2030-01-01
sources: []
---

# Interrogating a design through expert lenses

## Technique

Walk a design by rotating through a fixed roster of named expert viewpoints,
naming the lens as you apply it. Each lens owns a territory and carries trigger
cues; when a cue fires, you ask that lens's question in that lens's terms. The
roster is [the twelve architects](lens-roster.md).

## Applies when

- The design has genuine trade-offs rather than one obvious answer.
- Coverage matters more than speed — you would rather find the missing
  consistency question now than in production.
- The people in the room share enough vocabulary that "Nygard would ask" is
  shorthand rather than a puzzle, or are willing to learn it as they go.
- You are attacking work already written, where the risk is a blind spot the
  author shares with you.

## Doesn't apply when

- The question is business, customer, market, or regulatory — that is divergent
  ideation and wants a facilitation technique, not an architecture panel.
- The decision is genuinely reversible and cheap. Rotating twelve lenses over
  a two-day-to-undo choice costs more than the choice.
- The roster would be theatre: a room that reads named lenses as affectation
  gets less from them than from the plain question underneath.
- You already know which single territory is in play. Reach for that lens
  directly rather than performing the rotation.

## Trade-offs

Buys deliberate coverage — the questions you would not have thought to ask get
asked, because a lens owns them whether or not they occurred to you — and a
shared vocabulary that compresses long arguments into a name. Costs
conversational overhead, and creates a standing temptation to force a lens onto
a question it does not fit, which produces confident irrelevance.

## Failure modes

Naming the same lens for every question, which means the framing is being forced
rather than found. Impersonation drifting into caricature, at which point the
lens stops carrying information and starts carrying performance. Treating roster
completion as design completion — twelve lenses applied to a problem you never
actually understood is twelve wasted questions. And lens-shopping: rotating
until one of them endorses the answer you already had.

## Alternatives considered

- **Unstructured expert judgment** — wins when a genuine expert in the specific
  territory is in the room. The roster substitutes for expertise; it does not
  beat it.
- **ATAM or a formal scenario-based evaluation** — wins when the decision needs
  a defensible audit trail and there is budget for a multi-day structured
  workshop with real stakeholders.
- **A flat review checklist** — wins for repeated, well-understood classes of
  change. Cheaper and more consistent, but it only ever asks what someone
  already knew to write down.
