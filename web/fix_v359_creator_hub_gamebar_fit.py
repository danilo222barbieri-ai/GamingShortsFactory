#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V359_CREATOR_HUB_GAMEBAR_FIT'

PATCH = r'''
<!-- V359_CREATOR_HUB_GAMEBAR_FIT -->
<style id="v359CreatorHubGamebarFit">
@media(max-width:767px){
  #hub{--v359-gamebar-gap:6px}

  #hub .view[data-view="dashboard"] .dashboard{padding-bottom:var(--v359-gamebar-gap)!important}

  #hub .view[data-view="projects"] .detail,
  #hub .view[data-view="projects"] .detailCard{height:100%!important;min-height:0!important;box-sizing:border-box!important}
  #hub .view[data-view="projects"] .detailCard{overflow:hidden!important}
  #hub .view[data-view="projects"] .folderScroller{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;
    padding:4px 4px var(--v359-gamebar-gap)!important;overflow-y:auto!important;overflow-x:hidden!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .detail{display:block!important;padding:10px 0 0!important;gap:0!important}
  #hub .view[data-view="projects"].v359ProjectDirect .detailHead{display:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .detailCard{padding:0!important;border:0!important;background:transparent!important;box-shadow:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .folderScroller{
    display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:10px!important;
    padding:0 4px var(--v359-gamebar-gap)!important;overflow:hidden!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .hubProjectsGuide{margin:0!important;padding:8px 12px!important;min-height:0!important;box-sizing:border-box!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectHeroDuplicate{display:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane{
    height:100%!important;min-height:0!important;display:grid!important;grid-template-rows:minmax(0,1fr)!important;
    overflow:hidden!important;margin:0!important;padding:0!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane .projectSectionHead{display:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #projectRows:empty{display:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #projectRows,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #draftRows,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #shortRows{
    min-height:0!important;max-height:100%!important;overflow-y:auto!important;overflow-x:hidden!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #draftRows,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #shortRows{height:100%!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #draftRows>.empty,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #shortRows>.empty{
    width:100%!important;height:100%!important;min-height:0!important;margin:0!important;box-sizing:border-box!important;
    display:grid!important;place-content:center!important;padding:26px 20px!important;
  }

  #hub .view[data-view="live"]{height:100%!important;min-height:0!important;box-sizing:border-box!important;padding:10px 4px var(--v359-gamebar-gap)!important;overflow:hidden!important}
  #hub .view[data-view="live"] .detail,
  #hub .view[data-view="live"] .detailCard,
  #hub .view[data-view="live"] .folderScroller{height:100%!important;min-height:0!important;box-sizing:border-box!important}
  #hub .view[data-view="live"] .folderScroller{padding:0!important;overflow:hidden!important}
  #hub .v357LiveRoot{height:100%!important;min-height:0!important;grid-template-rows:repeat(2,minmax(0,1fr))!important;gap:12px!important;padding:0 4px!important}
  #hub .v357LiveDetail{height:100%!important;min-height:0!important;padding:0 4px!important}

  #hub .view[data-view="profile"] .profileReferenceScroll{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;overflow:hidden!important;
    grid-template-rows:42px minmax(146px,1.25fr) minmax(126px,1fr) minmax(104px,.9fr)!important;
    gap:10px!important;padding:12px 2px var(--v359-gamebar-gap)!important;
  }
  #hub .view[data-view="profile"] .profileReferenceEdit,
  #hub .view[data-view="profile"] .profilePlanRef,
  #hub .view[data-view="profile"] .profileSocialRef{height:100%!important;min-height:0!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileReferenceScroll{
    display:block!important;padding:14px 4px var(--v359-gamebar-gap)!important;overflow:hidden!important;
  }
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRef{height:100%!important;min-height:0!important}

  #hub .view[data-view="social"],
  #hub .view[data-view="subscription"]{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="social"] .detail,
  #hub .view[data-view="subscription"] .detail,
  #hub .view[data-view="social"] .detailCard,
  #hub .view[data-view="subscription"] .detailCard{height:100%!important;min-height:0!important;box-sizing:border-box!important;overflow:hidden!important}
  #hub .view[data-view="social"] .folderScroller,
  #hub .view[data-view="subscription"] .folderScroller{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;
    padding-bottom:var(--v359-gamebar-gap)!important;overflow-y:auto!important;overflow-x:hidden!important;
  }
}
</style>
<script id="v359CreatorHubGamebarFitRuntime">
(()=>{
  const hub=document.getElementById('hub');
  if(!hub)return;
  const projectView=hub.querySelector('.view[data-view="projects"]');
  if(!projectView)return;
  const qa=(s,r=projectView)=>[...r.querySelectorAll(s)];
  const isVisible=(el)=>!!el&&getComputedStyle(el).display!=='none';
  const savedRe=/^\d+\s+(?:bozze|shorts)\s+salvat/i;

  function syncProjects(){
    const landing=projectView.querySelector('#projectHubCards');
    const panes=qa('[data-project-pane]');
    const direct=!!landing&&!isVisible(landing);
    projectView.classList.toggle('v359ProjectDirect',direct);
    panes.forEach((pane)=>pane.classList.toggle('v359ProjectActivePane',direct&&isVisible(pane)));
    qa('.v359ProjectHeroDuplicate').forEach((el)=>el.classList.remove('v359ProjectHeroDuplicate'));
    if(!direct)return;
    const active=panes.find((pane)=>pane.classList.contains('v359ProjectActivePane'));
    if(!active)return;
    const title=String(projectView.querySelector('#projectsViewTitle')?.textContent||'').trim().toLowerCase();
    qa('h1,h2,h3,.projectCollectionTitle,.projectHeroTitle,.projectSummaryTitle',active).forEach((el)=>{
      const copy=String(el.textContent||'').trim();
      if((title&&copy.toLowerCase()===title)||savedRe.test(copy))el.classList.add('v359ProjectHeroDuplicate');
    });
  }

  syncProjects();
  try{new MutationObserver(syncProjects).observe(projectView,{subtree:true,attributes:true,childList:true,characterData:true,attributeFilter:['class','style']});}catch(_e){}
  window.addEventListener('resize',syncProjects,{passive:true});
})();
</script>
'''


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    if 'V357_CREATOR_HUB_HIERARCHY' not in text:
        raise RuntimeError('V359 requires V357 Creator Hub hierarchy')
    if '</body>' not in text:
        raise RuntimeError('V359 Creator Hub body anchor missing')
    return text.replace('</body>', PATCH + '\n</body>', 1)


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V359 Creator Hub target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')
    print('V359 Creator Hub Game Bar fit applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
