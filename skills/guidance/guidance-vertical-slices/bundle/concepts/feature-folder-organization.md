---
type: Guidance
title: Organizing an application by feature with a tool-enforced import direction
description: Organize a client application's source by product capability rather than by file role — one folder per feature, a shared tier for cross-feature code, a single checkable sorting rule (knows business logic goes to the feature, dumb visual goes to shared), features as non-importing peers, and an import boundary enforced by a dependency tool rather than by review.
tags: [architecture, frontend, feature-folders, vertical-slice, module-boundaries, import-rules]
created: 2026-08-26
generated: { by: write-guidance/claude-fable-5, at: 2026-08-26T16:22:41Z }
status: stable
stale_after: 2028-09-01
sources:
  - id: bulletproof-react
    resource: https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md
    title: bulletproof-react — Project Structure
  - id: feature-sliced-design
    resource: https://feature-sliced.design/docs/get-started/overview
    title: Feature-Sliced Design — Overview
  - id: bogard-vertical-slice
    resource: https://www.jimmybogard.com/vertical-slice-architecture/
    title: Jimmy Bogard — Vertical Slice Architecture
  - id: dependency-cruiser-rules
    resource: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md
    title: dependency-cruiser — Rules Reference
  - id: parnas-decomposition
    resource: https://dl.acm.org/doi/10.1145/361598.361623
    title: Parnas — On the Criteria To Be Used in Decomposing Systems into Modules
---

# Organizing an application by feature with a tool-enforced import direction

## Technique

Organize an application's source by **product capability**, not by file role. The
top level of the source tree names what the product does, not what kind of file
each thing is.

- **`features/<name>/`** — domain-aware code for one product surface: its views,
  its hooks, its platform glue. A feature is a **non-importing peer**: it never
  reaches into a sibling feature.
- **A shared tier** — cross-feature visual components (including owned design-
  system primitives) and cross-cutting infrastructure (API origin, auth client,
  fetch wrapper, formatting helpers). Shared code knows nothing about any
  feature.
- **A thin route or navigation layer** that only wraps feature views. The
  exemplar is a route file that is a one-line import of a feature's view
  component. When a route file contains logic, the logic belongs in the feature.

The sorting rule is the part that has to be **checkable**, because every file
that lands in the wrong tier does so at a moment when the answer felt obvious:

> **Knows business logic → feature. Dumb visual wrapper → shared.**

"Knows business logic" is testable by a question a reviewer can ask without
context: *does this file mention the domain's vocabulary?* A component that takes
`label` and `onPress` is shared. A component that takes an entity of the domain,
or names one of its states, is a feature's — even if it looks generic, and
especially if it looks generic.

Two refinements earn their keep. First, **cross-cutting business-aware code is
shared infrastructure, not a peer feature.** The gate component that wraps every
authenticated view is the recurring example: making authentication a peer feature
forces every other feature to import it, breaking the peer rule on day one and
forcing a permanent special case into the boundary rule. Classify by *who depends
on it*, not by *whether it knows the domain*. Second, **feature-internal
structure is organic.** A feature starts as flat files and earns a subfolder only
when a category has enough members to warrant one. Mandating a per-feature
segment skeleton means every feature pays a fixed structural cost from its first
file, and most features never grow into it.

Where a shared package holds render-free logic used by more than one application,
give it the **same feature axis** so the two sides are namesakes: the split is
*render-free and portable → the package; renders or is platform glue → the
application's feature folder*, and opening `features/x` on either side shows two
halves of the same capability. Without the mirror, tracing one capability
end-to-end crosses two different organizing axes, which is the specific cost that
makes by-role packages tiring to work in.

**The boundary is enforced by direction, by a tool, not by review.** A dependency
analyzer (dependency-cruiser and equivalents; or a build-level module boundary
system where the ecosystem has one) runs in CI with rules of the form:

- a feature must not import a sibling feature;
- the shared tier must not import any feature (inverted direction);
- nothing may import the route layer (a leaf reaching back into the composition
  root);
- inside a feature-mirrored shared package, feature namespaces must not import
  each other either.

