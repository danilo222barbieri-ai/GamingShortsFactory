#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')
DEFAULT_APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')
CACHE_KEY = '3115'
PROFILE_CACHE = 'profile-ref-2'

# V311 stays the single authoritative Creator Hub source. This revision keeps
# Dashboard / Projects / Live intact and makes Profile match the approved mobile
# reference directly, without adding another startup patch layer.
STYLE = r'''
<style id="v311HubForce">
/* V311 MOBILE HUB CLEAN PASS */
/* V311 SOURCE NORMALIZED */
/* V311 APPROVED CREATOR REFERENCE */
html,body{overflow:hidden!important}
#hub{height:100dvh!important;min-height:0!important;overflow:hidden!important;padding:8px 10px 6px!important;box-sizing:border-box!important}
#hub .stage{height:100%!important;min-height:0!important;overflow:hidden!important}

/* Approved dashboard: creator summary + Profile / Projects / Live. */
#hub .view[data-view="dashboard"]{height:100%!important;overflow:hidden!important}
#hub .view[data-view="dashboard"] .dashboard{
  height:100%!important;min-height:0!important;box-sizing:border-box!important;
  display:grid!important;grid-template-rows:136px minmax(0,1fr)!important;
  gap:12px!important;padding:0 0 94px!important;align-content:stretch!important;
}
#hub .view[data-view="dashboard"] .profileCard{
  min-height:136px!important;height:136px!important;padding:14px 16px!important;
  border:1px solid rgba(143,181,216,.22)!important;border-radius:28px!important;
  background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(234,248,255,.91) 55%,rgba(235,251,244,.89))!important;
  box-shadow:0 14px 34px rgba(61,104,145,.075),inset 0 1px 0 rgba(255,255,255,.99)!important;
  grid-template-columns:auto minmax(0,1fr)!important;gap:15px!important;align-items:center!important;
}
#hub .view[data-view="dashboard"] .profileCard .avatar{
  width:76px!important;height:76px!important;border-radius:50%!important;font-size:24px!important;
  border:3px solid rgba(255,255,255,.96)!important;box-shadow:0 5px 18px rgba(40,154,224,.18)!important;
}
#hub .view[data-view="dashboard"] .profileName{font-size:22px!important;line-height:1!important;letter-spacing:-.025em!important}
#hub .view[data-view="dashboard"] .profileMeta{font-size:13px!important;line-height:1.2!important;margin-top:5px!important}
#hub .view[data-view="dashboard"] .badges{margin-top:8px!important;gap:7px!important}
#hub .view[data-view="dashboard"] .badge{font-size:10px!important;padding:5px 9px!important;border-radius:12px!important}
#hub .view[data-view="dashboard"] .profileSocials{margin-top:8px!important;gap:7px!important}
#hub .view[data-view="dashboard"] .profileSocials .socialDot{width:32px!important;height:32px!important;border-radius:11px!important;font-size:13px!important}
#hub .view[data-view="dashboard"] .profileAction{display:none!important}
#hub .view[data-view="dashboard"] .folders{
  width:100%!important;height:100%!important;min-height:0!important;display:grid!important;
  grid-template-columns:1fr!important;grid-template-rows:repeat(3,minmax(0,1fr))!important;
  gap:12px!important;align-content:stretch!important;overflow:hidden!important;
  border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;
}
#hub .view[data-view="dashboard"] .folder,
#hub .view[data-view="dashboard"] .folder[data-folder]{
  position:relative!important;width:100%!important;height:100%!important;min-height:0!important;margin:0!important;
  padding:15px 18px!important;border:1px solid rgba(143,181,216,.19)!important;border-radius:26px!important;
  background:rgba(255,255,255,.95)!important;box-shadow:0 12px 28px rgba(61,104,145,.07),inset 0 1px 0 rgba(255,255,255,.99)!important;
  display:grid!important;grid-template-columns:auto minmax(0,1fr) auto!important;grid-template-rows:auto auto!important;
  column-gap:16px!important;row-gap:3px!important;align-items:center!important;text-align:left!important;
}
#hub .view[data-view="dashboard"] .folder::after{display:none!important}
#hub .view[data-view="dashboard"] .folder>div:first-child,
#hub .view[data-view="dashboard"] .folderTop{display:contents!important}
#hub .view[data-view="dashboard"] .folderIcon{
  grid-column:1!important;grid-row:1/3!important;width:58px!important;height:58px!important;border-radius:20px!important;
  font-size:22px!important;align-self:center!important;display:grid!important;place-items:center!important;
}
#hub .view[data-view="dashboard"] .folderArrow{grid-column:3!important;grid-row:1/3!important;font-size:30px!important;align-self:center!important;color:#7f98b6!important}
#hub .view[data-view="dashboard"] .folder h2{grid-column:2!important;grid-row:1!important;margin:0!important;font-size:22px!important;line-height:1.02!important;align-self:end!important;letter-spacing:-.025em!important}
#hub .view[data-view="dashboard"] .folder p{grid-column:2!important;grid-row:2!important;margin:0!important;font-size:12.5px!important;line-height:1.18!important;align-self:start!important;color:#7589a2!important}
#hub .view[data-view="dashboard"] .folderFoot{display:none!important}

/* V311 PROFILE REFERENCE LAYOUT */
#hub.profileReferenceActive{grid-template-rows:minmax(0,1fr)!important;padding:8px 10px 0!important}
#hub.profileReferenceActive>.top{display:none!important}
#hub .view[data-view="profile"]{height:100%!important;overflow:hidden!important}
#hub .view[data-view="profile"] .detail{height:100%!important;display:block!important}
#hub .view[data-view="profile"] .detailHead{display:none!important}
#hub .view[data-view="profile"] .detailCard.profileReferenceHost{height:100%!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;overflow:hidden!important}
#hub .view[data-view="profile"] .profileReferenceScroll{height:100%!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;padding:4px 2px 104px!important;display:block!important}
#hub .profileReferenceBrand{display:flex!important;align-items:center!important;gap:10px!important;min-height:46px!important;padding:4px 16px 12px!important;color:#6f83a3!important;white-space:nowrap!important}
#hub .profileReferenceBrand b{font-size:13px!important;letter-spacing:.19em!important;color:#17366f!important;font-weight:950!important}
#hub .profileReferenceBrand span{font-size:13px!important;font-weight:750!important}
#hub .profileReferenceCard{width:100%!important;margin:0 0 12px!important;border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.95)!important;box-shadow:0 14px 34px rgba(61,104,145,.075),inset 0 1px 0 rgba(255,255,255,.99)!important}
#hub .profileReferenceEdit{min-height:278px!important;padding:22px!important;display:grid!important;grid-template-columns:150px minmax(0,1fr)!important;gap:24px!important;align-items:center!important}
#hub .profileRefPhotoCol{display:flex!important;flex-direction:column!important;align-items:center!important;gap:14px!important}
#hub .profileRefAvatar{width:116px!important;height:116px!important;border-radius:50%!important;border:4px solid rgba(255,255,255,.96)!important;box-shadow:0 6px 22px rgba(40,154,224,.18)!important;overflow:hidden!important;font-size:30px!important}
#hub .profileRefAvatar img{width:100%!important;height:100%!important;object-fit:cover!important}
#hub .profileRefPhotoBtn{min-width:130px!important;min-height:44px!important;border:0!important;border-radius:18px!important;background:#e8f6ff!important;color:#1686dc!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important;font-size:13px!important;font-weight:900!important;padding:0 14px!important;cursor:pointer!important}
#hub .profileRefPhotoBtn input{display:none!important}
#hub .profileRefMain{min-width:0!important;display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;column-gap:16px!important;row-gap:8px!important;align-items:end!important}
#hub .profileRefHeading{grid-column:1/3!important}
#hub .profileRefTitle{font-size:28px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.035em!important;color:#0d2a66!important}
#hub .profileRefSubtitle{margin-top:6px!important;font-size:14px!important;line-height:1.25!important;font-weight:720!important;color:#7185a6!important}
#hub .profileRefField{grid-column:1/3!important;margin-top:8px!important}
#hub .profileRefField label{display:block!important;margin:0 0 7px!important;font-size:12px!important;font-weight:800!important;color:#7185a6!important;text-transform:none!important;letter-spacing:0!important}
#hub .profileRefInputWrap{height:58px!important;border:1px solid rgba(143,181,216,.28)!important;border-radius:18px!important;background:rgba(249,252,255,.96)!important;display:grid!important;grid-template-columns:minmax(0,1fr) 38px!important;align-items:center!important;padding:0 10px 0 16px!important}
#hub .profileRefInputWrap input{width:100%!important;border:0!important;outline:0!important;background:transparent!important;color:#0d2a66!important;font-size:18px!important;font-weight:850!important;padding:0!important}
#hub .profileRefPencil{font-size:21px!important;color:#6f8aad!important;text-align:center!important}
#hub .profileRefSave{grid-column:2!important;min-width:196px!important;height:52px!important;border:0!important;border-radius:17px!important;background:linear-gradient(135deg,#66b5ff,#247ff0)!important;color:#fff!important;box-shadow:0 9px 20px rgba(42,126,235,.20)!important;font-size:15px!important;font-weight:900!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:9px!important;cursor:pointer!important}

#hub .profilePlanRef{padding:20px 22px!important;display:grid!important;grid-template-columns:72px minmax(0,1fr) auto!important;column-gap:18px!important;row-gap:12px!important;align-items:center!important}
#hub .profileRefSectionIcon{width:66px!important;height:66px!important;border-radius:20px!important;display:grid!important;place-items:center!important;font-size:29px!important;font-weight:950!important}
#hub .profilePlanRef .profileRefSectionIcon{background:linear-gradient(145deg,#fff4c8,#ffeaa0)!important;color:#ffad00!important}
#hub .profileSocialRef .profileRefSectionIcon{background:linear-gradient(145deg,#efe7ff,#e5dcff)!important;color:#7a4de8!important}
#hub .profileRefSectionText h2{margin:0!important;font-size:27px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.035em!important;color:#0d2a66!important}
#hub .profileRefSectionText p{margin:6px 0 0!important;font-size:13px!important;line-height:1.25!important;font-weight:720!important;color:#7185a6!important}
#hub .profileRefChevron{font-size:31px!important;line-height:1!important;color:#7f98b6!important;font-style:normal!important}
#hub .profilePlanBody{grid-column:2/4!important;display:grid!important;grid-template-columns:auto minmax(0,1fr)!important;gap:16px!important;align-items:center!important}
#hub .profilePlanPill{min-width:84px!important;height:42px!important;border-radius:16px!important;background:#fff0ba!important;color:#c78300!important;display:grid!important;place-items:center!important;padding:0 15px!important;font-size:14px!important;font-weight:950!important}
#hub .profilePlanCopy{font-size:12px!important;line-height:1.35!important;font-weight:720!important;color:#627b9b!important}
#hub .profilePlanCta{grid-column:2/4!important;width:100%!important;height:54px!important;border:0!important;border-radius:17px!important;background:linear-gradient(145deg,#eaf7ff,#dceeff)!important;color:#1180d8!important;font-size:15px!important;font-weight:900!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:9px!important;cursor:pointer!important}

#hub .profileSocialRef{padding:20px 22px 16px!important}
#hub .profileSocialRefHead{display:grid!important;grid-template-columns:72px minmax(0,1fr)!important;gap:18px!important;align-items:center!important;margin-bottom:10px!important}
#hub .profileSocialRows{display:grid!important;grid-template-columns:1fr!important;gap:0!important}
#hub .profileSocialRefRow{position:relative!important;min-height:58px!important;padding:6px 4px!important;border:0!important;border-bottom:1px solid rgba(143,181,216,.15)!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;display:grid!important;grid-template-columns:46px minmax(0,1fr) auto 24px!important;gap:10px!important;align-items:center!important;color:#0d2a66!important;cursor:pointer!important}
#hub .profileSocialRefRow:last-child{border-bottom:0!important}
#hub .profileSocialRefRow .socialLogo{width:38px!important;height:38px!important;border-radius:10px!important;display:grid!important;place-items:center!important;font-size:18px!important;font-weight:950!important}
#hub .profileSocialRefRow[data-platform="youtube"] .socialLogo{background:#ffe5e8!important;color:#ff0033!important}
#hub .profileSocialRefRow[data-platform="tiktok"] .socialLogo{background:#edf1f5!important;color:#101820!important}
#hub .profileSocialRefRow[data-platform="instagram"] .socialLogo{background:#f6e8f7!important;color:#c13584!important}
#hub .profileSocialRefRow[data-platform="facebook"] .socialLogo{background:#e7f0ff!important;color:#1877f2!important}
#hub .profileSocialRefRow[data-platform="twitch"] .socialLogo{background:#eee8ff!important;color:#9146ff!important}
#hub .profileSocialRefRow .socialName{font-size:15px!important;font-weight:900!important}
#hub .profileSocialRefRow .socialState{min-width:118px!important;min-height:34px!important;padding:0 12px!important;border-radius:999px!important;background:#eef2f6!important;color:#7488a4!important;display:flex!important;align-items:center!important;justify-content:center!important;font-size:11px!important;font-weight:900!important;white-space:nowrap!important}
#hub .profileSocialRefRow.connected .socialState{background:#ddf8eb!important;color:#168b65!important}
#hub .profileSocialChevron{font-size:26px!important;line-height:1!important;color:#7f98b6!important}
#hub .profileSocialHiddenConnect{display:none!important}
#hub .profileReferenceLegacy,#hub .profileReferenceLogout{display:none!important}

@media(max-width:390px){
  #hub.profileReferenceActive{padding-left:6px!important;padding-right:6px!important}
  #hub .profileReferenceBrand{padding-left:10px!important;padding-right:10px!important;gap:7px!important}
  #hub .profileReferenceBrand b{font-size:10px!important;letter-spacing:.15em!important}
  #hub .profileReferenceBrand span{font-size:10px!important}
  #hub .profileReferenceCard{border-radius:24px!important;margin-bottom:10px!important}
  #hub .profileReferenceEdit{min-height:248px!important;padding:16px!important;grid-template-columns:112px minmax(0,1fr)!important;gap:14px!important}
  #hub .profileRefAvatar{width:94px!important;height:94px!important}
  #hub .profileRefPhotoBtn{min-width:104px!important;min-height:40px!important;font-size:11px!important;padding:0 10px!important}
  #hub .profileRefTitle{font-size:24px!important}
  #hub .profileRefSubtitle{font-size:12px!important}
  #hub .profileRefField label{font-size:11px!important}
  #hub .profileRefInputWrap{height:52px!important;border-radius:16px!important}
  #hub .profileRefInputWrap input{font-size:16px!important}
  #hub .profileRefSave{min-width:158px!important;height:48px!important;font-size:13px!important}
  #hub .profilePlanRef,#hub .profileSocialRef{padding:16px!important}
  #hub .profilePlanRef{grid-template-columns:60px minmax(0,1fr) auto!important;column-gap:12px!important}
  #hub .profileRefSectionIcon{width:56px!important;height:56px!important;border-radius:18px!important;font-size:24px!important}
  #hub .profileRefSectionText h2{font-size:23px!important}
  #hub .profileRefSectionText p{font-size:11.5px!important}
  #hub .profilePlanBody{grid-column:1/4!important;gap:10px!important}
  #hub .profilePlanCta{grid-column:1/4!important;height:50px!important;font-size:13px!important}
  #hub .profileSocialRefHead{grid-template-columns:60px minmax(0,1fr)!important;gap:12px!important}
  #hub .profileSocialRefRow{grid-template-columns:42px minmax(0,1fr) auto 20px!important;gap:8px!important;min-height:54px!important}
  #hub .profileSocialRefRow .socialLogo{width:36px!important;height:36px!important}
  #hub .profileSocialRefRow .socialName{font-size:14px!important}
  #hub .profileSocialRefRow .socialState{min-width:104px!important;min-height:31px!important;font-size:10px!important;padding:0 10px!important}
}

/* Projects: first show two destinations, then the selected collection. */
#hub .view[data-view="projects"] .folderScroller{overflow-y:auto!important;overflow-x:hidden!important;padding-bottom:104px!important}
#hub #projectHubCards{display:grid;grid-template-columns:1fr;gap:12px;margin:2px 0 12px}
#hub .projectHubCard{min-height:118px;padding:16px 18px;border:1px solid rgba(143,181,216,.20);border-radius:24px;background:rgba(255,255,255,.96);box-shadow:0 10px 26px rgba(61,104,145,.065);display:grid;grid-template-columns:56px minmax(0,1fr) auto;gap:14px;align-items:center;text-align:left;color:var(--ink);cursor:pointer}
#hub .projectHubIcon{width:56px;height:56px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(145deg,#e7f6ff,#eef0ff);font-size:21px;color:#318fd8}
#hub .projectHubCard b{display:block;font-size:20px;line-height:1.05}
#hub .projectHubCard small{display:block;margin-top:5px;font-size:11.5px;line-height:1.25;color:#7b8da4;font-weight:750}
#hub .projectHubCard i{font-style:normal;font-size:28px;color:#8198b4}

/* V311 LIVE REFERENCE LAYOUT: no profile/launcher strip; Twitch then YouTube. */
#hub .view[data-view="live"] .profileCard{display:none!important}
#hub .view[data-view="live"] .detail{grid-template-rows:minmax(0,1fr)!important;gap:0!important}
#hub .view[data-view="live"] .detailHead{display:none!important}
#hub .view[data-view="live"] .detailCard{padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
#hub .view[data-view="live"] .folderScroller{overflow-y:auto!important;overflow-x:hidden!important;padding:2px 2px 104px!important}
#hub .view[data-view="live"] .liveRootFolders{display:none!important}
#hub .view[data-view="live"] .livePane[data-live-pane="twitch"],
#hub .view[data-view="live"] .livePane[data-live-pane="youtube"]{display:block!important}
#hub .view[data-view="live"] .livePlatformCard{margin:0 0 14px!important;padding:16px!important;border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.94)!important;box-shadow:0 14px 34px rgba(61,104,145,.075),inset 0 1px 0 rgba(255,255,255,.99)!important}
#hub .view[data-view="live"] .livePlatformHead{display:grid!important;grid-template-columns:58px minmax(0,1fr)!important;gap:14px!important;align-items:center!important;margin-bottom:12px!important}
#hub .view[data-view="live"] .livePlatformIcon{width:58px!important;height:58px!important;border-radius:19px!important;display:grid!important;place-items:center!important;font-size:24px!important;font-weight:950!important}
#hub .view[data-view="live"] .livePlatformTwitch .livePlatformIcon{background:linear-gradient(145deg,#f0e8ff,#e9ddff)!important;color:#9146ff!important}
#hub .view[data-view="live"] .livePlatformYoutube .livePlatformIcon{background:linear-gradient(145deg,#ffe8ee,#fff0f3)!important;color:#ff1744!important}
#hub .view[data-view="live"] .livePaneTitle{margin:0!important;font-size:24px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.025em!important;color:#0d2a66!important}
#hub .view[data-view="live"] .livePlatformSubtitle{margin-top:5px!important;font-size:12px!important;line-height:1.28!important;font-weight:720!important;color:#7185a6!important}
#hub .view[data-view="live"] .liveMiniFolders{display:grid!important;grid-template-columns:1fr!important;gap:8px!important}
#hub .view[data-view="live"] .liveMiniFolder{min-height:72px!important;padding:10px 12px!important;border:1px solid rgba(143,181,216,.14)!important;border-radius:20px!important;background:rgba(252,254,255,.98)!important;box-shadow:0 7px 18px rgba(61,104,145,.035)!important;display:grid!important;grid-template-columns:48px minmax(0,1fr) auto!important;gap:12px!important;align-items:center!important;color:#0d2a66!important;text-align:left!important}
#hub .view[data-view="live"] .liveMiniFolder>span{width:48px!important;height:48px!important;border-radius:16px!important;display:grid!important;place-items:center!important;font-size:19px!important;font-weight:900!important}
#hub .view[data-view="live"] .livePlatformTwitch .liveMiniFolder>span{background:#f2eaff!important;color:#9146ff!important}
#hub .view[data-view="live"] .livePlatformYoutube .liveMiniFolder>span{background:#ffeaf0!important;color:#ff1744!important}
#hub .view[data-view="live"] .liveMiniFolder b{display:block!important;font-size:16px!important;line-height:1.05!important;font-weight:930!important}
#hub .view[data-view="live"] .liveMiniFolder small{display:block!important;margin-top:4px!important;font-size:11px!important;line-height:1.2!important;font-weight:700!important;color:#7185a6!important}
#hub .view[data-view="live"] .liveMiniFolder i{font-style:normal!important;font-size:26px!important;color:#7f98b6!important}
#hub .view[data-view="live"] .liveMiniContent{display:none!important}
@media(max-width:390px){
  #hub .view[data-view="live"] .livePlatformCard{padding:13px!important;border-radius:24px!important}
  #hub .view[data-view="live"] .livePlatformHead{grid-template-columns:52px minmax(0,1fr)!important;gap:11px!important}
  #hub .view[data-view="live"] .livePlatformIcon{width:52px!important;height:52px!important;border-radius:17px!important;font-size:22px!important}
  #hub .view[data-view="live"] .livePaneTitle{font-size:22px!important}
  #hub .view[data-view="live"] .livePlatformSubtitle{font-size:11px!important}
  #hub .view[data-view="live"] .liveMiniFolder{min-height:68px!important;grid-template-columns:44px minmax(0,1fr) auto!important;gap:10px!important;padding:9px 10px!important}
  #hub .view[data-view="live"] .liveMiniFolder>span{width:44px!important;height:44px!important;border-radius:14px!important;font-size:17px!important}
  #hub .view[data-view="live"] .liveMiniFolder b{font-size:15px!important}
  #hub .view[data-view="live"] .liveMiniFolder small{font-size:10.5px!important}
}
/* END V311 MOBILE HUB CLEAN PASS */
</style>
'''

