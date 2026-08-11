---
name: arche-init
description: Bootstrap an Arche at ./.arche/ in the current project using Karpathy's wiki pattern, as a conformant Open Knowledge Format (OKF) v0.2 bundle. The Arche captures **institutional context** (business domain, SME knowledge, ARB-style architectural decisions, research) that doesn't live in the code — adjacent to the codebase, never derived from it. Creates SCHEMA.md (conventions), index.md (catalog), log.md (changelog), the standard subdirectories with per-directory indexes, and registers the Arche in the repo's agent context file(s) (AGENTS.md / CLAUDE.md / .cursorrules) so coding agents treat it as a first-class context source. If ./.arche/ already exists, this skill stops and points at /arche-lint, which owns ongoing conformance and repair. Use when the user wants to start an Arche, set up an LLM-maintained knowledge base, or says "init Arche", "bootstrap Arche", or "set up an Arche here".
---

# arche-init

Bootstrap an Arche at `./.arche/`.

This skill owns only the Arche's **system files** (`SCHEMA.md`, `index.md`, `log.md`) and the directory tree. Each operation skill (`/arche-ingest`, `/arche-query`, `/arche-discover`, `/arche-architect`, `/arche-tell`) ships its own page templates and reads them from its own skill directory at runtime — `arche-init` does not copy templates into the Arche and does not need updating when a new Arche operation skill is added.

The path is **dotted** (`./.arche/` not `./arche/`) by convention with other agent-tooling directories (`.claude/`, `.cursor/`, `.vscode/`) and to avoid collision with project content folders. The Arche is curated content but has substantial machine-maintained scaffolding (index, log, frontmatter, lint) — the dot signals that.

## Workflow

1. Resolve today's date once (YYYY-MM-DD) and the current UTC timestamp (ISO 8601) — reuse both everywhere below.
2. Resolve the actor string: `arche-init/<model-id>`.
3. Check whether `./.arche/` already exists.
   - **Exists** → stop. Tell the user an Arche is already present and that `/arche-lint` owns conformance and repair — including bringing an older Arche up to the current OKF era. Do not modify anything.
   - **Does not exist** → bootstrap (step 4).

### Step 4: Bootstrap

1. Create the directory tree:
   ```
   .arche/
     SCHEMA.md
     index.md
     log.md
     raw/             # drop zone — immutable source files
     sources/
     entities/
     concepts/
     queries/
     discoveries/
     stories/
     assets/stories/
   ```
   Add `.gitkeep` to each empty subdir.
2. Copy from this skill's `assets/`, replacing `{{DATE}}` with today's date and `{{TIMESTAMP}}` with the UTC timestamp:
   - `assets/SCHEMA.template.md` → `.arche/SCHEMA.md`
   - `assets/index.template.md` → `.arche/index.md`
   - `assets/log.template.md` → `.arche/log.md`
3. Write a per-directory `index.md` into each of `sources/`, `entities/`, `concepts/`, `queries/`, `discoveries/`, and `stories/` from `assets/subindex.template.md`, replacing `{{TITLE}}` with that directory's singular type name (`Source`, `Entity`, `Concept`, `Query`, `Discovery`, `Story`). These carry **no frontmatter** — §8 permits it only on the bundle-root index.
4. **Register the Arche in the repo's agent context file(s)** — unchanged from before. The snippet is [assets/agents-md-snippet.md](assets/agents-md-snippet.md), marked with `<!-- arche-context-source -->`.
   1. **Canonical home — `AGENTS.md`.** Append the snippet if it exists; create it with the snippet if not.
   2. **Claude Code bridge — `CLAUDE.md`.** Claude Code reads `CLAUDE.md`, not `AGENTS.md` ([docs](https://code.claude.com/docs/en/memory)). If `CLAUDE.md` exists and carries neither the marker nor an `@AGENTS.md` import, add `@AGENTS.md` near the top; if it doesn't exist, create it containing `@AGENTS.md`.
   3. **Other tool files that already exist** — `.cursorrules` / `.cursor/rules/*.md`, `.windsurfrules`, `.github/copilot-instructions.md`. Append the snippet inline. Only touch them if they already exist.
   Idempotent: a file is done if it contains `<!-- arche-context-source -->`, and `CLAUDE.md` is also done if it contains an `@AGENTS.md` import. Don't edit `README.md`.
5. Tell the user the Arche is ready, list the context file(s) touched, note that it is a conformant OKF v0.2 bundle, and point them at `/arche-ingest <source>`.

## Notes

- **`arche-init` creates; `/arche-lint` maintains.** This skill writes `SCHEMA.md`, `index.md`, and `log.md` exactly once, at bootstrap. Everything afterward — OKF conformance, schema-era nonconformance, repair, agent-context registration checks — belongs to `/arche-lint`. That keeps a single writer per phase instead of two skills editing the same files. OKF will keep evolving, so conformance is a standing condition rather than a one-time bootstrap concern, which is why it lives with the audit skill.
- The schema is the source of truth for conventions — `/arche-ingest`, `/arche-query`, `/arche-lint`, `/arche-discover`, `/arche-architect`, and `/arche-tell` all read `.arche/SCHEMA.md` before acting. If the user later changes conventions, they edit the schema; the operation skills follow.
- Page templates (for `sources/`, `entities/`, `concepts/`, `queries/`, `discoveries/`, `stories/`) live next to the skills that write those page types. `arche-init` deliberately does not own them — that keeps init decoupled from the set of operation skills.
- Do not embed Arche content in the schema. The schema describes *how* pages are written, not what they contain.
- **Agent-context registration is what makes the Arche first-class.** A coding agent won't reliably consult `./.arche/` unless its always-loaded context file says to. Bootstrap writes the `<!-- arche-context-source -->` snippet into the repo's context file(s) so the Arche is picked up automatically — the user shouldn't have to remember to invoke `/arche-query`. The snippet is agent-neutral (same approach as `devbox-add`'s source-of-truth snippet). This is `arche-init`'s own policy snippet about the artifact it bootstraps — not a page template owned by another operation skill.
- **No agent detection — bridge instead.** `AGENTS.md` is the single source of truth; we never branch on "which coding agent is this". The one wrinkle is that **Claude Code reads `CLAUDE.md`, not `AGENTS.md`** ([memory docs](https://code.claude.com/docs/en/memory)), so a repo with only `AGENTS.md` would be invisible to it. Rather than detect Claude Code, we always add a `CLAUDE.md` that imports `AGENTS.md` via `@AGENTS.md` — the Anthropic-documented bridge. One import line, no duplicated content (so nothing to keep in sync), and non-Claude agents harmlessly ignore the extra file. Tool files without import syntax (`.cursorrules`, `.windsurfrules`, Copilot) get the snippet inline, but only if they already exist.

## Templates

System-file templates in this skill's directory:
- [SCHEMA.template.md](assets/SCHEMA.template.md) — full Arche conventions
- [index.template.md](assets/index.template.md) — catalog stub
- [log.template.md](assets/log.template.md) — changelog stub
- [subindex.template.md](assets/subindex.template.md) — per-directory `index.md` stub (§8 progressive disclosure)
- [agents-md-snippet.md](assets/agents-md-snippet.md) — the "consult the Arche first" snippet appended to the repo's agent context file(s) (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, …) so the Arche is a first-class, auto-loaded context source
