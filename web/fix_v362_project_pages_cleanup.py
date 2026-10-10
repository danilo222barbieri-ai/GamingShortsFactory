#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

MARK = 'V362_PROJECT_PAGES_CLEANUP'

PATCH = r'''
<!-- V362_PROJECT_PAGES_CLEANUP -->
<!-- V362_1_STABLE_OBSERVER -->
<style id="v362ProjectPagesCleanup">
@media(max-width:767px){
  /* Keep the real page title/subtitle at the top. Everything repeated inside
     the project scroller is redundant on direct Shorts/Drafts routes. */
  #hub .view[data-view="projects"].v362ProjectClean .detail{
    grid-template-rows:auto minmax(0,1fr)!important;
    gap:4px!important;
  }
  #hub .view[data-view="projects"].v362ProjectClean .detailHead{
    display:flex!important;
    min-height:66px!important;
    padding:7px 10px 5px!important;
  }
  #hub .view[data-view="projects"].v362ProjectClean .detailCard{
    padding:0!important;
    border:0!important;
    background:transparent!important;
    box-shadow:none!important;
    backdrop-filter:none!important;
    -webkit-backdrop-filter:none!important;
  }
  #hub .view[data-view="projects"].v362ProjectClean .folderScroller{
    padding:0 4px 104px!important;
  }
  #hub .view[data-view="projects"].v362ProjectClean .folderScroller>.hubProjectsGuide,
  #hub .view[data-view="projects"].v362ProjectClean .folderScroller>.v362RedundantProjectBlock,
  #hub .view[data-view="projects"].v362ProjectClean [data-project-pane]>.v362RedundantProjectBlock,
  #hub .view[data-view="projects"].v362ProjectClean .v362EmptyCollection{
    display:none!important;
  }
  #hub .view[data-view="projects"].v362CollectionEmpty .detailCard{
    display:none!important;
  }
  #hub .view[data-view="projects"].v362CollectionEmpty .detail{
    grid-template-rows:auto minmax(0,1fr)!important;
  }
}
</style>
<script id="v362ProjectPagesCleanupRuntime">
(()=>{
  const hub=document.getElementById('hub');
  const view=hub&&hub.querySelector('.view[data-view="projects"]');
  if(!view)return;
  const q=(s,r=view)=>r.querySelector(s);
  const qa=(s,r=view)=>[...r.querySelectorAll(s)];
  const mobile=()=>window.matchMedia('(max-width:767px)').matches;
  const visible=(el)=>!!el&&getComputedStyle(el).display!=='none';
  const emptyCopy=/^(?:nessun|nessuna|caricamento)\b/i;

  function resetCleanup(){
    view.classList.remove('v362ProjectClean','v362CollectionEmpty');
    qa('.v362RedundantProjectBlock').forEach((n)=>n.classList.remove('v362RedundantProjectBlock'));
    qa('.v362EmptyCollection').forEach((n)=>n.classList.remove('v362EmptyCollection'));
  }

  function clean(){
    if(!mobile()){
      resetCleanup();
      return;
    }
    const title=String(q('#projectsViewTitle')?.textContent||'').trim().toLowerCase();
    const direct=title==='i miei shorts'||title==='bozze';
    view.classList.toggle('v362ProjectClean',direct);
    if(!direct){
      resetCleanup();
      return;
    }

    const scroller=q('.folderScroller');
    if(scroller){
      [...scroller.children].forEach((child)=>{
        if(!child.matches('[data-project-pane]')) child.classList.add('v362RedundantProjectBlock');
      });
    }

    const panes=qa('[data-project-pane]');
    const active=panes.find(visible);
    if(!active){
      view.classList.remove('v362CollectionEmpty');
      return;
    }
    [...active.children].forEach((child)=>{
      if(!['projectRows','draftRows','shortRows'].includes(child.id)) child.classList.add('v362RedundantProjectBlock');
    });

    const rows=title==='i miei shorts'?q('#shortRows',active):q('#draftRows',active);
    if(!rows){
      view.classList.remove('v362CollectionEmpty');
      return;
    }
    const hasRealRows=!!rows.querySelector('.row,.shortRow,.projectBox');
    const empties=qa('.empty',rows);
    const removableEmpty=!hasRealRows&&empties.length>0&&empties.every((el)=>emptyCopy.test(String(el.textContent||'').trim()));
    empties.forEach((el)=>el.classList.toggle('v362EmptyCollection',removableEmpty));
    rows.classList.toggle('v362EmptyCollection',removableEmpty);
    view.classList.toggle('v362CollectionEmpty',removableEmpty);
  }

  clean();
  try{new MutationObserver(clean).observe(view,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','style']});}catch(_e){}
  window.addEventListener('resize',clean,{passive:true});
})();
</script>
'''


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    if 'V359_CREATOR_HUB_GAMEBAR_FIT' not in text:
        raise RuntimeError('V362 requires V359/V361 Creator Hub repair first')
    if '</body>' not in text:
        raise RuntimeError('V362 Creator Hub body anchor missing')
    return text.replace('</body>', PATCH + '\n</body>', 1)


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V362 Creator Hub target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')

    # V365: repair the base Hub bootstrap after every V359/V362 pass, before
    # the V359 regression contract runs. This keeps restart behavior deterministic.
    bootstrap_fix = Path(__file__).resolve().with_name('fix_v365_creator_hub_bootstrap.py')
    if not bootstrap_fix.is_file():
        raise RuntimeError('V365 Creator Hub bootstrap fix missing')
    subprocess.run([sys.executable, str(bootstrap_fix), str(path)], check=True)

    print('V362.1 project pages cleanup + V365 Hub bootstrap applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
