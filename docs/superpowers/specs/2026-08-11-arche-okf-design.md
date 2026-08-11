# Arche → Open Knowledge Format v0.2

**Date:** 2026-08-11
**Branch:** `arche-open-knowledge-format`
**Status:** approved, ready for planning

## Goal

Make the Arche a conformant Open Knowledge Format (OKF) v0.2 knowledge bundle, adopting OKF's provenance, trust, and lifecycle field families in full.

**Spec reference.** OKF v0.2, pinned at commit `3fcbb9f828c2f23d109c855ee403c3a4c81f3a96` (2026-07-24):
<https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>

Conventions not stated in the spec prose were taken from the `acme_retail` sample bundle at the same commit, which exercises every v0.2 family. Where the sample and a naive reading of the prose disagree, the sample wins — it is the reference producer's own output.

## Why

The Arche already implements the LLM-wiki pattern OKF formalizes: a directory of markdown files with YAML frontmatter, an `index.md` catalog, a `log.md` history, cross-linked by ordinary markdown links. It passes two of OKF's three hard conformance rules today without changes.

What it lacks is the v0.2 signal layer — `generated`, `verified`, `status`, `stale_after`, and structured `sources`. For a corpus that an LLM writes and a human curates, the missing question is the important one: *which pages has a person actually reviewed?* OKF's trust tiers answer it, and nothing in the Arche does today.

## Decisions

| # | Decision | Choice |
|---|---|---|
| 1 | Conformance posture | **Full conformance.** OKF's meaning wins on every key OKF defines. Arche-specific semantics survive only as extension keys, which §4.1 permits. |
| 2 | Link form | **Relative.** §6.1 supports both; absolute is only *recommended*. The Arche is a repo subdirectory, so `/concepts/foo.md` would 404 in GitHub and VS Code, which resolve `/` against the repo root. Google's own bundle uses relative links in `index.md`. |
| 3 | Type taxonomy | **Title-case singular, ARD/SAD/ADR promoted to first-class types** rather than filename slug conventions. |
| 4 | Conformance ownership | **`arche-lint` detects and repairs everything.** `arche-init`'s migrate mode is retired. |
| 5 | Trust model | **`verified` is human-only.** Skills write `generated` and never `verified`. Lint surfaces the gap. |

Decision 4 is the load-bearing one architecturally. OKF will keep moving; conformance drift is a standing condition, not a one-time migration. Lint already owns "frontmatter drift" and already has the correct posture — report findings, repair only on confirmation. Putting conformance anywhere else means rebuilding this machinery at every spec bump.

## Format mapping

### Frontmatter

| Arche today | OKF v0.2 | Notes |
|---|---|---|
| `type: source` | `type: Source` | Title-case singular |
| `type: entity` | `type: Entity` | |
| `type: concept` | `type: Concept` | |
| `type: query` | `type: Query` | |
| `type: discovery` | `type: Discovery` | |
| `type: story` | `type: Story` | |
| `type: schema` | `type: Schema` | `SCHEMA.md` is not a reserved filename in OKF, so it stays a concept document and keeps frontmatter |
| `type: index` | *dropped* | §8 — `index.md` carries no frontmatter |
| `type: log` | `type: Log` | §9 does not forbid frontmatter; the sample bundle uses `type: Log` |
| slug `ard-*` | `type: Architecture Requirements Document` | Promoted from slug convention |
| slug `sad-*` | `type: Solution Architecture Document` | Promoted from slug convention |
| slug `adr-*` | `type: Architecture Decision Record` | Promoted from slug convention |
| `title` | `title` | Unchanged |
| `tags` | `tags` | Unchanged |
| — | `description` | **New.** One sentence. Feeds `index.md` entry glosses |
| `created` | `created` | **Retained as an extension.** OKF has no equivalent; §4.1 permits extra keys |
| `updated` | `generated: { by, at }` | `at` is the last meaningful content change |
| — | `verified: [{ by, at }]` | **New.** Human-only — see Trust model |
| `status: proposed` | `status: draft` | |
| `status: accepted` | `status: stable` | Also the default when `status` is absent (§5.4) |
| `status: superseded` | `status: deprecated` | |
| `superseded_by` | `superseded_by` | **Retained as an extension.** Carries the supersession target that `deprecated` alone loses |
| — | `stale_after` | **New**, optional. Absolute `YYYY-MM-DD` |
| `sources: [sources/foo.md]` | `sources: [{ id, resource, … }]` | Reshaped to §5.1 |
| `url:` (source pages) | `resource:` | Canonical URI of the described asset |
| `raw:` (source pages) | a `sources` entry | See below |
| `context_pages` (discovery) | folded into `sources` | Discovery `sources` is already bidirectional |
| story `audience`, `action_ask`, `framework`, `format`, `html` | unchanged | Producer extensions |

### `sources` reshaping

