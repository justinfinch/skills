---
name: wiki-lint
description: Audit the project's LLM wiki at ./wiki/ for health. Finds contradictions flagged during ingest, stale dates, orphan pages with no inbound links, broken or missing cross-references, frontmatter drift, coverage gaps, and brainstorm-promotion drift (top ideas never filed back); suggests next investigations. Reports findings — does not auto-fix without confirmation. Use when the user says "lint the wiki", "wiki health check", "audit the wiki", or after a batch of ingests or brainstorm sessions when they want a tidy-up.
---

# wiki-lint

Audit the project wiki and report issues. Do not fix without asking.

## Preflight

1. Verify `./wiki/SCHEMA.md`, `./wiki/index.md`, `./wiki/log.md` all exist. If not, instruct the user to run `/wiki-init` first and stop.
2. Read `./wiki/SCHEMA.md` — it defines what "valid" means for this wiki.

## Checks

Run these against every page under `./wiki/`:

1. **Contradictions.** Grep `log.md` for past entries that noted contradictions. List each unresolved one. Also scan pages for `~~strikethrough~~` claims and flag any that don't have a paired replacement.
2. **Stale dates.** Any page whose `updated:` is older than 90 days AND that links to a source page updated more recently → flag as possibly stale.
3. **Orphan pages.** Any entity/concept/query/brainstorm page with zero inbound links from other wiki pages (excluding `index.md`) → flag. New pages get a grace pass — only flag if `created:` is older than 14 days. Brainstorms are expected to be linked from at least the concept/entity pages that promoted their top ideas; a brainstorm with no inbound links after the grace period likely means no promotions stuck.
4. **Orphan raw files.** Any file in `./wiki/raw/` not referenced by any `sources/*.md` page's `raw:` frontmatter → flag as unprocessed. This is the "inbox not drained" signal; suggest `/wiki-ingest` (batch mode) to handle them.
5. **Broken links.** Resolve every relative markdown link inside `./wiki/`. Flag any whose target file doesn't exist.
6. **Frontmatter drift.** For every page, check that required fields from SCHEMA.md's frontmatter spec are present and well-formed (valid date, valid `type:`, `sources:` is a list, etc.). Flag mismatches.
7. **Index/log integrity.** Every page in `./wiki/{sources,entities,concepts,queries,brainstorms}/` should appear in `index.md`. Every `ingest`/`query`/`brainstorm` entry in `log.md` should reference pages that exist. Flag mismatches both directions.
8. **Coverage gaps.** Concepts that are referenced from other pages but have no page of their own → flag as candidates to create. Entities mentioned in ≥3 sources but with thin entity pages (<5 lines of body) → flag for expansion.
9. **Brainstorm promotion drift.** For every `brainstorms/*.md` page older than 14 days, check that at least one concept or entity page lists it in their `sources:` frontmatter (i.e., a top idea was actually filed back). Brainstorms with zero promoted pages → flag with note "promotion never filed — was that intentional, or did the session end before Phase 4 wrote back?". Skip this check if the user explicitly chose "self-contained brainstorm" in the session.

## Report format

Single response, sectioned by check:

```
## wiki-lint report — {{TODAY}}

### Contradictions (N)
- [path](path) — one-line description

### Stale (N)
...

### Orphans (N)
...

(etc, omit sections with zero findings)

### Suggested next ingests
- topic — why
```

## After reporting

Ask: "Want me to fix any of these now?" Wait for the user to pick. Then handle one category at a time, confirming destructive edits (strikethrough resolutions, page deletions, slug renames).

Do not append a `lint` entry to `log.md` for the audit itself — only log when fixes are actually applied.

## Discipline

- Read-only by default. Never edit pages during the audit phase.
- Don't flood — if a check produces >20 findings, summarize and offer to drill in.
- Prefer suggesting next investigations over auto-creating empty stub pages.
