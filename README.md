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
└── <skill-name>/
    └── SKILL.md
```

Flat — one directory per skill, each containing a `SKILL.md` with YAML frontmatter (`name`, `description`).

## Skills

- **[write-a-skill](skills/write-a-skill/SKILL.md)** — meta-skill that walks the agent through authoring new skills.
- **[devbox-init](skills/devbox-init/SKILL.md)** — scaffold an isolated, declarative dev env (Devbox + direnv) for the current repo; agent-agnostic, with an optional Claude-Code-only env-snapshot hook.
- **[devbox-add](skills/devbox-add/SKILL.md)** — add an infra dep (db/queue/cache/search) or app dep to the repo's `devbox.json` instead of installing on the host; wires `devbox services` and records the policy in the repo's agent context file.
- **[arche-init](skills/arche-init/SKILL.md)** — bootstrap an Arche at `./.arche/` (Karpathy's LLM-wiki pattern): schema, index, log. Also registers the Arche in the repo's agent context file(s) (`AGENTS.md` / `CLAUDE.md` / `.cursorrules`, …) so coding agents pick it up automatically rather than waiting to be told. Arche captures institutional context — business/domain/SME/ARB — not code documentation.
- **[arche-ingest](skills/arche-ingest/SKILL.md)** — ingest a source (URL/file/text/SME-interview/ADR) into the Arche and update affected pages.
- **[arche-query](skills/arche-query/SKILL.md)** — answer a question from the Arche with inline citations; also fires as a cold-start orientation step before planning/design in agentic dev workflows.
- **[arche-discover](skills/arche-discover/SKILL.md)** — facilitated discovery / ideation session grounded in Arche context, for business/domain/architectural topics (not implementation design). Files the session and promotes top ideas back to concept/entity pages (including new ADRs).
- **[arche-specify](skills/arche-specify/SKILL.md)** — convergent feature-specification skill: grills out a technology-agnostic WHAT/WHY spec (testable requirements, measurable success criteria, user scenarios, ubiquitous language) grounded in Arche context, files it as a `spec-<feature>` page, and hands off to `arche-architect`. Sits between discover and architect.
- **[arche-architect](skills/arche-architect/SKILL.md)** — convergent technical-architecture skill: panel of senior-architect lenses, files ARD/SAD/ADR concept pages.
- **[arche-plan](skills/arche-plan/SKILL.md)** — convergent implementation-planning skill: turns an accepted spec into an executable, dependency-ordered plan (file/interface map, right-sized tasks, traceability), grounded in the spec + SAD/ADRs. Runs an architect gap-check first — halts and routes to `arche-architect` if the design isn't settled — then files a `plan-<feature>` page and hands off to your dev methodology to execute. Sits between architect and the build.
- **[arche-tell](skills/arche-tell/SKILL.md)** — interview the user on audience + action ask + narrative framework, then produce a shareable HTML artifact (reveal.js deck or scrollable narrative) for communicating Arche content. Files `stories/<slug>.md` + `assets/stories/<slug>.html`.
- **[arche-lint](skills/arche-lint/SKILL.md)** — audit the Arche for contradictions, stale dates, orphans, broken links, gaps, discovery-promotion drift.

## Why "Arche"?

**ἀρχή** (*arche*, "AR-kay") — Greek for *the beginning, the first principle, the foundational source from which what follows derives*. The pre-Socratics used it for the underlying thing from which everything else proceeds; Aristotle for the starting point of a chain of reasoning.

The `arche-*` skills cover the **before-development workflow most coding agents skip** — gathering institutional context (business, SME knowledge, ARB decisions, research) *before* anyone writes code. Etymologically, *arche* is also the root of "architect" (ἀρχή + τέκτων, "master builder of first principles") — so `arche-architect` is recursively apt.

## The Arche workflow

The `arche-*` skills implement [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern, pointed at **institutional context**: business domain, SME knowledge, ARB-style architectural decisions, and research. The Arche sits **adjacent to the code**, never derived from it.

Together they form a self-contained **before-development workflow** — the *arche* (first-principles) phase that most coding agents skip. We don't wrap or depend on third-party agentic methodologies at runtime. Instead, each `arche-*` skill is **built by learning from** the best of them — [obra/superpowers](https://github.com/obra/superpowers), [mattpocock/skills](https://github.com/mattpocock/skills), [github/spec-kit](https://github.com/github/spec-kit) — and re-grounding their proven techniques in the Arche. Proven shape, Arche-native ties, no external coupling. The grounded context and decisions then feed whatever implementation workflow you use; the Arche **complements** that workflow, it doesn't plug into it.

```
Your implementation workflow   (execute • TDD • review • ship — methodology-agnostic)
              ▲
              │ consumes the plan + grounded context + decisions
              │