PROJECT_LANDING = '''      <div id="projectHubCards" aria-label="I miei progetti">
       <button class="projectHubCard" type="button" data-project-dest="shorts"><span class="projectHubIcon">▣</span><span><b>I miei Shorts</b><small>Short finali, pronti da rivedere e condividere.</small></span><i>›</i></button>
       <button class="projectHubCard" type="button" data-project-dest="drafts"><span class="projectHubIcon">□</span><span><b>Bozze</b><small>Progetti salvati da riprendere quando vuoi.</small></span><i>›</i></button>
      </div>
'''

PROFILE_NEW = '''<section class="view" data-view="profile">
   <div class="detail">
    <div class="detailHead"><div class="detailHeadText"><h2>Profilo</h2><p>Gestisci le tue informazioni.</p></div></div>
    <div class="detailCard profileReferenceHost"><div class="folderScroller profileOnlyScroller profileReferenceScroll">
      <div class="profileReferenceBrand"><b>GAMING SHORTS FACTORY</b><span>|</span><span>Creator Hub</span></div>
      <div class="profileReferenceCard profileReferenceEdit profileEdit">
       <div class="profileRefPhotoCol profilePhotoEdit">
        <div class="avatar profileAvatarBig profileRefAvatar" id="profileAvatar"><img id="profileAvatarImg" alt=""><span class="avatarInitial" id="profileAvatarInitial">C</span></div>
        <label class="photoBtn profileRefPhotoBtn"><span>▣</span><span>Cambia foto</span><input id="profilePhotoInput" type="file" accept="image/jpeg,image/png,image/webp"></label>
       </div>
       <div class="profileRefMain profileField">
        <div class="profileRefHeading"><div class="profileRefTitle">Profilo</div><div class="profileRefSubtitle">Gestisci le tue informazioni.</div></div>
        <div class="profileRefField"><label for="profileNameInput">Nome del creator</label><div class="profileRefInputWrap"><input id="profileNameInput" maxlength="80" value="Creator"><span class="profileRefPencil">✎</span></div></div>
        <button class="saveProfileBtn profileRefSave" id="saveProfileBtn" type="button"><span>▣</span><span>Salva profilo</span></button>
       </div>
      </div>

      <div class="profileReferenceCard profilePlanRef">
       <div class="profileRefSectionIcon">♛</div>
       <div class="profileRefSectionText"><h2>Abbonamento</h2><p>Il tuo piano attuale e vantaggi.</p></div>
       <i class="profileRefChevron">›</i>
       <div class="profilePlanBody"><b class="profilePlanPill" id="profileOverviewPlan">FREE</b><div class="profilePlanCopy">Stai utilizzando il piano Free. Accedi a strumenti essenziali per creare e gestire i tuoi Shorts.</div></div>
       <button class="profilePlanCta" type="button" data-profile-overview="subscription"><span>♛</span><span>Scopri i piani Pro</span></button>
      </div>

      <div class="profileReferenceCard profileSocialRef">
       <div class="profileSocialRefHead"><div class="profileRefSectionIcon">↗</div><div class="profileRefSectionText"><h2>Social collegati</h2><p>Collega i tuoi account per pubblicare più facilmente.</p></div></div>
       <div class="profileSocialRows">
        <div class="socialCard profileSocialRefRow" data-platform="youtube" data-profile-social-connect="youtube"><div class="socialLogo">▶</div><div class="socialName">YouTube</div><div class="socialState">Non collegato</div><span class="profileSocialChevron">›</span><button class="connectBtn profileSocialHiddenConnect" data-connect="youtube">Collega</button></div>
        <div class="socialCard profileSocialRefRow" data-platform="tiktok" data-profile-social-connect="tiktok"><div class="socialLogo">♪</div><div class="socialName">TikTok</div><div class="socialState">Non collegato</div><span class="profileSocialChevron">›</span><button class="connectBtn profileSocialHiddenConnect" data-connect="tiktok">Collega</button></div>
        <div class="socialCard profileSocialRefRow" data-platform="instagram" data-profile-social-connect="instagram"><div class="socialLogo">◎</div><div class="socialName">Instagram</div><div class="socialState">Non collegato</div><span class="profileSocialChevron">›</span><button class="connectBtn profileSocialHiddenConnect" data-connect="instagram">Collega</button></div>
        <div class="socialCard profileSocialRefRow" data-platform="facebook" data-profile-social-connect="facebook"><div class="socialLogo">f</div><div class="socialName">Facebook</div><div class="socialState">Non collegato</div><span class="profileSocialChevron">›</span><button class="connectBtn profileSocialHiddenConnect" data-connect="facebook">Collega</button></div>
        <div class="socialCard profileSocialRefRow" data-platform="twitch" data-profile-social-connect="twitch"><div class="socialLogo">◧</div><div class="socialName">Twitch</div><div class="socialState">Non collegato</div><span class="profileSocialChevron">›</span><button class="connectBtn profileSocialHiddenConnect" data-connect="twitch">Collega</button></div>
       </div>
       <span id="profileOverviewSocial" hidden>0/5</span>
      </div>

      <div class="profileReferenceLegacy" aria-hidden="true">
       <button class="profileOverviewCard" type="button" data-profile-overview="subscription"></button>
       <button class="profileOverviewCard" type="button" data-profile-overview="social"></button>
      </div>
      <button class="logoutProfile profileReferenceLogout" id="logoutProfile" type="button">Disconnetti dal Creator Hub</button>
    </div></div>
   </div>
  </section>'''

