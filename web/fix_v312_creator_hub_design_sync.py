#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')

CSS = r'''
/* V312 CREATOR HUB DESIGN SYNC */
@media(max-width:760px){
  #hub{
    padding:8px 10px calc(10px + env(safe-area-inset-bottom))!important;
    background:
      radial-gradient(circle at 9% 7%,rgba(126,214,255,.20),transparent 26%),
      radial-gradient(circle at 92% 8%,rgba(127,236,197,.17),transparent 28%),
      linear-gradient(180deg,#FCFEFF 0%,#F7FCFF 58%,#F2F9FF 100%)!important;
  }
  #hub .top{min-height:44px!important;padding:0 4px!important}
  #hub .titleIcon{display:none!important}
  #hub .top h1{font-size:14px!important;letter-spacing:.17em!important;text-transform:uppercase!important;color:#4F6F9F!important}
  #hub .top .subtitle{display:none!important}
  #hub .closeTop{border-radius:999px!important;padding:8px 11px!important;background:rgba(255,255,255,.88)!important}
  #hub .stage{overflow:hidden!important}
  #hub .view.active{overflow:auto!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;padding-bottom:calc(96px + env(safe-area-inset-bottom))!important}
  #hub .detail{height:auto!important;min-height:100%!important;display:block!important}
  #hub .detailHead{padding:6px 4px 10px!important;display:block!important}
  #hub .detailHeadText h2{font-size:clamp(28px,8vw,38px)!important;line-height:1!important;letter-spacing:-.04em!important;color:#0D2A66!important}
  #hub .detailHeadText p{margin-top:8px!important;font-size:13px!important;line-height:1.25!important;color:#7185A6!important}
  #hub .detailCard{padding:0!important;border:0!important;background:transparent!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;overflow:visible!important}
  #hub .folderScroller{height:auto!important;overflow:visible!important;padding:0!important}

  /* Dashboard: the approved master page has only Profile, Projects and Live. */
  #hub .view[data-view="dashboard"] .dashboard{display:block!important;height:auto!important}
  #hub .view[data-view="dashboard"] .profileCard{
    min-height:142px!important;margin:6px 0 14px!important;padding:16px!important;border-radius:28px!important;
    grid-template-columns:auto minmax(0,1fr)!important;gap:15px!important;background:rgba(255,255,255,.88)!important;
    box-shadow:0 16px 40px rgba(61,104,145,.08),inset 0 1px 0 rgba(255,255,255,.98)!important;
  }
  #hub .view[data-view="dashboard"] .avatar{width:72px!important;height:72px!important;border-radius:50%!important}
  #hub .view[data-view="dashboard"] .profileName{font-size:28px!important;line-height:1!important}
  #hub .view[data-view="dashboard"] .profileMeta{font-size:12px!important;margin-top:5px!important}
  #hub .view[data-view="dashboard"] .badges{margin-top:8px!important;gap:7px!important}
  #hub .view[data-view="dashboard"] .badge{font-size:10px!important;padding:6px 9px!important}
  #hub .view[data-view="dashboard"] .profileSocials{margin-top:9px!important;gap:7px!important}
  #hub .view[data-view="dashboard"] .socialDot{width:36px!important;height:36px!important;border-radius:12px!important;font-size:12px!important}
  #hub .view[data-view="dashboard"] .hubMural{display:none!important}
  #hub .view[data-view="dashboard"] .folders{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:none!important;gap:12px!important;height:auto!important;overflow:visible!important;background:transparent!important}
  #hub .view[data-view="dashboard"] .folder{
    display:grid!important;grid-template-columns:auto minmax(0,1fr) auto!important;grid-template-rows:auto auto!important;
    min-height:132px!important;height:auto!important;padding:18px!important;border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;
    background:rgba(255,255,255,.91)!important;box-shadow:0 14px 34px rgba(61,104,145,.07)!important;column-gap:16px!important;row-gap:4px!important;
  }
  #hub .view[data-view="dashboard"] .folderIcon{grid-column:1!important;grid-row:1/3!important;width:62px!important;height:62px!important;border-radius:20px!important;font-size:22px!important}
  #hub .view[data-view="dashboard"] .folder h2{grid-column:2!important;grid-row:1!important;margin:0!important;font-size:24px!important;align-self:end!important}
  #hub .view[data-view="dashboard"] .folder p{grid-column:2!important;grid-row:2!important;margin:0!important;font-size:12px!important;align-self:start!important}
  #hub .view[data-view="dashboard"] .folderArrow{grid-column:3!important;grid-row:1/3!important;align-self:center!important;font-size:30px!important}
  #hub .view[data-view="dashboard"] .folderFoot{display:none!important}

  /* Profile: edit card + subscription + social, nothing else. */
  #hub .view[data-view="profile"] .profileOnlyScroller{display:grid!important;gap:14px!important;height:auto!important;overflow:visible!important}
  #hub .view[data-view="profile"] .profileEdit{
    display:grid!important;grid-template-columns:92px minmax(0,1fr)!important;gap:16px!important;padding:18px!important;margin:0!important;
    border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.91)!important;box-shadow:0 14px 34px rgba(61,104,145,.07)!important;
  }
  #hub .view[data-view="profile"] .profilePhotoEdit{display:flex!important;flex-direction:column!important;gap:10px!important;align-items:center!important}
  #hub .view[data-view="profile"] .profileAvatarBig{width:82px!important;height:82px!important;border-radius:50%!important}
  #hub .view[data-view="profile"] .photoBtn{width:100%!important;text-align:center!important;border-radius:14px!important;padding:9px 8px!important;background:#EAF5FF!important;color:#167CE7!important}
  #hub .view[data-view="profile"] .profileField{display:grid!important;gap:8px!important;align-content:center!important}
  #hub .view[data-view="profile"] .profileField label{font-size:11px!important;letter-spacing:.08em!important}
  #hub .view[data-view="profile"] .profileField input{min-height:48px!important;border-radius:16px!important;font-size:17px!important;padding:10px 13px!important}
  #hub .view[data-view="profile"] .saveProfileBtn{min-height:44px!important;border-radius:15px!important;font-size:13px!important;background:linear-gradient(90deg,#A9DFFF,#CFF3DD)!important;color:#287BAF!important}
  #hub .profilePortalCard{border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.91)!important;box-shadow:0 14px 34px rgba(61,104,145,.07)!important;padding:18px!important}
  #hub .profilePortalHeader{display:grid!important;grid-template-columns:58px minmax(0,1fr) auto!important;gap:14px!important;align-items:center!important}
  #hub .profilePortalIcon{width:58px!important;height:58px!important;border-radius:18px!important;display:grid!important;place-items:center!important;font-size:24px!important;font-weight:900!important}
  #hub .profilePortalPlan .profilePortalIcon{background:#FFF1C7!important;color:#B87800!important}
  #hub .profilePortalSocial .profilePortalIcon{background:#EEE8FF!important;color:#7A57E8!important}
  #hub .profilePortalTitle{font-size:24px!important;font-weight:900!important;letter-spacing:-.03em!important;color:#0D2A66!important}
  #hub .profilePortalSub{margin-top:2px!important;font-size:12px!important;color:#7185A6!important}
  #hub .profilePortalArrow{font-size:28px!important;color:#9AB0C2!important}
  #hub .profilePlanSummary{margin-top:14px!important;padding:14px!important;border-radius:18px!important;background:linear-gradient(90deg,#FFF8E3,#F7FCFF)!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:12px!important}
  #hub .profilePlanSummary b{font-size:22px!important}.profilePlanSummary span{font-size:11px!important;color:#7185A6!important}
  #hub .portalSocialRows{display:grid!important;gap:0!important;margin-top:12px!important}
  #hub .portalSocialRows .socialCard{border:0!important;border-top:1px solid rgba(143,181,216,.16)!important;border-radius:0!important;padding:10px 2px!important;background:transparent!important;grid-template-columns:40px minmax(0,1fr) auto!important}
  #hub .portalSocialRows .socialCard:first-child{border-top:0!important}
  #hub .portalSocialRows .socialLogo{width:36px!important;height:36px!important;border-radius:11px!important}
  #hub .portalSocialRows .socialName{font-size:13px!important}.portalSocialRows .socialState{font-size:10px!important}
  #hub .portalSocialRows .connectBtn{font-size:10px!important;padding:7px 9px!important;border-radius:999px!important}
  #hub .view[data-view="profile"] .logoutProfile{margin:0!important;min-height:42px!important;border-radius:14px!important;background:rgba(255,244,244,.88)!important;color:#A75C68!important;font-size:10px!important}

  /* Projects landing + deep views. */
  #hub #projectHubCards{display:grid!important;gap:14px!important}
  #hub #projectHubCards[hidden],#hub #projectDeep[hidden]{display:none!important}
  #hub .projectHubCard{min-height:150px!important;border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.91)!important;box-shadow:0 14px 34px rgba(61,104,145,.07)!important;padding:20px!important;display:grid!important;grid-template-columns:68px minmax(0,1fr) auto!important;gap:16px!important;align-items:center!important;color:#0D2A66!important;text-align:left!important}
  #hub .projectHubIcon{width:68px!important;height:68px!important;border-radius:22px!important;display:grid!important;place-items:center!important;font-size:28px!important;background:#E4F2FF!important;color:#2389E8!important}
  #hub .projectHubCard[data-project-dest="drafts"] .projectHubIcon{background:#EEE8FF!important;color:#8354F1!important}
  #hub .projectHubCard b{font-size:26px!important;line-height:1!important}.projectHubCard small{display:block!important;margin-top:8px!important;font-size:12px!important;color:#7185A6!important;line-height:1.25!important}.projectHubCard i{font-style:normal!important;font-size:30px!important;color:#9AB0C2!important}
  #hub #projectDeep{display:grid!important;gap:12px!important}
  #hub .projectSection{margin:0!important}
  #hub .projectSectionHead{display:flex!important;align-items:center!important;justify-content:space-between!important;margin:0 2px 10px!important;font-size:12px!important;letter-spacing:.06em!important;color:#7185A6!important}
  #hub .rows{display:grid!important;gap:12px!important}
  #hub .shortDesignCard,#hub .draftDesignCard{border:1px solid rgba(143,181,216,.18)!important;border-radius:24px!important;background:rgba(255,255,255,.94)!important;box-shadow:0 12px 28px rgba(61,104,145,.06)!important;padding:14px!important;display:grid!important;gap:10px!important}
  #hub .designCardTop{display:flex!important;align-items:flex-start!important;justify-content:space-between!important;gap:10px!important}
  #hub .designCardTitle{font-size:17px!important;font-weight:900!important;color:#0D2A66!important}.designCardMeta{margin-top:4px!important;font-size:11px!important;color:#7185A6!important}
  #hub .designCardActions{display:flex!important;gap:8px!important;flex-wrap:wrap!important}.designCardActions .action{min-height:38px!important;border-radius:12px!important;font-size:11px!important;padding:8px 12px!important}
  #hub .designCardActions .action.primary{background:#4CA6F5!important;color:#fff!important}

  /* Social page. */
  #hub .socialSummary{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:14px!important;padding:18px!important;margin-bottom:14px!important;border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.91)!important;box-shadow:0 14px 34px rgba(61,104,145,.07)!important}
  #hub .socialSummary strong{font-size:34px!important;line-height:1!important}.socialSummary span{font-size:12px!important;color:#7185A6!important}
  #hub .socialFolderScroller{display:grid!important;gap:12px!important;overflow:visible!important;height:auto!important}
  #hub .socialFolderScroller>.socialCard{padding:14px!important;border-radius:22px!important;grid-template-columns:48px minmax(0,1fr) auto!important;box-shadow:0 10px 24px rgba(61,104,145,.05)!important}
  #hub .socialFolderScroller>.socialCard .socialLogo{width:44px!important;height:44px!important;border-radius:14px!important;font-size:15px!important}.socialFolderScroller>.socialCard .socialName{font-size:16px!important}.socialFolderScroller>.socialCard .socialState{font-size:11px!important}.socialFolderScroller>.socialCard .connectBtn{font-size:11px!important;padding:9px 12px!important;border-radius:12px!important}

  /* Subscription page. */
  #hub .subscriptionScroller{display:grid!important;gap:14px!important;height:auto!important;overflow:visible!important}
  #hub .subscriptionPlanCard{border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.92)!important;box-shadow:0 14px 34px rgba(61,104,145,.07)!important;padding:18px!important;display:grid!important;grid-template-columns:58px minmax(0,1fr)!important;gap:14px!important}
  #hub .subscriptionPlanIcon{width:58px!important;height:58px!important;border-radius:18px!important;display:grid!important;place-items:center!important;font-size:26px!important;background:#E4F2FF!important;color:#2389E8!important}
  #hub .creatorPlan .subscriptionPlanIcon{background:#EEE8FF!important;color:#8354F1!important}.proPlan .subscriptionPlanIcon{background:#FFF1C7!important;color:#E49A00!important}
  #hub .subscriptionPlanCard h3{margin:0!important;font-size:24px!important;line-height:1!important;color:#0D2A66!important}.subscriptionPlanCard p{margin:7px 0 0!important;font-size:12px!important;line-height:1.35!important;color:#7185A6!important}
  #hub .subscriptionPlanMeta{grid-column:1/3!important;margin-top:4px!important;padding-top:12px!important;border-top:1px solid rgba(143,181,216,.16)!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:10px!important}.subscriptionPlanMeta b{font-size:15px!important}.subscriptionPlanMeta button{border:0!important;border-radius:13px!important;padding:10px 13px!important;background:#EAF5FF!important;color:#287BAF!important;font-size:11px!important;font-weight:900!important}

  /* Live page. */
  #hub .liveDesignWrap{display:grid!important;gap:14px!important}
  #hub .liveDesignSection{border:1px solid rgba(143,181,216,.18)!important;border-radius:28px!important;background:rgba(255,255,255,.92)!important;box-shadow:0 14px 34px rgba(61,104,145,.07)!important;padding:16px!important}
  #hub .liveDesignHead{display:grid!important;grid-template-columns:54px minmax(0,1fr)!important;gap:13px!important;align-items:center!important;margin-bottom:8px!important}.liveDesignIcon{width:54px!important;height:54px!important;border-radius:18px!important;display:grid!important;place-items:center!important;font-size:22px!important;background:#EEE8FF!important;color:#8354F1!important}.youtubeDesignSection .liveDesignIcon{background:#FFE7E7!important;color:#FF1744!important}.liveDesignHead h3{margin:0!important;font-size:24px!important;color:#0D2A66!important}.liveDesignHead p{margin:4px 0 0!important;font-size:11px!important;color:#7185A6!important}
  #hub .liveDesignRows{display:grid!important;gap:8px!important}.liveDesignRow{min-height:68px!important;border:0!important;border-radius:18px!important;background:#FAFDFF!important;padding:10px!important;display:grid!important;grid-template-columns:44px minmax(0,1fr) auto!important;gap:11px!important;align-items:center!important;text-align:left!important;color:#0D2A66!important}.liveDesignRow span:first-child{width:44px!important;height:44px!important;border-radius:14px!important;display:grid!important;place-items:center!important;background:#F0EBFF!important;color:#8354F1!important;font-size:18px!important}.youtubeDesignSection .liveDesignRow span:first-child{background:#FFF0F3!important;color:#FF1744!important}.liveDesignRow b{font-size:15px!important}.liveDesignRow small{display:block!important;margin-top:2px!important;font-size:10px!important;color:#7185A6!important}.liveDesignRow i{font-style:normal!important;font-size:25px!important;color:#9AB0C2!important}
}
/* END V312 CREATOR HUB DESIGN SYNC */
'''

