#!/usr/bin/env python3
"""Check a directory against Open Knowledge Format v0.2 conformance (SPEC §11).

A development tool for this repository. It does not ship -- `npx skills add`
installs from skills/, and this lives at the repo root -- and it never runs
against this repo's own files. It checks *bundles*, and this repo has no
.arche/ of its own; it holds the skills that build one.

Its automated job is narrow and specific. Six skills ship 13 static page
templates between them (SCHEMA/index/subindex/log, source/entity/concept,
ard/sad/adr, query, discovery, story). Those templates are what a user's Arche
gets built from, and the OKF v0.2 migration was a rewrite of their frontmatter.
A skill is a prompt and cannot be unit tested, but a template is a static file:
test_templates.py renders all 13 into a throwaway directory laid out as a real
bundle and runs this checker over it. That is how we know the pages these
skills emit are conformant, and it is the whole reason this file exists.

The CLI takes a bundle path because the other way you use it is by hand, while
developing -- run /arche-init into a scratch directory and check what it
actually produced, or point it at tools/fixtures/pre_okf.

Scope is deliberately just the three hard rules in §11 plus the reserved-file
structure they point at (§8, §9). Spec vendored at spec/okf/v0.2/SPEC.md
(upstream GoogleCloudPlatform/knowledge-catalog commit 3fcbb9f); see that
directory's PROVENANCE.md. OKF ships no validator and the spec recommends
none -- upstream's own reference_agent merely parses bundles, checking that a
`type` key is present without checking it is non-empty -- so this file is the
oracle.

It is deliberately not built on `arche-lint`: lint is the skill that claims to
enforce conformance, so testing that claim with the claimant would be circular.
But note the limit of that -- this checker verifies the six *writer* skills'
output, and nothing automated verifies arche-lint itself. Lint's remit is
mostly house conventions this checker ignores on purpose; its verification is
the manual fixture procedure in README.md.

What this must NEVER flag, because §11 names them as things consumers MUST NOT
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
