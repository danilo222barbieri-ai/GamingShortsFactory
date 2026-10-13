#!/usr/bin/env python3
"""V403 final visual ownership fixes.

Applied after apply_v403_flow and all historical surface gates. It retires the
legacy inline AI results panel without deleting the DOM required by V319/V320
boot checks, and ensures V403 pre-render wins over the V396 mobile publish skin.
"""
from __future__ import annotations

from pathlib import Path
import sys

MARK_AI = "V403_MOTORI_RESULTS_RETIRED"
MARK_SHARE = "V403_SHARE_V396_OVERRIDE"
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("/app")
AI = ROOT / "web/ai_v221_component/index.html"
SHARE = ROOT / "web/share_v156_component/index.html"

AI_BLOCK = r'''
<style id="v403MotoriResultsRetired">
/* V403_MOTORI_RESULTS_RETIRED */
#ai221>.panel:has(.moments),
#ai221 .v403LegacyMomentsRetired,
#ai221 .selectedShortPage,
#ai221 .momentNextActions,
#ai221 .momentFullscreen{
  display:none!important;
  visibility:hidden!important;
  pointer-events:none!important;
}
</style>
<script id="v403MotoriResultsRetiredRuntime">
(()=>{
 if(window.__GSF_V403_RESULTS_RETIRED)return;window.__GSF_V403_RESULTS_RETIRED=true;
 const retire=()=>{
   document.querySelectorAll('#ai221 .moments').forEach(el=>{
     const panel=el.closest('.panel');
     if(panel)panel.classList.add('v403LegacyMomentsRetired');
   });
   document.querySelectorAll('#ai221 .selectedShortPage,#ai221 .momentNextActions,#ai221 .momentFullscreen').forEach(el=>el.classList.add('v403LegacyMomentsRetired'));
 };
 retire();
 new MutationObserver(retire).observe(document.getElementById('ai221')||document.body,{childList:true,subtree:true});
})();
</script>
'''

SHARE_BLOCK = r'''
<style id="v403ShareV396Override">
/* V403_SHARE_V396_OVERRIDE */
#share[data-v403-state="pre-render"] #v403CreateShortPre{visibility:visible}
#share[data-v403-state="ready"] #v403CreateShortPre{visibility:hidden}
@media(max-width:760px){
  #share.v403PreRender.v396MobileMode>#v396MobilePublishSurface,
  #share.v403PreRender>#v396MobilePublishSurface,
  #share[data-v403-state="pre-render"]>#v396MobilePublishSurface{
    display:none!important;
    visibility:hidden!important;
    pointer-events:none!important;
  }
  #share.v403PreRender.v396MobileMode>#v403CreateShortPre,
  #share.v403PreRender>#v403CreateShortPre,
  #share[data-v403-state="pre-render"]>#v403CreateShortPre{
    display:grid!important;
    visibility:visible!important;
    pointer-events:auto!important;
  }
  #share.v403Ready.v396MobileMode>#v396MobilePublishSurface,
  #share[data-v403-state="ready"].v396MobileMode>#v396MobilePublishSurface{
    display:grid!important;
    visibility:visible!important;
    pointer-events:auto!important;
  }
}
</style>
'''


def patch_ai_text(text: str) -> str:
    if MARK_AI in text:
        return text
    if 'id="v403MotoriRuntime"' not in text:
        raise RuntimeError("V403 Motori runtime must be applied first")
    if "</body>" not in text:
        raise RuntimeError("V403 AI body anchor missing")
    return text.replace("</body>", AI_BLOCK + "\n</body>", 1)


def patch_share_text(text: str) -> str:
    if MARK_SHARE in text:
        return text
    if 'id="v403UnifiedCreateShortRuntime"' not in text:
        raise RuntimeError("V403 unified Short runtime must be applied first")
    if "</head>" not in text:
        raise RuntimeError("V403 Share head anchor missing")
    return text.replace("</head>", SHARE_BLOCK + "\n</head>", 1)


def _write(path: Path, fn, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"V403 missing {label}: {path}")
    before = path.read_text(encoding="utf-8")
    after = fn(before)
    path.write_text(after, encoding="utf-8")
    print(f"V403 {label} changed={before != after}", flush=True)


def main() -> None:
    _write(AI, patch_ai_text, "Motori result retirement")
    _write(SHARE, patch_share_text, "V396/V403 Short ownership")
    print("V403 SURFACE COLLISIONS: PASS", flush=True)


if __name__ == "__main__":
    main()
