---
name: guidance-architecture-lenses
description: A roster of twelve named architects — Fowler, Evans, Vernon, Nygard, Hohpe, Newman, Ford, Helland, Vogels, Bass, Beck, Martin — with the territory each owns and the trigger cues that should surface them, plus guidance on when driving a design conversation through named lenses is the right technique and when it is theatre. Consult when running or reviewing an architecture design session, attacking written architectural guidance, or when a design question needs a viewpoint you would not have thought to apply. Read `bundle/` and cite the pages that inform a decision in that decision's record. This pack is knowledge, not a workflow: it decides nothing on its own and writes nothing.
---

# guidance-architecture-lenses

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle.

- [Interrogating a design through expert lenses](bundle/concepts/expert-lens-interrogation.md)
  — the technique, with the conditions it holds under and the ones it doesn't.
- [The architect lens roster](bundle/concepts/lens-roster.md) — the twelve,
  with trigger cues.

## How to use this pack

1. Read the technique page first, and check its **Doesn't apply when** against
   the conversation you are actually in. A design panel run where it doesn't fit
   is worse than no panel.
2. Load the roster when a cue fires, not preemptively. You are looking for the
   lens whose territory the question already sits in.
3. When two lenses disagree — Vernon and Helland on consistency is the
   recurring case — surface both and let the user pick. Do not arbitrate
   silently.
4. If a lens shaped a decision, cite this pack in that decision's record so the
   reasoning outlives the conversation.

## What this pack is not

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
