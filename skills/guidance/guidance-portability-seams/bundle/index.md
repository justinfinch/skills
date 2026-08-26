---
okf_version: "0.2"
---

# Concepts

* [Naming the escape valve and the triggers that reopen the decision](concepts/named-migration-triggers.md) - When you commit all-in to a platform you cannot cheaply leave, make the same decision record carry the specific alternative you would move to and per-layer triggers — measurable thresholds on cost, latency, consumer count or a named feature gap — whose firing produces a new decision record rather than an automatic migration.
* [Putting the seam at the commodity API, not at the vendor](concepts/standard-api-seams.md) - Make the architectural seam a commodity API that several independent implementations already speak — the S3 API for object storage — or, where no commodity API exists, a narrow provider interface owned by the domain layer, and require the local development double to honor the same seam, choosing that double on upstream health rather than popularity.
