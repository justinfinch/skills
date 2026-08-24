# Guidance Packs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a `guidance-*` skill family — installable packs of durable architectural knowledge that an agent consults during a decision and cites in the resulting ADR — plus the `write-guidance` skill that authors them, proven by extracting `arche-architect`'s lens roster into the first pack.

**Architecture:** A pack is one directory that is simultaneously an agent skill (a thin `SKILL.md` acting as relevance trigger) and an OKF v0.2 bundle (`bundle/`, holding the citable content as `Guidance` pages). Guidance never enters a user's `./.arche/`; the Arche cites packs through `sources:`. Distribution rides the existing `npx skills add` installer — no new tooling.

**Tech Stack:** Markdown with YAML frontmatter (OKF v0.2), Python 3.12 + PyYAML for the template-conformance harness in `tools/`, devbox for the environment.

## Global Constraints

- **Branch:** `guidance-packs`, already created and tracking `origin/guidance-packs`. Do not branch again.
- **Spec:** `docs/superpowers/specs/2026-08-24-guidance-packs-design.md`. Read it before Task 1.
- **Skill naming:** `name` in frontmatter MUST match the parent directory name exactly. 1–64 chars, `[a-z0-9-]`, no leading/trailing/consecutive hyphens.
- **Layout:** flat under `skills/`. No category subdirectories — `skills/guidance-outbox/`, never `skills/guidance/outbox/`.
- **Four prefixes:** `arche-*` (Arche workflows), `devbox-*` (env workflows), `guidance-*` (consulted knowledge, never runs), `write-*` (authoring tools).
- **Links:** relative only. Never bundle-absolute (`](/...`) — `test_no_bundle_absolute_links` enforces this on every rendered template.
- **Status vocabulary:** `draft | stable | deprecated` only. `proposed`, `accepted`, and `superseded` are retired and enforced against by `test_no_retired_status_vocabulary`.
- **Packs carry no `log.md`.** Git history is a pack's changelog. `index.md` is kept for progressive disclosure.
- **Never write `verified:`** in any template or page. Human sign-off only.
- **Run tests with** `devbox run test` from the repo root (or `cd tools && python3 -m unittest discover -p 'test_*.py' -v` inside a devbox shell). CI runs exactly this.
- **Commit after every task.** Do not squash tasks together.

---

## File Structure

| Path | Responsibility |
| :--- | :--- |
| `tools/render_templates.py` | Modify — widen template discovery beyond `arche-*`; add the `Guidance` target and a skip sentinel for non-OKF templates |
| `skills/write-guidance/SKILL.md` | Create — the authoring skill: extract / author / revise modes, lenses as attackers, the counter-case rule |
| `skills/write-guidance/assets/guidance.template.md` | Create — the `Guidance` page skeleton. Rendered and conformance-checked by the harness |
| `skills/write-guidance/assets/pack-skill.template.md` | Create — the thin `SKILL.md` skeleton every pack gets. Not an OKF page; skipped by the renderer |
| `skills/guidance-architecture-lenses/SKILL.md` | Create — first pack's trigger |
| `skills/guidance-architecture-lenses/bundle/index.md` | Create — pack catalog |
| `skills/guidance-architecture-lenses/bundle/concepts/expert-lens-interrogation.md` | Create — `Guidance`: the technique of interrogating a design through named lenses |
| `skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md` | Create — `Concept`: the thirteen architects, moved from `LENSES.md` |
| `skills/arche-architect/references/LENSES.md` | Delete — content moves into the pack |
| `skills/arche-architect/SKILL.md` | Modify — soft pack dependency, gap signal in Phase 3, pack citation in Phase 4, roster in frontmatter |
| `README.md` | Modify — document the family and the naming convention |

**Why the lens content splits into two pages.** This is the design's own test, and the honest result is that `LENSES.md` does not fit one `Guidance` page. A lens is not a technique with trade-offs; *using a panel of lenses* is. So the technique gets the `Guidance` shape with its full section set, and the roster becomes a `Concept` page it links to. This also exercises the spec's claim that a pack may hold several pages under one trigger.

---

### Task 1: `Guidance` page type and harness support

**Files:**
- Modify: `tools/render_templates.py:13-28` (SAMPLE_TOKENS), `:33-47` (TEMPLATE_TARGETS), `:56-74` (find_templates, render_all)
- Create: `skills/write-guidance/assets/guidance.template.md`
- Test: `tools/test_templates.py` (existing suite — no new test file)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `guidance.template.md` with tokens `{{TITLE}}`, `{{DESCRIPTION}}`, `{{DATE}}`, `{{TIMESTAMP}}`, `{{ACTOR}}`, `{{STALE_AFTER}}`. `render_templates.find_templates()` now discovers `write-*/assets/*.template.md` in addition to `arche-*`. `TEMPLATE_TARGETS` accepts `None` as a value meaning "not an OKF page; do not render". Tasks 2 and 4 rely on both.

- [ ] **Step 1: Widen template discovery**

In `tools/render_templates.py`, replace `find_templates`:

```python
def find_templates(skills_dir: Path) -> list[Path]:
    """Every skill-owned template, whichever family owns it.

    `write-*` skills own templates too (write-guidance emits Guidance pages),
    so discovery can't stay scoped to `arche-*`.
    """
    return sorted(
        [*skills_dir.glob("arche-*/assets/*.template.md"),
         *skills_dir.glob("write-*/assets/*.template.md")]
    )
```

