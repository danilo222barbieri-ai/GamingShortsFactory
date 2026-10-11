#!/usr/bin/env python3
from pathlib import Path
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

if __name__=='__main__':
    main()
