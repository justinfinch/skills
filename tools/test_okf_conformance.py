"""Tests for the OKF v0.2 conformance checker."""

import tempfile
import unittest
from pathlib import Path

from okf_conformance import Finding, check_bundle, split_frontmatter


def write_bundle(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def rules(findings: list[Finding]) -> list[str]:
    return sorted(f.rule for f in findings)


class SplitFrontmatterTests(unittest.TestCase):
    def test_extracts_frontmatter_and_body(self):
        fm, body = split_frontmatter("---\na: 1\n---\nbody\n")
        self.assertEqual(fm, "a: 1\n")
        self.assertEqual(body, "body\n")

    def test_empty_frontmatter_is_a_block(self):
        fm, body = split_frontmatter("---\n---\nbody\n")
        self.assertEqual(fm, "")
        self.assertEqual(body, "body\n")

    def test_absent_frontmatter_returns_none(self):
        fm, body = split_frontmatter("# Just a heading\n")
        self.assertIsNone(fm)
        self.assertEqual(body, "# Just a heading\n")

    def test_unterminated_frontmatter_returns_none(self):
        fm, _ = split_frontmatter("---\na: 1\nno closing delimiter\n")
        self.assertIsNone(fm)


class Rule1Tests(unittest.TestCase):
    def test_concept_without_frontmatter_is_a_finding(self):
        root = write_bundle({"concepts/foo.md": "# Foo\n"})
        self.assertEqual(rules(check_bundle(root)), ["§11.1"])

    def test_unparseable_frontmatter_is_a_finding(self):
        root = write_bundle({"concepts/foo.md": "---\na: [unclosed\n---\nbody\n"})
        self.assertEqual(rules(check_bundle(root)), ["§11.1"])

    def test_raw_markdown_without_frontmatter_is_a_finding(self):
        root = write_bundle({"raw/pasted.md": "some pasted text\n"})
        self.assertEqual(rules(check_bundle(root)), ["§11.1"])

    def test_raw_non_markdown_is_ignored(self):
        root = write_bundle({"raw/pasted.txt": "some pasted text\n"})
        self.assertEqual(check_bundle(root), [])


class Rule2Tests(unittest.TestCase):
    def test_missing_type_is_a_finding(self):
        root = write_bundle({"concepts/foo.md": "---\ntitle: Foo\n---\nbody\n"})
        self.assertEqual(rules(check_bundle(root)), ["§11.2"])

    def test_empty_type_is_a_finding(self):
        root = write_bundle({"concepts/foo.md": "---\ntype: '  '\n---\nbody\n"})
        self.assertEqual(rules(check_bundle(root)), ["§11.2"])

    def test_non_empty_type_alone_conforms(self):
        root = write_bundle({"concepts/foo.md": "---\ntype: Concept\n---\nbody\n"})
        self.assertEqual(check_bundle(root), [])


class IndexTests(unittest.TestCase):
    def test_root_index_may_carry_okf_version(self):
        root = write_bundle({"index.md": '---\nokf_version: "0.2"\n---\n\n# Sections\n'})
        self.assertEqual(check_bundle(root), [])

    def test_root_index_rejects_other_keys(self):
        root = write_bundle({"index.md": '---\nokf_version: "0.2"\ntype: Index\n---\n'})
        self.assertEqual(rules(check_bundle(root)), ["§8"])

    def test_nested_index_rejects_any_frontmatter(self):
        root = write_bundle({"concepts/index.md": "---\ntype: Index\n---\n"})
        self.assertEqual(rules(check_bundle(root)), ["§8"])

    def test_bare_index_conforms(self):
        root = write_bundle({"index.md": "# Sections\n", "concepts/index.md": "# Concept\n"})
        self.assertEqual(check_bundle(root), [])


class LogTests(unittest.TestCase):
    def test_log_may_carry_frontmatter(self):
        root = write_bundle({"log.md": "---\ntype: Log\n---\n\n## 2026-08-11\n\n- **Init**: x\n"})
        self.assertEqual(check_bundle(root), [])

    def test_non_iso_date_heading_is_a_finding(self):
        root = write_bundle({"log.md": "---\ntype: Log\n---\n\n## [2026-08-11] init | x\n"})
        self.assertEqual(rules(check_bundle(root)), ["§9"])

    def test_oldest_first_ordering_is_a_finding(self):
        root = write_bundle(
            {"log.md": "---\ntype: Log\n---\n\n## 2026-01-01\n\n- a\n\n## 2026-08-11\n\n- b\n"}
        )
        self.assertEqual(rules(check_bundle(root)), ["§9"])

    def test_newest_first_ordering_conforms(self):
        root = write_bundle(
            {"log.md": "---\ntype: Log\n---\n\n## 2026-08-11\n\n- b\n\n## 2026-01-01\n\n- a\n"}
        )
        self.assertEqual(check_bundle(root), [])


if __name__ == "__main__":
    unittest.main()
