---
okf_version: "0.2"
---

# Concepts

* [Separating commands, projections, and queries over one database](concepts/cqrs-lite.md) - Run three models over a single relational store — a command model whose unit of work is one aggregate in one transaction, a projection model that owns derivation logic, and a query model returning DTOs that never touch the domain — and keep the separation honest with a dependency rule rather than a folder convention.
* [Treating read projections as rebuildable rather than backed up](concepts/rebuildable-projections.md) - Let projection workers be the only writers of derived read tables, stamp every row with the projector version that produced it, and buy safety with a rebuild guarantee on a CI-verified time budget instead of a backup — which means splitting durability targets deliberately, strong for the source stream and zero for everything derived from it.
* [Enforcing an append-only source stream at the database-role level](concepts/append-only-source-stream.md) - Grant the writing role INSERT and nothing else on the table that everything else is derived from, revoke UPDATE and DELETE, make corrections new events rather than edits, dedup on a client-generated key, and keep large payloads outside the row by reference — because application-level immutability discipline is honoured ninety-five percent of the time and the other five percent is permanent.
