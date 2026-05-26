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
