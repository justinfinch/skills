---
okf_version: "0.2"
---

# Concepts

* [Structuring an HTTP boundary as one slice per endpoint](concepts/repr-endpoints.md) - Give every route its own directory holding a request schema validated at the boundary, a thin handler that invokes exactly one command or query, and a response DTO — wired by a registration helper that is deliberately a convenience and not a command bus, with dependencies injected at registration and a composition file that registers endpoints and contains no inline handler.
* [Organizing an application by feature with a tool-enforced import direction](concepts/feature-folder-organization.md) - Organize a client application's source by product capability rather than by file role — one folder per feature, a shared tier for cross-feature code, a single checkable sorting rule (knows business logic goes to the feature, dumb visual goes to shared), features as non-importing peers, and an import boundary enforced by a dependency tool rather than by review.
