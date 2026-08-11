---
name: arche-query
description: Answer a question using the project's Arche at ./.arche/ — institutional context (business, SME, ARB decisions, research) the code doesn't carry. Reads index.md, walks to the relevant pages, synthesizes a cited answer, optionally files it back as queries/<slug>.md. Use when the user asks something answerable from their Arche; says "query the Arche" / "what does the Arche say about X" / "take a look at our/the Arche" / "based on / given our Arche"; asks a question after ingesting sources; OR is about to plan, design, scope, brainstorm, set up a dev environment, tooling, or dependencies, or make any setup decision in a repo with a ./.arche/ that should be grounded in domain, architecture, or prior-research context — surfacing relevant ADRs, constraints, or prior research first. This includes being invoked from inside another skill (e.g. devbox-init, or any planning skill) whose instructions say to "look at the Arche" — surface the pages via this skill rather than reading ad hoc.
---

# arche-query

Answer a question from the project Arche.

## When this fires

Beyond direct "query the Arche" questions, treat this skill as the **cold-start orientation step** for any work in a repo that has a `./.arche/`:

- A user instruction to "take a look at our Arche", "based on the Arche", or "given our Arche" — even when paired with an action ("…and set up X") — is a trigger. Run this skill, then proceed to the action with the surfaced context.
- A planning / design / scoping / brainstorming step, or a setup decision (dev environment, tooling, dependencies) — surface relevant ADRs, constraints, and prior research *before* that step runs.
- **Invoked from inside another skill** (e.g. `devbox-init`, or any planning skill) whose own instructions say to "look at the Arche": satisfy that instruction by invoking this skill, not by reading Arche pages ad hoc. This skill does not replace the host skill's planning/brainstorming/TDD work — it only feeds grounded context into it, then control returns to the host.

## Preflight

1. Verify `./.arche/SCHEMA.md` and `./.arche/index.md` exist. If either is missing, tell the user to run `/arche-init` and `/arche-ingest` first and stop.
2. Read `./.arche/SCHEMA.md` so you cite and link in the project's house style.
3. Read `./.arche/index.md` — this is the entry point. Use it to choose which pages to read next.

## Workflow

1. **Pick candidate pages.** From the index, list the entities/concepts/queries plausibly relevant to the question. Aim for high recall — better to read one page too many than miss one. If nothing in the index looks relevant, say so and recommend an `/arche-ingest`; do not fabricate.
2. **Read the candidates.** For each candidate page, read the full file. Note the sources cited at each claim — you may need to read source summaries too if the question hinges on provenance.
3. **Synthesize an answer.** Inline-cite every non-trivial claim with **both** the Arche page that synthesizes it and the underlying source page: `... per [Concept Name](../concepts/foo.md) citing [Source Title](../sources/bar.md).` Provenance traces to the original source, not just the synthesis layer. If a claim is supported by multiple sources, cite the strongest one; the others can be implied by the Arche page's own `sources:` list.
4. **Flag gaps.** If the Arche doesn't fully answer the question, say what's missing and suggest a source to ingest. Do not guess past the Arche's coverage.
5. **Architecture gap signal.** When the question is framed for building a feature and the design isn't settled in the Arche, surface that gap before any spec/plan/implementation work proceeds:
   - Find architecture pages by filtering frontmatter `type` for `Architecture Requirements Document`, `Solution Architecture Document`, or `Architecture Decision Record`. Do not rely on the `adr-`/`sad-`/`ard-` prefix as a lookup key — the prefix is a naming habit only, not authoritative.
   - If it's about **how to build / design** ("how should we build X", "what's the right approach for Y", "design a Z") AND no page of those types is relevant, surface that gap: *"The Arche has no decision filed for this. Want to run `/arche-architect` to grill the design and file ARD/SAD/ADRs before building starts?"*
   - Spec-writing, planning, and implementation themselves belong to your dev methodology's own skills (spec-kit, superpowers, your own) — this skill only **grounds** them. So when those skills run, feed them the surfaced decisions/constraints/research; don't reach for an Arche spec or plan artifact (there is none).
   - Suggest; do not auto-invoke. Recommend the architecture gap first — a feature built on an undecided design is the costliest gap to leave open.
6. **Offer to file the synthesis.** If the answer is non-trivial and reusable, ask: "Want me to file this as `queries/<slug>.md`?" Default: do not file unless asked or unless the question itself was framed as an Arche investigation.

## Trust surfacing

Trust tiers only carry information when tiers differ. In an Arche where nobody signs off, every page is `unverified`, and reporting that on every answer is noise that trains the user to ignore it.

So this is **gated on adoption**:

1. Before answering, check whether **any** page in the Arche carries a `verified` key.
2. **If none do** — say nothing about trust. Do not mention tiers, do not caveat the answer, do not suggest sign-off. The feature is invisible until it is used.
3. **If at least one does** — note the tier of the pages the answer rests on, briefly, after the answer:

   ```
   Trust: 2 of the 5 pages cited are human-reviewed; concepts/adr-billing.md is unverified.
   ```

Derive tiers per SCHEMA.md §5.3: no `verified` → unverified; `verified` by non-`human:` actors only → machine-confirmed; `verified` by a `human:` actor → human-reviewed.

Separately and **always** — never gated on the check above: if a cited page has `status: deprecated` or a `stale_after` date on or before today, say so. That is a staleness fact, not a trust tier.

## Filing a query back

If the user says yes:

1. **Create the page.** Write `.arche/queries/<slug>.md` using this skill's [query.template.md](assets/query.template.md) as the layout: `type: Query`, `title`, `description` (one sentence — feeds index.md glosses), today's date, `generated: { by: arche-query/<model-id>, at: <ISO 8601 UTC> }`, `status: stable`, and `sources:` as a list of mappings (stable `id` + required `resource`, never a bare path string) for every Arche page and source you cited. Never write `verified` — that's human sign-off only, via `/arche-lint`.
2. **Write the body.** Per template: the question as asked, the answer with citations preserved, the pages consulted and what each contributed, and any gaps left open.
3. **Update the indexes.** Add an entry under Queries in both `queries/index.md` and the root `index.md`, using the page's `description` as the gloss.
4. **Insert into `log.md`.** Insert a `- **Query**: …` bullet under today's `## YYYY-MM-DD` heading at the top of `log.md`, below `# Arche history` — reuse today's heading if one is already present, otherwise create it. Not at the end of the file — `log.md` is newest-first.

## Discipline

- Citations are mandatory — every non-obvious claim needs a link to the Arche page that synthesizes it AND the underlying source page. Uncited claims should not appear; if you'd write one, you don't know enough from the Arche and should flag the gap instead.
- Prefer answers grounded in concept/entity pages over raw source summaries — concepts and entities exist precisely to be the synthesis layer.
- Do not modify any Arche page during a query unless you're filing the synthesis back. Queries are read-mostly.

## Output

A direct answer to the user's question, with inline citations. No preamble.
