# GSF is mobile-only (V419)

## Decision (owner, 2026-10-17)

The desktop version is closed. Gaming Shorts Factory is a phone app.
Desktop and tablet browsers that open the app receive the mobile-only page
`web/mobile_only_gate.html`: app description, the link to open on the phone
(copy button + QR code), and links to `/privacy` and `/terms`. It also serves as
the public home page that OAuth reviewers (Google, TikTok, Meta) see on desktop.

## Where it is enforced

`web/nginx.conf.template`:

- `$gsf_mobile_client` is 1 for phones only: `Sec-CH-UA-Mobile: ?1`, or a phone
  user agent (iPhone, iPod, Android `… Mobile`, other mobile tokens). iPad,
  Android tablets and other tablets are excluded (regexes are evaluated in order).
- `location = /` and the catch-all `location /` return the gate for any
  non-phone client. In `location = /` the gate comes **after** the OAuth
  callback diversions (`gsfsc_`, `gsfyt_`, `gsfig_`, `gsfacg_`, `gsfacf_`,
  `gsfact_`), so a callback is never gated whatever device finishes it.
- `/__gsf_mobile_gate` is `internal` and `no-store`.
- Legal pages, icons, manifest, push and companion routes are unchanged.

## Removed desktop weight

- V407 desktop frame (480 px canvas + two AdSense rails) is no longer installed
  into Streamlit's `index.html`; `web/gsf_desktop_shell_v407.py` and its test are
  deleted. The V105.7 AdSense bridge for inline slots stays.
- Legacy desktop polish tests (V267/V268) that were not run by CI are deleted.

## Still to remove (blocked by ownership of `app.py`)

- `app.py` picks the desktop Editor 2027 (`/editor-live/`) when the viewport is
  wider than 760 px (phone landscape). It should always use
  `/game-editor-mobile/`; then `web/editor_2027_component/`, `web/editor_2027_embed.py`,
  the `/editor-live/` route and the inline Editor 2027 Streamlit embed can go.
- V267 desktop CSS blocks inside the component pages are inert on phones and can
  be dropped by the owners of those pages.

## Contract

`tests/test_mobile_only_gate.py` (in GSF CI via `pytest tests`): static
contracts plus a behavioural run of the real nginx template against a stub
backend (phones → app; desktop, iPad, Android tablet, curl → gate; legal pages
public; gate not directly addressable). `web/runtime_smoke_v411.py` checks the
same on the production image inside the Production Gate.
