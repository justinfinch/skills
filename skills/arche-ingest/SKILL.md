---
name: arche-ingest
description: Ingest a source into the project's Arche at ./.arche/. The Arche captures **institutional context** (business domain, SME knowledge, ARB-style architectural decisions, research) — not code documentation. Accepts a URL, a file path, pasted text, OR — with no argument — processes every file in ./.arche/raw/ not yet referenced by a source page (batch mode). Snapshots the raw input to ./.arche/raw/, writes a source-summary page, updates index.md, revises affected entity and concept pages, and inserts a log entry — following the conventions in ./.arche/SCHEMA.md. Use when the user provides a source to add to an Arche, says "ingest", "add to Arche", "remember this article", "process the raw folder", or shares an article/paper/PDF/transcript/SME-interview/ADR they want filed.
---

# arche-ingest

Add one or more sources to the project Arche.

## Preflight

1. Verify `./.arche/SCHEMA.md` exists. If not, tell the user to run `/arche-init` first and stop.
2. Read `./.arche/SCHEMA.md` end to end. The schema is authoritative — follow its slug rules (including the "Slug derivation" subsection), page-type definitions, frontmatter shape, cross-linking rules, contradiction marker convention, and log format.
3. Read `./.arche/index.md` so you know what entities and concepts already exist (you'll be linking into them and possibly extending them).
4. Read this skill's own page templates so new pages follow the canonical layout: [source.template.md](assets/source.template.md), [entity.template.md](assets/entity.template.md), [concept.template.md](assets/concept.template.md).

## Dispatch

- **Explicit argument** (URL, file path, pasted text): single-source ingest. Continue to Workflow.
- **No argument**: batch mode. List every file in `./.arche/raw/` that no existing `sources/*.md` page references via `resource:` or a `sources[].resource` entry. Show the user the list and ask which to ingest (default: all). Then run the Workflow once per file, in order.

## Workflow (per source)

1. **Land the raw file in `./.arche/raw/`.** Derive the slug per SCHEMA's "Slug derivation" rules.
   - File path → copy (don't move; leave the original alone) to `raw/<slug>.<ext>`. If the incoming extension is `.md`, save the copy as `.txt` instead — same reason as the pasted-text rule below.
   - URL → fetch the page, convert to markdown, save as `raw/<slug>.txt`, never `.md` — same reason as the pasted-text rule below. The canonical URL is not recorded in the snapshot; it goes in the source page's `resource:`.
   - Pasted text → save verbatim to `raw/<slug>.txt`, never `.md`, with a header noting the date and source description. Every `.md` file in the bundle must carry frontmatter (§11 rule 1), and `raw/` files are immutable, so a `.md` snapshot of pasted text would be permanently non-conformant — `.txt` sidesteps the rule entirely.
   - On slug collision: if the incoming file is byte-identical to the existing one, skip ingest and tell the user it's already captured. Otherwise append `-2`/`-3` to the slug (do not silently overwrite).
2. **Discuss with the user first** (one short message): name the 3–5 key points you saw and the entities/concepts you plan to touch. Stop and let them redirect before writing anything. This is the "discuss key points with you" step from Karpathy's pattern. Skip the discussion step in batch mode unless the user asked for it explicitly.
3. **Write the source summary** at `.arche/sources/<slug>.md` using this skill's [source.template.md](assets/source.template.md) as the layout.
   - Set `resource:` to the canonical URL for a web source, or to `../raw/<slug>.<ext>` — a path relative to the page containing it, where `<ext>` is the extension actually written to `raw/` in step 1, not the incoming one: it is `.txt` whenever the incoming file was `.md`, or the source was a URL or pasted text — for a file-only source. When both exist, `resource:` is the URL and the snapshot becomes a `sources` entry with `id: snapshot`.
   - Write `description:` — one sentence. This is what the directory `index.md` and root `index.md` use as the entry gloss, so it is not optional.
   - Keep the summary within SCHEMA.md's length cap, fill in `## Key claims`, and list every entity/concept page touched under `## See also`.
4. **Update or create entity/concept pages.** For each entity/concept the source touches:
   - If the page exists: add new claims with inline citations to the source page, update the `sources:` frontmatter list.
   - If the page is new: create it using this skill's [entity.template.md](assets/entity.template.md) or [concept.template.md](assets/concept.template.md) as the layout, with full frontmatter and at least the claims this source supports. Write `description:` here too — same reason as step 3.
   - `sources` is a list of mappings, each with a stable `id` and a required `resource`. Derive the `id` from the target's slug stem — ids are the join key for footnote citations and must survive list reordering, since a positional reference misattributes silently the moment an agent reorders the list. Attribute individual claims to external sources with markdown footnotes whose label is the `sources[].id`.
   - Write `generated: { by: arche-ingest/<model-id>, at: <ISO 8601 UTC> }` on every page you create or meaningfully change. Never write `verified` — that is human sign-off only, via `/arche-lint`.
   - Do not duplicate facts already present — extend, don't restate.
5. **Update `index.md`.** Update both the directory's own `index.md` and the root `index.md`. Entries are `* [Title](path) - description.` using the target page's `description` field. Add the new source under Sources, and any new entities/concepts under their sections (create the section if missing).
6. **Insert into `log.md`.** Insert the log entry as the first bullet under today's `## YYYY-MM-DD` heading; if today's heading is absent, create it immediately above the topmost existing date heading. Never append at the end of the file and never place the bullet outside a date heading, since `log.md` is newest-first. Format: a `- **Ingest**: …` bullet listing every page touched (including the new `raw/` file) and one sentence on what the source contributed.

## Discipline

- Touch as many pages as the source warrants. A rich source legitimately updates 10–15 pages; a thin one might update 2.
- Cite at the point of claim, not just in frontmatter.
- If the source contradicts an existing claim, do NOT silently rewrite. Use `~~strikethrough~~` on the old claim, add the new one with an inline `[source link](...)` citation in the same paragraph (this is what marks the strikethrough as resolved), and make sure the log entry's prose contains the prefix `contradiction —` (per SCHEMA's contradiction marker convention) so `/arche-lint` can find it.
- Rewrite the whole `generated` mapping — both `by` and `at` — on every page you meaningfully edit, so `by` names whoever wrote the content that is there now. Never touch it on pages you only read.
- If you're unsure whether to create a new entity or extend an existing one, ask the user — slug churn is expensive.

## Output

End with a one-line summary: `Ingested <title> → N pages updated (list them).` Nothing longer.
