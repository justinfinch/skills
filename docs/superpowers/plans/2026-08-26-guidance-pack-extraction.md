# Guidance Pack Extraction from unit-beat/core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Every pack task additionally REQUIRES the `write-guidance` skill** (invoke it via the Skill tool at task start; it lives at `skills/write-guidance/SKILL.md` in this repo). It carries the page template, the pack SKILL.md template, the attack table, and the counter-case gate. This plan supplies the *content* per pack; write-guidance supplies the *method*. Where this plan and that skill conflict, the skill wins.

**Goal:** Extract nine guidance packs from the unit-beat/core Arche (`/Users/justinfinch/Source/unit-beat/core/.arche/concepts/`) into this skills library, so future projects start from its architecture patterns.

**Architecture:** Each pack is a `guidance-<topic>/` skill under `skills/guidance/`, holding a thin `SKILL.md` (activation surface) and an OKF v0.2 `bundle/` of `Guidance` pages (plus `Concept` pages where content isn't a technique). One task per pack; each task is independently deliverable, conformance-checked, and committed.

**Tech Stack:** Markdown + YAML frontmatter (OKF v0.2); conformance via `devbox run check <bundle-dir>`; exemplar pack: `skills/guidance/guidance-ddd/`.

## Global Constraints

- Pack location: `skills/guidance/guidance-<slug>/` — matches the `guidance-ddd` neighbour. Directory name and `name:` frontmatter must match exactly.
- **Sanitize completely.** This library may be shared. No project identifiers anywhere in pack content: never `unitbeat`, `unit-beat`, `Unitbeat`, and no project domain vocabulary (`Walk`, `observation stream` as proper nouns, `Ledger-Green`, aggregate names). Cite evidence *shape*: "a field-operations product with an append-only event table and ~10 projections", "a project that first shipped X and superseded it with Y". Generic vocabulary: "capture event", "append-only event table", "read projection".
- Source material paths (read-only; never copied verbatim into packs): `/Users/justinfinch/Source/unit-beat/core/.arche/concepts/` — each task lists its exact source files.
- Frontmatter per page: `type: Guidance` (or `Concept`), `generated: { by: write-guidance/claude-fable-5, at: <actual UTC now> }`, never `verified`, `status: stable` when the counter-case gate passes (these extract from a production system), `status: draft` only if a named gap is stated in the body. Every Guidance page carries a concrete `stale_after` date (this plan seeds one per pack; adjust it if the Ford attack demands, don't delete it).
- Pack `SKILL.md` `description:` is a folded `>-` scalar, under 1024 chars, covering what + when in the domain's literal vocabulary, with a scope exclusion. No usage instructions in it.
- **Stack-bound packs declare their stack** in the description and as an explicit **Applies when** condition on each page — but keep the generic slug. Applies to Task 7 (React-ecosystem examples) and Task 8 (React/TypeScript recommendations).
- `bundle/index.md` frontmatter is exactly `okf_version: "0.2"`. Entries: `* [Title](concepts/<slug>.md) - <page description verbatim>.`
- Attacks: run at least Nygard (Failure modes), Ford (`stale_after`), Richards (Trade-offs) on every page. `Doesn't apply when` must contain checkable conditions — the seeds in each task below are the minimum, not the ceiling.
- Conformance gate per task: `devbox run check skills/guidance/guidance-<slug>/bundle` passes, plus a manual read for: relative links only (never `](/`), no `verified:` anywhere.
- README catalog: add one bullet per pack to the skills list in `README.md` (currently line 64, alongside `guidance-ddd`), same shape as the existing entries.
- Commit per task on branch `guidance-packs`. Commit messages end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Pack `SKILL.md` body: keep boilerplate items 2–4 of "How to use this pack" from the template verbatim in substance; item 1 is pack-specific reading order.

---

### Task 1: guidance-tenant-isolation

**Files:**
- Create: `skills/guidance/guidance-tenant-isolation/SKILL.md`
- Create: `skills/guidance/guidance-tenant-isolation/bundle/index.md`
- Create: `skills/guidance/guidance-tenant-isolation/bundle/concepts/rls-tenant-backstop.md`
- Create: `skills/guidance/guidance-tenant-isolation/bundle/concepts/narrowing-authorization-gates.md`
- Modify: `README.md` (catalog list, one bullet)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: pack slug `guidance-tenant-isolation`; page paths above (Task 9 greps and re-checks them).

- [ ] **Step 1: Invoke the `write-guidance` skill; read the source ADRs**

Read: `adr-tenant-isolation-and-authorization.md`, `adr-modular-auth-layer.md`, and the "Tenant isolation" bullet of `sad-unitbeat-core.md` `## Cross-cutting` (all under the source path in Global Constraints).

- [ ] **Step 2: Write `rls-tenant-backstop.md` (Guidance, `stale_after: 2028-09-01`)**

Technique: application-level tenant filters are the first line; Postgres Row-Level Security keyed on a per-transaction session variable (`SET LOCAL app.current_tenant`) is the database-level backstop that makes a cross-tenant read/write structurally impossible when a query forgets its filter. Background consumers set the tenant per unit of work from message metadata; `BYPASSRLS` is maintenance-only. Tables owned by an auth framework may need a *permissive* policy (framework logins exist before a tenant is chosen) while domain tables stay fail-closed — state both.
Seed conditions —
Applies when: multi-tenant rows share one database and every tenant-scoped table carries the tenant key; the database supports row-level policies; connections can guarantee per-transaction variables.
Doesn't apply when: isolation is already physical (database- or schema-per-tenant); the tenant key is not yet on every table (fix the schema first — RLS on half the tables is worse than none, it reads as covered); a pooler mode prevents reliable per-transaction session state.
Failure modes (Nygard): a forgotten `SET LOCAL` under fail-closed policy returns zero rows and presents as data loss, not as an auth error; auth-framework tables break login under fail-closed policy (evidence shape: a production system had to amend its policy to permissive for exactly those tables); a worker processing cross-tenant events with one connection leaks the previous event's tenant if the variable isn't reset.
Alternatives: app-layer filters only (wins when a single well-audited data-access layer owns every query); database-per-tenant (wins when compliance demands physical separation or tenants are few and large).

- [ ] **Step 3: Write `narrowing-authorization-gates.md` (Guidance, `stale_after: 2028-09-01`)**

Technique: compose authorization above the tenant boundary as strictly-narrowing gates (tenant ⊃ reachable subgraph ⊃ specific grant) evaluated by a single evaluator; resolve the reachable set once per request. This catches what RLS structurally cannot: over-sharing *within* a tenant.
Seed conditions —
Applies when: access follows a containment structure (location trees, org hierarchies); more than one permission granularity exists.
Doesn't apply when: flat roles fully describe access (a single evaluator is then indirection with no second gate); permissions are per-resource ACL grants with no containment to narrow through.
Failure modes: a traversal bug over-shares inside the tenant and no tenant-level control notices — pair the evaluator with a within-tenant isolation test; queries that bypass the evaluator "because they know the answer".

- [ ] **Step 4: Run the attacks on both pages; write `SKILL.md` and `bundle/index.md`**

Description seed (rework into the folded scalar): multi-tenant isolation and authorization — Postgres RLS as a database-level tenant backstop behind application filters, per-transaction tenant context, permissive-vs-fail-closed policy choice for auth-framework tables, and strictly-narrowing authorization gates through a single evaluator for within-tenant access. Trigger moments: designing a multi-tenant schema, adding `tenant_id`/`organization_id` columns, "how do we stop cross-tenant leaks", reviewing authorization for hierarchical access. Scope exclusion: not an authentication-provider comparison; not row-level *encryption* or residency.

- [ ] **Step 5: Verify conformance**

Run: `devbox run check skills/guidance/guidance-tenant-isolation/bundle`
Expected: PASS. Then read for relative links, no `verified:`, no project identifiers.

- [ ] **Step 6: Add README catalog bullet; commit**

```bash
git add skills/guidance/guidance-tenant-isolation README.md
git commit -m "Add guidance-tenant-isolation pack"
```

---

### Task 2: guidance-event-delivery

**Files:**
- Create: `skills/guidance/guidance-event-delivery/SKILL.md`
- Create: `skills/guidance/guidance-event-delivery/bundle/index.md`
- Create: `skills/guidance/guidance-event-delivery/bundle/concepts/transactional-outbox.md`
- Create: `skills/guidance/guidance-event-delivery/bundle/concepts/relay-to-broker-dispatch.md`
- Create: `skills/guidance/guidance-event-delivery/bundle/concepts/end-to-end-idempotency.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing. Produces: pack slug + page paths for Task 9.

- [ ] **Step 1: Invoke `write-guidance`; read the source ADRs — including all three superseded ones**

Read: `adr-transactional-outbox.md`, `adr-jetstream-dispatch.md`, `adr-nats-jetstream-broker.md`, `adr-feed-delivery-and-projection-dispatch.md`, and the superseded `adr-walk-as-publishable-event.md`, `adr-outbox-dispatch.md`, `adr-nats-jetstream-migration-trigger.md`. The supersession trail (row-state-as-event → outbox-as-log over `pg_notify` + per-consumer cursors → corrected to canonical relay → broker, broker adopted at v1) is the pack's failure-mode evidence. Cite its shape, not its ADR names.

- [ ] **Step 2: Write `transactional-outbox.md` (Guidance, `stale_after: 2029-01-01`)**

Technique: write the aggregate change and an outbox row in the same transaction; a single relay claims rows (`FOR UPDATE SKIP LOCKED`), publishes with the outbox row id as the broker message id, then marks them done. Publication cannot diverge from state.
Applies when: a state change and its event must not diverge; the system of record is a relational store; at-least-once delivery is acceptable downstream.
Doesn't apply when: the event store *is* the system of record (event sourcing — an outbox duplicates it); a single consumer in the same database can just read the source table; loss of an occasional event is genuinely acceptable (then a post-commit publish is simpler and honest about it).
Failure modes: relay lag under burst load (outbox depth is the metric to alarm on); unbounded outbox growth without a cleanup policy; **outbox-as-log** — keeping rows forever and giving each consumer a cursor into the table, which re-implements a broker inside the database and couples every consumer to it (evidence shape: a production system shipped exactly this and corrected it within weeks).

- [ ] **Step 3: Write `relay-to-broker-dispatch.md` (Guidance, `stale_after: 2029-01-01`)**

Technique: one relay publishes; a broker (durable stream) fans out; consumers are independent durable subscriptions (projection workers, push pumps) that each track their own position in the broker, not in the source database.
Applies when: two or more consumers with independent pace/failure domains; replay is required.
Doesn't apply when: one consumer and no replay requirement (call it directly or poll the table — a broker is operational surface with no fan-out to pay for it); the team cannot operate another stateful system and consumer count is stable at one or two (database LISTEN/NOTIFY + a polling cursor covers the gap — but name the threshold that forces the move).
Failure modes: broker adopted "for later" and running unexercised; migration triggers written to defer a broker that was adopted at v1 anyway weeks later (evidence shape — deferral triggers can fire immediately; writing them down is still what made the reversal cheap).

- [ ] **Step 4: Write `end-to-end-idempotency.md` (Guidance, `stale_after: 2029-01-01`)**

Technique: one identity travels the whole path — client-generated UUID at capture, unique dedup key at ingestion, broker publisher-dedup window keyed on the same id, consumers idempotent on it. Assume at-least-once at every hop.
Applies when: any hop can retry (mobile clients, at-least-once brokers, replayed streams).
Doesn't apply when: every operation is naturally idempotent by construction (keyed upserts) — explicit dedup machinery then adds state for nothing; when the actual requirement is ordering, which dedup does not provide.
Failure modes: dedup at one hop only (client retries still double-write past a broker-only window); dedup windows sized shorter than the longest realistic retry gap.

- [ ] **Step 5: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: reliable event delivery from a relational system of record — transactional outbox, single relay to a durable broker, independent durable consumers, end-to-end idempotency keys, and when database LISTEN/NOTIFY is enough versus when a broker earns its keep. Triggers: "how do we publish events without losing them", dual-write worries, choosing between Postgres notify and a message broker, consumers seeing duplicates. Exclusion: not event sourcing as a persistence model; not broker product comparison.

- [ ] **Step 6: Verify conformance; commit**

Run: `devbox run check skills/guidance/guidance-event-delivery/bundle` → PASS; manual read; README bullet.
```bash
git add skills/guidance/guidance-event-delivery README.md
git commit -m "Add guidance-event-delivery pack"
```

---

### Task 3: guidance-fitness-functions

**Files:**
- Create: `skills/guidance/guidance-fitness-functions/SKILL.md`
- Create: `skills/guidance/guidance-fitness-functions/bundle/index.md`
- Create: `skills/guidance/guidance-fitness-functions/bundle/concepts/architectural-fitness-functions.md` (Guidance)
- Create: `skills/guidance/guidance-fitness-functions/bundle/concepts/fitness-function-registry.md` (Concept)
- Modify: `README.md`

**Interfaces:** Consumes nothing. Produces pack slug + page paths for Task 9.

- [ ] **Step 1: Invoke `write-guidance`; read sources**

Read: `sad-unitbeat-core.md` `## Fitness functions` (including the Registry table), `sad-experience.md` `## Fitness functions`, plus the fitness-function mentions inside `adr-cqrs-lite-command-query-separation.md` (query-↛-domain), `adr-api-endpoint-repr-pattern.md` (no-inline-handlers), `adr-design-token-architecture.md` (semantic-tokens-only), `adr-immutable-observation-stream.md` (append-only role).

- [ ] **Step 2: Write `architectural-fitness-functions.md` (Guidance, `stale_after: 2029-06-01`)**

Technique: every load-bearing architectural decision names, at decision time, the executable check that detects its violation; checks run in CI in two lanes — static (dependency-direction rules, privilege lint) on every PR, integration (DB-privilege probes, cross-tenant probes, rebuild-time budgets) on every PR or nightly when slow. Tripping one means an architectural regression, not a flaky test — that sentence is the contract.
Applies when: the decision has a structural expression a machine can check (dependency direction, DB grants, schema properties, file placement); CI exists; code is written by more hands than made the decision — emphatically including coding agents.
Doesn't apply when: the decision has no mechanically checkable expression (vendor choice, naming taste) — a check would test something adjacent and rot; when the only possible check is so slow or flaky the team learns to ignore it (move it to a nightly lane or don't write it).
Failure modes: checks skipped-to-green under deadline (a skipped fitness function is a silently revoked decision); the check pins implementation detail rather than the decision, so refactors trip it and erode trust; registry says active for checks that no longer run.
Trade-offs (Richards): decisions stay enforced without review vigilance ↔ every architectural change now has two artifacts to update, and a wrong check is worse than none.

- [ ] **Step 3: Write `fitness-function-registry.md` (Concept — no six sections)**

The registry shape: one table in the architecture document — check name, enforced-by (exact script/test path), lane (static / integration / nightly), status (active ✅ / pending-milestone ⏳ / deferred ⏸ with the milestone named). Deferred entries are commitments with a date, not aspirations. Include a filled example table with sanitized generic entries.

- [ ] **Step 4: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: architectural fitness functions — encoding each load-bearing decision (dependency direction, database privileges, tenant isolation, rebuild budgets) as a named CI check with static and integration lanes, plus the registry that tracks name, enforcement point, lane, and status. Triggers: "how do we stop the architecture eroding", ADRs that get violated silently, enforcing layer boundaries with agents writing the code, dependency-cruiser/ArchUnit-style rules. Exclusion: not general test strategy or coverage practice.

- [ ] **Step 5: Verify conformance; commit**

`devbox run check skills/guidance/guidance-fitness-functions/bundle` → PASS; README bullet.
```bash
git add skills/guidance/guidance-fitness-functions README.md
git commit -m "Add guidance-fitness-functions pack"
```

---

### Task 4: guidance-cqrs-projections

**Files:**
- Create: `skills/guidance/guidance-cqrs-projections/SKILL.md`
- Create: `skills/guidance/guidance-cqrs-projections/bundle/index.md`
- Create: `skills/guidance/guidance-cqrs-projections/bundle/concepts/cqrs-lite.md`
- Create: `skills/guidance/guidance-cqrs-projections/bundle/concepts/rebuildable-projections.md`
- Create: `skills/guidance/guidance-cqrs-projections/bundle/concepts/append-only-source-stream.md`
- Modify: `README.md`

**Interfaces:** Consumes: `guidance-ddd` exists — `cqrs-lite.md` may cite `guidance-ddd/concepts/aggregate-boundaries.md` as the strategic prerequisite (relative cross-pack citation is by pack-qualified path in prose, not a markdown link — links must stay within the bundle). Produces pack slug + page paths for Task 9.

- [ ] **Step 1: Invoke `write-guidance`; read sources**

Read: `adr-cqrs-lite-command-query-separation.md`, `adr-ledger-entries-as-projections.md`, `adr-immutable-observation-stream.md`, `adr-availability-and-durability-targets.md`.

- [ ] **Step 2: Write `cqrs-lite.md` (Guidance, `stale_after: 2029-06-01`)**

Technique: three models over one database — command side with a full domain model and unit-of-work (transaction = aggregate = outbox append), projection side, and thin DTO queries that never touch the domain model; plain handler functions, no command bus; hydrate the aggregate richly only where invariants demand it, thin append otherwise; reads are eventually consistent with read-your-writes restored by an optimistic client echo. Enforce query-↛-domain with a dependency rule.
Doesn't apply when: read shape ≈ write shape (plain CRUD — three models is ceremony); reads must be strictly consistent and no echo trick is acceptable; the team actually needs separate read stores (that's full CQRS, different cost profile).
Failure modes: the query side quietly importing domain code until separation is fiction (the dependency rule exists because this *will* happen); commands growing return values that make callers treat them as queries.