Arche workflow      (the before-development phase, built from first principles)
  ingest → query → discover → specify → architect → plan → tell → lint
              ▲
              │ reads / writes
              │
Context layer       (the Arche)
  entities • concepts (incl. ADRs) • specs • plans • sources • discoveries • queries
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
- **Converge the WHAT/WHY** — `arche-specify` grills out a technology-agnostic `spec-<feature>` page, grounded in Arche context, then hands off to architecture. The bridge: `discover → specify → architect`.
- **Converge the HOW** — `arche-architect` runs a panel-of-architects interview and files ARD/SAD/ADR concept pages, citing the spec back.
- **Sequence the build** — `arche-plan` turns an accepted spec into an executable `plan-<feature>` page: a file/interface map and dependency-ordered, reviewable tasks, each traced to a requirement and a filed decision. It gap-checks the architecture first and routes back to `arche-architect` if a decision is missing, so a plan never quietly invents design. The bridge: `architect → plan → execute`.
- **Communicate it** — `arche-tell` packages Arche content into a shareable deck or narrative for a defined audience and ask.
- **Keep it healthy** — `arche-lint` audits for contradictions, stale dates, orphans, broken links, and gaps.

The workflow stops at the **execution boundary**. `arche-plan` produces the durable plan-of-record (the decomposition, grounded and traced) but does not run it — the build itself, code-implementation brainstorming (how to refactor a module, how to structure tests), and the transient execution state belong to your implementation workflow. The Arche feeds it the grounded *why*, *what*, and *how-sequence*, then gets out of the way.

### Anatomy of `arche-specify` — composing proven skills

`arche-specify` exists to fill the gap between *"we've decided what business problem to chase"* (`arche-discover`) and *"here's how we'll build it"* (`arche-architect`). That middle step — a crisp, testable, technology-agnostic statement of **what** a feature must do and **why** — is where coding agents most often hallucinate scope. Rather than invent a method, the skill composes three battle-tested ones and re-anchors them to the Arche.

