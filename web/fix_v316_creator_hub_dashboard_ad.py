#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys

STYLE_ID = 'v316HubDashboardAd'
AD_ID = 'hubDashboardAd'
AD_HTML = '<div id="hubDashboardAd" class="hubDashboardAd" data-ad-slot="hub-dashboard-mobile" aria-label="Pubblicità"><span>Pubblicità</span></div>'

STYLE = r'''<style id="v316HubDashboardAd">
/* V316: fill the mobile Creator Hub dashboard gap with a compact ad slot. */
#hub .hubDashboardAd{display:none}
@media(max-width:767px){
  #hub .view[data-view="dashboard"] .dashboard{grid-template-rows:136px minmax(0,1fr) 66px!important;gap:10px!important}
  #hub .view[data-view="dashboard"] .hubDashboardAd{display:flex!important;width:100%!important;height:66px!important;min-height:66px!important;box-sizing:border-box!important;align-items:center!important;justify-content:center!important;margin:0!important;padding:0 14px!important;border:1px solid rgba(143,181,216,.18)!important;border-radius:20px!important;background:linear-gradient(135deg,rgba(247,252,255,.96),rgba(239,248,255,.92) 52%,rgba(241,251,247,.93))!important;box-shadow:0 10px 24px rgba(61,104,145,.055),inset 0 1px 0 rgba(255,255,255,.98)!important;color:#8a9bb1!important;font-size:10px!important;font-weight:850!important;letter-spacing:.08em!important;text-transform:uppercase!important;overflow:hidden!important}
  #hub .view[data-view="dashboard"] .hubDashboardAd span{opacity:.82!important}
}
@media(max-width:767px) and (max-height:760px){
  #hub .view[data-view="dashboard"] .dashboard{grid-template-rows:126px minmax(0,1fr) 50px!important;gap:8px!important}
  #hub .view[data-view="dashboard"] .profileCard{height:126px!important;min-height:126px!important}
  #hub .view[data-view="dashboard"] .hubDashboardAd{height:50px!important;min-height:50px!important;border-radius:17px!important;font-size:9px!important}
}
</style>'''

def _remove_existing(text: str) -> str:
    text = re.sub(r'<style id="' + re.escape(STYLE_ID) + r'">.*?</style>\n?', '', text, count=1, flags=re.DOTALL)
    text = re.sub(r'\s*<div id="' + re.escape(AD_ID) + r'"[^>]*>.*?</div>', '', text, count=1, flags=re.DOTALL)
    return text

def _find_matching_div_end(text: str, start: int) -> int:
    depth=0;token=re.compile(r'<div\b[^>]*>|</div\s*>',re.IGNORECASE)
    for match in token.finditer(text,start):
        if match.group(0).lower().startswith('</div'):
            depth-=1
            if depth==0:return match.end()
        else:depth+=1
    raise RuntimeError('V316 dashboard folders closing div missing')

def patch_text(text: str) -> str:
    if 'V311 APPROVED CREATOR REFERENCE' not in text:raise RuntimeError('V316 requires normalized V311 Creator Hub')
    if 'data-view="dashboard"' not in text or 'data-folder="live"' not in text:raise RuntimeError('V316 dashboard/live anchors missing')
    out=_remove_existing(text)
    if '</head>' not in out:raise RuntimeError('V316 </head> anchor missing')
    out=out.replace('</head>',STYLE+'\n</head>',1)
    dashboard=out.find('data-view="dashboard"');folders=out.find('<div class="folders"',dashboard)
    if folders<0:raise RuntimeError('V316 dashboard folders anchor missing')
    folders_end=_find_matching_div_end(out,folders)
    return out[:folders_end]+AD_HTML+out[folders_end:]

def _load_patch(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def _apply_v317(hub: Path) -> None:
    web_root=hub.parents[1]
    patch=web_root/'fix_v317_compact_ai_selected_short.py'
    ai=web_root/'ai_v221_component'/'index.html'
    if not patch.is_file():raise RuntimeError('V317 patch missing: '+str(patch))
    if not ai.is_file():raise RuntimeError('V317 AI target missing: '+str(ai))
    mod=_load_patch(patch,'v317_compact_ai_selected_short')
    before=ai.read_text(encoding='utf-8');after=mod.patch_text(before);ai.write_text(after,encoding='utf-8')
    print('V317 compact AI + selected short page applied from V316 changed=',before!=after,flush=True)

def _apply_v318(hub: Path) -> None:
    patch=hub.parents[1]/'fix_v318_hub_fill_live_fit.py'
    if not patch.is_file():raise RuntimeError('V318 Hub fit patch missing: '+str(patch))
    mod=_load_patch(patch,'v318_hub_fill_live_fit')
    before=hub.read_text(encoding='utf-8');after=mod.patch_text(before);hub.write_text(after,encoding='utf-8')
    print('V318 Hub fill + Live viewport fit applied from V316 changed=',before!=after,flush=True)

def main() -> None:
    hub=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not hub.is_file():raise SystemExit(f'V316 Hub missing: {hub}')
    before=hub.read_text(encoding='utf-8');after=patch_text(before);hub.write_text(after,encoding='utf-8')
    print('V316 Creator Hub dashboard ad applied changed=',before!=after,flush=True)
    _apply_v317(hub)
    _apply_v318(hub)

if __name__=='__main__':main()
