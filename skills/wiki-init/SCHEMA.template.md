---
type: schema
created: {{DATE}}
updated: {{DATE}}
---

# LLM Wiki Schema

This file tells the LLM how to maintain `./.wiki/`. The operation skills (`/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-discover`) read it before acting. Keep it short and authoritative — when conventions change, edit this file rather than the skills.

Based on Andrej Karpathy's LLM Wiki pattern: humans curate, the LLM maintains.

## What belongs here (and what doesn't)

This wiki captures **institutional context that does not live in the code**:

- **Business domain** — customer context, product positioning, market signals, the *why* this product exists.
- **SME knowledge** — subject-matter expert insights, interview transcripts, regulatory/compliance constraints, the things "the senior person in the room" carries in their head.
- **Architectural decisions (ADRs)** — the decision, alternatives considered, rationale, constraints, supersession chain. See [ADRs](#adrs-architecture-decision-records) below.
- **Research** — papers, articles, competitor analyses, prior art relevant to product or architecture.

This wiki **does not** capture:

- Code documentation, API references, module diagrams — those live with the code (`docs/`, doc comments, generated references).
- Per-task plans, in-flight TODOs, debugging notes, commit-by-commit history — those live in PR descriptions, commits, or your dev methodology's working artifacts.
- Generated content (changelogs, dependency lists, build outputs).

**Rule of thumb:** if a question is answered by *"read the code,"* it doesn't belong here. If a question is answered by *"ask the senior architect or product owner what we decided and why,"* it does.

**How it plugs into dev workflows:** the wiki is *consumed* by agentic dev methodologies (superpowers, mattpocock skills, your own) during planning, design, and brainstorming phases — it surfaces ADRs, domain constraints, customer context, and prior research that should inform the work. It is **not** written to by coding sessions. Coding artifacts stay with the code.

## Three layers

1. **Raw** — immutable source files stored in `raw/`. PDFs, transcripts, downloaded articles, pasted text saved as `.md`. The human (or `/wiki-ingest`) drops files here; the LLM reads them but never modifies them. This is the audit trail.
2. **Wiki** — markdown pages the LLM owns: source summaries (which cite back into `raw/`), entity pages, concept pages, query-result pages, and discovery (session) pages.
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
| discovery  | `discoveries/<slug>.md`  | Captured discovery / ideation session (`/wiki-discover`): full idea inventory from a facilitated brainstorming session, themes, technique narrative; cites concept/entity pages and may be cited back by them |

### ADRs (Architecture Decision Records)

ADRs are a **convention layered on concept pages** — not a separate page type. Slug: `adr-<short-decision-name>` (e.g. `adr-session-token-storage`, `adr-event-driven-billing`). Body sections:

1. **Decision** — one paragraph: what was decided.
2. **Context** — what problem prompted it, what constraints applied.
3. **Alternatives considered** — what else was on the table, why each was rejected. (This is the most load-bearing section — the trail of why-not-X matters more than the why-Y over time.)
4. **Consequences** — what this enables, what it costs, what it locks in.
5. **Status** — one of: `proposed` | `accepted` | `superseded`. If `superseded`, set the `superseded_by:` frontmatter field (see below).

Cite sources in the body the same as any other concept page (the discovery session or research that produced the decision, the SME who flagged the constraint, etc.). When an ADR is reversed, do not delete the old page — set `status: superseded` and `superseded_by:` to the new ADR's path. The trail of "we tried X, reversed it after Y" is precisely the institutional memory the wiki exists to preserve.

## Slug rules

- Kebab-case, ASCII only, no dates in filename.
- Stable: prefer renaming via redirect (leave a stub pointing to the new file) over deleting.
- Discoveries re-run on the same topic use `-session-N` suffixes (e.g., `auth-rewrite.md`, then `auth-rewrite-session-2.md`). Date stays in frontmatter only.

### Slug derivation

When generating a slug from a source (URL, file path, or pasted text):

1. Pick a stem: URL → page title or final path segment; file → filename without extension; pasted text → user-supplied title or first heading.
2. Lowercase. Strip accents (NFD then drop combining marks). Replace any non-ASCII or non-alphanumeric character with `-`. Collapse repeated `-`. Trim leading/trailing `-`.
3. On collision in the target directory: if the new raw file is byte-identical to the existing one, treat it as already-ingested and skip; otherwise append `-2`, `-3`, etc.

## Page frontmatter

Every page (except files in `raw/`, which are not wiki pages) starts with YAML frontmatter:

```yaml
---
type: source | entity | concept | query | discovery | schema | index | log
title: Human-readable title
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [sources/foo.md]            # entities/concepts/queries/discoveries cite their sources
raw: raw/foo.pdf                     # source pages only — points to the raw file if one exists
url: https://...                     # source pages only — canonical URL if web-based
status: proposed | accepted | superseded   # ADR concept pages only
superseded_by: concepts/adr-new.md   # ADR concept pages only — when an ADR has been reversed, points to the replacement
---
```

For a source page, at least one of `raw:` or `url:` must be set. If both: `raw:` is the snapshot, `url:` is the canonical location.

`schema`, `index`, and `log` are reserved for the three system files at the wiki root (`SCHEMA.md`, `index.md`, `log.md`). All other pages use one of the content types.

For `discovery` pages, `sources:` is bidirectional: it lists both (a) the wiki pages cited inline during the session AND (b) the entity/concept pages the discovery promoted ideas to. This keeps navigation symmetric with the forward references those pages add back.

## Cross-linking

- Use relative markdown links: `[Title](../entities/foo.md)`. Do not use `[[wikilinks]]`.
- Every entity and concept page lists its sources in the `sources:` frontmatter array AND links to them inline at the point of claim.
- Source pages link out to the entities and concepts they touch (in a `## See also` section).

## index.md

The catalog. Read first when answering queries. Organized by section: Sources, Entities, Concepts, Queries, Discoveries. Each entry: bullet with title, one-line gloss, link, tags.

Append new entries on ingest. Never remove without leaving a redirect note.

## log.md

Append-only chronological record. Entry format:

```
## [YYYY-MM-DD] <op> | <title>
- pages touched: path1.md, path2.md
- notes: one-line summary
```

Ops: `ingest`, `query`, `lint`, `manual` (human edit), `init`, `migrate`, `discovery`.

**Contradiction marker.** When an ingest finds a source that contradicts an existing claim, the log entry's notes line starts with `contradiction —`. Example:

```
## [2026-05-27] ingest | New paper on X
- pages touched: sources/new-paper.md, entities/foo.md, index.md
- notes: contradiction — new paper disputes earlier dating in entities/foo.md (struck through, replacement cited)
```

`/wiki-lint` scans for this prefix to find unresolved contradictions. A `~~strikethrough~~` claim counts as **resolved** when the same paragraph contains a follow-up claim with a `[source link](...)` citation; otherwise lint flags it.

## Operations summary

- **ingest**: place the raw file in `raw/` (or capture a URL snapshot there) → write a summary page in `sources/` linking back to `raw/` via the `raw:` field → update index → revise affected entity/concept pages → append log entry. Touch as many pages as the source warrants; 10–15 is normal.
  - **Batch mode**: `/wiki-ingest` can also process every file in `raw/` not yet referenced from any `sources/` page — useful after dropping several files in at once.
- **query**: read index → read relevant pages → answer with inline citations. If the synthesis is reusable, file it as `queries/<slug>.md` and update index + log.
- **lint**: scan for contradictions, stale dates, orphan pages (no inbound links), orphan raw files (raw file with no source page citing it), broken links, frontmatter drift, gaps in coverage. Report findings; do not auto-fix without confirmation.
- **discovery**: facilitated discovery / ideation session (`/wiki-discover`) for business, domain, customer, market, regulatory, or architectural topics. Reads wiki context (relevant entity/concept/query/prior-discovery pages) → runs interactive brainstorming with the user → files the session as `discoveries/<slug>.md` with the full idea inventory → promotes user-selected top ideas to concept or entity pages (including new ADRs) with citations back → updates index and log. Aims for 100+ ideas before organization. **Not** for code-implementation brainstorming — that belongs to your dev methodology's own brainstorming skill.
- **migrate**: `/wiki-init` re-run against an existing wiki. Detects missing or stale system files (e.g., absent `_templates/`, outdated SCHEMA), proposes additive changes, applies what the user accepts, and logs the result. Never rewrites content pages.

Empty subdirectories carry a `.gitkeep` file so git tracks the structure; these have no other meaning.

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