- [ ] **Step 3: Write `rebuildable-projections.md` (Guidance, `stale_after: 2029-06-01`)**

Technique: derived read tables are written only by projection workers, versioned with a `projector_version`, and carry a rebuild guarantee with an explicit time budget verified in CI. Durability targets split deliberately: the source stream gets the strong number, projections get **zero** — rebuildable-within-budget replaces backed-up.
Applies when: an authoritative event/observation stream exists and is retained in full.
Doesn't apply when: source events are pruned or were never complete (a projection you cannot rebuild is a primary store wearing a costume — give it real durability targets); rebuild time exceeds tolerable staleness and no incremental path exists.
Failure modes: rebuild budget silently blown as data grows (the nightly rebuild check is the alarm); the projection path acquiring write access to the source (enforce at DB-role level); hand-edits to projection rows that vanish on rebuild.

- [ ] **Step 4: Write `append-only-source-stream.md` (Guidance, `stale_after: 2029-06-01`)**

Technique: enforce append-only at the database-role level — the writing role has only `INSERT` on the stream table; `UPDATE`/`DELETE` revoked; corrections are new events; client-generated UUIDs as dedup keys; large payloads (media) referenced, never embedded.
Doesn't apply when: legal erasure obligations require destroying rows in place and no redaction-by-reference design exists; the table is not actually a source of record.
Failure modes: "just this one fix" migrations that bypass the role; blob payloads bloating the stream until replay is impractical.

