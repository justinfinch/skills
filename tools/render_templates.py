#!/usr/bin/env python3
"""Render every skill-owned template into a throwaway bundle.

Skills are prompts and cannot be unit tested. Their templates are static
files, so rendering them with sample tokens and running the conformance
checker gives a real red/green cycle for a markdown-only migration.
"""

from __future__ import annotations

from pathlib import Path

SAMPLE_TOKENS = {
    "{{DATE}}": "2026-08-11",
    "{{TIMESTAMP}}": "2026-08-11T10:00:00Z",
    "{{STALE_AFTER}}": "2028-01-01",
    "{{ACTOR}}": "arche-ingest/claude-opus-5",
    "{{TITLE}}": "Sample Title",
    "{{DESCRIPTION}}": "One-sentence summary of the sample page.",
    "{{SLUG}}": "sample-slug",
    "{{EXT}}": "pdf",
    "{{URL}}": "https://example.com/sample",
    "{{RESOURCE}}": "https://example.com/sample",
    "{{SYSTEM}}": "billing",
    "{{AUDIENCE}}": "Engineering leadership",
    "{{AUDIENCE_DEPTH}}": "Senior engineers; assumes DDD and event-driven literacy",
    "{{ACTION_ASK}}": "Approve the migration",
    "{{TIME_BUDGET}}": "20 minutes",
}

# Where each template's rendered output must live inside the bundle. The
# destination matters: index.md and log.md are reserved filenames (SPEC 3.1),
# so they are checked by different rules than concept documents.
TEMPLATE_TARGETS = {
    "SCHEMA.template.md": "SCHEMA.md",
    "index.template.md": "index.md",
    "subindex.template.md": "concepts/index.md",
    "log.template.md": "log.md",
    "source.template.md": "sources/sample-slug.md",
    "concept.template.md": "concepts/sample-concept.md",
    "entity.template.md": "entities/sample-entity.md",
    "query.template.md": "queries/sample-query.md",
    "discovery.template.md": "discoveries/sample-discovery.md",
    "story.template.md": "stories/sample-story.md",
    "ard.template.md": "concepts/ard-billing.md",
    "sad.template.md": "concepts/sad-billing.md",
    "adr.template.md": "concepts/adr-event-driven-billing.md",
    # A pack's Guidance pages live in its bundle's concepts/ directory, so the
    # synthesized Arche bundle is a fine place to prove they conform.
    "guidance.template.md": "concepts/sample-guidance.md",
    # None means "skill-owned template, but not an OKF page". pack-skill is a
    # SKILL.md skeleton: it carries `name`/`description`, not `type`, so
    # rendering it into a bundle would fail SPEC 11 rule 2 by design.
    "pack-skill.template.md": None,
}


def render(text: str) -> str:
    for token, value in SAMPLE_TOKENS.items():
        text = text.replace(token, value)
    return text


def find_templates(skills_dir: Path) -> list[Path]:
    """Every skill-owned template, whichever family owns it.

    `write-*` skills own templates too (write-guidance emits Guidance pages),
    so discovery can't stay scoped to `arche-*`.
    """
    return sorted(
        [*skills_dir.glob("arche-*/assets/*.template.md"),
         *skills_dir.glob("write-*/assets/*.template.md")]
    )


def render_all(skills_dir: Path, dest: Path) -> list[Path]:
    """Render every skill template into `dest`. Returns the paths written."""
    written = []
    for template in find_templates(skills_dir):
        if template.name not in TEMPLATE_TARGETS:
            raise KeyError(
                f"{template.name} has no entry in TEMPLATE_TARGETS; "
                "add one so the harness knows where it belongs in a bundle"
            )
        target = TEMPLATE_TARGETS[template.name]
        if target is None:
            continue
        out = dest / target
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(template.read_text(encoding="utf-8")), encoding="utf-8")
        written.append(out)
    return written
