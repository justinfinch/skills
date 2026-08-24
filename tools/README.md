# tools

Development tooling for this repository. **Nothing here ships.**
`npx skills add justinfinch/skills` installs from `skills/`; this directory
sits at the repo root and never goes with it. Users of the skills never
receive these files, and these files never run against this repo's own
contents either.

## What `okf_conformance.py` is actually for

Seven skills ship 15 static templates between them:

| Skill | Templates |
| :--- | :--- |
| `arche-init` | `SCHEMA`, `index`, `subindex`, `log` |
| `arche-ingest` | `source`, `entity`, `concept` |
| `arche-architect` | `ard`, `sad`, `adr` |
| `arche-query` | `query` |
| `arche-discover` | `discovery` |
| `arche-tell` | `story` |
| `write-guidance` | `guidance`, `pack-skill` |

14 of those 15 render into the sample bundle. The fifteenth,
`pack-skill.template.md`, is a `write-guidance` template that is not an OKF
page at all: it's a `SKILL.md` skeleton carrying `name`/`description`, not
`type`, for the `guidance-*` packs `write-guidance` authors. `TEMPLATE_TARGETS`
maps it to `None`, and a `None` target marks a skill-owned template that must
never be rendered into a bundle — `render_all` skips anything mapped to `None`
rather than failing §11 rule 2 by rendering it. That skip is live today:
`find_templates`'s widened glob discovers the file, `render_all` matches it to
its `None` sentinel, and it never reaches the conformance checker.

Those 14 rendered OKF pages are what a user's Arche will actually be built
from, and the whole OKF v0.2 migration was a rewrite of their frontmatter. A
skill is a prompt and cannot be unit tested — but a template is a static file,
and a static file can be rendered and checked.

So: `render_templates.py` substitutes sample tokens into the 14 OKF templates
and writes each to the path it would occupy in a real bundle
(`story.template.md` → `stories/sample-story.md`, and so on), producing a
throwaway directory with reserved files plus one page per type. The 15th
template is discovered along with the rest but skipped at write time, per the
`None` sentinel above. `test_templates.py` runs `okf_conformance.py` over that
directory.

**That is the entire automated job of this checker**: proving the pages these
skills emit satisfy OKF §11. It is not a linter for the repo, and it is not
something users run.

### Why it takes a bundle path

Because the other way you use it is by hand, while developing. Bootstrap a
throwaway Arche with `/arche-init` into a scratch directory and check what the
skill *really* produced, rather than what its templates suggest it should:

    devbox run check /tmp/scratch/.arche
    devbox run check tools/fixtures/pre_okf     # the fixture, for a quick look

The path is required — there is no default, because this repo has no `.arche/`
of its own and shouldn't. It holds the skills that build one.

Exit code 0 when conformant, 1 when findings exist, 2 on usage or environment
error (bad arguments, missing PyYAML). A broken environment must never look
like a non-conformant bundle, so 1 is reserved for findings alone.

### Scope, and why it is independent of `arche-lint`

The checker implements only §11's three hard rules plus the reserved-file
structure they point at (§8, §9). The spec is vendored at
[`spec/okf/v0.2/`](../spec/okf/v0.2/) — see its `PROVENANCE.md`. OKF publishes
no validator and recommends none, so this file is the oracle.

It is deliberately not built on `arche-lint`, because lint is the skill that
*claims* to enforce conformance and testing that claim with the claimant is
circular. Note what that does and does not buy: this checker verifies the
seven writer skills' output, and **nothing automated verifies `arche-lint`
itself.**
Lint's remit is mostly Tier-2 house conventions this checker ignores on
purpose, and §11 forbids consumers from rejecting a bundle over unknown `type`
values, missing `index.md`, broken links, or missing optional fields — all of
which lint reports and this checker must stay silent on. Lint's own
verification is the manual procedure below.

## `fixtures/pre_okf/`

A hand-built, deliberately pre-v0.2 Arche exercising every drift class at once —
lowercase types, `updated:` without `generated:`, string-list `sources`,
`status: accepted`, `raw:`/`url:` on a source page, an `adr-` page still typed
`concept`, no subdirectory indexes, no `okf_version`, a `.md` file under `raw/`,
and `## [date] op | text` log headings.

**This is where `arche-lint` gets verified, and it is manual.** Copy the fixture
somewhere, run `/arche-lint` against the copy, and confirm the repair plan names
H1, H3, H4, T1, T2, F1, F3, F5, F6, S1, and S4.

`PreOkfFixtureTests` in `test_okf_conformance.py` pins only the *checker's* view
of it — three rules across four findings — so the one realistic bundle in the
repo can't silently regress. Those tests also assert the inverse: the checker
stays silent on the fixture's unknown types, missing indexes, and string
`sources`, because §11 forbids rejecting a bundle over any of them.

## The suites

| Suite | Runs against |
| :--- | :--- |
| `test_templates.py` | A bundle synthesized from the 14 OKF-page templates, out of 15 skill-owned templates total (see the `None`-sentinel mechanism above for how the 15th, non-OKF template is excluded). The load-bearing one — it tests the exact text the skills emit. |
| `test_okf_conformance.py` | Small hand-built bundles in temp dirs (unit coverage for the checker), plus the `pre_okf` fixture. |
| `test_spec_pin.py` | No bundle. Checksums the vendored spec against `PROVENANCE.md`. |

Requirements: Python 3.12+ and PyYAML, both declared in the repo's
`devbox.json`. Run `devbox shell` (or let direnv load it on `cd`) and they are
on `PATH`. Without devbox, `python3 -m pip install --user pyyaml`.

    devbox run test                          # or, inside a devbox shell:
    cd tools && python3 -m unittest discover -p 'test_*.py' -v

CI runs exactly this on every pull request — see
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
