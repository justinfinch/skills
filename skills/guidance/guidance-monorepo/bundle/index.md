---
okf_version: "0.2"
---

# Concepts

* [Splitting a workspace into apps and packages with the domain package at the dependency center](concepts/domain-centered-workspace.md) - Divide a monorepo into apps (deployables at the edge) and packages (libraries), with the domain package at the dependency center — packages point inward toward domain, domain imports nothing app- or infrastructure-flavored, apps only compose — and make the import direction a tool-enforced fact while a task-graph runner keyed on the workspace graph orchestrates builds.
* [Betting on one language across API, workers, and clients](concepts/single-language-end-to-end.md) - Choose one language for every runtime in the product — API, background workers, web and mobile clients — so domain types and validation schemas travel from the database boundary to the UI as imports rather than as translation layers, and treat the bet as a decision with an explicit revisit trigger rather than a default.
