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
- **[arche-init](skills/arche-init/SKILL.md)** — bootstrap an Arche at `./.arche/` (Karpathy's LLM-wiki pattern): schema, index, log. Arche captures institutional context — business/domain/SME/ARB — not code documentation.
- **[arche-ingest](skills/arche-ingest/SKILL.md)** — ingest a source (URL/file/text/SME-interview/ADR) into the Arche and update affected pages.
- **[arche-query](skills/arche-query/SKILL.md)** — answer a question from the Arche with inline citations; also fires as a cold-start orientation step before planning/design in agentic dev workflows.
- **[arche-discover](skills/arche-discover/SKILL.md)** — facilitated discovery / ideation session grounded in Arche context, for business/domain/architectural topics (not implementation design). Files the session and promotes top ideas back to concept/entity pages (including new ADRs).
- **[arche-architect](skills/arche-architect/SKILL.md)** — convergent technical-architecture skill: panel of senior-architect lenses, files ARD/SAD/ADR concept pages.
- **[arche-tell](skills/arche-tell/SKILL.md)** — interview the user on audience + action ask + narrative framework, then produce a shareable HTML artifact (reveal.js deck or scrollable narrative) for communicating Arche content. Files `stories/<slug>.md` + `assets/stories/<slug>.html`.
- **[arche-lint](skills/arche-lint/SKILL.md)** — audit the Arche for contradictions, stale dates, orphans, broken links, gaps, discovery-promotion drift.

## Why "Arche"?

**ἀρχή** (*arche*, "AR-kay") — Greek for *the beginning, the first principle, the foundational source from which what follows derives*. The pre-Socratics used it for the underlying thing from which everything else proceeds; Aristotle for the starting point of a chain of reasoning.

The `arche-*` skills cover the **before-development workflow most coding agents skip** — gathering institutional context (business, SME knowledge, ARB decisions, research) *before* anyone writes code. Etymologically, *arche* is also the root of "architect" (ἀρχή + τέκτων, "master builder of first principles") — so `arche-architect` is recursively apt.

## Arche + agentic dev methodologies

The `arche-*` skills implement [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern, pointed at **institutional context**: business domain, SME knowledge, ARB-style architectural decisions, and research. The Arche sits **adjacent to the code**, never derived from it.

It is designed to plug into any agentic dev methodology — [obra/superpowers](https://github.com/obra/superpowers), [mattpocock/skills](https://github.com/mattpocock/skills), your own — as the **context layer**, not the procedure layer:

```
Procedural layer    (superpowers / matt's skills / etc.)
  brainstorm → plan → TDD → review → finish
              ▲
              │ queries
              │
Context layer       (the Arche)
  entities • concepts (incl. ADRs) • sources • discoveries • queries
              ▲
              │ ingests / discoveries
              │
Raw layer           (.arche/raw/)
  research papers • SME interview transcripts • ADRs as decisions land
```

### How the integration works

- **During planning / design / brainstorming**, the dev methodology's planning skill (e.g. superpowers' `brainstorming` or `writing-plans`) runs. `arche-query`'s description triggers it as a sibling orientation step — surfacing relevant ADRs, domain constraints, customer context, prior discoveries — so the plan is informed by what the institution already knows.
- **For non-code-implementation ideation** (product strategy, new architecture direction, regulatory option-mapping), use `arche-discover` directly. It facilitates the session with Arche context loaded, then files the session + promotes top ideas back to the Arche.
- **For technical architecture decisions** (designing a system, choosing patterns, ADR-worthy choices), use `arche-architect` — it runs a panel-of-architects interview and files ARD/SAD/ADR concept pages.
- **For code-implementation brainstorming** (how to refactor a module, how to structure tests), use the dev methodology's own brainstorming skill — `arche-discover` is intentionally scoped *away* from that to avoid collision.
- **For new institutional sources** (a competitor analysis, an SME interview transcript, an external ADR you want recorded), use `arche-ingest`. The Arche grows by deliberate curation, not by accretion from coding sessions.

### What the Arche does *not* do

- It does not capture per-task plans, in-flight TODOs, or debugging notes — those live in your dev methodology's working artifacts (PR descriptions, commit messages, superpowers worktrees, etc.).
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
