---
name: arche-discover
description: Facilitate a structured discovery / ideation session grounded in the project's Arche at ./.arche/ — for **business, domain, customer, market, or regulatory** topics. Loads relevant pages as memory, facilitates across 60+ creativity techniques (Yes-And, First Principles, SCAMPER, etc.) with anti-bias pivots, then files the session as discoveries/<slug>.md, promotes top ideas to concept or entity pages, and inserts a `discovery` log entry. Use when the user wants to explore unknown unknowns about the business, customer, market, or regulatory landscape; surface non-technical strategic options or risks; says "help me think through X" / "explore options for Y" for non-technical topics; or wants to use prior Arche context as a launchpad. NOT for technical architecture (designing systems, choosing patterns, deciding integrations) — use `/arche-architect`, which converges on ARD/SAD/ADR artifacts. NOT for code-implementation brainstorming (refactor / test structure) — use your dev methodology's own skill.
---

# arche-discover

Run a structured discovery / ideation session that uses the project Arche as agent memory and writes its outputs back into the Arche. Scope: business, customer, market, or regulatory topics — the kinds of things that belong in the Arche as institutional context (see `.arche/SCHEMA.md`).

**Out of scope — delegate explicitly:**

- Technical architecture (designing a system, choosing patterns, deciding integrations, writing ADRs) → use `/arche-architect`, which is convergent and produces Architecture Requirements Document, Solution Architecture Document, and Architecture Decision Record pages with senior-architect lenses (Fowler, Evans, Vernon, Nygard, Hohpe, Newman, Ford, Helland, Vogels, Bass, Beck, Martin). If a discovery session here surfaces a strong architectural direction, suggest `/arche-architect` to converge it rather than promoting to an ADR directly.
- Code-implementation brainstorming (how to refactor X, how to test Y) → use your dev methodology's own brainstorming skill.

## Preflight

1. Verify `./.arche/SCHEMA.md` exists. If not, tell the user to run `/arche-init` first and stop.
2. Read `./.arche/SCHEMA.md` end to end.
3. Check SCHEMA defines the `Discovery` page type and has `discovery` in the log ops list. If either is missing, tell the user to run `/arche-lint`, which owns conformance detection and repair, and stop.
4. Ensure `./.arche/discoveries/` exists. If not, create it with a `.gitkeep`.
5. Read `./.arche/index.md`.

## Phase 1: Session setup

