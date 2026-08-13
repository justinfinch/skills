# tools

Verification for the Arche's OKF v0.2 conformance. Not shipped in any skill —
`arche-lint` implements its own checks; these exist so lint can be verified
against something independent.

The spec is vendored at [`spec/okf/v0.2/`](../spec/okf/v0.2/) — see its
`PROVENANCE.md`. OKF publishes no validator and the spec recommends none, so
`okf_conformance.py` is the oracle here. Its scope is deliberately just §11's
three hard rules plus the §8 / §9 reserved-file structure they point at; §11
forbids consumers from rejecting a bundle over unknown `type` values, missing
`index.md`, broken links, or missing optional fields, so this checker must
never exit non-zero on any of those. `test_spec_pin.py` asserts the vendored
spec still matches the digests `PROVENANCE.md` records.

## Requirements

Python 3.12+ and PyYAML, both declared in the repo's `devbox.json`. Run
`devbox shell` (or let direnv load it on `cd`) and they are on `PATH`. Without
devbox, install PyYAML with `python3 -m pip install --user pyyaml`.

## Check a bundle

    devbox run check path/to/.arche          # or, inside a devbox shell:
    python3 tools/okf_conformance.py path/to/.arche

The path is required — there is no default, because this repo has no `.arche/`
to fall back on. To try it: `devbox run check tools/fixtures/pre_okf`.

Exit code 0 when conformant, 1 when findings exist, 2 on usage or environment
error (bad arguments, missing PyYAML). A broken environment must never look
like a non-conformant bundle, so 1 is reserved for findings alone.

## What these run against

**This repo has no `.arche/` of its own, and shouldn't** — it holds the skills
that build one, not an Arche. So nothing here checks a real bundle in place.
The bridge is synthesis, and it works because skills are prompts (untestable)
while their *templates* are static files (very testable):

| Suite | Runs against |
| :--- | :--- |
| `test_templates.py` | A bundle **synthesized on the fly**. `render_templates.py` substitutes sample tokens into all 13 `skills/arche-*/assets/*.template.md` files and writes each to the path it would occupy in a real Arche (`TEMPLATE_TARGETS` maps `story.template.md` → `stories/sample-story.md`, and so on), producing reserved files plus one page per type. That temp bundle then goes through `check_bundle`. This is the load-bearing suite: it tests the exact text the skills will emit. |
| `test_okf_conformance.py` | Small hand-built bundles written to temp dirs by the `write_bundle` helper — unit coverage for the checker itself — plus `fixtures/pre_okf/` (below). |
| `test_spec_pin.py` | No bundle at all. Checksums the vendored spec against `PROVENANCE.md`. |

`okf_conformance.py` itself is the deliverable for *users* of these skills:
point it at your project's `.arche/`. Inside this repo it only ever sees
synthesized bundles and the fixture.

## `fixtures/pre_okf/`

A hand-built, deliberately pre-v0.2 Arche exercising every drift class at once —
lowercase types, `updated:` without `generated:`, string-list `sources`,
`status: accepted`, `raw:`/`url:` on a source page, an `adr-` page still typed
`concept`, no subdirectory indexes, no `okf_version`, a `.md` file under `raw/`,
and `## [date] op | text` log headings.

Its **primary job is manual**: it is the scratch bed for running `/arche-lint`
against, since a skill cannot be unit tested. Copy it somewhere, run the skill,
and confirm the repair plan names H1, H3, H4, T1, T2, F1, F3, F5, F6, S1, and S4.

`PreOkfFixtureTests` in `test_okf_conformance.py` pins the *checker's* view of
it — exactly three rules across four findings — so the one realistic bundle in
the repo can't silently regress. Those tests also assert the inverse: the
checker stays **silent** on the fixture's unknown types, missing indexes, and
string `sources`, because §11 forbids rejecting a bundle over any of them.

## Run the suites

    devbox run test                          # or, inside a devbox shell:
    cd tools && python3 -m unittest discover -p 'test_*.py' -v

CI runs exactly this on every pull request — see
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
