---
name: guidance-monorepo
description: >-
  Monorepo workspace topology — the apps/packages split with the domain package
  at the dependency center, inward-pointing import direction enforced by a
  dependency tool, task-graph build orchestration and its caching, and the
  single-language-end-to-end bet that lets domain types and validation schemas
  travel from the database boundary to the UI without translation layers.
  Examples assume TypeScript with pnpm and Turborepo; the topology reasoning is
  stack-agnostic. Use when setting up a monorepo, deciding how to structure
  packages or where a shared package belongs, weighing monorepo versus polyrepo,
  sharing types between backend and frontend, asking whether everything should be
  one language, or when a shared/utils package has become a dependency magnet.
  Not a package-manager or build-tool comparison and not dev-environment
  tooling; intra-app folder structure lives in guidance-vertical-slices.
---

# guidance-monorepo

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. Read [bundle/index.md](bundle/index.md), then start with
   [domain-centered-workspace.md](bundle/concepts/domain-centered-workspace.md)
   — the topology decision is the one that constrains the other. Walk its
   **Applies when** list condition by condition; the first condition (two or more
   deployables actually exist) settles most cases on its own. Read
   [single-language-end-to-end.md](bundle/concepts/single-language-end-to-end.md)
   when a language or runtime choice is genuinely open, and read it anyway before
   adopting the workspace: shared types are what the topology is *for*, and a
   workspace built without them is paying the structural cost for a smaller
   benefit. The two decisions are separable — a polyglot repo can still be one
   repository — but each page's reasoning assumes you know where the other landed.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so. The most common wrong adoption is a workspace scaffolded
   for deployables that exist only on a roadmap.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as `guidance-monorepo/<path-within-bundle>`, so the
   rationale outlives the conversation. In an Arche, that record is the ADR and
   the citation goes in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
5. Both pages depend on something a machine checks — the domain package's import
   list, and the absence of server-only dependencies in a shared package a client
   bundles. Carry the check into whatever record cites the page. Unenforced, the
   dependency direction is a claim in a README that decays commit by commit
   without ever failing a build.

**A package boundary is not a service boundary.** Everything here is about how
source and build targets are arranged in one repository. Package boundaries are
compile-time and free to cross; service boundaries carry latency, partial
failure, and independent deployment. "We already have packages, so each could be
a service" is how a legible workspace becomes an unplanned distributed system.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