**The spine — [superpowers/brainstorming](https://github.com/obra/superpowers).** Sets the session shape: a convergent, one-question-at-a-time interview (recommendation-first, matching the `arche-architect` house style), a self-review pass for placeholders/contradictions/ambiguity, a hard user-approval gate before any handoff, and YAGNI surfaced as explicit **non-goals**.

**The temperament — [mattpocock/grill-with-docs](https://github.com/mattpocock/skills).** A relentless branch-by-branch grill that resolves dependencies before moving on, plus a **ubiquitous-language** discipline — define *what things are*, not what they do, with aliases-to-avoid. The adaptation: grill-with-docs writes a standalone `CONTEXT.md` glossary; we don't, because **the Arche is the glossary** — terms reconcile against existing `entities/` and `concepts/` pages and cite them back.

**The rigor — [github/spec-kit](https://github.com/github/spec-kit) `specify`.** The discipline of the artifact itself: **WHAT/WHY, never HOW** (a technology name in a spec is treated as a defect), testable functional requirements (`FR-n`), measurable and technology-agnostic success criteria (`SC-n`), `[NEEDS CLARIFICATION]` markers capped at three and impact-prioritized (scope > security > UX > technical), and a requirements-quality gate. The adaptation: spec-kit keeps the checklist in a sidecar file; we **fold it into the spec page** as a `## Quality gate` section so the artifact stays self-contained.

**The connective tissue none of the three had — grounding.** The skill loads context through `arche-query` (not ad-hoc reads), so requirements and language *descend from* filed business/SME/decision context; it stores the result as a first-class `spec-<feature>` page; and it forward-links to the ARD/SAD that `arche-architect` later derives — closing the loop. The formula, in short: **superpowers shape + grill-with-docs temperament + spec-kit rigor, all re-anchored to read from and write into the Arche instead of loose files.**

A spec is implementation-adjacent, which brushes the Arche's "institutional context, never derived from code" rule. It earns its place because a spec is **upstream-of-code *intent*, not derived-from-code documentation** — which is exactly what *arche* (ἀρχή, "the beginning") names.

### Anatomy of `arche-plan` — one proven skill, two Arche-native ties

`arche-plan` fills the last step before the build: turning an accepted `spec-<feature>` and its settled architecture into an executable, dependency-ordered plan. Unlike `arche-specify` (which braids three sources), it adapts **one** battle-tested skill and adds two ties the original didn't have — grounding and an architect gate.

**The source — [superpowers/writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).** The artifact discipline, kept whole: write the plan as if the engineer has *zero context for the codebase and questionable taste*, so everything is exact — complete file paths, a file/interface map decided up front, **right-sized tasks** (the smallest unit worth independent review), interface consistency across tasks (if Task 1 produces `clearLayers()`, Task 5 consumes `clearLayers()`, never `resetLayers()`), a **no-placeholder** rule ("TBD", "add error handling", "similar to Task N" are defects), and a self-review pass. The TDD step ritual (write failing test → run → implement → verify → commit) is kept as the **default**, but made *swappable*: the durable contract is the decomposition + interfaces + traceability, so the plan plugs into superpowers' own executors, mattpocock, or your own — **no hard dependency** on any one execution skill. That keeps the Arche methodology-agnostic; superpowers hard-wires its own `subagent-driven-development` / `executing-plans` handoff, we only *recommend* one.

**Tie one — grounding.** The skill loads the spec, SAD, and ADRs through `arche-query` (not ad-hoc reads), so every task descends from a filed requirement and a filed decision, and file paths/interfaces are reconciled against the real codebase rather than guessed. A `## Traceability` table makes the loop checkable: every spec `FR-n`/`SC-n` maps to a task and every task back to a requirement.

**Tie two — the architect gate.** Before any task is written, `arche-plan` gap-checks the spec against the architecture: if a behavior lacks a covering SAD/ADR, or would force a load-bearing decision that isn't filed, it **halts and routes to `arche-architect`** rather than quietly inventing design in a task. The "no new ARD/ADR required" verdict (or the gap that was routed) is recorded in the plan itself. This is the structural reason a plan can live *downstream* of architecture without dissolving the `specify → architect → plan` boundary — the gate enforces it.

A plan is further past the code than a spec — it's the **HOW-sequence**, not the WHAT/WHY. It earns its place in the Arche by the same logic, sharpened: the durable **plan-of-record** (decomposition + grounding + traceability) is "how we decided to build this, traced to why" — institutional context — while the transient build state (checkboxes, debug notes, commits) is explicitly *not* captured. The formula, in short: **superpowers' plan rigor, re-anchored to read from the Arche and gated on its architecture, with the durable blueprint kept and the transient state left in the PR.**

### What the Arche does *not* do

- It is not a dumping ground for in-flight TODOs or debugging notes — those stay in your working artifacts (PR descriptions, commit messages). The Arche holds durable, curated *intent and decisions* — and the **plan-of-record** derived from them (`arche-plan`'s decomposition, grounding, and traceability) — but **not** the transient build state: ticked checkboxes, debug notes, and commit history stay in the PR. A `plan` page that accumulates execution state has drifted into TODO-tracker territory.
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