- [ ] **Step 5: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: command–query separation on a single database — three models (command with unit-of-work, projection, thin DTO query), conditional aggregate hydration, rebuildable read projections with zero durability targets and a CI'd rebuild budget, append-only source streams enforced at the DB-role level, eventual read-your-writes via optimistic echo. Triggers: "reads are getting slow/complex", designing read models or feeds, event-sourcing-versus-CRUD debates, "can we rebuild this table". Exclusion: not full CQRS with separate stores; strategic aggregate sizing lives in guidance-ddd.

- [ ] **Step 6: Verify conformance; commit**

`devbox run check skills/guidance/guidance-cqrs-projections/bundle` → PASS; README bullet.
```bash
git add skills/guidance/guidance-cqrs-projections README.md
git commit -m "Add guidance-cqrs-projections pack"
```

---

### Task 5: guidance-vertical-slices

**Files:**
- Create: `skills/guidance/guidance-vertical-slices/SKILL.md`
- Create: `skills/guidance/guidance-vertical-slices/bundle/index.md`
- Create: `skills/guidance/guidance-vertical-slices/bundle/concepts/repr-endpoints.md`
- Create: `skills/guidance/guidance-vertical-slices/bundle/concepts/feature-folder-organization.md`
- Modify: `README.md`

**Interfaces:** Consumes nothing. Produces pack slug + page paths for Task 9.

