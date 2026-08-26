---
type: Guidance
title: Two tiers of design tokens — a primitive scale behind semantic aliases
description: Structure design tokens in two tiers — a primitive scale holding raw values such as color ramps, spacing and type sizes, and a semantic alias layer naming intent such as surface, accent and danger — with a hard rule that components consume semantic tokens only, enforced by lint rather than assumed; hand-author the theme while it is small, but keep its shape transformable so a token pipeline can be adopted later without reshaping the tokens.
tags: [design-tokens, theming, semantic-tokens, primitives, style-dictionary, dark-mode, white-label, rebrand]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:45:31Z }
status: stable
stale_after: 2028-03-01
sources:
  - id: dtcg-format
    resource: https://tr.designtokens.org/format/
    title: W3C Design Tokens Community Group — Design Tokens Format Module
  - id: dtcg-home
    resource: https://www.designtokens.org/
    title: Design Tokens Community Group — charter and scope
  - id: style-dictionary
    resource: https://styledictionary.com/
    title: Style Dictionary — building tokens into per-platform artifacts
  - id: tailwind-theme
    resource: https://tailwindcss.com/docs/theme
    title: Tailwind CSS — theme variables as the token surface
  - id: curtis-naming-tokens
    resource: https://medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676
    title: Curtis — Naming Tokens in Design Systems
  - id: material-tokens
    resource: https://m3.material.io/foundations/design-tokens/overview
    title: Material Design 3 — reference, system and component token tiers
  - id: sfdc-tokens
    resource: https://www.lightningdesignsystem.com/design-tokens/
    title: Salesforce Lightning Design System — design tokens, an early production system
---

# Two tiers of design tokens — a primitive scale behind semantic aliases

## Technique

Split the design values into two named layers with a one-way dependency
between them.

**Tier one is the primitive scale.** Raw values with descriptive, valueless
names — a color ramp per hue, a spacing scale, a type scale, radii,
elevations, durations. These names describe *what the value is*, not what it
is for. There is no intent encoded here at all; the primitive layer is a
palette, in the painter's sense.

**Tier two is the semantic alias layer.** Names that describe *intent* and
whose values are references into the primitive scale — a page background, a
raised surface, a body text color, an accent, a destructive action, a
disabled state, a state each of the domain's real named statuses. This is the
layer components are allowed to see.

Then the rule that makes the structure worth having: **components consume
semantic tokens only.** No raw literals, no primitive-tier tokens, no
exceptions that aren't written down. The rule is not a convention; it is a
lint rule that fails the build, because the value of the whole arrangement is
exactly the guarantee it provides, and an unenforced guarantee provides
nothing. Registering the check is the practice covered by
`guidance-fitness-functions`.

What the two tiers buy is a **remap point**. A theme — dark, high-density,
a customer's white-label palette, a rebrand — becomes a different set of
alias-to-primitive bindings, with the component layer untouched. Without the
alias tier, every one of those is a change to components.

On tooling: **hand-author the theme while it is small, and keep it in a shape
a transform pipeline can consume later.** A token-build pipeline earns its
ceremony when there are several output targets, a designer with a design-tool
library to sync from, or more themes than a person can hold in their head. It
does not earn it on day one with two targets and one theme. What matters is
that the *structure* — two tiers, references rather than duplicated values,
consistent naming — is the same structure a pipeline expects, so adopting one
later is a format migration rather than a re-modelling of the design system.
Aligning the token names and reference syntax with the community format
specification is the cheap way to keep that door open.

**This page is deliberately stack-agnostic.** The two-tier structure is a
naming and indirection pattern, not a technology choice, and it holds
wherever a styling system supports variable indirection — CSS custom
properties, a native theme object, a utility framework's theme layer, a
platform resource system, a compiled stylesheet. Where the surrounding pack's
examples name a particular ecosystem, this page's reasoning does not depend
on it. What *is* required is that the styling system can express a reference
from one name to another and resolve it at build or render time; a system
where every value must be a literal cannot host the alias tier at all.

## Applies when

- **More than one theme is foreseeable and nameable.** A dark mode, a
  high-density mode, a customer white-label, a seasonal or brand refresh
  already on someone's roadmap. "Foreseeable" is the check: you can name the
  second theme and roughly when. One theme forever does not need a remap
  point.
- **More than one consumer reads the same values** — two platforms, two
  applications, a marketing site sharing the product's brand, an email
  template system, a documentation site. Multiple consumers make the token
  layer a contract, and a contract wants intent names rather than values.
- **"Re-skin without touching components" is a stated quality attribute**,
  not merely a nice idea. If nobody would notice or care that a rebrand
  touched three hundred components, the indirection is being bought for
  nothing.
