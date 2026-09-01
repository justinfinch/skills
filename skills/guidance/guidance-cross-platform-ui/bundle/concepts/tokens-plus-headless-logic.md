---
type: Guidance
title: Share the tokens and the headless logic, own the render stack per platform
description: Ship web and native from one team by sharing only the two layers that transfer cleanly — design tokens and render-free logic such as state machines, hooks and view-models — while each platform keeps its own render stack built on its own idioms, so the product is one design language spoken in two dialects rather than one component tree compiled everywhere.
tags: [cross-platform, ui, headless, design-tokens, react-native, render-stack, universal-components, platform-idiom]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:45:31Z }
status: stable
stale_after: 2027-09-01
sources:
  - id: fowler-headless-component
    resource: https://martinfowler.com/articles/headless-component.html
    title: Qiu — Headless Component, a pattern for composing UIs
  - id: fowler-presentation-model
    resource: https://martinfowler.com/eaaDev/PresentationModel.html
    title: Fowler — Presentation Model (render-free view state)
  - id: radix-primitives
    resource: https://www.radix-ui.com/primitives/docs/overview/introduction
    title: Radix Primitives — unstyled, behavior-and-accessibility-only components
  - id: react-native-learn-once
    resource: https://reactnative.dev/
    title: React Native — "learn once, write anywhere" positioning
  - id: react-native-web
    resource: https://necolas.github.io/react-native-web/
    title: React Native for Web — running RN primitives in the DOM
  - id: tamagui
    resource: https://tamagui.dev/docs/intro/introduction
    title: Tamagui — universal component system with a compile step
  - id: gluestack
    resource: https://gluestack.io/
    title: gluestack-ui — universal copy-owned components
  - id: nativewind
    resource: https://www.nativewind.dev/
    title: NativeWind — utility-class styling shared between web and native tooling
  - id: apple-hig
    resource: https://developer.apple.com/design/human-interface-guidelines
    title: Apple Human Interface Guidelines — the platform idiom, stated
  - id: material-design
    resource: https://m3.material.io/
    title: Material Design 3 — the other platform idiom, stated
---

# Share the tokens and the headless logic, own the render stack per platform

## Technique

Draw the sharing line by *what actually transfers between platforms*, not by
what is nominally written in the same language.

Two layers transfer cleanly and are shared as first-class packages:

**Design tokens.** The values that make the product look like itself —
color ramps, spacing scale, type scale, radii, elevation — authored once and
consumed by both platforms' styling engines. This is the design-consistency
mechanism, and it is the layer that makes "separate render stacks" affordable
at all; see
`guidance-cross-platform-ui/concepts/two-tier-design-tokens.md` for how the
token layer itself is structured.

**Render-free logic.** Data fetching and caching, real-time subscription
handling, optimistic-update reconciliation, form state and validation,
formatting, and the state machines that describe what a screen is *doing* as
opposed to what it *looks like*. Packaged as hooks, view-models, or plain
functions with **zero render, DOM, or native-UI dependencies** — a constraint
that is stated as a build-failing rule, not as a convention.

Everything that renders is owned per platform. The web app renders with the
web's idioms — semantic DOM, tables, keyboard and focus behavior,
server-rendering, the accessibility primitives the platform ecosystem already
solved. The native app renders with the native idioms — platform navigation,
gesture handling, large touch targets, hardware access, the OS accessibility
APIs. Neither imports the other's components, and there is no compile step
translating one component model into the other.

The result is **one language, two dialects**: a shared vocabulary of intent
(tokens, behavior, data) with per-platform grammar of expression. The design
consistency comes from the shared token layer and a shared design review, not
from a shared component tree.