- [ ] **Step 2: Create the Guidance template**

Create `skills/write-guidance/assets/guidance.template.md`:

```markdown
---
type: Guidance
title: {{TITLE}}
description: {{DESCRIPTION}}
tags: []
created: {{DATE}}
generated: { by: {{ACTOR}}, at: {{TIMESTAMP}} }
status: draft
stale_after: {{STALE_AFTER}}
sources: []
---

# {{TITLE}}

## Technique

What the technique is, in two or three sentences. Active voice. State the
mechanism, not the benefit.

## Applies when

- An observable condition about a project under which this is the right call.
- Another. Conditions are facts someone can check, not preferences or taste.

## Doesn't apply when

- A condition under which this is the wrong call.
- Another, ideally one that is tempting rather than obvious.

## Trade-offs

What the technique buys, and what it costs to buy it. Name both halves; a
trade-off with only an upside is an advertisement.

## Failure modes

What actually breaks once this is running, and what it looks like from the
outside when it does.

## Alternatives considered

- **Alternative** — the conditions under which it wins instead.
- **Alternative** — the conditions under which it wins instead.
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `devbox run test`

Expected: FAIL. `TemplateTargetTests.test_every_template_has_a_target` reports `['guidance.template.md']`, and the three `RenderedTemplateTests` error with `KeyError: guidance.template.md has no entry in TEMPLATE_TARGETS`.

This is the real red: discovery now sees a template the harness has no home for.

- [ ] **Step 4: Add the sample token**

In `tools/render_templates.py`, add to `SAMPLE_TOKENS` after the `{{TIMESTAMP}}` line:

```python
    "{{STALE_AFTER}}": "2028-01-01",
```

- [ ] **Step 5: Add the target and the skip sentinel**

In `tools/render_templates.py`, add to `TEMPLATE_TARGETS` after the `adr.template.md` line:

```python
    # A pack's Guidance pages live in its bundle's concepts/ directory, so the
    # synthesized Arche bundle is a fine place to prove they conform.
    "guidance.template.md": "concepts/sample-guidance.md",
    # None means "skill-owned template, but not an OKF page". pack-skill is a
    # SKILL.md skeleton: it carries `name`/`description`, not `type`, so
    # rendering it into a bundle would fail SPEC 11 rule 2 by design.
    "pack-skill.template.md": None,
```

- [ ] **Step 6: Teach `render_all` to skip sentinel entries**

In `tools/render_templates.py`, replace the body of the loop in `render_all`:

```python
def render_all(skills_dir: Path, dest: Path) -> list[Path]:
    """Render every skill template into `dest`. Returns the paths written."""
    written = []
    for template in find_templates(skills_dir):
        if template.name not in TEMPLATE_TARGETS:
            raise KeyError(
                f"{template.name} has no entry in TEMPLATE_TARGETS; "
                "add one so the harness knows where it belongs in a bundle"
            )
        target = TEMPLATE_TARGETS[template.name]
        if target is None:
            continue
        out = dest / target
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(template.read_text(encoding="utf-8")), encoding="utf-8")
        written.append(out)
    return written
```

Note the change in failure semantics: a *missing* entry still raises, a `None` entry skips. Without splitting those cases, `pack-skill.template.md` would either crash the harness or get rendered into a bundle it does not belong in.

- [ ] **Step 7: Run tests to verify they pass**

Run: `devbox run test`

Expected: PASS, with the test count up from 36 (the rendered-bundle suites now cover one more page).

- [ ] **Step 8: Confirm the rendered page really is conformant**

Run:

```bash
devbox run check tools/fixtures/pre_okf
```

Expected: exit 1 with the fixture's four known findings — this confirms the checker is actually running and reporting, not silently passing everything.

- [ ] **Step 9: Commit**

```bash
git add tools/render_templates.py skills/write-guidance/assets/guidance.template.md
git commit -m "Add the Guidance page type and widen the template harness

