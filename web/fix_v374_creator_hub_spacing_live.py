#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

MARK='V374_CREATOR_HUB_SPACING_LIVE_ISOLATION'

PATCH=r'''
<!-- V374_CREATOR_HUB_SPACING_LIVE_ISOLATION -->
<style id="v374CreatorHubSpacingLiveIsolation">
@media(max-width:767px){
  /* Give the collection pages a real 30px extra breath below the global header. */
  #hub>.stage>.view[data-view="projects"]{top:46px!important}
  #hub>.stage>.view[data-view="live"]{top:46px!important}

  /* Inside a Live platform, render only that platform's card/categories. */
  #hub .view[data-view="live"][data-v374-platform="twitch"] .livePlatformYoutube{display:none!important}
  #hub .view[data-view="live"][data-v374-platform="twitch"] .livePlatformTwitch{display:grid!important}
  #hub .view[data-view="live"][data-v374-platform="youtube"] .livePlatformTwitch{display:none!important}
  #hub .view[data-view="live"][data-v374-platform="youtube"] .livePlatformYoutube{display:grid!important}
}
</style>
<script id="v374CreatorHubSpacingLiveIsolationRuntime">
(()=>{
  const hub=document.getElementById('hub');
  const live=hub&&hub.querySelector('.view[data-view="live"]');
  if(!live)return;

  const setPlatform=(name)=>{
    if(name==='twitch'||name==='youtube'){
      live.setAttribute('data-v374-platform',name);
      live.querySelectorAll('.livePlatformCard').forEach((card)=>{
        const selected=(name==='twitch'&&card.classList.contains('livePlatformTwitch'))||
          (name==='youtube'&&card.classList.contains('livePlatformYoutube'));
        card.classList.toggle('v374PlatformSelected',selected);
        card.setAttribute('aria-hidden',selected?'false':'true');
      });
    }else{
      live.removeAttribute('data-v374-platform');
      live.querySelectorAll('.livePlatformCard').forEach((card)=>card.removeAttribute('aria-hidden'));
    }
  };

  const sync=()=>{
    if(!live.classList.contains('v357LiveOpen')){setPlatform('');return;}
    const selected=live.querySelector('.livePlatformCard.v357Selected');
    if(selected?.classList.contains('livePlatformTwitch'))setPlatform('twitch');
    else if(selected?.classList.contains('livePlatformYoutube'))setPlatform('youtube');
  };

  live.addEventListener('click',(ev)=>{
    const folder=ev.target.closest?.('[data-v357-live]');
    if(folder){
      const name=String(folder.getAttribute('data-v357-live')||'').toLowerCase();
      if(name==='twitch'||name==='youtube')setPlatform(name);
      return;
    }
    if(ev.target.closest?.('.v357LiveBack'))setPlatform('');
  },true);

  sync();
  try{new MutationObserver(sync).observe(live,{subtree:true,attributes:true,attributeFilter:['class']});}catch(_e){}
})();
</script>
'''

def patch_text(text:str)->str:
    if MARK in text:
        return text
    if 'V373_CREATOR_HUB_HEADER_BREATH' not in text:
        raise RuntimeError('V374 requires V373 Creator Hub spacing baseline')
    if 'V357_CREATOR_HUB_HIERARCHY' not in text:
        raise RuntimeError('V374 requires V357 Live hierarchy')
    if '</body>' not in text:
        raise RuntimeError('V374 Creator Hub body anchor missing')
    return text.replace('</body>',PATCH+'\n</body>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V374 Creator Hub target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V374 Creator Hub spacing + Live platform isolation applied changed=',before!=after,flush=True)

    # V403 keeps the same single Creator Hub build chain and only simplifies
    # the presentation/actions; it does not introduce a parallel navigation path.
    v403=Path(__file__).resolve().with_name('fix_v403_creator_hub_simplified.py')
    t403=Path(__file__).resolve().with_name('test_v403_creator_hub_simplified.py')
    if not v403.is_file() or not t403.is_file():
        raise RuntimeError('V403 simplified Creator Hub continuation missing')
    subprocess.run([sys.executable,str(v403),str(path)],check=True)
    subprocess.run([sys.executable,str(t403)],check=True)

if __name__=='__main__':
    main()
