---
name: write-guidance
description: Author or extract a guidance pack — an installable `guidance-*` skill whose `bundle/` holds OKF v0.2 `Guidance` pages (plus supporting `Concept` pages) stating when a technique is the right call and when it isn't. Three modes — extract (generalize recurring decisions out of existing project Arches into "applies when" conditions), author (greenfield on a topic), revise (a pack hit `stale_after` or reality moved). Uses the architect lenses adversarially, to attack what's written rather than to design. Use when the user says "write guidance", "extract guidance", "make a guidance pack", "turn this into a pack", or when an `/arche-architect` session emitted a gap signal for an uncovered decision area. NOT for recording what THIS project decided — that is an ADR, and belongs to `/arche-architect`.
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
<skills-dir>/guidance-<topic>/
  SKILL.md              # the relevance trigger; thin by design
  bundle/
    index.md            # catalog; frontmatter carries okf_version and nothing else
    concepts/
      <slug>.md         # one or more Guidance pages (plus supporting Concept pages)
```

`<skills-dir>` is wherever the host project keeps its skills — see step 2 of
[Writing the pack](#writing-the-pack). It is `skills/guidance/` in the library
this skill came from, which groups packs under a category directory; that is a
default, not an assumption. A category directory is safe because the installer
walks each container up to three levels deep, but the pack's own directory name
must still equal its `name`, so keep the `guidance-` prefix on the directory
itself rather than folding it into the category.

No `log.md` — a pack's changelog is its git history. `SKILL.md` is the doorbell,
not the content: it carries the trigger and nothing that duplicates the bundle.

## Preflight

1. Read this skill's [guidance.template.md](assets/guidance.template.md) and
   [pack-skill.template.md](assets/pack-skill.template.md).
2. The attack table below is self-contained — you do not need any other skill's
   roster to run it. If a `guidance-*` pack surfaces on its own because this
   work touches its territory, consult it; you never enumerate packs, path to
   them, or hard-code one that may not be installed.
3. Establish the mode: **extract**, **author**, or **revise**. If the user
   hasn't said, ask once.

## Mode: extract

Generalize recurring decisions out of existing projects. The point of extraction
is **sharing** — getting hard-won reasoning out of one project's Arche and into a
form the next project can pick up — not validation by project count. One
well-reasoned project is enough to extract from; what makes the result guidance
rather than a testimonial is the conditioning work in step 4 and the attacks,
not a second data point. When more projects are available, use them — recurrence
across projects sharpens conditions — but never block on them.

1. Ask for the project path(s).
2. In each project, read `./.arche/concepts/` for pages typed `Architecture
   Decision Record` and `Solution Architecture Document`, plus any infra
   manifests the decisions reference.
3. Find techniques that recur **under different names** — across projects
   (project A's `adr-event-delivery` and project B's `adr-outbox` are one
   candidate, not two) or within one (a supersession trail, or the same move
   showing up in three ADRs, is recurrence too — and a supersession trail is
   prime material, because it carries real failure modes).
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
2. **Ask where the pack should live.** Extract mode runs inside *other people's*
   repos, so never assume a layout. If the project has a `skills/` directory at
   its root, propose `skills/guidance/guidance-<topic>/` when it already groups
   packs that way and `skills/guidance-<topic>/` when it is flat — match the
   neighbours rather than imposing a shape. Otherwise ask — some
   projects keep skills under `.claude/skills/`, `.agent/skills/`, or nowhere at
   all, in which case ask whether the pack belongs in this repo or in the user's
   own skills library. Call the answer `<pack-dir>` from here on.
3. Write `<pack-dir>/SKILL.md` from
   [pack-skill.template.md](assets/pack-skill.template.md), deleting the
   template's authoring-notes comment block. Then **confirm the frontmatter
   parses as YAML** before moving on. The one failure that actually happens:
   a colon followed by a space inside `description` — *"Outbox: deliver events
   atomically"* — which YAML reads as the start of a nested mapping key, making
   the whole skill unloadable. Keep the template's folded `>-` scalar, which is
   immune to it; if you have flattened `description` to a plain scalar for any
   reason, rephrase the colon away with an em dash. If
   [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)
   is available, `skills-ref validate <pack-dir>` checks this and the naming
   rules together.

   Then hold the `description` to its job: it is the pack's entire activation
   surface — the only text an agent sees when deciding whether to load the
   pack. Check three things before moving on: it covers *what* and *when* in
   the domain's literal vocabulary (pattern names double as trigger keywords);
   it includes the decision moment for a user who doesn't know the technique's
   name yet; and it contains no usage instructions — a sentence that would
   only help an agent that has already loaded the pack belongs in the body.
   Keep the folded value under the spec's 1024-character cap.

   **Stack-bound guidance declares its stack.** Some packs reason at a level
   any stack can use; others recommend named libraries in a named ecosystem.
   When the recommendations are stack-bound, say so in the `description`
   ("in React/TypeScript apps"; the library names double as trigger keywords)
   and carry the stack as an explicit **Applies when** condition on each page —
   an agent in another ecosystem should load the pack, keep the reasoning, and
   know exactly which parts to re-derive for its own stack. Keep the slug
   generic (`guidance-client-state`, not `guidance-react-client-state`) unless
   the technique's reasoning itself assumes the stack, or a sibling pack for
   another stack exists — the slug is namespace, and per-framework slugs
   proliferate; the description and conditions are where scope belongs.
4. Write each page to `<pack-dir>/bundle/concepts/<slug>.md` from
   [guidance.template.md](assets/guidance.template.md). Set `description:` — it
   is the index gloss. Write `generated: { by: write-guidance/<model-id>, at:
   <ISO 8601 UTC> }` with the model actually running. Never write `verified`.
5. Write `<pack-dir>/bundle/index.md`. Its frontmatter is exactly
   `okf_version: "0.2"` and nothing else — a bundle-root `index.md` is the one
   index that may carry frontmatter, and only that key (OKF §8). It is how a
   consumer knows which OKF version the pack targets, which a versioned,
   installable artifact owes its readers. Entries go
   `* [Title](concepts/<slug>.md) - description.`, gloss exactly the page's
   `description`.
6. **Verify conformance.** This is the pack's only mechanical gate, so run it
   whatever the host project is — by reading the files, which needs no tooling:
   - Every `.md` under `bundle/` except `index.md` starts with a `---` block
     that parses as a YAML mapping and carries a non-empty `type` (§11.1–11.2).
   - `bundle/index.md` carries no frontmatter key other than `okf_version` (§8).
   - Every markdown link is relative. Never `](/…` — a bundle is a
     subdirectory, not a site root.
   - No `verified:` anywhere; every `status:` is `draft`, `stable`, or
     `deprecated`.

   Inside the library this skill ships from, `devbox run check <pack-dir>/bundle`
   automates the first two (it implements §11 and §8 and nothing else); the link
   and vocabulary checks stay a read either way. That script is a `devbox.json`
   entry in that one repo — it does not exist in a user's project, so don't tell
   the user to run it unless you have seen it in their `devbox.json`.
7. **Index it only where the host repo indexes skills.** If the project keeps a
   catalog of its skills (a `README.md` list, a docs page), add the pack to it in
   the same shape as its neighbours. If it doesn't, skip this step — do not
   invent a catalog, and do not edit a `README.md` that isn't already a skill
   index. For host projects driven by agents that do not scan skill
   directories at all, the fallback is a one-line pointer to the pack in the
   project's agent context file (`AGENTS.md`, `CLAUDE.md`) — offer it, don't
   impose it.

A page whose reasoning is genuinely general but whose *type* isn't `Guidance` —
a roster, a taxonomy, a comparison table — is a `Concept` page in the same
bundle. Don't force the six sections onto content that isn't a technique.

## Discipline

- Extraction is for sharing, not validation. One project extracts fine; the
  conditioning work and the attacks are what separate guidance from testimony.
- Conditions must be checkable facts, not preferences.
- Stack-bound guidance declares its stack. Generic slug when the reasoning is
  stack-agnostic; the stack goes in the slug only when the technique itself
  assumes it.
- The description is the activation surface: what and when, in the domain's
  vocabulary — never how. Instructions live in the body.
- `Doesn't apply when` is a gate, not a section.
- Sanitize by default; ask before including any identifier.
- Never file a guidance page into a project's `./.arche/`.
- Never write `verified`.
- The host project's layout is the host project's. Ask where the pack lives;
  verify conformance by reading rather than by a script only this library has.

## Output

End with one line: `Guidance pack <slug> → <N> page(s) filed. Bundle conforms.`
