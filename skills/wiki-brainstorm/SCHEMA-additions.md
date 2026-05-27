# Adding brainstorm support to an existing wiki

If your `./wiki/SCHEMA.md` predates the `brainstorm` page type, append the changes below before running `/wiki-brainstorm`. New wikis bootstrapped with `/wiki-init` ship with brainstorm support already wired in.

Show this file to the user during Phase 0 preflight and ask permission before editing their SCHEMA.md.

---

## 1. Page types table

Add this row to the **Page types** table in SCHEMA.md:

| Type       | Path                     | Purpose                                                                                                              |
| :--------- | :----------------------- | :------------------------------------------------------------------------------------------------------------------- |
| brainstorm | `brainstorms/<slug>.md`  | Captured ideation session: full idea inventory, themes, technique narrative; cites concept/entity pages (and is cited by them) |

## 2. Slug rules

Append to the **Slug rules** section:

> - Brainstorms re-run on the same topic use `-session-N` suffixes (e.g., `auth-rewrite.md`, then `auth-rewrite-session-2.md`). Date stays in frontmatter only — the no-dates-in-filename rule still holds.

## 3. Operations summary

Append to the **Operations summary** section:

> - **brainstorm**: facilitated ideation session. Reads wiki context (relevant entity/concept/query/prior-brainstorm pages) → runs interactive ideation with the user → files the session as `brainstorms/<slug>.md` with the full idea inventory and technique narrative → promotes user-selected top ideas to concept or entity pages with citations back → updates index and log. Aims for 100+ ideas before organization. See `/wiki-brainstorm`.

## 4. log.md ops list

Update the list of valid log ops:

> Ops: `ingest`, `query`, `lint`, `manual` (human edit), `init`, `brainstorm`.

## 5. index.md (optional, but recommended)

Add a `## Brainstorms` section to `index.md`, alongside Sources / Entities / Concepts / Queries. If you don't, `/wiki-brainstorm` will create the section on the first run.
