---
name: wiki-brainstorm
description: Facilitate a structured brainstorming session grounded in the project's LLM wiki at ./wiki/. Loads relevant entity/concept/query pages as agent memory before ideation, runs interactive facilitation across 60+ creativity techniques (Yes-And, First Principles, SCAMPER, Six Hats, Reverse Brainstorming, Cross-Pollination, etc.) with anti-bias domain pivots and energy checkpoints, then files the session as brainstorms/<slug>.md, promotes user-selected top ideas to concept or entity pages, and appends a `brainstorm` log entry. Use when the user wants to brainstorm a topic, ideate, "help me think through X", "explore options for Y", or wants to use prior wiki context as a launchpad for new ideas. Adapted from BMAD-METHOD's bmad-brainstorming skill.
---

# wiki-brainstorm

Run a structured brainstorming session that uses the project wiki as agent memory and writes its outputs back into the wiki.

## Preflight

1. Verify `./wiki/SCHEMA.md` exists. If not, tell the user to run `/wiki-init` first and stop.
2. Read `./wiki/SCHEMA.md` end to end.
3. Check SCHEMA defines a `brainstorm` page type and a `brainstorm` log op. If missing, show the user [SCHEMA-additions.md](SCHEMA-additions.md) and offer to append it. Do not proceed without approval — the operation skills follow the schema.
4. Ensure `./wiki/brainstorms/` exists. If not, create it with a `.gitkeep`.
5. Read `./wiki/index.md`.

## Phase 1: Session setup

1. In one short message, ask the user for **topic**, **goals**, and any **constraints**.
2. **Load wiki context.** Scan `index.md` for entities, concepts, and prior queries plausibly relevant to the topic — aim for high recall. Read each candidate page fully. Also check `./wiki/brainstorms/` for prior sessions on the same or adjacent topic; if any exist, read them — do not re-explore ground already covered.
3. Present the context bundle in one message: `"Here's what the wiki already knows about <topic>: N entities, M concepts, K prior brainstorm(s)."` List them with one-line glosses. Ask: "Use this as context, ignore it, or focus on a subset?"
4. **Pick the slug.** Default: kebab-case of the topic. If `brainstorms/<topic>.md` already exists, use `<topic>-session-2`, `<topic>-session-3`, etc. (per SCHEMA's brainstorm slug rule). Date stays in frontmatter only.

## Phase 2: Choose technique mode

Offer four modes (full prompts in [FACILITATION.md](FACILITATION.md)):

- **User-Selected** — user browses [TECHNIQUES.md](TECHNIQUES.md) and picks.
- **AI-Recommended** — facilitator picks 2–3 based on topic + wiki context. When substantial wiki context was loaded, prefer the techniques flagged as wiki-leveraged in TECHNIQUES.md.
- **Random** — pick a wild card from any category. Good for stuck thinking.
- **Progressive Flow** — sequence across phases: divergent → analogical → convergent.

## Phase 3: Facilitate

Run the chosen technique(s) per [FACILITATION.md](FACILITATION.md). Non-negotiable disciplines:

- **One idea/provocation at a time.** Present, wait for the user, build together. No batch lists.
- **Anti-bias domain pivot every ~10 ideas.** Consciously shift to an orthogonal domain (UX → business → physics → social → ethics → governance → ...). LLMs drift toward semantic clustering; counter it.
- **Inline-cite the wiki when relevant.** When an idea touches a known page: `"this connects to [Concept Foo](../concepts/foo.md) — what if we extended it by..."`. Citations belong in the conversation now and in the brainstorm page later.
- **Energy checkpoint every 4–5 exchanges.** Offer: continue / switch technique / deepen / break. Never auto-conclude.
- **Aim for 100+ collaboratively developed ideas** before suggesting organization. Quantity unlocks quality. Ideas count only when they emerge through dialogue or are accepted/developed by the user.
- **No wiki writes during facilitation.** Capture ideas in-conversation using FACILITATION.md's idea format. All wiki edits batch into Phase 4.

## Phase 4: Organize and promote

Only when the user signals readiness to wrap up:

1. **Cluster** ideas into 3–6 themes; identify breakthrough concepts and cross-cutting threads.
2. **Prioritize** with the user across impact / feasibility / innovation / alignment. See FACILITATION.md.
3. **Write `wiki/brainstorms/<slug>.md`** per SCHEMA. Frontmatter: `type: brainstorm`, today's date, topic, techniques used, total idea count, wiki pages loaded as context. Body: themes with full idea inventory, prioritized top ideas with action plans, technique narrative + creative breakthroughs, and a `## See also` section listing every wiki page touched.
4. **Promote top ideas.** For each user-selected top idea:
   - Extends an existing concept/entity page → append with inline citation to this brainstorm; bump `updated:`; add the brainstorm to that page's `sources:` list.
   - New concept warranted → create `concepts/<slug>.md` with frontmatter, the concept body, and `sources: [brainstorms/<slug>.md]`.
   - If unsure whether to extend or create, ask. Slug churn is expensive.
5. **Update `index.md`.** Add the brainstorm under a `## Brainstorms` section (create the section if missing). Add any new concept/entity pages under their sections.
6. **Append to `log.md`** with op `brainstorm`. List every page touched. Notes line: topic + idea count + count of promoted ideas.

## Discipline

- Wiki is read-only during facilitation. All writes are batched into Phase 4.
- Promote only what the user explicitly picks. The brainstorm page is the home for the full inventory — concept pages stay dense and signal-rich.
- If a prior brainstorm on the same topic exists, the new session must build on it, not duplicate it. Cite it in the new brainstorm's `## See also`.
- If the conversation drifts into question-answer instead of true collaboration, pause and reset to one-idea-at-a-time facilitation.

## Output

End with one line: `Brainstormed <topic> → <N> ideas across <T> techniques, <M> promoted. Filed as brainstorms/<slug>.md.`

## See also

- [TECHNIQUES.md](TECHNIQUES.md) — the 61-technique library
- [FACILITATION.md](FACILITATION.md) — coaching patterns, idea format, energy checkpoints, prioritization framework
- [SCHEMA-additions.md](SCHEMA-additions.md) — text to append to existing `wiki/SCHEMA.md` to register the brainstorm page type

_Adapted from [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)'s `bmad-brainstorming` skill (MIT-licensed)._