TWITCH_NEW = '''<div class="livePane active livePlatformCard livePlatformTwitch" data-live-pane="twitch">
       <div class="livePlatformHead"><span class="livePlatformIcon">◧</span><div><div class="livePaneTitle">Twitch</div><div class="livePlatformSubtitle">Gestisci e riutilizza i contenuti delle tue live su Twitch.</div></div></div>
       <div class="liveMiniFolders">
        <button class="liveMiniFolder active" data-live-mini="sessions"><span>▣</span><div><b>Le tue live</b><small>Tutte le live trasmesse su Twitch.</small></div><i>›</i></button>
        <button class="liveMiniFolder" data-live-mini="vod"><span>▶</span><div><b>VOD</b><small>Rivedi e gestisci i tuoi VOD.</small></div><i>›</i></button>
        <button class="liveMiniFolder" data-live-mini="twitch-highlights"><span>✦</span><div><b>Highlights</b><small>I momenti migliori delle tue live.</small></div><i>›</i></button>
       </div>
       <div id="liveMiniContent" class="liveMiniContent"></div>
      </div>'''

YOUTUBE_NEW = '''<div class="livePane livePlatformCard livePlatformYoutube" data-live-pane="youtube">
       <div class="livePlatformHead"><span class="livePlatformIcon">▶</span><div><div class="livePaneTitle">YouTube</div><div class="livePlatformSubtitle">Gestisci e riutilizza i contenuti delle tue live su YouTube.</div></div></div>
       <div class="liveMiniFolders youtubeLiveFolders">
        <div class="liveMiniFolder"><span>▣</span><div><b>Le tue live</b><small>Tutte le live trasmesse su YouTube.</small></div><i>›</i></div>
        <div class="liveMiniFolder"><span>▶</span><div><b>VOD</b><small>Rivedi e gestisci i tuoi VOD.</small></div><i>›</i></div>
        <div class="liveMiniFolder"><span>✦</span><div><b>Highlights</b><small>I momenti migliori delle tue live.</small></div><i>›</i></div>
       </div>
      </div>'''