- [ ] **Step 1: Invoke `write-guidance`; read sources**

Read: `adr-api-endpoint-repr-pattern.md`, `adr-frontend-feature-organization.md`. Note the explicit parallel the frontend ADR draws to the API pattern — that parallel (one principle, two layers) is the pack's through-line.

- [ ] **Step 2: Write `repr-endpoints.md` (Guidance, `stale_after: 2028-09-01`)**

Technique: one directory per endpoint holding request schema (validated at the boundary), a thin handler that invokes exactly one command or query, and a response DTO; a `defineEndpoint`/`registerEndpoints` helper wires them — a registration convenience, explicitly **not** a command bus (no middleware pipeline, no dispatch indirection); dependencies injected at registration; the app composition file registers endpoints and nothing else, enforceable as a no-inline-handlers check.
Doesn't apply when: the API is a handful of endpoints where a single routes file is fully legible; the framework's own controller idiom already gives one-file-per-endpoint (imposing a second convention on top adds nothing); an actual mediator/command-bus is in use (then the bus's conventions own this).
Failure modes: the registration helper accreting behavior until it *is* an undeclared command bus; handlers growing business logic because "it's just one line more".

- [ ] **Step 3: Write `feature-folder-organization.md` (Guidance, `stale_after: 2028-09-01`)**

Technique: organize app code by feature (`features/<name>/`), with a shared tier for cross-feature code; the sorting rule is checkable — knows-business-logic → feature, dumb-visual → shared; features are non-importing peers; direction-only import boundaries enforced by a dependency tool, not by review. Present it as the presentation-layer twin of REPR: same principle — slice by capability, keep slices from importing each other — applied to another layer.
Doesn't apply when: the app is small enough that layer folders stay legible end-to-end; a full formal methodology (e.g. FSD) is already adopted — mixing two taxonomies is worse than either.
Failure modes: the shared tier becoming a dumping ground (the sorting rule exists to be applied at review, and a shared component that knows business vocabulary is mis-filed); cross-feature imports "temporarily" allowed and never removed — which is why the boundary is tooling-enforced.

- [ ] **Step 4: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: vertical-slice organization at two layers — REPR (Request–EndPoint–Response) endpoint slices with schema-validated boundaries and thin handlers on the API side; by-feature folder taxonomy with a knows-business-logic sorting rule and tool-enforced, direction-only import boundaries on the frontend side. Triggers: "how should we organize endpoints/components", route files or controllers growing unwieldy, features importing each other, vertical slice architecture, dependency-cruiser/import-boundary rules. Exclusion: not service granularity (that is a deployment question); not a framework recommendation.

- [ ] **Step 5: Verify conformance; commit**

`devbox run check skills/guidance/guidance-vertical-slices/bundle` → PASS; README bullet.
```bash
git add skills/guidance/guidance-vertical-slices README.md
git commit -m "Add guidance-vertical-slices pack"
```

---

### Task 6: guidance-portability-seams

**Files:**
- Create: `skills/guidance/guidance-portability-seams/SKILL.md`
- Create: `skills/guidance/guidance-portability-seams/bundle/index.md`
- Create: `skills/guidance/guidance-portability-seams/bundle/concepts/named-migration-triggers.md`
- Create: `skills/guidance/guidance-portability-seams/bundle/concepts/standard-api-seams.md`
- Modify: `README.md`

**Interfaces:** Consumes nothing. Produces pack slug + page paths for Task 9.

- [ ] **Step 1: Invoke `write-guidance`; read sources**

Read: `adr-cloud-platform.md`, `adr-local-object-store-double.md`, `adr-modular-auth-layer.md`, the migration-trigger legs of `adr-feed-delivery-and-projection-dispatch.md`, and superseded `adr-nats-jetstream-migration-trigger.md` (a trigger that "fired" by the technology being adopted at v1 instead — counter-case material).

- [ ] **Step 2: Write `named-migration-triggers.md` (Guidance, `stale_after: 2028-09-01`)**

Technique: when committing all-in to a platform or product, the same decision names (a) the escape valve — the specific alternative you would move to — and (b) per-layer triggers: observable thresholds (cost, latency, feature gap, consumer count) that reopen the decision. Triggers are facts someone can measure, not vibes; hitting one produces a new decision record, not an automatic migration.
Applies when: the commitment is expensive to reverse and the platform market is live enough that the calculus can shift.
Doesn't apply when: the commitment is cheap to reverse anyway (a trigger is ceremony); when trigger-writing becomes a way to *avoid* a decision that is actually cheap to make now — evidence shape: a project wrote adoption triggers to defer a message broker, then adopted it at v1 weeks later; the written trigger made the reversal cheap, but the honest lesson is the deferral was the wrong call.
Failure modes: triggers written and never measured (an unmonitored trigger is a comment); escape valve named but never exercised, so the seam has silently rusted shut.

- [ ] **Step 3: Write `standard-api-seams.md` (Guidance, `stale_after: 2028-09-01`)**

Technique: make the *commodity API*, not the vendor, the architectural seam — e.g. the S3 API for object storage (local double ↔ cloud interop ↔ alternative provider), a provider interface owned by the domain layer for auth. The local development double must honor the same seam; choose doubles by upstream health, not popularity (evidence shape: the most popular S3 double was rejected for a stalled upstream in favor of a maintained one).
Doesn't apply when: the differentiating value you're buying *is* the proprietary API surface (using a database as a queue-with-standard-API when you chose it for its unique features); when the standard API is a least-common-denominator that forfeits the capability that justified the dependency.
Failure modes: seam erosion — proprietary parameters leaking through "just this once" until the seam is decorative; a double that drifts behaviorally from production (checksum, presign semantics) so local green means nothing.

- [ ] **Step 4: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: keeping expensive platform commitments reversible — named escape valves with per-layer, measurable migration triggers decided at commitment time, and commodity-standard APIs (S3-compatible storage, provider interfaces) as the seam between the system and the vendor, with local doubles that honor the same seam. Triggers: choosing a cloud platform or managed service, "are we locked in", vendor lock-in review, picking a local development stand-in for a cloud service. Exclusion: not a multi-cloud advocacy piece; not a cloud-provider comparison.

- [ ] **Step 5: Verify conformance; commit**

`devbox run check skills/guidance/guidance-portability-seams/bundle` → PASS; README bullet.
```bash
git add skills/guidance/guidance-portability-seams README.md
git commit -m "Add guidance-portability-seams pack"
```

---

### Task 7: guidance-cross-platform-ui

**Files:**
- Create: `skills/guidance/guidance-cross-platform-ui/SKILL.md`
- Create: `skills/guidance/guidance-cross-platform-ui/bundle/index.md`
- Create: `skills/guidance/guidance-cross-platform-ui/bundle/concepts/tokens-plus-headless-logic.md`
- Create: `skills/guidance/guidance-cross-platform-ui/bundle/concepts/two-tier-design-tokens.md`
- Modify: `README.md`

**Interfaces:** Consumes nothing. Produces pack slug + page paths for Task 9.
**Stack note:** examples are React / React Native / Tailwind; the *reasoning* is general. Declare the ecosystem in the description; `tokens-plus-headless-logic.md` carries a "component model with a headless/render split (React, Vue, …)" Applies-when condition; `two-tier-design-tokens.md` is stack-agnostic and says so.

- [ ] **Step 1: Invoke `write-guidance`; read sources**

Read: `adr-cross-platform-ui-strategy.md`, `adr-design-token-architecture.md`, `sad-experience.md` (Logical view + Fitness functions).

- [ ] **Step 2: Write `tokens-plus-headless-logic.md` (Guidance, `stale_after: 2027-09-01`)**

Technique: share the two layers that transfer cleanly — design tokens and render-free logic (state machines, hooks, view-models) — and own a separate render stack per platform (web components on web idioms, native components on native idioms): one language, two dialects. Explicitly rejects universal-component frameworks that render one component tree everywhere.
Applies when: shipping web + native from one team; a component model that supports a headless/render split; platform feel matters to the product.
Doesn't apply when: the app is a thin content viewer where a webview or universal renderer is honestly good enough — per-platform render stacks are double the surface, and that cost needs platform-feel revenue to justify; when the team lacks capacity to maintain two render stacks (the universal framework's compromise beats an abandoned platform).
Failure modes: the "shared logic" layer sprouting render imports until the split is fiction (enforce with a boundary check); tokens forked per platform "temporarily"; the two dialects drifting into two languages without a shared design review.

