---
name: guidance-{{SLUG}}
description: >-
  {{DESCRIPTION}} Consult when {{TRIGGER}}. Read `bundle/` and cite the pages
  that inform a decision in that decision's record — in an Arche, the ADR's
  `sources:`. This pack is knowledge, not a workflow — it decides nothing on
  its own and writes nothing.
---

<!-- AUTHORING NOTES — delete this block when you file the pack.

`description` is a folded block scalar (`>-`) on purpose. A plain YAML scalar
breaks on a colon followed by a space, and "Outbox: deliver events atomically"
is exactly the phrasing that goes into {{DESCRIPTION}} or {{TRIGGER}}. Folded,
the value is one line of prose to any YAML parser with no escaping to get
wrong. Keep the `>-`.

In "How to use this pack", items 2, 3 and 4 are fixed boilerplate — they carry
the guidance discipline (check the conditions, cite the page, never drop the
trade-off) and every pack keeps all three, in substance. Item 1 is the
pack-specific one: replace it with how *these* pages are actually read, since a
roster is loaded when a cue fires while a technique page is walked condition by
condition. Add further pack-specific items and reorder freely — just don't drop
2, 3 or 4. -->

# guidance-{{SLUG}}

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages, plus any supporting `Concept` pages the topic
needs (a roster, a taxonomy, a comparison table).

## How to use this pack

1. Read [bundle/index.md](bundle/index.md), then the pages relevant to the
   decision actually in play.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as `guidance-{{SLUG}}/<path-within-bundle>`, so
   the rationale outlives the conversation.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

## What this pack is not

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