RUNTIME = r'''
<script id="v311HubRuntime">
(()=>{
  document.documentElement.dataset.gsfHubVersion='3115';
  const $=(q)=>document.querySelector(q), $$=(q)=>[...document.querySelectorAll(q)];
  const showProjectLanding=()=>{
    const landing=$('#projectHubCards'); if(!landing)return;
    landing.style.display='grid';
    $$('[data-project-pane]').forEach((p)=>p.style.display='none');
    const title=$('#projectsViewTitle'), sub=$('#projectsViewSubtitle');
    if(title)title.textContent='I miei progetti';
    if(sub)sub.textContent='I miei Shorts e Bozze, nello stesso posto.';
  };
  const openProjectDest=(dest)=>{
    const landing=$('#projectHubCards'); if(landing)landing.style.display='none';
    $$('[data-project-pane]').forEach((p)=>p.style.display=p.dataset.projectPane===dest?'':'none');
    const title=$('#projectsViewTitle'), sub=$('#projectsViewSubtitle');
    if(title)title.textContent=dest==='shorts'?'I miei Shorts':'Bozze';
    if(sub)sub.textContent=dest==='shorts'?'Tutti gli Shorts completati e salvati nel Creator Hub.':'Progetti salvati da riprendere quando vuoi.';
  };
  const syncProfileShell=()=>{
    const hub=$('#hub'), profile=$('.view[data-view="profile"]');
    if(hub)hub.classList.toggle('profileReferenceActive',!!(profile&&profile.classList.contains('active')));
  };
  const bind=()=>{
    $$('[data-project-dest]').forEach((b)=>{b.onclick=()=>openProjectDest(b.dataset.projectDest)});
    const projectFolder=$('[data-folder="projects"]');
    if(projectFolder)projectFolder.addEventListener('click',()=>setTimeout(showProjectLanding,0));
    $$('[data-profile-social-connect]').forEach((row)=>{
      row.onclick=(e)=>{
        if(e.target.closest('.profileSocialHiddenConnect'))return;
        const b=row.querySelector('.profileSocialHiddenConnect');
        if(b&&!b.disabled)b.click();
      };
    });
    const profile=$('.view[data-view="profile"]');
    if(profile)new MutationObserver(syncProfileShell).observe(profile,{attributes:true,attributeFilter:['class']});
    syncProfileShell();
  };
  window.addEventListener('message',(e)=>{
    if(!e.data||e.data.type!=='GSF_HUB_FOCUS')return;
    if(String(e.data.section||'')==='projects')setTimeout(showProjectLanding,0);
    setTimeout(syncProfileShell,0);
  });
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
})();
</script>
'''


