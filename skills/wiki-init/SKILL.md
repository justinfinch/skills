---
name: wiki-init
description: Bootstrap an LLM Wiki at ./.wiki/ in the current project using Karpathy's wiki pattern. The wiki captures **institutional context** (business domain, SME knowledge, ARB-style architectural decisions, research) that doesn't live in the code — adjacent to the codebase, never derived from it. Creates SCHEMA.md (conventions and operations), index.md (catalog), log.md (append-only changelog), and the standard subdirectories. If ./.wiki/ already exists, runs in migration mode — additively brings the wiki's system files up to the current schema without rewriting content pages. Use when the user wants to start a wiki, set up an LLM-maintained knowledge base, upgrade an existing wiki, or says "init wiki", "bootstrap wiki", "set up an LLM wiki here", or "migrate the wiki".
---

# wiki-init

Bootstrap or migrate an LLM Wiki at `./.wiki/`.

This skill owns only the wiki's **system files** (`SCHEMA.md`, `index.md`, `log.md`) and the directory tree. Each operation skill (`/wiki-ingest`, `/wiki-query`, `/wiki-discover`) ships its own page templates and reads them from its own skill directory at runtime — `wiki-init` does not copy templates into the wiki and does not need updating when a new wiki operation skill is added.

The path is **dotted** (`./.wiki/` not `./wiki/`) by convention with other agent-tooling directories (`.claude/`, `.cursor/`, `.vscode/`) and to avoid collision with project content folders. The wiki is curated content but has substantial machine-maintained scaffolding (index, log, frontmatter, lint) — the dot signals that.

## Workflow

1. Resolve today's date once (YYYY-MM-DD from the environment) — reuse it everywhere below.
2. Check whether `./.wiki/` already exists.
   - **Does not exist** → fresh bootstrap (step 3).
   - **Exists** → migration mode (step 4).

### Step 3: Fresh bootstrap

1. Create the directory tree:
   ```
   .wiki/
     SCHEMA.md
     index.md
     log.md
     raw/         # drop zone — immutable source files (PDFs, transcripts, snapshots)
     sources/     # LLM-written summaries that cite raw/ or external URLs
     entities/
     concepts/
     queries/
     discoveries/ # captured discovery / ideation sessions (see /wiki-discover)
   ```
   Add `.gitkeep` to each empty subdir so git tracks the structure.
2. Copy these files from this skill's directory, replacing every `{{DATE}}` token with today's date:
   - `SCHEMA.template.md` → `.wiki/SCHEMA.md`
   - `index.template.md` → `.wiki/index.md`
   - `log.template.md` → `.wiki/log.md`
3. Tell the user the wiki is ready and point them at `/wiki-ingest <source>` to add the first source.

### Step 4: Migration mode (wiki already exists)

The wiki already has content. The job is **additive** — never rewrite a content page (`sources/`, `entities/`, `concepts/`, `queries/`, `discoveries/`). Existing content normalizes opportunistically when future ingests touch it.

1. **Detect drift.** Compare the existing wiki against the current templates in this skill's directory. The principle: anything present in the current `SCHEMA.template.md` that is missing or stale in the existing `SCHEMA.md` is a candidate patch. Check at minimum for:
   - **Framing block** — the "What belongs here (and what doesn't)" section that scopes the wiki to institutional context (business / SME / ADRs / research) and rules out code documentation
   - **ADRs subsection** — the "ADRs (Architecture Decision Records)" section under Page types: convention layered on concept pages, slug `adr-<name>`, 5 body sections, status enum
   - **Frontmatter fields** — `status:` and `superseded_by:` for ADR concept pages
   - **Page-type rename** — if SCHEMA still has `brainstorm` instead of `discovery` in the `type:` enum, the page-types table, the frontmatter spec, the sources-bidirectional clause, or the operations summary
   - **Log-op rename** — if SCHEMA's ops list still has `brainstorm` instead of `discovery`
   - **Index sections** — if SCHEMA's index.md description still says "Brainstorms" instead of "Discoveries"
   - **Earlier-era checks (still relevant for very old wikis):**
     - The expanded `type:` enum including `schema | index | log`
     - The "Slug derivation" subsection
     - The "Contradiction marker" subsection (log notes prefix `contradiction —`)
     - `migrate` in the ops list
     - The `.gitkeep` one-liner
   - Are any expected subdirs missing (`discoveries/`, `queries/`, etc.)? Note their `.gitkeep` if so. If a `brainstorms/` directory exists but no `discoveries/`, flag for the user — directory rename and any `type: brainstorm` content pages need their manual attention (this migration does not rewrite content pages).
2. **Present a migration plan** in one message. Example:
   ```
   Migration plan for ./.wiki/:

   Additive (safe — new files only):
   - create .wiki/discoveries/ (missing)

   Schema patches (overlay .wiki/SCHEMA.md):
   - add "What belongs here (and what doesn't)" framing block
   - add ADRs (Architecture Decision Records) subsection under Page types
   - add status / superseded_by frontmatter fields
   - rename brainstorm → discovery in type enum, page-types table, log ops list, operations summary
   - update index.md section name "Brainstorms" → "Discoveries"

   Needs your manual attention (out of scope for migration):
   - .wiki/brainstorms/ directory exists with N pages — rename directory to discoveries/ and update each page's frontmatter `type: brainstorm` → `type: discovery`

   Untouched: all sources/, entities/, concepts/, queries/ pages.

   Apply all schema patches, pick selectively, or cancel?
   ```
3. **Apply** what the user accepts. For schema patches: overlay the relevant sections of the current `SCHEMA.template.md` into the existing `SCHEMA.md`, preserving any human edits the user has made in the "Conventions the human controls" section. Do not rewrite content pages or rename directories — those stay in the user's hands.
4. **Append a `migrate` log entry** to `.wiki/log.md` listing what changed:
   ```
   ## [{{DATE}}] migrate | Wiki upgraded to current schema
   - pages touched: SCHEMA.md
   - notes: patched SCHEMA (added framing block, ADR section, status/superseded_by, renamed brainstorm→discovery)
   ```
5. Tell the user migration is done. Mention that existing content pages were left as-is and will normalize as future ingests touch them. If you flagged a brainstorms/ directory or `type: brainstorm` pages for manual attention, restate that. Suggest running `/wiki-lint` to confirm the schema/index/log false positives are gone.

## Notes

- The schema is the source of truth for conventions — `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, and `/wiki-discover` all read `.wiki/SCHEMA.md` before acting. If the user later changes conventions, they edit the schema; the operation skills follow.
- Page templates (for `sources/`, `entities/`, `concepts/`, `queries/`, `discoveries/`) live next to the skills that write those page types. `wiki-init` deliberately does not own them — that keeps init decoupled from the set of operation skills.
- Do not embed wiki content in the schema. The schema describes *how* pages are written, not what they contain.

## Templates

System-file templates in this skill's directory:
- [SCHEMA.template.md](SCHEMA.template.md) — full wiki conventions
- [index.template.md](index.template.md) — catalog stub
- [log.template.md](log.template.md) — changelog stub