PROJECTS = r'''  <section class="view" data-view="projects">
   <div class="detail">
    <div class="detailHead"><button class="backBtn" type="button">‹ Creator Hub</button><div class="detailHeadText"><h2 id="projectsViewTitle">I miei progetti</h2><p id="projectsViewSubtitle">Gestisci i tuoi Shorts e le bozze.</p></div></div>
    <div class="detailCard"><div class="folderScroller">
      <div id="projectHubCards">
       <button class="projectHubCard" data-project-dest="shorts" type="button"><span class="projectHubIcon">▶</span><span><b>I miei Shorts</b><small>Short finali pubblicati e pronti da rivedere.</small></span><i>›</i></button>
       <button class="projectHubCard" data-project-dest="drafts" type="button"><span class="projectHubIcon">▱</span><span><b>Bozze</b><small>Progetti salvati da riprendere.</small></span><i>›</i></button>
      </div>
      <div id="projectDeep" hidden>
       <div class="projectSection" data-project-pane="drafts">
        <div class="projectSectionHead"><span>BOZZE</span><b id="draftProjectCount">0</b></div>
        <div id="projectRows"></div>
        <div class="rows" id="draftRows"><div class="empty">Caricamento progetti…</div></div>
       </div>
       <div class="projectSection" data-project-pane="shorts">
        <div class="projectSectionHead"><span>I MIEI SHORTS</span><b id="shortProjectCount">0</b></div>
        <div class="rows" id="shortRows"><div class="empty">Caricamento Shorts…</div></div>
       </div>
      </div>
    </div></div>
   </div>
  </section>
'''

