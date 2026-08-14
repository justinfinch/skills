---
type: Architecture Requirements Document
title: {{TITLE}}
description: {{DESCRIPTION}}
tags: []
created: {{DATE}}
generated: { by: {{ACTOR}}, at: {{TIMESTAMP}} }
status: draft
sources: []
---

# {{TITLE}}

What any architecture for {{SYSTEM}} must satisfy. Pairs with [the solution architecture](./sad-{{SYSTEM}}.md).

## Stakeholders

- Role — what they need from this system and how they judge it.

## Functional requirements

- Requirement, stated as a capability.

## Quality attributes

Each as stimulus → environment → response → measure.

| Attribute | Stimulus | Environment | Response | Measure |
| :--- | :--- | :--- | :--- | :--- |
| Availability | Node fails | Normal load | Fail over | < 30s, no data loss |

## Constraints

- Constraint, and who imposed it.

## Assumptions

- Assumption, and what breaks if it is wrong.

## Risks

- Risk, its likelihood, and its impact.
