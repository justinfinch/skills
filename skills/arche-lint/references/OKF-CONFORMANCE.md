# OKF v0.2 conformance matrix

Every drift class `/arche-lint` detects, how to detect it, and how to repair it.
Spec pinned at `GoogleCloudPlatform/knowledge-catalog` commit `3fcbb9f`.

Repairs touch **frontmatter and reserved-file structure only**. Never rewrite body prose.

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
| T2 | `type: Concept` on a page whose filename starts `ard-`, `sad-`, or `adr-` | Promote to `Architecture Requirements Document`, `Solution Architecture Document`, or `Architecture Decision Record`. This is the **only** case where a filename prefix is authoritative, and only during this one-time promotion. |
| T3 | `type: brainstorm` (a pre-`discovery` era value) | Set `type: Discovery`. Flag the containing `brainstorms/` directory for the user; do not rename directories. |

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

## Structure

| # | Detect | Repair |
| :--- | :--- | :--- |
| S1 | A content subdirectory with no `index.md` | Create one from `arche-init`'s `subindex.template.md`, populated from the directory's pages. |
| S2 | An `index.md` entry whose gloss does not match the target's `description` | Update the gloss. |
| S3 | A bundle-absolute link (`](/`) in any page | Rewrite as relative from the containing file. |
| S4 | Root `index.md` with no `okf_version` | Add `okf_version: "0.2"`. |

## Version skew

Three inputs, compared pairwise:

1. `okf_version` in the root `index.md` — what the bundle was written to.
2. The era `SCHEMA.md` documents — detected from its type taxonomy and field families.
3. What these skills implement — currently **0.2**.

Any mismatch is a finding. Report the direction: a bundle behind the skills needs repair; a bundle ahead of the skills means the skills need upgrading, and repair must **not** run.
