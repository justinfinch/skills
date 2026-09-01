---
okf_version: "0.2"
---

# Concepts

* [Structuring an HTTP boundary as one slice per endpoint](concepts/repr-endpoints.md) - Give every route its own file — one route per slice, named for the application command or query it calls, grouped in a resource folder that is navigational only — holding a request schema validated at the boundary, a thin handler that invokes exactly one command or query, and a response DTO; wired by a registration helper that is deliberately a convenience and not a command bus, with dependencies injected at registration, authority declared at each slice's own registration site, and a composition file that registers endpoints and contains no inline handler.
* [Organizing an application by feature with a tool-enforced import direction](concepts/feature-folder-organization.md) - Organize a client application's source by product capability rather than by file role — one folder per feature, a shared tier for cross-feature code, a single checkable sorting rule (knows business logic goes to the feature, dumb visual goes to shared), features as non-importing peers, and an import boundary enforced by a dependency tool rather than by review.
* [Sharing code between peer slices without re-centralizing them](concepts/shared-code-between-peers.md) - Constrain any module shared between peer slices to exported functions with no state and no composed behavior, scope it to the narrowest group that actually shares it, and assemble the peers from data rather than from a composite registration function — so the hub the slicing removed is structurally incapable of reassembling inside it.
