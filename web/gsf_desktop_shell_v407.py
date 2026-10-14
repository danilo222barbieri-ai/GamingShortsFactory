"""GSF V407 desktop shell — production/runtime implementation.

Desktop is a frame around the existing mobile-first app, never a second UI.
On wide screens the Streamlit content is constrained to a phone-like canvas and
the remaining width is used by two large ad rails. Mobile/tablet are untouched.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re
from typing import Any, Mapping


_CLIENT_RE = re.compile(r"^ca-pub-\d{10,20}$")
_SLOT_RE = re.compile(r"^\d{5,20}$")


@dataclass(frozen=True)
class DesktopShellConfig:
    desktop_breakpoint_px: int = 1100
    center_width_px: int = 480
    rail_min_px: int = 220
    rail_max_px: int = 460
    rail_gap_px: int = 24
    outer_gap_px: int = 24
    rail_top_px: int = 20
    center_radius_px: int = 28

    def __post_init__(self) -> None:
        if self.desktop_breakpoint_px < 900:
            raise ValueError("desktop_breakpoint_px must keep tablet/mobile untouched")
        if not 420 <= self.center_width_px <= 520:
            raise ValueError("center_width_px must remain phone-like")
        if self.rail_min_px <= 0 or self.rail_max_px < self.rail_min_px:
            raise ValueError("invalid desktop ad rail bounds")
        if self.rail_gap_px < 12 or self.outer_gap_px < 12:
            raise ValueError("desktop gaps are too small")


def _default_ad_placeholder(side: str) -> str:
    label = "SINISTRA" if side == "left" else "DESTRA"
    return (
        '<div class="gsf-desktop-ad-placeholder">'
        '<span class="gsf-desktop-ad-kicker">AD</span>'
        '<strong>SPAZIO PUBBLICITARIO</strong>'
        f'<small>RAIL {escape(label)}</small>'
        "</div>"
    )


def build_runtime_ad_markup(index: int, environ: Mapping[str, str]) -> str:
    """Build a rail ad using the already-installed V105.7 AdSense bridge.

    `preview` shows a geometry-only placeholder. `live` emits the exact
    `.gsf-v1057-live`/`.gsf-v1057-ad-mount` contract consumed by the existing
    Streamlit AdSense bridge. Invalid live credentials fail closed to no ad.
    """

    idx = int(index)
    if idx < 1:
        raise ValueError("ad slot index must be >= 1")

    mode = str(environ.get("GSF_ADS_MODE", "off") or "off").strip().lower()
    if mode == "preview":
        side = "left" if idx == 1 else "right"
        return _default_ad_placeholder(side)
    if mode != "live":
        return ""

    client = str(environ.get("GSF_ADSENSE_CLIENT", "") or "").strip()
    slot = str(environ.get(f"GSF_ADSENSE_SLOT_{idx}", "") or "").strip()
    if not (_CLIENT_RE.fullmatch(client) and _SLOT_RE.fullmatch(slot)):
        return ""

    return (
        '<div class="gsf-v1057-ad gsf-v1057-live gsf-v407-rail-ad" '
        f'data-ad-client="{escape(client, quote=True)}" '
        f'data-ad-slot="{escape(slot, quote=True)}" '
        f'data-gsf-placement="v407-rail-{idx}">'
        '<div class="gsf-v1057-ad-mount" aria-label="Annuncio Google"></div>'
        "</div>"
    )


def build_desktop_shell_html(
    config: DesktopShellConfig | None = None,
    *,
    left_html: str | None = None,
    right_html: str | None = None,
    hide_empty_rails: bool = False,
) -> str:
    """Return the global V407 desktop frame markup."""

    cfg = config or DesktopShellConfig()
    left_supplied = left_html is not None
    right_supplied = right_html is not None
    left = left_html.strip() if left_html is not None else _default_ad_placeholder("left")
    right = right_html.strip() if right_html is not None else _default_ad_placeholder("right")
    left_empty = hide_empty_rails and left_supplied and not left
    right_empty = hide_empty_rails and right_supplied and not right
    left_class = " gsf-desktop-ad-empty" if left_empty else ""
    right_class = " gsf-desktop-ad-empty" if right_empty else ""

    return f'''<!-- GSF DESKTOP MOBILE SHELL V407 -->
<style id="gsf-desktop-mobile-shell-v407">
:root{{
  --gsf-mobile-canvas:{cfg.center_width_px}px;
  --gsf-rail-min:{cfg.rail_min_px}px;
  --gsf-rail-max:{cfg.rail_max_px}px;
  --gsf-rail-gap:{cfg.rail_gap_px}px;
  --gsf-outer-gap:{cfg.outer_gap_px}px;
  --gsf-shell-radius:{cfg.center_radius_px}px;
}}
.gsf-desktop-ad-rail{{display:none}}

@media (min-width:{cfg.desktop_breakpoint_px}px){{
  html,body{{overflow-x:hidden!important}}
  [data-testid="stAppViewContainer"]{{
    background:
      radial-gradient(circle at 9% 16%,rgba(76,182,255,.15),transparent 26%),
      radial-gradient(circle at 91% 82%,rgba(121,221,203,.13),transparent 28%),
      linear-gradient(135deg,#edf7ff 0%,#f8fbff 48%,#eef9f7 100%)!important;
  }}

  /* The real app stays phone-shaped. No parallel desktop component tree. */
  .block-container{{
    box-sizing:border-box!important;
    max-width:var(--gsf-mobile-canvas)!important;
    width:var(--gsf-mobile-canvas)!important;
    min-height:100vh!important;
    margin-left:auto!important;
    margin-right:auto!important;
    padding-left:16px!important;
    padding-right:16px!important;
    background:
      radial-gradient(circle at 10% 9%,rgba(33,168,255,.13) 0 70px,transparent 72px),
      radial-gradient(circle at 92% 20%,rgba(83,224,234,.14) 0 82px,transparent 84px),
      #f4f9ff!important;
    border-left:1px solid rgba(112,166,201,.16)!important;
    border-right:1px solid rgba(112,166,201,.16)!important;
    box-shadow:0 0 0 1px rgba(255,255,255,.56),0 26px 70px rgba(40,93,133,.16)!important;
  }}

  /* Native Streamlit columns also adopt mobile stacking on desktop. Embedded
     components inherit the 480px parent and therefore fire their mobile CSS. */
  .block-container [data-testid="stHorizontalBlock"]{{
    flex-direction:column!important;
    align-items:stretch!important;
    width:100%!important;
    gap:.55rem!important;
  }}
  .block-container [data-testid="column"]{{
    width:100%!important;
    min-width:0!important;
    flex:1 1 100%!important;
  }}

  .gsf-desktop-ad-rail{{
    display:flex;
    position:fixed;
    z-index:35;
    top:{cfg.rail_top_px}px;
    height:calc(100vh - {cfg.rail_top_px * 2}px);
    width:clamp(
      var(--gsf-rail-min),
      calc((100vw - var(--gsf-mobile-canvas) - (2 * var(--gsf-rail-gap)) - (2 * var(--gsf-outer-gap))) / 2),
      var(--gsf-rail-max)
    );
    align-items:stretch;
    pointer-events:auto;
  }}
  .gsf-desktop-ad-left{{right:calc(50% + (var(--gsf-mobile-canvas) / 2) + var(--gsf-rail-gap))}}
  .gsf-desktop-ad-right{{left:calc(50% + (var(--gsf-mobile-canvas) / 2) + var(--gsf-rail-gap))}}
  .gsf-desktop-ad-empty{{display:none!important}}
  .gsf-desktop-ad-content{{
    width:100%;height:100%;overflow:hidden;border-radius:30px;
    border:1px solid rgba(118,170,203,.22);
    background:rgba(255,255,255,.74);
    box-shadow:0 20px 60px rgba(43,91,127,.14),inset 0 1px 0 rgba(255,255,255,.82);
    backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  }}
  .gsf-desktop-ad-content>iframe,
  .gsf-desktop-ad-content>ins,
  .gsf-desktop-ad-content>[data-ad-provider],
  .gsf-desktop-ad-content>.gsf-v407-rail-ad{{
    display:block;width:100%!important;height:100%!important;border:0;
  }}
  .gsf-v407-rail-ad .gsf-v1057-ad-mount,
  .gsf-v407-rail-ad .adsbygoogle{{display:block!important;width:100%!important;height:100%!important;min-height:100%!important}}
  .gsf-desktop-ad-placeholder{{
    width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;
    gap:9px;text-align:center;color:#60758f;
    background:radial-gradient(circle at 50% 26%,rgba(33,168,255,.10),transparent 31%),linear-gradient(155deg,rgba(255,255,255,.90),rgba(237,248,255,.78));
    font-family:inherit;
  }}
  .gsf-desktop-ad-kicker{{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:#e8f6ff;color:#238fce;font-size:12px;font-weight:900;letter-spacing:.12em}}
  .gsf-desktop-ad-placeholder strong{{font-size:13px;letter-spacing:.08em}}
  .gsf-desktop-ad-placeholder small{{font-size:10px;letter-spacing:.14em;opacity:.72}}
}}
@media (min-width:{cfg.desktop_breakpoint_px}px) and (max-height:720px){{
  .gsf-desktop-ad-rail{{top:12px;height:calc(100vh - 24px)}}
  .gsf-desktop-ad-content{{border-radius:24px}}
}}
</style>
<aside id="gsf-desktop-ad-left" class="gsf-desktop-ad-rail gsf-desktop-ad-left{left_class}" aria-label="Pubblicità sinistra">
  <div class="gsf-desktop-ad-content">{left}</div>
</aside>
<aside id="gsf-desktop-ad-right" class="gsf-desktop-ad-rail gsf-desktop-ad-right{right_class}" aria-label="Pubblicità destra">
  <div class="gsf-desktop-ad-content">{right}</div>
</aside>
'''


def install_desktop_shell(
    st_module: Any,
    config: DesktopShellConfig | None = None,
    *,
    left_html: str | None = None,
    right_html: str | None = None,
    hide_empty_rails: bool = False,
) -> None:
    st_module.markdown(
        build_desktop_shell_html(
            config,
            left_html=left_html,
            right_html=right_html,
            hide_empty_rails=hide_empty_rails,
        ),
        unsafe_allow_html=True,
    )


def install_runtime_desktop_shell(st_module: Any, environ: Mapping[str, str]) -> None:
    """Install V407 using the project's existing AdSense environment contract."""

    install_desktop_shell(
        st_module,
        left_html=build_runtime_ad_markup(1, environ),
        right_html=build_runtime_ad_markup(2, environ),
        hide_empty_rails=True,
    )
