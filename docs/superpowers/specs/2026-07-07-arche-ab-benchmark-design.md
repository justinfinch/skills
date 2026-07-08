# Arche A/B Benchmark — Design Spec

**Date:** 2026-07-07
**Status:** Approved design, pending implementation plan
**Author:** Justin Finch (with Claude)

## 1. Purpose

Validate empirically whether making the **Arche** (the `./.arche/` institutional-knowledge base produced by the `arche-*` skills) available to a coding agent improves its **output quality** and affects its **token efficiency**.

The Arche captures institutional context — business/domain rules, SME knowledge, ARB-style architectural decisions (ADRs), and research — that does not live in the code. The hypothesis is that an agent with this context makes better domain-correct decisions. The open tension is cost: the Arche *adds* input tokens (more to read), but may *save* tokens by preventing wrong turns and rework. This benchmark is designed to surface that tradeoff rather than assume it.

**Success = a trustworthy, reproducible directional answer** to: "On tasks that genuinely require institutional knowledge, does the Arche improve quality, and at what token cost?"

## 2. Method Overview

A two-arm A/B experiment. The independent variable is **"is the Arche present and discoverable?"**

- **Arm A (treatment):** fixture repo contains `./.arche/` *and* the `AGENTS.md`/`CLAUDE.md` registration block the `arche-init` skill writes (the pointer that makes an agent treat `.arche/` as first-class context). Treatment is **passive** — the agent discovers and reads the Arche naturally via the registration pointer; it is *not* required to actively invoke the `arche-query` skill. (An active-query third arm may be added later.)
- **Arm B (control):** byte-identical fixture with `./.arche/` removed and the registration block stripped from `AGENTS.md`. Task prompt, tests, tools, model, and seed are held constant.

Everything else is held constant across arms. The confound that Arm A receives more raw input tokens is **not** noise to eliminate — it is the tradeoff under measurement.

### Data flow

```
                    ┌─────────── seed phase (once) ───────────┐
  authored source →  arche-init + arche-ingest → ./.arche/ (genuine, skill-produced)
                    └──────────────────────────────────────────┘
                                     │
                 ┌───────────────────┴────────────────────┐
          bake into task fixture               strip for control
                 │                                         │
        ARM A: repo + .arche/ + AGENTS.md          ARM B: identical repo, no .arche/
                 │                                         │
                 └──────────── harbor run (Sonnet 5) ──────┘
                                     │
       ATIF trajectories on disk (per run: prompt/completion tokens, cost, transcript, final workspace)
                                     │
                    external analysis script (Python)
                       ├── read token/cost from each ATIF run
                       ├── LLM-judge each final workspace vs. rubric (blind to arm)
                       └── aggregate: 5 tasks × 5 trials × 2 arms
                                     │
                              report (tokens Δ, quality Δ, per-task table)
```

Harbor's only responsibility is **execution + emitting ATIF**. All comparison logic lives in an external analysis script.

## 3. Corpus — Seeding the Arche and Authoring Tasks

### Seeding (via the real skills)

To exercise the genuine pipeline while controlling which facts exist, author a small set of realistic raw source documents for **one coherent fictional domain: a subscription billing service** (rich, testable, full of non-obvious rules). Place them in `.arche/raw/`, then run `arche-ingest` in batch mode to produce a genuine, skill-built `.arche/`. Inputs are controlled; the artifact is real skill output. The seeded `.arche/` is committed for reproducibility.

### The 5 tasks

Each task is a coding/design problem whose correct answer depends on a fact recorded in the Arche that is **not inferable** from the code or general knowledge. Each hinges on a **different Arche page type**, so the benchmark tests breadth of value rather than one lucky case.

| # | Hinges on | Example task | Without the Arche, the agent… |
|---|---|---|---|
| 1 | **ADR** (decision against the obvious default) | "Add concurrency control to invoice updates" | reaches for row locks; the ADR chose optimistic concurrency for a stated reason |
| 2 | **Domain rule / entity** | "Implement proration on plan change" | guesses rounding/grace-period; finance rule says half-up, 14-day grace |
| 3 | **SME gotcha / landmine** | "Integrate the legacy payments API" | assumes dollars; SME note says the endpoint returns **cents** |
| 4 | **Superseded ADR** (`superseded_by`) | "Wire up event publishing" | uses the deprecated approach the Arche marks superseded |
| 5 | **Research / regulatory constraint** | "Add invoice deletion" | hard-deletes; research page requires 7-year audit retention |

Each task ships a prompt plus a hidden ground-truth **key fact**, used only by the judge and never shown to the agent. Tasks 1, 3, and 5 give the strongest signal — the Arche fact directly contradicts what a capable model would otherwise assume.

## 4. Metrics & Judging

### Token axis (objective, from ATIF per run)

`prompt_tokens`, `completion_tokens`, `total_tokens`, `cost_usd`, and **step/tool-call count** (proxy for wrong-turns/rework). Reported per run, then averaged per cell.

### Quality axis (LLM-judge, blind)

An independent, **stronger judge model (Opus 4.8)** scores each final workspace. The judge is **blind to arm** — it sees only the task prompt, the agent's final output/diff, and the ground-truth key fact; it never learns whether the Arche was present.

Rubric, 0–3 per dimension:

- **Arche-fact adherence** — did it honor the recorded decision/rule? *(primary dimension)*
- **Domain justification** — reasoned from the domain vs. guessed a default?
- **Task completion** — does it actually work, independent of the fact?

