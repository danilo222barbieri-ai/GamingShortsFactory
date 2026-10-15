# Brand token adoption audit — 2026-10-15

Snapshot of how the v1 tokens (see `README.md`) are used in the current code,
taken when the kit was added. It is a baseline for a later migration, not a
change to the runtime UI.

## Numbers

Scope: literal 6-digit hex colors in `app.py`, `gsf_core/**/*.py`, `web/**/*.py`.

| Metric | Value |
|---|---|
| Distinct hex colors | 754 |
| Total literal hex uses | 1,440 |
| Uses matching a v1 token (incl. `#FFFFFF`) | 77 |
| Files that reference `#27AEF3` (primary) | 1 (`app.py`, as `--gsf-blue`) |

`app.py` already defines part of the palette as CSS custom properties
(`--gsf-blue`, `--gsf-ink`, `--purple`), but with names that differ from the
v1 tokens (`--gsf-primary`, `--gsf-ink`, `--gsf-ai`).

## Most frequent off-token colors

| Color | Uses | Closest v1 role (to decide) |
|---|---|---|
| `#F7FCFF`, `#FBFDFF`, `#F8FCFF`, `#F7FBFF`, `#FEFFFF`, `#F8FBFE` | 95 | Surface / Soft background |
| `#22C55E` | 23 | Short green? |
| `#FFD400` | 21 | Warning |
| `#0D2A66`, `#17324A`, `#315D82` | 41 | Ink |
| `#7185A6`, `#6C81A1` | 25 | Muted |
| `#EAF2F7` | 8 | Line |
| `#1877F2` | 9 | Facebook brand color (third-party, keep) |

Many hits live in versioned `web/apply_*` / `web/fix_*` patches, some of which
may be superseded; a migration should start from the CSS actually rendered in
production, not from these raw counts.

## Suggested migration order

1. Load `gsf-brand-tokens.css` once in the global chrome and alias the
   existing `--gsf-blue` / `--purple` variables to the v1 names.
2. Replace near-white backgrounds and the ink/muted variants with tokens.
3. Decide whether `#22C55E` and `#FFD400` become `--gsf-short` / `--gsf-warning`
   or are added as new tokens.
4. Add a CI check that flags new literal hex values outside `design/brand/`.