find_templates was scoped to arche-*, so write-guidance's templates were
invisible to the conformance harness. Widen it to write-* as well, and add
a None sentinel to TEMPLATE_TARGETS for skill-owned templates that are not
OKF pages -- pack-skill.template.md carries name/description, not type, so
rendering it into a bundle would fail SPEC 11 rule 2 by design."
```

---

### Task 2: The `write-guidance` skill

**Files:**
- Create: `skills/write-guidance/SKILL.md`
- Create: `skills/write-guidance/assets/pack-skill.template.md`
- Test: `tools/test_templates.py` (existing suite)

**Interfaces:**
- Consumes: `guidance.template.md` and the `None` sentinel from Task 1.
- Produces: the `skills/write-guidance/` skill directory. Task 3 uses this skill's documented pack layout (`SKILL.md` + `bundle/index.md` + `bundle/concepts/*.md`) as the shape it builds by hand.

- [ ] **Step 1: Create the pack `SKILL.md` template**

Create `skills/write-guidance/assets/pack-skill.template.md`:

```markdown
---
name: guidance-{{SLUG}}
description: {{DESCRIPTION}} Consult when {{TRIGGER}}. Read `bundle/` and cite the pages that inform a decision in that decision's record — in an Arche, the ADR's `sources:`. This pack is knowledge, not a workflow: it decides nothing on its own and writes nothing.
---

# guidance-{{SLUG}}

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Read [bundle/index.md](bundle/index.md), then the pages relevant to the
   decision actually in play.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite it in that decision's record so the
   rationale outlives the conversation.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

## What this pack is not

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
```

- [ ] **Step 2: Run tests to verify the new template is skipped, not rendered**

Run: `devbox run test`

Expected: PASS. `pack-skill.template.md` is discovered by the widened glob, matched to its `None` sentinel, and skipped — so its `name:`/`description:` frontmatter never reaches the conformance checker. If this fails with a SPEC 11 rule 2 finding about a missing `type`, Task 1 Step 6 was not applied.

- [ ] **Step 3: Write the skill**

Create `skills/write-guidance/SKILL.md`:

````markdown
---
name: write-guidance
description: Author or extract a guidance pack — an installable `guidance-*` skill whose `bundle/` holds OKF v0.2 `Guidance` pages stating when a technique is the right call and when it isn't. Three modes — extract (generalize recurring decisions out of existing project Arches into "applies when" conditions), author (greenfield on a topic), revise (a pack hit `stale_after` or reality moved). Uses the architect lenses adversarially, to attack what's written rather than to design. Use when the user says "write guidance", "extract guidance", "make a guidance pack", "turn this into a pack", or when an `/arche-architect` session emitted a gap signal for an uncovered decision area. NOT for recording what THIS project decided — that is an ADR, and belongs to `/arche-architect`.
---

# write-guidance

Author a **guidance pack**: durable, general architectural knowledge, packaged as
an installable skill and a citable OKF bundle.

The distinction this skill exists to hold: an ADR asserts *"we decided X, on
this date, in this context."* A `Guidance` page asserts *"in situations like C,
X is usually right — and here is when it isn't."* The first is institutional
memory and belongs in a project's Arche. The second travels between projects
and must never be filed into one.

## Pack layout

```
skills/guidance-<topic>/
  SKILL.md              # the relevance trigger; thin by design
  bundle/
    index.md            # catalog; no frontmatter
    concepts/
      <slug>.md         # one or more Guidance pages
```

No `log.md` — a pack's changelog is its git history. `SKILL.md` is the doorbell,
not the content: it carries the trigger and nothing that duplicates the bundle.

## Preflight

1. Read this skill's [guidance.template.md](assets/guidance.template.md) and
   [pack-skill.template.md](assets/pack-skill.template.md).
2. If `guidance-architecture-lenses` is installed, read its
   `bundle/concepts/lens-roster.md`. It is the roster this skill attacks with.
   If it is not installed, say so once and proceed — the attacks below still
   work, they are just less specific.
3. Establish the mode: **extract**, **author**, or **revise**. If the user
   hasn't said, ask once.

## Mode: extract

Generalize recurring decisions out of existing projects.

1. Ask for the project paths. Two or more is the point — one project yields a
   testimonial, not guidance.
2. In each project, read `./.arche/concepts/` for pages typed `Architecture
   Decision Record` and `Solution Architecture Document`, plus any infra
   manifests the decisions reference.
3. Find techniques that recur **under different names**. Project A's
   `adr-event-delivery` and project B's `adr-outbox` are one candidate, not two.
   Report the candidate set with one-line glosses and let the user cut it.
4. For each surviving candidate, do the central move: **convert project
   particulars into conditions, never delete them.**

   > *"We already run Postgres and can't justify a broker for three consumers"*
   > becomes
   > **Applies when:** single relational store; consumer count low enough that a
   > broker isn't justified.

   Deleting the context is what turns guidance into a context-free best
   practice. If a particular resists becoming a condition, it is project
   context and belongs in that project's ADR, not in the pack.
5. Run the attacks. File the pack.

**Sanitize by default.** Evidence like *"decided in acme-billing"* is fine in a
private pack and a leak in a public one. Cite the *shape* of the evidence —
"two internal services, roughly five consumers each" — not client names, repo
names, or internal system names. Ask before including any identifier.

## Mode: author

Greenfield on a topic. Interview one question at a time, recommendation first,
same shape `/arche-architect` uses. Drive toward the six sections; the two that
take real work are **Doesn't apply when** and **Failure modes**, so spend the
questions there rather than polishing **Technique**.

## Mode: revise

A pack hit its `stale_after`, or reality moved.

1. Read the existing pages. Establish what specifically changed — a new option,
   a deprecation, a CVE, a shifted default.
2. Re-run the attacks against the *current* world, not the world at authoring
   time.
3. Rewrite the whole `generated` mapping — both `by` and `at`. Never write
   `verified`.
4. Strike superseded claims with `~~strikethrough~~` and a replacement claim
   beside them. Never silently overwrite: the trail of "we thought X until Y"
   is most of what a reader is here for.
5. Set a new `stale_after`. If you can't name a date, you don't understand the
   decay rate yet — ask.

## The attacks

Where `/arche-architect` uses lenses to help you design, this skill uses them to
attack what you have written. The failure mode of guidance is writing down what
you happened to do and calling it universal.

| Lens | Attack |
| :--- | :--- |
| Nygard | "Your Failure modes section has two entries. What actually pages someone at 3am?" |
| Ford | "Under what future does this stop being right? That is your `stale_after`." |
| Helland | "You have assumed a consistency model without stating it." |
| Hohpe | "This presumes a particular integration shape. Say which." |
| Evans | "Is that your project's vocabulary, or the domain's?" |
| Richards | "You recommended it without naming what it costs." |
| Newman | "You have described a boundary. Is the granularity claim separate?" |
| Bass | "Which quality attribute does this move, and what does it cost the others?" |

Run at least Nygard, Ford, and Richards on every page. They map to the three
sections most likely to be thin.

## The counter-case rule

**No recommendation ships without its counter-case.**

Refuse to file a pack whose `Doesn't apply when` section is empty, or whose
entries are non-conditions (*"when it doesn't fit"*, *"when you don't need it"*).
Say plainly that the section is the gate and ask for the real counter-case. If
the user genuinely cannot name one, the honest outcome is that this isn't
guidance yet — offer to file it as `status: draft` with the gap stated in the
body, rather than shipping a testimonial.

## Writing the pack

1. Confirm the pack slug: `guidance-<topic>`, kebab-case. The directory name and
   the `name:` frontmatter must match exactly.
2. Write `skills/guidance-<topic>/SKILL.md` from
   [pack-skill.template.md](assets/pack-skill.template.md).
3. Write each page to `bundle/concepts/<slug>.md` from
   [guidance.template.md](assets/guidance.template.md). Set `description:` — it
   is the index gloss. Write `generated: { by: write-guidance/<model-id>, at:
   <ISO 8601 UTC> }` with the model actually running. Never write `verified`.
4. Write `bundle/index.md`, no frontmatter, entries as
   `* [Title](concepts/<slug>.md) - description.` where the gloss is exactly the
   page's `description`.
5. Verify: `devbox run check skills/guidance-<topic>/bundle`. Exit 0 or fix.
6. Add the pack to the repo `README.md` skill list.

A page whose reasoning is genuinely general but whose *type* isn't `Guidance` —
a roster, a taxonomy, a comparison table — is a `Concept` page in the same
bundle. Don't force the six sections onto content that isn't a technique.

## Discipline

- Two projects minimum for extract mode. One is a testimonial.
- Conditions must be checkable facts, not preferences.
- `Doesn't apply when` is a gate, not a section.
- Sanitize by default; ask before including any identifier.
- Never file a guidance page into a project's `./.arche/`.
- Never write `verified`.

## Output

End with one line: `Guidance pack <slug> → <N> page(s) filed. Bundle conforms.`
````

- [ ] **Step 4: Verify the skill's frontmatter is valid**

Run:

```bash
python3 - <<'PY'
import re, sys, pathlib
p = pathlib.Path("skills/write-guidance/SKILL.md")
text = p.read_text()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
assert m, "no frontmatter"
import yaml
fm = yaml.safe_load(m.group(1))
assert fm["name"] == p.parent.name, f'name {fm["name"]!r} != dir {p.parent.name!r}'
assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm["name"]), "bad name chars"
assert 1 <= len(fm["description"]) <= 1024, len(fm["description"])
print("ok:", fm["name"], len(fm["description"]), "chars")
PY
```

Expected: `ok: write-guidance <n> chars`, with n under 1024.

- [ ] **Step 5: Run the full suite**

Run: `devbox run test`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/write-guidance
git commit -m "Add write-guidance, the pack authoring skill

Three modes -- extract, author, revise -- over one discipline. Extract's
central move is converting project particulars into 'applies when'
conditions rather than deleting them, since deleting context is what turns
guidance into a context-free best practice.

Lenses are used adversarially here rather than generatively: the failure
mode of guidance is writing down what you happened to do and calling it
universal. The counter-case rule is a gate, not a section -- a pack with an
empty 'Doesn't apply when' is a testimonial and the skill refuses to file it."
```

---

### Task 3: Extract `guidance-architecture-lenses`

**Files:**
- Create: `skills/guidance-architecture-lenses/SKILL.md`
- Create: `skills/guidance-architecture-lenses/bundle/index.md`
- Create: `skills/guidance-architecture-lenses/bundle/concepts/expert-lens-interrogation.md`
- Create: `skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md`
- Delete: `skills/arche-architect/references/LENSES.md`

**Interfaces:**
- Consumes: the pack layout from Task 2.
- Produces: `skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md`, which Task 4 adds Richards to and Task 5 points `arche-architect` at.

- [ ] **Step 1: Create the pack directories and move the roster**

```bash
mkdir -p skills/guidance-architecture-lenses/bundle/concepts
git mv skills/arche-architect/references/LENSES.md \
       skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md
rmdir skills/arche-architect/references 2>/dev/null || true
```

`git mv` rather than create-and-delete so the history of the twelve entries follows the content.

- [ ] **Step 2: Give the roster page OKF frontmatter and reframe its header**

In `skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md`, replace the file's first five lines — from `# Lenses` through the line beginning `When two lenses disagree` — with:

```markdown
---
type: Concept
title: The architect lens roster
description: Thirteen named architects, what each pushes on, and the trigger cues that should surface them in a design conversation.
tags: [architecture, lenses]
created: 2026-08-24
generated: { by: write-guidance/claude-opus-5, at: 2026-08-24T00:00:00Z }
status: stable
sources: []
---

# The architect lens roster

Thirteen architects invoked by name during a design conversation. Each entry
gives what they push on and the **trigger cues** that should cause you to name
them. Lenses are pedagogy — the reader learns whose framework is in play — not
theatrics. Do not impersonate; do not caricature; do not invent quotes.

When two lenses disagree on the same question (common with Vernon and Helland on
consistency, and with Newman and Richards on granularity), surface both and ask
the user to pick. When no lens applies cleanly, ask the question in your own
voice.

See [Interrogating a design through expert lenses](expert-lens-interrogation.md)
for when this technique is the right call and when it isn't.
```

Set `generated.at` to the actual current UTC timestamp and `generated.by` to the model actually running, not the placeholder above.

Leave the twelve `## <Name> — <territory>` entries and the closing `## Using the panel` section exactly as they are. Richards is Task 4; keep this task a pure move so the diff is reviewable.

- [ ] **Step 3: Write the technique page**

Create `skills/guidance-architecture-lenses/bundle/concepts/expert-lens-interrogation.md`:

```markdown
---
type: Guidance
title: Interrogating a design through expert lenses
description: Drive architectural questioning from a fixed roster of named expert viewpoints so coverage is deliberate rather than incidental.
tags: [architecture, method, review]
created: 2026-08-24
generated: { by: write-guidance/claude-opus-5, at: 2026-08-24T00:00:00Z }
status: stable
stale_after: 2030-01-01
sources: []
---

# Interrogating a design through expert lenses

## Technique

Walk a design by rotating through a fixed roster of named expert viewpoints,
naming the lens as you apply it. Each lens owns a territory and carries trigger
cues; when a cue fires, you ask that lens's question in that lens's terms. The
roster is [the thirteen architects](lens-roster.md).

## Applies when

- The design has genuine trade-offs rather than one obvious answer.
- Coverage matters more than speed — you would rather find the missing
  consistency question now than in production.
- The people in the room share enough vocabulary that "Nygard would ask" is
  shorthand rather than a puzzle, or are willing to learn it as they go.
- You are attacking work already written, where the risk is a blind spot the
  author shares with you.

## Doesn't apply when

- The question is business, customer, market, or regulatory — that is divergent
  ideation and wants a facilitation technique, not an architecture panel.
- The decision is genuinely reversible and cheap. Rotating thirteen lenses over
  a two-day-to-undo choice costs more than the choice.
- The roster would be theatre: a room that reads named lenses as affectation
  gets less from them than from the plain question underneath.
- You already know which single territory is in play. Reach for that lens
  directly rather than performing the rotation.

## Trade-offs

Buys deliberate coverage — the questions you would not have thought to ask get
asked, because a lens owns them whether or not they occurred to you — and a
shared vocabulary that compresses long arguments into a name. Costs
conversational overhead, and creates a standing temptation to force a lens onto
a question it does not fit, which produces confident irrelevance.

## Failure modes

Naming the same lens for every question, which means the framing is being forced
rather than found. Impersonation drifting into caricature, at which point the
lens stops carrying information and starts carrying performance. Treating roster
completion as design completion — thirteen lenses applied to a problem you never
actually understood is thirteen wasted questions. And lens-shopping: rotating
until one of them endorses the answer you already had.

## Alternatives considered

- **Unstructured expert judgment** — wins when a genuine expert in the specific
  territory is in the room. The roster substitutes for expertise; it does not
  beat it.
- **ATAM or a formal scenario-based evaluation** — wins when the decision needs
  a defensible audit trail and there is budget for a multi-day structured
  workshop with real stakeholders.
- **A flat review checklist** — wins for repeated, well-understood classes of
  change. Cheaper and more consistent, but it only ever asks what someone
  already knew to write down.
```

Set `generated` to the real actor and timestamp.

- [ ] **Step 4: Write the bundle index**

Create `skills/guidance-architecture-lenses/bundle/index.md` — no frontmatter:

```markdown
# Concepts

* [Interrogating a design through expert lenses](concepts/expert-lens-interrogation.md) - Drive architectural questioning from a fixed roster of named expert viewpoints so coverage is deliberate rather than incidental.
* [The architect lens roster](concepts/lens-roster.md) - Thirteen named architects, what each pushes on, and the trigger cues that should surface them in a design conversation.
```

Each gloss is exactly the target page's `description`.

- [ ] **Step 5: Write the pack `SKILL.md`**

Create `skills/guidance-architecture-lenses/SKILL.md`:

```markdown
---
name: guidance-architecture-lenses
description: A roster of thirteen named architects — Fowler, Evans, Vernon, Nygard, Hohpe, Newman, Ford, Richards, Helland, Vogels, Bass, Beck, Martin — with the territory each owns and the trigger cues that should surface them, plus guidance on when driving a design conversation through named lenses is the right technique and when it is theatre. Consult when running or reviewing an architecture design session, attacking written architectural guidance, or when a design question needs a viewpoint you would not have thought to apply. Read `bundle/` and cite the pages that inform a decision in that decision's record. This pack is knowledge, not a workflow: it decides nothing on its own and writes nothing.
---

# guidance-architecture-lenses

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle.

- [Interrogating a design through expert lenses](bundle/concepts/expert-lens-interrogation.md)
  — the technique, with the conditions it holds under and the ones it doesn't.
- [The architect lens roster](bundle/concepts/lens-roster.md) — the thirteen,
  with trigger cues.

## How to use this pack

1. Read the technique page first, and check its **Doesn't apply when** against
   the conversation you are actually in. A design panel run where it doesn't fit
   is worse than no panel.
2. Load the roster when a cue fires, not preemptively. You are looking for the
   lens whose territory the question already sits in.
3. When two lenses disagree — Vernon and Helland on consistency, Newman and
   Richards on granularity — surface both and let the user pick. Do not
   arbitrate silently.
4. If a lens shaped a decision, cite this pack in that decision's record so the
   reasoning outlives the conversation.

## What this pack is not

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
```

- [ ] **Step 6: Verify the bundle conforms**

Run:

```bash
devbox run check skills/guidance-architecture-lenses/bundle
```

Expected: exit 0, no findings. If the checker reports "only a bundle-root index.md may carry frontmatter", the index in Step 4 was given frontmatter — remove it.

- [ ] **Step 7: Confirm the lens content survived the move intact**

Run:

```bash
grep -c '^## ' skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md
git show HEAD:skills/arche-architect/references/LENSES.md | grep -c '^## '
```

Expected: both print `13` — twelve architect entries plus `## Using the panel`. Task 4 takes it to 14.

- [ ] **Step 8: Run the full suite**

Run: `devbox run test`

Expected: PASS. Nothing in the harness globs `references/`, so removing `LENSES.md` moves no tests.

- [ ] **Step 9: Commit**

```bash
git add -A skills/guidance-architecture-lenses skills/arche-architect
git commit -m "Extract the lens roster into guidance-architecture-lenses

The first pack, and the design's own test. The honest result: LENSES.md
does not fit a single Guidance page. A lens is not a technique with
trade-offs -- using a panel of lenses is. So the technique takes the
Guidance shape with its full section set, and the roster stays a Concept
page beside it. That split is what a multi-page pack is for.

Content moved with git mv so the history of the twelve entries follows it.
Richards lands next, as the first content change made through the new shape."
```

---

### Task 4: Add the Mark Richards lens

**Files:**
- Modify: `skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md`

**Interfaces:**
- Consumes: `lens-roster.md` from Task 3.
- Produces: a thirteen-architect roster. Task 5 relies on Richards existing when it updates `arche-architect`'s frontmatter list.

- [ ] **Step 1: Insert the Richards entry**

In `skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md`, insert between the `## Neal Ford` block and the `## Pat Helland` block — i.e. immediately after Ford's last trigger-cue bullet and its following `---`:

```markdown
## Mark Richards — architecture styles, granularity, and explicit trade-offs

**Pushes on:** deliberate style selection (layered, pipeline, microkernel, service-based, event-driven, space-based, microservices) and what each buys; granularity as distinct from boundaries — disintegrators vs. integrators; ranking driving characteristics down to a handful; refusing any recommendation that doesn't state its cost.

**Trigger cues:**
- A style is in play implicitly ("we'll do microservices") → ask which style this is and which characteristics drove the choice, rather than letting the style pick the characteristics.
- Services keep getting smaller → ask for the disintegrator forcing the split, and the integrator arguing against it.
- More than about seven driving characteristics are named → force a ranking; everything prioritized means nothing is.
- An option is recommended without its cost → "there are no best practices" — name what you're giving up, explicitly.

---
```

Ford sits immediately before Richards deliberately: they co-wrote *Fundamentals of Software Architecture*, and their territories abut without overlapping — Ford owns how an architecture changes over time, Richards owns which shape it takes now.

- [ ] **Step 2: Distinguish Richards from Newman in the header**

The header written in Task 3 Step 2 already names the Newman/Richards disagreement. Add the distinction to the entry itself, so a reader landing on it directly gets it. Replace Richards' `**Pushes on:**` paragraph (written in Step 1) with this — same text, one sentence appended:

```markdown
**Pushes on:** deliberate style selection (layered, pipeline, microkernel, service-based, event-driven, space-based, microservices) and what each buys; granularity as distinct from boundaries — disintegrators vs. integrators; ranking driving characteristics down to a handful; refusing any recommendation that doesn't state its cost. Where Newman asks *where the seam belongs*, Richards asks *how small is too small*; they disagree often, which makes them productive to surface together.
```

- [ ] **Step 3: Verify the count**

Run:

```bash
grep -c '^## ' skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md
grep -n 'thirteen\|twelve' skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md
```

Expected: `14` (thirteen architects plus `## Using the panel`), and no occurrence of "twelve" anywhere in the file.

- [ ] **Step 4: Verify the bundle still conforms**

Run: `devbox run check skills/guidance-architecture-lenses/bundle`

Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add skills/guidance-architecture-lenses/bundle/concepts/lens-roster.md
git commit -m "Add Mark Richards to the lens roster

arche-architect's Phase 3 already read 'Patterns and trade-offs (Fowler,
Richards)' while LENSES.md defined twelve lenses, none of them Richards --
the workflow cited a lens the roster never defined. This closes that.

His territory was genuinely unclaimed: Ford holds evolutionary architecture,
Newman holds service boundaries, Bass holds the quality-attribute taxonomy,
and nobody held style selection or granularity. Placed after Ford, whom he
co-wrote Fundamentals of Software Architecture with."
```

---

### Task 5: `arche-architect` integration

**Files:**
- Modify: `skills/arche-architect/SKILL.md` — frontmatter roster, preflight step 5, Phase 3 step 1, Phase 3 conversation discipline, Phase 4 step 4, See also

**Interfaces:**
- Consumes: `guidance-architecture-lenses` from Tasks 3–4.
- Produces: no downstream dependency. Task 6 documents what this establishes.

- [ ] **Step 1: Add Richards to the frontmatter roster**

In `skills/arche-architect/SKILL.md`, in the `description:` line, replace:

```
(Fowler, Evans, Vernon, Nygard, Hohpe, Newman, Ford, Helland, Vogels, Bass, Beck, Martin)
```

with:

```
(Fowler, Evans, Vernon, Nygard, Hohpe, Newman, Ford, Richards, Helland, Vogels, Bass, Beck, Martin)
```

- [ ] **Step 2: Repoint preflight at the pack, as a soft dependency**

Replace preflight step 5 in full:

```markdown
5. Read the lens roster. It ships as the `guidance-architecture-lenses` pack:
   read its `bundle/concepts/lens-roster.md` and
   `bundle/concepts/expert-lens-interrogation.md`. If the pack isn't installed,
   say so once — *"lens naming will be coarse; `npx skills add
   justinfinch/skills --skill guidance-architecture-lenses` for the full
   roster"* — and continue. The branch list in Phase 3 names the relevant
   architects inline, so the grill still works without it; you lose the trigger
   cues, not the structure.
6. Read the three templates so you write pages in the canonical layout:
   [ard.template.md](assets/ard.template.md),
   [sad.template.md](assets/sad.template.md),
   [adr.template.md](assets/adr.template.md).
```

The dependency is soft on purpose. A hard requirement would mean installing
`arche-architect` alone leaves a skill that refuses to run, which is a worse
failure than a grill with less specific lens naming.

- [ ] **Step 3: Add the gap signal to Phase 3**

In Phase 3, after the numbered list item 4 (`**Explores the Arche or codebase instead of asking**…`), add item 5:

```markdown
5. **Names the gap when no guidance covers the question.** If a decision area
   has no installed `guidance-*` pack speaking to it, say so once as you enter
   that branch: *"nothing in the installed guidance covers event-delivery
   semantics — we're deciding this from first principles."* That is not an
   apology; it tells the user which parts of the session are re-derivation and
   flags a candidate for `/write-guidance` afterwards. Don't repeat it per
   question — once per branch.
```

- [ ] **Step 4: Add pack consultation to the conversation discipline**

In Phase 3's *Conversation discipline* list, after the bullet beginning `Inline-cite Arche pages as you go:`, add:

```markdown
- Consult installed `guidance-*` packs when their territory comes up, and check
  the page's **Doesn't apply when** against this project before recommending
  anything from it. A pack whose conditions don't hold here is evidence
  *against* the technique — say that out loud rather than skipping the page.
```

- [ ] **Step 5: Add pack citation to Phase 4**

In Phase 4 step 4 (writing ADRs), after the sentence ending `use \`draft\` only if the user explicitly wants the decision left open for further debate.`, add a new sub-bullet as the first item of that step's bullet list:

```markdown
   - If a `guidance-*` pack informed the decision, cite it in `sources:` with a
     stable `id`, the pack page's relative or installed path as `resource`, and
     the page title. The pack is why the trade-off was already framed; without
     the citation, that reasoning dies with the conversation. Cite the *page*,
     not the pack directory.
```

- [ ] **Step 6: Update See also**

Replace the See also line:

```markdown
- [LENSES.md](references/LENSES.md) — the twelve-architect panel with trigger cues
```

with:

```markdown
- `guidance-architecture-lenses` — the thirteen-architect panel with trigger cues, shipped as an installable guidance pack rather than owned by this skill
```

- [ ] **Step 7: Verify no dangling references to the moved file**

Run:

```bash
grep -rn "LENSES.md\|references/LENSES" skills/ README.md docs/ || echo "clean"
```

Expected: `clean`. Any hit is a dangling reference to the file Task 3 moved — fix it before committing.

- [ ] **Step 8: Run the full suite**

Run: `devbox run test`

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add skills/arche-architect/SKILL.md
git commit -m "Point arche-architect at the lens pack; add the gap signal

Three changes. The roster moves to guidance-architecture-lenses as a soft
dependency -- a hard one would leave a skill that refuses to run when
installed alone, which is worse than coarser lens naming, and Phase 3's
branch list already names the architects inline.

Phase 4 now cites any pack that informed a decision, so the reasoning
outlives the conversation. And Phase 3 names the gap when no pack covers a
branch, which is the signal /write-guidance consumes -- that is the loop
that stops the next project re-deriving this one's decisions."
```

---

### Task 6: Document the family

**Files:**
- Modify: `README.md` — skills list, a new naming-convention section, the workflow diagram's surroundings

**Interfaces:**
- Consumes: everything from Tasks 1–5.
- Produces: nothing downstream.

- [ ] **Step 1: Add the two new skills to the list**

In `README.md`, after the `arche-lint` bullet, add:

```markdown
- **[write-guidance](skills/write-guidance/SKILL.md)** — author or extract a guidance pack: extract mode generalizes recurring decisions out of existing project Arches into "applies when" conditions, author mode works greenfield, revise mode refreshes a pack that aged out. Uses the architect lenses adversarially and refuses to file a pack with an empty "Doesn't apply when".
- **[guidance-architecture-lenses](skills/guidance-architecture-lenses/SKILL.md)** — the first guidance pack: thirteen named architects with trigger cues, plus when driving a design conversation through named lenses is the right technique and when it's theatre. Consumed by `arche-architect` and `write-guidance`; owned by neither.
```

- [ ] **Step 2: Replace the Layout section**

Replace the `## Layout` section's code block and the sentence under it with:

````markdown
```
skills/
└── <skill-name>/
    └── SKILL.md
```

Flat — one directory per skill, each containing a `SKILL.md` with YAML
frontmatter (`name`, `description`). The `name` must match the directory name,
which is why the families are prefixes rather than subdirectories.

| Prefix | Kind |
| :--- | :--- |
| `arche-*` | Workflows that act on the repo's Arche |
| `devbox-*` | Workflows that act on the repo's dev environment |
| `guidance-*` | Knowledge that is consulted and cited; never runs |
| `write-*` | Tools that author the other kinds |

The prefix says what kind of thing a skill is, which matters once these install
flat alongside everyone else's.
````

- [ ] **Step 3: Add the guidance-packs section**

After the `### Open Knowledge Format` section, add:

````markdown
### Guidance packs

A `guidance-*` skill is a **pack**: durable architectural knowledge that travels
between projects, packaged as an installable skill whose `bundle/` is an OKF v0.2
bundle of `Guidance` pages.

```
skills/guidance-<topic>/
  SKILL.md       # relevance trigger; thin by design
  bundle/
    index.md
    concepts/<slug>.md
```

Packs are deliberately **not** part of the Arche, and never get copied into one.
The Arche holds what *this* organization decided; a pack holds knowledge that is
true whether or not the organization exists. Those have different provenance
(`generated.by` means nothing for a pack someone else wrote), different lifecycle
(Arche pages accrete, packs are versioned dependencies), and different audiences.

What connects them is citation. A `Guidance` page states when a technique is the
right call and — the load-bearing half — when it isn't:

```markdown
## Applies when
- Single relational store, and the write and the publish must not diverge.

## Doesn't apply when
- Your broker supports transactional publish.
- You can tolerate lost events.
```

`/arche-architect` consults installed packs during a grill and cites the ones
that informed a decision in the ADR's `sources:`. So a new project doesn't
inherit old answers — it inherits the trade-off space already framed, and the
ADR that comes out is genuinely its own. When a decision area has no pack
covering it, the grill says so; that gap signal is what `/write-guidance`
consumes, and the loop is why the next project doesn't start from scratch.

Packs carry no `log.md` — git history is the changelog.
````

- [ ] **Step 4: Verify every README link resolves**

Run:

```bash
python3 - <<'PY'
import re, pathlib
root = pathlib.Path(".")
bad = []
for m in re.finditer(r"\]\((?!https?://|#)([^)]+)\)", (root/"README.md").read_text()):
    target = (root / m.group(1).split("#")[0]).resolve()
    if not target.exists():
        bad.append(m.group(1))
print("broken:", bad or "none")
PY
```

Expected: `broken: none`.

- [ ] **Step 5: Run the full suite**

Run: `devbox run test`

Expected: PASS.

- [ ] **Step 6: Commit and push**

```bash
git add README.md
git commit -m "Document the guidance-pack family and the prefix convention

Names the four prefixes explicitly -- arche-*, devbox-*, guidance-*,
write-* -- since the prefix is what tells you the kind of thing a skill is
once these install flat alongside everyone else's, and the spec's
name-matches-directory rule rules out subdirectories.

States the boundary the whole design rests on: packs are never copied into
an Arche. The Arche holds what this organization decided; a pack holds what
is true regardless. Citation is what connects them."
git push
```

---

## Verification

After Task 6, confirm the spec's success criteria hold:

- [ ] **1. The pack installs.** `npx skills add justinfinch/skills --skill guidance-architecture-lenses` in a scratch directory resolves and copies the pack, `bundle/` included. If the installer flattens or drops `bundle/`, that is a finding to report — it would invalidate Decision 2 and needs a design answer, not a workaround.
- [ ] **2. The bundle conforms.** `devbox run check skills/guidance-architecture-lenses/bundle` exits 0.
- [ ] **3. Templates conform.** `devbox run test` passes, including the rendered `concepts/sample-guidance.md`.
- [ ] **4. Citation works end to end.** Run `/arche-architect` against a scratch Arche on a topic the pack covers. Confirm it loads the pack unprompted and the resulting ADR carries the pack page in `sources:`.
- [ ] **5. The gap signal fires.** Run the same session on a topic no pack covers. Confirm it says so once, per branch, without apologizing.
- [ ] **6. The counter-case rule bites.** Run `/write-guidance` in author mode and try to file a page with an empty `Doesn't apply when`. Confirm it refuses and offers `status: draft` with the gap stated.
- [ ] **7. Neither skill owns the roster.** `grep -rn "LENSES.md" skills/` returns nothing, and both `arche-architect` and `write-guidance` reference the pack.

Criteria 4–6 exercise skills, which are prompts and cannot be unit tested — they are manual, the same way `arche-lint`'s verification is manual per `tools/README.md`.

## Open risk

Success criterion 1 is the one that could force a design change. The vercel CLI
discovers skills by walking for `SKILL.md`; whether it copies sibling
directories like `bundle/` wholesale is assumed, not verified. If it doesn't,
the options are to nest the bundle under `references/` (which the installer
does carry), or to publish packs from a separate repo fetched by other means.
Check this early — ideally before Task 3 — rather than discovering it at the end.
