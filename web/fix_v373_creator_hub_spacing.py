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

    v374=Path(__file__).resolve().with_name('fix_v374_creator_hub_spacing_live.py')
    t374=Path(__file__).resolve().with_name('test_v374_creator_hub_spacing_live.py')
    if not v374.is_file() or not t374.is_file(): raise RuntimeError('V374 Creator Hub continuation missing')
    subprocess.run([sys.executable,str(v374),str(path)],check=True)
    subprocess.run([sys.executable,str(t374)],check=True)

    ai=Path('/app/web/ai_v221_component/index.html')
    v375=Path(__file__).resolve().with_name('fix_v375_ai_header_breath.py')
    t375=Path(__file__).resolve().with_name('test_v375_ai_header_breath.py')
    if not v375.is_file() or not t375.is_file(): raise RuntimeError('V375 AI header-breath continuation missing')
    subprocess.run([sys.executable,str(v375),str(ai)],check=True)
    subprocess.run([sys.executable,str(t375),str(ai)],check=True)

    app=Path('/app')
    v380=Path(__file__).resolve().with_name('fix_v380_mobile_editor_unified.py')
    t380=Path(__file__).resolve().with_name('test_v380_mobile_editor_unified.py')
    if not v380.is_file() or not t380.is_file(): raise RuntimeError('V380 unified mobile Editor continuation missing')
    subprocess.run([sys.executable,str(v380),str(app)],check=True)
    subprocess.run([sys.executable,str(t380),str(app)],check=True)

    # V381 keeps V380 logic but makes the normal editor deliberately small;
    # FULL uses the existing real fullscreen engine with controls at the sides.
    v381=Path(__file__).resolve().with_name('fix_v381_mobile_editor_compact_full.py')
    t381=Path(__file__).resolve().with_name('test_v381_mobile_editor_compact_full.py')
    if not v381.is_file() or not t381.is_file(): raise RuntimeError('V381 compact/full Editor continuation missing')
    subprocess.run([sys.executable,str(v381),str(app)],check=True)
    subprocess.run([sys.executable,str(t381),str(app)],check=True)

if __name__=='__main__':
    main()
