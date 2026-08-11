---
type: Schema
title: Arche Schema
description: Conventions and operations for maintaining this Arche as an OKF v0.2 bundle.
created: {{DATE}}
generated: { by: {{ACTOR}}, at: {{TIMESTAMP}} }
---

# Arche Schema

This file tells the LLM how to maintain `./.arche/`. The operation skills read it before acting. When conventions change, edit this file rather than the skills.

Based on Andrej Karpathy's LLM Wiki pattern: humans curate, the LLM maintains. The on-disk format is [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — this Arche is a conformant OKF bundle, and `/arche-lint` keeps it that way.

## What belongs here (and what doesn't)

This Arche captures **institutional context that does not live in the code**:

- **Business domain** — customer context, product positioning, market signals, the *why* this product exists.
- **SME knowledge** — subject-matter expert insights, interview transcripts, regulatory constraints.
- **Architectural decisions (ARD, SAD, ADR)** — requirements, chosen solution, and the individual reversible decisions behind it.
- **Research** — papers, articles, competitor analyses, prior art.

This Arche **does not** capture code documentation, feature specs, implementation plans, in-flight execution state, or generated content.

**Rule of thumb:** if a question is answered by *"read the code,"* it doesn't belong here. If it's answered by *"ask the senior architect or product owner what we decided and why,"* it does.

## Three layers

1. **Raw** — immutable source files in `raw/`. PDFs, transcripts, snapshots. Never modified. Pasted text is saved as `.txt`, never `.md`, because every `.md` file in the bundle must carry frontmatter (§11 rule 1).
2. **Arche** — the markdown pages the LLM owns.
3. **Schema** — this file.

## Page types

`type` is the only always-required frontmatter key (§11 rule 2). Values are title-case singular.

| `type` | Path | Purpose |
| :--- | :--- | :--- |
| `Source` | `sources/<slug>.md` | Summary + key claims for one raw file or URL |
| `Entity` | `entities/<slug>.md` | A person, org, system, or place |
| `Concept` | `concepts/<slug>.md` | An idea, pattern, or technique |
| `Query` | `queries/<slug>.md` | A filed-back synthesis worth keeping |
| `Discovery` | `discoveries/<slug>.md` | A captured discovery / ideation session |
| `Story` | `stories/<slug>.md` | A communication artifact; pairs with `assets/stories/<slug>.html` |
| `Schema` | `SCHEMA.md` | This file |
| `Log` | `log.md` | Update history |