PROFILE = r'''  <section class="view" data-view="profile">
   <div class="detail">
    <div class="detailHead"><button class="backBtn" type="button">‹ Creator Hub</button><div class="detailHeadText"><h2>Profilo</h2><p>Gestisci le tue informazioni.</p></div></div>
    <div class="detailCard"><div class="folderScroller profileOnlyScroller">
      <div class="profileEdit">
       <div class="profilePhotoEdit">
        <div class="avatar profileAvatarBig" id="profileAvatar"><img id="profileAvatarImg" alt=""><span class="avatarInitial" id="profileAvatarInitial">C</span></div>
        <label class="photoBtn">Cambia foto<input id="profilePhotoInput" type="file" accept="image/jpeg,image/png,image/webp"></label>
       </div>
       <div class="profileField">
        <label for="profileNameInput">NOME CREATOR</label>
        <input id="profileNameInput" maxlength="80" value="Creator">
        <button class="saveProfileBtn" id="saveProfileBtn" type="button">Salva profilo</button>
       </div>
      </div>

      <div class="profilePortalCard profilePortalPlan">
       <div class="profilePortalHeader"><span class="profilePortalIcon">♕</span><span><span class="profilePortalTitle">Abbonamento</span><span class="profilePortalSub">Il tuo piano attuale e vantaggi.</span></span><button class="profilePortalArrow" data-open-folder="subscription" type="button">›</button></div>
       <div class="profilePlanSummary"><div><b id="profilePortalPlanName">FREE</b><span> Piano attuale</span></div><button class="planBtn" data-open-folder="subscription" type="button">Scopri i piani</button></div>
      </div>

      <div class="profilePortalCard profilePortalSocial">
       <div class="profilePortalHeader"><span class="profilePortalIcon">⌯</span><span><span class="profilePortalTitle">Social collegati</span><span class="profilePortalSub">Collega i tuoi account per pubblicare più facilmente.</span></span><button class="profilePortalArrow" data-open-folder="social" type="button">›</button></div>
       <div class="portalSocialRows">
        <div class="socialCard" data-platform="youtube"><div class="socialLogo">▶</div><div><div class="socialName">YouTube</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="youtube">Collega</button></div>
        <div class="socialCard" data-platform="tiktok"><div class="socialLogo">♪</div><div><div class="socialName">TikTok</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="tiktok">Collega</button></div>
        <div class="socialCard" data-platform="instagram"><div class="socialLogo">◎</div><div><div class="socialName">Instagram</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="instagram">Collega</button></div>
        <div class="socialCard" data-platform="facebook"><div class="socialLogo">f</div><div><div class="socialName">Facebook</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="facebook">Collega</button></div>
        <div class="socialCard" data-platform="twitch"><div class="socialLogo">◧</div><div><div class="socialName">Twitch</div><div class="socialState">Live in arrivo</div></div><button class="connectBtn" data-connect="twitch" disabled>Live in arrivo</button></div>
       </div>
      </div>
      <button class="logoutProfile" id="logoutProfile" type="button">Disconnetti dal Creator Hub</button>
    </div></div>
   </div>
  </section>
'''