- [ ] **Step 3: Write `two-tier-design-tokens.md` (Guidance, `stale_after: 2028-03-01`)**

Technique: two tiers — a primitive scale (raw values: color ramps, spacing, type scale) and semantic aliases (intent: `surface`, `accent`, `danger`) — with a hard rule that components consume semantic tokens only, enforceable by lint; hand-author the theme now, keep it transformable (Style-Dictionary-shaped) for when more targets appear.
Doesn't apply when: a single-platform app with a bought theme it will never rebrand (two tiers is indirection with one consumer); when a design team already ships tokens from a tool — consume theirs, don't build a parallel system.
Failure modes: primitives leaking into components one hex code at a time until theming is a grep exercise; semantic vocabulary growing a synonym per author without a naming gate.

- [ ] **Step 4: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: cross-platform UI without a universal renderer — share design tokens and headless (render-free) logic, own separate per-platform render stacks (one language, two dialects), and structure tokens as primitive scale plus semantic aliases with components consuming semantic only. Examples assume a React/React Native/Tailwind ecosystem; the layering reasoning is stack-agnostic. Triggers: "web and mobile from one codebase", evaluating universal-component frameworks, setting up design tokens or theming, brand refresh requiring re-skinning. Exclusion: not a visual design language; not native-vs-cross-platform app-strategy advice.

