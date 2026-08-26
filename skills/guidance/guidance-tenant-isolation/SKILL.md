---
name: guidance-tenant-isolation
description: >-
  Multi-tenant isolation and authorization — Postgres Row-Level Security as a
  database-level tenant backstop behind application query filters,
  per-transaction tenant context via `SET LOCAL`, the choice between a
  permissive and a fail-closed policy for authentication-framework tables, and
  strictly-narrowing authorization gates (tenant, then reachable subgraph, then
  specific grant) through a single evaluator for within-tenant access. Use when
  designing a multi-tenant schema, adding a `tenant_id` or `organization_id`
  column, running background workers or a connection pooler against
  tenant-scoped tables, asking how to stop cross-tenant leaks or within-tenant
  over-sharing, or reviewing authorization for hierarchical access over location
  trees and org hierarchies. Not an authentication-provider or identity-library
  comparison; not row-level encryption, data residency, or per-tenant key
  management.
---

# guidance-tenant-isolation

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Read the pages in order — they are two gates at different depths, and the
   outer one has to hold first.
   [rls-tenant-backstop.md](bundle/concepts/rls-tenant-backstop.md) is the hard
   tenant boundary, enforced below the query;
   [narrowing-authorization-gates.md](bundle/concepts/narrowing-authorization-gates.md)
   composes what sits above it, within a tenant. Reading the second alone
   produces a system whose access rules are careful and whose tenant boundary
   still rides on every query remembering its filter.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-tenant-isolation/<path-within-bundle>`, so the rationale outlives
   the conversation. In an Arche, that record is the ADR and the citation goes
   in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.

The distinction the pack exists to keep sharp: a tenant backstop makes
cross-*customer* disclosure structurally impossible and says nothing whatsoever
about over-sharing *within* a tenant. Those are two boundaries with two
enforcement mechanisms and two separate tests, and treating either as coverage
for the other is the failure both pages are written against.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
