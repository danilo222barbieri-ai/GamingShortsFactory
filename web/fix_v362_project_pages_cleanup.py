#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

MARK = 'V362_PROJECT_PAGES_CLEANUP'
STABLE_MARK = 'V371_OBSERVER_STABILITY'

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
  const V371_OBSERVER_STABILITY=true;
  const hub=document.getElementById('hub');
  const view=hub&&hub.querySelector('.view[data-view="projects"]');
  if(!view)return;
  const q=(s,r=view)=>r.querySelector(s);
  const qa=(s,r=view)=>[...r.querySelectorAll(s)];
  const mobile=()=>window.matchMedia('(max-width:767px)').matches;
  const visible=(el)=>!!el&&getComputedStyle(el).display!=='none';
  const emptyCopy=/^(?:nessun|nessuna|caricamento)\b/i;

  // V371: this observer watches class/style. Every class write in its callback
  // must therefore be idempotent or V368's startup style repair can kick off a
  // class -> observer -> class feedback loop that pins Safari's main thread.
  function v362SetClass(el,name,on){
    if(!el)return;
    const wanted=!!on;
    if(el.classList.contains(name)!==wanted)el.classList.toggle(name,wanted);
  }

  function resetCleanup(){
    v362SetClass(view,'v362ProjectClean',false);
    v362SetClass(view,'v362CollectionEmpty',false);
    qa('.v362RedundantProjectBlock').forEach((n)=>v362SetClass(n,'v362RedundantProjectBlock',false));
    qa('.v362EmptyCollection').forEach((n)=>v362SetClass(n,'v362EmptyCollection',false));
  }

  function clean(){
    if(!mobile()){
      resetCleanup();
      return;
    }
    const title=String(q('#projectsViewTitle')?.textContent||'').trim().toLowerCase();
    const direct=title==='i miei shorts'||title==='bozze';
    v362SetClass(view,'v362ProjectClean',direct);
    if(!direct){
      resetCleanup();
      return;
    }

    const scroller=q('.folderScroller');
    if(scroller){
      [...scroller.children].forEach((child)=>{
        if(!child.matches('[data-project-pane]'))v362SetClass(child,'v362RedundantProjectBlock',true);
      });
    }

    const panes=qa('[data-project-pane]');
    const active=panes.find(visible);
    if(!active){
      v362SetClass(view,'v362CollectionEmpty',false);
      return;
    }
    [...active.children].forEach((child)=>{
      if(!['projectRows','draftRows','shortRows'].includes(child.id))v362SetClass(child,'v362RedundantProjectBlock',true);
    });

    const rows=title==='i miei shorts'?q('#shortRows',active):q('#draftRows',active);
    if(!rows){
      v362SetClass(view,'v362CollectionEmpty',false);
      return;
    }
    const hasRealRows=!!rows.querySelector('.row,.shortRow,.projectBox');
    const empties=qa('.empty',rows);
    const removableEmpty=!hasRealRows&&empties.length>0&&empties.every((el)=>emptyCopy.test(String(el.textContent||'').trim()));
    empties.forEach((el)=>v362SetClass(el,'v362EmptyCollection',removableEmpty));
    v362SetClass(rows,'v362EmptyCollection',removableEmpty);
    v362SetClass(view,'v362CollectionEmpty',removableEmpty);
  }

  clean();
  try{new MutationObserver(clean).observe(view,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','style']});}catch(_e){}
  window.addEventListener('resize',clean,{passive:true});
})();
</script>
'''


def patch_text(text: str) -> str:
    if MARK in text:
        if STABLE_MARK in text:
            return text
        start = text.find('<!-- V362_PROJECT_PAGES_CLEANUP -->')
        script_start = text.find('<script id="v362ProjectPagesCleanupRuntime">', start)
        script_end = text.find('</script>', script_start)
        if start < 0 or script_start < 0 or script_end < 0:
            raise RuntimeError('V362 legacy cleanup block is malformed')
        script_end += len('</script>')
        return text[:start] + PATCH + text[script_end:]
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

    # V366: after the bootstrap is valid, stabilize the real Profile state path.
    # Patch both the Hub client and direct-upload API, then enforce the runtime contract.
    web_root = Path(__file__).resolve().parent
    app_root = web_root.parent
    state_fix = web_root/'fix_v366_creator_hub_state_stability.py'
    state_test = web_root/'test_v366_creator_hub_state_stability.py'
    if not state_fix.is_file() or not state_test.is_file():
        raise RuntimeError('V366 Creator Hub state stability files missing')
    subprocess.run([sys.executable, str(state_fix), str(app_root)], check=True)
    subprocess.run([sys.executable, str(state_test), str(app_root)], check=True)

    # V367.1 emergency recovery: do NOT run the V367 parent-document interaction
    # arbiter. It could mark the wrong surface inert and freeze every tap on Safari.
    # Keep V343 as the only global shell and preserve the validated V365/V366 path.
    touch_test = web_root/'test_v367_1_touch_recovery.py'
    if not touch_test.is_file():
        raise RuntimeError('V367.1 touch recovery contract missing')
    subprocess.run([sys.executable, str(touch_test), str(app_root)], check=True)

    # V368: Hub-local recovery only. It may repair visibility/pointer state but
    # must never become a second navigation owner.
    touch_fix = web_root/'fix_v368_creator_hub_touch_recovery.py'
    touch_contract = web_root/'test_v368_creator_hub_touch_recovery.py'
    if not touch_fix.is_file() or not touch_contract.is_file():
        raise RuntimeError('V368 Creator Hub touch recovery files missing')
    subprocess.run([sys.executable, str(touch_fix), str(path)], check=True)
    subprocess.run([sys.executable, str(touch_contract), str(app_root)], check=True)

    # V370: remove the architectural race itself. Home emits navigation intent;
    # V158/V160 stand down whenever V343 is active; hidden Hub stays lazy.
    owner_fix = web_root/'fix_v370_single_navigation_owner.py'
    owner_contract = web_root/'test_v370_single_navigation_owner.py'
    if not owner_fix.is_file() or not owner_contract.is_file():
        raise RuntimeError('V370 single navigation owner files missing')
    subprocess.run([sys.executable, str(owner_fix), str(app_root)], check=True)
    subprocess.run([sys.executable, str(owner_contract), str(app_root)], check=True)

    # V371: enforce the no-feedback observer contract after all Hub repair layers.
    observer_contract = web_root/'test_v371_creator_hub_observer_stability.py'
    if not observer_contract.is_file():
        raise RuntimeError('V371 observer stability contract missing')
    subprocess.run([sys.executable, str(observer_contract), str(app_root)], check=True)

    print('V362.2/V371 project cleanup observer stabilization + V365/V366/V368/V370 applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
