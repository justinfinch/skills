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
- **[wiki-init](skills/wiki-init/SKILL.md)** — bootstrap an LLM Wiki at `./.wiki/` (Karpathy's pattern): schema, index, log. The wiki captures institutional context — business/domain/SME/ARB — not code documentation.
- **[wiki-ingest](skills/wiki-ingest/SKILL.md)** — ingest a source (URL/file/text/SME-interview/ADR) into the wiki and update affected pages.
- **[wiki-query](skills/wiki-query/SKILL.md)** — answer a question from the wiki with inline citations; also fires as a cold-start orientation step before planning/design in agentic dev workflows.
- **[wiki-discover](skills/wiki-discover/SKILL.md)** — facilitated discovery / ideation session grounded in wiki context, for business/domain/architectural topics (not implementation design). Files the session and promotes top ideas back to concept/entity pages (including new ADRs).
- **[wiki-lint](skills/wiki-lint/SKILL.md)** — audit the wiki for contradictions, stale dates, orphans, broken links, gaps, discovery-promotion drift.

## Wiki + agentic dev methodologies

The `wiki-*` skills implement [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern, pointed at **institutional context**: business domain, SME knowledge, ARB-style architectural decisions, and research. The wiki sits **adjacent to the code**, never derived from it.

It is designed to plug into any agentic dev methodology — [obra/superpowers](https://github.com/obra/superpowers), [mattpocock/skills](https://github.com/mattpocock/skills), your own — as the **context layer**, not the procedure layer:

```
Procedural layer    (superpowers / matt's skills / etc.)
  brainstorm → plan → TDD → review → finish
              ▲
              │ queries
              │
Context layer       (this wiki)
  entities • concepts (incl. ADRs) • sources • discoveries • queries
              ▲
              │ ingests / discoveries
              │
Raw layer           (.wiki/raw/)
  research papers • SME interview transcripts • ADRs as decisions land
```

### How the integration works

- **During planning / design / brainstorming**, the dev methodology's planning skill (e.g. superpowers' `brainstorming` or `writing-plans`) runs. `wiki-query`'s description triggers it as a sibling orientation step — surfacing relevant ADRs, domain constraints, customer context, prior discoveries — so the plan is informed by what the institution already knows.
- **For non-code-implementation ideation** (product strategy, new architecture direction, regulatory option-mapping), use `wiki-discover` directly. It facilitates the session with wiki context loaded, then files the session + promotes top ideas (including new ADRs) back to the wiki.
- **For code-implementation brainstorming** (how to refactor a module, how to structure tests), use the dev methodology's own brainstorming skill — `wiki-discover` is intentionally scoped *away* from that to avoid collision.
- **For new institutional sources** (a competitor analysis, an SME interview transcript, an external ADR you want recorded), use `wiki-ingest`. The wiki grows by deliberate curation, not by accretion from coding sessions.

### What the wiki does *not* do

- It does not capture per-task plans, in-flight TODOs, or debugging notes — those live in your dev methodology's working artifacts (PR descriptions, commit messages, superpowers worktrees, etc.).
- It is not a substitute for episodic conversation memory like [obra/episodic-memory](https://github.com/obra/episodic-memory) — that's a separate, complementary layer (raw recall vs. curated synthesis). Both can coexist.
- It is not code documentation. If a question is answered by *reading the code*, the wiki is the wrong place.

### Location

By convention the wiki lives at `./.wiki/` in the repo (dotted, like `.claude/` and `.vscode/`) so it doesn't collide with content folders named `wiki/`. For monorepos, one wiki at the repo root covers cross-cutting concerns across services.

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
