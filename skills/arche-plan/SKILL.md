---
name: arche-plan
description: Convergent implementation-planning skill for the Arche at ./.arche/. Turns an accepted feature spec into an executable, dependency-ordered plan — file/interface map, right-sized reviewable tasks, traceability to every requirement — grounded in the spec and its architecture (SAD/ADRs) via /arche-query and stored back as a `plan-<feature>` page under ./.arche/plans/. Runs an architect gap-check FIRST: if a spec behavior lacks a covering SAD/ADR or needs a load-bearing decision not yet recorded, it HALTS and routes to /arche-architect rather than planning around an undecided architecture. Produce-only — hands the plan to the team's dev methodology to execute; transient checkbox/execution state stays in the PR. Use when the user wants to turn a spec into a plan, says "plan this feature", "break the spec into tasks", or "implementation plan for X". NOT the WHAT/WHY (that's /arche-specify) and NOT the design/HOW (that's /arche-architect) — this sequences an already-decided design into buildable work.
---

# arche-plan

Run a convergent implementation-planning session that uses the project Arche as agent memory and writes its output back as a `plan-<feature>` page. The plan is the **durable execution blueprint** — how an accepted spec gets built, decomposed into dependency-ordered, independently reviewable tasks, with every task traced to a requirement and a filed architectural decision.

Position in the pipeline:

`/arche-discover` (business / market / domain ideation) → `/arche-specify` (feature WHAT/WHY) → `/arche-architect` (technical HOW: ARD / SAD / ADR) → **`/arche-plan` (executable HOW-sequence)** → your dev methodology executes.

This skill is decisive like `/arche-specify` and `/arche-architect`, not divergent like `/arche-discover`: it converges on one durable artifact with a self-review gate. It adapts the [superpowers writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) approach — assume the engineer has zero context for the codebase and questionable taste, so the plan must be exact — but grounds every choice in the Arche and stays methodology-agnostic in how it's executed.

## What goes in a plan (and what doesn't)

A plan is the **HOW-sequence** — it instantiates an already-decided design; it does not make new ones.

- **In (durable):** the goal, the architecture it instantiates (lifted from the SAD), file/interface map, dependency-ordered right-sized tasks with exact paths and exact steps, traceability from every spec FR/SC to a task, the architect gap-check verdict, a self-review gate.
- **Out:** new architectural decisions (a load-bearing choice surfacing here is a gap → route to `/arche-architect`), and the **transient execution state** — ticked checkboxes, debugging notes, commit-by-commit history. Those live in the PR / working tree, never in the Arche. The Arche stores the *plan of record*, not a live TODO tracker.

If the request is actually "decide the design" (what queue, what schema, sync vs async), that's `/arche-architect`. If it's "decide what to build / why," that's `/arche-specify`. This skill assumes both are settled and sequences the build.

> **Why a plan lives in the Arche at all.** The Arche's default rule is "plans don't belong here — they're transient." This skill applies the deliberate carve-out the SCHEMA now encodes: the *execution blueprint* (decomposition + architectural grounding + traceability) is durable institutional context — "how we decided to build this, traced to why" — while the *execution state* stays transient and external. Keep that line sharp; a plan page that accumulates checkbox state or debug logs has drifted into TODO-tracker territory and violates the carve-out.

## Interaction style

Convergent and recommendation-first, like its sibling skills. Where the decomposition has genuine forks (task boundaries, ordering, test seams), present a recommended cut with 1–2 alternatives and let the user redirect. Don't brainstorm the plan from zero — propose it, grounded in the spec and SAD, and refine.

If your runtime has a structured-question tool (e.g. Claude Code's `AskUserQuestion`), use it: recommendation first labeled `(Recommended)`, alternatives as the other options. Otherwise ask in prose, same shape.

## Preflight

1. Verify `./.arche/SCHEMA.md` exists. If not, tell the user to run `/arche-init` first and stop.
2. Read `./.arche/SCHEMA.md` end to end.
3. Check SCHEMA defines the **`plan` page type** (row pointing at `plans/<slug>.md`), the **`plan` log op**, and that `status:` / `superseded_by:` / `spec:` apply to plan pages. If any are missing, tell the user to run `/arche-init` in migration mode (it will detect the stale schema and propose patches) and stop.
4. Ensure `./.arche/plans/` exists. If not, create it with a `.gitkeep`.
5. Read `./.arche/index.md`.
6. Read this skill's [plan.template.md](assets/plan.template.md) so you write the page in the canonical layout.

## Phase 1: Session setup & grounding

1. **Identify the spec.** Ask the user which feature to plan, or take it from their request. The input to this skill is an **accepted `spec-<feature>` page**. If no spec exists for the feature, stop and recommend `/arche-specify` first — planning without a spec means inventing the WHAT, which isn't this skill's job. If a spec exists but is still `proposed`, flag it: planning against an unaccepted spec is a risk the user should accept explicitly.
2. **Load Arche context — via `/arche-query`.** Don't read pages ad hoc; invoke `/arche-query` to surface the grounding: the `spec-<feature>` page, the `sad-<system>` and `adr-*` pages for the system it touches, the `ard-<system>`, related entities, and any prior plan for the same feature. This is what "grounded in the Arche" means — the plan's tasks and constraints descend from filed requirements and decisions, not a cold read of the code.
3. **Sweep the codebase for ground truth.** The Arche says *what we decided*; the code says *what exists now*. Read the directories, manifests, and existing interfaces the plan will touch so file paths and consumed signatures are real, not guessed. The plan's "zero-context engineer" reader depends on these being exact.
4. **Present the grounding bundle** in one message: the spec (with FR/SC counts and status), the covering SAD/ADRs (with statuses), the ARD, related entities, prior plans, and the codebase surfaces in scope. One-line glosses. Ask: "Use this as the grounding, ignore part, or focus a subset?"
5. **Pick the slug.** Default `plan-<feature>`, reusing the spec's `<feature>` stem (e.g. `spec-bulk-export` → `plan-bulk-export`). If a plan for the feature already exists and this is a revision, plan to supersede it (Phase 4). Date stays in frontmatter.

## Phase 2: Architect gap-check (the gate)

**Run this before writing any tasks. It is a hard gate.** The user's intent: a plan must never silently make architectural decisions. Walk the spec's functional requirements and the work each implies, and for each ask: *is there a current SAD/ADR that covers this, or would building it force a load-bearing technical choice that isn't filed?*

A **gap** is any of:

- A spec behavior whose implementation has no covering decision in the SAD or an ADR (e.g. the spec needs durable retries but no consistency/idempotency ADR exists).
- A load-bearing choice the plan would otherwise have to invent — a one-way door, a new integration contract, a data-ownership boundary, a new external dependency — not recorded as an ADR.
- A contradiction between the spec and a current decision (the spec needs X; an accepted ADR forbids X).

Decision rule:

- **Gap found → HALT.** Do not write a plan around an undecided architecture. Report the specific gap(s) with the FR(s) that expose them, and recommend `/arche-architect` to file the missing ARD/SAD/ADR (or supersede the contradicting one). Offer to hand the gap list to that session. The plan resumes once the decision is filed.
- **No gap → proceed**, and **record the verdict** — the explicit "no new ARD/ADR required, every behavior maps to a filed decision" mapping goes into the plan's *Architect gap-check verdict* section. The verdict is part of the durable artifact: future readers see the architecture was checked, not assumed.

Borderline calls (is this a real load-bearing decision or just an implementation detail?) go to the user with a recommendation. Mechanical choices inside a settled design (variable names, file splits, which test runner the repo already uses) are **not** gaps — don't route trivia to the architect.

## Phase 3: Build the plan

Only once the gate passes. Converge the decomposition with the user, recommendation-first. Walk these branches (re-order to fit the feature):

- **Scope check.** If the spec spans independent subsystems that each produce independently testable software, recommend splitting into separate plans (one per subsystem) rather than one mega-plan. Name the split; plan the first.
- **File structure.** Map the files created/modified/tested before writing tasks. Prefer smaller, focused files over large ones that do too much. Ground paths in the codebase sweep.
- **Task decomposition.** A task is the smallest unit worth independent review and testing — split only where a reviewer could accept one task and reject its neighbor. Setup and docs fold into the task they serve. Order by dependency; each task independently testable.
- **Interfaces.** For each task, state what it **consumes** (exact signatures from earlier tasks or existing code) and **produces** (exact names/types later tasks rely on). Consistency is load-bearing: if Task 1 produces `clearLayers()`, Task 5 consumes `clearLayers()`, never `resetLayers()`.
- **Steps.** Default to the TDD ritual — write failing test → run to confirm failure → minimal implementation → run to confirm pass → commit — with **exact code and exact commands**, no placeholders. This step ritual is a **swappable default**: if the user's dev methodology prescribes different mechanics, follow that; the durable contract is the task boundaries + interfaces + traceability, not the specific ritual. There is **no hard dependency** on any particular execution skill.
- **Global constraints.** Pull project-wide requirements with exact values from the spec's success criteria and the ARD/SAD quality attributes ("p95 ≤ 200 ms (SC-2)", "all writes idempotent per adr-…"). Every task honors them.
- **Traceability.** Every spec FR and SC maps to at least one task; every task traces to at least one requirement. Build the mapping as you go — it's a Phase-4 gate item.

### Conversation discipline

- Recommend the cut; the user redirects. Don't make them decompose from scratch.
- **Explore the Arche or codebase instead of asking** when the answer is written down. Don't ask what an interface is when the code defines it.
- **Inline-cite** the spec FR/SC and the SAD/ADR each task descends from as you propose it.
- **No new architecture.** If a load-bearing decision surfaces mid-decomposition that Phase 2 missed, stop and route back to `/arche-architect` — don't quietly decide it in a task.
- **No Arche writes during planning.** All artifacts batch into Phase 4.

## Phase 4: Write the plan + self-review gate

Only when the user signals the decomposition is walked:

1. **Restate.** One message: the goal in a sentence, task count, the file map, the gap-check verdict, and the traceability summary (all FR/SC covered?). Get confirmation.
2. **Write the plan** at `.arche/plans/plan-<feature>.md` using [plan.template.md](assets/plan.template.md). Frontmatter: `type: plan`, today's date, tags, `spec:` (the originating spec page), `context_pages:` (the Arche pages `/arche-query` loaded), `sources:` (every Arche page cited inline — spec, SAD, ADRs, ARD, entities). Set `status: accepted` once the user approves the gate; use `proposed` to leave it a draft.
3. **Run the self-review gate** (the template's `## Self-review` checklist): gap-check passed, every FR/SC maps to a task, no placeholder language, every path exact, type/signature consistency across tasks, tasks right-sized, global constraints carry exact values. Fix inline; **bounded to 3 iterations** — if an item still fails, record it as an open question in the plan rather than looping. This is the hard approval gate: the user must accept before handoff.
4. **Back-link the spec.** Append a `## See also` line to the `spec-<feature>` page pointing at this plan, add the plan to the spec's `sources:`, and bump the spec's `updated:`. Forward-and-back navigation, like spec↔ARD. Do **not** rewrite the spec's body — the plan is downstream of it.
5. **Update `index.md`.** Add the plan under a `## Plans` section (create it if missing). One-line gloss + tags.
6. **Append to `log.md`** with op `plan`. List every page touched. Notes line: feature + task count + gap-check verdict (e.g. "no new ADR required").
7. **Hand off.** This skill is produce-only. Recommend the user's dev methodology execute the plan (subagent-driven or inline — e.g. superpowers `subagent-driven-development` / `executing-plans`, mattpocock, or their own). Remind them execution state stays in the PR, not the plan page. Suggest; do not auto-invoke or start building.

## Discipline

- Arche is read-only during planning. All writes batch into Phase 4.
- HOW-sequence only. The first *new* architectural decision in a plan is a defect — it means Phase 2's gate leaked; route it to `/arche-architect`.
- The architect gap-check is a **hard gate**, not advice. No plan ships around an undecided architecture.
- Ground in the Arche via `/arche-query`, not ad-hoc reads — and ground file paths / interfaces in the real codebase. A plan whose paths don't exist fails its zero-context reader.
- No placeholders. "TBD", "add appropriate error handling", "similar to Task N" are defects — every step carries executable content.
- Durable blueprint, transient state stays out. Checkbox ticking, debug notes, and commit history belong in the PR, never written back to the plan page.
- A plan can supersede an earlier plan for the same feature (spec revised, architecture changed). Mark the old one `status: superseded` with `superseded_by:` pointing at the replacement — never delete; the trail of how the build approach changed is institutional memory.
- If a plan task would contradict a current Arche decision, surface it in conversation and route to `/arche-architect`; don't encode the contradiction in a task.

## Output

End with one line — either the gate halt:

`Architect gap-check on <feature> found <N> gap(s): <list>. Halting — recommend /arche-architect to file the missing decision(s) before planning.`

or the filed plan:

`Plan on <feature> → plan-<feature> filed with <N> tasks, all <M> requirements traced, no new ARD/ADR required. Spec back-linked, index and log updated. Recommend your dev methodology execute next.`

## See also

- [plan.template.md](assets/plan.template.md) — the page skeleton this skill writes.
