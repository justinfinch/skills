"""Every skill-owned template must render to a conformant OKF v0.2 page."""

import tempfile
import unittest
from pathlib import Path

from okf_conformance import check_bundle
from render_templates import TEMPLATE_TARGETS, find_templates, render, render_all

SKILLS = Path(__file__).resolve().parent.parent / "skills"


class TemplateTargetTests(unittest.TestCase):
    def test_every_template_has_a_target(self):
        missing = [t.name for t in find_templates(SKILLS) if t.name not in TEMPLATE_TARGETS]
        self.assertEqual(missing, [], f"templates with no TEMPLATE_TARGETS entry: {missing}")

    def test_template_basenames_are_unique(self):
        """TEMPLATE_TARGETS is keyed on basename while discovery is repo-wide.

        Two skills owning a same-named template would map to one entry, so the
        second rendered over the first and one of them was never checked. No
        error is raised on that path, which is what makes it worth a test.
        """
        names = [t.name for t in find_templates(SKILLS)]
        dupes = sorted({n for n in names if names.count(n) > 1})
        self.assertEqual(
            dupes,
            [],
            f"template basenames owned by more than one skill: {dupes}; "
            "key TEMPLATE_TARGETS on the skill-relative path instead",
        )

    def test_template_targets_are_distinct(self):
        """Two entries rendering to the same destination silently lose one."""
        targets = [t for t in TEMPLATE_TARGETS.values() if t is not None]
        dupes = sorted({t for t in targets if targets.count(t) > 1})
        self.assertEqual(dupes, [], f"TEMPLATE_TARGETS destinations claimed twice: {dupes}")


class RenderedTemplateTests(unittest.TestCase):
    def test_rendered_templates_conform(self):
        dest = Path(tempfile.mkdtemp())
        render_all(SKILLS, dest)
        findings = check_bundle(dest)
        self.assertEqual(
            findings, [], "\n".join(str(f) for f in findings)
        )

    def test_no_unsubstituted_tokens_remain(self):
        dest = Path(tempfile.mkdtemp())
        for path in render_all(SKILLS, dest):
            self.assertNotIn("{{", path.read_text(encoding="utf-8"), f"{path} has stray tokens")

    def test_no_bundle_absolute_links(self):
        """Relative links only — the Arche is a repo subdirectory (design decision 2)."""
        dest = Path(tempfile.mkdtemp())
        for path in render_all(SKILLS, dest):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("](/", text, f"{path} uses a bundle-absolute link")

    def test_no_retired_status_vocabulary(self):
        dest = Path(tempfile.mkdtemp())
        for path in render_all(SKILLS, dest):
            for retired in ("status: proposed", "status: accepted", "status: superseded"):
                self.assertNotIn(retired, path.read_text(encoding="utf-8"), f"{path}: {retired}")


if __name__ == "__main__":
    unittest.main()