Arche `sources` is an array of bundle paths. OKF `sources` is an array of mappings, each requiring `resource`. Every entry gets a stable `id`, because §5.1 keys per-claim footnote attribution to `sources[].id` and warns that positional references misattribute silently when an agent reorders the list.

```yaml
# before
sources: [sources/arb-minutes.md, sources/billing-rfc.md]

# after
sources:
  - id: arb-minutes
    resource: ../sources/arb-minutes.md
    title: ARB minutes, 2026-03
  - id: billing-rfc
    resource: ../sources/billing-rfc.md
    title: Billing RFC
```

The `id` is derived from the target's slug stem, deduplicated with a numeric suffix on collision within a single page.

### Source pages: `resource` and `raw`

A source page describes one underlying asset, which is what OKF's `resource` names. The `url:` / `raw:` pair collapses:

- **Web-based source with a snapshot** — `resource:` is the canonical URL; the `raw/` snapshot becomes a `sources` entry with `id: snapshot`.
- **File-based source with no URL** — `resource:` is the bundle-relative path to the `raw/` file.

`raw:` and `url:` are removed from the schema.

### Conformance bug in `raw/` today

§11 rule 1 applies to *every non-reserved `.md` file in the tree*. `arche-ingest` currently saves pasted text into `raw/` as `.md` with no frontmatter, which violates it.

**Fix:** pasted text is captured as `.txt`. Non-`.md` files (PDFs, transcripts, HTML snapshots) are outside rule 1 entirely, so `raw/` needs no other change and is **not** renamed to `references/`.

### Actor strings (§7)

- **Skills** — `<skill-name>/<model-id>`, e.g. `arche-ingest/claude-opus-5`.
- **Humans** — `human:<id>`, where `<id>` is `git config user.email`, falling back to `git config user.name`, falling back to asking. The sample bundle uses email-shaped ids (`human:jsmith@acme`).

`generated.by` is **not** always an agent. Hand-authored pages record `generated: { by: human:… }`, matching the sample bundle. This is what `created`/`updated` never carried.

### Per-claim attribution

External-source claims use §5.1 footnotes keyed to `sources[].id`:

```markdown
Billing moved to events in Q1.[^arb-minutes]

[^arb-minutes]: ARB minutes, 2026-03
```

Inline markdown links to other Arche pages remain as they are — they are ordinary links, already conformant, and they render.

## Reserved files

### `index.md`

Frontmatter is stripped entirely. The **root** `index.md` alone may carry frontmatter, and only `okf_version: "0.2"` (§12).

Body follows §8 — sections of `* [Title](relative-path) - description.` bullets, where the description is the target's `description` field:

```markdown
# Concepts

* [Event-driven billing](concepts/adr-billing.md) - Why billing moved to events.
* [Order lifecycle](concepts/order-lifecycle.md) - States an order passes through.
```

**Per-directory `index.md` is adopted.** OKF's progressive-disclosure model lets an agent read `concepts/index.md` without loading the whole catalog. Each content subdirectory gets one; the root index links to them.

### `log.md`

Keeps frontmatter (`type: Log`, `title`). Body inverts to §9 form: `## YYYY-MM-DD` date headings, **newest first**, entries as prose bullets led by a bold verb.

Arche's op vocabulary becomes the bold lead word: `**Ingest**`, `**Query**`, `**Lint**`, `**Discovery**`, `**Architect**`, `**Story**`, `**Init**`, `**Migrate**`, `**Manual**`. Pages touched move into the prose. The `contradiction —` marker `/arche-lint` greps for stays in the prose text.

```markdown
## 2026-08-11

- **Ingest**: ARB minutes on billing. Touched `sources/arb-minutes.md`, `concepts/adr-billing.md`, `index.md`. contradiction — disputes the dating in `entities/acme.md` (struck through, replacement cited).
```

**Cost to note during implementation:** appending flips from "write at end of file" to "insert after the frontmatter block." Every skill that logs is affected.

## Trust model

Skills write `generated` on every page they touch. **Skills never write `verified`.** A `verified` entry appears only from explicit human sign-off, which keeps §5.3's tiers meaningful:

- no `verified` → **unverified**
- `verified` by non-`human:` actors only → **machine-confirmed** (the Arche does not produce this tier)
- `verified` by a `human:<id>` actor → **human-reviewed**

`/arche-lint` gains an unverified-pages report so the gap is visible and actionable, listing pages by `generated.at` age. Sign-off appends `verified: { by: human:<id>, at: <now> }`.

Per §11, a bare `verified` mapping is a one-element list; consumers must treat it as such. The Arche writes the list form once there are two or more entries.

## Conformance ownership

> **`arche-init` creates. `arche-lint` maintains.**

`arche-init` becomes **bootstrap-only**. Its migrate mode is retired, along with its ~60-line accumulated drift checklist — every check in that list is now a lint finding. Run against an existing Arche, `/arche-init` reports that one exists and points at `/arche-lint`.