- **The domain has real named states that want color and weight.** Statuses
  with business meaning — pending versus confirmed, valid versus in-error,
  draft versus final, active versus archived — are exactly what a semantic
  tier models well, because the name in the token file matches the name the
  business uses. When a semantic tier maps onto vocabulary that already
  exists, it is modelling something real rather than adding an abstraction.
- **You are the author of the theme.** The technique describes how to
  structure tokens you own. If tokens arrive from elsewhere, see the
  counter-case below.
- **The styling system supports reference indirection** and resolves it at
  build or render time. This is a mechanical check, and it is the one
  condition on this page that a given stack can actually fail.

## Doesn't apply when

- **A single-platform app with a bought theme it will never rebrand.** A
  purchased or vendor-supplied theme, one output target, no white-label
  ambition, no second brand. Two tiers there is indirection with exactly one
  consumer and one binding — you pay a lookup hop on every debugging session
  and never once exercise the remap. Use the theme's own variables directly
  and say in the record that you chose to.
- **A design team already ships tokens from a design tool.** Consume theirs.
  Building a parallel semantic layer beside a token set that a design
  organization publishes creates two sources of truth for the same values, and
  the reconciliation lands on whoever notices the drift. If their published
  tier structure is missing an intent name you need, the work is to request it
  upstream or to add a *thin, documented* local extension layer that
  references theirs — not to re-model the system locally. The tempting version
  of this mistake is that the published tokens are slightly awkward for your
  app, so a "small local mapping" is added, and eighteen months later the
  local mapping is the real design system.
- **The product has no design surface of its own.** An internal tool that uses
  a component library's defaults wholesale, with no brand and no restyling
  intent. Tokens are a mechanism for controlling appearance; where appearance
  is delegated entirely, there is nothing to control.
- **A prototype or a time-boxed experiment.** The two-tier structure pays back
  over the life of a codebase. Something being deleted in six weeks has no
  such life, and the naming work is real work.
- **You cannot name the second theme *or* the second consumer.** This is the
  compressed form of the first two conditions above and it is the honest gate:
  if neither exists, the alias tier is a rename of the primitive tier with
  extra steps, and the first failure mode below is already waiting.

## Trade-offs

**Buys** re-skinning as an edit to one file — dark mode, density variants and
white-label themes become alias remaps with zero component changes, which is
the entire point and the only thing that justifies the rest. It buys a single
legible home for the design decisions, so "what color is a destructive
action" has one answer rather than a distribution. It buys a vocabulary that
designers and developers can share, since intent names are the names both
professions already use. And it buys a clean later adoption path for a token
pipeline or a design-tool sync, because the structure is already the shape
those tools expect.

**Costs**, first, a lookup hop: debugging a color now means resolving an
alias to a primitive to a value, three steps where there was one, on every
investigation for the life of the codebase. Second, naming work — permanent,
subjective, and never finished, because every new intent needs a name and
every name needs to be consistent with the ones already there. Third,
governance: the semantic vocabulary is a shared language and shared languages
need an owner, or they fragment. Fourth, the enforcement machinery itself —
the lint rule has to be written, kept current with the token set, and
defended when someone hits a legitimate exception. Fifth, a real risk of
over-modelling, since the tier invites tokens for things that do not vary.

The quality attribute moved is **modifiability**, specifically the cost of a
visual change. What is paid is **directness** — the ability to read a value
at its point of use — and a standing tax on **developer velocity** at the
moment of adding any new visual intent.

**What would make this stale.** Less than most guidance about front-end
practice, which is why this page carries a later expiry than the
cross-platform page beside it: the two-tier idea long predates any of the
current tooling and has survived several complete turnovers of the surrounding
ecosystem, because it is a naming pattern rather than a technology bet. Two
things could still move it. If the community token format specification
reaches broad adoption with mature, boring tooling, the "hand-author now,
pipeline later" advice weakens — the pipeline stops being ceremony and
becomes the default starting point, and the deferral loses its justification.
And if platform styling systems ship first-class semantic-token support with
built-in theming and validation, the hand-rolled alias layer and its custom
lint rule become a reimplementation of a platform feature. Re-check by asking
whether a token pipeline still costs a day of setup and a permanent build
step, or whether it has become a one-line dependency.

## Failure modes

- **Primitives leak into components, one hex code at a time, until theming is
  a grep exercise.** The deadline case where a designer's value has no alias
  yet; the "just this once" for an internal debug screen; the pasted snippet
  from documentation. Each is defensible and none is reverted. The
  characteristic discovery is during the first real theme change, when the new
  palette lands and roughly a fifth of the interface does not change — and
  worse, the fifth is scattered rather than clustered, so finding it is a
  visual sweep of every screen rather than a code search. The lint rule is
  what prevents this and the reason the rule has to fail a build rather than
  emit a warning; a warning-level rule reaches thousands of hits and is
  switched off.
