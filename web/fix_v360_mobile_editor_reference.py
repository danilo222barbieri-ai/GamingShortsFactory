#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V360_MOBILE_EDITOR_REFERENCE'

PATCH = r'''
<!-- V360_MOBILE_EDITOR_REFERENCE -->
<!-- GSF_V361_EDITOR_REPAIR -->
<style id="v360MobileEditorReference">
#ng27.v326Mobile.v360Reference{
  --v360-player-w:286px;
  width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
  box-sizing:border-box!important;margin:0!important;padding:5px 6px 96px!important;overflow:hidden!important;
  background:
    radial-gradient(circle at 50% 8%,rgba(207,238,251,.96),transparent 34%),
    radial-gradient(circle at 12% 54%,rgba(219,246,255,.72),transparent 32%),
    linear-gradient(180deg,#FBFEFF 0%,#F2FAFE 100%)!important;
}
#ng27.v326Mobile.v360Reference .shell{
  width:100%!important;height:100%!important;min-height:0!important;max-width:460px!important;
  margin:0 auto!important;padding:0!important;overflow:hidden!important;background:transparent!important;
  display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:6px!important;
}
#ng27.v326Mobile.v360Reference .v360EditorHeader{
  width:100%!important;min-height:50px!important;padding:7px 64px 7px 10px!important;
  border:1px solid rgba(151,187,216,.22)!important;border-radius:18px!important;
  background:rgba(255,255,255,.84)!important;box-shadow:0 9px 24px rgba(69,113,151,.08),inset 0 1px 0 rgba(255,255,255,.98)!important;
  -webkit-backdrop-filter:blur(16px)!important;backdrop-filter:blur(16px)!important;
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;gap:0!important;align-items:center!important;
}
#ng27.v326Mobile.v360Reference .v360EditorTitle{min-width:0!important}
#ng27.v326Mobile.v360Reference .v360EditorTitle b{
  display:block!important;color:#0D2D6D!important;font-size:20px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.025em!important;
}
#ng27.v326Mobile.v360Reference .v360EditorTitle span{
  display:block!important;margin-top:4px!important;color:#7184A4!important;font-size:9.8px!important;line-height:1.15!important;font-weight:750!important;
  white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
}
/* Parent shell already owns the close affordance. Keep fullscreen on the real
   player control instead of creating a competing header button. */
#ng27.v326Mobile.v360Reference .v360FullProxy{display:none!important}

#ng27.v326Mobile.v360Reference .cockpit,#ng27.v326Mobile.v360Reference.expanded .cockpit{
  width:100%!important;max-width:460px!important;height:100%!important;min-height:0!important;margin:0 auto!important;padding:0 2px!important;
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:minmax(0,1fr) auto auto!important;
  gap:6px!important;align-items:stretch!important;align-content:stretch!important;justify-items:stretch!important;overflow:hidden!important;
}
/* PLAYER -> ACTIONS -> TIMELINE */
#ng27.v326Mobile.v360Reference .stageWrap{
  grid-row:1!important;width:var(--v360-player-w)!important;max-width:calc(100% - 8px)!important;min-height:0!important;
  margin:0 auto!important;padding:0!important;align-self:start!important;justify-self:center!important;overflow:visible!important;
}
#ng27.v326Mobile.v360Reference .stage.r916,#ng27.v326Mobile.v360Reference.expanded .stage.r916{
  position:relative!important;width:100%!important;max-width:none!important;height:auto!important;aspect-ratio:9/16!important;margin:0!important;
  border-radius:22px!important;border:1px solid rgba(126,207,240,.52)!important;overflow:hidden!important;
  box-shadow:0 12px 30px rgba(43,98,139,.15),0 0 0 4px rgba(255,255,255,.48)!important;
}

/* V325 and V326 both contributed player meta/playback shells. V326 is the
   canonical mobile layer now, so suppress only the older duplicate shells. */
#ng27.v326Mobile.v360Reference .v325PlayerMeta{display:none!important}
#ng27.v326Mobile.v360Reference .v325PlaybackDock{display:none!important}

#ng27.v326Mobile.v360Reference .v326LeftDock{left:8px!important}
#ng27.v326Mobile.v360Reference .v326RightDock{right:8px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock{gap:6px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn{
  width:44px!important;height:52px!important;min-width:44px!important;min-height:52px!important;border-radius:15px!important;
  border:1px solid rgba(255,255,255,.72)!important;
  background:linear-gradient(145deg,rgba(29,54,81,.68),rgba(49,76,105,.54))!important;
  -webkit-backdrop-filter:blur(15px) saturate(1.12)!important;backdrop-filter:blur(15px) saturate(1.12)!important;
  box-shadow:0 7px 18px rgba(10,27,44,.20),inset 0 1px 0 rgba(255,255,255,.26)!important;
}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn .ico{width:19px!important;height:19px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn span{font-size:6.8px!important;font-weight:950!important}
#ng27.v326Mobile.v360Reference .v326Meta{top:9px!important;left:9px!important;right:9px!important}
#ng27.v326Mobile.v360Reference .v326Ratio{margin-left:auto!important;margin-right:44px!important}
#ng27.v326Mobile.v360Reference .v326Time,#ng27.v326Mobile.v360Reference .v326Ratio{
  height:29px!important;padding:0 9px!important;border-radius:12px!important;font-size:8.4px!important;
}

/* Re-enable the existing fullscreen button inside the player. No cloned
   control, no second handler. */
#ng27.v326Mobile.v360Reference #zoomEditorBtn{
  display:flex!important;position:absolute!important;top:9px!important;right:9px!important;z-index:104!important;
  width:38px!important;height:38px!important;min-width:38px!important;min-height:38px!important;
  padding:0!important;border-radius:12px!important;opacity:1!important;pointer-events:auto!important;overflow:visible!important;
  border:1px solid rgba(255,255,255,.68)!important;background:rgba(24,48,74,.64)!important;color:#fff!important;
  -webkit-backdrop-filter:blur(13px)!important;backdrop-filter:blur(13px)!important;
}
#ng27.v326Mobile.v360Reference #zoomEditorBtn .ico{width:18px!important;height:18px!important;margin:auto!important;color:#fff!important}
#ng27.v326Mobile.v360Reference #zoomEditorBtn span{display:none!important}

#ng27.v326Mobile.v360Reference .v326PlaybackDock{bottom:18px!important;gap:10px!important}
#ng27.v326Mobile.v360Reference #playBtn{
  width:52px!important;height:52px!important;min-width:52px!important;min-height:52px!important;
  background:linear-gradient(145deg,#57BCFC,#377CE8)!important;box-shadow:0 8px 22px rgba(17,50,94,.32),inset 0 1px 0 rgba(255,255,255,.42)!important;
}
#ng27.v326Mobile.v360Reference .v326Skip{font-size:22px!important}

#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions{
  grid-row:2!important;width:100%!important;max-width:none!important;min-height:44px!important;margin:0!important;padding:0!important;
  display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:6px!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction{
  min-height:44px!important;height:44px!important;border-radius:15px!important;font-size:9px!important;line-height:1!important;font-weight:950!important;
  box-shadow:0 7px 18px rgba(61,104,145,.08)!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction.primary{
  background:linear-gradient(135deg,#55B8FA,#3E83EC)!important;color:#fff!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction.secondary{
  background:rgba(255,255,255,.92)!important;color:#123B7A!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.timeline{
  grid-row:3!important;width:100%!important;max-width:none!important;min-height:0!important;margin:0!important;padding:7px 8px 6px!important;
  border-radius:16px!important;background:rgba(255,255,255,.76)!important;border:1px solid rgba(151,187,216,.24)!important;
  box-shadow:0 7px 18px rgba(79,118,157,.07),inset 0 1px 0 rgba(255,255,255,.84)!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .tlMeta{margin:0 1px 5px!important;font-size:7.5px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .track{height:36px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .trimRow{margin-top:3px!important;font-size:7px!important}
#ng27.v326Mobile.v360Reference .drawer{
  z-index:180!important;max-height:min(48%,360px)!important;overflow-y:auto!important;overflow-x:hidden!important;
  border-radius:18px!important;box-shadow:0 14px 34px rgba(36,75,112,.18)!important;
}

@media(max-width:390px){
  #ng27.v326Mobile.v360Reference{padding:4px 5px 94px!important}
  #ng27.v326Mobile.v360Reference .v360EditorHeader{min-height:48px!important;padding:6px 60px 6px 9px!important}
  #ng27.v326Mobile.v360Reference .v360EditorTitle b{font-size:19px!important}
  #ng27.v326Mobile.v360Reference .v360EditorTitle span{font-size:9px!important}
  #ng27.v326Mobile.v360Reference .v326ToolDock .railBtn{width:42px!important;height:49px!important;min-width:42px!important;min-height:49px!important;border-radius:14px!important}
  #ng27.v326Mobile.v360Reference .v326ToolDock .railBtn .ico{width:18px!important;height:18px!important}
  #ng27.v326Mobile.v360Reference .v326ToolDock .railBtn span{font-size:6.5px!important}
  #ng27.v326Mobile.v360Reference #playBtn{width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important}
  #ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction{height:42px!important;min-height:42px!important;font-size:8.5px!important}
  #ng27.v326Mobile.v360Reference .cockpit>.timeline .track{height:32px!important}
}
</style>
<script id="v360MobileEditorReferenceRuntime">
(()=>{
  const root=document.getElementById('ng27');
  if(!root)return;
  const shell=root.querySelector('.shell');
  const cockpit=root.querySelector('.cockpit');
  const actions=root.querySelector('#v323EditorActions');
  const timeline=root.querySelector('.timeline');
  const stage=root.querySelector('#stage');
  const fullBtn=root.querySelector('#zoomEditorBtn');
  if(!shell||!cockpit||!actions||!timeline||!stage)return;

  function isMobile(){
    const P=window.parent;
    const w=Number(P&&P.innerWidth)||Number(window.innerWidth)||9999;
    return w<=760 || (!!navigator.maxTouchPoints && w<=1024);
  }

  function ensureHeader(){
    let header=shell.querySelector('.v360EditorHeader');
    if(header)return header;
    header=document.createElement('div');
    header.className='v360EditorHeader';
    header.innerHTML='<div class="v360EditorTitle"><b>Game Editor</b><span>Il tuo gameplay resta nel progetto mentre modifichi.</span></div><button class="v360FullProxy" type="button" aria-label="Apri editor a schermo intero"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4H4v4M16 4h4v4M20 16v4h-4M4 16v4h4"/></svg><span>FULL</span></button>';
    shell.insertBefore(header,cockpit);
    const proxy=header.querySelector('.v360FullProxy');
    if(proxy)proxy.addEventListener('click',()=>{if(fullBtn)fullBtn.click()});
    return header;
  }

  function v360FitLayout(){
    const mobile=isMobile();
    root.classList.toggle('v360Reference',mobile);
    if(!mobile)return;
    const header=ensureHeader();
    const shellH=Math.max(360,Math.floor(shell.getBoundingClientRect().height||root.getBoundingClientRect().height||560));
    const shellW=Math.max(260,Math.floor(shell.getBoundingClientRect().width||root.getBoundingClientRect().width||360));
    const headerH=Math.max(48,Math.ceil(header.getBoundingClientRect().height||50));
    const actionsH=Math.max(42,Math.ceil(actions.getBoundingClientRect().height||44));
    const timelineH=Math.max(68,Math.ceil(timeline.getBoundingClientRect().height||78));
    const verticalGap=18;
    const availableH=Math.max(250,shellH-headerH-actionsH-timelineH-verticalGap);
    const maxByWidth=Math.max(210,Math.min(340,shellW-18));
    const targetW=Math.max(210,Math.min(maxByWidth,Math.floor(availableH*9/16)));
    root.style.setProperty('--v360-player-w',targetW+'px');
  }

  let raf=0;
  function schedule(){
    cancelAnimationFrame(raf);
    raf=requestAnimationFrame(()=>requestAnimationFrame(v360FitLayout));
  }

  v360FitLayout();
  setTimeout(schedule,80);
  setTimeout(schedule,320);
  setTimeout(schedule,900);
  window.addEventListener('resize',schedule,{passive:true});
  try{new ResizeObserver(schedule).observe(root);}catch(_e){}
  try{new MutationObserver(schedule).observe(root,{attributes:true,attributeFilter:['class']});}catch(_e){}
})();
</script>
'''


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    required = (
        'id="ng27"',
        'id="v326MobileEditorExact"',
        'id="v323EditorActions"',
        'id="zoomEditorBtn"',
        'id="stage"',
        'data-panel="frame"',
        'data-panel="caption"',
        'data-panel="look"',
        'data-panel="audio"',
        'data-panel="vision"',
    )
    for anchor in required:
        if anchor not in text:
            raise RuntimeError('V360 missing editor anchor: ' + anchor)
    if '</body>' not in text:
        raise RuntimeError('V360 editor body anchor missing')
    return text.replace('</body>', PATCH + '\n</body>', 1)


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/editor_2027_component/index.html')
    if not path.is_file():
        raise SystemExit('V360 editor target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')
    print('V360/V361 mobile editor reference applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
