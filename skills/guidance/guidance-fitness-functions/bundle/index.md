---
okf_version: "0.2"
---

# Concepts

* [Making a load-bearing decision executable in CI](concepts/architectural-fitness-functions.md) - Name, at decision time, the executable check that detects each load-bearing decision's violation, and run it in CI in a fast static lane and a slower integration lane, so architectural erosion fails a build instead of surfacing in production.
* [The fitness-function registry](concepts/fitness-function-registry.md) - One table in the architecture document listing every named check, the exact script or test that enforces it, its CI lane, and whether it is active, pending a milestone, or deferred — so "we have a check for that" is a claim a reader can verify.
