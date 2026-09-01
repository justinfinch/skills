---
name: guidance-{{SLUG}}
description: >-
  {{WHAT}}. Use when {{TRIGGERS}}. {{SCOPE_EXCLUSION}}.
---

<!-- AUTHORING NOTES — delete this block when you file the pack.

`description` is the activation surface. It is the only part of the skill an
agent sees when deciding whether to load it, so spend every character on WHAT
the pack covers and WHEN to load it — never on how to use it. Usage
instructions live in the body below, which loads only after activation; a
sentence that would only help an agent that has already loaded the pack
belongs in the body, not here.

Three slots, three rules:

- {{WHAT}} — the decisions this pack covers, in the domain's own vocabulary.
  Matching is substantially lexical, so include the topic's literal
  vocabulary; the pattern names here double as trigger keywords, and an agent
  whose user asks about one of them by name matches directly.
- {{TRIGGERS}} — the tasks, decision moments, and literal words a user would
  say. Include the trigger for the user who doesn't know the topic's name yet:
  the upstream decision moment or observable symptom ("starting a greenfield
  service", "the same term means different things to different teams"), not
  just the jargon.
- {{SCOPE_EXCLUSION}} — what this pack deliberately does not cover. For a
  knowledge pack a false-positive load costs more than a false-negative, and
  the exclusion is itself signal. Naming another pack that owns an adjacent
  decision belongs here.

`description` is a folded block scalar (`>-`) on purpose. A plain YAML scalar
breaks on a colon followed by a space, and "Outbox: deliver events atomically"
is exactly the phrasing that goes into {{WHAT}} or {{TRIGGERS}}. Folded, the
value is one line of prose to any YAML parser with no escaping to get wrong.
Keep the `>-`, and keep the folded value under the spec's 1024-character cap.

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
   the rationale outlives the conversation. In an Arche, that record is the
   ADR and the citation goes in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
