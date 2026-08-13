---
type: Story
title: {{TITLE}}
description: {{DESCRIPTION}}
tags: []
created: {{DATE}}
generated: { by: {{ACTOR}}, at: {{TIMESTAMP}} }
status: stable
audience: {{AUDIENCE}}
audience_depth: {{AUDIENCE_DEPTH}}
action_ask: {{ACTION_ASK}}
framework: pyramid
format: deck
time_budget: {{TIME_BUDGET}}
html: ../assets/stories/{{SLUG}}.html
sources: []
---

# {{TITLE}}

## Audience

Who they are, what they already believe, and what they can decide. `audience_depth`
and `time_budget` above carry the two answers a re-render cannot recover from prose:
the technical depth the narrative is pitched at, and the minutes (deck) or
scroll-depth (narrative) that set the section count.

## Action ask

The one thing this story asks the audience to do, decide, or believe.

## Framework

Which narrative framework structures this story, and why it fits this audience and ask.

## Outline

1. Beat — the claim it carries.
2. Beat — the claim it carries.

## Narrative

The story itself, every claim cited to an Arche page — `... as decided in [the billing ADR](../concepts/adr-billing.md).`

## Rendered artifact

[Open the rendered story](../assets/stories/{{SLUG}}.html). The `.md` is the source of truth; the HTML is derived.
