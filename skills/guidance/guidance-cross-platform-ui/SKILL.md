---
name: guidance-cross-platform-ui
description: >-
  Cross-platform UI without a universal renderer — sharing design tokens and
  headless, render-free logic (hooks, state machines, view-models) while each
  platform owns its own render stack, one design language spoken in two
  dialects; and design-token architecture in two tiers, a primitive scale
  behind semantic aliases, with components consuming semantic tokens only.
  Examples assume a React / React Native / Tailwind ecosystem and weigh
  Tamagui, gluestack and React-Native-Web as the rejected alternatives; the
  layering reasoning is stack-agnostic. Use when building web and mobile from
  one codebase, evaluating a universal component framework, deciding what to
  share between apps, setting up design tokens or theming, adding a dark,
  dense or white-label theme, or planning a brand refresh that means
  re-skinning the product. Not a visual design language; not
  native-vs-cross-platform app-strategy advice.
---

# guidance-cross-platform-ui

A guidance pack. The content is [bundle/](bundle/), an Open Knowledge Format
v0.2 bundle of `Guidance` pages.

## How to use this pack

1. The two pages are one decision in two halves, and the sharing decision comes
   first.
   [tokens-plus-headless-logic.md](bundle/concepts/tokens-plus-headless-logic.md)
   decides *where the line between shared and per-platform sits*, and its
   **Doesn't apply when** is the real gate — several products should be reading
   it to conclude that a universal renderer or a webview is the right answer
   for them.
   [two-tier-design-tokens.md](bundle/concepts/two-tier-design-tokens.md)
   decides how the shared token layer is shaped, and stands on its own for a
   single-platform product that never asks the first question. Read both when
   the first page's technique is adopted, because the token layer is what makes
   separate render stacks affordable — separate stacks over an unshared token
   source is two apps, not one product.
2. Check each page's **Applies when** and **Doesn't apply when** against the
   project in front of you. A page whose conditions don't hold is evidence
   *against* the technique here — not a neutral result, and not a page to skip
   past quietly. Say so.
3. If a page informs a decision, cite that **page** — not the pack directory —
   in that decision's record, as
   `guidance-cross-platform-ui/<path-within-bundle>`, so the rationale outlives
   the conversation. In an Arche, that record is the ADR and the citation goes
   in its `sources:`.
4. Never restate a recommendation without its trade-off. The trade-off is the
   part that transfers.
5. Both techniques are guarantees that only exist while something enforces
   them — a boundary rule keeping render dependencies out of the shared logic
   layer, and a lint rule keeping primitive tokens and raw values out of
   components. Neither survives a quarter as a convention. If a project cannot
   or will not run the checks, say plainly that it is adopting the costs of
   both techniques without the property either one is bought for.

The pack's stack scoping is deliberate. The sharing line and the token tiers
are stack-agnostic reasoning; the named frameworks are the ecosystem the
evidence came from. An agent working in another ecosystem should keep the
conditions and re-derive the specific tooling — the questions "does my
component model support a headless split" and "does my styling system resolve
references" are the two that have to be answered locally.

## What this pack is not

It is not a workflow — it decides nothing on its own and writes nothing; it
informs decisions that are recorded elsewhere.

It is not institutional context and must never be copied into a project's
`./.arche/`. The Arche holds what *this* organization decided; this pack holds
knowledge that is true whether or not the organization exists. Cite it, don't
absorb it.
