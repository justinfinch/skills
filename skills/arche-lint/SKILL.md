---
name: arche-lint
description: Audit the project's Arche at ./.arche/ for health and own its ongoing OKF v0.2 conformance — detection and repair alike. `/arche-init` writes the system files once at bootstrap; this skill maintains them after that. Finds contradictions flagged during ingest, stale dates, orphan pages with no inbound links, broken or missing cross-references, frontmatter drift, schema-era version skew, non-relative links, coverage gaps, discovery-promotion drift (top ideas never filed back), and whether the Arche is registered in the repo's agent context files so coding agents pick it up; suggests next investigations. Reports findings — does not auto-fix without confirmation. Use when the user says "lint the Arche", "Arche health check", "audit the Arche", "check conformance", "migrate the Arche", "upgrade the Arche", or after a batch of ingests or discovery sessions when they want a tidy-up.
---

# arche-lint

Audit the project Arche and report issues. Do not fix without asking.

## OKF conformance

This Arche is an [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/3fcbb9f/okf/SPEC.md) bundle, and this skill is what keeps it one. `/arche-init` writes the system files once at bootstrap; everything afterward — conformance, schema-era drift, repair — belongs here. OKF will keep evolving, so drift is a standing condition rather than a one-time migration, which is why it lives with the audit skill rather than a bootstrap migrate mode.

Read [references/OKF-CONFORMANCE.md](references/OKF-CONFORMANCE.md) before checking. It is the full matrix: every drift class, its detection rule, and its repair.

**Conformance is narrower than this skill's remit.** Per §11, a bundle is conformant if every non-reserved `.md` has parseable frontmatter, every frontmatter block has a non-empty `type`, and `index.md` / `log.md` follow §8 / §9 when present. That is the whole list — the matrix calls it Tier 1. Everything else this skill checks is drift from *this Arche's* `SCHEMA.md`, not from OKF. The spec explicitly forbids consumers from **rejecting** a bundle over unknown `type` values, missing `index.md` files, broken cross-links, missing optional fields, or unknown extra keys — all of which appear below as findings. Reporting them and offering repair is correct; refusing to read an Arche over any of them is not. Audit and ask; never reject.

**Scope of repair.** Frontmatter and reserved-file structure only. **Never rewrite body prose.** Two carve-outs: renaming a `raw/*.md` file to `.txt` is permitted because its content is unchanged, and `SCHEMA.md` may be overlaid section by section from `arche-init`'s template (matrix rule SC1) because it is rendered scaffolding, not authored content. No other file's body is touched.

**Order of operations:**

1. Read the root `index.md` for `okf_version`, and `SCHEMA.md` for its era. Compare both against 0.2. If the bundle is **ahead** of these skills, stop and report — do not repair.
2. **If `SCHEMA.md` is behind, settle that first.** Present the SC1 overlay on its own, apply what the user accepts, and re-read `SCHEMA.md` before going further. Every rule below reads the schema as the definition of valid — T4 checks `type` against the page types it declares, F9 checks key shapes against its frontmatter spec — so running them against a stale schema makes them contradict each other. T2 would promote an ADR and T4 would immediately flag the promoted value as unrecognized.
3. Walk every `.md` file and collect findings against the matrix.
4. Group findings by class and present them as a plan, separating what you can repair mechanically from what needs the user (F4 descriptions, F5 missing `superseded_by`, T3 directory renames, T4 unrecognized types).
5. Apply only what the user accepts, **group by group in matrix order** — hard conformance, type taxonomy, field families, structure — never page by page. Rules consume what earlier rules produce (T2 promotes the value T1 normalizes), so a per-page walk silently skips the dependent half.
6. Insert a `- **Lint**: …` entry as the first bullet under today's `## YYYY-MM-DD` heading in `log.md`, creating that heading immediately above the topmost existing date heading only if today's is absent, recording what changed.