Each rule must be **verified to bite** when authored — write the violating
import, watch it fail, delete it. A rule that has never failed is indistinguishable
from a rule matching nothing, and the second is the common case: rules keyed on a
directory layout that does not exist yet pass vacuously and read as coverage.
Naming these checks, choosing their lane, and tracking whether they still run is
the practice in
`guidance-fitness-functions/concepts/architectural-fitness-functions.md`;
this page only supplies the rules worth naming.

A per-feature public-surface barrel — a feature importable only through its
`index`— is worth encouraging as convention and usually not worth machine-policing
at first: it is real friction (every shared export re-exported) for features that
are consumed once, by their own route. Revisit when a feature grows several
external consumers.

**This is the same move as [REPR endpoint slices](repr-endpoints.md), applied at
the presentation layer.** Slice by capability; keep the slices from importing
each other; make the composition root do nothing but compose. The API side calls
a slice an endpoint directory and enforces it with a no-inline-handlers check;
the client side calls it a feature folder and enforces it with import-direction
rules. Adopting one and not the other is coherent — they are separate decisions
in separate codebases — but a team that has adopted both should say so out loud,
because the shared principle is what makes the two conventions predict each other
for anyone (or any agent) moving between them.

## Applies when

- **The application has more than one distinct product surface**, and a third or
  fourth is coming. One surface plus a login screen does not need a taxonomy.
- **A feature has already precipitated out of a flat folder.** The honest
  trigger: three or four files whose names share a prefix sit scattered among
  unrelated files in one `components/` directory. That cluster is a feature
  asking for a folder, and it is evidence the flat layout has already stopped
  working.
- **More than one application shares logic**, so the axis question has to be
  answered deliberately rather than by accident — otherwise the applications
  organize by feature while the shared package organizes by technical kind, and
  every end-to-end trace crosses axes.
- **A dependency analyzer already runs, or can be added cheaply.** If enforcement
  would mean introducing a second linter into a toolchain that deliberately has
  one, the boundary is a convention and should be described as one; the rule
  below about tooling is then unavailable, and the failure modes get worse.
- **Code will be written by hands that were not in the room** — new contributors
  and coding agents alike. A taxonomy is legible to an agent when it is
  mechanical and enforced; it is invisible when it lives in a review habit.
- **Feature work is parallel.** Two people or two agents adding two surfaces in
  the same week are the case feature folders are for: disjoint directories mean
  near-zero merge conflict surface, which a shared by-role folder cannot give.

## Doesn't apply when

- **The application is small enough that layer folders stay legible end to end.**
  A `components/` + `hooks/` + `lib/` layout that one person can read in a
  sitting is not a problem to be solved. Feature folders cost navigation depth
  and a taxonomy argument per file; below a handful of surfaces those costs
  exceed the benefit. Adopt when the flat folder stops being readable, not
  before — and when you do, migrate the already-formed cluster first as the
  reference refactor rather than migrating everything at once.
- **A full formal methodology is already adopted** — Feature-Sliced Design or a
  comparable framework with its own layers, slices, and segments. Mixing two
  taxonomies is worse than either: files sort by whichever rule the author had
  in mind, and neither rule is reliably true afterward. If a formal methodology
  is in place, follow it. If one is being *considered*, note that its own
  documentation scopes it to rapidly-growing, multi-team projects; the fixed
  per-feature segment skeleton is ceremony a small team pays on every feature
  from day one. The single idea worth taking from it regardless is the enforced
  import direction.
- **The framework's routing idiom already provides the organization and the app
  will never leave that framework.** Route colocation — private component folders
  inside the route tree — is a real answer for a single application whose
  structure genuinely follows its URLs. It loses when logic must be shared across
  routes, and it loses hard when a second application without a route tree has to
  share the organizing principle; the two then diverge in their first idea. Know
  which case you are in before choosing.
- **The product's surfaces are not separable.** Some applications are one deeply
  interconnected canvas — an editor, a map, a timeline — where a "feature" cannot
  be drawn without every feature importing every other. Forcing feature folders
  there produces a boundary rule with a permanent allowlist, which is a
  convention wearing a tool's uniform. Organize by layer or by domain object
  instead, and enforce a direction that is actually true.
- **The team will not enforce the boundary.** Unenforced, the taxonomy decays
  into folders that look like features and import each other freely, which is
  strictly worse than a flat layout: a reader now believes a boundary exists.
  Either wire the tool or describe the layout honestly as a naming convention.