SOCIAL = r'''  <section class="view" data-view="social">
   <div class="detail">
    <div class="detailHead"><button class="backBtn" type="button">‹ Creator Hub</button><div class="detailHeadText"><h2>Social collegati</h2><p>Collega i tuoi profili per gestire tutto da un unico posto.</p></div></div>
    <div class="detailCard"><div class="folderScroller socialFolderScroller">
      <div class="socialSummary"><div><strong id="socialSummaryCount">0/5</strong><br><span>account collegati</span></div><span>Gestisci i tuoi account</span></div>
      <div class="socialCard" data-platform="youtube"><div class="socialLogo">▶</div><div><div class="socialName">YouTube</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="youtube">Collega</button></div>
      <div class="socialCard" data-platform="tiktok"><div class="socialLogo">♪</div><div><div class="socialName">TikTok</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="tiktok">Collega</button></div>
      <div class="socialCard" data-platform="instagram"><div class="socialLogo">◎</div><div><div class="socialName">Instagram</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="instagram">Collega</button></div>
      <div class="socialCard" data-platform="facebook"><div class="socialLogo">f</div><div><div class="socialName">Facebook</div><div class="socialState">Non collegato</div></div><button class="connectBtn" data-connect="facebook">Collega</button></div>
      <div class="socialCard" data-platform="twitch"><div class="socialLogo">◧</div><div><div class="socialName">Twitch</div><div class="socialState">Live in arrivo</div></div><button class="connectBtn" data-connect="twitch" disabled>Live in arrivo</button></div>
    </div></div>
   </div>
  </section>
'''

