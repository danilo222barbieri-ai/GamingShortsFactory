#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V359_CREATOR_HUB_GAMEBAR_FIT'

PATCH = r'''
<!-- V359_CREATOR_HUB_GAMEBAR_FIT -->
<!-- GSF_V361_HUB_REPAIR -->
<style id="v359CreatorHubGamebarFit">
@media(max-width:767px){
  /* The parent Game Bar + footer are fixed. Keep internal pages scrollable and
     reserve their real footprint instead of stretching cards to a 6px gap. */
  #hub{padding:4px 6px 0!important;grid-template-rows:minmax(0,1fr)!important;gap:0!important;overflow:hidden!important}
  #hub>.top{display:none!important}
  #hub>.stage{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="dashboard"] .dashboard{padding-bottom:104px!important}

  /* Profile: compact natural cards + internal scrolling. */
  #hub .view[data-view="profile"] .profileReferenceScroll{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;display:block!important;
    overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;
    overscroll-behavior-y:contain!important;padding:10px 3px 104px!important;
  }
  #hub .profileReferenceBrand{display:none!important}
  #hub .profileReferenceCard{height:auto!important;margin:0 0 10px!important}
  #hub .profileReferenceEdit{
    min-height:188px!important;padding:14px!important;grid-template-columns:106px minmax(0,1fr)!important;
    gap:13px!important;align-items:center!important;
  }
  #hub .profileRefAvatar{width:88px!important;height:88px!important}
  #hub .profileRefPhotoBtn{min-width:98px!important;min-height:38px!important;font-size:10.5px!important}
  #hub .profileRefTitle{font-size:23px!important}
  #hub .profileRefSubtitle{font-size:11px!important;margin-top:4px!important}
  #hub .profileRefField{margin-top:5px!important}
  #hub .profileRefField label{font-size:10px!important;margin-bottom:5px!important}
  #hub .profileRefInputWrap{height:46px!important;border-radius:15px!important}
  #hub .profileRefInputWrap input{font-size:15px!important}
  #hub .profileRefSave{min-width:142px!important;height:44px!important;font-size:12px!important}
  #hub .profilePlanRef{min-height:142px!important;padding:13px 14px!important;grid-template-columns:54px minmax(0,1fr) auto!important;column-gap:10px!important;row-gap:8px!important}
  #hub .profileRefSectionIcon{width:50px!important;height:50px!important;border-radius:16px!important;font-size:21px!important}
  #hub .profileRefSectionText h2{font-size:21px!important}
  #hub .profileRefSectionText p{font-size:10.5px!important;margin-top:4px!important}
  #hub .profilePlanBody{grid-column:1/4!important;gap:9px!important}
  #hub .profilePlanPill{min-width:70px!important;height:36px!important;font-size:11px!important}
  #hub .profilePlanCopy{font-size:10px!important;line-height:1.25!important}
  #hub .profilePlanCta{grid-column:1/4!important;height:44px!important;font-size:12px!important}
  #hub .profileSocialRef{min-height:108px!important;padding:12px 14px!important}
  #hub .profileSocialRefHead{grid-template-columns:52px minmax(0,1fr)!important;gap:10px!important;margin:0!important}
  #hub .profileSocialRef .profileRefSectionIcon{width:50px!important;height:50px!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileReferenceScroll{display:block!important;padding:10px 3px 104px!important;overflow-y:auto!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRef{height:auto!important;min-height:430px!important;overflow:visible!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRows{height:auto!important;overflow:visible!important;grid-template-rows:repeat(5,56px)!important}

  /* Projects: selected collection starts at the top and scrolls naturally. */
  #hub .view[data-view="projects"]{padding:8px 2px 0!important;box-sizing:border-box!important}
  #hub .view[data-view="projects"] .detail,
  #hub .view[data-view="projects"] .detailCard{height:100%!important;min-height:0!important;box-sizing:border-box!important}
  #hub .view[data-view="projects"] .detail{display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:8px!important;padding:0!important}
  #hub .view[data-view="projects"] .detailCard{overflow:hidden!important}
  #hub .view[data-view="projects"] .folderScroller,
  #hub .view[data-view="projects"].v359ProjectDirect .folderScroller{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;display:block!important;
    padding:0 4px 104px!important;overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .detail{display:grid!important;padding:0!important;gap:8px!important}
  #hub .view[data-view="projects"].v359ProjectDirect .detailHead{display:flex!important;min-height:66px!important;padding:7px 10px 5px!important;align-items:flex-start!important}
  #hub .view[data-view="projects"] .detailHeadText h2{font-size:24px!important;line-height:1.02!important;margin:0!important}
  #hub .view[data-view="projects"] .detailHeadText p{font-size:11px!important;line-height:1.22!important;margin-top:5px!important}
  #hub .view[data-view="projects"].v359ProjectDirect .detailCard{padding:0!important;border:0!important;background:transparent!important;box-shadow:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .hubProjectsGuide{margin:0 0 10px!important;padding:9px 11px!important;min-height:0!important;box-sizing:border-box!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectHeroDuplicate{display:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane{
    height:auto!important;min-height:0!important;display:block!important;overflow:visible!important;margin:0!important;padding:0!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane .projectSectionHead{display:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #projectRows:empty{display:none!important}
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #projectRows,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #draftRows,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #shortRows{
    height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;
  }
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #draftRows>.empty,
  #hub .view[data-view="projects"].v359ProjectDirect .v359ProjectActivePane #shortRows>.empty{
    width:100%!important;height:auto!important;min-height:220px!important;margin:0 0 10px!important;box-sizing:border-box!important;
    display:grid!important;place-content:center!important;padding:24px 18px!important;
  }

  /* Live: keep Twitch/YouTube as folders but never let them become two giant
     half-screen tiles. */
  #hub .view[data-view="live"]{height:100%!important;min-height:0!important;box-sizing:border-box!important;padding:10px 2px 0!important;overflow:hidden!important}
  #hub .view[data-view="live"] .detail,
  #hub .view[data-view="live"] .detailCard,
  #hub .view[data-view="live"] .folderScroller{height:100%!important;min-height:0!important;box-sizing:border-box!important}
  #hub .view[data-view="live"] .folderScroller{display:block!important;padding:0 2px 104px!important;overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important}
  #hub .v357LiveRoot{height:auto!important;min-height:0!important;display:grid!important;grid-template-rows:repeat(2,148px)!important;gap:12px!important;padding:0 4px!important;align-content:start!important}
  #hub .v357LiveFolder{height:148px!important;min-height:148px!important;padding:15px!important;border-radius:25px!important;grid-template-columns:60px minmax(0,1fr) auto!important;gap:13px!important}
  #hub .v357LiveFolderIcon{width:58px!important;height:58px!important;border-radius:19px!important;font-size:23px!important}
  #hub .v357LiveFolderCopy b{font-size:22px!important;line-height:1!important}
  #hub .v357LiveFolderCopy small{font-size:11px!important;line-height:1.22!important;margin-top:5px!important}
  #hub .v357LiveFolderArrow{font-size:27px!important}
  #hub .v357LiveDetail{height:auto!important;min-height:0!important;padding:0 4px 8px!important;grid-template-rows:46px auto!important;overflow:visible!important}
  #hub .v357LiveDetailBody{height:auto!important;min-height:0!important;overflow:visible!important}
  #hub .v357LiveDetailBody .livePlatformCard{height:auto!important;min-height:0!important;overflow:visible!important}
  #hub .v357LiveDetailBody .liveMiniFolders{height:auto!important;grid-template-rows:none!important;grid-auto-rows:minmax(66px,auto)!important;overflow:visible!important}
  #hub .v357LiveDetailBody .liveMiniFolder{height:auto!important;min-height:66px!important}

  #hub .view[data-view="social"],
  #hub .view[data-view="subscription"]{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="social"] .detail,
  #hub .view[data-view="subscription"] .detail,
  #hub .view[data-view="social"] .detailCard,
  #hub .view[data-view="subscription"] .detailCard{height:100%!important;min-height:0!important;box-sizing:border-box!important;overflow:hidden!important}
  #hub .view[data-view="social"] .folderScroller,
  #hub .view[data-view="subscription"] .folderScroller{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;padding-bottom:104px!important;
    overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;
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
    print('V359/V361 Creator Hub mobile repair applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
