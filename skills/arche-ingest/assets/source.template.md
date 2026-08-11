---
type: Source
title: {{TITLE}}
description: {{DESCRIPTION}}
resource: {{RESOURCE}}
tags: []
created: {{DATE}}
generated: { by: {{ACTOR}}, at: {{TIMESTAMP}} }
sources:
  # The `snapshot` entry belongs here ONLY for a web source that also has a local
  # snapshot — i.e. when `resource:` above is the canonical URL. For a file-only
  # source, `resource:` is already the `../raw/…` path, so drop this entry (and the
  # `[^snapshot]` footnote below) rather than duplicating it.
  - id: snapshot
    resource: ../raw/{{SLUG}}.{{EXT}}
    title: Local snapshot
---

# {{TITLE}}

One-paragraph summary of the source (≤ 400 words by default — see SCHEMA).

## Key claims

- Claim, paraphrased.[^snapshot]
- Claim.
- Claim.

## See also

- [Entity this source touches](../entities/example.md)
- [Concept this source touches](../concepts/example.md)

[^snapshot]: Local snapshot
