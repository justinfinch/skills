---
okf_version: "0.2"
---

# Concepts

* [Share the tokens and the headless logic, own the render stack per platform](concepts/tokens-plus-headless-logic.md) - Ship web and native from one team by sharing only the two layers that transfer cleanly — design tokens and render-free logic such as state machines, hooks and view-models — while each platform keeps its own render stack built on its own idioms, so the product is one design language spoken in two dialects rather than one component tree compiled everywhere.
* [Two tiers of design tokens — a primitive scale behind semantic aliases](concepts/two-tier-design-tokens.md) - Structure design tokens in two tiers — a primitive scale holding raw values such as color ramps, spacing and type sizes, and a semantic alias layer naming intent such as surface, accent and danger — with a hard rule that components consume semantic tokens only, enforced by lint rather than assumed; hand-author the theme while it is small, but keep its shape transformable so a token pipeline can be adopted later without reshaping the tokens.
