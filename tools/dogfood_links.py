#!/usr/bin/env python3
"""Keep `.claude/skills/` a flat mirror of every skill in this repo.

Claude Code loads `.claude/skills/<name>/SKILL.md` and does *not* descend into
category directories. The vercel-labs/skills installer does recurse (depth 5)
and then writes each skill to `<agent-skills-dir>/<name>/` — flat, keyed on the
skill's `name` rather than its path in the source repo. So an installed copy of
this library is flat even though the repo groups packs under `skills/guidance/`.

Dogfooding by symlinking `.claude/skills -> ../skills` skipped that flattening
and exposed the repo layout directly to the loader, which silently dropped every
`guidance-*` pack. This module instead mirrors what the installer produces: one
symlink per skill, flat, named for its directory.

Run as a script to repair the mirror; `test_dogfood_links.py` asserts it is
current, so a new skill that never got linked fails the suite instead of going
quietly missing at load time.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
DOGFOOD = REPO / ".claude" / "skills"


def skill_dirs(skills_dir: Path = SKILLS) -> list[Path]:
    """Every directory holding a SKILL.md, at any nesting depth."""
    return sorted(p.parent for p in skills_dir.rglob("SKILL.md"))


def expected_links(skills_dir: Path = SKILLS, dogfood: Path = DOGFOOD) -> dict[str, str]:
    """Map link name -> the relative target it should point at."""
    return {
        d.name: os.path.relpath(d, dogfood)
        for d in skill_dirs(skills_dir)
    }


def actual_links(dogfood: Path = DOGFOOD) -> dict[str, str]:
    """Map link name -> its recorded target, for symlinks only.

    Non-symlink entries are reported as their name mapping to None so a real
    directory sitting where a link belongs surfaces as a mismatch rather than
    being silently accepted.
    """
    if not dogfood.is_dir():
        return {}
    return {
        p.name: (os.readlink(p) if p.is_symlink() else None)
        for p in sorted(dogfood.iterdir())
        if not p.name.startswith(".")
    }


def sync(skills_dir: Path = SKILLS, dogfood: Path = DOGFOOD) -> tuple[list[str], list[str]]:
    """Make the mirror match. Returns (created, removed) link names."""
    dogfood.mkdir(parents=True, exist_ok=True)
    expected = expected_links(skills_dir, dogfood)
    created, removed = [], []

    for name, target in actual_links(dogfood).items():
        if expected.get(name) != target:
            path = dogfood / name
            if path.is_symlink() or path.is_file():
                path.unlink()
                removed.append(name)

    for name, target in expected.items():
        path = dogfood / name
        if not path.is_symlink():
            path.symlink_to(target)
            created.append(name)

    return created, removed


if __name__ == "__main__":
    created, removed = sync()
    for name in removed:
        print(f"- {name}")
    for name in created:
        print(f"+ {name}")
    print(f"{len(expected_links())} skills linked into .claude/skills/")
