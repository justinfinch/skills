---
name: wiki-init
description: Bootstrap an LLM Wiki at ./wiki/ in the current project using Karpathy's wiki pattern. Creates SCHEMA.md (conventions and operations), index.md (catalog), and log.md (append-only changelog). Use when the user wants to start a wiki, set up an LLM-maintained knowledge base, or says "init wiki", "bootstrap wiki", or "set up an LLM wiki here".
---

# wiki-init

Bootstrap an LLM Wiki at `./wiki/`.

## Workflow

1. If `./wiki/` already exists, list its contents and ask the user before overwriting any file. Do not silently clobber.
2. Resolve today's date once (YYYY-MM-DD from the environment) — reuse it everywhere below.
3. Create the directory tree:
   ```
   wiki/
     SCHEMA.md
     index.md
     log.md
     raw/         # drop zone — immutable source files (PDFs, transcripts, snapshots)
     sources/     # LLM-written summaries that cite raw/ or external URLs
     entities/
     concepts/
     queries/
   ```
   Add `.gitkeep` to each empty subdir so git tracks the structure.
4. Copy `SCHEMA.template.md` from this skill's directory to `wiki/SCHEMA.md`, replacing every `{{DATE}}` token with today's date.
5. Copy `index.template.md` to `wiki/index.md` and `log.template.md` to `wiki/log.md`, again replacing `{{DATE}}`.
6. Tell the user the wiki is ready and point them at `/wiki-ingest <source>` to add the first source.

## Notes

- The schema is the source of truth for conventions — `/wiki-ingest`, `/wiki-query`, and `/wiki-lint` all read `wiki/SCHEMA.md` before acting. If the user later changes conventions, they edit the schema; the operation skills follow.
- Do not embed wiki content in the schema. The schema describes *how* pages are written, not what they contain.

## Templates

See sibling files in this skill's directory:
- [SCHEMA.template.md](SCHEMA.template.md) — full wiki conventions
- [index.template.md](index.template.md) — catalog stub
- [log.template.md](log.template.md) — changelog stub