1. In one short message, ask the user for **topic**, **goals**, and any **constraints**.
2. **Load Arche context.** Scan `index.md` for entities, concepts, and prior queries plausibly relevant to the topic — aim for high recall. Read each candidate page fully. Also check `./.arche/discoveries/` for prior sessions on the same or adjacent topic; if any exist, read them — do not re-explore ground already covered.
3. Present the context bundle in one message: `"Here's what the Arche already knows about <topic>: N entities, M concepts, K prior discovery session(s)."` List them with one-line glosses. Ask: "Use this as context, ignore it, or focus on a subset?"
4. **Pick the slug.** Default: kebab-case of the topic. If `discoveries/<topic>.md` already exists, use `<topic>-session-2`, `<topic>-session-3`, etc. (per SCHEMA's discovery slug rule). Date stays in frontmatter only.

## Phase 2: Choose technique mode

Offer four modes (full prompts in [FACILITATION.md](references/FACILITATION.md)):

- **User-Selected** — user browses [TECHNIQUES.md](references/TECHNIQUES.md) and picks.
- **AI-Recommended** — facilitator picks 2–3 based on topic + Arche context. When substantial Arche context was loaded, prefer the techniques flagged as arche-leveraged in TECHNIQUES.md.
- **Random** — pick a wild card from any category. Good for stuck thinking.
- **Progressive Flow** — sequence across phases: divergent → analogical → convergent.

## Phase 3: Facilitate

Run the chosen technique(s) per [FACILITATION.md](references/FACILITATION.md). Non-negotiable disciplines:

- **One idea/provocation at a time.** Present, wait for the user, build together. No batch lists.
- **Anti-bias domain pivot every ~10 ideas.** Consciously shift to an orthogonal domain (UX → business → physics → social → ethics → governance → ...). LLMs drift toward semantic clustering; counter it.
- **Inline-cite the Arche when relevant.** When an idea touches a known page: `"this connects to [Concept Foo](../concepts/foo.md) — what if we extended it by..."`. Citations belong in the conversation now and in the discovery page later.
- **Energy checkpoint every 4–5 exchanges.** Offer: continue / switch technique / deepen / break. Never auto-conclude.
- **Aim for 100+ collaboratively developed ideas** before suggesting organization. Quantity unlocks quality. Ideas count only when they emerge through dialogue or are accepted/developed by the user.
- **No Arche writes during facilitation.** Capture ideas in-conversation using FACILITATION.md's idea format. All Arche edits batch into Phase 4.

## Phase 4: Organize and promote

Only when the user signals readiness to wrap up:

1. **Cluster** ideas into 3–6 themes; identify breakthrough concepts and cross-cutting threads.
2. **Prioritize** with the user across impact / feasibility / innovation / alignment. See FACILITATION.md.
3. **Write `.arche/discoveries/<slug>.md`** using this skill's [discovery.template.md](assets/discovery.template.md) as the layout. Frontmatter: `type: Discovery`, today's date in `created:`, `status: stable`, and `sources:`. Record the pages that grounded the session in `sources` (with stable `id`s) and narrate them in the body's *Context loaded* section — there is no separate `context_pages` key; `sources` is bidirectional for discovery pages, listing both what grounded the session and what the session promoted to (the promoted half fills in after Phase 4 step 4). Write `description:` — one sentence. Write `generated: { by: arche-discover/<model-id>, at: <ISO 8601 UTC> }`. Never write `verified` — that is human sign-off only, via `/arche-lint`. Body: full idea inventory, themes, techniques used, prioritized top ideas, and open questions.
4. **Promote top ideas.** For each user-selected top idea:
   - Extends an existing concept/entity page → append with inline citation to this discovery; rewrite the whole `generated` mapping — both `by` and `at` — so `by` names whoever wrote the content that is there now; add the discovery to that page's `sources:` list; **and** add the page to this discovery's `sources:` list (forward and back).
   - New concept warranted → create `concepts/<slug>.md` from `/arche-ingest`'s [concept.template.md](../arche-ingest/assets/concept.template.md) with `sources: [{ id: <slug>, resource: ../discoveries/<slug>.md }]` — the `resource` is relative to the page containing it, and the page lives in `concepts/`; add the new page to this discovery's `sources:` list.
   - If unsure whether to extend or create, ask. Slug churn is expensive.
5. **Update `index.md`.** Update both `discoveries/index.md` and the root `index.md`. Add the discovery under its section (create if missing) with a one-line gloss — the page's `description`. Add any new concept/entity pages under their sections in both the relevant directory index and the root index.
6. **Insert into `log.md`** with op `discovery`. Insert a `- **Discovery**: …` bullet immediately above the topmost `## YYYY-MM-DD` heading, creating today's heading if it is absent. The bullet's prose names the topic, the idea count, the count of promoted ideas, and every page touched.

## Discipline

- Arche is read-only during facilitation. All writes are batched into Phase 4.
- Promote only what the user explicitly picks. The discovery page is the home for the full inventory — concept pages stay dense and signal-rich.
- If a prior discovery on the same topic exists, the new session must build on it, not duplicate it. Cite it in the new discovery's `## See also`.
- If the conversation drifts into question-answer instead of true collaboration, pause and reset to one-idea-at-a-time facilitation.

## Output

End with one line: `Discovery session on <topic> → <N> ideas across <T> brainstorming techniques, <M> promoted. Filed as discoveries/<slug>.md.`

## See also

- [TECHNIQUES.md](references/TECHNIQUES.md) — the 61-technique library
- [FACILITATION.md](references/FACILITATION.md) — coaching patterns, idea format, energy checkpoints, prioritization framework
- [discovery.template.md](assets/discovery.template.md) — page skeleton this skill writes
