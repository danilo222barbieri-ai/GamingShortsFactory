#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V360_MOBILE_EDITOR_REFERENCE'

PATCH = r'''
<!-- V360_MOBILE_EDITOR_REFERENCE -->
<style id="v360MobileEditorReference">
#ng27.v326Mobile.v360Reference{
  --v360-player-w:286px;
  --v360-bottom-gap:4px;
  width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
  margin:0!important;padding:6px 7px var(--v360-bottom-gap)!important;overflow:hidden!important;
  background:
    radial-gradient(circle at 50% 8%,rgba(207,238,251,.96),transparent 34%),
    radial-gradient(circle at 12% 54%,rgba(219,246,255,.72),transparent 32%),
    linear-gradient(180deg,#FBFEFF 0%,#F2FAFE 100%)!important;
}
#ng27.v326Mobile.v360Reference .shell{
  width:100%!important;height:100%!important;min-height:0!important;max-width:460px!important;
  margin:0 auto!important;padding:0!important;overflow:hidden!important;background:transparent!important;
  display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:8px!important;
}
#ng27.v326Mobile.v360Reference .v360EditorHeader{
  width:100%!important;min-height:56px!important;padding:8px 10px 8px 12px!important;
  border:1px solid rgba(151,187,216,.22)!important;border-radius:20px!important;
  background:rgba(255,255,255,.84)!important;box-shadow:0 9px 24px rgba(69,113,151,.08),inset 0 1px 0 rgba(255,255,255,.98)!important;
  -webkit-backdrop-filter:blur(16px)!important;backdrop-filter:blur(16px)!important;
  display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;gap:10px!important;align-items:center!important;
}
#ng27.v326Mobile.v360Reference .v360EditorTitle{min-width:0!important}
#ng27.v326Mobile.v360Reference .v360EditorTitle b{
  display:block!important;color:#0D2D6D!important;font-size:22px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.025em!important;
}
#ng27.v326Mobile.v360Reference .v360EditorTitle span{
  display:block!important;margin-top:5px!important;color:#7184A4!important;font-size:10.5px!important;line-height:1.15!important;font-weight:750!important;
  white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
}
#ng27.v326Mobile.v360Reference .v360FullProxy{
  height:42px!important;min-width:88px!important;padding:0 14px!important;border-radius:15px!important;
  border:1px solid rgba(151,187,216,.24)!important;background:rgba(255,255,255,.92)!important;color:#385C9C!important;
  display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important;
  font-size:12px!important;line-height:1!important;font-weight:950!important;letter-spacing:.02em!important;
  box-shadow:0 7px 18px rgba(61,104,145,.08)!important;
}
#ng27.v326Mobile.v360Reference .v360FullProxy svg{width:18px!important;height:18px!important;fill:none!important;stroke:currentColor!important;stroke-width:2!important}
#ng27.v326Mobile.v360Reference #zoomEditorBtn{opacity:0!important;pointer-events:none!important;width:1px!important;height:1px!important;min-width:1px!important;overflow:hidden!important}

#ng27.v326Mobile.v360Reference .cockpit,#ng27.v326Mobile.v360Reference.expanded .cockpit{
  width:100%!important;max-width:460px!important;height:100%!important;min-height:0!important;margin:0 auto!important;padding:0 2px!important;
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;grid-template-rows:minmax(0,1fr) auto auto!important;
  gap:8px!important;align-items:stretch!important;align-content:stretch!important;justify-items:stretch!important;overflow:hidden!important;
}
/* PLAYER -> ACTIONS -> TIMELINE */
#ng27.v326Mobile.v360Reference .stageWrap{
  grid-row:1!important;width:var(--v360-player-w)!important;max-width:calc(100% - 6px)!important;min-height:0!important;
  margin:0 auto!important;padding:0!important;align-self:start!important;justify-self:center!important;overflow:visible!important;
}
#ng27.v326Mobile.v360Reference .stage.r916,#ng27.v326Mobile.v360Reference.expanded .stage.r916{
  width:100%!important;max-width:none!important;height:auto!important;aspect-ratio:9/16!important;margin:0!important;
  border-radius:24px!important;border:1px solid rgba(126,207,240,.52)!important;overflow:hidden!important;
  box-shadow:0 14px 34px rgba(43,98,139,.16),0 0 0 5px rgba(255,255,255,.50)!important;
}
#ng27.v326Mobile.v360Reference .v326LeftDock{left:8px!important}
#ng27.v326Mobile.v360Reference .v326RightDock{right:8px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock{gap:8px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn{
  width:50px!important;height:60px!important;min-width:50px!important;min-height:60px!important;border-radius:18px!important;
  border:1px solid rgba(255,255,255,.72)!important;
  background:linear-gradient(145deg,rgba(29,54,81,.68),rgba(49,76,105,.54))!important;
  -webkit-backdrop-filter:blur(15px) saturate(1.12)!important;backdrop-filter:blur(15px) saturate(1.12)!important;
  box-shadow:0 8px 21px rgba(10,27,44,.22),inset 0 1px 0 rgba(255,255,255,.26)!important;
}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn .ico{width:22px!important;height:22px!important}
#ng27.v326Mobile.v360Reference .v326ToolDock .railBtn span{font-size:7.6px!important;font-weight:950!important}
#ng27.v326Mobile.v360Reference .v326Meta{top:10px!important;left:10px!important;right:10px!important}
#ng27.v326Mobile.v360Reference .v326Ratio{margin-left:auto!important;margin-right:0!important}
#ng27.v326Mobile.v360Reference .v326Time,#ng27.v326Mobile.v360Reference .v326Ratio{
  height:31px!important;padding:0 10px!important;border-radius:13px!important;font-size:8.9px!important;
}
#ng27.v326Mobile.v360Reference .v326PlaybackDock{bottom:24px!important;gap:13px!important}
#ng27.v326Mobile.v360Reference #playBtn{
  width:58px!important;height:58px!important;min-width:58px!important;min-height:58px!important;
  background:linear-gradient(145deg,#57BCFC,#377CE8)!important;box-shadow:0 9px 25px rgba(17,50,94,.34),inset 0 1px 0 rgba(255,255,255,.42)!important;
}
#ng27.v326Mobile.v360Reference .v326Skip{font-size:24px!important}

#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions{
  grid-row:2!important;width:100%!important;max-width:none!important;min-height:50px!important;margin:0!important;padding:0!important;
  display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:8px!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction{
  min-height:50px!important;height:50px!important;border-radius:17px!important;font-size:10px!important;line-height:1!important;font-weight:950!important;
  box-shadow:0 8px 20px rgba(61,104,145,.09)!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction.primary{
  background:linear-gradient(135deg,#55B8FA,#3E83EC)!important;color:#fff!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction.secondary{
  background:rgba(255,255,255,.92)!important;color:#123B7A!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.timeline{
  grid-row:3!important;width:100%!important;max-width:none!important;min-height:0!important;margin:0!important;padding:8px 9px 7px!important;
  border-radius:18px!important;background:rgba(255,255,255,.76)!important;border:1px solid rgba(151,187,216,.24)!important;
  box-shadow:0 8px 20px rgba(79,118,157,.07),inset 0 1px 0 rgba(255,255,255,.84)!important;
}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .tlMeta{margin:0 2px 6px!important;font-size:8px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .track{height:48px!important}
#ng27.v326Mobile.v360Reference .cockpit>.timeline .trimRow{margin-top:4px!important;font-size:7.4px!important}
#ng27.v326Mobile.v360Reference .drawer{
  z-index:180!important;max-height:min(48%,360px)!important;overflow-y:auto!important;overflow-x:hidden!important;
  border-radius:18px!important;box-shadow:0 14px 34px rgba(36,75,112,.18)!important;
}

@media(max-width:390px){
  #ng27.v326Mobile.v360Reference{padding-left:5px!important;padding-right:5px!important}
  #ng27.v326Mobile.v360Reference .v360EditorHeader{min-height:52px!important;padding:7px 8px 7px 10px!important}
  #ng27.v326Mobile.v360Reference .v360EditorTitle b{font-size:20px!important}
  #ng27.v326Mobile.v360Reference .v360EditorTitle span{font-size:9.4px!important}
  #ng27.v326Mobile.v360Reference .v360FullProxy{height:39px!important;min-width:78px!important;padding:0 11px!important;font-size:10.5px!important}
  #ng27.v326Mobile.v360Reference .v326ToolDock .railBtn{width:46px!important;height:55px!important;min-width:46px!important;min-height:55px!important;border-radius:16px!important}
  #ng27.v326Mobile.v360Reference .v326ToolDock .railBtn .ico{width:20px!important;height:20px!important}
  #ng27.v326Mobile.v360Reference .v326ToolDock .railBtn span{font-size:7px!important}
  #ng27.v326Mobile.v360Reference #playBtn{width:54px!important;height:54px!important;min-width:54px!important;min-height:54px!important}
  #ng27.v326Mobile.v360Reference .cockpit>.v323EditorActions .v323EditorAction{height:46px!important;min-height:46px!important;font-size:9px!important}
  #ng27.v326Mobile.v360Reference .cockpit>.timeline .track{height:42px!important}
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
    const shellH=Math.max(420,Math.floor(shell.getBoundingClientRect().height||root.getBoundingClientRect().height||620));
    const shellW=Math.max(260,Math.floor(shell.getBoundingClientRect().width||root.getBoundingClientRect().width||360));
    const headerH=Math.max(50,Math.ceil(header.getBoundingClientRect().height||56));
    const actionsH=Math.max(46,Math.ceil(actions.getBoundingClientRect().height||50));
    const timelineH=Math.max(82,Math.ceil(timeline.getBoundingClientRect().height||94));
    const floorGap=Math.max(4,Math.min(8,Math.round(shellH*.008)));
    root.style.setProperty('--v360-bottom-gap',floorGap+'px');
    const verticalGap=24;
    const availableH=Math.max(300,shellH-headerH-actionsH-timelineH-verticalGap-floorGap);
    const maxByWidth=Math.max(220,Math.min(360,shellW-18));
    const targetW=Math.max(220,Math.min(maxByWidth,Math.floor(availableH*9/16)));
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
  try{
    new ResizeObserver(schedule).observe(root);
  }catch(_e){}
  try{
    new MutationObserver(schedule).observe(root,{attributes:true,attributeFilter:['class']});
  }catch(_e){}
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
    print('V360 mobile editor reference applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