**Sibling-skill assets.** Two repairs read files from `arche-init`: the SC1 schema overlay needs [SCHEMA.template.md](../arche-init/assets/SCHEMA.template.md), and check 12's registration repair needs [agents-md-snippet.md](../arche-init/assets/agents-md-snippet.md). Both resolve relative to this skill's own directory and only exist when `arche-init` is installed alongside. When either is unreachable, report the finding as detected-but-unrepairable and name the missing skill — **never improvise the content**. A reconstructed schema or registration snippet diverges from what `arche-init` writes, so the next run sees drift the user cannot explain. Everything else this skill repairs is specified inline in the matrix and needs no sibling skill.

## Preflight

1. Verify `./.arche/SCHEMA.md`, `./.arche/index.md`, `./.arche/log.md` all exist. If not, instruct the user to run `/arche-init` first and stop.
2. Read `./.arche/SCHEMA.md` — it defines what "valid" means for this Arche.

## Checks

Run these against every page under `./.arche/`:

1. **Contradictions.** Grep `log.md` for entry bullets whose prose contains `contradiction —` (per SCHEMA's contradiction marker convention). For each, locate the strikethrough(s) on the pages the bullet names — a strikethrough is **resolved** if the same paragraph contains a follow-up claim with an inline `[source link](...)` citation; otherwise flag it. Also scan all pages for stray `~~strikethrough~~` claims that have no corresponding `contradiction —` log entry — flag as untracked.
2. **Stale dates.** Two signals, reported together:
    - **Explicit.** Any page whose `stale_after` is on or before today → flag as stale, unconditionally. This is the author saying "this expires"; it is not a heuristic and takes no grace period, no 90-day window, and no corroborating source. `/arche-query` and `/arche-tell` both honor `stale_after` when they cite a page, so an audit that ignored it would be the one place the field silently does nothing.
    - **Inferred.** Any page whose `generated.at` is older than 90 days AND that links to a source page with a more recent `generated.at` → flag as possibly stale.
   A page with a malformed `generated:` (a bare date rather than a `{ by, at }` mapping) has no readable `generated.at`; do not skip it silently — report it under check 6 (F9) so it stops being invisible here.
3. **Orphan pages.** Any entity/concept/query/discovery page with zero inbound links from other Arche pages (excluding `index.md`) → flag. New pages get a grace pass — only flag if `created:` is older than 14 days. Discoveries are expected to be linked from at least the concept/entity pages that promoted their top ideas; a discovery with no inbound links after the grace period likely means no promotions stuck.
4. **Orphan raw files.** Any file in `./.arche/raw/` not referenced by any `sources/*.md` page's `resource:` or `sources[].resource` → flag as unprocessed. This is the "inbox not drained" signal; suggest `/arche-ingest` (batch mode) to handle them.
5. **Broken links.** Resolve every relative markdown link inside `./.arche/`. Flag any whose target file doesn't exist.
6. **OKF conformance.** Walk every page against the matrix in [references/OKF-CONFORMANCE.md](references/OKF-CONFORMANCE.md) — hard rules (H1–H4), type taxonomy (T1–T4), and field families (F1–F9). Group and report findings by class, separating what's mechanically repairable from what needs the user (F4 descriptions, F5 missing `superseded_by`, T3 directory renames, T4 unrecognized types). **The matrix is not a closed list of everything worth flagging.** T4 and F9 are its catch-alls: T4 fires on any `type` value the schema doesn't define, F9 on any frontmatter key whose shape contradicts SCHEMA.md's spec. Check every page against SCHEMA.md's frontmatter spec as written, not only against the enumerated rows — an unrecognized `type` still satisfies §11.2 (it is a non-empty string) while being invisible to every skill that filters on `type`, so a page that drifts in a way nobody enumerated must still surface rather than passing clean.
7. **Structure.** Also from the matrix (S1–S4): a content subdirectory with no `index.md`; an `index.md` entry whose gloss doesn't match the target's `description` — **only where the target carries one**, so per-directory `index.md` entries and the root index's `SCHEMA.md` / `log.md` entries are exempt (see S2); a bundle-absolute link (`](/`) in any page; the root `index.md` missing `okf_version`.
8. **Version skew.** Compare `okf_version` in the root `index.md`, the era `SCHEMA.md` documents, and what these skills implement (currently 0.2). Any mismatch is a finding — report the direction. If the bundle is **ahead** of the skills, stop and report only; do not offer repair. A bundle **behind** the skills is repairable: `okf_version` via S4, and the schema body via SC1's section-by-section overlay. This is the path an Arche created before the current era takes to become usable by `/arche-architect`, `/arche-discover`, and `/arche-tell` again — all three refuse to run against a stale schema, and this skill owns the only repair for it.
9. **Index/log integrity.** Every page in `./.arche/{sources,entities,concepts,queries,discoveries,stories}/` should appear in `index.md`. Every `**Init**` / `**Ingest**` / `**Query**` / `**Lint**` / `**Discovery**` / `**Architect**` / `**Story**` / `**Manual**` entry in `log.md` should reference pages that exist. Flag mismatches both directions.
10. **Coverage gaps.** Concepts that are referenced from other pages but have no page of their own → flag as candidates to create. Entities mentioned in ≥3 sources but with thin entity pages (<5 lines of body) → flag for expansion.
11. **Discovery promotion drift.** For every `discoveries/*.md` page older than 14 days, check that at least one concept or entity page lists it in their `sources:` frontmatter (i.e., a top idea was actually filed back). Discoveries with zero promoted pages → flag with note "promotion never filed — was that intentional, or did the session end before Phase 4 wrote back?". Skip this check if the user explicitly chose "self-contained discovery" in the session.
12. **Agent-context registration.** Grep the repo's agent context files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules` / `.cursor/rules/*.md`, `.windsurfrules`, `.github/copilot-instructions.md`) for the marker `<!-- arche-context-source -->`. Two failure modes:
    - **Not registered** — no context file carries the marker. Flag: "Arche isn't wired in as a first-class context source — coding agents won't reliably consult it." Register it directly using [arche-init's snippet](../arche-init/assets/agents-md-snippet.md): append it to `AGENTS.md` (creating the file if needed), marked with `<!-- arche-context-source -->`. If that file is unreachable because `arche-init` isn't installed alongside, report the finding and stop there per [Sibling-skill assets](#okf-conformance) — do not write a snippet of your own wording. Common for Arches created before agent-context registration existed.
    - **Claude Code can't see it** — a file (typically `AGENTS.md`) carries the marker, but `CLAUDE.md` neither carries the marker nor imports the marked file via `@AGENTS.md`. Claude Code reads only `CLAUDE.md`, so flag: "Registered for other agents but not bridged to Claude Code." Repair it directly: add an `@AGENTS.md` import near the top of `CLAUDE.md` (creating the file with just that import if it doesn't exist). Easy to miss because non-Claude agents pick it up fine.
13. **Trust tiers.** Scan for whether any page carries a `verified` key at all — this is the sole gate for whether the report carries a `### Trust` section. See [Trust reporting](#trust-reporting) below for the exact rule and format. This is distinct from F8 in check 6: F8 flags a machine-written `verified` as a conformance anomaly; this check aggregates tier counts across the whole bundle and only fires the section when the gate is open.

## Trust reporting

A trust tier only carries information when tiers differ. In an Arche where nobody signs off, every page is `unverified`, and a report listing all of them on every run is wallpaper — it trains the reader to scroll past this skill's other findings. So trust reporting is **gated on adoption**, the same rule `/arche-query` uses for its own trust surfacing:

1. Scan each content page's **parsed frontmatter mapping** — `sources/`, `entities/`, `concepts/`, `queries/`, `discoveries/`, `stories/` — for a top-level `verified` key. This is a frontmatter check, not a text search: body prose, fenced examples, and mentions of the word `verified` do not count. **Do not text-scan `SCHEMA.md`** — its body documents the `verified` field (including a fenced YAML example) on every bootstrapped Arche, so a grep-style scan would false-positive on a fresh Arche where nobody has signed off anything. Exclude the reserved files entirely: `SCHEMA.md`, `index.md` (no frontmatter at all), and `log.md` (`type: Log`) — none can legitimately carry `verified`.
2. **Zero found** → emit **no `### Trust` section at all**. Do not list unverified pages, do not mention tiers, do not suggest sign-off. The feature is invisible until it is used. This scan result is the entire gate — no judgment call, no partial reporting.
3. **At least one found** → include a `### Trust` section: the tier breakdown, then every unverified page, oldest `generated.at` first:

   ```
   Trust: 6 human-reviewed, 36 unverified

     concepts/adr-billing.md    generated 2026-03-02
     entities/acme.md           generated 2026-01-14
   ```

Derive tiers per SCHEMA.md §5.3: no `verified` key → unverified; `verified` by non-`human:` actors only → machine-confirmed; `verified` by a `human:` actor → human-reviewed. The Arche never machine-verifies, so machine-confirmed appears only if something outside these skills wrote it — when that happens, check 6 (F8) already flags it as a conformance anomaly; this section only adds the aggregate tier count and does not re-report it.

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

### Trust (only if the gate in Trust reporting is open — omit entirely otherwise)
Trust: N human-reviewed, M unverified

  path   generated date
  ...

### Suggested next ingests
- topic — why
```

## After reporting

Ask: "Want me to fix any of these now?" Wait for the user to pick. Then handle one category at a time, confirming destructive edits (strikethrough resolutions, page deletions, slug renames).

Do not insert a `lint` entry into `log.md` for the audit itself, and do not insert one for a sign-off that nobody accepted — only log when fixes are actually applied or pages are actually signed off (see [Sign-off](#sign-off)). When something did change, insert a `- **Lint**: …` bullet as the first bullet under today's `## YYYY-MM-DD` heading in `log.md`; if today's heading is absent, create it immediately above the topmost existing date heading. Never append at the end of the file, per SCHEMA's newest-first convention.

## Sign-off

**This is the only place in any `arche-*` skill that writes `verified`.** Every other skill — `arche-ingest`, `arche-architect`, `arche-discover`, `arche-tell`, `arche-query` — is instructed never to write it; `arche-query` only *reads* it, to derive the tiers reported above.

Hand-editing YAML frontmatter is enough friction that sign-off would never happen otherwise, which would leave the whole trust family dead weight. So `/arche-lint` offers it inline, attached to a report the user is already reading, rather than building any dedicated path to it.

After the fix phase above, if the user reviewed any pages during this run — confirmed a flagged page's content as still correct, resolved a contradiction on it, or otherwise read and endorsed it — ask once:

```
Mark the N pages you just reviewed as verified by human:<id>? [y/N]
```

On yes, for each page append to its frontmatter:

```yaml
verified:
  - { by: human:<id>, at: <ISO 8601 UTC now> }
```

If the page already carries a `verified` entry, append to that list. Per §11 a bare `verified: { ... }` mapping is a one-element list — normalize it to list form before appending a second entry.

**Resolve `<id>`:** try `git config user.email`, then `git config user.name`, then ask the user directly. Reuse the same `<id>` for every page accepted in this one prompt.

**This is deliberately not a workflow.** No review queue, no partial-review state, no scheduling, no dedicated command, no re-prompting later for pages the user declined this time. One prompt on an existing report is the entire sign-off surface — resist growing it.

A sign-off is a change to the bundle like any repair: log it per [After reporting](#after-reporting) above, e.g. `- **Lint**: signed off 6 pages as verified by human:jf`. Declining (`N` or no reviewed pages) logs nothing, same as a no-op audit.

## Discipline

- Read-only by default. Never edit pages during the audit phase.
- Don't flood — if a check produces >20 findings, summarize and offer to drill in.
- Prefer suggesting next investigations over auto-creating empty stub pages.
