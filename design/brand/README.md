# Gaming Shorts Factory — Mini Design System v1

## Logo
Official direction: wordmark only, **GAMING SHORTS FACTORY**.
- `gsf-wordmark.svg`: primary version for light surfaces.
- `gsf-wordmark-on-dark.svg`: version for dark surfaces.
- No separate icon is defined as part of the official brand mark.

## Official color tokens
| Role | Token | Value |
|---|---|---|
| Primary | `--gsf-primary` | `#27AEF3` |
| Primary light | `--gsf-primary-light` | `#79D2FF` |
| Cyan / mint | `--gsf-cyan` | `#53E0EA` |
| Crea con IA | `--gsf-ai` | `#9D82FF` |
| Game Editor | `--gsf-editor` | `#27AEF3` |
| Crea Short | `--gsf-short` | `#5ED6A0` |
| Warning | `--gsf-warning` | `#FFD84D` |
| Danger | `--gsf-danger` | `#FF6673` |
| Soft background | `--gsf-bg-soft` | `#EEF9FF` |
| Border | `--gsf-line` | `#D9EFFB` |
| Main text | `--gsf-ink` | `#10283D` |
| Secondary text | `--gsf-muted` | `#6D8497` |

## Typography
Canonical stack:

```css
font-family: "Avenir Next","SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
```

Use **Avenir Next** when available. On Apple systems the stack naturally falls back to SF Pro; elsewhere it falls back to the native system UI font.

No font binaries are included in this kit.

## Usage rules
- Primary actions and navigation: GSF Primary.
- AI-specific controls/highlights: AI purple.
- Editor-specific controls/highlights: Editor blue.
- Publishing / Short-specific controls/highlights: Short green.
- Keep body copy in GSF Ink; secondary copy in GSF Muted.
- Use Soft Background for light panels and White for cards.
- Prefer the shared tokens over literal hex values in page code.
- Wordmark clear space: at least the height of the capital “G” / 4 around the mark.
- Do not add a separate symbol to the wordmark unless the brand direction is intentionally changed.

## Files
- `gsf-wordmark.svg`
- `gsf-wordmark-on-dark.svg`
- `gsf-brand-tokens.css`
- `gsf-brand-tokens.json`