def _strip_old_v311(text: str) -> str:
    text = re.sub(r'\s*<style id="v311HubForce">.*?</style>\s*(?=</head>)','\n',text,count=1,flags=re.DOTALL)
    text = re.sub(r'\s*<script id="v311HubRuntime">.*?</script>\s*(?=</body>)','\n',text,count=1,flags=re.DOTALL)
    return text


def _remove_profile_mobile_plan(text: str) -> str:
    token = '<div class="profileGroup profilePlanGroup profileMobilePlan"'
    start = text.find(token)
    if start < 0: return text
    line_start = text.rfind('\n',0,start)+1
    anchors=[text.find('<div class="profileMural profileOnlyMural"',start),text.find('<div class="profileOverviewGrid"',start)]
    anchors=[p for p in anchors if p>=0]
    if not anchors: raise RuntimeError('V311: profile mobile plan end anchor missing')
    return text[:line_start]+text[min(anchors):]


def _remove_profile_overview_actions(text: str) -> str:
    token='<div class="profileOverviewActions">'
    start=text.find(token)
    if start<0:return text
    line_start=text.rfind('\n',0,start)+1
    end=text.find('<button class="logoutProfile"',start)
    if end<0:raise RuntimeError('V311: profile overview actions end anchor missing')
    return text[:line_start]+text[end:]


