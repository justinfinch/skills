# skills

Justin Finch's library of agent skills. Compatible with the open [agent skills](https://agentskills.io) ecosystem — install with the [vercel-labs/skills](https://github.com/vercel-labs/skills) CLI.

## Install

```bash
# Install all skills to your detected agents
npx skills add justinfinch/skills

# Install a specific skill
npx skills add justinfinch/skills --skill write-a-skill

# Install globally (available across all projects)
npx skills add justinfinch/skills -g
```

## Layout

```
skills/
├── <skill-name>/              # arche-*, devbox-*, write-*
│   └── SKILL.md
└── guidance/                  # packs grouped: content, not workflows
    └── guidance-<topic>/
        └── SKILL.md
```

One directory per skill, each containing a `SKILL.md` with YAML frontmatter
(`name`, `description`).

| Prefix | Kind |
| :--- | :--- |
| `arche-*` | Workflows that act on the repo's Arche |
| `devbox-*` | Workflows that act on the repo's dev environment |
| `guidance-*` | Knowledge that is consulted and cited; never runs |
| `write-*` | Tools that author the other kinds |

The prefix says what kind of thing a skill is, and it does the real work: skills
install into one flat namespace alongside everyone else's, where a directory
here is invisible. Guidance packs additionally sit under a `guidance/` category
directory, because they are content rather than workflows and will outnumber
everything else as the library grows.

Two constraints that make this layout work. The installer walks each container
directory up to three levels deep, so a category directory is discovered
normally. And `name` must match its **own** parent directory — not the path — so
a pack keeps the `guidance-` prefix in its directory name rather than shortening
to `ddd` and losing the prefix at install time. `skills/guidance/guidance-ddd/`
reads redundantly in the tree and never appears that way anywhere else.

## Skills

