---
name: arche-lint
description: Audit the project's Arche at ./.arche/ for health and own its ongoing OKF v0.2 conformance — detection and repair alike. `/arche-init` writes the system files once at bootstrap; this skill maintains them after that. Finds contradictions flagged during ingest, stale dates, orphan pages with no inbound links, broken or missing cross-references, frontmatter drift, schema-era version skew, non-relative links, coverage gaps, discovery-promotion drift (top ideas never filed back), and whether the Arche is registered in the repo's agent context files so coding agents pick it up; suggests next investigations. Reports findings — does not auto-fix without confirmation. Use when the user says "lint the Arche", "Arche health check", "audit the Arche", "check conformance", "migrate the Arche", "upgrade the Arche", or after a batch of ingests or discovery sessions when they want a tidy-up.
---

# arche-lint

Audit the project Arche and report issues. Do not fix without asking.

## OKF conformance

This Arche is an [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle, and this skill is what keeps it one. `/arche-init` writes the system files once at bootstrap; everything afterward — conformance, schema-era drift, repair — belongs here. OKF will keep evolving, so drift is a standing condition rather than a one-time migration, which is why it lives with the audit skill rather than a bootstrap migrate mode.

Read [references/OKF-CONFORMANCE.md](references/OKF-CONFORMANCE.md) before checking. It is the full matrix: every drift class, its detection rule, and its repair.

**Scope of repair.** Frontmatter and reserved-file structure only. **Never rewrite body prose.** Renaming a `raw/*.md` file to `.txt` is permitted because its content is unchanged.

**Order of operations:**

1. Read the root `index.md` for `okf_version`, and `SCHEMA.md` for its era. Compare both against 0.2. If the bundle is **ahead** of these skills, stop and report — do not repair.
2. Walk every `.md` file and collect findings against the matrix.
3. Group findings by class and present them as a plan, separating what you can repair mechanically from what needs the user (F4 descriptions, F5 missing `superseded_by`, T3 directory renames).
4. Apply only what the user accepts. Insert a `- **Lint**: …` entry at the top of `log.md` recording what changed.

## Preflight

1. Verify `./.arche/SCHEMA.md`, `./.arche/index.md`, `./.arche/log.md` all exist. If not, instruct the user to run `/arche-init` first and stop.
2. Read `./.arche/SCHEMA.md` — it defines what "valid" means for this Arche.

## Checks

Run these against every page under `./.arche/`:

1. **Contradictions.** Grep `log.md` for entries whose `notes:` line starts with `contradiction —` (per SCHEMA's contradiction marker convention). For each, locate the strikethrough(s) on the pages listed in `pages touched:` — a strikethrough is **resolved** if the same paragraph contains a follow-up claim with an inline `[source link](...)` citation; otherwise flag it. Also scan all pages for stray `~~strikethrough~~` claims that have no corresponding `contradiction —` log entry — flag as untracked.
2. **Stale dates.** Any page whose `updated:` is older than 90 days AND that links to a source page updated more recently → flag as possibly stale.
3. **Orphan pages.** Any entity/concept/query/discovery page with zero inbound links from other Arche pages (excluding `index.md`) → flag. New pages get a grace pass — only flag if `created:` is older than 14 days. Discoveries are expected to be linked from at least the concept/entity pages that promoted their top ideas; a discovery with no inbound links after the grace period likely means no promotions stuck.
4. **Orphan raw files.** Any file in `./.arche/raw/` not referenced by any `sources/*.md` page's `resource:` or `sources[].resource` → flag as unprocessed. This is the "inbox not drained" signal; suggest `/arche-ingest` (batch mode) to handle them.
5. **Broken links.** Resolve every relative markdown link inside `./.arche/`. Flag any whose target file doesn't exist.
6. **OKF conformance.** Walk every page against the matrix in [references/OKF-CONFORMANCE.md](references/OKF-CONFORMANCE.md) — hard rules (H1–H4), type taxonomy (T1–T3), and field families (F1–F8). Group and report findings by class, separating what's mechanically repairable from what needs the user (F4 descriptions, F5 missing `superseded_by`, T3 directory renames).
7. **Structure.** Also from the matrix (S1–S4): a content subdirectory with no `index.md`; an `index.md` entry whose gloss doesn't match the target's `description`; a bundle-absolute link (`](/`) in any page; the root `index.md` missing `okf_version`.
8. **Version skew.** Compare `okf_version` in the root `index.md`, the era `SCHEMA.md` documents, and what these skills implement (currently 0.2). Any mismatch is a finding — report the direction. If the bundle is **ahead** of the skills, stop and report only; do not offer repair.
9. **Index/log integrity.** Every page in `./.arche/{sources,entities,concepts,queries,discoveries}/` should appear in `index.md`. Every `ingest`/`query`/`discovery` entry in `log.md` should reference pages that exist. Flag mismatches both directions.
10. **Coverage gaps.** Concepts that are referenced from other pages but have no page of their own → flag as candidates to create. Entities mentioned in ≥3 sources but with thin entity pages (<5 lines of body) → flag for expansion.
11. **Discovery promotion drift.** For every `discoveries/*.md` page older than 14 days, check that at least one concept or entity page lists it in their `sources:` frontmatter (i.e., a top idea was actually filed back). Discoveries with zero promoted pages → flag with note "promotion never filed — was that intentional, or did the session end before Phase 4 wrote back?". Skip this check if the user explicitly chose "self-contained discovery" in the session.
12. **Agent-context registration.** Grep the repo's agent context files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules` / `.cursor/rules/*.md`, `.windsurfrules`, `.github/copilot-instructions.md`) for the marker `<!-- arche-context-source -->`. Two failure modes:
    - **Not registered** — no context file carries the marker. Flag: "Arche isn't wired in as a first-class context source — coding agents won't reliably consult it." Register it directly using [arche-init's snippet](../arche-init/assets/agents-md-snippet.md): append it to `AGENTS.md` (creating the file if needed), marked with `<!-- arche-context-source -->`. Common for Arches created before agent-context registration existed.
    - **Claude Code can't see it** — a file (typically `AGENTS.md`) carries the marker, but `CLAUDE.md` neither carries the marker nor imports the marked file via `@AGENTS.md`. Claude Code reads only `CLAUDE.md`, so flag: "Registered for other agents but not bridged to Claude Code." Repair it directly: add an `@AGENTS.md` import near the top of `CLAUDE.md` (creating the file with just that import if it doesn't exist). Easy to miss because non-Claude agents pick it up fine.

## Report format

Single response, sectioned by check:

```
## arche-lint report — {{TODAY}}

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

Do not insert a `lint` entry into `log.md` for the audit itself — only log when fixes are actually applied. When they are, insert a `- **Lint**: …` bullet under today's `## YYYY-MM-DD` heading at the top of `log.md`, below `# Arche history`, per SCHEMA's newest-first convention.

## Discipline

- Read-only by default. Never edit pages during the audit phase.
- Don't flood — if a check produces >20 findings, summarize and offer to drill in.
- Prefer suggesting next investigations over auto-creating empty stub pages.