- [ ] **Step 5: Verify conformance; commit**

`devbox run check skills/guidance/guidance-cross-platform-ui/bundle` → PASS; README bullet.
```bash
git add skills/guidance/guidance-cross-platform-ui README.md
git commit -m "Add guidance-cross-platform-ui pack"
```

---

### Task 8: guidance-client-state

**Files:**
- Create: `skills/guidance/guidance-client-state/SKILL.md`
- Create: `skills/guidance/guidance-client-state/bundle/index.md`
- Create: `skills/guidance/guidance-client-state/bundle/concepts/client-state-taxonomy.md`
- Create: `skills/guidance/guidance-client-state/bundle/concepts/store-and-forward-capture.md`
- Modify: `README.md`

**Interfaces:** Consumes: `guidance-cqrs-projections` pages exist (Task 4) — the taxonomy page's real-time-patching section is the client home of that pack's optimistic echo; cite by pack-qualified path in prose. Produces pack slug + page paths for Task 9.
**Stack note:** this pack's recommendations are stack-bound (React/TypeScript; TanStack Query, Zustand). Generic slug per the write-guidance convention; the description says "in React/TypeScript apps" and names the libraries (they double as triggers); every page carries "Applies when: React application" as its first condition. Body states which parts transfer to other ecosystems (the taxonomy; the scoped-resiliency move) and which to re-derive (library choices).