def _remove_live_root(text: str) -> str:
    token='<div class="liveRootFolders">'
    start=text.find(token)
    if start<0:return text
    line_start=text.rfind('\n',0,start)+1
    end=text.find('<div class="livePane',start)
    if end<0:raise RuntimeError('V311: live root end anchor missing')
    return text[:line_start]+text[end:]


def _remove_dashboard_folder(text: str, name: str) -> str:
    return re.sub(r'^\s*<button class="folder" data-folder="'+re.escape(name)+r'">.*?</button>\s*$','',text,count=1,flags=re.MULTILINE)


def _remove_profile_card(text: str, name: str) -> str:
    return re.sub(r'^\s*<button class="profileOverviewCard"[^>]*data-profile-overview="'+re.escape(name)+r'".*?</button>\s*$','',text,count=1,flags=re.MULTILINE)


def normalize_profile_reference(text: str) -> str:
    start=text.find('<section class="view" data-view="profile">')
    if start<0:return text
    end=text.find('<section class="view" data-view="social">',start)
    if end<0:raise RuntimeError('V311: Profile section end anchor missing')
    return text[:start]+PROFILE_NEW+'\n\n  '+text[end:]


def normalize_live_reference(text: str) -> str:
    start=text.find('<section class="view" data-view="live">')
    if start<0:return text
    end=text.find('</section>',start)
    if end<0:raise RuntimeError('V311: Live section end anchor missing')
    end+=len('</section>')
    live=text[start:end]
    live=re.sub(r'\s*<div class="profileCard"[^>]*>.*?(?=<div class="detail">)', '\n ', live, count=1, flags=re.DOTALL)
    live=_remove_live_root(live)
    live=re.sub(r'\s*<div class="livePane" data-live-pane="highlights">.*?</div></div>\s*','\n',live,count=1,flags=re.DOTALL)
    if 'livePlatformTwitch' not in live:
        twitch_pattern=r'<div class="livePane active" data-live-pane="twitch">.*?(?=\s*<div class="livePane" data-live-pane="youtube">)'
        live,count=re.subn(twitch_pattern,TWITCH_NEW+'\n\n      ',live,count=1,flags=re.DOTALL)
        if count!=1:raise RuntimeError('V311: Twitch Live pane anchor missing')
    if 'livePlatformYoutube' not in live:
        youtube_pattern=r'<div class="livePane" data-live-pane="youtube">.*?(?=\s*(?:<div class="livePane" data-live-pane="highlights">|</div></div>\s*</div>\s*</section>))'
        live,count=re.subn(youtube_pattern,YOUTUBE_NEW+'\n',live,count=1,flags=re.DOTALL)
        if count!=1:raise RuntimeError('V311: YouTube Live pane anchor missing')
    return text[:start]+live+text[end:]


