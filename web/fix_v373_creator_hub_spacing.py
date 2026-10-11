#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

MARK='V373_CREATOR_HUB_HEADER_BREATH'

PATCH=r'''
<!-- V373_CREATOR_HUB_HEADER_BREATH -->
<style id="v373CreatorHubHeaderBreath">
@media(max-width:767px){
  #hub>.stage>.view{top:16px!important;bottom:0!important;height:auto!important}
  #hub .view[data-view="projects"].v373DraftsOnly #shortRows{display:none!important}
}
</style>
<script id="v373CreatorHubHeaderBreathRuntime">
(()=>{
  const hub=document.getElementById('hub');
  const view=hub&&hub.querySelector('.view[data-view="projects"]');
  if(!view)return;
  const sync=()=>{
    const title=String(view.querySelector('#projectsViewTitle')?.textContent||'').trim().toLowerCase();
    const wanted=title==='bozze';
    if(view.classList.contains('v373DraftsOnly')!==wanted)view.classList.toggle('v373DraftsOnly',wanted);
  };
  sync();
  try{new MutationObserver(sync).observe(view,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','style']});}catch(_e){}
})();
</script>
'''

def patch_text(text:str)->str:
    if MARK in text:
        return text
    if '</body>' not in text:
        raise RuntimeError('V373 Creator Hub body anchor missing')
    return text.replace('</body>',PATCH+'\n</body>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V373 Creator Hub target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V373 Creator Hub header breath + drafts cleanup applied changed=',before!=after,flush=True)

    # V374 continues this same Creator Hub pass: +30px on collections/Live and
    # strict Twitch/YouTube category isolation. Keeping the handoff here means
    # production still uses the existing single Creator Hub startup path.
    v374=Path(__file__).resolve().with_name('fix_v374_creator_hub_spacing_live.py')
    t374=Path(__file__).resolve().with_name('test_v374_creator_hub_spacing_live.py')
    if not v374.is_file() or not t374.is_file():
        raise RuntimeError('V374 Creator Hub continuation missing')
    subprocess.run([sys.executable,str(v374),str(path)],check=True)
    subprocess.run([sys.executable,str(t374)],check=True)

    # V375 is an independent final mobile-AI spacing pass. Run it from this
    # always-executed late UI chain so earlier V308 padding cannot win again.
    ai=Path('/app/web/ai_v221_component/index.html')
    v375=Path(__file__).resolve().with_name('fix_v375_ai_header_breath.py')
    t375=Path(__file__).resolve().with_name('test_v375_ai_header_breath.py')
    if not v375.is_file() or not t375.is_file():
        raise RuntimeError('V375 AI header-breath continuation missing')
    subprocess.run([sys.executable,str(v375),str(ai)],check=True)
    subprocess.run([sys.executable,str(t375),str(ai)],check=True)

    # V376 is the final mobile Game Editor composition pass. It only touches
    # the Editor component and the existing Editor overlay title card.
    app=Path('/app')
    v376=Path(__file__).resolve().with_name('fix_v376_mobile_editor_reference.py')
    t376=Path(__file__).resolve().with_name('test_v376_mobile_editor_reference.py')
    if not v376.is_file() or not t376.is_file():
        raise RuntimeError('V376 mobile Editor continuation missing')
    subprocess.run([sys.executable,str(v376),str(app)],check=True)
    subprocess.run([sys.executable,str(t376),str(app)],check=True)

    # V378 fixes the spacing bug visible on mobile: V376's first grid row could
    # absorb the whole iframe height and push actions/timeline behind the Game Bar.
    v378=Path(__file__).resolve().with_name('fix_v378_mobile_editor_stack.py')
    t378=Path(__file__).resolve().with_name('test_v378_mobile_editor_stack.py')
    if not v378.is_file() or not t378.is_file():
        raise RuntimeError('V378 mobile Editor stack continuation missing')
    subprocess.run([sys.executable,str(v378),str(app)],check=True)
    subprocess.run([sys.executable,str(t378),str(app)],check=True)

    # V379 completes the approved mobile composition: internal Game Editor/FULL
    # card, slightly smaller player, unclipped timeline, and no duplicate final CTA.
    v379=Path(__file__).resolve().with_name('fix_v379_mobile_editor_final_compose.py')
    t379=Path(__file__).resolve().with_name('test_v379_mobile_editor_final_compose.py')
    if not v379.is_file() or not t379.is_file():
        raise RuntimeError('V379 mobile Editor final compose continuation missing')
    subprocess.run([sys.executable,str(v379),str(app)],check=True)
    subprocess.run([sys.executable,str(t379),str(app)],check=True)

if __name__=='__main__':
    main()