`index.md` carries **no** `type` — see [Reserved files](#reserved-files).

### Architecture pages

Three first-class types, forming a chain: an **ARD** frames what any architecture must satisfy, a **SAD** describes the chosen solution, and **ADRs** capture each load-bearing decision.

| `type` | Path | Slug convention | Body sections |
| :--- | :--- | :--- | :--- |
| `Architecture Requirements Document` | `concepts/ard-<system>.md` | `ard-<system>` | Stakeholders / Functional requirements / Quality attributes / Constraints / Assumptions / Risks |
| `Solution Architecture Document` | `concepts/sad-<system>.md` | `sad-<system>` | Context / Drivers / Logical view / Process view / Data view / Deployment view / Cross-cutting / Fitness functions / Decision summary / Risks and trade-offs |
| `Architecture Decision Record` | `concepts/adr-<name>.md` | `adr-<name>` | Decision / Context / Alternatives considered / Consequences |

The slug is a **naming habit, not a lookup mechanism** — find architecture pages by filtering `type`, never by parsing filenames.

**Pairing.** An ARD and SAD for the same system share the stem and link to each other. The SAD's *Decision summary* lists every ADR; each ADR cites the SAD in `sources`.

**Supersession.** Set `status: deprecated` and `superseded_by:` to the replacement page. Never delete a superseded page — the trail of "we tried X, reversed it after Y" is the institutional memory this Arche exists to preserve.

## Frontmatter

```yaml
---
type: Concept                        # REQUIRED — the only always-required key
title: Human-readable title
description: One sentence. Feeds index.md entry glosses.
resource: https://...                # canonical URI of the asset described
tags: [tag1, tag2]
created: YYYY-MM-DD                  # extension: when the page was first written
generated: { by: <actor>, at: <ISO 8601> }   # who wrote the current content
verified:                            # human sign-off only — skills never write this
  - { by: human:<id>, at: <ISO 8601> }
status: draft | stable | deprecated  # absent means stable
stale_after: YYYY-MM-DD              # content is stale on/after this date
superseded_by: ./adr-new.md          # extension: pairs with status: deprecated
sources:
  - id: stable-key
    resource: ../sources/foo.md
    title: Human-readable label
---
```

Story pages additionally carry `audience`, `action_ask`, `framework`, `format`, and `html`.

### Actors (§7)

- Skills: `<skill-name>/<model-id>`, e.g. `arche-ingest/claude-opus-5`.
- Humans: `human:<id>`, from `git config user.email`.

`generated.by` is **not** always an agent — a hand-authored page records a `human:` actor.

### Trust tiers (§5.3)

Derived from `verified`, never stored: no `verified` → **unverified**; `verified` by non-`human:` actors only → **machine-confirmed**; `verified` by a `human:` actor → **human-reviewed**.

**Skills never write `verified`.** It appears only from explicit human sign-off via `/arche-lint`.

### Sources and citation (§5.1)

`sources` is a list of mappings, each with a required `resource` and a stable `id`. The `id` is the join key for per-claim attribution, and it is keyed rather than positional because agents constantly reorder these lists.

Attribute a claim to an external source with a footnote whose label is a `sources[].id`:

```markdown
Billing moved to events in Q1.[^arb-minutes]

[^arb-minutes]: ARB minutes, 2026-03
```

Links to other Arche pages stay as ordinary inline markdown links.

## Cross-linking

- **Relative links only** — `[Title](../entities/foo.md)`. Never bundle-absolute (`/entities/foo.md`), which resolves against the repo root in GitHub and VS Code and 404s. Never `[[wikilinks]]`.
- Every entity and concept lists its sources in `sources:` and links them inline at the point of claim.
- Source pages link out to what they touch in a `## See also` section.

## Reserved files

`index.md` and `log.md` are reserved (§3.1) and must never be used for a concept page.

### index.md

Carries **no frontmatter**. The bundle-root `index.md` alone may carry frontmatter, and only `okf_version`.

Body is sections of bullets, where the gloss is the target's `description`:

```markdown
# Concepts

* [Event-driven billing](concepts/adr-billing.md) - Why billing moved to events.
```

Every content subdirectory also carries its own `index.md` for progressive disclosure, so an agent can read one directory without loading the whole catalog.

### log.md

Carries `type: Log`. Body is `## YYYY-MM-DD` date headings, **newest first**, with prose bullets led by a bold verb:

```markdown
## 2026-08-11

- **Ingest**: ARB minutes on billing. Touched `sources/arb-minutes.md`, `concepts/adr-billing.md`, `index.md`.
```

Verbs: `**Init**`, `**Ingest**`, `**Query**`, `**Lint**`, `**Discovery**`, `**Architect**`, `**Story**`, `**Manual**`.

New entries are **inserted immediately above the topmost `## YYYY-MM-DD` heading, creating today's heading if it is absent** — never appended at the end.

**Contradiction marker.** When an ingest finds a source contradicting an existing claim, the entry prose contains `contradiction —`. `/arche-lint` scans for it. A `~~strikethrough~~` claim counts as resolved when the same paragraph carries a follow-up claim with a citation.

## Slug rules

- Kebab-case, ASCII only, no dates in filenames.
- Derive: pick a stem (page title, filename, or first heading) → lowercase → strip accents → replace non-alphanumerics with `-` → collapse and trim `-`.
- On collision: byte-identical raw file means already ingested, skip; otherwise append `-2`, `-3`.
- Repeat discoveries on one topic use `-session-N`.

## Operations

- **ingest** — place the raw file in `raw/` → write a `Source` page → update the directory index and root index → revise affected pages → insert a log entry.
- **query** — read index → walk to relevant pages → answer with inline citations. File reusable syntheses as `Query` pages.
- **lint** — the maintenance operation. Checks OKF conformance (and repairs on confirmation), contradictions, stale dates, orphans, broken links, and version skew. Owns this file after bootstrap.
- **discovery** — facilitated ideation for business, domain, customer, market, or regulatory topics. Not for technical architecture.
- **architect** — convergent technical-architecture session producing ARD, SAD, and ADR pages.
- **story** — packages Arche content for an audience as `stories/<slug>.md` plus rendered HTML.

Empty subdirectories carry `.gitkeep`; this has no other meaning.

## Editing rules for the LLM

- Rewrite the whole `generated` mapping — both `by` and `at` — on every page whose content you meaningfully change. `generated.by` means *who wrote the content that is there now*, so bumping only `at` leaves the page asserting the wrong author the moment a different skill or a human edits it.
- **Never write `verified`.**
- Never delete a claim without a `~~strikethrough~~` and a log entry citing the contradicting source.
- Prefer adding to existing pages over creating near-duplicates.
- Quote sparingly. Paraphrase and cite.

## Conventions the human controls

Edit this section freely; the LLM respects it:

- **Tone**: neutral, dense, no filler.
- **Length**: source summaries ≤ 400 words; entity and concept pages grow as needed.
- **Tags**: free-form, lowercase, kebab-case.