def _normalize_structure(text: str) -> str:
    text=re.sub(r'^\s*<div class="hubMural">.*?</div>\s*$','',text,count=1,flags=re.MULTILINE)
    text=_remove_dashboard_folder(text,'social')
    text=_remove_dashboard_folder(text,'subscription')
    text=text.replace('<h2>Le mie live</h2>','<h2>Live</h2>',1)
    text=_remove_profile_mobile_plan(text)
    text=_remove_profile_overview_actions(text)
    text=_remove_profile_card(text,'shorts')
    text=_remove_profile_card(text,'drafts')
    text=normalize_profile_reference(text)
    if 'id="projectHubCards"' not in text:
        anchor='''    <div class="detailCard"><div class="folderScroller">\n      <div class="projectSection" data-project-pane="drafts">'''
        if anchor not in text: raise RuntimeError('V311: Projects landing anchor missing')
        text=text.replace(anchor,'    <div class="detailCard"><div class="folderScroller">\n'+PROJECT_LANDING+'      <div class="projectSection" data-project-pane="drafts">',1)
    text=re.sub(r'^[ \t]*\$\("#projectRows"\)\.innerHTML=.*?;\s*$','   $("#projectRows").innerHTML="";',text,count=1,flags=re.MULTILINE)
    text=normalize_live_reference(text)
    return text


