#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V357_CREATOR_HUB_HIERARCHY'

PATCH = r'''
<!-- V357_CREATOR_HUB_HIERARCHY -->
<style id="v357CreatorHubHierarchy">
@media(max-width:767px){
  /* Remove the component's legacy title row on Projects/Live. The parent GSF header stays untouched. */
  #hub.v357NoLegacyTop{grid-template-rows:minmax(0,1fr)!important;gap:0!important}
  #hub.v357NoLegacyTop>.top{display:none!important}
  #hub.v357NoLegacyTop>.stage{height:100%!important;min-height:0!important}

  /* Projects: one title only, with real air below the global app header. */
  #hub .view[data-view="projects"]{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="projects"] .detail{height:100%!important;min-height:0!important;padding-top:16px!important;gap:12px!important;box-sizing:border-box!important}
  #hub .view[data-view="projects"] .detailHead{min-height:70px!important;padding:8px 14px 6px!important;align-items:flex-start!important}
  #hub .view[data-view="projects"] .detailHeadText h2{font-size:27px!important;line-height:1.02!important;margin:0!important}
  #hub .view[data-view="projects"] .detailHeadText p{font-size:12.5px!important;line-height:1.28!important;margin-top:7px!important}
  #hub .view[data-view="projects"] .folderScroller{padding:4px 4px 104px!important;overflow-y:auto!important;overflow-x:hidden!important}
  #hub .view[data-view="projects"] #projectHubCards{margin-top:2px!important}

  /* Live root: exactly two platform folders; no root-level scrolling. */
  #hub .view[data-view="live"]{height:100%!important;min-height:0!important;overflow:hidden!important;padding:16px 4px 96px!important;box-sizing:border-box!important}
  #hub .view[data-view="live"] .detail{height:100%!important;min-height:0!important;display:block!important;padding:0!important}
  #hub .view[data-view="live"] .detailHead{display:none!important}
  #hub .view[data-view="live"] .detailCard{height:100%!important;min-height:0!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;overflow:hidden!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
  #hub .view[data-view="live"] .folderScroller{height:100%!important;min-height:0!important;padding:0!important;overflow:hidden!important;display:block!important}
  #hub .view[data-view="live"] .hubLiveGuide{display:none!important}
  #hub .v357LiveRoot{height:100%!important;min-height:0!important;display:grid!important;grid-template-rows:repeat(2,minmax(0,1fr))!important;gap:14px!important;padding:0 4px!important}
  #hub .v357LiveFolder{width:100%!important;min-height:0!important;border:1px solid rgba(143,181,216,.20)!important;border-radius:28px!important;background:rgba(255,255,255,.96)!important;box-shadow:0 13px 30px rgba(61,104,145,.07),inset 0 1px 0 rgba(255,255,255,.99)!important;padding:18px!important;display:grid!important;grid-template-columns:70px minmax(0,1fr) auto!important;gap:16px!important;align-items:center!important;text-align:left!important;color:#0d2a66!important;cursor:pointer!important}
  #hub .v357LiveFolderIcon{width:66px!important;height:66px!important;border-radius:22px!important;display:grid!important;place-items:center!important;font-size:27px!important;font-weight:950!important}
  #hub .v357LiveFolder[data-v357-live="twitch"] .v357LiveFolderIcon{background:linear-gradient(145deg,#f0e8ff,#e5d9ff)!important;color:#9146ff!important}
  #hub .v357LiveFolder[data-v357-live="youtube"] .v357LiveFolderIcon{background:linear-gradient(145deg,#ffe8ee,#fff0f3)!important;color:#ff1744!important}
  #hub .v357LiveFolderCopy b{display:block!important;font-size:25px!important;line-height:1.02!important;font-weight:950!important;letter-spacing:-.03em!important}
  #hub .v357LiveFolderCopy small{display:block!important;margin-top:7px!important;font-size:12px!important;line-height:1.3!important;font-weight:720!important;color:#7185a6!important}
  #hub .v357LiveFolderArrow{font-size:31px!important;line-height:1!important;color:#7f98b6!important;font-style:normal!important}

  #hub .v357LiveDetail{height:100%!important;min-height:0!important;display:none!important;grid-template-rows:48px minmax(0,1fr)!important;gap:10px!important;padding:0 4px!important}
  #hub .view[data-view="live"].v357LiveOpen .v357LiveRoot{display:none!important}
  #hub .view[data-view="live"].v357LiveOpen .v357LiveDetail{display:grid!important}
  #hub .v357LiveDetailHead{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:10px!important;min-height:48px!important;padding:0 4px!important}
  #hub .v357LiveBack,#hub .v357SocialBack{height:40px!important;border:1px solid rgba(143,181,216,.24)!important;border-radius:14px!important;background:rgba(255,255,255,.96)!important;color:#567a9b!important;padding:0 13px!important;font-size:11px!important;font-weight:900!important;box-shadow:0 7px 18px rgba(61,104,145,.05)!important;cursor:pointer!important}
  #hub .v357LiveDetailTitle{font-size:18px!important;font-weight:950!important;color:#0d2a66!important;margin-right:4px!important}
  #hub .v357LiveDetailBody{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .v357LiveDetailBody .livePlatformCard{display:none!important;width:100%!important;height:100%!important;min-height:0!important;margin:0!important;padding:14px!important;border-radius:26px!important;overflow:hidden!important;grid-template-rows:auto minmax(0,1fr)!important;gap:10px!important}
  #hub .v357LiveDetailBody .livePlatformCard.v357Selected{display:grid!important}
  #hub .v357LiveDetailBody .livePlatformHead{min-height:56px!important;margin:0!important;grid-template-columns:54px minmax(0,1fr)!important;gap:12px!important}
  #hub .v357LiveDetailBody .livePlatformIcon{width:54px!important;height:54px!important;border-radius:18px!important}
  #hub .v357LiveDetailBody .livePaneTitle{font-size:22px!important}
  #hub .v357LiveDetailBody .livePlatformSubtitle{font-size:11px!important;line-height:1.22!important}
  #hub .v357LiveDetailBody .liveMiniFolders{min-height:0!important;height:100%!important;display:grid!important;grid-template-rows:repeat(3,minmax(0,1fr))!important;gap:8px!important;overflow:hidden!important}
  #hub .v357LiveDetailBody .liveMiniFolder{min-height:0!important;height:100%!important;padding:9px 11px!important;border-radius:18px!important;grid-template-columns:44px minmax(0,1fr) auto!important}
  #hub .v357LiveDetailBody .liveMiniFolder>span{width:44px!important;height:44px!important;border-radius:14px!important}
  #hub .v357LiveDetailBody .liveMiniFolder b{font-size:14.5px!important}
  #hub .v357LiveDetailBody .liveMiniFolder small{font-size:10px!important;margin-top:3px!important}

  /* Profile root gets breathing room; Social becomes one folder instead of five exposed rows. */
  #hub .view[data-view="profile"] .profileReferenceScroll{height:100%!important;min-height:0!important;display:grid!important;grid-template-rows:42px 158px 140px 112px!important;gap:10px!important;overflow:hidden!important;padding:12px 2px 96px!important;box-sizing:border-box!important}
  #hub .profileReferenceBrand{height:42px!important;min-height:42px!important;padding:5px 12px 7px!important}
  #hub .profileReferenceEdit{height:158px!important;min-height:0!important;padding:12px 14px!important}
  #hub .profileRefAvatar{width:76px!important;height:76px!important}
  #hub .profileRefPhotoBtn{height:30px!important;min-height:30px!important}
  #hub .profileRefTitle{font-size:22px!important}
  #hub .profileRefSubtitle{font-size:10.5px!important;margin-top:3px!important}
  #hub .profileRefInputWrap{height:39px!important}
  #hub .profileRefSave{height:34px!important}
  #hub .profilePlanRef{height:140px!important;min-height:0!important;padding:10px 14px!important}
  #hub .profileSocialRef{height:112px!important;min-height:112px!important;padding:12px 14px!important;display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;align-items:center!important;overflow:hidden!important;cursor:pointer!important}
  #hub .profileSocialRefHead{grid-column:1!important;display:grid!important;grid-template-columns:58px minmax(0,1fr)!important;gap:12px!important;align-items:center!important;margin:0!important;min-width:0!important}
  #hub .profileSocialRef .profileRefSectionIcon{width:56px!important;height:56px!important;border-radius:18px!important;font-size:23px!important}
  #hub .profileSocialRef .profileRefSectionText h2{font-size:22px!important;line-height:1!important}
  #hub .profileSocialRef .profileRefSectionText p{font-size:11px!important;line-height:1.2!important;margin-top:5px!important}
  #hub .v357SocialFolderChevron{grid-column:2!important;font-size:30px!important;color:#7f98b6!important;line-height:1!important}
  #hub .profileSocialRef>.profileSocialRows{display:none!important}
  #hub .v357SocialBack{display:none!important}

  /* Dedicated Social detail state: reuse the five original rows and their handlers. */
  #hub .view[data-view="profile"].v357SocialOpen .profileReferenceScroll{display:block!important;padding:14px 4px 96px!important;overflow:hidden!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileReferenceBrand,
  #hub .view[data-view="profile"].v357SocialOpen .profileReferenceEdit,
  #hub .view[data-view="profile"].v357SocialOpen .profilePlanRef{display:none!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRef{height:100%!important;min-height:0!important;padding:12px 14px!important;display:grid!important;grid-template-columns:1fr!important;grid-template-rows:42px 66px minmax(0,1fr)!important;gap:8px!important;align-items:stretch!important;cursor:default!important;border-radius:26px!important}
  #hub .view[data-view="profile"].v357SocialOpen .v357SocialBack{display:block!important;justify-self:start!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRefHead{grid-column:1!important;grid-template-columns:52px minmax(0,1fr)!important;gap:11px!important;cursor:default!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRef .profileRefSectionIcon{width:50px!important;height:50px!important;border-radius:16px!important}
  #hub .view[data-view="profile"].v357SocialOpen .v357SocialFolderChevron{display:none!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRows{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:repeat(5,minmax(0,1fr))!important;gap:0!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRefRow{min-height:0!important;height:100%!important;padding:5px 3px!important;grid-template-columns:42px minmax(0,1fr) auto 20px!important;gap:8px!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRefRow .socialLogo{width:36px!important;height:36px!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRefRow .socialName{font-size:14px!important}
  #hub .view[data-view="profile"].v357SocialOpen .profileSocialRefRow .socialState{min-width:104px!important;min-height:31px!important;font-size:10px!important}

  @media(max-height:760px){
    #hub .view[data-view="profile"] .profileReferenceScroll{grid-template-rows:38px 146px 130px 100px!important;gap:7px!important;padding-top:8px!important;padding-bottom:88px!important}
    #hub .profileReferenceBrand{height:38px!important;min-height:38px!important}
    #hub .profileReferenceEdit{height:146px!important}
    #hub .profilePlanRef{height:130px!important}
    #hub .profileSocialRef{height:100px!important;min-height:100px!important}
    #hub .v357LiveRoot{gap:10px!important}
    #hub .v357LiveFolder{padding:14px!important}
    #hub .v357LiveFolderIcon{width:58px!important;height:58px!important;border-radius:19px!important}
  }
}
</style>
<script id="v357CreatorHubHierarchyRuntime">
(()=>{
  const hub=document.getElementById('hub');
  if(!hub)return;
  const mobile=()=>window.matchMedia('(max-width:767px)').matches;
  const q=(s,r=document)=>r.querySelector(s);
  const qa=(s,r=document)=>[...r.querySelectorAll(s)];
  const liveView=q('.view[data-view="live"]',hub);
  const profileView=q('.view[data-view="profile"]',hub);
  let lastView='';

  function closeLivePlatform(){
    if(!liveView)return;
    liveView.classList.remove('v357LiveOpen');
    qa('.livePlatformCard.v357Selected',liveView).forEach((n)=>n.classList.remove('v357Selected'));
  }

  function openLivePlatform(name){
    if(!mobile()||!liveView)return;
    const card=q(name==='twitch'?'.livePlatformTwitch':'.livePlatformYoutube',liveView);
    if(!card)return;
    qa('.livePlatformCard.v357Selected',liveView).forEach((n)=>n.classList.remove('v357Selected'));
    card.classList.add('v357Selected');
    const title=q('.v357LiveDetailTitle',liveView);
    if(title)title.textContent=name==='twitch'?'Twitch':'YouTube';
    liveView.classList.add('v357LiveOpen');
  }

  function buildLiveHierarchy(){
    if(!liveView||q('.v357LiveRoot',liveView))return;
    const twitch=q('.livePlatformTwitch',liveView);
    const youtube=q('.livePlatformYoutube',liveView);
    if(!twitch||!youtube)return;
    const scroller=q('.folderScroller',liveView);
    if(!scroller)return;
    const oldParent=twitch.parentElement;

    const root=document.createElement('div');
    root.className='v357LiveRoot';
    root.innerHTML=`
      <button class="v357LiveFolder" type="button" data-v357-live="twitch"><span class="v357LiveFolderIcon">◧</span><span class="v357LiveFolderCopy"><b>Twitch</b><small>Live, VOD e Highlights di Twitch.</small></span><i class="v357LiveFolderArrow">›</i></button>
      <button class="v357LiveFolder" type="button" data-v357-live="youtube"><span class="v357LiveFolderIcon">▶</span><span class="v357LiveFolderCopy"><b>YouTube</b><small>Live, VOD e Highlights di YouTube.</small></span><i class="v357LiveFolderArrow">›</i></button>`;

    const detail=document.createElement('div');
    detail.className='v357LiveDetail';
    detail.innerHTML='<div class="v357LiveDetailHead"><button class="v357LiveBack" type="button">‹ Live</button><div class="v357LiveDetailTitle"></div></div><div class="v357LiveDetailBody"></div>';
    const body=q('.v357LiveDetailBody',detail);
    body.appendChild(twitch);
    body.appendChild(youtube);
    scroller.insertBefore(root,scroller.firstChild);
    scroller.insertBefore(detail,root.nextSibling);
    if(oldParent&&oldParent!==scroller&&oldParent.children.length===0)oldParent.style.display='none';

    qa('[data-v357-live]',root).forEach((b)=>b.addEventListener('click',()=>openLivePlatform(b.dataset.v357Live)));
    q('.v357LiveBack',detail).addEventListener('click',closeLivePlatform);
  }

  function closeSocialDetail(){
    if(profileView)profileView.classList.remove('v357SocialOpen');
  }

  function openSocialDetail(){
    if(mobile()&&profileView)profileView.classList.add('v357SocialOpen');
  }

  function buildSocialHierarchy(){
    if(!profileView)return;
    const social=q('.profileSocialRef',profileView);
    const head=q('.profileSocialRefHead',social||profileView);
    const rows=q('.profileSocialRows',social||profileView);
    if(!social||!head||!rows)return;
    if(!q('.v357SocialFolderChevron',social)){
      const chevron=document.createElement('i');
      chevron.className='v357SocialFolderChevron';
      chevron.textContent='›';
      social.appendChild(chevron);
    }
    if(!q('.v357SocialBack',social)){
      const back=document.createElement('button');
      back.type='button';
      back.className='v357SocialBack';
      back.textContent='‹ Profilo';
      back.addEventListener('click',(e)=>{e.stopPropagation();closeSocialDetail();});
      social.insertBefore(back,social.firstChild);
    }
    head.setAttribute('role','button');
    head.setAttribute('tabindex','0');
    head.addEventListener('click',()=>{if(!profileView.classList.contains('v357SocialOpen'))openSocialDetail();});
    head.addEventListener('keydown',(e)=>{if((e.key==='Enter'||e.key===' ')&&!profileView.classList.contains('v357SocialOpen')){e.preventDefault();openSocialDetail();}});
  }

  function syncViewChrome(){
    const active=q('.view.active',hub);
    const name=active&&active.dataset?active.dataset.view:'';
    hub.classList.toggle('v357NoLegacyTop',mobile()&&(name==='projects'||name==='live'));
    if(name!==lastView){
      if(name==='live')closeLivePlatform();
      if(name!=='profile')closeSocialDetail();
      lastView=name;
    }
    if(!mobile()){
      hub.classList.remove('v357NoLegacyTop');
      closeLivePlatform();
      closeSocialDetail();
    }
  }

  function apply(){
    buildLiveHierarchy();
    buildSocialHierarchy();
    syncViewChrome();
    const f=hub; f.dataset.v357Bound='1';
  }

  apply();
  setTimeout(apply,80);
  setTimeout(apply,300);
  setTimeout(apply,900);
  try{
    new MutationObserver(syncViewChrome).observe(q('.stage',hub)||hub,{subtree:true,attributes:true,attributeFilter:['class']});
  }catch(_e){}
  window.addEventListener('resize',syncViewChrome,{passive:true});
})();
</script>
'''


def patch_text(text: str) -> str:
    if MARK in text:
        return text
    required = (
        'V311 APPROVED CREATOR REFERENCE',
        'id="v352CreatorMobilePages"',
        'id="projectHubCards"',
        'livePlatformTwitch',
        'livePlatformYoutube',
        'profileSocialRef',
        'profileSocialRows',
        'profileSocialRefRow',
    )
    for marker in required:
        if marker not in text:
            raise RuntimeError('V357 missing Creator Hub anchor: ' + marker)
    if '</body>' not in text:
        raise RuntimeError('V357 Creator Hub </body> anchor missing')
    return text.replace('</body>', PATCH + '\n</body>', 1)


def main() -> None:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V357 Creator Hub target missing: ' + str(path))
    before = path.read_text(encoding='utf-8')
    after = patch_text(before)
    path.write_text(after, encoding='utf-8')
    print('V357 Creator Hub hierarchy applied changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
