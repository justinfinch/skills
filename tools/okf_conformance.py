#!/usr/bin/env python3
"""Check a directory against Open Knowledge Format v0.2 conformance (SPEC §11).

Spec vendored at spec/okf/v0.2/SPEC.md (upstream GoogleCloudPlatform/
knowledge-catalog commit 3fcbb9f); see that directory's PROVENANCE.md.

This is deliberately independent of `arche-lint`: checking lint's output with
lint would be circular. It implements only the three hard rules in §11, plus
the reserved-file structure those rules point at (§8, §9).

OKF ships no validator and the spec recommends none -- §11 is prose, and
upstream's own reference_agent only parses bundles, checking that a `type` key
is present without checking it is non-empty. So this file is the oracle, and
its scope is deliberately narrow.

What it must NEVER flag, because §11 names these as things consumers MUST NOT
reject a bundle over: missing optional frontmatter fields, unknown `type`
values, unknown extra frontmatter keys, broken cross-links, missing index.md.
`arche-lint` reports several of those as house-convention drift, which is fine
-- it audits and asks. A non-zero exit here means non-conformant, so anything
on that list would make this checker itself out of spec.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    # Exit 2, not 1: 1 means "the bundle has findings". A missing dependency is
    # an environment problem, and conflating the two lets a broken CI runner
    # read as a non-conformant bundle.
    print(
        "PyYAML required: run inside `devbox shell`, or "
        "`python3 -m pip install --user pyyaml`",
        file=sys.stderr,
    )
    raise SystemExit(2)

DATE_HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")


@dataclass(frozen=True)
class Finding:
    path: Path
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: [{self.rule}] {self.message}"


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter_yaml, body); frontmatter is None when absent."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        # A closing `---` as the final line with no trailing newline still
        # terminates the block. Frontmatter-only pages (entity stubs, pages
        # whose body was trimmed) hit this whenever the editor omits the
        # final newline; treating them as unterminated would report a page
        # that has frontmatter as having none.
        if text.endswith("\n---"):
            return text[4 : len(text) - 3], ""
        return None, text
    return text[4 : end + 1], text[end + 5 :]


def _load(fm: str) -> tuple[object | None, str | None]:
    """Parse frontmatter YAML; return (data, error_message)."""
    try:
        return yaml.safe_load(fm), None
    except yaml.YAMLError as exc:
        return None, str(exc).replace("\n", " ")


def check_concept(rel: Path, text: str) -> list[Finding]:
    fm, _ = split_frontmatter(text)
    if fm is None:
        return [Finding(rel, "§11.1", "no YAML frontmatter block")]
    data, err = _load(fm)
    if err is not None:
        return [Finding(rel, "§11.1", f"unparseable frontmatter: {err}")]
    if not isinstance(data, dict):
        return [Finding(rel, "§11.1", "frontmatter is not a mapping")]
    value = data.get("type")
    if not isinstance(value, str) or not value.strip():
        return [Finding(rel, "§11.2", "missing or empty `type`")]
    return []


def check_index(rel: Path, text: str, is_root: bool) -> list[Finding]:
    fm, _ = split_frontmatter(text)
    if fm is None:
        return []
    if not is_root:
        return [Finding(rel, "§8", "only a bundle-root index.md may carry frontmatter")]
    data, err = _load(fm)
    if err is not None:
        return [Finding(rel, "§8", f"unparseable frontmatter: {err}")]
    if not isinstance(data, dict):
        return [Finding(rel, "§8", "frontmatter is not a mapping")]
    extra = set(data) - {"okf_version"}
    if extra:
        return [
            Finding(rel, "§8", f"root index.md may only carry okf_version; found {sorted(extra)}")
        ]
    return []


def check_log(rel: Path, text: str) -> list[Finding]:
    _, body = split_frontmatter(text)
    findings: list[Finding] = []
    dates: list[str] = []
    for line in body.splitlines():
        if not line.startswith("## "):
            continue
        match = DATE_HEADING.match(line)
        if match is None:
            findings.append(Finding(rel, "§9", f"date heading not ISO YYYY-MM-DD: {line!r}"))
        else:
            dates.append(match.group(1))
    if dates != sorted(dates, reverse=True):
        findings.append(Finding(rel, "§9", "date headings must be ordered newest first"))
    return findings


def check_bundle(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        if path.name == "index.md":
            findings += check_index(rel, text, is_root=rel.parent == Path("."))
        elif path.name == "log.md":
            findings += check_log(rel, text)
        else:
            findings += check_concept(rel, text)
    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: okf_conformance.py <bundle-dir>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    findings = check_bundle(root)
    total = len(list(root.rglob("*.md")))
    for finding in findings:
        print(finding)
    if findings:
        print(f"\n{len(findings)} finding(s) across {total} markdown file(s)")
        return 1
    print(f"OK: {total} markdown file(s) conform to OKF v0.2 §11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