`arche-lint` becomes the sole repair path for all conformance drift, content pages and system files alike. This resolves the two-writer risk temporally rather than living with it: init writes `SCHEMA.md` once at bootstrap, lint owns it thereafter.

**Template ownership.** `SCHEMA.template.md` stays in `arche-init` — it is the seed text for a file init creates — and lint reads it when patching. That is one template for one file, read by the two skills that write that one file. The `ingest`/`query`/`discover`/`architect`/`tell` page templates stay with their own skills, unchanged in ownership.

**Version-skew detection.** Lint keys off three inputs, in order:

1. `okf_version` in the root `index.md` — what the bundle was written to
2. The era `SCHEMA.md` documents
3. What the skills currently implement

Skew between any two is a finding. This is the mechanism that makes a future OKF v0.3 a lint run rather than a migration project, and it is why `okf_version` is written rather than omitted.

## Per-skill changes

| Skill | Change |
|---|---|
| **arche-init** | Bootstrap-only; migrate mode and its drift checklist removed. `index.template.md` loses frontmatter, gains `okf_version: "0.2"`, adopts §8 bullet form. `log.template.md` inverts to newest-first with `type: Log`. `SCHEMA.template.md` rewritten around the OKF field families. Creates per-directory `index.md` stubs. |
| **arche-lint** | Largest change. Gains the full conformance engine — detection and confirmed repair, content pages and system files. Absorbs init's drift checklist. Gains the unverified-pages report and version-skew detection. Gets a `references/` file for the conformance matrix to keep `SKILL.md` readable. |
| **arche-ingest** | Writes `generated`, `description`, reshaped `sources` with `id`s, `resource` in place of `url`/`raw`. Pasted text captured as `.txt`. Footnote attribution for external claims. Updates `source`, `concept`, `entity` templates. |
| **arche-architect** | ARD/SAD/ADR become `type:` values, not slug conventions. `status` moves to `draft`/`stable`/`deprecated`; `superseded_by` retained. Updates `ard`, `sad`, `adr` templates. |
| **arche-query** | Reads the new shape; filters by `type` instead of parsing `adr-*` filenames. Surfaces the trust tier of pages an answer rests on. Updates `query` template. |
| **arche-discover** | `context_pages` folds into `sources`. Updates `discovery` template. |
| **arche-tell** | Story extension keys unchanged. Flags `deprecated` or past-`stale_after` citations as stale. Updates `story` template. |
| **`SCHEMA.md`** | Rewritten: OKF field families, type taxonomy, reserved-file rules, actor convention, `okf_version`, footnote attribution. The "Conventions the human controls" section is preserved verbatim. |

### Scope note on `arche-query`

Trust-tier surfacing in `/arche-query` is a feature, not a format migration. It is kept in scope because it is small — reading `verified` and reporting a tier alongside citations — but it is the first thing to cut if the branch grows. No sign-off *workflow* is built here; that is lint's report plus a manual edit.

## Out of scope

- **Attested Computation (§10).** Executors, receipts, attesters, `runtime`, `parameters`. Nothing in the Arche computes values.
- **Bundle-absolute links.** Rejected under decision 2.
- **Renaming `raw/` to `references/`.** The `.txt` fix resolves the only conformance issue.
- **Rewriting existing Arche body prose.** Lint repairs frontmatter and reserved-file structure only; bodies are never rewritten.
- **A `verified` sign-off workflow or command.** Lint reports the gap; sign-off is a manual edit for now.

## Rollout for existing Arches

An existing Arche is **not broken** by this change. Old pages still satisfy §11's three hard rules — they have parseable frontmatter and a non-empty `type`. They are conformant but pre-v0.2: they simply lack the signal layer. There is no flag day.

The upgrade path is a single `/arche-lint` run, which reports drift and repairs it on confirmation. Bodies are untouched throughout.

## Verification

The work is done when:

1. A freshly bootstrapped Arche passes all three §11 conformance rules, checked by a **standalone script** — not by `/arche-lint`. The OKF repo ships no validator (`okf/src` is a BigQuery enrichment agent), and checking lint's output with lint is circular. The script implements §11 directly: every non-reserved `.md` has parseable frontmatter; every one has a non-empty `type`; `index.md` and `log.md` match §8 and §9. It lives in the repo as a test fixture, not shipped in any skill.
2. `/arche-lint` on a deliberately pre-v0.2 fixture Arche reports every drift class in the mapping table above, and repairs each on confirmation. After repair, the step-1 script passes on that fixture.
3. `/arche-lint` on a freshly bootstrapped Arche reports zero conformance findings.
4. Root `index.md` declares `okf_version: "0.2"`; no other `index.md` carries frontmatter.
5. `log.md` is newest-first and carries `type: Log`.
6. No `.md` file anywhere in the tree lacks frontmatter, including under `raw/`.
7. Every `arche-*` skill's templates emit the v0.2 shape, and no skill writes `verified`.
