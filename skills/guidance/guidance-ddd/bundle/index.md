---
okf_version: "0.2"
---

# Concepts

* [Whether strategic DDD is warranted](concepts/strategic-ddd.md) - Decide whether to treat the domain model as the primary design artifact, before adopting any of the machinery that follows from it.
* [Where the modelling investment belongs](concepts/core-domain.md) - Classify subdomains as core, supporting, or generic, so the scarce modelling effort lands on what differentiates the business and the rest is bought or kept deliberately plain.
* [Where a bounded context boundary belongs](concepts/bounded-contexts.md) - Draw boundaries where the language changes meaning, not where the org chart or the deployment topology happens to fall.
* [Naming the relationship between two contexts](concepts/context-mapping.md) - Choose and state the integration relationship explicitly, so translation cost and the power balance between teams are visible rather than assumed.
* [Sizing an aggregate's consistency boundary](concepts/aggregate-boundaries.md) - Group entities by the invariants that must hold atomically, and reference everything else by identity so the consistency model is stated rather than assumed.