- **A large migration would collide with in-flight work.** This is a timing
  exclusion, not a permanent one. Codify the pattern so new work binds to it,
  write the rules **forward-binding** — keyed on the path convention new code
  will use, so they bind when that code arrives without failing today's layout —
  and schedule the migration as its own focused change. Accept the temporary
  two-shape state knowingly and write down when it ends.

## Trade-offs

**Buys:** one obvious home per product surface, so "where does this go?" has an
answer that does not depend on who is asking. A near-zero merge-conflict surface
between parallel feature work. A taxonomy an agent can follow without
re-deriving it. Deletion becomes cheap and honest — removing a feature is
removing a directory, and whatever is left behind in `shared/` is exactly the
part that was genuinely cross-cutting. And a CI-gated boundary means the peer
property is a fact about the codebase rather than a belief about it.

**Costs:** a per-file sorting decision that must actually be made, and a rule
that must be argued at review when the answer is not obvious. Deliberate
duplication: two features that each need something similar-but-not-identical will
each own their version until the commonality is proven, and the discipline says
to leave it that way rather than hoisting prematurely to `shared/` and coupling
them. Navigation depth. A set of dependency rules to author, verify, and keep
green — including the maintenance when a directory is renamed. And, if a shared
package is feature-mirrored, one capability now lives in two places by design,
which is only a benefit if the split rule (render-free versus renders) is crisp
enough to place any given file without discussion.

The quality attribute this moves is **modifiability**, and specifically the
locality of change: the number of directories a feature change touches. What it
spends is **structural simplicity** — there is more of it — and a small amount
of **build/CI time**. It is a good trade when several surfaces are under
concurrent development and a bad one for a single-surface application.

Two things it does not do. It does not improve runtime behavior; a feature folder
compiles to the same bundle a flat folder would, unless barrels break
tree-shaking, in which case it makes things slightly worse (see below). And it
makes **no claim about deployment granularity** — see the note closing
[the endpoint page](repr-endpoints.md). Feature folders are not micro-frontends,
are not a step toward them, and do not indicate where an application should be
split. Independent deployment is a separate decision with versioning, runtime
integration, and shared-dependency costs of its own.

## Failure modes

- **The shared tier becomes a dumping ground.** This is the characteristic
  failure and the reason the sorting rule exists in a checkable form. Anything
  ambiguous goes to `shared/` because that is the choice nobody argues with in
  review; within a year the shared folder is larger than every feature and is a
  flat sprawl — precisely the thing the taxonomy was adopted to prevent, now with
  extra directories around it. The diagnostic is mechanical and worth running
  periodically: **a shared component that mentions the domain's vocabulary is
  mis-filed.** Grep the shared tier for the domain's nouns and the hits are the
  work list. The rule is not self-enforcing — a dependency tool can prove shared
  code does not *import* a feature while that same code is thick with the
  domain's concepts — so this one is applied by a human at review, and it decays
  the instant nobody is applying it.
- **Cross-feature imports "temporarily" allowed and never removed.** One feature
  needs a component another feature already has; the import is added with a
  comment promising to extract it later. Nothing is extracted. Six months on, the
  features are a graph, the peer rule is fiction, and the extraction is now a
  large refactor nobody will schedule. This is exactly why the boundary is
  tooling-enforced rather than reviewed: the violation is one line in a large
  diff, it is locally correct, and it is invisible to everyone who was not in the
  room for the decision. When the tool fires, the two legitimate answers are hoist
  the shared part into the shared tier, or duplicate it — never an exemption.
- **The rule is added to the tool but never verified to bite.** A glob keyed on a
  path that does not exist, a rule scoped to the wrong workspace, a config that
  silently stops being read. It passes; the dashboard says the boundary is
  guarded; nothing is guarded. Write the violating import once, watch the rule
  fail, then delete it — for every rule, at authoring time. Re-verify after any
  directory rename, which is precisely when a path-keyed rule stops matching.
- **Exemptions accumulate until the rule matches nothing meaningful.** Each
  exception is granted for a real deadline, and the allowlist is never read as a
  whole. The build is green throughout; there is no moment marking when the
  boundary stopped being enforced. Treat the exemption list as an architectural
  artifact — read it at each milestone, and require the decision record to change
  when it grows.
