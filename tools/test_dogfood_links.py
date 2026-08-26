"""`.claude/skills/` must stay a flat, current mirror of every skill.

This is the harness for the failure that motivated it: a `guidance-*` pack that
loads fine from a real install but is invisible when dogfooding, because the
loader does not descend into `skills/guidance/`. A missing link produces no
error at load time — the skill is simply never offered — so the only place that
can notice is a test.
"""

import unittest

from dogfood_links import DOGFOOD, actual_links, expected_links, skill_dirs


class DogfoodLinkTests(unittest.TestCase):
    def test_mirror_is_current(self):
        expected, actual = expected_links(), actual_links()
        self.assertEqual(
            expected,
            actual,
            "run `python tools/dogfood_links.py` to repair .claude/skills/",
        )

    def test_every_skill_is_linked(self):
        linked = set(actual_links())
        missing = sorted(d.name for d in skill_dirs() if d.name not in linked)
        self.assertEqual(missing, [], f"skills absent from the dogfood mirror: {missing}")

    def test_links_resolve_to_a_skill_file(self):
        broken = sorted(
            name for name in actual_links()
            if not (DOGFOOD / name / "SKILL.md").is_file()
        )
        self.assertEqual(broken, [], f"dogfood links not resolving to a SKILL.md: {broken}")

    def test_mirror_is_flat(self):
        """A link name is what the loader sees, so it must equal the skill's own
        directory name — never a path segment like `guidance/guidance-ddd`."""
        nested = sorted(name for name in actual_links() if "/" in name)
        self.assertEqual(nested, [], f"nested entries in the dogfood mirror: {nested}")


if __name__ == "__main__":
    unittest.main()
