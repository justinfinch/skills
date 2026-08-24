"""Every skills/*/SKILL.md must carry valid, well-formed frontmatter.

Nothing else in this repo checks this. `okf_conformance.py` and
`test_templates.py` verify the OKF bundles the skills *emit*; they never look
at the skills' own SKILL.md files. That gap is how an unparseable
`description` shipped in `guidance-architecture-lenses/SKILL.md` — a plain
YAML scalar containing `workflow: ` (colon-space), which `yaml.safe_load`
reads as the start of a nested mapping key rather than prose — and how a
`description` that had grown past the spec's 1024-character limit went
unnoticed for months. A SKILL.md is a prompt and cannot be unit tested, but
its frontmatter is a static YAML document, and a static document can be
parsed and checked.

It also covers the SKILL.md *skeleton* every guidance pack is generated from,
`write-guidance/assets/pack-skill.template.md`. That template is invisible to
test_templates.py — its TEMPLATE_TARGETS entry is None, because it is a
SKILL.md and not an OKF page, so render_all skips it — which left the exact
same colon-space defect free to ship into every pack anyone authored. Here it
is rendered directly and parsed, including with deliberately hostile token
values.
"""

import re
import unittest
from pathlib import Path

import yaml

from okf_conformance import split_frontmatter
from render_templates import SAMPLE_TOKENS, render

SKILLS = Path(__file__).resolve().parent.parent / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PACK_SKILL_TEMPLATE = SKILLS / "write-guidance" / "assets" / "pack-skill.template.md"


def skill_files() -> list[Path]:
    return sorted(SKILLS.glob("*/SKILL.md"))


class SkillFrontmatterTests(unittest.TestCase):
    def test_frontmatter_parses(self):
        for path in skill_files():
            rel = path.relative_to(SKILLS.parent)
            with self.subTest(file=str(rel)):
                text = path.read_text(encoding="utf-8")
                fm, _ = split_frontmatter(text)
                self.assertIsNotNone(
                    fm, f"{rel}: no `---`-delimited frontmatter block found"
                )
                try:
                    data = yaml.safe_load(fm)
                except yaml.YAMLError as exc:
                    self.fail(f"{rel}: frontmatter is not valid YAML: {exc}")
                self.assertIsInstance(
                    data, dict, f"{rel}: frontmatter did not parse to a mapping, got {data!r}"
                )

    def test_name_present_and_matches_directory(self):
        for path in skill_files():
            rel = path.relative_to(SKILLS.parent)
            dirname = path.parent.name
            with self.subTest(file=str(rel)):
                fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
                data = yaml.safe_load(fm) or {}
                name = data.get("name")
                self.assertIsNotNone(name, f"{rel}: no `name` field in frontmatter")
                self.assertEqual(
                    name,
                    dirname,
                    f"{rel}: `name: {name!r}` does not match parent directory {dirname!r}",
                )

    def test_name_matches_slug_pattern(self):
        for path in skill_files():
            rel = path.relative_to(SKILLS.parent)
            with self.subTest(file=str(rel)):
                fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
                data = yaml.safe_load(fm) or {}
                name = data.get("name", "")
                self.assertTrue(
                    1 <= len(name) <= 64,
                    f"{rel}: `name: {name!r}` is {len(name)} chars, must be 1-64",
                )
                self.assertRegex(
                    name,
                    NAME_RE,
                    f"{rel}: `name: {name!r}` does not match [a-z0-9]+(-[a-z0-9]+)* "
                    "(lowercase alphanumerics, single hyphens, no leading/trailing/"
                    "consecutive hyphens)",
                )

    def test_description_present_and_within_length(self):
        for path in skill_files():
            rel = path.relative_to(SKILLS.parent)
            with self.subTest(file=str(rel)):
                fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
                data = yaml.safe_load(fm) or {}
                description = data.get("description")
                self.assertIsNotNone(description, f"{rel}: no `description` field in frontmatter")
                n = len(description)
                self.assertTrue(
                    1 <= n <= 1024,
                    f"{rel}: `description` is {n} chars (must be 1-1024): {description!r}",
                )


class PackSkillTemplateTests(unittest.TestCase):
    """The generated pack's frontmatter must parse, hostile prose and all."""

    # Colon-space in both interpolated tokens. Either one, dropped into a plain
    # YAML scalar, yields "mapping values are not allowed here" and a SKILL.md
    # no agent can load. `Outbox: deliver events atomically` is not a contrived
    # string — it is how a pack author writes a title-cased description.
    HOSTILE = {
        "{{DESCRIPTION}}": "Outbox: deliver events atomically with the state change.",
        "{{TRIGGER}}": "a service must publish an event and commit state: both or neither.",
    }

    def _frontmatter(self, tokens: dict[str, str]) -> dict:
        rendered = render(PACK_SKILL_TEMPLATE.read_text(encoding="utf-8"), tokens)
        fm, _ = split_frontmatter(rendered)
        self.assertIsNotNone(fm, "rendered pack SKILL.md has no frontmatter block")
        try:
            data = yaml.safe_load(fm)
        except yaml.YAMLError as exc:
            self.fail(f"rendered pack SKILL.md frontmatter is not valid YAML: {exc}")
        self.assertIsInstance(data, dict, f"frontmatter is not a mapping, got {data!r}")
        return data

    def _assert_well_formed(self, data: dict, slug: str):
        name = data.get("name")
        self.assertEqual(name, f"guidance-{slug}", f"unexpected `name`: {name!r}")
        self.assertRegex(name, NAME_RE, f"`name: {name!r}` is not a valid skill slug")
        description = data.get("description")
        self.assertIsInstance(
            description, str, f"`description` did not parse to a string, got {description!r}"
        )
        self.assertTrue(
            1 <= len(description) <= 1024,
            f"`description` is {len(description)} chars (must be 1-1024)",
        )

    def test_renders_with_sample_tokens(self):
        rendered = render(PACK_SKILL_TEMPLATE.read_text(encoding="utf-8"))
        self.assertNotIn(
            "{{",
            rendered.split("\n---\n", 1)[0],
            "unsubstituted token in frontmatter; every token needs a SAMPLE_TOKENS entry",
        )
        self._assert_well_formed(self._frontmatter(SAMPLE_TOKENS), "sample-slug")

    def test_colon_space_in_author_prose_still_parses(self):
        data = self._frontmatter({**SAMPLE_TOKENS, **self.HOSTILE})
        self._assert_well_formed(data, "sample-slug")
        self.assertIn(
            "Outbox: deliver events atomically",
            data["description"],
            "the author's description was mangled rather than carried through",
        )
        self.assertIn("both or neither", data["description"])


if __name__ == "__main__":
    unittest.main()