- **A barrel pulls the whole application into the initial bundle.** A shared
  index re-exports everything, one feature imports one symbol from it, and
  tree-shaking fails on a side-effecting module in the chain. First-load size
  jumps, and the regression shows up as a user-facing performance complaint
  rather than as a build error — which makes it the closest thing this practice
  has to a production incident. Keep a bundle-size budget in CI, and prefer deep
  imports over barrels in any path that is code-split.
- **Duplication in the shared tier diverges.** Two near-identical helpers, one
  hoisted and one left in a feature; a defect is fixed in the one the author
  found. The two surfaces now format, round, or validate differently, and the
  discrepancy is reported by a user rather than caught by a test. Deliberate
  duplication is a legitimate choice here, but it must be *known* duplication —
  when you decline to hoist, say so where the duplicate lives.
- **Route or navigation files quietly become the logic layer.** A little
  data-fetching in a route wrapper, then a conditional, then a redirect rule. The
  thin-route-layer property erodes without ever tripping the import rules, which
  only check direction. The observable symptom is a route file longer than a few
  lines; the fix is that the route layer imports a feature view and does nothing
  else.
- **Feature names track screens instead of capabilities.** Folders named after
  navigation destinations rather than after what the product does. The tree then
  reorganizes every time the navigation does, and a capability used by two
  screens has no home — which sends it, inevitably, to the dumping ground above.

## Alternatives considered

- **Organize by file role** (`components/`, `hooks/`, `utils/`) — wins for small
  applications and for libraries, where the consumer's mental model genuinely is
  "what kind of thing is this". Loses at scale for the reason Parnas gave: it
  groups by what changes least (the technical kind) rather than by what changes
  together (the capability), so every feature change fans out across every
  folder.
- **Feature-Sliced Design, full form** — wins for rapidly-growing, multi-team
  codebases where a shared, documented, externally-specified taxonomy is worth
  more than a bespoke one, and where the layer hierarchy resolves genuine
  arguments about what may depend on what. Loses for small teams: the fixed
  segment skeleton is per-feature ceremony from day one, and the layer count
  exceeds the number of distinctions a small application actually has.
- **Route colocation inside the framework's route tree** — wins for a single
  application whose structure genuinely follows its URLs and which will never
  share its organizing principle with a second application. Loses when logic is
  shared across routes (it has no home) and when a non-route-tree application
  must match. Colocating a genuinely route-local component *inside* a feature
  remains fine; it is only the top-level model that is being rejected.
- **A cross-cutting concern as a peer feature** — wins where the concern is used
  by a minority of features and can honestly be a peer. Loses for anything that
  wraps every gated view: every feature would import it, killing the peer rule
  and forcing a permanent special case into the boundary rules. Treat
  everything-depends-on-it code as shared infrastructure regardless of how much
  domain vocabulary it knows.
- **Keep the shared package organized by technical kind** while applications go
  by feature — wins when the package is genuinely a library with external
  consumers who think in kinds. Loses inside one product: two organizing axes
  across one layer means every end-to-end trace crosses axes, and the by-kind
  folders re-become the flat sprawl the applications just escaped.
- **Mandated per-feature segments** (`features/x/{ui,model,api}`) — wins when
  features are large and uniform enough that the skeleton is always filled, and
  when a strict intra-feature dependency rule is wanted. Loses when most features
  are small: it is empty structure paid for on every feature. Organic growth —
  a folder appears when a category has enough members — reaches the same place
  for the features that need it and costs nothing for the ones that do not.
- **A second linter dedicated to module boundaries** — wins when it is the only
  tool that expresses the rule, or when its rule language is materially better
  for the boundaries in play. Loses when a dependency analyzer already runs over
  these directories: a second linter for one rule is a permanent toolchain and
  CI cost, and the rule it expresses is not better for having its own binary.
- **Barrel-only enforcement** (a feature importable only through its public
  index) — wins when features have several external consumers and the public
  surface genuinely needs to be smaller than the file tree. Loses at v1: real
  friction for features consumed once, by their own route. Encourage the barrel
  as convention; police it when a feature's consumer count makes the surface
  worth defining.
