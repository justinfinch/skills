---
okf_version: "0.2"
---

# guidance-clean-architecture — bundle index

Clean Architecture as a pragmatic synthesis: the Dependency Rule as the
invariant, ports and adapters as the boundary mechanics, a feature-sliced
use-case layer, sociable testing at the boundary, and the lineage behind the
vocabulary. Read `dependency-rule` first; the other technique pages assume
it.

## Concepts

* [The Dependency Rule — source dependencies point toward policy](concepts/dependency-rule.md) - Keep every source dependency pointing from infrastructure toward business policy — the domain and use-case core imports nothing framework- or IO-flavored, outer code implements interfaces the core declares, and one composition root at the process entry point wires the graph — treating the named layers as schematic and collapsing any layer that would be pass-through.
* [Ports and adapters — boundary mechanics for a clean core](concepts/ports-and-adapters.md) - Give the core its seams as ports it declares and adapters implement, honoring the driving/driven asymmetry — driving adapters call the core, driven adapters are called through core-owned interfaces — with ports declared next to the use case that consumes them, a repository port on the write side only, translation DTOs only where representations genuinely diverge, and partial boundaries where a full seam is not yet defensible.
* [The use-case layer — first-class operations, sliced by feature](concepts/use-case-layer.md) - Make each state-changing business operation a first-class, named use case that owns its transaction boundary and speaks the domain's vocabulary, organize use cases as feature slices inside the clean boundary rather than as a horizontal service layer, let simple slices be transaction scripts, and refuse to write the use case that would only proxy a repository call.
* [Testing at the boundary — sociable tests through use cases](concepts/testing-at-the-boundary.md) - Test business behavior by driving the use-case boundary the way a driving adapter would, with real domain objects and real in-memory implementations of driven ports, substituting doubles only for out-of-process dependencies — never mock-per-class — and push computation-heavy logic into a functional core tested with plain values and no doubles at all.
* [Lineage — BCE, Hexagonal, Onion, Clean](concepts/lineage.md) - The family tree behind Clean Architecture — Jacobson's Entity-Control-Boundary, Cockburn's Hexagonal, Palermo's Onion, and Martin's synthesis — with what each formulation actually contributed, where the community treats them as synonyms, and the three differences that still matter in practice.