- [ ] **Step 1: Invoke `write-guidance`; read sources**

Read: `adr-client-and-server-state.md`, `adr-capture-path-resiliency.md`, `sad-experience.md` (Process view).

- [ ] **Step 2: Write `client-state-taxonomy.md` (Guidance, `stale_after: 2027-09-01`)**

Technique: four kinds of client state, each with its own store, never one store for all — (1) server cache: a query library (TanStack Query) owning fetching, staleness, invalidation; (2) ephemeral UI state: a light store (Zustand) or component state; (3) durable pending writes: a purpose-built persistent queue, *not* the query library's mutation cache; (4) real-time updates: push events (SSE/WebSocket) patch the query cache directly — which is where an eventually-consistent backend's optimistic read-your-writes echo lives on the client.
Applies when: React/TypeScript application against a remote API.
Doesn't apply when: server state is trivially small and read-once (a query library is machinery without a cache problem); a full local-first sync engine is in use (the sync engine *is* the taxonomy then — don't layer both).
Failure modes: server data copied into the UI store "for convenience" and going permanently stale (the classic global-store-for-everything failure this taxonomy exists to prevent); push patches and refetches fighting over the same cache keys without an ownership rule.

- [ ] **Step 3: Write `store-and-forward-capture.md` (Guidance, `stale_after: 2028-03-01`)**

Technique: scope the offline promise to the critical write path — a durable local queue for captured writes that survives process death and drains on connectivity, plus a session-scoped read-only cache for the workflow in flight — and explicitly *decline* general offline mode. The narrowing is the technique: name the one workflow that must survive dead connectivity, make writes on that path unlosable, let everything else fail visibly.
Applies when: one identifiable field workflow performs writes under unreliable connectivity; losing a captured write is unacceptable while a stale read is tolerable.
Doesn't apply when: users must *browse* arbitrary data offline (that is real offline mode — a sync engine, a different cost class); connectivity is reliable enough that a failed write with a retry button is honest UX.
Failure modes: the queue silently growing when drain fails (surface depth to the user; an invisible queue converts an outage into data loss discovered weeks later); the read-only session cache quietly accreting write features until an accidental, unowned sync engine exists.

- [ ] **Step 4: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: client state in React/TypeScript apps — a four-way taxonomy (server cache via TanStack Query, ephemeral UI state via Zustand or component state, a durable capture queue for pending writes, SSE/WebSocket patches into the query cache for real-time and read-your-writes), plus store-and-forward capture as a deliberately narrower promise than offline mode. Triggers: "where does this state live", choosing Redux vs Query vs Zustand, stale data after mutations, field/mobile capture that must survive dead connectivity, "do we need offline mode". Exclusion: not local-first sync engines; not server-side caching.

- [ ] **Step 5: Verify conformance; commit**

`devbox run check skills/guidance/guidance-client-state/bundle` → PASS; README bullet.
```bash
git add skills/guidance/guidance-client-state README.md
git commit -m "Add guidance-client-state pack"
```

---

### Task 9: guidance-monorepo

**Files:**
- Create: `skills/guidance/guidance-monorepo/SKILL.md`
- Create: `skills/guidance/guidance-monorepo/bundle/index.md`
- Create: `skills/guidance/guidance-monorepo/bundle/concepts/domain-centered-workspace.md`
- Create: `skills/guidance/guidance-monorepo/bundle/concepts/single-language-end-to-end.md`
- Modify: `README.md`

**Interfaces:** Consumes nothing. Produces pack slug + page paths for Task 10. Seams to respect: intra-app folder taxonomy belongs to `guidance-vertical-slices`; what the domain model contains belongs to `guidance-ddd`; this pack owns only the workspace topology and the language bet.
**Stack note:** examples are TypeScript/pnpm/Turborepo; the topology reasoning is stack-agnostic — declare the ecosystem in the description, keep the generic slug. Deliberately out of scope (state as the exclusion): package-manager and build-tool comparison (commodity, fast-decaying), dev-environment tooling (devbox/direnv — workflow skills, not knowledge).

- [ ] **Step 1: Invoke `write-guidance`; read sources**

Read: `adr-monorepo-structure-and-language.md`, `sad-unitbeat-core.md` `## Logical view`.

- [ ] **Step 2: Write `domain-centered-workspace.md` (Guidance, `stale_after: 2028-03-01`)**

