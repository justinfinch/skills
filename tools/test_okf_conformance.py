"""Tests for the OKF v0.2 conformance checker."""

import tempfile
import unittest
from pathlib import Path  # noqa: F401  (used by PreOkfFixtureTests)

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

    def test_closing_delimiter_at_eof_without_trailing_newline(self):
        # Editors that omit the final newline produce this on any page with no
        # body. It is a terminated block, not a missing one.
        fm, body = split_frontmatter("---\ntype: Concept\n---")
        self.assertEqual(fm, "type: Concept\n")
        self.assertEqual(body, "")

    def test_empty_frontmatter_at_eof_without_trailing_newline(self):
        fm, body = split_frontmatter("---\n---")
        self.assertEqual(fm, "")
        self.assertEqual(body, "")

    def test_bare_delimiter_is_not_frontmatter(self):
        # "---\n" alone has an opening delimiter and nothing else.
        fm, _ = split_frontmatter("---\n")
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

    def test_bodyless_page_without_trailing_newline_conforms(self):
        root = write_bundle({"entities/acme.md": "---\ntype: Entity\n---"})
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

    def test_root_index_frontmatter_that_is_not_a_mapping_is_a_finding(self):
        # A YAML list, a bare scalar, and an empty block all parse to a non-mapping.
        # Without an isinstance guard these pass silently, because the key set falls
        # back to empty and the "only okf_version" subtraction then finds nothing.
        for frontmatter in ('- okf_version: "0.2"\n', "just a string\n", ""):
            with self.subTest(frontmatter=frontmatter):
                root = write_bundle({"index.md": f"---\n{frontmatter}---\n\n# Sections\n"})
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


class PreOkfFixtureTests(unittest.TestCase):
    """`tools/fixtures/pre_okf/` is the one realistic bundle in the repo.

    It is a hand-built pre-v0.2 Arche exercising every drift class, and its
    primary job is manual: it is the scratch bed for running `/arche-lint`
    against, since a skill is a prompt and cannot be unit tested. That leaves
    its checker-visible behavior unpinned, so this test pins it — otherwise the
    checker could regress against the only non-synthetic bundle we have and
    nothing would notice.
    """

    FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pre_okf"

    def test_fixture_is_deliberately_non_conformant(self):
        found = {(str(f.path), f.rule) for f in check_bundle(self.FIXTURE)}
        self.assertEqual(
            found,
            {
                ("index.md", "§8"),  # carries created/type/updated
                ("log.md", "§9"),  # two `## [date] op | text` headings
                ("raw/pasted-notes.md", "§11.1"),  # .md snapshot, no frontmatter
            },
        )

    def test_log_ordering_is_not_reported_when_headings_are_unparseable(self):
        # The fixture's headings are oldest-first, but they are also non-ISO, so
        # no date parses and there is no ordering claim to make. Reporting an
        # ordering finding here would be inventing one from headings we could
        # not read.
        messages = [f.message for f in check_bundle(self.FIXTURE) if f.rule == "§9"]
        self.assertEqual(len(messages), 2)
        self.assertTrue(all(m.startswith("date heading not ISO") for m in messages))

    def test_fixture_has_no_findings_outside_okf_hard_conformance(self):
        # §11 forbids consumers from rejecting a bundle over unknown `type`
        # values, missing index.md, or broken links. The fixture has all three
        # (lowercase types, no subdirectory indexes, string `sources`), and the
        # checker must stay silent on every one of them.
        self.assertEqual(
            {f.rule for f in check_bundle(self.FIXTURE)}, {"§8", "§9", "§11.1"}
        )


if __name__ == "__main__":
    unittest.main()
