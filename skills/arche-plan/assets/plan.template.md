---
type: plan
title: Plan — {{FEATURE}}
created: {{DATE}}
updated: {{DATE}}
tags: [plan]
status: proposed
spec: ../specs/spec-{{FEATURE}}.md
sources: []
context_pages: []
---

# Plan — {{FEATURE}}

> **Execution blueprint, not execution state.** This page is the durable, dependency-ordered decomposition of how the feature gets built — grounded in its spec and architecture. The *transient* state of building it (ticked checkboxes, debug notes, commit-by-commit history) lives in the PR / working tree, **not** here. Re-render this plan if the spec or architecture it cites changes.
>
> **For the executing methodology:** the durable contract below is the **task decomposition + file/interface map + traceability**. The per-step ritual (the `- [ ]` steps) defaults to TDD but is **swappable** — if your dev methodology (superpowers subagent-driven-development, mattpocock, your own) prescribes different step mechanics, follow that; keep the task boundaries and interfaces intact.

**Goal:** {{One sentence — what the user can do when this is shipped.}}

**Architecture:** {{2–3 sentences, lifted from the SAD — the shape of the solution this plan instantiates.}} (see [SAD — {{system}}](../concepts/sad-{{system}}.md))

**Tech stack:** {{Key technologies — from the SAD / ADRs, not invented here.}}

## Arche grounding

What this plan descends from. Every load-bearing choice traces to a filed decision — this plan **sequences** an already-decided design, it does not make new architectural calls.

- **Spec:** [Spec — {{FEATURE}}](../specs/spec-{{FEATURE}}.md) — the WHAT/WHY this plan builds.
- **Architecture:** [SAD — {{system}}](../concepts/sad-{{system}}.md), [ADR — {{decision}}](../concepts/adr-{{decision}}.md) — the HOW this plan instantiates.
- **Other context:** {{entities / prior research / constraints surfaced via /arche-query}}.

### Architect gap-check verdict

Run before any tasks were written. Outcome: **no new ARD/ADR required** — every behavior below is covered by a current decision above. (If a gap had been found, this plan would not exist: the session would have halted and routed to `/arche-architect`.)

- {{FR / behavior}} → covered by [{{ADR/SAD}}](../concepts/adr-{{decision}}.md).
- {{…}}

## Global constraints

Project-wide requirements every task must honor — exact values, drawn from the spec's success criteria and the ARD/SAD quality attributes. No vague "be fast" — state the number.

- {{Constraint — e.g. "p95 latency ≤ 200 ms (SC-2)"}}.
- {{Constraint — e.g. "all writes idempotent per adr-idempotent-ingest"}}.

## File structure

Files this plan creates or modifies, decided up front. Prefer smaller, focused files over large ones that do too much.

- Create: `exact/path/to/new.ext` — {{purpose}}.
- Modify: `exact/path/to/existing.ext:line-range` — {{change}}.
- Test: `exact/path/to/test.ext` — {{what it covers}}.

## Tasks

A **task** is the smallest unit worth independent review and testing — split only where a reviewer could reject one task while approving its neighbors. Setup and docs fold into the task they serve. Tasks are dependency-ordered; each is independently testable.

### Task 1: {{Component name}}

**Files:**
- Create: `exact/path/to/file.ext`
- Modify: `exact/path/to/existing.ext:line-range`
- Test: `tests/exact/path/to/test.ext`

**Interfaces:**
- Consumes: {{what this task uses — exact signatures / names from earlier tasks or existing code}}.
- Produces: {{what later tasks rely on — exact names/types; later tasks must use these verbatim}}.

**Traces:** FR-{{n}}, SC-{{n}} (from the spec).

Steps (default TDD ritual — swap per your dev methodology, keep the boundaries):

- [ ] **Write the failing test** — {{exact test code, no placeholder}}.
- [ ] **Run the test, verify it fails** — `{{exact command}}` → expect {{failure}}.
- [ ] **Write the minimal implementation** — {{exact code}}.
- [ ] **Run the test, verify it passes** — `{{exact command}}` → expect pass.
- [ ] **Commit** — `{{exact git command}}`.

### Task 2: {{…}}

{{Repeat. Type names, method signatures, and properties must be consistent across tasks — if Task 1 produces `clearLayers()`, Task 2 consumes `clearLayers()`, not `resetLayers()`.}}

## Traceability

Every spec requirement maps to at least one task; every task traces to at least one requirement. No orphans either direction.

| Requirement | Task(s) |
| :---------- | :------ |
| FR-1 | Task 1 |
| SC-1 | Task 1, Task 3 |

## Self-review

Run before the plan is accepted (max 3 fix iterations). Every box checked, or the gap recorded as an open question above.

- [ ] Architect gap-check passed — no behavior needs a new/unrecorded ARD/ADR.
- [ ] Every spec FR and SC maps to a task (traceability table complete).
- [ ] No placeholder language — no "TBD", "add error handling", "similar to Task N"; every step has real, executable content.
- [ ] Every file path is exact and complete.
- [ ] Type names / method signatures / properties are consistent across tasks.
- [ ] Tasks are right-sized — each is independently reviewable and testable.
- [ ] Global constraints carry exact values, traced to spec SC / ARD quality attributes.

## Execution handoff

This plan is **produce-only** — the Arche does not execute it. Hand off to your dev methodology to build:

- **Subagent-driven** (recommended for agentic execution) — dispatch a fresh worker per task with inter-task review (e.g. superpowers `subagent-driven-development`).
- **Inline** — execute in the current session with checkpoint reviews (e.g. superpowers `executing-plans`).

Ticked checkboxes, debug notes, and commit history stay in the PR / working tree, **not** in this page.

## See also

- [Spec — {{FEATURE}}](../specs/spec-{{FEATURE}}.md) — the requirements this plan builds.
- [SAD — {{system}}](../concepts/sad-{{system}}.md) — the architecture this plan instantiates.