Technique: split the workspace into apps (deployables, at the edge) and packages (libraries), with the *domain* package at the dependency center — packages point inward toward domain, domain imports nothing app- or infrastructure-flavored, apps only compose; import direction enforced by tooling, builds orchestrated by a task-graph runner keyed on the workspace graph.
Applies when: two or more deployables share a business core; the teams involved share a release cadence; the language has first-class workspace tooling.
Doesn't apply when: a single deployable exists (a workspace is ceremony — folders suffice until the second app is real, and the tempting version of this mistake is scaffolding packages for apps that are only planned); teams need independent release cadence and ownership boundaries (a polyrepo or strict internal versioning wins); packages are published to external semver consumers (versioning discipline changes the calculus entirely).
Failure modes: a `shared`/`utils` package sitting at the center instead of domain, becoming a dependency magnet every package couples through; the domain package quietly importing infrastructure until the center is decorative (this is a fitness-function candidate — cross-reference the enforcement idea, own the topology claim); task-graph caches poisoned by nondeterministic build steps, so "cached green" stops meaning anything.
Trade-offs (Richards): atomic cross-cutting changes and one dependency graph ↔ one shared toolchain version for everyone, CI that must scale with the graph, and a blast radius that grows with every package pointed at the center.

- [ ] **Step 3: Write `single-language-end-to-end.md` (Guidance, `stale_after: 2028-03-01`)**

Technique: one language across API, workers, and clients so domain types and validation schemas travel from the database boundary to the UI without translation layers — the domain-centered workspace is what makes the shared types real rather than copy-pasted.
Applies when: a small team owns the whole surface; the product spans client and server; the language's ecosystem genuinely covers every runtime need in view.
Doesn't apply when: a workload has a decisive ecosystem elsewhere (ML in Python, high-performance systems components) — a translation layer at one seam costs less than exiling the workload from its ecosystem; the team's existing strength is genuinely polyglot and retraining costs more than the translation layers the single language would remove.
Failure modes: the claim eroding one "temporary exception" service at a time with no decision record marking the erosion; shared type packages leaking server-only concerns (secrets, heavy dependencies) into client bundles.

- [ ] **Step 4: Attacks; `SKILL.md` + `bundle/index.md`**

Description seed: monorepo workspace topology — the apps/packages split with the domain package at the dependency center, inward-pointing import direction, task-graph build orchestration, and the single-language-end-to-end bet that lets domain types and validation schemas travel from database to UI without translation layers. Examples assume TypeScript with pnpm and Turborepo; the topology reasoning is stack-agnostic. Triggers: "setting up a monorepo", "how should we structure packages", monorepo versus polyrepo, sharing types between backend and frontend, "should everything be TypeScript". Exclusion: not a package-manager or build-tool comparison; intra-app folder structure lives in guidance-vertical-slices.

- [ ] **Step 5: Verify conformance; commit**

`devbox run check skills/guidance/guidance-monorepo/bundle` → PASS; README bullet.
```bash
git add skills/guidance/guidance-monorepo README.md
git commit -m "Add guidance-monorepo pack"
```

---

### Task 10: Cross-pack review and final gate

**Files:**
- Modify: any pack file the review flags; `README.md` if entries drifted from the shared shape.

**Interfaces:** Consumes: all nine pack slugs and page paths from Tasks 1–9.

- [ ] **Step 1: Sanitization sweep**

Run: `grep -ri -E 'unitbeat|unit-beat' skills/guidance/ && echo LEAK || echo CLEAN`
Expected: `CLEAN`. Also grep for project domain vocabulary that slipped through: `grep -rniE '\b(walk|observation stream|ledger-green)\b' skills/guidance/` and judge each hit in context (generic uses of "walk" are fine; the product's proper nouns are not).

- [ ] **Step 2: Conformance across all bundles**

Run: `for d in skills/guidance/guidance-*/bundle; do devbox run check "$d" || echo "FAIL: $d"; done`
Expected: no `FAIL` lines.

- [ ] **Step 3: Trigger-overlap read**

Read all ten pack descriptions (the nine new plus `guidance-ddd`) side by side: `grep -A20 '^description' skills/guidance/guidance-*/SKILL.md`. Check that no two descriptions claim the same decision moment as their primary trigger (known seams to verify: aggregate sizing belongs to guidance-ddd, not guidance-cqrs-projections; migration triggers belong to guidance-portability-seams, with guidance-event-delivery only referencing the graduation threshold; the SSE cache-patching moment belongs to guidance-client-state, with guidance-cqrs-projections owning the server side of the echo; workspace topology belongs to guidance-monorepo, with intra-app folder taxonomy staying in guidance-vertical-slices). Fix by sharpening scope exclusions, not by deleting triggers.

- [ ] **Step 4: Counter-case gate re-check**

For every Guidance page: confirm `Doesn't apply when` has ≥2 entries and each is a checkable condition, not a preference. Any page failing this gets fixed now or demoted to `status: draft` with the gap named in its body.

- [ ] **Step 5: Repo test suite; commit**

Run: `devbox run test`
Expected: PASS.
```bash
git add -A
git commit -m "Cross-pack review: sanitization, conformance, trigger seams"
```