The explicit rejection is the *universal component library* — one component
set that renders on every platform, whether by compiler, by copy-owned
universal source, or by running the native primitive library in the browser.
Those are legitimate techniques with their own conditions, listed in
[Alternatives considered](#alternatives-considered); this technique is what to
do when those conditions don't hold.

The move is reversible in the cheap direction. Tokens and headless logic are
exactly the substrate a universal component library sits on top of, so
adopting one later is an addition. Removing one after a codebase has been
written against its component model is the expensive direction — which is the
asymmetry that makes this the lower-regret starting position when the answer
is genuinely uncertain.

## Applies when

- **You are shipping a web surface and a native surface from one team**, with
  no separate web and mobile organizations. Two independent teams change the
  calculus entirely — they will not share a package on either side of the line
  without a coordination cost that this technique does not price in.
- **Your component model supports a headless/render split** — a framework
  where behavior and state can be expressed as composable units with no render
  output attached (React hooks, Vue composables, Svelte stores, or an
  equivalent). This is a stack condition and it is load-bearing: in a stack
  where UI logic can only be expressed inside a widget or a component class,
  the "shared logic, separate render" split has no natural expression and you
  are back to sharing at a service or protocol boundary instead.
- **The two platforms' styling systems can read a common token source.** A
  build step that compiles one token definition into both platforms' style
  representation is the enabling condition; without it, the shared token layer
  is a manual copy and the whole technique degrades to two independent apps
  with a shared style guide.
- **Platform feel is load-bearing for the product**, which is checkable rather
  than a matter of taste. The test: name each platform's flagship surface and
  ask what it depends on. If one depends on hardware, backgrounding, offline
  durability, or gesture behavior, and the other depends on dense tabular
  layout, keyboard navigation, deep linking, print, or server-side rendering,
  the surfaces are platform-bound and a universal component model buys reuse
  precisely where the surfaces overlap least.
- **The genuinely shared *render* surface is small.** Count the screens that
  would be pixel-and-behavior identical on both platforms. If it is a
  minority, sharing rendered components is optimizing the minority case at the
  cost of the majority.
- **The team can staff and maintain two render stacks** — which in practice
  means people who are competent in both platform idioms, or willing to
  become so. This is a hiring and capacity fact, and it is the condition most
  often assumed rather than checked.
- **You have a shared design review, or can institute one.** The technique
  moves the consistency guarantee from the compiler to a human ritual. If
  nothing reviews both platforms against each other, consistency is
  unenforced.

## Doesn't apply when

- **The app is a thin content viewer and a webview or universal renderer is
  honestly good enough.** Per-platform render stacks are roughly double the
  UI surface — double the components, double the accessibility work, double
  the review, double the bug fixes — and that cost has to be paid for by
  revenue that platform feel actually generates. A content-reading app, an
  internal admin tool with a mobile wrapper, a dashboard, or a marketing
  surface frequently does not have that revenue, and the honest answer is a
  webview shell or a universal renderer. Say the quiet part out loud: the
  question is not "is a webview worse", it is "is it worse by enough to fund
  a second render stack".
- **The team lacks capacity to maintain two render stacks.** A universal
  framework's compromise beats an abandoned platform. This is the most
  important counter-case and the one most often lost to optimism: two
  developers who can build one excellent web app and one excellent native app
  cannot necessarily build *both* and keep them at parity for two years. When
  capacity is the binding constraint, a universal component library delivers a
  mediocre-but-present experience on both platforms, and that dominates an
  excellent web app beside a native app that stopped being updated eight
  months ago.
- **The two surfaces are substantially the same app.** If both platforms are
  forms, lists, and detail views over the same data, with no platform-bound
  flagship on either side, the overlap is the majority of the product and the
  universal component library is buying reuse exactly where the reuse is. The
  tempting error is applying this technique because the platforms are
  *different technologies*, when the question is whether the platforms have
  *different jobs*.
- **One platform is strategically secondary.** A companion app, a
  read-only viewer, a compliance checkbox. Then the right move is the cheapest
  thing that ships it, and a second render stack is a permanent cost taken on
  for a surface nobody's roadmap prioritizes.
- **You are targeting more than two platforms with one small team.** The cost
  of this technique scales linearly with platform count while the universal
  framework's does not. At web plus iOS plus Android-as-separate-idioms plus
  desktop plus TV, the per-platform ownership model is a staffing plan, not an
  architecture.
- **An organizational component library already exists and is mandated.** If
  the design organization ships a universal component set that other products
  in the portfolio consume, building a parallel per-platform stack costs you
  the portfolio consistency the library exists to provide, and you will be
  the team that diverged.

## Trade-offs

**Buys** first-class experience on each platform: the native surface can use
hardware, background execution, and platform gestures without fighting an
abstraction, and the web surface keeps semantic markup, keyboard and focus
behavior, server rendering, and the mature accessibility primitive ecosystem.
It buys freedom from a universal framework's compile step, release cadence,
and version-coupling risk — no third party sits between your code and the
screen on either platform. It buys the cheap-direction reversibility described
above. And, less obviously, it buys *honesty*: the platform differences are
visible in the code rather than hidden behind an abstraction that mostly
works.

**Costs**, first and most concretely, duplicated render work — components
written twice, styled twice, tested twice, and fixed twice. The count is
bounded by how small the genuinely-shared surface is, but it is real and it is
permanent. Second, two styling engines to keep aligned, which makes the token
build step infrastructure you now own and must keep working across both
toolchains' upgrade cycles. Third, two accessibility implementations, which is
the duplication that most often silently becomes one-and-a-half. Fourth, a
standing discipline tax: the headless boundary and the semantic-token rule are
only real if something enforces them. Fifth, breadth of skill — every
contributor is now expected to work in two idioms, which narrows hiring and
lengthens onboarding.

The quality attributes moved are **usability** (each platform gets its native
feel) and **evolvability** (no universal framework dictating the component
model). What is paid is **development cost** and **time to market**, and
**consistency** shifts from a compile-time guarantee to a reviewed practice —
which is a genuine downgrade in enforcement strength, not a lateral move.

**What would make this stale.** The whole recommendation is priced off two
things that are moving fast. First, the maturity of universal component
frameworks: the historical case against them is compile-step complexity,
release instability, and a component model that fits neither platform
perfectly. If a universal framework becomes boring — stable releases, no
exotic build integration, escape hatches to per-platform rendering when needed
— the cost side of the counter-case shrinks and the "team capacity" condition
above starts dominating more cases than it does today. Second, the convergence
of the platforms themselves: as native frameworks gain first-class web
rendering targets and web frameworks gain better native integration, the claim
that the render layer *cannot* transfer weakens. Re-check by asking what a
universal framework's failure modes actually cost this year, not what they
cost when the decision was made. This page decays faster than the token page
beside it for exactly this reason — the token structure is a naming pattern,
while this page is a bet on the state of a specific tooling ecosystem.

## Failure modes

- **The shared logic layer sprouts render imports until the split is
  fiction.** It starts with one component type in a hook's signature, then a
  formatting helper that returns markup because that was convenient, then a
  platform check inside a shared module. Nothing breaks; every step is
  individually defensible. What you discover, usually at the moment someone
  tries to use the shared layer from the *other* platform, is that half of it
  was never platform-neutral. Enforce the boundary as a build-failing
  dependency rule — the shared logic package has zero render, DOM, or
  native-UI dependencies, and no app imports another app's components. See
  `guidance-fitness-functions`. Without the check, the boundary lasts about a
  quarter.
- **A platform conditional appears inside the shared layer, and the split
  becomes a branch.** The subtler version of the above, and the one a
  dependency rule does not catch: the shared module imports nothing forbidden
  but reads a platform flag and forks. Now the "shared" logic is two
  implementations in a trench coat, with the worst property of both — neither
  platform's author can read it, and neither can change it safely. Treat a
  platform conditional in the shared layer as a design signal that the
  behavior is not actually shared, and push it back into the app.
- **Tokens get forked per platform, "temporarily".** A native styling engine
  does not support a token type, or a value needs a different concrete number
  on the two platforms, so someone copies the token file and adjusts it with a
  note to reconcile later. The reconciliation does not happen; six months on,
  the platforms are visually diverging and no single source describes the
  brand. When the platforms genuinely need different values, the fix is a
  platform *dimension* in the one token source, not a second token source.
- **The two dialects drift into two languages.** Each platform's UI is
  reviewed by whoever built it, against nothing. Interaction patterns diverge
  first (where a destructive confirm lives, how errors are surfaced, what a
  disabled state looks like), then information architecture, then vocabulary,
  and users who move between the platforms stop recognizing the product.
  Nothing fails, no test catches it, and by the time it is visible it is a
  redesign. The counter is a standing review that looks at both platforms
  side by side on the same flow, and treats a divergence as a decision that
  needs a reason.
- **A behavior fixed on one platform stays broken on the other, and it is a
  data bug rather than a visual one.** This is the failure that pages someone.
  Retry and backoff policy, offline queue draining, optimistic-update
  reconciliation, and idempotency-key handling are the shared-logic
  candidates that are most often *nearly* shared — implemented in the shared
  package on one platform and re-implemented, subtly differently, inside the
  other app because it needed to interact with something platform-specific.
  During an outage, the platform with the less careful retry policy hammers
  the API and materially extends the incident. The rule that prevents it is
  the one that is hardest to hold under deadline: anything that decides
  *when to talk to the server* belongs in the shared layer, always, even when
  wiring it there is more work than inlining it.
- **Accessibility is implemented once.** The web stack gets it, because the
  web primitive libraries provide focus management, ARIA, and keyboard
  behavior nearly for free, and the native stack quietly does not, because
  there is no equivalent free lunch and nobody's checklist asked. The
  asymmetry is structural — the platform where correctness is cheap gets it
  and the platform where it is expensive does not — so it must be checked
  per platform rather than as one project-level box.
- **Version skew across the shared packages.** The shared logic package
  releases; the web app picks it up on its weekly deploy; the native app is
  waiting on a store review and pins the previous version for three weeks.
  Now the two platforms disagree about a cache key, an event shape, or a
  reconciliation rule, and the bug reproduces on exactly one platform. The
  native release cadence is the constraint here and it does not go away —
  design the shared layer's changes to be backward-compatible across at least
  one release cycle, and know which version each store binary is carrying.
- **The web stack's owned primitives silently fall out of date.** Copying
  accessibility primitives into the repository is the right call for control
  and for token styling, and the cost is that upstream fixes — including
  accessibility and security fixes — no longer arrive. Nothing signals this.
  Schedule a periodic diff against upstream, or accept that you are now the
  maintainer.

## Alternatives considered

- **A universal component framework with a compile step** (Tamagui-class) —
  one component set compiling to platform-atomic CSS on web and native views
  on native, with a single, strong token system. Wins when the two surfaces
  are mostly the same app, when a single canonical component library is a
  design-organization requirement, or when team capacity cannot fund two
  render stacks. It is also the natural *later* adoption if this technique's
  shared token layer already exists, since the framework can sit on those
  tokens. Its costs are a build-toolchain integration to keep working across
  framework upgrades, and a component model that has to be a compromise
  between the platforms by construction.
- **A universal copy-owned component library** (gluestack-class) — universal
  components brought into the repository as source rather than consumed as a
  runtime dependency. Wins where the compile-step risk of the previous option
  is the objection but universality is still wanted, and where owning and
  restyling the component source is acceptable. It removes the framework from
  the dependency graph and puts the maintenance on you; the "one component
  model straddling two divergent surfaces" question is unchanged.
- **Native-primitives-everywhere, with the native framework rendering the web
  target** (React-Native-Web-class) — write in native primitives and render
  the web through a compatibility layer. Wins decisively when native is the
  primary product and web is a secondary surface, and when one toolchain and
  one deployment story is worth more than web-native capability. What it
  costs is the web platform: semantic markup, table and form semantics,
  keyboard behavior, server-side rendering, and the web framework ecosystem —
  all reachable only through the compatibility layer. It is the highest
  coupling of the options, and the hardest of them to walk back.
- **A webview or hybrid shell** — one web application wrapped for
  distribution on the app stores. Wins for content-viewer apps, internal
  tools, and any product where the app-store presence matters more than the
  in-app experience, and it is by a wide margin the cheapest to build and
  ship. Loses where hardware access, offline durability, background work, or
  gesture-level responsiveness are the product.
- **Fully independent apps, sharing nothing** — separate teams, separate
  stacks, no shared packages at all. Wins when the platforms genuinely are
  different products for different users, or when two independent
  organizations own them and the coordination cost of a shared package
  exceeds its benefit. Loses on brand consistency and on the duplication of
  data-layer and reconciliation logic, which is the duplication that produces
  behavior bugs rather than cosmetic ones.
- **Hand-rolling the web primitive layer instead of adopting one** — building
  your own focus management, ARIA wiring, and keyboard interaction. Wins only
  where an unusual interaction model genuinely has no primitive available.
  Otherwise it is slow and a standing accessibility risk, since the primitive
  libraries encode years of edge cases that will not occur to you in the
  order they occur to users.
