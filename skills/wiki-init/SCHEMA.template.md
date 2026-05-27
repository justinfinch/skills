---
type: schema
created: {{DATE}}
updated: {{DATE}}
---

# LLM Wiki Schema

This file tells the LLM how to maintain `./wiki/`. The operation skills (`/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-brainstorm`) read it before acting. Keep it short and authoritative — when conventions change, edit this file rather than the skills.

Based on Andrej Karpathy's LLM Wiki pattern: humans curate, the LLM maintains.

## Three layers

1. **Raw** — immutable source files stored in `raw/`. PDFs, transcripts, downloaded articles, pasted text saved as `.md`. The human (or `/wiki-ingest`) drops files here; the LLM reads them but never modifies them. This is the audit trail.
2. **Wiki** — markdown pages the LLM owns: source summaries (which cite back into `raw/`), entity pages, concept pages, query-result pages, and brainstorm pages.
3. **Schema** — this file. The LLM-readable contract that keeps the wiki coherent.

`raw/` doubles as a drop zone: dragging a file into `raw/` is the capture step. Processing is a separate step (`/wiki-ingest`), so capture stays frictionless.

## Page types

| Type       | Path                     | Purpose                                                                  |
| :--------- | :----------------------- | :----------------------------------------------------------------------- |
| raw        | `raw/<filename>`         | The actual source file (PDF, MD, transcript). Immutable. Not summarized in-place. |
| source     | `sources/<slug>.md`      | LLM-written summary + key claims for one raw file (or external URL)      |
| entity     | `entities/<slug>.md`     | A person, org, system, place — facts aggregated across sources            |
| concept    | `concepts/<slug>.md`     | An idea, pattern, or technique — explanation + examples                  |
| query      | `queries/<slug>.md`      | A filed-back synthesis from a `/wiki-query` worth keeping                |
| brainstorm | `brainstorms/<slug>.md`  | Captured ideation session: full idea inventory, themes, technique narrative; cites concept/entity pages and may be cited back by them |

## Slug rules

- Kebab-case, ASCII only, no dates in filename.
- Stable: prefer renaming via redirect (leave a stub pointing to the new file) over deleting.
- Brainstorms re-run on the same topic use `-session-N` suffixes (e.g., `auth-rewrite.md`, then `auth-rewrite-session-2.md`). Date stays in frontmatter only.

## Page frontmatter

Every page (except files in `raw/`, which are not wiki pages) starts with YAML frontmatter:

```yaml
---
type: source | entity | concept | query | brainstorm
title: Human-readable title
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [sources/foo.md]   # entities/concepts/queries/brainstorms cite their sources
raw: raw/foo.pdf            # source pages only — points to the raw file if one exists
url: https://...            # source pages only — canonical URL if web-based
---
```

For a source page, at least one of `raw:` or `url:` must be set. If both: `raw:` is the snapshot, `url:` is the canonical location.

## Cross-linking

- Use relative markdown links: `[Title](../entities/foo.md)`. Do not use `[[wikilinks]]`.
- Every entity and concept page lists its sources in the `sources:` frontmatter array AND links to them inline at the point of claim.
- Source pages link out to the entities and concepts they touch (in a `## See also` section).

## index.md

The catalog. Read first when answering queries. Organized by section: Sources, Entities, Concepts, Queries, Brainstorms. Each entry: bullet with title, one-line gloss, link, tags.

Append new entries on ingest. Never remove without leaving a redirect note.

## log.md

Append-only chronological record. Entry format:

```
## [YYYY-MM-DD] <op> | <title>
- pages touched: path1.md, path2.md
- notes: one-line summary
```

Ops: `ingest`, `query`, `lint`, `manual` (human edit), `init`, `brainstorm`.

## Operations summary

- **ingest**: place the raw file in `raw/` (or capture a URL snapshot there) → write a summary page in `sources/` linking back to `raw/` via the `raw:` field → update index → revise affected entity/concept pages → append log entry. Touch as many pages as the source warrants; 10–15 is normal.
  - **Batch mode**: `/wiki-ingest` can also process every file in `raw/` not yet referenced from any `sources/` page — useful after dropping several files in at once.
- **query**: read index → read relevant pages → answer with inline citations. If the synthesis is reusable, file it as `queries/<slug>.md` and update index + log.
- **lint**: scan for contradictions, stale dates, orphan pages (no inbound links), orphan raw files (raw file with no source page citing it), broken links, frontmatter drift, gaps in coverage. Report findings; do not auto-fix without confirmation.
- **brainstorm**: facilitated ideation session. Reads wiki context (relevant entity/concept/query/prior-brainstorm pages) → runs interactive ideation with the user → files the session as `brainstorms/<slug>.md` with the full idea inventory → promotes user-selected top ideas to concept or entity pages with citations back → updates index and log. Aims for 100+ ideas before organization.

## Editing rules for the LLM

- Update `updated:` frontmatter on every page touched.
- Never delete a claim without leaving a `~~strikethrough~~` and a note in log.md citing the contradicting source.
- Prefer adding to existing pages over creating near-duplicates. If unsure whether something is a new entity or a section of an existing one, ask.
- Quote sparingly. Paraphrase and cite.

## Conventions the human controls

Edit this section freely; the LLM respects it:

- **Tone**: neutral, dense, no filler.
- **Length**: source summaries ≤ 400 words, entity/concept pages grow as needed.
- **Tags**: free-form, lowercase, kebab-case.