def patch_hub_text(text: str) -> str:
    if ('V311 APPROVED CREATOR REFERENCE' in text and 'V311 PROFILE REFERENCE LAYOUT' in text and 'V311 LIVE REFERENCE LAYOUT' in text and 'id="v311HubForce"' in text and 'id="v311HubRuntime"' in text and "gsfHubVersion='3115'" in text and 'profileReferenceEdit' in text and 'livePlatformTwitch' in text and 'livePlatformYoutube' in text and 'youtubeLiveFolders' in text and 'id="projectHubCards"' in text):
        return text
    text=_strip_old_v311(text)
    text=_normalize_structure(text)
    if '</head>' not in text:raise RuntimeError('V311: head anchor missing')
    if '</body>' not in text:raise RuntimeError('V311: body anchor missing')
    text=text.replace('</head>',STYLE+'\n</head>',1)
    text=text.replace('</body>',RUNTIME+'\n</body>',1)
    return text


def _button_pattern(*, active: str | None = None, section: str | None = None, target: str | None = None) -> re.Pattern:
    checks=[]
    if active is not None: checks.append(r'(?=[^>]*\bdata-active="'+re.escape(active)+r'")')
    if section is not None: checks.append(r'(?=[^>]*\bdata-section="'+re.escape(section)+r'")')
    if target is not None: checks.append(r'(?=[^>]*\bdata-target="'+re.escape(target)+r'")')
    return re.compile(r'<button\b'+''.join(checks)+r'[^>]*>.*?</button>',re.DOTALL)


def _set_attr(button: str, name: str, value: str) -> str:
    attr=name+'="'+value+'"'
    if re.search(r'\b'+re.escape(name)+r'="[^"]*"',button):
        return re.sub(r'\b'+re.escape(name)+r'="[^"]*"',attr,button,count=1)
    return button.replace('>', ' '+attr+'>', 1)


def _find_button(text: str, *, active: str | None = None, section: str | None = None, target: str | None = None):
    pat=_button_pattern(active=active,section=section,target=target)
    return pat,pat.search(text)


def _replace_gamebar(text: str) -> str:
    home_pat,home_match=_find_button(text,active='home')
    if not home_match: home_pat,home_match=_find_button(text,target='home')
    if home_match:
        home=home_match.group(0)
        home=_set_attr(home,'data-target','hub');home=_set_attr(home,'data-section','dashboard');home=_set_attr(home,'data-active','home')
        text=home_pat.sub(lambda _m:home,text,count=1)
    shorts_pat,shorts_match=_find_button(text,active='shorts')
    if not shorts_match: shorts_pat,shorts_match=_find_button(text,section='shorts')
    if shorts_match:text=shorts_pat.sub('',text,count=1)
    drafts_pat,drafts_match=_find_button(text,active='drafts')
    if not drafts_match: drafts_pat,drafts_match=_find_button(text,section='drafts')
    if drafts_match:
        projects=drafts_match.group(0)
        projects=_set_attr(projects,'data-target','hub');projects=_set_attr(projects,'data-section','projects');projects=_set_attr(projects,'data-active','projects')
        projects=projects.replace('<span>Bozze</span>','<span>Progetti</span>',1)
        text=drafts_pat.sub(lambda _m:projects,text,count=1)
    if "activeKey==='projects'" not in text:
        anchor="else if(activeKey==='live') active=(lastTarget==='hub'&&lastSection==='live');"
        if anchor in text:text=text.replace(anchor,"else if(activeKey==='projects') active=(lastTarget==='hub'&&lastSection==='projects');\n"+anchor,1)
    text=re.sub(r"else if\(target==='hub'\) active=\(lastTarget==='hub'&&lastSection!=='drafts'&&lastSection!=='shorts'&&lastSection!=='live'\);","else if(target==='hub') active=(lastTarget==='hub'&&(lastSection==='dashboard'||!lastSection));",text,count=1)
    text=re.sub(r'grid-template-columns\s*:\s*repeat\(5\s*,\s*minmax\(0\s*,\s*1fr\)\)', 'grid-template-columns:repeat(4,minmax(0,1fr))', text)
    return text


def patch_shell_text(text: str) -> str:
    text=_replace_gamebar(text)
    target=f'/creator-hub-v156/?v={CACHE_KEY}&ui={PROFILE_CACHE}'
    if target not in text:
        text,count=re.subn(r'/creator-hub-v156/\?v=[^"\'\s]+',target,text)
        if count<1:raise RuntimeError('V311: Creator Hub shell cache anchor missing')
    return text


def main():
    hub=Path(sys.argv[1]) if len(sys.argv)>1 else DEFAULT_HUB
    app=Path(sys.argv[2]) if len(sys.argv)>2 else DEFAULT_APP
    if not hub.is_file():raise SystemExit(f'V311 target missing: {hub}')
    if not app.is_file():raise SystemExit(f'V311 shell missing: {app}')
    before=hub.read_text(encoding='utf-8')
    after=patch_hub_text(before)
    hub.write_text(after,encoding='utf-8')
    shell_before=app.read_text(encoding='utf-8')
    shell_after=patch_shell_text(shell_before)
    compile(shell_after,str(app),'exec')
    app.write_text(shell_after,encoding='utf-8')
    print('V311 Creator Hub approved reference applied:',hub,'changed=',before!=after,flush=True)
    print('V311 four-item Game Bar + cache key:','v='+CACHE_KEY,'changed=',shell_before!=shell_after,flush=True)


if __name__=='__main__':
    main()
