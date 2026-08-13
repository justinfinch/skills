# OKF v0.2 conformance matrix

Every drift class `/arche-lint` detects, how to detect it, and how to repair it.
Spec pinned at `GoogleCloudPlatform/knowledge-catalog` commit `3fcbb9f`.

Repairs touch **frontmatter and reserved-file structure only**. Never rewrite body prose.
The one exception is `SCHEMA.md`, which is not authored prose — see [Schema era](#schema-era).

**Order matters twice over.**

**Schema era first.** If [SC1](#schema-era) fires, apply it before anything else
and re-read `SCHEMA.md` afterward. `SCHEMA.md` is what defines "valid" for the
rest of this matrix: T4 checks `type` values against the page types it declares,
F9 checks key shapes against its frontmatter spec, and F5 maps `status` into the
vocabulary it adopts. Run the page rules against a stale schema and they fight
each other — T2 promotes an ADR to `Architecture Decision Record`, then T4 flags
that very value as unrecognized, because the old schema has never heard of it.

**Then rule group by rule group, in table order** — hard conformance, then type
taxonomy, then field families, then structure — never page by page. Several rules
consume what an earlier rule produces (T2 matches the value T1 normalizes; F5's
`superseded_by` check assumes F1 has already run), so a repairer that walks a
single page through the whole matrix before moving to the next one silently
skips the dependent half.

## Hard conformance (§11)

| # | Detect | Repair |
| :--- | :--- | :--- |
| H1 | A non-reserved `.md` file with no parseable frontmatter block | If under `raw/`, rename to `.txt` (raw files are immutable, so they can never carry frontmatter) **and** rewrite every `resource:` and `sources[].resource` in the bundle that pointed at the old name. Renaming without repointing manufactures a broken link plus an orphan-raw finding and invites a duplicate re-ingest; the pointers are frontmatter, so rewriting them stays inside the never-rewrite-body-prose boundary. Otherwise add a frontmatter block, inferring `type` per H2. |
| H2 | Frontmatter with no `type`, or an empty one | Set `type` from the directory: `sources/`→`Source`, `entities/`→`Entity`, `concepts/`→`Concept`, `queries/`→`Query`, `discoveries/`→`Discovery`, `stories/`→`Story`. Bundle-root files are not covered by the directory rule — use the filename: `SCHEMA.md`→`Schema`, `log.md`→`Log`. (`index.md` carries no `type` at all — see H3.) |
| H3 | A non-root `index.md` carrying frontmatter, or a root `index.md` carrying keys other than `okf_version` | Strip the frontmatter. On the root index, replace it with `okf_version: "0.2"`. |
| H4 | `log.md` with non-ISO `## ` date headings, or headings not ordered newest first | Rewrite headings to `## YYYY-MM-DD` and sort the date groups descending, moving each group's bullets with it. Preserve every entry's prose verbatim. |

## Type taxonomy

| # | Detect | Repair |
| :--- | :--- | :--- |
| T1 | A lowercase `type` value (`source`, `entity`, `concept`, `query`, `discovery`, `story`, `schema`, `log`) | Title-case it. `index` is removed entirely (see H3). |
| T2 | A `Concept` type **in any casing** on a page whose filename starts `ard-`, `sad-`, or `adr-` | Promote to `Architecture Requirements Document`, `Solution Architecture Document`, or `Architecture Decision Record`. This is the **only** case where a filename prefix is authoritative, and only during this one-time promotion. Match case-insensitively: a pre-OKF Arche carries `type: concept`, so a T2 that only saw title-case would leave every migrated ADR untyped as an architecture page — and since `/arche-query` and `/arche-architect` find these pages by filtering `type` and never by filename, an unpromoted ADR is invisible to both. |
| T3 | `type: brainstorm` (a pre-`discovery` era value) | Set `type: Discovery`. Flag the containing `brainstorms/` directory for the user; do not rename directories. |
| T4 | After T1–T3, a `type` value that is not one of the page types `SCHEMA.md` defines (`Source`, `Entity`, `Concept`, `Query`, `Discovery`, `Story`, `Schema`, `Log`, `Architecture Requirements Document`, `Solution Architecture Document`, `Architecture Decision Record`) | Report the page, its directory, and the value found — a casing slip (`Architecture Decision record`), a retired era value (`Spec`, `Plan`), or a type the user added on purpose. Do **not** guess: name the directory-implied type from H2 as the likely intent and ask. This row is the catch-all that keeps T1–T3 from being a closed list — an unrecognized `type` passes §11.2 (it is a non-empty string) but is invisible to every skill that filters on `type`. |

## Field families (§5)

| # | Detect | Repair |
| :--- | :--- | :--- |
| F1 | `updated:` present, `generated:` absent | `generated: { by: <actor>, at: <updated as ISO 8601, midnight UTC> }`. Resolve `<actor>` in this order: (1) a `human:` actor built from `git config user.email`, since a page with no agent provenance was hand-authored; (2) failing that, `arche-lint/<model-id>`. Remove `updated:`. |
| F2 | `created:` present | Keep. It is a permitted extension with no OKF equivalent. |
| F3 | `sources` is a list of strings | Convert each to `{ id, resource, title }`. The `id` is the target's slug stem; `resource` is the path to the target relative to the page containing it (e.g. `../raw/foo.txt` from a page in `sources/`), never a path from the bundle root and never leading with `/`; `title` is the target's `title` if readable. |
| F4 | `description` absent | Report. Do **not** invent one — a description is a summary of body prose, and generating it is authoring, not repair. Offer to draft one interactively. |
| F5 | `status: proposed \| accepted \| superseded` | Map to `draft \| stable \| deprecated`. When mapping `superseded`, require `superseded_by:`; if absent, report it as needing manual attention. |
| F6 | `raw:` or `url:` on a Source page | `url:` becomes `resource:`. `raw:` becomes a `sources` entry with `id: snapshot`. When only `raw:` exists, it becomes `resource:` instead. |
| F7 | `context_pages:` on a Discovery page | Merge its entries into `sources` as mappings; remove the key. |
| F8 | `verified` written by a non-`human:` actor | Report only. The Arche never machine-verifies, so this indicates hand-editing or an external producer. Never strip it — §11 forbids rejecting a concept over an optional family. |
| F9 | Any key whose **shape** contradicts `SCHEMA.md`'s frontmatter spec: `generated:` as a scalar rather than a `{ by, at }` mapping, `sources:` as anything but a list, `tags:` as a bare string, a `created:` / `stale_after:` that is not an ISO date, a `verified:` that is neither a mapping nor a list of them | Repair where the intent is unambiguous — `generated: 2026-01-01` → `generated: { by: <actor per F1>, at: 2026-01-01T00:00:00Z }`, `tags: billing` → `tags: [billing]`. Report the rest. This is the catch-all: F1–F8 name the drift classes seen in the wild, and this row exists so a class nobody enumerated is still caught rather than passing clean. A malformed `generated:` in particular is invisible to the stale-date check, which reads `generated.at` and silently skips a page where that lookup fails. |

## Structure

| # | Detect | Repair |
| :--- | :--- | :--- |
| S1 | A content subdirectory with no `index.md` | Create one. The stub is a heading and a placeholder — no frontmatter, per H3:<br>`# <Singular type name>`<br><br>`_None yet._`<br>Then populate it with an `* [Title](path) - description.` entry per page in the directory. Inlined here rather than read from `arche-init`'s `subindex.template.md` so this repair works when `arche-lint` is installed on its own. |
| S2 | An `index.md` entry whose gloss does not match the target's `description` | Update the gloss to the target's `description`. **Only fires when the target actually carries a `description`.** Entries pointing at a per-directory `index.md` carry no `description` to compare against — non-root indexes carry no frontmatter at all (H3) — and neither do the `SCHEMA.md` and `log.md` entries under the root index's `# Bundle` section. Those glosses are hand-written navigation text seeded at bootstrap: skip them entirely. Flagging them would fire on every freshly bootstrapped, fully conformant Arche, and applying the repair would blank the eight glosses `arche-init` deliberately wrote. |
| S3 | A bundle-absolute link (`](/`) in any page | Rewrite as relative from the containing file. |
| S4 | Root `index.md` with no `okf_version` | Add `okf_version: "0.2"`. |

## Version skew

Three inputs, compared pairwise:

1. `okf_version` in the root `index.md` — what the bundle was written to.
2. The era `SCHEMA.md` documents — detected from its type taxonomy and field families.
3. What these skills implement — currently **0.2**.

Any mismatch is a finding. Report the direction: a bundle behind the skills needs repair; a bundle ahead of the skills means the skills need upgrading, and repair must **not** run.

## Schema era

**This runs first.** Everything above reads `SCHEMA.md` as the definition of
valid, so the overlay has to land before the page rules do — see [Order matters
twice over](#okf-v02-conformance-matrix) at the top. It is documented last only
because it is the rule most Arches never need.

`SCHEMA.md` is the one file where repair reaches past frontmatter. It is not
authored prose — it is `arche-init`'s template rendered once at bootstrap, and it
is what every other `arche-*` skill preflights against. `/arche-architect`,
`/arche-discover`, and `/arche-tell` all refuse to run when it documents an older
era, so if nothing can rewrite it, an Arche created before the current era is
permanently frozen: init stops because `./.arche/` exists, and the operation
skills stop because the schema is stale. This section is what breaks that
deadlock.

| # | Detect | Repair |
| :--- | :--- | :--- |
| SC1 | `SCHEMA.md` documents an older era — its type taxonomy is missing `Architecture Requirements Document` / `Solution Architecture Document` / `Architecture Decision Record`, its frontmatter spec is missing `generated` / `verified` / `stale_after`, its `status` vocabulary still reads `proposed \| accepted \| superseded`, or it still defines retired `spec` / `plan` page types or `specify` / `plan` log ops | Overlay the current template section by section. Never regenerate the whole file — a user who edited their conventions keeps those edits. |

**How to overlay.** Read `arche-init`'s [SCHEMA.template.md](../arche-init/assets/SCHEMA.template.md), diff it against the bundle's `SCHEMA.md` heading by heading, and show the user the per-section plan before writing:

- **Section missing from `SCHEMA.md`** → add it verbatim from the template.
- **Section present but documenting an older era** → replace that section's body with the template's, and say so in the plan. This is the only place body text is rewritten, and only for sections the template owns.
- **Section present in `SCHEMA.md` but not in the template** → leave it. It is a user convention, not drift.
- **Retired constructs** (`spec` / `plan` page types, `specs/` / `plans/` rows, `specify` / `plan` log ops, `## Specs` / `## Plans` index sections) → remove, and report any pages that still carry the retired type so T4 can pick them up.

Then set `okf_version: "0.2"` on the root index (S4) and log the era change.

**If `arche-init` is not installed alongside this skill**, its template is
unreachable. Report SC1 as detected-but-unrepairable and tell the user to install
`arche-init` to enable the overlay. Do **not** reconstruct the schema from
memory — an improvised `SCHEMA.md` becomes the authority every other skill reads,
so a plausible-looking reconstruction is worse than leaving the drift visible.
