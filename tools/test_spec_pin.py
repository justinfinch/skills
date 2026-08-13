"""The vendored OKF spec must stay byte-identical to what PROVENANCE.md records.

A vendored copy is only a pin if something enforces it. Without this, an
accidental edit — a stray reformat, an agent "helpfully" fixing a typo —
silently turns the spec into a stale photocopy, and every `§` citation in the
repo starts pointing at text upstream never published.
"""

import hashlib
import re
import unittest
from pathlib import Path

SPEC_DIR = Path(__file__).resolve().parent.parent / "spec" / "okf" / "v0.2"
PROVENANCE = SPEC_DIR / "PROVENANCE.md"

# Rows look like: | `SPEC.md` | 37544 | `<64 hex>` |
ROW = re.compile(
    r"^\|\s*`(?P<name>[^`]+)`\s*\|\s*(?P<size>\d+)\s*\|\s*`(?P<sha>[0-9a-f]{64})`\s*\|",
    re.MULTILINE,
)


def recorded_files() -> dict[str, tuple[int, str]]:
    """Parse the Files table out of PROVENANCE.md — it is the source of truth."""
    text = PROVENANCE.read_text(encoding="utf-8")
    return {m["name"]: (int(m["size"]), m["sha"]) for m in ROW.finditer(text)}


class SpecPinTests(unittest.TestCase):
    def test_provenance_records_both_files(self):
        self.assertEqual(sorted(recorded_files()), ["LICENSE", "SPEC.md"])

    def test_vendored_files_match_recorded_digests(self):
        for name, (size, sha) in recorded_files().items():
            with self.subTest(file=name):
                blob = (SPEC_DIR / name).read_bytes()
                self.assertEqual(len(blob), size, f"{name} size drifted from PROVENANCE.md")
                self.assertEqual(
                    hashlib.sha256(blob).hexdigest(),
                    sha,
                    f"{name} content drifted from PROVENANCE.md — the vendored spec is "
                    "no longer the pinned upstream text. Re-fetch it, or update "
                    "PROVENANCE.md if the pin moved deliberately.",
                )

    def test_spec_declares_the_version_this_repo_implements(self):
        head = (SPEC_DIR / "SPEC.md").read_text(encoding="utf-8")[:400]
        self.assertIn("**Version 0.2**", head)

    def test_conformance_section_is_still_section_11(self):
        # Every §11.x citation in the skills and in okf_conformance.py assumes
        # this. Section numbers renumber across spec revisions, so if a future
        # re-pin moves Conformance, the citations must move with it.
        text = (SPEC_DIR / "SPEC.md").read_text(encoding="utf-8")
        self.assertIn("## 11. Conformance", text)
        self.assertIn("## 8. Index files", text)
        self.assertIn("## 9. Log files", text)


if __name__ == "__main__":
    unittest.main()