- **[write-a-skill](skills/write-a-skill/SKILL.md)** — meta-skill that walks the agent through authoring new skills.
- **[devbox-init](skills/devbox-init/SKILL.md)** — scaffold an isolated, declarative dev env (Devbox + direnv) for the current repo; agent-agnostic, with an optional Claude-Code-only env-snapshot hook.
- **[devbox-add](skills/devbox-add/SKILL.md)** — add an infra dep (db/queue/cache/search) or app dep to the repo's `devbox.json` instead of installing on the host; wires `devbox services` and records the policy in the repo's agent context file.
- **[arche-init](skills/arche-init/SKILL.md)** — bootstrap-only: creates an Arche at `./.arche/` (Karpathy's LLM-wiki pattern) — schema, index, log — as a conformant OKF v0.2 bundle. Also registers the Arche in the repo's agent context file(s) (`AGENTS.md` / `CLAUDE.md` / `.cursorrules`, …) so coding agents pick it up automatically rather than waiting to be told. Arche captures institutional context — business/domain/SME/ARB — not code documentation. `/arche-lint` owns migration and ongoing conformance from here on.
- **[arche-ingest](skills/arche-ingest/SKILL.md)** — ingest a source (URL/file/text/SME-interview/ADR) into the Arche and update affected pages.
- **[arche-query](skills/arche-query/SKILL.md)** — answer a question from the Arche with inline citations; also fires as a cold-start orientation step before planning/design in agentic dev workflows.
- **[arche-discover](skills/arche-discover/SKILL.md)** — facilitated discovery / ideation session grounded in Arche context, for business/domain/architectural topics (not implementation design). Files the session and promotes top ideas back to concept/entity pages (including new ADRs).
- **[arche-architect](skills/arche-architect/SKILL.md)** — convergent technical-architecture skill: panel of senior-architect lenses, files Architecture Requirements Document, Solution Architecture Document, and Architecture Decision Record pages.
- **[arche-tell](skills/arche-tell/SKILL.md)** — interview the user on audience + action ask + narrative framework, then produce a shareable HTML artifact (reveal.js deck or scrollable narrative) for communicating Arche content. Files `stories/<slug>.md` + `assets/stories/<slug>.html`.
- **[arche-lint](skills/arche-lint/SKILL.md)** — audit the Arche for contradictions, stale dates, orphans, broken links, gaps, discovery-promotion drift; owns OKF v0.2 conformance detection and repair, including migrating an older Arche to the current era.
- **[guidance-ddd](skills/guidance/guidance-ddd/SKILL.md)** — the first guidance pack: strategic domain-driven design, led by the page arguing when *not* to adopt it. Covers bounded-context boundaries, context-map relationships, and aggregate sizing; tactical patterns are deliberately out of scope.
- **[guidance-tenant-isolation](skills/guidance/guidance-tenant-isolation/SKILL.md)** — multi-tenant isolation and authorization: Postgres RLS as the database-level tenant backstop behind application filters, per-transaction tenant context, and strictly-narrowing authorization gates through a single evaluator for within-tenant access. Not an auth-provider comparison, not encryption or residency.
- **[guidance-event-delivery](skills/guidance/guidance-event-delivery/SKILL.md)** — reliable event delivery from a relational system of record: the transactional outbox, a single relay claiming rows and publishing under the row id, a durable broker fanning out to independent consumers, and end-to-end idempotency keys — including when `LISTEN/NOTIFY` is still enough. Not event sourcing as a persistence model, not a broker product comparison.
- **[guidance-fitness-functions](skills/guidance/guidance-fitness-functions/SKILL.md)** — architectural fitness functions: encoding each load-bearing decision as a named CI check in a static and an integration/nightly lane, so erosion fails a build rather than surfacing in production, plus the registry tracking each check's name, enforcement point, lane, and status. Not general test strategy or coverage practice.
- **[write-guidance](skills/write-guidance/SKILL.md)** — author or extract a guidance pack: extract mode generalizes recurring decisions out of existing project Arches into "applies when" conditions, author mode works greenfield, revise mode refreshes a pack that aged out. Uses the architect lenses adversarially and refuses to file a pack with an empty "Doesn't apply when".

### Open Knowledge Format

The Arche is a conformant [Open Knowledge Format v0.2](spec/okf/v0.2/SPEC.md) bundle — a directory of markdown files with YAML frontmatter, carrying OKF's provenance (`sources`), trust (`generated`, `verified`), and lifecycle (`status`, `stale_after`) families. That means any OKF-aware tool can read your Arche, and the format is portable off these skills entirely.

`/arche-init` creates the bundle; `/arche-lint` maintains it, including upgrading an older Arche to the current OKF era. `tools/okf_conformance.py` is a standalone checker used to verify lint against something independent of itself.

The spec is vendored, unmodified and pinned, at [`spec/okf/v0.2/`](spec/okf/v0.2/) (Apache-2.0, quarantined from this repo's MIT license) so every `§` citation in the skills resolves locally and survives upstream renumbering — see its [PROVENANCE.md](spec/okf/v0.2/PROVENANCE.md). Worth knowing what conformance actually costs: §11 requires only parseable frontmatter, a non-empty `type`, and well-formed `index.md` / `log.md`. Everything else the Arche does — the type taxonomy, the field families, the index glosses — is house convention layered on top, and §11 explicitly forbids consumers from rejecting a bundle over unknown types, missing indexes, or broken links. Your Arche stays readable by any OKF tool even when `/arche-lint` has plenty to say about it.

### Guidance packs

A `guidance-*` skill is a **pack**: durable architectural knowledge that travels
between projects, packaged as an installable skill whose `bundle/` is an OKF v0.2
bundle of `Guidance` pages, plus whatever supporting `Concept` pages the topic
needs — a roster, a taxonomy, a comparison table.

```
skills/guidance/guidance-<topic>/
  SKILL.md       # relevance trigger; thin by design
  bundle/
    index.md     # frontmatter carries okf_version and nothing else
    concepts/<slug>.md
```

Packs are deliberately **not** part of the Arche, and never get copied into one.
The Arche holds what *this* organization decided; a pack holds knowledge that is
true whether or not the organization exists. Those have different provenance
(`generated.by` means nothing for a pack someone else wrote), different lifecycle
(Arche pages accrete, packs are versioned dependencies), and different audiences.

What connects them is citation. A `Guidance` page states when a technique is the
right call and — the load-bearing half — when it isn't:

```markdown
## Applies when
- Single relational store, and the write and the publish must not diverge.

## Doesn't apply when
- Your broker supports transactional publish.
- You can tolerate lost events.
```

`/arche-architect` consults installed packs during a **grill** — its interview
phase, where every branch of the design gets pushed on one question at a time —
and cites the pages that informed a decision in the ADR's `sources:`, by their
host-independent `<pack-name>/<path-within-bundle>` identity. So a new project
doesn't inherit old answers — it inherits the trade-off space already framed, and the
ADR that comes out is genuinely its own. When a decision area has no pack
covering it, the grill says so; that gap signal is what `/write-guidance`
consumes, and the loop is why the next project doesn't start from scratch.

Packs carry no `log.md` — git history is the changelog.

## Why "Arche"?

**ἀρχή** (*arche*, "AR-kay") — Greek for *the beginning, the first principle, the foundational source from which what follows derives*. The pre-Socratics used it for the underlying thing from which everything else proceeds; Aristotle for the starting point of a chain of reasoning.

The `arche-*` skills cover the **before-development workflow most coding agents skip** — gathering institutional context (business, SME knowledge, ARB decisions, research) *before* anyone writes code. Etymologically, *arche* is also the root of "architect" (ἀρχή + τέκτων, "master builder of first principles") — so `arche-architect` is recursively apt.

## The Arche workflow

The `arche-*` skills implement [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern, pointed at **institutional context**: business domain, SME knowledge, ARB-style architectural decisions, and research. The Arche sits **adjacent to the code**, never derived from it.

Together they form a self-contained **context-gathering workflow** — the *arche* (first-principles) phase that most coding agents skip. The Arche stops at the **institutional-context boundary**: it captures the business/SME/decision/research context and the architecture, then hands that grounding to whatever spec, plan, and implementation skills you already use. It does **not** ship its own specify/plan/build skills — those belong to your dev-methodology library ([github/spec-kit](https://github.com/github/spec-kit), [obra/superpowers](https://github.com/obra/superpowers), [mattpocock/skills](https://github.com/mattpocock/skills), your own). The integration is the AGENTS.md registration `arche-init` writes (see [below](#how-the-agentsmd-registration-bridges-to-your-dev-skills)): it tells any agent — including those external skills — to consult the Arche first. The Arche **complements** your workflow by feeding it grounded context; it doesn't reimplement it.

```
Your dev-methodology skills    (spec • plan • execute • TDD • review • ship)
  spec-kit / superpowers / mattpocock / your own — grounded by reading the Arche
              ▲
              │ AGENTS.md says "consult ./.arche/ first" → they pick it up automatically
              │
Arche workflow      (the context-gathering phase, built from first principles)
  ingest → query → discover → architect → tell → lint
              ▲
              │ reads / writes
              │
Context layer       (the Arche)
  entities • concepts (incl. ARD/SAD/ADRs) • sources • discoveries • queries • stories
              ▲
              │ ingests / discoveries
              │
Raw layer           (.arche/raw/)
  research papers • SME interview transcripts • ADRs as decisions land
```

### How the skills work together

- **Bring sources in** — `arche-ingest` files a competitor analysis, an SME interview transcript, or an external ADR. The Arche grows by deliberate curation, not by accretion from coding sessions.
- **Orient before any work** — `arche-query` is the canonical cold-start step. Before planning, design, scoping, or a setup decision, it surfaces relevant ADRs, domain constraints, customer context, and prior research so the work is informed by what the institution already knows. So this happens *without the user having to ask*, `arche-init` registers the Arche in the repo's agent context files: it writes a `<!-- arche-context-source -->` snippet to `AGENTS.md` (the cross-agent source of truth) and, since [Claude Code reads `CLAUDE.md` not `AGENTS.md`](https://code.claude.com/docs/en/memory), bridges it with a one-line `@AGENTS.md` import in `CLAUDE.md` (no agent detection, no duplicated content). That always-loaded instruction tells any coding agent to consult `./.arche/` before such work, making the Arche a first-class context source rather than a skill someone has to remember to invoke.
- **Diverge on the business** — `arche-discover` facilitates ideation for product strategy, new direction, or regulatory option-mapping, then files the session and promotes top ideas back to the Arche.
- **Converge the HOW** — `arche-architect` runs a panel-of-architects interview and files ARD, SAD, and ADR pages, grounded in the discovery and research already in the Arche.
- **Communicate it** — `arche-tell` packages Arche content into a shareable deck or narrative for a defined audience and ask.
- **Keep it healthy** — `arche-lint` audits for contradictions, stale dates, orphans, broken links, and gaps.

The workflow stops at the **institutional-context boundary**. Specifying a feature (WHAT/WHY), planning the build (the HOW-sequence), the build itself, code-implementation brainstorming (how to refactor a module, how to structure tests), and the transient execution state all belong to your dev-methodology library. The Arche feeds those skills the grounded *why* and the architecture *how*, then gets out of the way. The next section explains the one mechanism that makes that handoff automatic.

### How the AGENTS.md registration bridges to your dev skills

Earlier versions of this library shipped `arche-specify` and `arche-plan` skills — an Arche-native spec step and an Arche-native plan step. **They were removed.** Owning the spec and the plan meant reimplementing what mature dev-methodology libraries already do well, and it pulled the Arche across its own boundary: a spec and a plan are *implementation artifacts*, not institutional context. The cleaner design is for the Arche to **ground** those steps rather than perform them.

The bridge is the snippet `arche-init` writes into the repo's agent context files. It registers the Arche as a first-class, always-loaded context source:

- `arche-init` writes a `<!-- arche-context-source -->` block to **`AGENTS.md`** (the cross-agent source of truth) and, since [Claude Code reads `CLAUDE.md` not `AGENTS.md`](https://code.claude.com/docs/en/memory), bridges it with a one-line `@AGENTS.md` import in `CLAUDE.md` — no agent detection, no duplicated content.
- That block instructs **any** agent — including a spec, plan, or implementation skill from another library — to read `./.arche/index.md` and walk to the relevant decisions, constraints, and research *before* proposing an approach.

So when you run spec-kit's `/specify`, a superpowers planning skill, or your own implementation agent in a repo with an Arche, it is told to consult the Arche first. The grounded context flows into those skills automatically; the spec/plan/build artifacts they produce stay where they belong — in your dev workflow, the PR, and the working tree — not in the Arche.

This is why the Arche skills are **built by learning from** the best dev-methodology libraries — [obra/superpowers](https://github.com/obra/superpowers), [mattpocock/skills](https://github.com/mattpocock/skills), [github/spec-kit](https://github.com/github/spec-kit) — without wrapping or depending on them at runtime: proven techniques re-grounded in the Arche for the *context* phase, with the *implementation* phase left to whichever of those libraries you already run.

### What the Arche does *not* do

- It does not own specs, plans, or any implementation artifact. Feature specs (WHAT/WHY) and implementation plans (the task decomposition) are produced by your dev-methodology skills, which *read* the Arche for grounding via the AGENTS.md registration. The Arche holds durable, curated *intent and decisions* — not the artifacts derived downstream of them.
- It is not a dumping ground for in-flight TODOs or debugging notes — those stay in your working artifacts (PR descriptions, commit messages).
- It is not a substitute for episodic conversation memory like [obra/episodic-memory](https://github.com/obra/episodic-memory) — that's a separate, complementary layer (raw recall vs. curated synthesis). Both can coexist.
- It is not code documentation. If a question is answered by *reading the code*, the Arche is the wrong place.

### Location

By convention the Arche lives at `./.arche/` in the repo (dotted, like `.claude/` and `.vscode/`) so it doesn't collide with content folders. For monorepos, one Arche at the repo root covers cross-cutting concerns across services.

## Add a new skill

Two options:

1. Invoke the bundled `write-a-skill` skill and follow its workflow.
2. Run the CLI scaffolder from inside `skills/`:
   ```bash
   cd skills && npx skills init my-new-skill
   ```

Either path produces a directory with a valid `SKILL.md`. Commit and push.

## References

- [Agent Skills Specification](https://agentskills.io)
- [vercel-labs/skills](https://github.com/vercel-labs/skills) — the installer CLI
- [skills.sh](https://skills.sh) — public skill directory

## Credits

The `write-a-skill` seed is adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT).

## License

MIT — see [LICENSE](LICENSE).
