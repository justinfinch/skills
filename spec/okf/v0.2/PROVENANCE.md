# Provenance — Open Knowledge Format v0.2

Vendored, unmodified, so that every `§`-citation in this repo resolves without a
network fetch and so the pin survives upstream force-pushes, renames, or
renumbering across spec versions.

## Upstream

| | |
| :--- | :--- |
| Repository | [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog) |
| Commit | `3fcbb9f` |
| Path | `okf/SPEC.md` |
| Permalink | <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/3fcbb9f/okf/SPEC.md> |
| Upstream license | Apache-2.0 (`LICENSE.md` at repo root, vendored here as `LICENSE`) |
| Retrieved | 2026-08-13 |

## Files

| File | Bytes | SHA-256 |
| :--- | ---: | :--- |
| `SPEC.md` | 37544 | `5a3311d270bebb16d558010e75064f5b75323f284992641732b1c8097511f948` |
| `LICENSE` | 11359 | `8c6db340475136df3c1201d458fa5755698eace76e510471ecc9d857d6083dac` |

**Modifications: none.** Both files are byte-for-byte as retrieved.
`tools/test_spec_pin.py` asserts these digests on every test run, so an
accidental edit fails the suite rather than silently turning the pin into a
stale photocopy.

## Licensing

The vendored spec and its license are Apache-2.0, and stay quarantined in this
directory. The rest of this repository is MIT (see the root `LICENSE`). Nothing
here is relicensed; nothing outside here is Apache-2.0.

## Why a copy rather than a link

1. **Citations resolve locally.** This repo cites §2, §3.1, §5, §5.1, §5.3, §7,
   §8, §9, §11, §11.1, and §11.2 across `arche-lint`'s conformance matrix, the
   `arche-init` SCHEMA template, and `tools/okf_conformance.py`. Without a local
   copy none of them is checkable by a reader — or a review agent — offline.
2. **Section numbers are not stable across versions.** They renumber between
   spec revisions, so a citation is only meaningful against the exact revision it
   was written for. The pin is what makes `§11.2` mean something.
3. **Upstream is live.** The knowledge-catalog repo is active and unarchived, so
   the pinned commit is a moving target's snapshot, not a settled artifact.

## Upgrading to a later OKF version

Do not edit this directory. Add a sibling — `spec/okf/v0.3/` — with its own
`SPEC.md`, `LICENSE`, and `PROVENANCE.md`, then diff the two and work the delta
through `skills/arche-lint/references/OKF-CONFORMANCE.md`. Keeping both on disk
is what makes `arche-lint`'s version-skew check (SKILL.md check 8) a diff you
can run rather than a claim you have to trust. `SC1` in the conformance matrix
is the repair that carries an existing Arche across the gap.
