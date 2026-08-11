# Arche A/B Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible two-arm A/B benchmark that measures whether making the `./.arche/` institutional-knowledge base available to a coding agent improves output quality and at what token cost.

**Architecture:** A seed phase produces a genuine, skill-built `.arche/` for a fictional subscription-billing domain, baked into a small base fixture repo. A Python build script materializes 5 coding tasks × 2 arms (A = repo + `.arche/` + `AGENTS.md` registration; B = identical repo, stripped) as local Harbor task directories. Harbor runs the agent (Sonnet 5) locally on Docker and emits ATIF trajectories. An external Python analysis pipeline reads token/cost from each ATIF file, LLM-judges each final workspace diff blind-to-arm (Opus 4.8), applies a validity gate, and renders a markdown report. Harbor only executes and emits ATIF; all comparison logic is external.

**Tech Stack:** Python 3.11, [Harbor](https://github.com/harbor-framework/harbor) (`uv tool install harbor`), Docker, the Anthropic Python SDK (`anthropic`), `pytest`. The `arche-init` and `arche-ingest` skills seed the corpus.

## Global Constraints

Copy these exact values into every task that references them:

- **Agent model (Harbor `-m`):** `anthropic/claude-sonnet-5`
- **Judge model (Anthropic SDK):** `claude-opus-4-8`
- **Judge sampling:** `claude-opus-4-8` **rejects `temperature`/`top_p`/`top_k` with a 400** — do NOT pass them. Control judge variance with `thinking={"type": "disabled"}` plus **median of 3 passes** (the spec's "low temperature" resolves to this on Opus 4.8). Use `client.messages.parse()` with a Pydantic schema for structured JSON.
- **Harbor task selection flag:** `-p <path>` (local dataset = a folder of task dirs).
- **Harbor trials-per-task flag:** `-k` / `--n-attempts` (NOT `-n`, which is concurrency).
- **Harbor agent names:** `claude-code` (real runs), `oracle` (`$0` wiring check, runs `solution/solve.sh`).
- **Anthropic key in container:** env var `ANTHROPIC_API_KEY` (Harbor reads it from `os.environ`, or pass `--ae ANTHROPIC_API_KEY=...`).
- **Harbor output layout:** `jobs/<job-name>/<trial-name>/agent/trajectory.json` (ATIF-v1.7) + `jobs/<job-name>/<trial-name>/verifier/` (persisted files written by `tests/test.sh`).
- **ATIF token fields:** per-step `metrics.{prompt_tokens,completion_tokens,cached_tokens,cost_usd}`; trajectory-level `final_metrics.{total_prompt_tokens,total_completion_tokens,total_cached_tokens,total_cost_usd,total_steps}`. **There is no `total_tokens` field — derive it** as `total_prompt_tokens + total_completion_tokens`. Tool-call count = `sum(len(step.tool_calls))`.
- **Reward contract:** `tests/test.sh` runs from `/tests`, must write `/logs/verifier/reward.txt` (a `1`/`0`).
- **Verifier environment is shared** with the agent workspace by default (`[verifier].environment_mode = "shared"`), so `tests/test.sh` can read `/workspace` and capture the agent's diff.
- **Scale:** 5 tasks × 5 trials × 2 arms = 50 agent runs. n=5 is directional, not statistically significant — state this in the report.
- **All artifacts committed and version-pinned** so the run reproduces.
- **Spend is gated:** oracle ($0) → smoke (1×1×2, measure real cost) → explicit dollar sign-off → full matrix. No open-ended spend.

## File Structure

Everything lives under `benchmark/` at the repo root.

```
benchmark/
  README.md                         # how to run the benchmark end to end
  pyproject.toml                    # deps: anthropic, pytest (analysis + build tooling)
  fixture-base/                     # COMMITTED base fixture (Arm-A payload source)
    billing/                        #   the subscription-billing service (task targets)
      __init__.py
      invoices.py                   #   update_invoice (task 1), delete_invoice (task 5)
      proration.py                  #   prorate_plan_change (task 2)
      payments.py                   #   record_payment (task 3)
      events.py                     #   publish_invoice_paid (task 4)
    README.md                       #   fixture repo readme (no key facts)
    AGENTS.md                       #   arche-init registration block (arm A only)
    .arche/                         #   seeded by arche-init + arche-ingest (committed)
      raw/ sources/ concepts/ entities/ SCHEMA.md index.md log.md ...
  seed/
    raw/                            # authored raw source docs (input to arche-ingest)
      adr-002-invoice-concurrency.md
      finance-proration-policy.md
      sme-legacy-payments-notes.md
      adr-004-event-publishing.md
      adr-007-transactional-outbox.md
      regulatory-retention-research.md
  tasks/                            # the 5 arm-agnostic task overlays (source of truth)
    task-1-concurrency/
      instruction.md                #   shown to the agent (never reveals the fact)
      task.toml
      solution/solve.sh             #   oracle reference implementation
      tests/test.sh                 #   structural gate + diff/task-id capture
      key_fact.md                   #   hidden ground truth — JUDGE ONLY, never baked
    task-2-proration/ ...
    task-3-payments/ ...
    task-4-events/ ...
    task-5-retention/ ...
  build_fixtures.py                 # tasks/ + fixture-base -> fixtures/arm-{a,b}/
  analysis/
    __init__.py
    parse_trajectory.py             # ATIF file -> token/cost/step metrics
    judge.py                        # Opus 4.8 blind rubric judge (median of 3)
    collect_runs.py                 # walk a Harbor jobs/<job> dir -> run records
    aggregate.py                    # per-cell means, validity gate, headline metrics
    report.py                       # aggregated data -> markdown report
    run_analysis.py                 # collect -> judge -> aggregate -> report
  tests/                            # pytest for build + analysis tooling
    fixtures/
      trajectory_sample.json        # golden ATIF file for parse_trajectory tests
    test_build_fixtures.py
    test_parse_trajectory.py
    test_judge.py
    test_collect_runs.py
    test_aggregate.py
    test_report.py
  fixtures/                         # GENERATED by build_fixtures.py (gitignored)
    arm-a/task-1-concurrency/ ...   #   full Harbor task dirs, .arche + AGENTS.md baked
    arm-b/task-1-concurrency/ ...   #   identical minus .arche + AGENTS.md block
  jobs/                             # GENERATED by Harbor (gitignored)
  report/
    report.md                       # GENERATED final report
    judgments.json                  # GENERATED judge cache (avoids re-spend on re-run)
```

**Decomposition notes.** `fixture-base/` (including the seeded `.arche/`) and `tasks/` are committed source. `build_fixtures.py` is a pure function from those into `fixtures/`. The analysis modules each have one responsibility and are unit-testable without Docker or the API (the judge is tested with a mocked client). `run_analysis.py` is the only module that talks to both the filesystem `jobs/` output and the live API.

---

### Task 0: Scaffold the benchmark project and toolchain

**Files:**
- Create: `benchmark/pyproject.toml`
- Create: `benchmark/README.md`
- Create: `benchmark/analysis/__init__.py` (empty)
- Modify: `.gitignore` (repo root) — append benchmark generated dirs

**Interfaces:**
- Produces: a Python env with `anthropic` and `pytest` importable; `harbor` on PATH; `benchmark/` package skeleton that later tasks fill in.

- [ ] **Step 1: Create `benchmark/pyproject.toml`**

```toml
[project]
name = "arche-ab-benchmark"
version = "0.1.0"
description = "Two-arm A/B benchmark for the Arche institutional-knowledge base"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.69",
]

[project.optional-dependencies]
dev = ["pytest>=8"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create `benchmark/README.md`**

```markdown
# Arche A/B Benchmark

Measures whether an `./.arche/` institutional-knowledge base improves a coding
agent's output quality, and at what token cost. See the design spec at
`docs/superpowers/specs/2026-07-07-arche-ab-benchmark-design.md`.

## Run order

```
# one-time: seed the Arche (already committed under fixture-base/.arche/)
python build_fixtures.py                                            # -> fixtures/arm-{a,b}/
harbor run -p fixtures/arm-a -a oracle --job-name oracle-arm-a      # $0 wiring check
harbor run -p fixtures/arm-b -a oracle --job-name oracle-arm-b      # $0 wiring check
# smoke (measure real cost) then full matrix — see the plan for exact commands
python analysis/run_analysis.py                                     # -> report/report.md
```

## Prerequisites
- Docker running.
- `uv tool install harbor` (or `pip install harbor`).
- `export ANTHROPIC_API_KEY=...` (bills real money on non-oracle runs).
```

- [ ] **Step 3: Create `benchmark/analysis/__init__.py`** (empty file)

- [ ] **Step 4: Append generated dirs to the repo-root `.gitignore`**

```
# Arche A/B benchmark generated artifacts
benchmark/fixtures/
benchmark/jobs/
benchmark/report/report.md
benchmark/report/judgments.json
benchmark/.venv/
```

- [ ] **Step 5: Install the toolchain and verify**

Run:
```bash
uv tool install harbor || pip install harbor
harbor --version
harbor run --help | grep -E -- "--n-attempts|--path|--agent" | head
python -m venv benchmark/.venv && benchmark/.venv/bin/pip install -e "benchmark[dev]"
benchmark/.venv/bin/python -c "import anthropic, pytest; print('deps ok')"
```
Expected: `harbor --version` prints a version; the `grep` shows the `--path`, `--agent`, and `--n-attempts` flags exist; `deps ok` prints. If `harbor run --help` does not show `--n-attempts`, STOP and reconcile flag names against `harbor run --help` before continuing (the plan assumes `-k/--n-attempts` for trials and `-p/--path` for a local dataset).

- [ ] **Step 6: Commit**

```bash
git add benchmark/pyproject.toml benchmark/README.md benchmark/analysis/__init__.py .gitignore
git commit -m "chore(benchmark): scaffold arche-ab benchmark project and toolchain"
```

---

### Task 1: Author the base fixture billing service

**Files:**
- Create: `benchmark/fixture-base/billing/__init__.py`
- Create: `benchmark/fixture-base/billing/invoices.py`
- Create: `benchmark/fixture-base/billing/proration.py`
- Create: `benchmark/fixture-base/billing/payments.py`
- Create: `benchmark/fixture-base/billing/events.py`
- Create: `benchmark/fixture-base/README.md`

**Interfaces:**
- Produces: five importable stub modules whose target functions raise `NotImplementedError` (or carry a TODO). Each task's `tests/test.sh` imports its module, and each `solution/solve.sh` overwrites one file. The stubs must contain **no hint of the hidden key fact** — the point is that a capable model without the Arche guesses the default.

- [ ] **Step 1: Create `benchmark/fixture-base/billing/__init__.py`**

```python
"""A small subscription-billing service (benchmark fixture)."""
```

- [ ] **Step 2: Create `benchmark/fixture-base/billing/invoices.py`**

```python
"""Invoice operations for the subscription billing service."""

from dataclasses import dataclass


@dataclass
class Invoice:
    id: str
    customer_id: str
    amount_cents: int
    version: int = 0
    deleted_at: str | None = None


def update_invoice(store, invoice_id, **changes):
    """Apply `changes` to the invoice identified by `invoice_id`.

    `store` is a key-value store exposing `get(id) -> Invoice` and `put(invoice)`.
    TODO: this has no concurrency control — two simultaneous updates clobber each other.
    """
    invoice = store.get(invoice_id)
    for key, value in changes.items():
        setattr(invoice, key, value)
    store.put(invoice)
    return invoice


def delete_invoice(store, invoice_id):
    """Delete the invoice identified by `invoice_id`.

    TODO: implement deletion.
    """
    raise NotImplementedError
```

- [ ] **Step 3: Create `benchmark/fixture-base/billing/proration.py`**

```python
"""Proration for mid-cycle plan changes."""


def prorate_plan_change(
    old_cents: int,
    new_cents: int,
    days_used: int,
    days_in_cycle: int,
    days_since_last_change: int,
) -> int:
    """Return the billing adjustment, in integer cents, for a mid-cycle plan change.

    TODO: implement proration.
    """
    raise NotImplementedError
```

- [ ] **Step 4: Create `benchmark/fixture-base/billing/payments.py`**

```python
"""Integration with the legacy payments gateway."""


class PaymentsGatewayClient:
    """Thin client for the legacy payments gateway (provided at runtime)."""

    def charge(self, customer_id: str, amount: int) -> dict:
        """Charge the customer and return the gateway's response dict."""
        raise NotImplementedError


def record_payment(invoice, gateway_response: dict) -> None:
    """Record the result of a gateway charge on `invoice`.

    `invoice` has an integer `amount_cents` field.
    TODO: store the charged amount on the invoice.
    """
    raise NotImplementedError
```

- [ ] **Step 5: Create `benchmark/fixture-base/billing/events.py`**

```python
"""Domain event publishing."""


def publish_invoice_paid(conn, invoice_id: str) -> None:
    """Publish an 'invoice paid' domain event for `invoice_id`.

    `conn` is an open database connection/transaction.
    TODO: wire up event publishing.
    """
    raise NotImplementedError
```

- [ ] **Step 6: Create `benchmark/fixture-base/README.md`**

```markdown
# Billing service (benchmark fixture)

A minimal subscription-billing service used as the working repo for the Arche
A/B benchmark. Each task asks you to implement or fix one function under
`billing/`.
```

- [ ] **Step 7: Verify the stubs import**

Run:
```bash
cd benchmark/fixture-base && python -c "import billing.invoices, billing.proration, billing.payments, billing.events; print('import ok')"
```
Expected: `import ok`.

- [ ] **Step 8: Commit**

```bash
git add benchmark/fixture-base/billing benchmark/fixture-base/README.md
git commit -m "feat(benchmark): add base billing-service fixture with task stubs"
```

---

### Task 2: Author the raw source documents encoding the 5 key facts

**Files:**
- Create: `benchmark/seed/raw/adr-002-invoice-concurrency.md`
- Create: `benchmark/seed/raw/finance-proration-policy.md`
- Create: `benchmark/seed/raw/sme-legacy-payments-notes.md`
- Create: `benchmark/seed/raw/adr-004-event-publishing.md`
- Create: `benchmark/seed/raw/adr-007-transactional-outbox.md`
- Create: `benchmark/seed/raw/regulatory-retention-research.md`

**Interfaces:**
- Produces: raw documents that, when ingested by `arche-ingest`, create Arche pages of five distinct types (ADR, domain rule, SME source note, superseded ADR pair, research page). Each raw doc must state its key fact plainly enough that ingest records it, and must be non-inferable from the code. These are the *inputs* to the real skill pipeline in Task 3.

- [ ] **Step 1: Create `adr-002-invoice-concurrency.md`** (ADR page type — task 1)

```markdown
# ADR-002: Invoice updates use optimistic concurrency

Status: accepted
Date: 2025-11-03

## Context
Invoice writes fan out to external webhook deliveries while the write is in flight.

## Decision
Invoice updates use **optimistic concurrency**: read the invoice's integer
`version`, and on write persist only if the stored version still equals the one
read, then increment `version` (compare-and-set). A conflicting write raises a
stale-version error rather than overwriting.

## Alternatives rejected
Pessimistic row locks (`SELECT ... FOR UPDATE`) were explicitly rejected: holding
a row lock across the webhook fan-out caused deadlocks in the legacy system.
```

- [ ] **Step 2: Create `finance-proration-policy.md`** (domain rule — task 2)

```markdown
# Finance policy: proration on plan change

Owner: Finance. Effective: 2025-09-01.

When a customer changes plan mid-cycle we prorate by exact days used. Two rules
are load-bearing and non-obvious:

1. **Rounding is HALF-UP to the whole cent** — not banker's/half-even rounding,
   not truncation. (Auditors flagged half-even as inconsistent with our tax
   filings.)
2. **14-day grace window.** If the plan was changed within the last 14 days
   (`days_since_last_change < 14`), the new change is NOT re-prorated: the
   adjustment is 0. This prevents plan-flip abuse.
```

- [ ] **Step 3: Create `sme-legacy-payments-notes.md`** (SME source note — task 3)

```markdown
# SME interview: legacy payments gateway (2025-10-14)

Notes from the payments SME on `PaymentsGatewayClient.charge()`:

- **The returned `amount` is in integer CENTS, not dollars.** This has bitten us
  repeatedly — code that treats the return value as dollars overcharges/undercharges
  by 100x. The invoice's `amount_cents` field expects cents, so store the gateway's
  `amount` value as-is.
- The `currency` field is always uppercase ISO-4217.
```

- [ ] **Step 4: Create `adr-004-event-publishing.md`** (superseded ADR — task 4)

```markdown
# ADR-004: Publish domain events via a dedicated events table

Status: superseded_by ADR-007
Date: 2025-06-20

## Decision (SUPERSEDED)
Domain events were published by writing directly to an `events` table and
dual-writing to the message broker after commit.

## Why superseded
Dual-writes lost events when the broker write failed after the DB commit.
Replaced by the transactional outbox pattern — see ADR-007.
```

- [ ] **Step 5: Create `adr-007-transactional-outbox.md`** (superseding ADR — task 4)

```markdown
# ADR-007: Publish domain events via a transactional outbox

Status: accepted
Date: 2025-08-11
Supersedes: ADR-004

## Decision
New event publishing MUST use the **transactional outbox** pattern: inside the
same database transaction as the state change, insert a row into the `outbox`
table. A separate relay process reads `outbox` and publishes to the broker.
Do NOT write directly to an `events` table or dual-write to the broker.
```

- [ ] **Step 6: Create `regulatory-retention-research.md`** (research page — task 5)

```markdown
# Compliance research: invoice retention

Date: 2025-07-30. Source: outside counsel memo.

Invoices are financial records subject to a **7-year audit-retention**
requirement (SOX and tax regulation). Consequences for engineering:

- Invoices must **never be hard-deleted**.
- "Deleting" an invoice is a **soft delete**: set `deleted_at` to the current
  timestamp and exclude soft-deleted invoices from normal queries. The row is
  retained for 7 years.
```

- [ ] **Step 7: Verify each key fact is present exactly where expected**

Run:
```bash
cd benchmark/seed/raw
grep -l "optimistic concurrency" adr-002-invoice-concurrency.md
grep -l "HALF-UP" finance-proration-policy.md
grep -l "integer CENTS" sme-legacy-payments-notes.md
grep -l "transactional outbox" adr-007-transactional-outbox.md
grep -l "superseded_by ADR-007" adr-004-event-publishing.md
grep -l "7-year audit-retention" regulatory-retention-research.md
```
Expected: each `grep -l` prints its filename (fact present). If any prints nothing, fix the doc.

- [ ] **Step 8: Commit**

```bash
git add benchmark/seed/raw
git commit -m "feat(benchmark): author raw source docs for the 5 Arche key facts"
```

---

### Task 3: Seed the Arche with the real skills and commit it

**Files:**
- Create (via skills): `benchmark/fixture-base/.arche/` (SCHEMA.md, index.md, log.md, subdirs, and skill-produced pages)
- Create/Modify (via skills): `benchmark/fixture-base/AGENTS.md` (arche-init registration block, marker `<!-- arche-context-source -->`)
- Modify: `benchmark/fixture-base/.arche/raw/` (arche-ingest snapshots the seed docs here)

**Interfaces:**
- Consumes: `benchmark/seed/raw/*.md` from Task 2.
- Produces: a genuine, skill-built, committed `.arche/` plus an `AGENTS.md` carrying the arche registration block. This is the Arm-A payload. It is *not scripted* — the skills write the pages — so the acceptance check is that every key fact is discoverable in the committed Arche, not an exact page layout.

> This task runs the real `arche-init` and `arche-ingest` skills interactively; it is semi-manual by design (the design spec requires exercising the genuine pipeline). The steps below are the operator checklist. Do not hand-write Arche pages.

- [ ] **Step 1: Stage the raw docs into the fixture's Arche drop zone**

Run:
```bash
cd benchmark/fixture-base
# (arche-init creates .arche/ with a raw/ drop zone; copy the seed docs in for batch ingest)
```
Then run `/arche-init` from `benchmark/fixture-base/` so `.arche/` and the `AGENTS.md` registration block are created **in that directory** (the Arche must live inside the fixture so it can be baked into Arm A). Confirm `AGENTS.md` gains the `<!-- arche-context-source -->` block and a `CLAUDE.md` bridge is created if the skill adds one.

- [ ] **Step 2: Copy the seed docs into `.arche/raw/` and batch-ingest**

Run:
```bash
cp benchmark/seed/raw/*.md benchmark/fixture-base/.arche/raw/
```
Then run `/arche-ingest` (no argument → batch mode) from `benchmark/fixture-base/`, accepting all six raw files. Let the skill write the source/concept/entity pages and update `index.md` / `log.md`. Expect an ADR concept page for optimistic concurrency, a proration domain-rule concept/entity, an SME source note for the cents gotcha, an ADR-004 page marked `superseded_by` ADR-007 plus the ADR-007 page, and a research page for retention.

- [ ] **Step 3: Verify every key fact is discoverable in the committed Arche**

Run:
```bash
cd benchmark/fixture-base
grep -rq "optimistic concurrency" .arche/ && echo "fact1 ok"
grep -rqi "half-up" .arche/ && echo "fact2 ok"
grep -rqi "cents" .arche/ && echo "fact3 ok"
grep -rqi "outbox" .arche/ && echo "fact4 ok"
grep -rq "superseded_by" .arche/ && echo "fact5-supersession ok"
grep -rq "7-year" .arche/ && echo "fact5-retention ok"
grep -q "arche-context-source" AGENTS.md && echo "registration ok"
```
Expected: all seven `ok` lines print. If a fact is missing, re-run `/arche-ingest` on the relevant raw file or fix the raw doc and re-ingest.

- [ ] **Step 4: Commit the seeded Arche as the reproducible Arm-A payload**

```bash
git add benchmark/fixture-base/.arche benchmark/fixture-base/AGENTS.md
# also add CLAUDE.md if arche-init created a bridge inside fixture-base/
git add benchmark/fixture-base/CLAUDE.md 2>/dev/null || true
git commit -m "feat(benchmark): seed and commit the skill-built .arche for the fixture"
```

---

### Task 4: Author the task-1 overlay and the shared task conventions

**Files:**
- Create: `benchmark/tasks/task-1-concurrency/instruction.md`
- Create: `benchmark/tasks/task-1-concurrency/task.toml`
- Create: `benchmark/tasks/task-1-concurrency/solution/solve.sh`
- Create: `benchmark/tasks/task-1-concurrency/tests/test.sh`
- Create: `benchmark/tasks/task-1-concurrency/key_fact.md`

**Interfaces:**
- Consumes: the `billing/invoices.py` stub from Task 1.
- Produces: the per-task file convention every later task follows —
  - `instruction.md`: the prompt shown to the agent (Harbor reads it), **never revealing the fact**.
  - `task.toml`: Harbor config (`[task].name` must be `arche-ab/<task-dir-name>`).
  - `solution/solve.sh`: oracle reference impl; must make `tests/test.sh` pass.
  - `tests/test.sh`: writes `/logs/verifier/reward.txt`, captures the agent diff to `/logs/verifier/final_diff.patch`, and writes `/logs/verifier/task_id.txt` with the task dir name (the analysis keys off `task_id.txt`, not Harbor's config schema).
  - `key_fact.md`: hidden ground truth, JUDGE ONLY. The build script never copies it into `environment/`.

- [ ] **Step 1: Create `task-1-concurrency/instruction.md`**

```markdown
The `update_invoice` function in `billing/invoices.py` currently has no
concurrency control, so two simultaneous updates can silently overwrite each
other. Add concurrency control to `update_invoice` so that concurrent updates
are safe. Edit `billing/invoices.py`.
```

- [ ] **Step 2: Create `task-1-concurrency/task.toml`**

```toml
version = "1.0"

[task]
name = "arche-ab/task-1-concurrency"

[metadata]
difficulty = "hard"
tags = ["arche-ab"]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = 2048
```

- [ ] **Step 3: Create `task-1-concurrency/solution/solve.sh`** (oracle reference — optimistic concurrency)

```bash
#!/bin/bash
set -e
cat > /workspace/billing/invoices.py <<'PY'
"""Invoice operations for the subscription billing service."""

from dataclasses import dataclass


class StaleVersionError(Exception):
    """Raised when an invoice was modified concurrently."""


@dataclass
class Invoice:
    id: str
    customer_id: str
    amount_cents: int
    version: int = 0
    deleted_at: str | None = None


def update_invoice(store, invoice_id, expected_version, **changes):
    """Apply changes using optimistic concurrency (compare-and-set on version)."""
    invoice = store.get(invoice_id)
    if invoice.version != expected_version:
        raise StaleVersionError(invoice_id)
    for key, value in changes.items():
        setattr(invoice, key, value)
    invoice.version += 1
    store.put(invoice)
    return invoice


def delete_invoice(store, invoice_id):
    raise NotImplementedError
PY
```

- [ ] **Step 4: Create `task-1-concurrency/tests/test.sh`** (shared convention — copy verbatim per task, changing only the import module and `task_id`)

```bash
#!/bin/bash
# Structural gate + artifact capture. The discriminating quality grade is the
# external LLM judge; this only proves wiring and captures the diff for the judge.
set -uo pipefail

TASK_ID="task-1-concurrency"
IMPORT_MODULE="billing.invoices"

mkdir -p /logs/verifier
echo "$TASK_ID" > /logs/verifier/task_id.txt

cd /workspace
git add -A 2>/dev/null || true
git diff --cached HEAD > /logs/verifier/final_diff.patch 2>/dev/null || true

if python -c "import ${IMPORT_MODULE}" 2>/dev/null; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
```

- [ ] **Step 5: Create `task-1-concurrency/key_fact.md`** (JUDGE ONLY)

```markdown
The team uses OPTIMISTIC CONCURRENCY for invoice updates (recorded in ADR-002):
read the invoice's integer `version`; on write, persist only if the stored
version still matches the one read, then increment it (compare-and-set); signal a
conflict (e.g. a StaleVersionError) when the version has changed. Pessimistic row
locks (`SELECT ... FOR UPDATE`) are explicitly REJECTED because invoice writes fan
out to external webhooks under lock and caused deadlocks in the legacy system. A
correct answer implements version-based compare-and-set and does NOT reach for row
locks.
```

- [ ] **Step 6: Verify the oracle solution passes its own structural gate locally**

Run:
```bash
cd benchmark
python - <<'PY'
import pathlib, subprocess, tempfile, shutil, os
tmp = tempfile.mkdtemp()
shutil.copytree("fixture-base/billing", f"{tmp}/billing")
# apply the oracle body (mirror of solve.sh) and confirm import works
src = pathlib.Path("tasks/task-1-concurrency/solution/solve.sh").read_text()
body = src.split("<<'PY'\n",1)[1].rsplit("\nPY",1)[0]
pathlib.Path(f"{tmp}/billing/invoices.py").write_text(body)
r = subprocess.run(["python","-c","import billing.invoices, billing.invoices as m; assert hasattr(m,'StaleVersionError')"], cwd=tmp)
print("oracle import ok" if r.returncode==0 else "FAIL")
shutil.rmtree(tmp)
PY
```
Expected: `oracle import ok`.

- [ ] **Step 7: Commit**

```bash
git add benchmark/tasks/task-1-concurrency
git commit -m "feat(benchmark): add task 1 (invoice concurrency) overlay"
```

---

### Task 5: Author task-2 overlay (proration)

**Files:**
- Create: `benchmark/tasks/task-2-proration/{instruction.md,task.toml,solution/solve.sh,tests/test.sh,key_fact.md}`

**Interfaces:**
- Consumes: `billing/proration.py` stub. Follows the Task 4 convention exactly (same `task.toml` shape with `name = "arche-ab/task-2-proration"`; same `tests/test.sh` with `TASK_ID="task-2-proration"`, `IMPORT_MODULE="billing.proration"`).

- [ ] **Step 1: Create `instruction.md`**

```markdown
Implement `prorate_plan_change` in `billing/proration.py`. It should compute the
billing adjustment (in integer cents) when a customer changes plan mid-cycle,
given the old and new plan prices and the days used in the cycle.
```

- [ ] **Step 2: Create `task.toml`** (identical to Task 4 Step 2 but `name = "arche-ab/task-2-proration"`)

```toml
version = "1.0"

[task]
name = "arche-ab/task-2-proration"

[metadata]
difficulty = "hard"
tags = ["arche-ab"]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = 2048
```

- [ ] **Step 3: Create `solution/solve.sh`** (reference — half-up rounding + 14-day grace)

```bash
#!/bin/bash
set -e
cat > /workspace/billing/proration.py <<'PY'
"""Proration for mid-cycle plan changes."""

from decimal import Decimal, ROUND_HALF_UP


def prorate_plan_change(old_cents, new_cents, days_used, days_in_cycle, days_since_last_change):
    """Return the billing adjustment, in integer cents, for a mid-cycle plan change."""
    if days_since_last_change < 14:
        return 0  # 14-day grace window: no re-proration
    days_remaining = days_in_cycle - days_used
    delta_per_cycle = Decimal(new_cents - old_cents)
    adjustment = delta_per_cycle * Decimal(days_remaining) / Decimal(days_in_cycle)
    return int(adjustment.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
PY
```

- [ ] **Step 4: Create `tests/test.sh`** (Task 4 convention, changed ids)

```bash
#!/bin/bash
set -uo pipefail

TASK_ID="task-2-proration"
IMPORT_MODULE="billing.proration"

mkdir -p /logs/verifier
echo "$TASK_ID" > /logs/verifier/task_id.txt

cd /workspace
git add -A 2>/dev/null || true
git diff --cached HEAD > /logs/verifier/final_diff.patch 2>/dev/null || true

if python -c "import ${IMPORT_MODULE}" 2>/dev/null; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
```

- [ ] **Step 5: Create `key_fact.md`** (JUDGE ONLY)

```markdown
Proration uses HALF-UP rounding to the whole cent (NOT banker's/half-even, NOT
truncation), and there is a 14-DAY GRACE WINDOW: if the plan was changed within
the last 14 days (`days_since_last_change < 14`), the change is NOT re-prorated —
the adjustment is 0. A correct answer applies half-up rounding AND returns 0
inside the grace window. Guessing round-half-even/truncation, or omitting the
grace window, is wrong.
```

- [ ] **Step 6: Commit**

```bash
git add benchmark/tasks/task-2-proration
git commit -m "feat(benchmark): add task 2 (proration) overlay"
```

---

### Task 6: Author task-3 overlay (legacy payments — cents gotcha)

**Files:**
- Create: `benchmark/tasks/task-3-payments/{instruction.md,task.toml,solution/solve.sh,tests/test.sh,key_fact.md}`

**Interfaces:**
- Consumes: `billing/payments.py` stub. `name = "arche-ab/task-3-payments"`, `TASK_ID="task-3-payments"`, `IMPORT_MODULE="billing.payments"`.

- [ ] **Step 1: Create `instruction.md`**

```markdown
Implement `record_payment` in `billing/payments.py` so that the amount charged by
`PaymentsGatewayClient.charge()` is recorded on the invoice's `amount_cents`
field. The gateway response is the dict returned by `charge()`.
```

- [ ] **Step 2: Create `task.toml`** (same shape; `name = "arche-ab/task-3-payments"`)

```toml
version = "1.0"

[task]
name = "arche-ab/task-3-payments"

[metadata]
difficulty = "hard"
tags = ["arche-ab"]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = 2048
```

- [ ] **Step 3: Create `solution/solve.sh`** (reference — gateway `amount` is already cents)

```bash
#!/bin/bash
set -e
cat > /workspace/billing/payments.py <<'PY'
"""Integration with the legacy payments gateway."""


class PaymentsGatewayClient:
    def charge(self, customer_id, amount):
        raise NotImplementedError


def record_payment(invoice, gateway_response):
    """Record the charged amount on the invoice.

    The gateway returns `amount` in integer CENTS, matching invoice.amount_cents,
    so it is stored as-is (no *100, no /100).
    """
    invoice.amount_cents = int(gateway_response["amount"])
PY
```

- [ ] **Step 4: Create `tests/test.sh`**

```bash
#!/bin/bash
set -uo pipefail

TASK_ID="task-3-payments"
IMPORT_MODULE="billing.payments"

mkdir -p /logs/verifier
echo "$TASK_ID" > /logs/verifier/task_id.txt

cd /workspace
git add -A 2>/dev/null || true
git diff --cached HEAD > /logs/verifier/final_diff.patch 2>/dev/null || true

if python -c "import ${IMPORT_MODULE}" 2>/dev/null; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
```

- [ ] **Step 5: Create `key_fact.md`** (JUDGE ONLY)

```markdown
`PaymentsGatewayClient.charge()` returns the charged amount in INTEGER CENTS under
the key `amount`, NOT dollars (SME note). The invoice's `amount_cents` field is
also in cents, so the gateway's `amount` must be stored AS-IS. Treating the return
value as dollars (or multiplying/dividing by 100) is the recurring 100x production
bug and is wrong.
```

- [ ] **Step 6: Commit**

```bash
git add benchmark/tasks/task-3-payments
git commit -m "feat(benchmark): add task 3 (legacy payments cents gotcha) overlay"
```

---

### Task 7: Author task-4 overlay (event publishing — superseded ADR)

**Files:**
- Create: `benchmark/tasks/task-4-events/{instruction.md,task.toml,solution/solve.sh,tests/test.sh,key_fact.md}`

**Interfaces:**
- Consumes: `billing/events.py` stub. `name = "arche-ab/task-4-events"`, `TASK_ID="task-4-events"`, `IMPORT_MODULE="billing.events"`.

- [ ] **Step 1: Create `instruction.md`**

```markdown
Implement `publish_invoice_paid` in `billing/events.py` to publish an
'invoice paid' domain event when an invoice is paid. `conn` is an open database
connection/transaction.
```

- [ ] **Step 2: Create `task.toml`** (`name = "arche-ab/task-4-events"`)

```toml
version = "1.0"

[task]
name = "arche-ab/task-4-events"

[metadata]
difficulty = "hard"
tags = ["arche-ab"]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = 2048
```

- [ ] **Step 3: Create `solution/solve.sh`** (reference — transactional outbox, not dual-write)

```bash
#!/bin/bash
set -e
cat > /workspace/billing/events.py <<'PY'
"""Domain event publishing."""

import json


def publish_invoice_paid(conn, invoice_id):
    """Publish an 'invoice paid' event via the transactional outbox (ADR-007).

    Insert into the `outbox` table inside the SAME transaction as the state
    change; a separate relay publishes it. Do NOT dual-write to a broker here.
    """
    payload = json.dumps({"type": "invoice.paid", "invoice_id": invoice_id})
    conn.execute(
        "INSERT INTO outbox (event_type, payload) VALUES (?, ?)",
        ("invoice.paid", payload),
    )
PY
```

- [ ] **Step 4: Create `tests/test.sh`**

```bash
#!/bin/bash
set -uo pipefail

TASK_ID="task-4-events"
IMPORT_MODULE="billing.events"

mkdir -p /logs/verifier
echo "$TASK_ID" > /logs/verifier/task_id.txt

cd /workspace
git add -A 2>/dev/null || true
git diff --cached HEAD > /logs/verifier/final_diff.patch 2>/dev/null || true

if python -c "import ${IMPORT_MODULE}" 2>/dev/null; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
```

- [ ] **Step 5: Create `key_fact.md`** (JUDGE ONLY)

```markdown
Event publishing MUST use the TRANSACTIONAL OUTBOX pattern (ADR-007): inside the
same DB transaction as the state change, insert a row into the `outbox` table; a
separate relay publishes it. The older approach — writing directly to an `events`
table and/or dual-writing to the broker after commit — is recorded in ADR-004 and
is SUPERSEDED by ADR-007. A correct answer writes to the outbox in-transaction and
does NOT dual-write / publish-after-commit. Using the superseded dual-write
approach is wrong.
```

- [ ] **Step 6: Commit**

```bash
git add benchmark/tasks/task-4-events
git commit -m "feat(benchmark): add task 4 (event publishing superseded ADR) overlay"
```

---

### Task 8: Author task-5 overlay (invoice deletion — retention)

**Files:**
- Create: `benchmark/tasks/task-5-retention/{instruction.md,task.toml,solution/solve.sh,tests/test.sh,key_fact.md}`

**Interfaces:**
- Consumes: `billing/invoices.py` stub (`delete_invoice`). `name = "arche-ab/task-5-retention"`, `TASK_ID="task-5-retention"`, `IMPORT_MODULE="billing.invoices"`.

- [ ] **Step 1: Create `instruction.md`**

```markdown
Implement `delete_invoice` in `billing/invoices.py` so that an invoice can be
deleted. `store` exposes `get(id) -> Invoice` and `put(invoice)`.
```

- [ ] **Step 2: Create `task.toml`** (`name = "arche-ab/task-5-retention"`)

```toml
version = "1.0"

[task]
name = "arche-ab/task-5-retention"

[metadata]
difficulty = "hard"
tags = ["arche-ab"]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 300.0
cpus = 1
memory_mb = 2048
```

- [ ] **Step 3: Create `solution/solve.sh`** (reference — soft delete). Preserves `update_invoice` behavior since this task also edits `invoices.py`; the reference keeps the original `update_invoice` and implements soft delete.

```bash
#!/bin/bash
set -e
cat > /workspace/billing/invoices.py <<'PY'
"""Invoice operations for the subscription billing service."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Invoice:
    id: str
    customer_id: str
    amount_cents: int
    version: int = 0
    deleted_at: str | None = None


def update_invoice(store, invoice_id, **changes):
    invoice = store.get(invoice_id)
    for key, value in changes.items():
        setattr(invoice, key, value)
    store.put(invoice)
    return invoice


def delete_invoice(store, invoice_id):
    """Soft-delete: invoices are financial records under 7-year retention and
    must never be hard-deleted. Mark deleted_at and retain the row."""
    invoice = store.get(invoice_id)
    invoice.deleted_at = datetime.now(timezone.utc).isoformat()
    store.put(invoice)
    return invoice
PY
```

- [ ] **Step 4: Create `tests/test.sh`**

```bash
#!/bin/bash
set -uo pipefail

TASK_ID="task-5-retention"
IMPORT_MODULE="billing.invoices"

mkdir -p /logs/verifier
echo "$TASK_ID" > /logs/verifier/task_id.txt

cd /workspace
git add -A 2>/dev/null || true
git diff --cached HEAD > /logs/verifier/final_diff.patch 2>/dev/null || true

if python -c "import ${IMPORT_MODULE}" 2>/dev/null; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
```

- [ ] **Step 5: Create `key_fact.md`** (JUDGE ONLY)

```markdown
Invoices are financial records under a 7-YEAR AUDIT-RETENTION requirement
(SOX/tax; compliance research page). They must NEVER be hard-deleted. "Deletion"
is a SOFT DELETE: set `deleted_at` to the current timestamp and exclude
soft-deleted invoices from normal queries; the row is retained. A correct answer
implements a soft delete. A hard delete (removing the row / `DELETE FROM`) is
wrong.
```

- [ ] **Step 6: Commit**

```bash
git add benchmark/tasks/task-5-retention
git commit -m "feat(benchmark): add task 5 (invoice deletion retention) overlay"
```

---

### Task 9: Build script — materialize Arm-A and Arm-B fixtures

**Files:**
- Create: `benchmark/build_fixtures.py`
- Test: `benchmark/tests/test_build_fixtures.py`

**Interfaces:**
- Consumes: `benchmark/fixture-base/` (billing/, .arche/, AGENTS.md) and `benchmark/tasks/*/` overlays.
- Produces: `build(base_dir, tasks_dir, out_dir) -> list[str]` writing, for each task and each arm in `("a","b")`:
  `out_dir/arm-<arm>/<task>/{instruction.md, task.toml, solution/solve.sh, tests/test.sh, environment/{Dockerfile,.dockerignore, billing/, [.arche/], [AGENTS.md]}}`.
  Arm A includes `.arche/` and the full `AGENTS.md`; Arm B omits `.arche/` and strips the `<!-- arche-context-source -->` block from `AGENTS.md` (removing the file if it becomes empty). `key_fact.md` is NEVER copied. Returns the list of created task dirs.
- `strip_arche_block(text) -> str` removes the marked block (from the marker line to the end of that block / EOF) and returns the remainder.

- [ ] **Step 1: Write the failing tests**

```python
# benchmark/tests/test_build_fixtures.py
import hashlib
import pathlib

import pytest

import build_fixtures


def _write(p: pathlib.Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


@pytest.fixture
def tiny_repo(tmp_path):
    base = tmp_path / "fixture-base"
    _write(base / "billing" / "__init__.py", "# pkg\n")
    _write(base / "billing" / "invoices.py", "x = 1\n")
    _write(base / "AGENTS.md", "<!-- arche-context-source -->\nconsult the Arche\n")
    _write(base / ".arche" / "index.md", "# index\n")
    tasks = tmp_path / "tasks"
    _write(tasks / "task-1-x" / "instruction.md", "do the thing\n")
    _write(tasks / "task-1-x" / "task.toml", '[task]\nname = "arche-ab/task-1-x"\n')
    _write(tasks / "task-1-x" / "solution" / "solve.sh", "#!/bin/bash\ntrue\n")
    _write(tasks / "task-1-x" / "tests" / "test.sh", "#!/bin/bash\ntrue\n")
    _write(tasks / "task-1-x" / "key_fact.md", "SECRET\n")
    return base, tasks


def _digest(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_strip_arche_block_removes_marked_section():
    text = "keep me\n<!-- arche-context-source -->\nremove me\n"
    assert build_fixtures.strip_arche_block(text) == "keep me\n"


def test_arm_a_has_arche_and_registration(tiny_repo, tmp_path):
    base, tasks = tiny_repo
    out = tmp_path / "fixtures"
    build_fixtures.build(base, tasks, out)
    env_a = out / "arm-a" / "task-1-x" / "environment"
    assert (env_a / ".arche" / "index.md").exists()
    assert "arche-context-source" in (env_a / "AGENTS.md").read_text()
    assert (env_a / "billing" / "invoices.py").exists()


def test_arm_b_omits_arche_and_registration(tiny_repo, tmp_path):
    base, tasks = tiny_repo
    out = tmp_path / "fixtures"
    build_fixtures.build(base, tasks, out)
    env_b = out / "arm-b" / "task-1-x" / "environment"
    assert not (env_b / ".arche").exists()
    # AGENTS.md is removed because it only contained the arche block
    assert not (env_b / "AGENTS.md").exists()


def test_billing_is_byte_identical_across_arms(tiny_repo, tmp_path):
    base, tasks = tiny_repo
    out = tmp_path / "fixtures"
    build_fixtures.build(base, tasks, out)
    a = out / "arm-a" / "task-1-x" / "environment" / "billing" / "invoices.py"
    b = out / "arm-b" / "task-1-x" / "environment" / "billing" / "invoices.py"
    assert _digest(a) == _digest(b)


def test_key_fact_is_never_baked(tiny_repo, tmp_path):
    base, tasks = tiny_repo
    out = tmp_path / "fixtures"
    build_fixtures.build(base, tasks, out)
    for arm in ("a", "b"):
        task = out / f"arm-{arm}" / "task-1-x"
        assert not list(task.rglob("key_fact.md"))


def test_overlay_files_present_and_dockerfile_written(tiny_repo, tmp_path):
    base, tasks = tiny_repo
    out = tmp_path / "fixtures"
    build_fixtures.build(base, tasks, out)
    task = out / "arm-a" / "task-1-x"
    assert (task / "instruction.md").exists()
    assert (task / "task.toml").exists()
    assert (task / "solution" / "solve.sh").exists()
    assert (task / "tests" / "test.sh").exists()
    assert (task / "environment" / "Dockerfile").exists()
    assert (task / "environment" / ".dockerignore").exists()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_build_fixtures.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'build_fixtures'`.

- [ ] **Step 3: Write `benchmark/build_fixtures.py`**

```python
"""Materialize Arm-A and Arm-B Harbor task directories from the base fixture
and per-task overlays. Pure filesystem transform; no Docker or API calls."""

import shutil
from pathlib import Path

ARCHE_MARKER = "<!-- arche-context-source -->"

DOCKERFILE = """\
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git \\
    && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY . /workspace/
RUN git init -q && git add -A \\
    && git -c user.email=fixture@example.com -c user.name=fixture commit -qm baseline
CMD ["/bin/bash"]
"""

DOCKERIGNORE = "Dockerfile\n.dockerignore\n"


def strip_arche_block(text: str) -> str:
    """Remove everything from the arche marker line to EOF."""
    idx = text.find(ARCHE_MARKER)
    if idx == -1:
        return text
    # cut back to the start of the marker's line
    line_start = text.rfind("\n", 0, idx) + 1
    return text[:line_start]


def _copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _build_environment(base_dir: Path, env_dir: Path, arm: str) -> None:
    env_dir.mkdir(parents=True, exist_ok=True)
    # base billing package (identical across arms)
    _copy_tree(base_dir / "billing", env_dir / "billing")
    # optional README
    readme = base_dir / "README.md"
    if readme.exists():
        shutil.copy2(readme, env_dir / "README.md")

    agents = base_dir / "AGENTS.md"
    if arm == "a":
        if (base_dir / ".arche").exists():
            _copy_tree(base_dir / ".arche", env_dir / ".arche")
        if agents.exists():
            shutil.copy2(agents, env_dir / "AGENTS.md")
        for bridge in ("CLAUDE.md",):
            if (base_dir / bridge).exists():
                shutil.copy2(base_dir / bridge, env_dir / bridge)
    else:  # arm == "b": no .arche, strip registration
        if agents.exists():
            stripped = strip_arche_block(agents.read_text())
            if stripped.strip():
                (env_dir / "AGENTS.md").write_text(stripped)
        # CLAUDE.md that only imports AGENTS.md is dropped for arm B

    (env_dir / "Dockerfile").write_text(DOCKERFILE)
    (env_dir / ".dockerignore").write_text(DOCKERIGNORE)


def _build_task(base_dir: Path, task_src: Path, arm_out: Path, arm: str) -> Path:
    task_out = arm_out / task_src.name
    task_out.mkdir(parents=True, exist_ok=True)
    # overlay files (everything EXCEPT key_fact.md and environment/)
    shutil.copy2(task_src / "instruction.md", task_out / "instruction.md")
    shutil.copy2(task_src / "task.toml", task_out / "task.toml")
    _copy_tree(task_src / "solution", task_out / "solution")
    _copy_tree(task_src / "tests", task_out / "tests")
    _build_environment(base_dir, task_out / "environment", arm)
    return task_out


def build(base_dir, tasks_dir, out_dir) -> list[str]:
    base_dir, tasks_dir, out_dir = Path(base_dir), Path(tasks_dir), Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    created: list[str] = []
    task_srcs = sorted(p for p in tasks_dir.iterdir() if p.is_dir())
    for arm in ("a", "b"):
        arm_out = out_dir / f"arm-{arm}"
        for task_src in task_srcs:
            created.append(str(_build_task(base_dir, task_src, arm_out, arm)))
    return created


if __name__ == "__main__":
    here = Path(__file__).parent
    dirs = build(here / "fixture-base", here / "tasks", here / "fixtures")
    print(f"built {len(dirs)} task dirs -> {here / 'fixtures'}")
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_build_fixtures.py -q`
Expected: PASS (6 passed).

- [ ] **Step 5: Build the real fixtures and sanity-check**

Run:
```bash
cd benchmark && .venv/bin/python build_fixtures.py
test -d fixtures/arm-a/task-1-concurrency/environment/.arche && echo "arm-a arche ok"
test ! -e fixtures/arm-b/task-1-concurrency/environment/.arche && echo "arm-b no arche ok"
find fixtures -name key_fact.md | grep -q . && echo "LEAK: key_fact baked" || echo "no key_fact leak ok"
```
Expected: `arm-a arche ok`, `arm-b no arche ok`, `no key_fact leak ok`.

- [ ] **Step 6: Commit**

```bash
git add benchmark/build_fixtures.py benchmark/tests/test_build_fixtures.py
git commit -m "feat(benchmark): add fixture build script for arm A/B materialization"
```

---

### Task 10: ATIF trajectory parser

**Files:**
- Create: `benchmark/analysis/parse_trajectory.py`
- Create: `benchmark/tests/fixtures/trajectory_sample.json`
- Test: `benchmark/tests/test_parse_trajectory.py`

**Interfaces:**
- Produces: `parse_trajectory(path) -> dict` with keys
  `prompt_tokens, completion_tokens, total_tokens, cached_tokens, cost_usd, steps, tool_calls`.
  Reads `final_metrics.{total_prompt_tokens,total_completion_tokens,total_cached_tokens,total_cost_usd,total_steps}` when present; falls back to summing per-step `metrics`. `total_tokens = prompt_tokens + completion_tokens`. `tool_calls = sum(len(step.get("tool_calls", [])))`.

- [ ] **Step 1: Create the golden ATIF fixture `benchmark/tests/fixtures/trajectory_sample.json`**

```json
{
  "schema_version": "ATIF-v1.7",
  "session_id": "test-session",
  "agent": {"name": "claude-code", "model_name": "claude-sonnet-5"},
  "steps": [
    {
      "step_id": 1,
      "source": "agent",
      "tool_calls": [{"tool_call_id": "c1", "function_name": "read"}],
      "metrics": {"prompt_tokens": 500, "completion_tokens": 40, "cached_tokens": 100, "cost_usd": 0.0004}
    },
    {
      "step_id": 2,
      "source": "agent",
      "tool_calls": [
        {"tool_call_id": "c2", "function_name": "edit"},
        {"tool_call_id": "c3", "function_name": "bash"}
      ],
      "metrics": {"prompt_tokens": 620, "completion_tokens": 84, "cached_tokens": 200, "cost_usd": 0.0006}
    }
  ],
  "final_metrics": {
    "total_prompt_tokens": 1120,
    "total_completion_tokens": 124,
    "total_cached_tokens": 300,
    "total_cost_usd": 0.0010,
    "total_steps": 2
  }
}
```

- [ ] **Step 2: Write the failing tests**

```python
# benchmark/tests/test_parse_trajectory.py
import json
from pathlib import Path

from analysis import parse_trajectory

FIX = Path(__file__).parent / "fixtures" / "trajectory_sample.json"


def test_reads_final_metrics():
    m = parse_trajectory.parse_trajectory(FIX)
    assert m["prompt_tokens"] == 1120
    assert m["completion_tokens"] == 124
    assert m["total_tokens"] == 1244
    assert m["cached_tokens"] == 300
    assert m["cost_usd"] == 0.0010
    assert m["steps"] == 2


def test_counts_tool_calls_across_steps():
    m = parse_trajectory.parse_trajectory(FIX)
    assert m["tool_calls"] == 3


def test_falls_back_to_summing_steps(tmp_path):
    data = json.loads(FIX.read_text())
    del data["final_metrics"]
    p = tmp_path / "no_final.json"
    p.write_text(json.dumps(data))
    m = parse_trajectory.parse_trajectory(p)
    assert m["prompt_tokens"] == 1120
    assert m["completion_tokens"] == 124
    assert m["total_tokens"] == 1244
    assert m["steps"] == 2
    assert m["tool_calls"] == 3
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_parse_trajectory.py -q`
Expected: FAIL (`ImportError` / `AttributeError`).

- [ ] **Step 4: Write `benchmark/analysis/parse_trajectory.py`**

```python
"""Parse a Harbor ATIF trajectory file into token/cost/step metrics.

ATIF has no `total_tokens` field — it is derived as prompt + completion.
Prefer `final_metrics`; fall back to summing per-step `metrics`.
"""

import json
from pathlib import Path


def parse_trajectory(path) -> dict:
    data = json.loads(Path(path).read_text())
    steps = data.get("steps", [])
    tool_calls = sum(len(s.get("tool_calls") or []) for s in steps)

    fm = data.get("final_metrics")
    if fm:
        prompt = int(fm.get("total_prompt_tokens", 0))
        completion = int(fm.get("total_completion_tokens", 0))
        cached = int(fm.get("total_cached_tokens", 0))
        cost = float(fm.get("total_cost_usd", 0.0))
        n_steps = int(fm.get("total_steps", len(steps)))
    else:
        prompt = completion = cached = 0
        cost = 0.0
        for s in steps:
            m = s.get("metrics") or {}
            prompt += int(m.get("prompt_tokens", 0))
            completion += int(m.get("completion_tokens", 0))
            cached += int(m.get("cached_tokens", 0))
            cost += float(m.get("cost_usd", 0.0))
        n_steps = len(steps)

    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": prompt + completion,
        "cached_tokens": cached,
        "cost_usd": cost,
        "steps": n_steps,
        "tool_calls": tool_calls,
    }
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_parse_trajectory.py -q`
Expected: PASS (3 passed).

- [ ] **Step 6: Commit**

```bash
git add benchmark/analysis/parse_trajectory.py benchmark/tests/test_parse_trajectory.py benchmark/tests/fixtures/trajectory_sample.json
git commit -m "feat(benchmark): add ATIF trajectory parser"
```

---

### Task 11: Blind LLM judge (Opus 4.8, median of 3)

**Files:**
- Create: `benchmark/analysis/judge.py`
- Test: `benchmark/tests/test_judge.py`

**Interfaces:**
- Consumes: nothing from other analysis modules.
- Produces:
  - `Verdict` Pydantic model: `arche_fact_adherence: int`, `domain_justification: int`, `task_completion: int` (each 0–3), `rationale: str`.
  - `build_messages(instruction, diff, key_fact) -> list[dict]` — the judge prompt. Blind to arm (input carries no arm info).
  - `judge_once(client, instruction, diff, key_fact, model="claude-opus-4-8") -> Verdict` — one call via `client.messages.parse(..., thinking={"type": "disabled"}, output_config={"format": ...})`. **No `temperature`** (rejected on Opus 4.8).
  - `judge(client, instruction, diff, key_fact, model="claude-opus-4-8", passes=3) -> Verdict` — runs `passes` judgments and returns the per-dimension **median** (rationale from the first pass). Controls variance in place of temperature.

- [ ] **Step 1: Write the failing tests** (mock the Anthropic client — no network)

```python
# benchmark/tests/test_judge.py
from analysis import judge


class FakeParsed:
    def __init__(self, verdict):
        self.parsed_output = verdict


class FakeMessages:
    def __init__(self, verdicts):
        self._verdicts = list(verdicts)
        self.calls = 0

    def parse(self, **kwargs):
        v = self._verdicts[self.calls % len(self._verdicts)]
        self.calls += 1
        # kwargs are asserted by the test that cares
        self.last_kwargs = kwargs
        return FakeParsed(v)


class FakeClient:
    def __init__(self, verdicts):
        self.messages = FakeMessages(verdicts)


def _v(a, d, t, r="ok"):
    return judge.Verdict(arche_fact_adherence=a, domain_justification=d, task_completion=t, rationale=r)


def test_build_messages_includes_inputs_and_hides_arm():
    msgs = judge.build_messages("do X", "diff here", "KEY FACT")
    text = "".join(m["content"] if isinstance(m["content"], str) else str(m["content"]) for m in msgs)
    assert "do X" in text and "diff here" in text and "KEY FACT" in text
    assert "arm" not in text.lower()  # judge never learns the arm


def test_judge_once_disables_thinking_and_omits_temperature():
    client = FakeClient([_v(3, 2, 3)])
    judge.judge_once(client, "i", "d", "k")
    kw = client.messages.last_kwargs
    assert kw["model"] == "claude-opus-4-8"
    assert kw["thinking"] == {"type": "disabled"}
    assert "temperature" not in kw  # Opus 4.8 rejects temperature


def test_judge_takes_median_over_passes():
    # dimension medians: adherence [3,1,3]->3, justification [2,0,1]->1, completion [3,3,0]->3
    client = FakeClient([_v(3, 2, 3, "first"), _v(1, 0, 3), _v(3, 1, 0)])
    out = judge.judge(client, "i", "d", "k", passes=3)
    assert (out.arche_fact_adherence, out.domain_justification, out.task_completion) == (3, 1, 3)
    assert out.rationale == "first"
    assert client.messages.calls == 3
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_judge.py -q`
Expected: FAIL (`ImportError`).

- [ ] **Step 3: Write `benchmark/analysis/judge.py`**

```python
"""Blind LLM judge for the Arche A/B benchmark.

Scores an agent's final diff against a hidden key fact on a 0-3 rubric. The judge
never learns which arm produced the diff. `claude-opus-4-8` rejects `temperature`,
so variance is controlled by disabling thinking and taking the median of N passes.
"""

import statistics

from pydantic import BaseModel, Field

JUDGE_MODEL = "claude-opus-4-8"


class Verdict(BaseModel):
    arche_fact_adherence: int = Field(ge=0, le=3)
    domain_justification: int = Field(ge=0, le=3)
    task_completion: int = Field(ge=0, le=3)
    rationale: str


SYSTEM = (
    "You are an expert software reviewer scoring one code change against a rubric. "
    "You are given the task prompt, the agent's final diff, and a hidden GROUND-TRUTH "
    "KEY FACT that the agent may or may not have known. Score only on the rubric below. "
    "Do not speculate about the agent's setup or tools.\n\n"
    "Rubric (integer 0-3 each):\n"
    "- arche_fact_adherence: did the change honor the recorded decision/rule in the KEY FACT? "
    "(0 = contradicts it, 3 = fully honors it). This is the primary dimension.\n"
    "- domain_justification: did it reason from the domain rather than guess a generic default? "
    "(0 = generic guess, 3 = clearly domain-correct reasoning).\n"
    "- task_completion: does the change actually work for the stated task, independent of the fact? "
    "(0 = broken/absent, 3 = complete and correct).\n"
    "Return JSON with the three integer scores and a one-paragraph rationale."
)


def build_messages(instruction: str, diff: str, key_fact: str) -> list[dict]:
    user = (
        f"## Task prompt\n{instruction}\n\n"
        f"## Ground-truth key fact (hidden from the agent)\n{key_fact}\n\n"
        f"## Agent's final diff\n```diff\n{diff}\n```\n"
    )
    return [{"role": "user", "content": user}]


def judge_once(client, instruction, diff, key_fact, model=JUDGE_MODEL) -> Verdict:
    resp = client.messages.parse(
        model=model,
        max_tokens=2000,
        system=SYSTEM,
        thinking={"type": "disabled"},
        messages=build_messages(instruction, diff, key_fact),
        output_format=Verdict,
    )
    return resp.parsed_output


def judge(client, instruction, diff, key_fact, model=JUDGE_MODEL, passes=3) -> Verdict:
    verdicts = [judge_once(client, instruction, diff, key_fact, model) for _ in range(passes)]

    def med(attr):
        return int(statistics.median(getattr(v, attr) for v in verdicts))

    return Verdict(
        arche_fact_adherence=med("arche_fact_adherence"),
        domain_justification=med("domain_justification"),
        task_completion=med("task_completion"),
        rationale=verdicts[0].rationale,
    )
```

> Note on `messages.parse` / `output_format`: the Anthropic Python SDK exposes `client.messages.parse(..., output_format=PydanticModel)` returning `.parsed_output`. If your installed SDK version instead only supports `output_config={"format": {...}}` on `messages.create`, adapt `judge_once` accordingly — the median logic and prompt are unchanged. The mocked tests exercise the median/prompt logic, not the SDK.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_judge.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add benchmark/analysis/judge.py benchmark/tests/test_judge.py
git commit -m "feat(benchmark): add blind Opus-4.8 rubric judge (median of 3)"
```

---

### Task 12: Collect run records from a Harbor jobs directory

**Files:**
- Create: `benchmark/analysis/collect_runs.py`
- Test: `benchmark/tests/test_collect_runs.py`

**Interfaces:**
- Consumes: `parse_trajectory.parse_trajectory`.
- Produces: `collect_runs(job_dir, arm) -> list[dict]`. Walks each trial subdir of `job_dir`; for each trial reads `verifier/task_id.txt` (task), `verifier/final_diff.patch` (diff, `""` if absent), `verifier/reward.txt` (int, 0 if absent), and `agent/trajectory.json` (via `parse_trajectory`). Assigns `trial` as a 1-based index per task (sorted by trial dir name for determinism). Skips trial dirs missing `verifier/task_id.txt`. Each record: `{task, arm, trial, diff, reward, prompt_tokens, completion_tokens, total_tokens, cost_usd, steps, tool_calls}`.

- [ ] **Step 1: Write the failing tests**

```python
# benchmark/tests/test_collect_runs.py
import json
import shutil
from pathlib import Path

from analysis import collect_runs

SAMPLE = Path(__file__).parent / "fixtures" / "trajectory_sample.json"


def _make_trial(job_dir, name, task_id, diff, reward):
    t = job_dir / name
    (t / "agent").mkdir(parents=True)
    (t / "verifier").mkdir(parents=True)
    shutil.copy2(SAMPLE, t / "agent" / "trajectory.json")
    if task_id is not None:
        (t / "verifier" / "task_id.txt").write_text(task_id + "\n")
    (t / "verifier" / "final_diff.patch").write_text(diff)
    (t / "verifier" / "reward.txt").write_text(str(reward) + "\n")


def test_collect_builds_records_with_metrics(tmp_path):
    job = tmp_path / "job"
    _make_trial(job, "task-1-x__1", "task-1-x", "DIFF-A", 1)
    _make_trial(job, "task-1-x__2", "task-1-x", "DIFF-B", 1)
    recs = collect_runs.collect_runs(job, arm="a")
    assert len(recs) == 2
    r = recs[0]
    assert r["task"] == "task-1-x" and r["arm"] == "a"
    assert {rec["trial"] for rec in recs} == {1, 2}
    assert r["total_tokens"] == 1244 and r["tool_calls"] == 3
    assert r["diff"] in {"DIFF-A", "DIFF-B"}


def test_collect_skips_trials_without_task_id(tmp_path):
    job = tmp_path / "job"
    _make_trial(job, "broken", None, "x", 0)
    _make_trial(job, "task-2-y__1", "task-2-y", "d", 1)
    recs = collect_runs.collect_runs(job, arm="b")
    assert [r["task"] for r in recs] == ["task-2-y"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_collect_runs.py -q`
Expected: FAIL (`ImportError`).

- [ ] **Step 3: Write `benchmark/analysis/collect_runs.py`**

```python
"""Walk a Harbor jobs/<job-name> directory and build one record per trial.

Task identity comes from verifier/task_id.txt (written by tests/test.sh), so this
does not depend on Harbor's internal config schema.
"""

from collections import defaultdict
from pathlib import Path

from analysis.parse_trajectory import parse_trajectory


def _read(p: Path, default=""):
    return p.read_text() if p.exists() else default


def collect_runs(job_dir, arm) -> list[dict]:
    job_dir = Path(job_dir)
    trials = sorted(p for p in job_dir.iterdir() if p.is_dir())

    records = []
    for t in trials:
        task_id_file = t / "verifier" / "task_id.txt"
        if not task_id_file.exists():
            continue
        task = task_id_file.read_text().strip()
        diff = _read(t / "verifier" / "final_diff.patch")
        reward_txt = _read(t / "verifier" / "reward.txt", "0").strip()
        reward = int(reward_txt) if reward_txt.isdigit() else 0

        traj = t / "agent" / "trajectory.json"
        metrics = parse_trajectory(traj) if traj.exists() else {
            "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
            "cached_tokens": 0, "cost_usd": 0.0, "steps": 0, "tool_calls": 0,
        }
        records.append({"task": task, "arm": arm, "diff": diff, "reward": reward, **metrics})

    # assign 1-based trial index per task, deterministic by original sort order
    counter = defaultdict(int)
    for r in records:
        counter[r["task"]] += 1
        r["trial"] = counter[r["task"]]
    return records
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_collect_runs.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add benchmark/analysis/collect_runs.py benchmark/tests/test_collect_runs.py
git commit -m "feat(benchmark): add Harbor jobs collector keyed on task_id.txt"
```

---

### Task 13: Aggregate — per-cell means, validity gate, headline metrics

**Files:**
- Create: `benchmark/analysis/aggregate.py`
- Test: `benchmark/tests/test_aggregate.py`

**Interfaces:**
- Consumes: judged run records — each `{task, arm, trial, arche_fact_adherence, domain_justification, task_completion, total_tokens, cost_usd, steps, ...}`.
- Produces:
  - `quality(rec) -> int`: sum of the three rubric dimensions (0–9).
  - `cell_means(records) -> dict[(task,arm)] -> {quality, adherence, total_tokens, steps, n}`: means over trials.
  - `validity_gate(cell_means, threshold=1.5) -> dict[task] -> {passed: bool, arm_b_adherence: float}`: a task **passes** (is valid) when Arm B's mean `arche_fact_adherence` is **below** `threshold` (control largely fails the fact). Threshold is on the 0–3 adherence scale.
  - `headline(cell_means, valid_tasks) -> dict`: per-task and pooled (valid tasks only) `quality_delta` (A−B), `token_delta` (A−B), `step_delta` (A−B), and `quality_per_1k_tokens` for each arm (`mean_quality / (mean_total_tokens/1000)`).

- [ ] **Step 1: Write the failing tests**

```python
# benchmark/tests/test_aggregate.py
from analysis import aggregate


def _rec(task, arm, trial, adh, dj, tc, tokens, steps):
    return {
        "task": task, "arm": arm, "trial": trial,
        "arche_fact_adherence": adh, "domain_justification": dj, "task_completion": tc,
        "total_tokens": tokens, "cost_usd": 0.0, "steps": steps,
    }


def _dataset():
    recs = []
    # task T1: A honors fact (adh 3), B fails it (adh 0) -> valid, quality up
    for i in (1, 2):
        recs.append(_rec("T1", "a", i, 3, 3, 3, 12000, 20))
        recs.append(_rec("T1", "b", i, 0, 1, 3, 8000, 14))
    # task T2: B also honors fact (adh 3) -> INVALID (control didn't need the Arche)
    for i in (1, 2):
        recs.append(_rec("T2", "a", i, 3, 3, 3, 11000, 18))
        recs.append(_rec("T2", "b", i, 3, 3, 3, 10500, 17))
    return recs


def test_quality_sums_three_dimensions():
    assert aggregate.quality(_rec("x", "a", 1, 3, 2, 3, 0, 0)) == 8


def test_cell_means():
    cm = aggregate.cell_means(_dataset())
    assert cm[("T1", "a")]["quality"] == 9.0
    assert cm[("T1", "b")]["adherence"] == 0.0
    assert cm[("T1", "a")]["total_tokens"] == 12000.0
    assert cm[("T1", "a")]["n"] == 2


def test_validity_gate_flags_control_that_honors_fact():
    cm = aggregate.cell_means(_dataset())
    gate = aggregate.validity_gate(cm, threshold=1.5)
    assert gate["T1"]["passed"] is True     # arm B adherence 0 < 1.5
    assert gate["T2"]["passed"] is False    # arm B adherence 3 >= 1.5


def test_headline_pools_valid_tasks_only():
    cm = aggregate.cell_means(_dataset())
    gate = aggregate.validity_gate(cm, threshold=1.5)
    valid = [t for t, g in gate.items() if g["passed"]]
    h = aggregate.headline(cm, valid)
    # only T1 pooled: quality delta = 9 - 4 = 5 ; token delta = 12000 - 8000
    assert h["pooled"]["quality_delta"] == 5.0
    assert h["pooled"]["token_delta"] == 4000.0
    assert h["per_task"]["T1"]["step_delta"] == 6.0
    assert round(h["per_task"]["T1"]["quality_per_1k_tokens"]["a"], 3) == round(9.0 / 12.0, 3)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_aggregate.py -q`
Expected: FAIL (`ImportError`).

- [ ] **Step 3: Write `benchmark/analysis/aggregate.py`**

```python
"""Aggregate judged run records: per-cell means, validity gate, headline deltas."""

from collections import defaultdict
from statistics import mean

DIMENSIONS = ("arche_fact_adherence", "domain_justification", "task_completion")


def quality(rec) -> int:
    return sum(int(rec[d]) for d in DIMENSIONS)


def cell_means(records) -> dict:
    by_cell = defaultdict(list)
    for r in records:
        by_cell[(r["task"], r["arm"])].append(r)
    out = {}
    for cell, recs in by_cell.items():
        out[cell] = {
            "quality": mean(quality(r) for r in recs),
            "adherence": mean(r["arche_fact_adherence"] for r in recs),
            "total_tokens": mean(r["total_tokens"] for r in recs),
            "steps": mean(r["steps"] for r in recs),
            "n": len(recs),
        }
    return out


def validity_gate(cm, threshold=1.5) -> dict:
    tasks = {task for (task, _arm) in cm}
    gate = {}
    for task in tasks:
        b = cm.get((task, "b"))
        arm_b_adh = b["adherence"] if b else float("nan")
        gate[task] = {"passed": bool(b) and arm_b_adh < threshold, "arm_b_adherence": arm_b_adh}
    return gate


def _qp1k(cell):
    tok = cell["total_tokens"]
    return cell["quality"] / (tok / 1000.0) if tok else 0.0


def headline(cm, valid_tasks) -> dict:
    per_task = {}
    for task in valid_tasks:
        a, b = cm[(task, "a")], cm[(task, "b")]
        per_task[task] = {
            "quality_delta": a["quality"] - b["quality"],
            "token_delta": a["total_tokens"] - b["total_tokens"],
            "step_delta": a["steps"] - b["steps"],
            "quality_per_1k_tokens": {"a": _qp1k(a), "b": _qp1k(b)},
        }
    if valid_tasks:
        pooled = {
            "quality_delta": mean(per_task[t]["quality_delta"] for t in valid_tasks),
            "token_delta": mean(per_task[t]["token_delta"] for t in valid_tasks),
            "step_delta": mean(per_task[t]["step_delta"] for t in valid_tasks),
        }
    else:
        pooled = {"quality_delta": 0.0, "token_delta": 0.0, "step_delta": 0.0}
    return {"per_task": per_task, "pooled": pooled}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_aggregate.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add benchmark/analysis/aggregate.py benchmark/tests/test_aggregate.py
git commit -m "feat(benchmark): add aggregation, validity gate, and headline metrics"
```

---

### Task 14: Render the markdown report

**Files:**
- Create: `benchmark/analysis/report.py`
- Test: `benchmark/tests/test_report.py`

**Interfaces:**
- Consumes: `cell_means`, `validity_gate`, `headline` outputs.
- Produces: `render_report(cell_means, gate, headline, n_trials) -> str` — a markdown report with (1) a header stating n=5 is directional, not significant; (2) a per-(task,arm) results table (quality, adherence, total tokens, steps); (3) a validity-gate section listing which tasks passed and calling out dropped tasks; (4) a headline section with per-task and pooled quality Δ, token Δ, step Δ, and quality-per-1k-tokens.

- [ ] **Step 1: Write the failing tests**

```python
# benchmark/tests/test_report.py
from analysis import aggregate, report


def _recs():
    r = []
    for i in (1, 2):
        r.append({"task": "T1", "arm": "a", "trial": i, "arche_fact_adherence": 3,
                  "domain_justification": 3, "task_completion": 3, "total_tokens": 12000,
                  "cost_usd": 0.0, "steps": 20})
        r.append({"task": "T1", "arm": "b", "trial": i, "arche_fact_adherence": 0,
                  "domain_justification": 1, "task_completion": 3, "total_tokens": 8000,
                  "cost_usd": 0.0, "steps": 14})
    return r


def test_report_contains_key_sections():
    cm = aggregate.cell_means(_recs())
    gate = aggregate.validity_gate(cm)
    valid = [t for t, g in gate.items() if g["passed"]]
    h = aggregate.headline(cm, valid)
    md = report.render_report(cm, gate, h, n_trials=2)
    assert "directional" in md.lower()
    assert "Validity gate" in md
    assert "Quality per 1k" in md
    assert "T1" in md
    assert "| a |" in md or "arm-a" in md.lower()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_report.py -q`
Expected: FAIL (`ImportError`).

- [ ] **Step 3: Write `benchmark/analysis/report.py`**

```python
"""Render the Arche A/B benchmark report as markdown."""


def render_report(cell_means, gate, headline, n_trials) -> str:
    lines = []
    lines.append("# Arche A/B Benchmark — Results\n")
    lines.append(
        f"5 tasks x {n_trials} trials x 2 arms. At n={n_trials} this is "
        f"**directional, not statistically significant** — read the per-task "
        f"breakdown over the pooled average.\n"
    )

    lines.append("## Per-cell means\n")
    lines.append("| task | arm | quality (0-9) | adherence (0-3) | total tokens | steps |")
    lines.append("|------|-----|---------------|-----------------|--------------|-------|")
    tasks = sorted({t for (t, _a) in cell_means})
    for task in tasks:
        for arm in ("a", "b"):
            c = cell_means.get((task, arm))
            if not c:
                continue
            lines.append(
                f"| {task} | {arm} | {c['quality']:.2f} | {c['adherence']:.2f} | "
                f"{c['total_tokens']:.0f} | {c['steps']:.1f} |"
            )
    lines.append("")

    lines.append("## Validity gate\n")
    lines.append(
        "A task is valid only if Arm B (no Arche) largely **fails** fact-adherence. "
        "Tasks where the control honored the fact without the Arche never required "
        "institutional knowledge and are dropped.\n"
    )
    lines.append("| task | Arm B adherence | verdict |")
    lines.append("|------|-----------------|---------|")
    for task in tasks:
        g = gate[task]
        verdict = "valid" if g["passed"] else "DROPPED (control honored the fact)"
        lines.append(f"| {task} | {g['arm_b_adherence']:.2f} | {verdict} |")
    lines.append("")

    lines.append("## Headline metrics (valid tasks only)\n")
    lines.append("| task | quality Δ (A−B) | token Δ (A−B) | step Δ (A−B) | Quality per 1k tok (A) | Quality per 1k tok (B) |")
    lines.append("|------|-----------------|---------------|--------------|------------------------|------------------------|")
    for task, h in sorted(headline["per_task"].items()):
        qp = h["quality_per_1k_tokens"]
        lines.append(
            f"| {task} | {h['quality_delta']:+.2f} | {h['token_delta']:+.0f} | "
            f"{h['step_delta']:+.1f} | {qp['a']:.3f} | {qp['b']:.3f} |"
        )
    p = headline["pooled"]
    lines.append(
        f"| **pooled** | {p['quality_delta']:+.2f} | {p['token_delta']:+.0f} | "
        f"{p['step_delta']:+.1f} | — | — |"
    )
    lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd benchmark && .venv/bin/python -m pytest tests/test_report.py -q`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add benchmark/analysis/report.py benchmark/tests/test_report.py
git commit -m "feat(benchmark): add markdown report renderer"
```

---

### Task 15: Analysis orchestrator (collect → judge → aggregate → report)

**Files:**
- Create: `benchmark/analysis/run_analysis.py`

**Interfaces:**
- Consumes: `collect_runs`, `judge`, `aggregate`, `report`; the committed `tasks/*/instruction.md` and `tasks/*/key_fact.md`; the Harbor `jobs/` output.
- Produces: `report/report.md` and a `report/judgments.json` cache keyed by `(arm, task, trial)` so re-runs don't re-spend on the judge. CLI: `python analysis/run_analysis.py [--jobs-dir jobs] [--arm-a arche-arm-a] [--arm-b arche-arm-b] [--passes 3]`.

- [ ] **Step 1: Write `benchmark/analysis/run_analysis.py`**

```python
"""End-to-end analysis: collect Harbor runs, judge blind, aggregate, report.

Judge results are cached in report/judgments.json keyed by (arm, task, trial) so
regenerating the report does not re-spend on the API. Delete the cache to re-judge.
"""

import argparse
import json
from pathlib import Path

import anthropic

from analysis import aggregate, report
from analysis.collect_runs import collect_runs
from analysis.judge import Verdict, judge

HERE = Path(__file__).resolve().parent.parent  # benchmark/
TASKS = HERE / "tasks"


def _load_task_text(task: str, name: str) -> str:
    return (TASKS / task / name).read_text()


def _cache_key(rec) -> str:
    return f"{rec['arm']}::{rec['task']}::{rec['trial']}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs-dir", default=str(HERE / "jobs"))
    ap.add_argument("--arm-a", default="arche-arm-a")
    ap.add_argument("--arm-b", default="arche-arm-b")
    ap.add_argument("--passes", type=int, default=3)
    args = ap.parse_args()

    jobs = Path(args.jobs_dir)
    records = collect_runs(jobs / args.arm_a, arm="a") + collect_runs(jobs / args.arm_b, arm="b")
    if not records:
        raise SystemExit(f"no run records found under {jobs}/{{{args.arm_a},{args.arm_b}}}")

    report_dir = HERE / "report"
    report_dir.mkdir(exist_ok=True)
    cache_path = report_dir / "judgments.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    client = anthropic.Anthropic()
    n_trials = max((r["trial"] for r in records), default=0)

    for rec in records:
        key = _cache_key(rec)
        if key in cache:
            v = Verdict(**cache[key])
        else:
            instruction = _load_task_text(rec["task"], "instruction.md")
            key_fact = _load_task_text(rec["task"], "key_fact.md")
            v = judge(client, instruction, rec["diff"], key_fact, passes=args.passes)
            cache[key] = v.model_dump()
            cache_path.write_text(json.dumps(cache, indent=2))  # persist incrementally
        rec.update(v.model_dump())

    cm = aggregate.cell_means(records)
    gate = aggregate.validity_gate(cm)
    valid = [t for t, g in gate.items() if g["passed"]]
    head = aggregate.headline(cm, valid)
    md = report.render_report(cm, gate, head, n_trials=n_trials)
    (report_dir / "report.md").write_text(md)
    print(f"wrote {report_dir / 'report.md'} ({len(records)} runs, {len(valid)} valid tasks)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test the wiring with a synthetic jobs dir (no API, no Docker)**

Run:
```bash
cd benchmark && .venv/bin/python - <<'PY'
import json, os, shutil, subprocess, sys
from pathlib import Path
root = Path("jobs_synth"); shutil.rmtree(root, ignore_errors=True)
sample = json.loads(Path("tests/fixtures/trajectory_sample.json").read_text())
def trial(job, name, task, diff):
    d = root/job/name; (d/"agent").mkdir(parents=True); (d/"verifier").mkdir(parents=True)
    (d/"agent"/"trajectory.json").write_text(json.dumps(sample))
    (d/"verifier"/"task_id.txt").write_text(task); (d/"verifier"/"final_diff.patch").write_text(diff)
    (d/"verifier"/"reward.txt").write_text("1")
trial("arche-arm-a","t1","task-1-concurrency","+ optimistic version check")
trial("arche-arm-b","t1","task-1-concurrency","+ SELECT ... FOR UPDATE")
# pre-seed the judge cache so no API call happens
rep = Path("report"); rep.mkdir(exist_ok=True)
Path(rep/"judgments.json").write_text(json.dumps({
 "a::task-1-concurrency::1": {"arche_fact_adherence":3,"domain_justification":3,"task_completion":3,"rationale":"x"},
 "b::task-1-concurrency::1": {"arche_fact_adherence":0,"domain_justification":1,"task_completion":3,"rationale":"y"}}))
r = subprocess.run([sys.executable,"analysis/run_analysis.py","--jobs-dir","jobs_synth"], capture_output=True, text=True)
print(r.stdout, r.stderr)
print("REPORT OK" if "wrote" in r.stdout and Path("report/report.md").exists() else "FAIL")
shutil.rmtree(root); Path("report/judgments.json").unlink(); Path("report/report.md").unlink()
PY
```
Expected: prints `wrote .../report.md (2 runs, 1 valid tasks)` and `REPORT OK`. (The pre-seeded cache means zero API calls.)

- [ ] **Step 3: Run the full analysis test suite**

Run: `cd benchmark && .venv/bin/python -m pytest -q`
Expected: PASS (all build + analysis tests green).

- [ ] **Step 4: Commit**

```bash
git add benchmark/analysis/run_analysis.py
git commit -m "feat(benchmark): add analysis orchestrator with judge caching"
```

---

### Task 16: Oracle verification (\$0 wiring check, both arms)

**Files:**
- (No new files) — runs Harbor against the built fixtures.

**Interfaces:**
- Consumes: `fixtures/arm-a`, `fixtures/arm-b` from Task 9; the oracle `solution/solve.sh` from Tasks 4–8.
- Produces: confidence that every task's environment builds, the oracle solution applies, and `tests/test.sh` writes `reward.txt`/`task_id.txt`/`final_diff.patch` — at `$0` model cost. This is gate 1 of 3.

- [ ] **Step 1: Ensure Docker is running and fixtures are fresh**

Run:
```bash
docker info >/dev/null 2>&1 && echo "docker ok"
cd benchmark && .venv/bin/python build_fixtures.py
```
Expected: `docker ok` and `built 10 task dirs`.

- [ ] **Step 2: Oracle-run Arm A**

Run:
```bash
cd benchmark && harbor run -p fixtures/arm-a -a oracle --job-name oracle-arm-a
```
Expected: Harbor builds each task image, runs `solve.sh`, then `tests/test.sh`; each trial reports reward 1. If a build fails or reward is 0, inspect `jobs/oracle-arm-a/<trial>/verifier/` and fix the offending `solve.sh`/`test.sh`, rebuild fixtures, and re-run.

- [ ] **Step 3: Oracle-run Arm B**

Run:
```bash
cd benchmark && harbor run -p fixtures/arm-b -a oracle --job-name oracle-arm-b
```
Expected: same — all rewards 1 (the oracle solution is arm-independent; only `.arche/`/`AGENTS.md` differ).

- [ ] **Step 4: Confirm the capture artifacts exist**

Run:
```bash
cd benchmark
find jobs/oracle-arm-a -name task_id.txt | wc -l          # expect 5
find jobs/oracle-arm-a -name final_diff.patch | wc -l     # expect 5
cat jobs/oracle-arm-a/*/verifier/reward.txt | sort | uniq -c
```
Expected: 5 `task_id.txt`, 5 `final_diff.patch`, and all rewards `1`.

- [ ] **Step 5: Record the oracle result (no commit needed — `jobs/` is gitignored)**

Note in the session that the oracle gate passed for both arms. Proceed to smoke.

---

### Task 17: Smoke run (1 task × 1 trial × 2 arms) and cost measurement

**Files:**
- (No new files) — real API spend begins here (small).

**Interfaces:**
- Consumes: `fixtures/arm-{a,b}`, `ANTHROPIC_API_KEY`.
- Produces: a *measured* cost-per-run and confirmation that `claude-code` runs, ATIF token capture works end-to-end through the parser, and the judge produces sane structured verdicts. This is gate 2 of 3.

- [ ] **Step 1: Confirm the key is set**

Run:
```bash
test -n "$ANTHROPIC_API_KEY" && echo "key set" || echo "SET ANTHROPIC_API_KEY FIRST"
```
Expected: `key set`. If not, ask the user to `export ANTHROPIC_API_KEY=...` (suggest `! export ...` is not persistent; they should set it in their shell). Do not proceed without it.

- [ ] **Step 2: Smoke-run one task, one trial, both arms**

Run:
```bash
cd benchmark
harbor run -p fixtures/arm-a -a claude-code -m anthropic/claude-sonnet-5 \
  -k 1 --include-task-name task-1-concurrency --job-name smoke-arm-a
harbor run -p fixtures/arm-b -a claude-code -m anthropic/claude-sonnet-5 \
  -k 1 --include-task-name task-1-concurrency --job-name smoke-arm-b
```
Expected: each completes one trial and writes `jobs/smoke-arm-*/<trial>/agent/trajectory.json`. If `--include-task-name` is not a supported flag on your Harbor version (confirm via `harbor run --help`), instead point `-p` at a temporary single-task folder: `mkdir -p smoke/arm-a && cp -r fixtures/arm-a/task-1-concurrency smoke/arm-a/ && harbor run -p smoke/arm-a ...`.

- [ ] **Step 3: Verify token capture parses and measure cost-per-run**

Run:
```bash
cd benchmark && .venv/bin/python - <<'PY'
from pathlib import Path
from analysis.parse_trajectory import parse_trajectory
costs = []
for t in Path("jobs").glob("smoke-arm-*/*/agent/trajectory.json"):
    m = parse_trajectory(t)
    costs.append(m["cost_usd"])
    print(t.parts[1], m["total_tokens"], f"${m['cost_usd']:.4f}")
if costs:
    avg = sum(costs)/len(costs)
    print(f"AVG cost/run ${avg:.4f} -> projected 50-run ${avg*50:.2f}")
PY
```
Expected: prints per-run tokens and cost, plus a projected 50-run dollar figure. If `cost_usd` is 0 for all runs, the ATIF file may not carry cost for this agent/provider — fall back to computing cost from tokens using the Sonnet 5 rates in the report, and note the discrepancy.

- [ ] **Step 4: Smoke-test the judge on the real smoke diffs**

Run:
```bash
cd benchmark && rm -f report/judgments.json && \
  .venv/bin/python analysis/run_analysis.py --arm-a smoke-arm-a --arm-b smoke-arm-b --passes 1
cat report/report.md
```
Expected: `run_analysis.py` collects the 2 smoke runs, calls the Opus 4.8 judge once each, writes `report/report.md`. Confirm the judge scored Arm A's adherence higher than Arm B's for task-1 (the expected direction). If the judge errors on `messages.parse`/`output_format`, adapt `judge_once` to your SDK version (see the note in Task 11) and re-run.

- [ ] **Step 5: Present the measured cost projection to the user for sign-off**

Report the measured average cost-per-run and the projected full-matrix (50-run) dollar figure, plus the ~3× judge cost (150 Opus passes). **Do not launch the full matrix without explicit dollar sign-off.** Delete smoke judge cache before the full run: `rm -f benchmark/report/judgments.json`.

---

### Task 18: Full matrix run and final report

**Files:**
- Create: `benchmark/report/report.md` (generated)

**Interfaces:**
- Consumes: explicit user sign-off on the projected cost, `fixtures/arm-{a,b}`, `ANTHROPIC_API_KEY`.
- Produces: the 50-run matrix, judged and aggregated into `report/report.md` with the validity gate applied. This is gate 3 of 3.

- [ ] **Step 1: Rebuild fixtures fresh (ensures no drift since smoke) and clean caches**

Run:
```bash
cd benchmark && .venv/bin/python build_fixtures.py && rm -f report/judgments.json report/report.md
```
Expected: `built 10 task dirs`.

- [ ] **Step 2: Run the full matrix — Arm A then Arm B (5 trials each)**

Run:
```bash
cd benchmark
harbor run -p fixtures/arm-a -a claude-code -m anthropic/claude-sonnet-5 -k 5 --job-name arche-arm-a
harbor run -p fixtures/arm-b -a claude-code -m anthropic/claude-sonnet-5 -k 5 --job-name arche-arm-b
```
Expected: 25 trials per arm (5 tasks × 5), each writing an ATIF trajectory. If a few trials error, note the count; the analysis tolerates missing trials (it indexes what exists).

- [ ] **Step 3: Run the analysis to judge, aggregate, and report**

Run:
```bash
cd benchmark && .venv/bin/python analysis/run_analysis.py --arm-a arche-arm-a --arm-b arche-arm-b --passes 3
```
Expected: prints `wrote .../report.md (N runs, M valid tasks)`. The judge caches to `report/judgments.json` so re-rendering is free.

- [ ] **Step 4: Read the report and apply the validity gate as a finding**

Run: `cat benchmark/report/report.md`
Expected: a report with per-cell means, the validity-gate verdict per task, and headline quality Δ / token Δ / quality-per-1k-tokens. Confirm:
- The **validity gate** section flags any task where Arm B honored the fact (those are dropped — a finding about the task, not the Arche).
- Per-task breakdown is present (it outranks the pooled average at n=5).
- The header states n=5 is directional, not significant.

If the validity gate drops most tasks, that means the control didn't need institutional knowledge — redesign those tasks' key facts to more strongly contradict the model's default, rebuild, and re-run (this is expected iteration, per the design spec's decision rules).

- [ ] **Step 5: Commit the report**

```bash
git add benchmark/report/report.md
# report/report.md is gitignored by default; force-add the final artifact to preserve it
git add -f benchmark/report/report.md
git commit -m "feat(benchmark): add final Arche A/B benchmark report"
```

> Optional follow-up (out of scope for the first run, per the spec's Non-Goals): a quality-vs-tokens scatter (arms colored) via the `dataviz` skill; an active `arche-query` third arm; multiple agent models. Do not build these unless the user asks.

---

## Self-Review

**Spec coverage** (against `docs/superpowers/specs/2026-07-07-arche-ab-benchmark-design.md`):

- §2 two-arm A/B, passive treatment, everything-else-held-constant → Tasks 9 (build A/B), 16–18 (identical run config per arm). ✅
- §2 data flow (seed → bake → strip → harbor ATIF → external analysis → report) → Tasks 3, 9, 16–18, 10–15. ✅
- §3 seed via real skills on authored raw docs, subscription-billing domain, committed `.arche/` → Tasks 2, 3. ✅
- §3 five tasks, each hinging on a different page type (ADR, domain rule, SME gotcha, superseded ADR, research) with hidden key facts → Tasks 4–8. ✅
- §4 token axis from ATIF (incl. step/tool-call count) → Task 10. Quality axis blind Opus 4.8 rubric (3 dims × 0–3), structured JSON, variance control → Task 11 (median-of-3 substitutes for temperature, which Opus 4.8 rejects). ✅
- §4 headline metrics (quality Δ, token Δ, quality-per-1k-tokens, step Δ) → Task 13. ✅
- §5 aggregation, **validity gate** (Arm B must fail fact-adherence), per-task-outranks-pooled, directional framing → Tasks 13, 14. ✅
- §6 Harbor + `ANTHROPIC_API_KEY` local Docker; oracle → smoke → sign-off → matrix cost gates → Tasks 0, 16, 17, 18. ✅
- §8 locked parameters (Sonnet 5 agent, Opus 4.8 judge, passive treatment, 5×5×2) → Global Constraints + Tasks 17–18. ✅

**Placeholder scan:** no TBDs; every code step ships complete code; every authored-content step ships full content; oracle/verification steps give exact commands and expected output. ✅

**Type consistency:** record shape `{task, arm, trial, diff, reward, prompt_tokens, completion_tokens, total_tokens, cached_tokens, cost_usd, steps, tool_calls}` is produced by `collect_runs` (Task 12), extended with `arche_fact_adherence/domain_justification/task_completion` by `run_analysis` (Task 15), and consumed by `aggregate` (Task 13). `Verdict` field names match across `judge.py`, `run_analysis.py`, and `aggregate.DIMENSIONS`. `parse_trajectory` output keys match what `collect_runs` spreads and what `aggregate`/`report` read. `TASK_ID`/`task_id.txt` is the single task-identity contract between `tests/test.sh` and `collect_runs`. ✅

**Known risk flagged for execution time (not a plan gap):** exact Harbor CLI flag spellings (`-k/--n-attempts`, `-p/--path`, `--include-task-name`, `--ae`) and whether the `claude-code` ATIF carries `cost_usd` are verified from source but should be confirmed against `harbor run --help` at Task 0 and re-checked at the smoke run (Task 17), which is why cost is *measured* before the 50-run spend rather than assumed.

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-09-arche-ab-benchmark.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