SUBSCRIPTION = r'''  <section class="view" data-view="subscription">
   <div class="detail">
    <div class="detailHead"><button class="backBtn" type="button">‹ Creator Hub</button><div class="detailHeadText"><h2>Abbonamento</h2><p>Scegli il piano più adatto al tuo percorso da creator.</p></div></div>
    <div class="detailCard"><div class="folderScroller subscriptionScroller">
      <div class="subscriptionPlanCard currentPlan"><span class="subscriptionPlanIcon">♕</span><div><h3 id="profilePlanName">FREE</h3><p id="profilePlanText">Piano attuale</p></div><div class="subscriptionPlanMeta"><b>Piano attivo</b><button type="button" disabled>Attuale</button></div></div>
      <div class="subscriptionPlanCard creatorPlan"><span class="subscriptionPlanIcon">☆</span><div><h3>Creator</h3><p>Più strumenti per creare di più, con un flusso più completo.</p></div><div class="subscriptionPlanMeta"><b>In arrivo</b><button type="button" disabled>Scegli piano</button></div></div>
      <div class="subscriptionPlanCard proPlan"><span class="subscriptionPlanIcon">ϟ</span><div><h3>Pro</h3><p>Funzioni avanzate per creator che vogliono spingere al massimo il workflow.</p></div><div class="subscriptionPlanMeta"><b>In arrivo</b><button type="button" disabled>Scegli piano</button></div></div>
    </div></div>
   </div>
  </section>
'''