The judge emits structured JSON (scores + rationale) so every verdict is auditable. To control judge variance, judge at low temperature and retain rationale; if a task's judge scores look noisy in the smoke/pilot phase, escalate to 3 judge passes and take the median.

### Headline metrics computed by the report

- Raw quality Δ (Arm A − Arm B), per task and pooled
- Raw token Δ (Arm A expected higher on input)
- **Quality per 1k total tokens** — the efficiency-adjusted view that resolves the core tension
- Rework proxy: step-count Δ

## 5. Analysis & Decision Rules

### Aggregation

Mean quality, mean total tokens, mean step-count per cell (5 trials), broken out per task and pooled, reported as mean ± spread. At n=5 this is **directional, not statistically significant** — stated plainly, not overclaimed.

### Validity gate (non-negotiable)

Before trusting any comparison, confirm that **Arm B largely *fails* fact-adherence**. If the control honors the key fact *without* the Arche, that task never required institutional knowledge — it is invalid and is dropped or redesigned. This gate is what makes the benchmark trustworthy.

### Reading the outcome

1. **Quality ↑, tokens ~flat/↓** → clean win; the Arche improves output *and* pays for itself.
2. **Quality ↑, tokens ↑** → the expected, interesting case. Verdict rests on **quality-per-1k-tokens** and whether the quality gain justifies the marginal input cost.
3. **Quality ~flat, tokens ↑** → the Arche is not earning its keep here — *provided the validity gate passed*. If it did not, the tasks were the problem, not the Arche.

**Per-task breakdown outranks the pooled average** at this scale; expect some page types (ADR, SME gotcha) to help more than others, and treat that texture as a finding.

### Output

A markdown report plus a results table; later a quality-vs-tokens scatter (arms colored) via the `dataviz` skill.

## 6. Execution, Cost & Operational Setup

### Executor decision

**Harbor + `ANTHROPIC_API_KEY`**, run locally on Docker. Rationale: full container isolation, ATIF token metrics, and leaderboard-comparable task format. This bills the API at pay-as-you-go rates (no subscription pricing).

- Investigated alternative — using the existing Claude Code subscription: Harbor runs the agent inside a throwaway Docker container that does not inherit the host `~/.claude` OAuth login, and Harbor exposes no supported subscription path. Mounting OAuth creds into the container is fragile/unsupported. Using the subscription would require moving the executor off Harbor to a host-based `claude -p` harness. **Decision: keep Harbor + API key.** The design's arms/metrics/judge/analysis are executor-agnostic, so a host-based executor remains a possible future swap.

### Prerequisites & gaps

- Docker — installed and running ✓
- `uv` + `harbor` — **not installed** (`uv tool install harbor`, or `pip install harbor`)
- `ANTHROPIC_API_KEY` — **not set**; must be provided. Bills real money.
- Run **locally on Docker** (free compute); avoid Daytona (paid cloud env) — only tokens cost money.

### Cost control — two mandatory gates before the 50-run spend

Agentic runs regrow context every turn, so per-run token cost is unpredictable up front (~50k to ~500k tokens each). Spend is gated in steps:

1. **Oracle verify:** `harbor run … -a oracle` — sanity-check task wiring at $0 model cost.
2. **Smoke run:** 1 task × 1 trial × 2 arms (+1 judge pass). Confirms harness, token capture, and judge all work, and yields a *real* measured cost-per-run.
3. **Extrapolate → confirm → launch:** multiply to the full 50, present the projected dollar figure for explicit sign-off, then run the matrix. No open-ended spend.

### Run flow

```
seed:    author raw docs → arche-ingest → commit .arche/
build:   generate arm-A and arm-B fixtures (A = repo+.arche+AGENTS.md; B = stripped)
verify:  harbor run … -a oracle                                   # $0 model cost
smoke:   harbor run … -a claude-code -m anthropic/claude-sonnet-5 -n 1   # measure cost
matrix:  harbor run … -n 5  (arm A, then arm B)                   # after cost sign-off
analyze: python analysis/aggregate.py → report.md
```

Everything is committed and version-pinned (model IDs, seed docs, fixtures) so the run reproduces.

## 7. Scope & Non-Goals

**In scope:** the seed fixture, 5 tasks, the two-arm Harbor run at 5 trials on Sonnet 5, the external analysis + judge, and a report.

**Out of scope (YAGNI for the first run):**
- Statistical significance testing (n=5 is directional only)
- An active `arche-query` third arm
- Multiple agent models (Sonnet 5 only)
- Leaderboard submission
- CI automation of the benchmark

## 8. Key Parameters (locked)

| Parameter | Value |
|---|---|
| Corpus | Seeded via `arche-init` + `arche-ingest` on authored raw docs (subscription-billing domain) |
| Quality metric | Blind LLM-judge rubric (Opus 4.8), 3 dimensions × 0–3 |
| Scale | 5 tasks × 5 trials × 2 arms = 50 agent runs |
| Agent model | Sonnet 5 |
| Judge model | Opus 4.8 |
| Treatment | Passive (Arche auto-discovered via AGENTS.md pointer) |
| Executor | Harbor + `ANTHROPIC_API_KEY`, local Docker |
| Analysis | External Python script reading ATIF |
| Validity gate | Arm B must largely fail fact-adherence |
