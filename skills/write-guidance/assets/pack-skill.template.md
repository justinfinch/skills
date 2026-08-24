---
name: guidance-{{SLUG}}
description: {{DESCRIPTION}} Consult when {{TRIGGER}}. Read `bundle/` and cite the pages that inform a decision in that decision's record — in an Arche, the ADR's `sources:`. This pack is knowledge, not a workflow: it decides nothing on its own and writes nothing.
---

# guidance-{{SLUG}}

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Read [bundle/index.md](bundle/index.md), then the pages relevant to the
   decision actually in play.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite it in that decision's record so the
   rationale outlives the conversation.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

## What this pack is not

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