LIVE = r'''  <section class="view" data-view="live">
   <div class="detail">
    <div class="detailHead"><button class="backBtn" type="button">‹ Creator Hub</button><div class="detailHeadText"><h2>Live</h2><p>Le tue dirette diventano una libreria di momenti.</p></div></div>
    <div class="detailCard"><div class="folderScroller liveDesignWrap">
      <div class="liveDesignSection twitchDesignSection">
       <div class="liveDesignHead"><span class="liveDesignIcon">◧</span><div><h3>Twitch</h3><p>Gestisci e riutilizza i contenuti delle tue live su Twitch.</p></div></div>
       <div class="liveDesignRows">
        <button class="liveDesignRow" data-live-mini="sessions"><span>▣</span><div><b>Le tue live</b><small>Tutte le live trasmesse su Twitch.</small></div><i>›</i></button>
        <button class="liveDesignRow" data-live-mini="vod"><span>▶</span><div><b>VOD</b><small>Rivedi e gestisci i tuoi VOD.</small></div><i>›</i></button>
        <button class="liveDesignRow" data-live-mini="twitch-highlights"><span>✦</span><div><b>Highlights</b><small>I momenti migliori delle tue live.</small></div><i>›</i></button>
       </div>
       <div id="liveMiniContent" class="liveMiniContent"><div class="empty">Le tue live Twitch compariranno qui appena disponibili.</div></div>
      </div>
      <div class="liveDesignSection youtubeDesignSection">
       <div class="liveDesignHead"><span class="liveDesignIcon">▶</span><div><h3>YouTube</h3><p>Gestisci e riutilizza i contenuti delle tue live su YouTube.</p></div></div>
       <div class="liveDesignRows">
        <button class="liveDesignRow" type="button"><span>▣</span><div><b>Le tue live</b><small>Dirette YouTube salvate nel Creator Hub.</small></div><i>›</i></button>
        <button class="liveDesignRow" type="button"><span>▶</span><div><b>VOD</b><small>Replay completi delle live YouTube.</small></div><i>›</i></button>
        <button class="liveDesignRow" type="button"><span>✦</span><div><b>Highlights</b><small>Short e momenti estratti da YouTube.</small></div><i>›</i></button>
       </div>
      </div>
    </div></div>
   </div>
  </section>
'''