- **The semantic vocabulary grows a synonym per author.** No naming gate, so
  one person adds an accent token, the next adds a primary, the third adds a
  brand and the fourth a highlight — four names, three of them bound to the
  same primitive, and no one able to say which to use. The rebrand then has to
  decide, per token, whether each synonym was intentional. The counter is
  cheap and organizational: one reviewer owns the semantic tier and adding a
  token is a reviewed change, not an ambient one.
- **The semantic tier is a rename of the primitive tier, so the indirection is
  decorative.** Aliases named after their values rather than their intent — a
  green-accent, a large-heading-size — bound one-to-one to primitives.
  Everything passes the lint rule and nothing is themeable, because the alias
  names encode the very thing a theme changes. The diagnostic question is
  whether an alias's name would still be *true* after a rebrand. If a
  hypothetical rebrand to a different hue would make the token's name a lie,
  it is a primitive wearing a semantic name.
- **The aliases encode assumptions that the second theme violates.** Names
  like a light-surface or a dark-text read as intent and are actually
  lightness claims, so when dark mode arrives, the remap inverts them and
  every name in the file is backwards. This surfaces at the worst time — the
  theme is being built, the structure that was supposed to make it a config
  change turns out to need a rename across the component layer, and the
  project's estimate was made on the config-change assumption. Names should
  describe role and elevation, never lightness or hue.
- **A token rename ships and the interface fails silently rather than
  loudly.** This is the one that pages someone. Variable-based styling systems
  characteristically resolve an unknown reference to nothing — an empty value,
  an inherited value, a transparent color — rather than raising an error. So a
  renamed or deleted token does not fail the build and does not throw at
  runtime; it produces invisible text, an unstyled surface, or a control with
  no affordance, on whichever screens happened to use it. Type-checked or
  generated token accessors, plus a build-time assertion that every referenced
  token resolves, are what turn this from a production incident into a failed
  pipeline.
- **Only color is ever tokenized.** Color gets the two tiers; spacing, type
  scale, radii, elevation, motion durations, and z-index stay as literals
  scattered through components. Then the density theme or the accessibility
  motion setting arrives and it is the untokenized dimensions that have to
  change. Color is simply the easiest dimension to see, which is why it is the
  one that gets done.
- **The alias tier absorbs a token per component.** A well-intentioned drift
  toward naming tokens after the components that consume them, so every new
  component contributes several tokens, the file grows into the thousands, and
  no one can hold the vocabulary in their head. Some systems do run a
  deliberate third, component-scoped tier — see the alternatives — but that is
  a decision with an owner and a rule, not what this failure mode is. The
  failure mode is the tier arriving by accident, one component at a time.
- **The lint rule accumulates exemptions.** A legitimate exception is granted
  by a suppression comment, the pattern is copied, and the suppression count
  becomes the real measure of the design system's integrity — unwatched.
  Count the suppressions and treat the count as a tracked number, or the rule
  degrades to advice.

## Alternatives considered

- **Single-tier flat tokens.** One set of values consumed directly. Wins for
  a small, single-theme, single-platform product with no rebrand horizon,
  where the up-front saving is real and the modifiability tax never comes
  due. Loses the moment a second theme is wanted, because there is no remap
  point and the change lands in the component layer.
- **Three tiers, adding a component-scoped layer.** A reference tier, a system
  or semantic tier, and per-component tokens bound to the semantic tier — the
  structure large published design systems converge on. Wins at scale, where
  many teams consume the system and a component's appearance needs to be
  overridable without touching the shared semantic vocabulary. Loses on
  volume: the token count grows with the component count, and below a certain
  organization size the third tier is bookkeeping without a beneficiary.
- **A formal token pipeline from day one.** Author tokens in a portable
  format and compile per-platform artifacts. Wins with several output targets,
  a designer syncing from a design-tool library, or more than a couple of
  themes — and it is the *correct* end state for a system that grows. Loses
  early, as toolchain weight and a build step maintained before there is a
  second theme or a designer to justify it. The two-tier hand-authored
  structure is what keeps this a later, non-breaking adoption rather than a
  re-modelling.
- **The design tool as the source of truth, synced to code.** Wins as soon as
  there is a dedicated designer and an established design-tool library — the
  semantic tier is the natural sync target, and it removes the class of drift
  where design and code disagree about a value. Loses before a design hire,
  where the sync overhead has no counterparty and the tool's export shape ends
  up dictating the token model.
- **The component library's own theme API, with no token layer of your own.**
  Wins when one library renders essentially the whole product and its theming
  surface is expressive enough for the brand. Loses when a second consumer
  appears that cannot read that library's theme — a native app, a marketing
  site, an email template — because there is then no shared source and the
  values are copied.
- **No tokens at all, with a rebrand rewrite budgeted.** Wins for short-lived
  products and for those where the visual identity is genuinely fixed by
  something outside the team. It is a defensible trade and worth stating as
  one — the failure is not choosing it, it is arriving at it by default and
  then being surprised by the rebrand estimate.