def section_replace(text, view, next_view, replacement):
    pattern = rf'  <section class="view(?: active)?" data-view="{re.escape(view)}">.*?(?=  <section class="view" data-view="{re.escape(next_view)}">)'
    updated, count = re.subn(pattern, replacement + '\n', text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f'V312 section anchor missing: {view}')
    return updated


def patch_hub_text(text: str) -> str:
    if 'V312 CREATOR HUB DESIGN SYNC' in text:
        return text
    if '</style>' not in text:
        raise RuntimeError('V312 style anchor missing')
    text = text.replace('</style>', CSS + '\n</style>', 1)

    # Dashboard: remove redundant top-level Social/Subscription cards and normalize Live label.
    text = re.sub(r'\n\s*<button class="folder" data-folder="social">.*?</button>', '', text, count=1, flags=re.S)
    text = re.sub(r'\n\s*<button class="folder" data-folder="subscription">.*?</button>', '', text, count=1, flags=re.S)
    text = text.replace('<h2>Le mie live</h2>', '<h2>Live</h2>', 1)

    text = section_replace(text, 'projects', 'profile', PROJECTS)
    text = section_replace(text, 'profile', 'social', PROFILE)
    text = section_replace(text, 'social', 'subscription', SOCIAL)
    text = section_replace(text, 'subscription', 'live', SUBSCRIPTION)
    live_pattern = r'  <section class="view" data-view="live">.*?(?=\n </div>\n</main>)'
    text, count = re.subn(live_pattern, LIVE.rstrip(), text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError('V312 section anchor missing: live')

    old_open = '''   if(view==="projects"){
     $("[data-project-pane]").forEach(p=>{p.style.display=(!projectMode||p.dataset.projectPane===projectMode)?"":"none"});
     if(title)title.textContent=projectMode==="shorts"?"I miei Shorts":projectMode==="drafts"?"Bozze":"Progetti";
     if(sub)sub.textContent=projectMode==="shorts"?"Tutti gli Shorts completati e salvati nel Creator Hub.":projectMode==="drafts"?"Progetti salvati da riprendere quando vuoi.":"Quello che stai creando e gli Shorts già completati.";
   }'''
    new_open = '''   if(view==="projects"){
     const projectHub=$("#projectHubCards"),projectDeep=$("#projectDeep");
     if(projectHub)projectHub.hidden=!!projectMode;
     if(projectDeep)projectDeep.hidden=!projectMode;
     $("[data-project-pane]").forEach(p=>{p.style.display=(projectMode&&p.dataset.projectPane===projectMode)?"":"none"});
     if(title)title.textContent=projectMode==="shorts"?"I miei Shorts":projectMode==="drafts"?"Bozze":"I miei progetti";
     if(sub)sub.textContent=projectMode==="shorts"?"Short finali pubblicati e pronti da rivedere.":projectMode==="drafts"?"Progetti salvati da riprendere quando vuoi.":"Gestisci i tuoi Shorts e le bozze.";
   }'''
    if old_open not in text:
        raise RuntimeError('V312 openView anchor missing')
    text = text.replace(old_open, new_open, 1)

    # Keep dynamic plan/social values synced in the new approved profile layout.
    plan_anchor = '   const ppn=$("#profilePlanName");if(ppn)ppn.textContent=String(a.plan||"FREE").toUpperCase();'
    plan_inject = plan_anchor + '\n   const pppn=$("#profilePortalPlanName");if(pppn)pppn.textContent=String(a.plan||"FREE").toUpperCase();'
    if plan_anchor not in text:
        raise RuntimeError('V312 plan render anchor missing')
    text = text.replace(plan_anchor, plan_inject, 1)

    social_anchor = '   const socialCount=$("#socialCount");if(socialCount)socialCount.textContent=String(st.social||0)+" collegati";'
    social_inject = social_anchor + '\n   const socialSummaryCount=$("#socialSummaryCount");if(socialSummaryCount)socialSummaryCount.textContent=String(st.social||0)+"/5";'
    if social_anchor not in text:
        raise RuntimeError('V312 social render anchor missing')
    text = text.replace(social_anchor, social_inject, 1)

    short_pattern = r'   \$\("#shortRows"\)\.innerHTML=shorts\.length\?.*?;\n\n   const drafts='
    short_repl = '''   $("#shortRows").innerHTML=shorts.length?shorts.map(s=>'<div class="shortDesignCard"><div class="designCardTop"><div><div class="designCardTitle">'+esc(s.title||"Short")+'</div><div class="designCardMeta">'+((s.published||[]).length?"Pubblicato":"Salvato")+' · '+((Number(s.final_bytes)||0)>1048576?Math.max(1,Math.round(Number(s.final_bytes)/1048576))+" MB":"Short")+'</div></div><span class="status">SHORT</span></div><div class="designCardActions"><button class="action primary" data-short-download="'+esc(s.id||"")+'">Guarda</button><button class="action danger" data-short-delete="'+esc(s.id||"")+'">Elimina</button></div></div>').join(""):'<div class="empty">Nessuno Short archiviato.</div>';

   const drafts='''
    text, count = re.subn(short_pattern, short_repl, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError('V312 shorts render anchor missing')

    draft_pattern = r'   \$\("#draftRows"\)\.innerHTML=drafts\.length\?.*?;\n\n   const p='
    draft_repl = '''   $("#draftRows").innerHTML=drafts.length?drafts.map(d=>'<div class="draftDesignCard"><div class="designCardTop"><div><div class="designCardTitle">'+esc(d.title||d.source_name||"Gameplay")+'</div><div class="designCardMeta">'+(d.duration?d.duration+" sec · ":"")+ago(d.updated_at)+'</div></div><span class="status">BOZZA</span></div><div class="designCardActions"><button class="action primary" data-resume="'+esc(d.id||"")+'">Riprendi</button></div></div>').join(""):'<div class="empty">Nessun progetto in lavorazione salvato.</div>';

   const p='''
    text, count = re.subn(draft_pattern, draft_repl, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError('V312 drafts render anchor missing')

    listeners_anchor = ' $$("[data-live-folder]").forEach(b=>b.onclick=()=>openLiveFolder(b.dataset.liveFolder));'
    listeners_new = ' $$("[data-project-dest]").forEach(b=>b.onclick=()=>openView(b.dataset.projectDest));\n' + listeners_anchor
    if listeners_anchor not in text:
        raise RuntimeError('V312 listener anchor missing')
    text = text.replace(listeners_anchor, listeners_new, 1)
    return text


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HUB
    if not target.is_file():
        raise SystemExit(f'V312 target missing: {target}')
    before = target.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    target.write_text(after, encoding='utf-8')
    print('V312 Creator Hub design sync applied:', target, 'changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
